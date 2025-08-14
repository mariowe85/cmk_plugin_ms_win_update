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
# CHECKMK RULESET: Microsoft Windows Update with SCCM Support (check plug-in)
#
# This file defines the check plug-in parameters for the enhanced "Microsoft Windows Update" check.
####################################################################################################

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    List,
    MatchingScope,
    RegularExpression,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostCondition,
    Topic,
)
from cmk.rulesets.v1.form_specs.validators import LengthInRange


def _parameter_form_ms_win_update_v2() -> Dictionary:
    return Dictionary(
        title=Title("Check Parameters"),
        help_text=Help(
            "Check parameters for Windows updates from both Windows Update and SCCM sources. "
            "To use this service, you need to deploy the <b>Windows Updates v2</b> agent plugin."
        ),
        elements={
            "update_count": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Total Pending Update Count"),
                    help_text=Help(
                        "Set upper thresholds for the total count of pending Windows updates "
                        "from all sources (Windows Update + SCCM).<br>"
                        'All pending updates that have not been ignored in "Ignored Update '
                        'Patterns" are counted.<br>To ignore the pending update count completely, '
                        'select "No levels".<br>The default values are 1 (WARN) and 5 (CRIT).'
                    ),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(1, 5)),
                ),
            ),
            "windows_update_count": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Windows Update Count"),
                    help_text=Help(
                        "Set separate upper thresholds specifically for Windows Update pending count. "
                        "This allows different thresholds for Windows Update vs SCCM updates."
                    ),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                ),
            ),
            "sccm_update_count": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("SCCM Update Count"),
                    help_text=Help(
                        "Set separate upper thresholds specifically for SCCM pending update count. "
                        "This allows different thresholds for SCCM vs Windows Update updates."
                    ),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                ),
            ),
            "monitor_sccm_client": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Monitor SCCM Client Status"),
                    help_text=Help(
                        "Enable monitoring of the SCCM client service status and version information. "
                        "When enabled, the check will report warnings if the SCCM client is not running."
                    ),
                    prefill=InputHint(True),
                ),
            ),
            "alert_on_critical": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Alert on Critical Updates"),
                    help_text=Help(
                        "Generate a warning state when critical or important security updates are pending, "
                        "regardless of the update count thresholds. This helps prioritize security patches."
                    ),
                    prefill=InputHint(False),
                ),
            ),
            "ignored_update_patterns": DictElement(
                parameter_form=List[str](
                    title=Title("Ignored Update Patterns"),
                    help_text=Help(
                        "Define a list of update names to be ignored for the pending update "
                        "thresholds. Updates matching these patterns will be excluded from "
                        "threshold calculations but still shown in service details."
                    ),
                    custom_validate=(LengthInRange(min_value=1),),
                    element_template=RegularExpression(
                        title=Title("Pattern"),
                        predefined_help_text=MatchingScope.INFIX,
                        custom_validate=(LengthInRange(min_value=1),),
                    ),
                ),
            ),
        },
    )


rule_spec_ms_win_update_v2 = CheckParameters(
    name="ms_win_update_v2",
    title=Title("Microsoft Windows Update with SCCM"),
    parameter_form=_parameter_form_ms_win_update_v2,
    topic=Topic.OPERATING_SYSTEM,
    condition=HostCondition(),
)
