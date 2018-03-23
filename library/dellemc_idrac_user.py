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
module: dellemc_idrac_user
short_description: Configures an iDRAC local User
version_added: "2.3"
description:
    - Configures an iDRAC local user
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
  share_name:
    required: True
    description:
      - CIFS or NFS Network share
    type: 'str'
  share_user:
    required: False
    description:
      - Network share user in the format 'user@domain' if user is part of domain, else 'user'
    type: 'str'
  share_pwd:
    required: False
    description:
      - Network share user password
    type: 'str'
  share_mnt:
    required: False
    description:
      - Local mount path of the network file share with read-write permission for ansible user
    type: 'str'
  user_name:
    required: True
    description:
      - User name to be configured
    type: 'str'
  user_pwd:
    required: False
    description:
      - User password
    default: None
    type: 'str'
  user_priv:
    required: False
    description: User privileges
    choices: ['Administrator', 'Operator', 'ReadOnly', 'NoAccess']
    default: None
  state:
    description:
      - if C(present), will create/add/modify an user
      - if C(absent), will delete the user
      - if C(enable), will enable the user
      - if C(disable), will disable the user
    choices: ['present', 'absent', 'enable','disable']
    default: 'present'

requirements: ['omsdk']
author: anupam.aloke@dell.com
'''

EXAMPLES = '''
---
- name: Add a new iDRAC User
    dellemc_idrac_user:
      idrac_ip:   "192.168.1.1"
      idrac_user: "root"
      idrac_pwd:  "calvin"
      share_name: "\\\\192.168.10.10\\share"
      share_user: "user1"
      share_pwd:  "password"
      share_mnt:  "/mnt/share"
      user_name:  "newuser"
      user_pwd:   "password"
      user_priv:  "Administrator"
      state:      "present"

- name: Change password for the "newuser"
    dellemc_idrac_user:
      idrac_ip:   "192.168.1.1"
      idrac_user: "root"
      idrac_pwd:  "calvin"
      share_name: "\\\\192.168.10.10\\share"
      share_user: "user1"
      share_pwd:  "password"
      share_mnt:  "/mnt/share"
      user_name:  "newuser"
      user_pwd:   "newpassword"
      state:      "present"

- name: Change privilege for the "newuser"
    dellemc_idrac_user:
      idrac_ip:   "192.168.1.1"
      idrac_user: "root"
      idrac_pwd:  "calvin"
      share_name: "\\\\192.168.10.10\\share"
      share_user: "user1"
      share_pwd:  "password"
      share_mnt:  "/mnt/share"
      user_name:  "newuser"
      user_priv:  "Operator"
      state:      "present"

- name: Delete "newuser"
    dellemc_idrac_user:
      idrac_ip:   "192.168.1.1"
      idrac_user: "root"
      idrac_pwd:  "calvin"
      share_name: "\\\\192.168.10.10\\share"
      share_user: "user1"
      share_pwd:  "password"
      share_mnt:  "/mnt/share"
      user_name:  "newuser"
      state:      "absent"
