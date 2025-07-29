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
# Checkmk graph parameters for Windows updates.
# These graph parameters are part of the Microsoft Windows Update plugin (ms_win_update).


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

metric_ms_win_updates_pending = Metric(
    name="ms_win_updates_pending",
    title=Title("Pending Updates"),
    unit=UNIT_COUNTER,
    color=Color.ORANGE,
)

metric_ms_win_updates_ignored = Metric(
    name="ms_win_updates_ignored",
    title=Title("Ignored Updates"),
    unit=UNIT_COUNTER,
    color=Color.DARK_GRAY,
)

graph_ms_win_updates = Graph(
    name="ms_win_updates",
    title=Title("Windows Updates"),
    compound_lines=[
        "ms_win_updates_pending",
        "ms_win_updates_ignored",
        WarningOf("ms_win_updates_pending"),
        CriticalOf("ms_win_updates_pending"),
    ],
)

perfometer_ms_win_updates_pending = Perfometer(
    name="ms_win_updates_pending",
    focus_range=FocusRange(Closed(0), Open(10)),
    segments=["ms_win_updates_pending", "ms_win_updates_ignored"],
)
