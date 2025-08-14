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
# CHECKMK METRICS & GRAPHS: Microsoft Windows Update with SCCM Support
#
# This file defines the enhanced Checkmk metrics and graphs for the check plug-ins.
####################################################################################################

from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph
from cmk.graphing.v1.metrics import (
    Color,
    CriticalOf,
    DecimalNotation,
    Metric,
    StrictPrecision,
    Unit,
    WarningOf,
)
from cmk.graphing.v1.perfometers import Closed, Open, FocusRange, Perfometer

UNIT_COUNTER = Unit(DecimalNotation(""), StrictPrecision(0))

# --------------------------------------------------------------------------------------------------
# Microsoft Windows Update with SCCM Support
# --------------------------------------------------------------------------------------------------

metric_ms_win_updates_pending = Metric(
    name="ms_win_updates_pending",
    title=Title("Total Pending Updates"),
    unit=UNIT_COUNTER,
    color=Color.ORANGE,
)

metric_ms_win_updates_windows_pending = Metric(
    name="ms_win_updates_windows_pending",
    title=Title("Windows Update Pending"),
    unit=UNIT_COUNTER,
    color=Color.BLUE,
)

metric_ms_win_updates_sccm_pending = Metric(
    name="ms_win_updates_sccm_pending",
    title=Title("SCCM Pending Updates"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_ms_win_updates_ignored = Metric(
    name="ms_win_updates_ignored",
    title=Title("Ignored Updates"),
    unit=UNIT_COUNTER,
    color=Color.DARK_GRAY,
)

# Main graph showing all update sources
graph_ms_win_updates_v2 = Graph(
    name="ms_win_updates_v2",
    title=Title("Windows Updates (Enhanced)"),
    compound_lines=[
        "ms_win_updates_pending",
        "ms_win_updates_windows_pending", 
        "ms_win_updates_sccm_pending",
        "ms_win_updates_ignored",
        WarningOf("ms_win_updates_pending"),
        CriticalOf("ms_win_updates_pending"),
    ],
)

# Separate graph for update sources breakdown
graph_ms_win_updates_sources = Graph(
    name="ms_win_updates_sources",
    title=Title("Windows Updates by Source"),
    compound_lines=[
        "ms_win_updates_windows_pending",
        "ms_win_updates_sccm_pending",
        "ms_win_updates_ignored",
    ],
)

# Enhanced perfometer showing total pending with source breakdown
perfometer_ms_win_updates_v2 = Perfometer(
    name="ms_win_updates_v2",
    focus_range=FocusRange(Closed(0), Open(15)),
    segments=[
        "ms_win_updates_windows_pending",
        "ms_win_updates_sccm_pending", 
        "ms_win_updates_ignored"
    ],
)

# Perfometer for Windows Update only
perfometer_ms_win_updates_windows = Perfometer(
    name="ms_win_updates_windows",
    focus_range=FocusRange(Closed(0), Open(10)),
    segments=["ms_win_updates_windows_pending"],
)

# Perfometer for SCCM only
perfometer_ms_win_updates_sccm = Perfometer(
    name="ms_win_updates_sccm", 
    focus_range=FocusRange(Closed(0), Open(10)),
    segments=["ms_win_updates_sccm_pending"],
)
