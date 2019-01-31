#! /usr/bin/python
# _*_ coding: utf-8 _*_

#
# Dell EMC OpenManage Ansible Modules
# Version BETA
#
# Copyright (C) 2018 Dell Inc.

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# All rights reserved. Dell, EMC, and other trademarks are trademarks of Dell Inc. or its subsidiaries.
# Other trademarks may be trademarks of their respective owners.
#

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: dellemc_idrac_inventory
short_description: Returns the PowerEdge Server hardware inventory
version_added: "2.3"
description:
    - Returns the Dell EMC PowerEdge Server hardware inventory
options:
  idrac_ip:
    required: True
    description:
      - iDRAC IP Address
  idrac_user:
    required: True
    description:
      - iDRAC user name
  idrac_pwd:
    required: True
    description:
      - iDRAC user password
  idrac_port:
    required: False
    description:
      - iDRAC port
    default: 443

requirements: ['omsdk']
author: "anupam.aloke@dell.com"
'''

EXAMPLES = '''
---
- name: Get System Inventory
  dellemc_idrac_inventory:
    idrac_ip:   "192.168.1.1"
    idrac_user: "username"
    idrac_pwd:  "pword"
'''

RETURN = '''
---
'''

from ansible.module_utils.dellemc_idrac import iDRACConnection
from ansible.module_utils.basic import AnsibleModule

def get_system_inventory(idrac):
    """
    Returns the hardware inventory

    Keyword arguments:
    idrac  -- iDRAC handle
    """

    msg = {}
    msg['changed'] = False
    msg['failed'] = False
    err = False

    try:
        idrac.get_entityjson()
        msg['msg'] = idrac.get_json_device()
    except Exception as e:
        err = True
        msg['msg'] = "Error: %s" % str(e)
        msg['failed'] = True

    return msg, err

# Main
def main():

    module = AnsibleModule(
        argument_spec=dict(

            # iDRAC Handle
            idrac=dict(required=False, type='dict'),

            # iDRAC credentials
            idrac_ip=dict(required=True, type='str'),
            idrac_user=dict(required=True, type='str'),
            idrac_pwd=dict(required=True, type='str', no_log=True),
            idrac_port=dict(required=False, default=443, type='int')
        ),

        supports_check_mode=True)

    # Connect to iDRAC
    idrac_conn = iDRACConnection(module)
    idrac = idrac_conn.connect()

    # Get System Inventory
    msg, err = get_system_inventory(idrac)

    # Disconnect from iDRAC
    idrac_conn.disconnect()

    if err:
        module.fail_json(**msg)
    module.exit_json(ansible_facts = {idrac.ipaddr: {'SystemInventory': msg['msg']}})


if __name__ == '__main__':
    main()
