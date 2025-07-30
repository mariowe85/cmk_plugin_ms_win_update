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
# Bakery plugin for the deployment of the Windows update script.
# This is part of the Microsoft Windows Update plugin (ms_win_update).


from pathlib import Path
from typing import Dict, Optional, Tuple, TypedDict

from .bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    register,
)


class WinUpdateConfig(TypedDict, total=False):
    deployment: Tuple[str, Optional[Dict[str, float]]]


def get_ms_win_update_files(conf: WinUpdateConfig) -> FileGenerator:
    deployment = conf["deployment"]

    if deployment[0] == "deploy_no":
        return

    interval = deployment[1].get("interval")

    yield Plugin(
        base_os=OS.WINDOWS,
        source=Path("ms_win_update.ps1"),
        interval=int(interval) if interval else None,
    )


register.bakery_plugin(
    name="ms_win_update",
    files_function=get_ms_win_update_files,
)
