#! /usr/bin/python
# _*_ coding: utf-8 _*_

#
# Dell EMC OpenManage Ansible Modules
#
# Copyright © 2017 Dell Inc. or its subsidiaries. All rights reserved.
# Dell, EMC, and other trademarks are trademarks of Dell Inc. or its
# subsidiaries. Other trademarks may be trademarks of their respective owners.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: dellemc_idrac_power
short_description: Configure the Power Cycle options on PowerEdge Server
version_added: "2.3"
description:
    - Configure the Power Cycle options on a Dell EMC PowerEdge Server
options:
  idrac_ip:
    required: True
    description:
      - iDRAC IP Address
    type: 'str'
  idrac_user:
    required: True
    description:
      - iDRAC user name
    type: 'str'
  idrac_pwd:
    required: True
    description:
      - iDRAC user password
    type: 'str'
  idrac_port:
    required: False
    description:
      - iDRAC port
    default: 443
    type: 'int'
  state:
    description:
      - if C(PowerOn), will Power On the server
      - if C(SoftPowerCycle), will close the running applications and Reboot the Server
      - if C(SoftPowerOff), will close the running applications and Power Off the server
      - if C(HardReset), will Reboot the Server immediately
      - if C(DiagnosticInterrupt), will reboot the Server for troubleshooting
      - if C(GracefulPowerOff), will close the running applications and Power Off the server
    choices: ["PowerOn", "SoftPowerCycle", "SoftPowerOff", "HardReset", "DiagnosticInterrupt", "GracefulPowerOff"]
    required: True

requirements: ['omsdk']
author: "anupam.aloke@dell.com"
'''

EXAMPLES = '''
---
- name: Power On the Server
    dellemc_idrac_power:
      idrac_ip:   "192.168.1.1"
      idrac_user: "username"
      idrac_pwd:  "pword"
      state:      "PowerOn"
'''

RETURN = '''
---
    "msg": {
        "Data": {
            "RequestPowerStateChange_OUTPUT": {
                                    "ReturnValue": "0"
            }
        }, 
        "Message": "none", 
        "Return": "Success", 
        "Status": "Success", 
        "retval": true
    }

'''

from ansible.module_utils.dellemc_idrac import iDRACConnection
from ansible.module_utils.basic import AnsibleModule
try:
    from omsdk.sdkcenum import TypeHelper
    from omdrivers.enums.iDRAC.iDRACEnums import PowerStateEnum
    HAS_OMSDK = True
except ImportError:
    HAS_OMSDK = False


def change_power_state(idrac, module):
    """
    Change Power State of PowerEdge Server

    Keywork arguments:
    idrac  -- iDRAC handle
    module -- Ansible module
    """

    msg = {}
    msg['msg'] = {}
    msg['changed'] = False
    msg['failed'] = False
    err = False

    power_state = None
    if module.params['state'] == "PowerOn":
        power_state = PowerStateEnum.PowerOn
    elif module.params['state'] == "SoftPowerCycle":
        power_state = PowerStateEnum.SoftPowerCycle
    elif module.params['state'] == "SoftPowerOff":
        power_state = PowerStateEnum.SoftPowerOff
    elif module.params['state'] == "HardReset":
        power_state = PowerStateEnum.HardReset
    elif module.params['state'] == "DiagnosticInterrupt":
        power_state = PowerStateEnum.DiagnosticInterrupt
    elif module.params['state'] == "GracefulPowerOff":
        power_state = PowerStateEnum.GracefulPowerOff

    current_power_state = idrac.PowerState
    is_power_on = (current_power_state == PowerStateEnum.PowerOn)

    try:
        if module.params['state'] == "PowerOn":
            if module.check_mode or is_power_on:
                msg['changed'] = not is_power_on
            else:
                msg['msg'] = idrac.config_mgr.change_power(power_state)
        elif module.params['state'] == "PowerOff":
            if module.check_mode or not is_power_on:
                msg['changed'] = is_power_on
            else:
                msg['msg'] = idrac.config_mgr.change_power(power_state)
        else:
            if module.check_mode:
                msg['changed'] = True
            else:
                msg['msg'] = idrac.config_mgr.change_power(power_state)

        if 'Status' in msg['msg']:
            if msg['msg']['Status'] == "Success":
                msg['changed'] = True
            else:
                msg['failed'] = True

    except Exception as e:
        err = True
        msg['msg'] = "Error: %s" % str(e)
        msg['failed'] = True

    return msg, err

# Main()
def main():

    module = AnsibleModule(
        argument_spec=dict(

            # iDRAC Handle
            idrac=dict(required=False, type='dict'),

            # iDRAC Credentials
            idrac_ip=dict(required=True, type='str'),
            idrac_user=dict(required=True, type='str'),
            idrac_pwd=dict(required=True, type='str', no_log=True),
            idrac_port=dict(required=False, default=443, type='int'),

            # Power Cycle State
            state=dict(required=True,
                       choice=["PowerOn", "SoftPowerCycle", "SoftPowerOff",
                               "HardReset", "DiagnosticInterrupt", "GracefulPowerOff"],
                       type='str')
            ),

        supports_check_mode=True)

    if not HAS_OMSDK:
        module.fail_json(msg="Dell EMC OpenManage Python SDK required for this module")

    # Connect to iDRAC
    idrac_conn = iDRACConnection(module)
    idrac = idrac_conn.connect()

    # Setup Power Cycle State
    (msg, err) = change_power_state(idrac, module)

    # Disconnect from iDRAC
    idrac_conn.disconnect()

    if err:
        module.fail_json(**msg)
    module.exit_json(**msg)

if __name__ == '__main__':
    main()
