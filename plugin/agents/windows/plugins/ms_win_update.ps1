# Copyright (C) 2025  Christopher Pommer <cp.software@outlook.de>
# Enhanced with SCCM support by Mario Fellner <mario.fellner@outlook.at>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

####################################################################################################
# CHECKMK AGENT PLUG-IN SCRIPT: Microsoft Windows Update with SCCM Support
#
# This script generates the Checkmk agent section for pending Windows updates from both
# Windows Update and SCCM sources.
# This file is part of the Microsoft Windows Update agent plug-in with SCCM support.
####################################################################################################

param(
    [switch]$EnableSCCM = $true,
    [switch]$EnableWindowsUpdate = $true,
    [switch]$Debug = $false
)

function Write-Debug-Info {
    param([string]$Message)
    if ($Debug) {
        Write-Host "[DEBUG] $Message" -ForegroundColor Yellow
    }
}

function Get-WindowsUpdates {
    Write-Debug-Info "Checking Windows Updates..."
    $updates = @()
    
    try {
        $UpdateSession = New-Object -ComObject Microsoft.Update.Session
        $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
        $SearchResults = $UpdateSearcher.Search("IsInstalled=0 and IsHidden=0")
        
        foreach ($Update in $SearchResults.Updates) {
            $updates += [PSCustomObject]@{
                Title = $Update.Title
                Source = "WindowsUpdate"
                KB = if ($Update.KBArticleIDs.Count -gt 0) { "KB" + ($Update.KBArticleIDs -join ",KB") } else { "" }
                Severity = $Update.MsrcSeverity
                Categories = ($Update.Categories | ForEach-Object { $_.Name }) -join ", "
                Size = $Update.MaxDownloadSize
                IsDownloaded = $Update.IsDownloaded
                RebootRequired = $Update.RebootRequired
            }
        }
        Write-Debug-Info "Found $($updates.Count) Windows Updates"
    }
    catch {
        Write-Debug-Info "Error getting Windows Updates: $($_.Exception.Message)"
    }
    
    return $updates
}

function Get-SCCMUpdates {
    Write-Debug-Info "Checking SCCM Updates..."
    $updates = @()
    
    try {
        # Check if SCCM client is installed and running
        $sccmClient = Get-Service -Name "CcmExec" -ErrorAction SilentlyContinue
        if (-not $sccmClient -or $sccmClient.Status -ne "Running") {
            Write-Debug-Info "SCCM client not found or not running"
            return $updates
        }

        # Get SCCM updates using WMI
        $sccmUpdates = Get-WmiObject -Namespace "ROOT\ccm\ClientSDK" -Class "CCM_SoftwareUpdate" -ErrorAction SilentlyContinue
        
        if ($sccmUpdates) {
            foreach ($Update in $sccmUpdates) {
                # Only include updates that are not installed
                if ($Update.EvaluationState -ne 3) {  # 3 = Installed
                    $updates += [PSCustomObject]@{
                        Title = $Update.Name
                        Source = "SCCM"
                        KB = $Update.ArticleID
                        Severity = $Update.Severity
                        Categories = $Update.UpdateClassification
                        Size = $Update.ContentSize
                        IsDownloaded = $Update.EvaluationState -eq 6  # 6 = Downloaded
                        RebootRequired = $Update.RebootRequired
                        EvaluationState = $Update.EvaluationState
                        Deadline = $Update.Deadline
                        ComplianceState = $Update.ComplianceState
                    }
                }
            }
        }
        
        # Also check for SCCM Software Update assignments
        $updateAssignments = Get-WmiObject -Namespace "ROOT\ccm\Policy\Machine\ActualConfig" -Class "CCM_UpdateStatus" -ErrorAction SilentlyContinue
        
        Write-Debug-Info "Found $($updates.Count) SCCM Updates"
    }
    catch {
        Write-Debug-Info "Error getting SCCM Updates: $($_.Exception.Message)"
    }
    
    return $updates
}

