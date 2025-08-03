# Copyright (C) 2025  Christopher Pommer <cp.software@outlook.de>

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
# CHECKMK AGENT PLUG-IN SCRIPT: Microsoft Windows Update
#
# This script generates the Checkmk agent section for pending Windows updates.
# This file is part of the Microsoft Windows Update agent plug-in.
####################################################################################################

# Get pending updates
$UpdateSession = New-Object -ComObject Microsoft.Update.Session
$UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
$SearchResults = $UpdateSearcher.Search("IsInstalled=0 and IsHidden=0")


Write-Output "<<<ms_win_update>>>"

# Output all pending update names
foreach ($Update in $SearchResults.Updates) {
    Write-Output $Update.Title
}
