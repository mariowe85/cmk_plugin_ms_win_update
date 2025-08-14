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
# CHECKMK RULESET: Microsoft Windows Update with SCCM Support (bakery plug-in)
#
# This file defines the deployment parameters for the ms_win_update_v2.ps1 agent plug-in.
####################################################################################################

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    InputHint,
    TimeMagnitude,
    TimeSpan,
)

from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_ms_win_update_v2():
    return Dictionary(
        title=Title("Agent Plugin Parameters"),
        help_text=Help(
            "This will deploy an enhanced agent plugin to check Windows updates from both "
            "Windows Update and SCCM sources on a Windows host."
        ),
        elements={
            "deployment": DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title("Deployment"),
                    help_text=Help(
                        "Select <tt>Deploy the plugin</tt> to install the enhanced agent plugin "
                        "<tt>ms_win_update_v2.ps1</tt> on the host."
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
                                                "the plugin on the host to save resources. "
                                                "Recommended: 300 seconds (5 minutes) or higher "
                                                "as update checks can be resource intensive."
                                            ),
                                            displayed_magnitudes=[
                                                TimeMagnitude.MINUTE,
                                                TimeMagnitude.HOUR,
                                                TimeMagnitude.DAY,
                                            ],
                                            prefill=DefaultValue(300.0),
                                        ),
                                    ),
                                    "enable_sccm": DictElement(
                                        parameter_form=BooleanChoice(
                                            title=Title("Enable SCCM Monitoring"),
                                            help_text=Help(
                                                "Enable monitoring of SCCM (System Center Configuration Manager) "
                                                "updates in addition to Windows Update. This will check for "
                                                "pending updates managed by SCCM and monitor the SCCM client status."
                                            ),
                                            prefill=InputHint(True),
                                        ),
                                    ),
                                    "enable_windows_update": DictElement(
                                        parameter_form=BooleanChoice(
                                            title=Title("Enable Windows Update Monitoring"),
                                            help_text=Help(
                                                "Enable monitoring of standard Windows Update. "
                                                "You may want to disable this if your environment "
                                                "exclusively uses SCCM for update management."
                                            ),
                                            prefill=InputHint(True),
                                        ),
                                    ),
                                    "debug_mode": DictElement(
                                        parameter_form=BooleanChoice(
                                            title=Title("Enable Debug Mode"),
                                            help_text=Help(
                                                "Enable debug output in the agent plugin for troubleshooting. "
                                                "Debug information will be written to the Windows Event Log. "
                                                "Disable this in production environments."
                                            ),
                                            prefill=InputHint(False),
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


rule_spec_agent_config_ms_win_update_v2 = AgentConfig(
    title=Title("Microsoft Windows Update with SCCM"),
    topic=Topic.OPERATING_SYSTEM,
    name="ms_win_update_v2",
    parameter_form=_valuespec_agent_config_ms_win_update_v2,
)
