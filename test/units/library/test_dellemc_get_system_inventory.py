#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Dell EMC OpenManage Ansible Modules
# Version 2.0.14
# Copyright (C) 2020 Dell Inc. or its subsidiaries. All Rights Reserved.

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import

import pytest
from ansible.modules.remote_management.dellemc import dellemc_get_system_inventory
from units.modules.remote_management.dellemc.common import FakeAnsibleModule, Constants
from units.compat.mock import MagicMock, Mock
from units.compat.mock import PropertyMock
from units.modules.utils import set_module_args, exit_json, fail_json, AnsibleFailJson, AnsibleExitJson
from pytest import importorskip

importorskip("omsdk.sdkfile")
importorskip("omsdk.sdkcreds")


class TestSystemInventory(FakeAnsibleModule):
    module = dellemc_get_system_inventory

    @pytest.fixture
    def idrac_system_inventory_mock(self, mocker):
        omsdk_mock = MagicMock()
        idrac_obj = MagicMock()
        omsdk_mock.get_entityjson = idrac_obj
        type(idrac_obj).get_json_device = Mock(return_value="msg")
        return idrac_obj

    @pytest.fixture
    def idrac_get_system_inventory_connection_mock(self, mocker, idrac_system_inventory_mock):
        idrac_conn_class_mock = mocker.patch('ansible.modules.remote_management.dellemc.'
                                             'dellemc_get_system_inventory.iDRACConnection',
                                             return_value=idrac_system_inventory_mock)
        idrac_conn_class_mock.return_value.__enter__.return_value = idrac_system_inventory_mock
        return idrac_system_inventory_mock

    def test_main_idrac_get_system_inventory_success_case01(self, idrac_get_system_inventory_connection_mock, mocker,
                                                            idrac_default_args):
        mocker.patch('ansible.modules.remote_management.dellemc.dellemc_get_system_inventory.run_get_system_inventory',
                     return_value=({"msg": "Success"}, False))
        msg = self._run_module(idrac_default_args)
        assert msg['changed'] is False
        assert msg['ansible_facts'] == {idrac_get_system_inventory_connection_mock.ipaddr:
                                        {'SystemInventory': "Success"}}

    def test_run_get_system_inventory_error_case(self, idrac_get_system_inventory_connection_mock, idrac_default_args,
                                                 mocker):
        f_module = self.get_module_mock()
        idrac_get_system_inventory_connection_mock.get_json_device = {"msg": "Success"}
        result, err = self.module.run_get_system_inventory(idrac_get_system_inventory_connection_mock, f_module)
        assert result["failed"] is True
        assert err is True

    def test_main_error_case(self, idrac_get_system_inventory_connection_mock, idrac_default_args, mocker):
        mocker.patch('ansible.modules.remote_management.dellemc.dellemc_get_system_inventory.run_get_system_inventory',
                     return_value=({"msg": "Failed"}, True))
        result = self._run_module_with_fail_json(idrac_default_args)
        assert result['failed'] is True

    @pytest.mark.parametrize("exc_type", [ImportError, ValueError, RuntimeError])
    def test_main_exception_handling_case(self, exc_type, mocker, idrac_default_args,
                                          idrac_get_system_inventory_connection_mock):

        mocker.patch('ansible.modules.remote_management.dellemc.dellemc_get_system_inventory.run_get_system_inventory',
                     side_effect=exc_type('test'))
        result = self._run_module_with_fail_json(idrac_default_args)
        assert 'msg' in result
        assert result['failed'] is True