'''

RETURN = '''
---
'''

from ansible.module_utils.dellemc_idrac import iDRACConnection
from ansible.module_utils.basic import AnsibleModule

try:
    from omsdk.sdkcenum import TypeHelper
    from omdrivers.enums.iDRAC.iDRAC import (
        Enable_UsersTypes, Privilege_UsersTypes
    )
    HAS_OMSDK = True
except ImportError:
    HAS_OMSDK = False


def setup_idrac_user(idrac, module):
    """
    Setup iDRAC local user

    Keyword arguments:
    idrac  -- iDRAC handle
    module -- Ansible module
    """

    msg = {}
    msg['changed'] = False
    msg['failed'] = False
    msg['msg'] = {}
    err = False

    user_name = module.params['user_name']
    user_pwd = module.params['user_pwd']
    user_priv = None

    if module.params['user_priv']:
        if module.params['user_priv'] == "Administrator":
            user_priv = Privilege_UsersTypes.Administrator
        elif module.params['user_priv'] == "Operator":
            user_priv = Privilege_UsersTypes.Operator
        elif module.params['user_priv'] == "ReadOnly":
            user_priv = Privilege_UsersTypes.ReadOnly

    try:
        # Check if user exists
        user = idrac.config_mgr._sysconfig.iDRAC.Users.find_first(UserName_Users=user_name)

        if module.params["state"] == "present":
            if not user:
                # Set the iDRAC user privilege to NoAccess if not provided
                if user_priv is None:
                    user_priv = Privilege_UsersTypes.NoAccess

                idrac.user_mgr.Users.new(
                                   UserName_Users=user_name.lower(),
                                   Password_Users=user_pwd,
                                   Privilege_Users=user_priv,
                                   Enable_Users=Enable_UsersTypes.Enabled)
            else:
                if user.Enable_Users.get_value() != Enable_UsersTypes.Enabled:
                    user.Enable_Users.set_value(Enable_UsersTypes.Enabled)

                if user_priv:
                    user.Privilege_Users.set_value(user_priv)

                if user_pwd is not None:
                    user.Password_Users.set_value(user_pwd)

        elif module.params["state"] == "enable":
            if user:
                user.Enable_Users.set_value(Enable_UsersTypes.Enabled)
            else:
                msg['msg'] = "User: " + user_name + " does not exist"
                msg['failed'] = True
                return msg

        elif module.params["state"] == "disable":
            if user:
                user.Enable_Users.set_value(Enable_UsersTypes.Disabled)
            else:
                msg['msg'] = "User: " + user_name + " does not exist"
                msg['failed'] = True
                return msg

        elif module.params["state"] == "absent":
            if user:
                idrac.config_mgr._sysconfig.iDRAC.Users.remove(UserName_Users = user_name)
            else:
                msg['msg'] = "User: " + user_name + " does not exist"
                msg['failed'] = True
                return msg

        msg['changed'] = idrac.config_mgr._sysconfig.is_changed()

        if module.check_mode:
            # Since it is running in check mode, reject the changes
            idrac.config_mgr._sysconfig.reject()
        else:
            msg['msg'] = idrac.config_mgr.apply_changes()

            if "Status" in msg['msg'] and msg['msg']['Status'] != "Success":
                msg['failed'] = True
                msg['changed'] = False

    except Exception as e:
        err = False
        msg['msg'] = "Error: %s" % str(e)
        msg['failed'] = True

    return msg, err

# Main
def main():

    module = AnsibleModule(
        argument_spec=dict(
            # iDRAC handle
            idrac=dict(required=False, type='dict'),

            # iDRAC credentials
            idrac_ip=dict(required=True, type='str'),
            idrac_user=dict(required=True, type='str'),
            idrac_pwd=dict(required=True, type='str', no_log=True),
            idrac_port=dict(required=False, default=443, type='int'),

            # Network File Share
            share_name=dict(required=True, type='str'),
            share_user=dict(required=False, type='str'),
            share_pwd=dict(required=False, type='str', no_log=True),
            share_mnt=dict(required=False, type='path'),

            # Local user credentials
            user_name=dict(required=True, type='str'),
            user_pwd=dict(required=False, default=None, type='str', no_log=True),
            user_priv=dict(required=False,
                           choices=['Administrator', 'Operator', 'ReadOnly', 'NoAccess'],
                           default=None),

            # State
            state=dict(required=False,
                       choices=['present', 'absent', 'enable', 'disable'],
                       default='present')
        ),
        supports_check_mode=True)

    if not HAS_OMSDK:
        module.fail_json(msg="Dell EMC OpenManage Python SDK required for this module")

    # Connect to iDRAC
    idrac_conn = iDRACConnection(module)
    idrac = idrac_conn.connect()

    # Setup network share as local mount
    if not idrac_conn.setup_nw_share_mount():
        module.fail_json(msg="Failed to setup network share local mount point")

    # Setup User
    msg, err = setup_idrac_user(idrac, module)

    # Disconnect from iDRAC
    idrac_conn.disconnect()

    if err:
        module.fail_json(**msg)
    module.exit_json(**msg)


if __name__ == '__main__':
    main()