function Get-SCCMClientInfo {
    try {
        $sccmClient = Get-Service -Name "CcmExec" -ErrorAction SilentlyContinue
        $clientVersion = ""
        $lastPolicyUpdate = ""
        
        if ($sccmClient) {
            try {
                $clientInfo = Get-WmiObject -Namespace "ROOT\ccm" -Class "CCM_InstalledComponent" -Filter "DisplayName='Configuration Manager Client'" -ErrorAction SilentlyContinue
                if ($clientInfo) {
                    $clientVersion = $clientInfo.Version
                }
                
                $policyInfo = Get-WmiObject -Namespace "ROOT\ccm\Policy\Machine" -Class "CCM_PolicyAgent_Configuration" -ErrorAction SilentlyContinue
                if ($policyInfo) {
                    $lastPolicyUpdate = $policyInfo.LastUpdateTime
                }
            }
            catch {
                Write-Debug-Info "Error getting SCCM client details: $($_.Exception.Message)"
            }
        }
        
        return [PSCustomObject]@{
            ServiceStatus = if ($sccmClient) { $sccmClient.Status } else { "NotInstalled" }
            Version = $clientVersion
            LastPolicyUpdate = $lastPolicyUpdate
        }
    }
    catch {
        Write-Debug-Info "Error getting SCCM client info: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
Write-Output "<<<ms_win_update_v2>>>"

# Get all updates
$allUpdates = @()

if ($EnableWindowsUpdate) {
    $windowsUpdates = Get-WindowsUpdates
    $allUpdates += $windowsUpdates
}

if ($EnableSCCM) {
    $sccmUpdates = Get-SCCMUpdates
    $allUpdates += $sccmUpdates
}

# Output SCCM client information
if ($EnableSCCM) {
    $sccmInfo = Get-SCCMClientInfo
    if ($sccmInfo) {
        Write-Output "SCCM_CLIENT_STATUS:$($sccmInfo.ServiceStatus)"
        Write-Output "SCCM_CLIENT_VERSION:$($sccmInfo.Version)"
        Write-Output "SCCM_LAST_POLICY_UPDATE:$($sccmInfo.LastPolicyUpdate)"
    }
}

# Output update counts by source
$windowsUpdateCount = ($allUpdates | Where-Object { $_.Source -eq "WindowsUpdate" }).Count
$sccmUpdateCount = ($allUpdates | Where-Object { $_.Source -eq "SCCM" }).Count

Write-Output "WINDOWS_UPDATE_COUNT:$windowsUpdateCount"
Write-Output "SCCM_UPDATE_COUNT:$sccmUpdateCount"
Write-Output "TOTAL_UPDATE_COUNT:$($allUpdates.Count)"

# Output all pending updates with detailed information
foreach ($Update in $allUpdates) {
    $updateLine = "UPDATE|$($Update.Source)|$($Update.Title)"
    
    # Add KB information if available
    if ($Update.KB) {
        $updateLine += "|KB:$($Update.KB)"
    }
    
    # Add severity if available
    if ($Update.Severity) {
        $updateLine += "|SEVERITY:$($Update.Severity)"
    }
    
    # Add categories if available
    if ($Update.Categories) {
        $updateLine += "|CATEGORIES:$($Update.Categories)"
    }
    
    # Add size if available (convert bytes to MB for readability)
    if ($Update.Size -and $Update.Size -gt 0) {
        $sizeMB = [math]::Round($Update.Size / 1MB, 2)
        $updateLine += "|SIZE:${sizeMB}MB"
    }
    
    # Add download status
    if ($Update.IsDownloaded -ne $null) {
        $updateLine += "|DOWNLOADED:$($Update.IsDownloaded)"
    }
    
    # Add reboot requirement
    if ($Update.RebootRequired -ne $null) {
        $updateLine += "|REBOOT:$($Update.RebootRequired)"
    }
    
    # Add SCCM-specific information
    if ($Update.Source -eq "SCCM") {
        if ($Update.EvaluationState) {
            $updateLine += "|EVAL_STATE:$($Update.EvaluationState)"
        }
        if ($Update.Deadline) {
            $updateLine += "|DEADLINE:$($Update.Deadline)"
        }
        if ($Update.ComplianceState) {
            $updateLine += "|COMPLIANCE:$($Update.ComplianceState)"
        }
    }
    
    Write-Output $updateLine
}

Write-Debug-Info "Script completed successfully"
