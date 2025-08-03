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
# CHECKMK RULESET: Microsoft Windows Update (bakery plug-in)
#
# This file defines the deployment parameters for the ms_win_update.ps1 agent plug-in.
####################################################################################################

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    TimeMagnitude,
    TimeSpan,
)

from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_ms_win_update():
    return Dictionary(
        title=Title("Agent Plugin Parameters"),
        help_text=Help(
            "This will deploy an agent plugin to check the Windows updates on a Windows host."
        ),
        elements={
            "deployment": DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title("Deployment"),
                    help_text=Help(
                        "Select <tt>Deploy the plugin</tt> to install the agent plugin "
                        "<tt>ms_win_update.ps1</tt> on the host."
                    ),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="deploy_no",
                            title=Title("Do not deploy the plugin"),
                            parameter_form=FixedValue(value=None),
                        ),
                        CascadingSingleChoiceElement(
                            name="deploy_yes",
                            title=Title("Deploy the plugin"),
                            parameter_form=Dictionary(
                                elements={
                                    "interval": DictElement(
                                        parameter_form=TimeSpan(
                                            title=Title("Run Asynchronously"),
                                            help_text=Help(
                                                "Define an interval to limit the execution of "
                                                "the plugin on the host to save resources."
                                            ),
                                            displayed_magnitudes=[
                                                TimeMagnitude.MINUTE,
                                                TimeMagnitude.HOUR,
                                                TimeMagnitude.DAY,
                                            ],
                                            prefill=DefaultValue(300.0),
                                        ),
                                    ),
                                },
                            ),
                        ),
                    ],
                    prefill=DefaultValue("deploy_no"),
                ),
                required=True,
            ),
        },
    )


rule_spec_agent_config_ms_win_update = AgentConfig(
    title=Title("Microsoft Windows Update"),
    topic=Topic.OPERATING_SYSTEM,
    name="ms_win_update",
    parameter_form=_valuespec_agent_config_ms_win_update,
)
