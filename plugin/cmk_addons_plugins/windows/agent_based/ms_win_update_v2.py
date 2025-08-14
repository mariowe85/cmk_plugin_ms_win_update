#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4; max-line-length: 100 -*-

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
# CHECKMK CHECK PLUG-IN: Microsoft Windows Update with SCCM Support
#
# This plug-in generates the Checkmk services and determines their status for both
# Windows Update and SCCM updates.
####################################################################################################

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime, timezone

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class WindowsUpdate:
    title: str
    source: str  # "WindowsUpdate" or "SCCM"
    kb: Optional[str] = None
    severity: Optional[str] = None
    categories: Optional[str] = None
    size_mb: Optional[float] = None
    is_downloaded: Optional[bool] = None
    reboot_required: Optional[bool] = None
    # SCCM-specific fields
    evaluation_state: Optional[int] = None
    deadline: Optional[str] = None
    compliance_state: Optional[int] = None


@dataclass(frozen=True)
class SCCMClientInfo:
    status: str
    version: str
    last_policy_update: str


@dataclass(frozen=True)
class Section:
    updates: list[WindowsUpdate]
    windows_update_count: int
    sccm_update_count: int
    total_count: int
    sccm_client_info: Optional[SCCMClientInfo] = None


def parse_ms_win_update_v2(string_table: StringTable) -> Section:
    updates = []
    windows_update_count = 0
    sccm_update_count = 0
    total_count = 0
    sccm_client_info = None
    
    sccm_status = ""
    sccm_version = ""
    sccm_last_policy = ""

    for line in string_table:
        if not line:
            continue
            
        line_str = " ".join(line).strip()
        
        if line_str.startswith("SCCM_CLIENT_STATUS:"):
            sccm_status = line_str.split(":", 1)[1]
        elif line_str.startswith("SCCM_CLIENT_VERSION:"):
            sccm_version = line_str.split(":", 1)[1]
        elif line_str.startswith("SCCM_LAST_POLICY_UPDATE:"):
            sccm_last_policy = line_str.split(":", 1)[1]
        elif line_str.startswith("WINDOWS_UPDATE_COUNT:"):
            windows_update_count = int(line_str.split(":", 1)[1])
        elif line_str.startswith("SCCM_UPDATE_COUNT:"):
            sccm_update_count = int(line_str.split(":", 1)[1])
        elif line_str.startswith("TOTAL_UPDATE_COUNT:"):
            total_count = int(line_str.split(":", 1)[1])
        elif line_str.startswith("UPDATE|"):
            # Parse update line: UPDATE|Source|Title|KB:xxx|SEVERITY:xxx|...
            parts = line_str.split("|")
            if len(parts) >= 3:
                source = parts[1]
                title = parts[2]
                
                # Parse additional fields
                kb = None
                severity = None
                categories = None
                size_mb = None
                is_downloaded = None
                reboot_required = None
                evaluation_state = None
                deadline = None
                compliance_state = None
                
                for part in parts[3:]:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        if key == "KB":
                            kb = value
                        elif key == "SEVERITY":
                            severity = value
                        elif key == "CATEGORIES":
                            categories = value
                        elif key == "SIZE":
                            # Remove "MB" suffix and convert to float
                            try:
                                size_mb = float(value.replace("MB", ""))
                            except ValueError:
                                pass
                        elif key == "DOWNLOADED":
                            is_downloaded = value.lower() == "true"
                        elif key == "REBOOT":
                            reboot_required = value.lower() == "true"
                        elif key == "EVAL_STATE":
                            try:
                                evaluation_state = int(value)
                            except ValueError:
                                pass
                        elif key == "DEADLINE":
                            deadline = value
                        elif key == "COMPLIANCE":
                            try:
                                compliance_state = int(value)
                            except ValueError:
                                pass
                
                updates.append(WindowsUpdate(
                    title=title,
                    source=source,
                    kb=kb,
                    severity=severity,
                    categories=categories,
                    size_mb=size_mb,
                    is_downloaded=is_downloaded,
                    reboot_required=reboot_required,
                    evaluation_state=evaluation_state,
                    deadline=deadline,
                    compliance_state=compliance_state
                ))
    
    # Create SCCM client info if we have status information
    if sccm_status:
        sccm_client_info = SCCMClientInfo(
            status=sccm_status,
            version=sccm_version,
            last_policy_update=sccm_last_policy
        )

    return Section(
        updates=updates,
        windows_update_count=windows_update_count,
        sccm_update_count=sccm_update_count,
        total_count=total_count,
        sccm_client_info=sccm_client_info
    )


def discover_ms_win_update_v2(section: Section) -> DiscoveryResult:
    yield Service()


