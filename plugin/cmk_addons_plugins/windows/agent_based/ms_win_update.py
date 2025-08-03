#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4; max-line-length: 100 -*-

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
# CHECKMK CHECK PLUG-IN: Microsoft Windows Update
#
# This plug-in generates the Checkmk services and determines their status.
# This file is part of the Microsoft Windows Update agent plug-in (ms_win_update.ps1).
####################################################################################################

# Example data from agent plug-in:
# <<<ms_win_update>>>
# SQL Server 2019 RTM Cumulative Update (CU) 30 KB5049235
# Security Intelligence Update for Microsoft Defender Antivirus - KB2267602 (Version 1.421.1334.0)


import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

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
    update_title: str


Section = list[WindowsUpdate]


def parse_ms_win_update(string_table: StringTable) -> Section:
    parsed = []
    for line in string_table:
        if line:
            update_title = " ".join(line).strip()
            if update_title:
                parsed.append(WindowsUpdate(update_title=update_title))

    return parsed


def discover_ms_win_update(section: Section) -> DiscoveryResult:
    yield Service()


def check_ms_win_update(params: Mapping[str, Any], section: Section) -> CheckResult:
    if not section:
        yield from check_levels(
            0,
            levels_upper=params.get("update_count"),
            metric_name="ms_win_updates_pending",
            label="Pending",
            render_func=int,
        )
        yield Metric(name="ms_win_updates_ignored", value=0)
        return

    ignored_patterns_param = params.get("ignored_update_patterns", [])

    compiled_patterns = [re.compile(pattern) for pattern in ignored_patterns_param]

    pending_updates = []
    ignored_updates = []

    for update in section:
        is_ignored = any(pattern.search(update.update_title) for pattern in compiled_patterns)

        if is_ignored:
            ignored_updates.append(update.update_title)
        else:
            pending_updates.append(update.update_title)

    result_details = []

    if pending_updates:
        result_details.append(
            "Pending Updates:\n"
            + "\n".join(f"\u00a0\u00a0• {update}" for update in pending_updates)
        )

    if ignored_updates:
        result_details.append(
            "Ignored Updates:\n"
            + "\n".join(f"\u00a0\u00a0• {update}" for update in ignored_updates)
        )

    result_details = "\n\n".join(result_details) if result_details else ""

    yield from check_levels(
        len(pending_updates),
        levels_upper=params.get("update_count"),
        metric_name="ms_win_updates_pending",
        label="Pending",
        render_func=int,
    )

    ignored_count = len(ignored_updates)

    if ignored_count > 0:
        yield from check_levels(
            ignored_count,
            metric_name="ms_win_updates_ignored",
            label="Ignored",
            render_func=int,
        )
    else:
        yield Metric(name="ms_win_updates_ignored", value=0)

    yield Result(
        state=State.OK,
        notice=" ",
        details=f"\n{result_details}",
    )


agent_section_ms_win_update = AgentSection(
    name="ms_win_update",
    parse_function=parse_ms_win_update,
)


check_plugin_ms_win_update = CheckPlugin(
    name="ms_win_update",
    service_name="Windows update",
    discovery_function=discover_ms_win_update,
    check_function=check_ms_win_update,
    check_ruleset_name="ms_win_update",
    check_default_parameters={"update_count": ("fixed", (1.0, 5.0))},
)
