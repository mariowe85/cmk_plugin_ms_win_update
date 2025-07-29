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
# Checkmk ruleset to set the thresholds and excludes of Windows updates.
# This ruleset is part of the Microsoft Windows Update plugin (ms_win_update).


from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
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


def _parameter_form_ms_win_update() -> Dictionary:
    return Dictionary(
        title=Title("Check Parameters"),
        help_text=Help(
            "Check parameters for the count of Windows updates. "
            "To use this service, you need to deploy the <b>Windows Updates</b> agent plugin."
        ),
        elements={
            "update_count": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Pending Update Count"),
                    help_text=Help(
                        "Set upper level thresholds for the count of pending Windows updates. "
                        "All pending updates that have not been ignored are counted."
                    ),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(1, 5)),
                ),
            ),
            "ignored_update_patterns": DictElement(
                parameter_form=List[str](
                    title=Title("Ignored Update Patterns"),
                    help_text=Help(
                        "Define a list of update names to be ignored for the pending update "
                        "thresholds."
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


rule_spec_ms_win_update = CheckParameters(
    name="ms_win_update",
    title=Title("Microsoft Windows Update"),
    parameter_form=_parameter_form_ms_win_update,
    topic=Topic.OPERATING_SYSTEM,
    condition=HostCondition(),
)
