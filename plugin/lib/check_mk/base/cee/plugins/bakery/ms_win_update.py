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
# CHECKMK BAKERY PLUG-IN: Microsoft Windows Update with SCCM Support
#
# This plug-in packages the enhanced agent script for deployment via the Checkmk agent bakery.
####################################################################################################

from pathlib import Path
from typing import TypedDict

from .bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    PluginConfig,
    register,
)


class WinUpdateConfigV2(TypedDict, total=False):
    deployment: tuple[str, dict[str, any] | None]


def get_ms_win_update_v2_files(conf: WinUpdateConfigV2) -> FileGenerator:
    deployment = conf["deployment"]

    if deployment[0] == "deploy_no":
        return

    config = deployment[1] or {}
    interval = config.get("interval")
    enable_sccm = config.get("enable_sccm", True)
    enable_windows_update = config.get("enable_windows_update", True)
    debug_mode = config.get("debug_mode", False)

    # Build PowerShell parameters based on configuration
    ps_params = []
    if not enable_sccm:
        ps_params.append("-EnableSCCM:$false")
    if not enable_windows_update:
        ps_params.append("-EnableWindowsUpdate:$false")
    if debug_mode:
        ps_params.append("-Debug")

    # Create plugin configuration
    plugin_config = None
    if ps_params:
        plugin_config = PluginConfig(
            arguments=ps_params
        )

    yield Plugin(
        base_os=OS.WINDOWS,
        source=Path("ms_win_update_v2.ps1"),
        interval=int(interval) if interval else None,
        config=plugin_config,
    )


register.bakery_plugin(
    name="ms_win_update_v2",
    files_function=get_ms_win_update_v2_files,
)