def check_ms_win_update_v2(params: Mapping[str, Any], section: Section) -> CheckResult:
    # Check SCCM client status first if SCCM monitoring is enabled
    if section.sccm_client_info and params.get("monitor_sccm_client", True):
        sccm_info = section.sccm_client_info
        if sccm_info.status == "NotInstalled":
            yield Result(
                state=State.OK,
                summary="SCCM client not installed"
            )
        elif sccm_info.status != "Running":
            yield Result(
                state=State.WARN,
                summary=f"SCCM client status: {sccm_info.status}"
            )
        else:
            client_details = f"SCCM client running (v{sccm_info.version})"
            if sccm_info.last_policy_update:
                client_details += f", last policy update: {sccm_info.last_policy_update}"
            yield Result(
                state=State.OK,
                notice=client_details
            )

    # Filter updates based on ignore patterns
    ignored_patterns_param = params.get("ignored_update_patterns", [])
    compiled_patterns = [re.compile(pattern) for pattern in ignored_patterns_param]
    
    # Separate updates by source and apply filtering
    windows_pending = []
    windows_ignored = []
    sccm_pending = []
    sccm_ignored = []
    
    for update in section.updates:
        is_ignored = any(pattern.search(update.title) for pattern in compiled_patterns)
        
        if update.source == "WindowsUpdate":
            if is_ignored:
                windows_ignored.append(update)
            else:
                windows_pending.append(update)
        elif update.source == "SCCM":
            if is_ignored:
                sccm_ignored.append(update)
            else:
                sccm_pending.append(update)
    
    total_pending = len(windows_pending) + len(sccm_pending)
    total_ignored = len(windows_ignored) + len(sccm_ignored)
    
    # Check thresholds for different update sources
    update_count_params = params.get("update_count")
    windows_count_params = params.get("windows_update_count")
    sccm_count_params = params.get("sccm_update_count")
    
    # Main pending update count check
    yield from check_levels(
        total_pending,
        levels_upper=update_count_params,
        metric_name="ms_win_updates_pending",
        label="Total pending",
        render_func=int,
    )
    
    # Windows Update specific count
    if windows_count_params and len(windows_pending) > 0:
        yield from check_levels(
            len(windows_pending),
            levels_upper=windows_count_params,
            metric_name="ms_win_updates_windows_pending",
            label="Windows Update pending",
            render_func=int,
        )
    else:
        yield Metric(name="ms_win_updates_windows_pending", value=len(windows_pending))
    
    # SCCM specific count
    if sccm_count_params and len(sccm_pending) > 0:
        yield from check_levels(
            len(sccm_pending),
            levels_upper=sccm_count_params,
            metric_name="ms_win_updates_sccm_pending",
            label="SCCM pending",
            render_func=int,
        )
    else:
        yield Metric(name="ms_win_updates_sccm_pending", value=len(sccm_pending))
    
    # Ignored updates metric
    if total_ignored > 0:
        yield Metric(name="ms_win_updates_ignored", value=total_ignored)
    else:
        yield Metric(name="ms_win_updates_ignored", value=0)

    # Check for critical updates (security updates, etc.)
    critical_updates = [u for u in windows_pending + sccm_pending 
                      if u.severity and u.severity.lower() in ['critical', 'important']]
    
    if critical_updates and params.get("alert_on_critical", False):
        yield Result(
            state=State.WARN,
            summary=f"{len(critical_updates)} critical/important updates pending"
        )

    # Check for updates requiring reboot
    reboot_updates = [u for u in windows_pending + sccm_pending 
                     if u.reboot_required]
    
    if reboot_updates:
        yield Result(
            state=State.OK,
            notice=f"{len(reboot_updates)} updates require reboot"
        )

    # Build detailed output
    result_details = []
    
    if windows_pending:
        result_details.append("Windows Update - Pending:\n" + 
            "\n".join(f"  • {_format_update_details(update)}" for update in windows_pending))
    
    if sccm_pending:
        result_details.append("SCCM - Pending:\n" + 
            "\n".join(f"  • {_format_update_details(update)}" for update in sccm_pending))
    
    if windows_ignored:
        result_details.append("Windows Update - Ignored:\n" + 
            "\n".join(f"  • {update.title}" for update in windows_ignored))
    
    if sccm_ignored:
        result_details.append("SCCM - Ignored:\n" + 
            "\n".join(f"  • {update.title}" for update in sccm_ignored))

    if result_details:
        yield Result(
            state=State.OK,
            notice=" ",
            details="\n\n".join(result_details),
        )


def _format_update_details(update: WindowsUpdate) -> str:
    """Format update details for display."""
    details = update.title
    
    info_parts = []
    if update.kb:
        info_parts.append(f"KB: {update.kb}")
    if update.severity:
        info_parts.append(f"Severity: {update.severity}")
    if update.size_mb:
        info_parts.append(f"Size: {update.size_mb}MB")
    if update.is_downloaded is not None:
        info_parts.append(f"Downloaded: {'Yes' if update.is_downloaded else 'No'}")
    if update.reboot_required:
        info_parts.append("Reboot required")
    if update.deadline:
        info_parts.append(f"Deadline: {update.deadline}")
    
    if info_parts:
        details += f" ({', '.join(info_parts)})"
    
    return details


agent_section_ms_win_update_v2 = AgentSection(
    name="ms_win_update_v2",
    parse_function=parse_ms_win_update_v2,
)


check_plugin_ms_win_update_v2 = CheckPlugin(
    name="ms_win_update_v2",
    service_name="Windows update",
    discovery_function=discover_ms_win_update_v2,
    check_function=check_ms_win_update_v2,
    check_ruleset_name="ms_win_update_v2",
    check_default_parameters={
        "update_count": ("fixed", (1.0, 5.0)),
        "monitor_sccm_client": True,
        "alert_on_critical": False,
    },
)
