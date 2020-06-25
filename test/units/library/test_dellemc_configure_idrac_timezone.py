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
from ansible.modules.remote_management.dellemc import dellemc_configure_idrac_timezone
from units.modules.remote_management.dellemc.common import FakeAnsibleModule, Constants
from units.compat.mock import MagicMock, patch, Mock
from units.modules.utils import set_module_args, exit_json, fail_json, AnsibleFailJson, AnsibleExitJson
from units.compat.mock import PropertyMock
from pytest import importorskip

importorskip("omsdk.sdkfile")
importorskip("omsdk.sdkcreds")


class TestConfigTimezone(FakeAnsibleModule):
    module = dellemc_configure_idrac_timezone

    @pytest.fixture
    def idrac_configure_timezone_mock(self, mocker):
        omsdk_mock = MagicMock()
        idrac_obj = MagicMock()
        omsdk_mock.file_share_manager = idrac_obj
        omsdk_mock.config_mgr = idrac_obj
        type(idrac_obj).create_share_obj = Mock(return_value="servicesstatus")
        type(idrac_obj).set_liason_share = Mock(return_value="servicestatus")
        return idrac_obj

    @pytest.fixture
    def idrac_file_manager_config_timesone_mock(self, mocker):
        try:
            file_manager_obj = mocker.patch(
                'ansible.modules.remote_management.dellemc.dellemc_configure_idrac_timezone.file_share_manager')
        except AttributeError:
            file_manager_obj = MagicMock()
        obj = MagicMock()
        file_manager_obj.create_share_obj.return_value = obj
        return file_manager_obj

    @pytest.fixture
    def is_changes_applicable_timezone_mock(self, mocker):
        try:
            changes_applicable_mock = mocker.patch('ansible.modules.remote_management.dellemc.'
                                            'dellemc_configure_idrac_timezone.config_mgr')
        except AttributeError:
            changes_applicable_mock = MagicMock()
        obj = MagicMock()
        changes_applicable_mock.is_change_applicable.return_value = obj
        return changes_applicable_mock

    @pytest.fixture
    def idrac_connection_configure_timezone_mock(self, mocker, idrac_configure_timezone_mock):
        idrac_conn_class_mock = mocker.patch('ansible.modules.remote_management.dellemc.'
                                             'dellemc_configure_idrac_timezone.iDRACConnection',
                                             return_value=idrac_configure_timezone_mock)
        idrac_conn_class_mock.return_value.__enter__.return_value = idrac_configure_timezone_mock
        return idrac_configure_timezone_mock

    def test_main_idrac_timezone_config_success_Case(self, idrac_connection_configure_timezone_mock, idrac_default_args,
                                                     mocker, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename"})
        message = {'changed': False, 'msg': {'Status': "Success", "message": "No changes found to commit!"}}
        mocker.patch('ansible.modules.remote_management.dellemc.'
                     'dellemc_configure_idrac_timezone.run_idrac_timezone_config', return_value=(message, False))
        result = self._run_module(idrac_default_args)
        assert result == {'changed': False, 'msg': {'Status': 'Success', "message": "No changes found to commit!"}}

    def test_run_idrac_timezone_config_success_case01(self, idrac_connection_configure_timezone_mock,
                                                      idrac_default_args, idrac_file_manager_config_timesone_mock,
                                                      is_changes_applicable_timezone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": "setuptimezone",
                                   "enable_ntp": "Enabled", "ntp_server_1": "ntp server1",
                                   "ntp_server_2": "ntp server2", "ntp_server_3": "ntp server3"})
        message = {"changes_applicable": True, "message": "changes are applicable"}
        idrac_connection_configure_timezone_mock.config_mgr.is_change_applicable.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args, check_mode=True)
        msg, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert msg == {"changed": True, "failed": False, "msg": {"changes_applicable": True,
                                                                 "message": "changes are applicable"}}
        assert msg['changed'] is True
        assert msg['failed'] is False

    def test_run_idrac_timezone_config_success_case02(self, idrac_connection_configure_timezone_mock,
                                                      idrac_default_args, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": "setuptimezone",
                                   "enable_ntp": "Enabled", "ntp_server_1": "ntp server1",
                                   "ntp_server_2": "ntp server2", "ntp_server_3": "ntp server3"})
        message = {"changes_applicable": True, "message": "changes found to commit!", "changed": True,
                   "Status": "Success"}
        idrac_connection_configure_timezone_mock.config_mgr.apply_changes.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args)
        f_module.check_mode = False
        msg, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert msg == {'msg': {'Status': 'Success', 'message': 'changes found to commit!', 'changed': True,
                               'changes_applicable': True}, 'failed': False, 'changed': True}
        assert msg['changed'] is True
        assert msg['failed'] is False

    def test_run_idrac_timezone_config_success_case03(self, idrac_connection_configure_timezone_mock,
                                                      idrac_default_args, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": "setuptimezone",
                                   "enable_ntp": "Enabled", "ntp_server_1": "ntp server1",
                                   "ntp_server_2": "ntp server2", "ntp_server_3": "ntp server3"})
        message = {"changes_applicable": False, "Message": "No changes found to commit!", "changed": False,
                   "Status": "Success"}
        idrac_connection_configure_timezone_mock.config_mgr.apply_changes.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args)
        f_module.check_mode = False
        msg, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert msg == {'msg': {'Status': 'Success', 'Message': 'No changes found to commit!', 'changed': False,
                               'changes_applicable': False}, 'failed': False, 'changed': False}
        assert msg['changed'] is False
        assert msg['failed'] is False

    def test_run_idrac_timezone_config_success_case04(self, idrac_connection_configure_timezone_mock,
                                                      idrac_default_args, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": "setuptimezone",
                                   "enable_ntp": "Enabled", "ntp_server_1": "ntp server1",
                                   "ntp_server_2": "ntp server2", "ntp_server_3": "ntp server3"})
        message = {"changes_applicable": False, "Message": "No changes found to commit!", "changed": False,
                   "Status": "Success"}
        idrac_connection_configure_timezone_mock.config_mgr.apply_changes.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args)
        f_module.check_mode = False
        msg, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert msg == {'msg': {'Status': 'Success', 'Message': "No changes found to commit!", 'changed': False,
                               'changes_applicable': False}, 'failed': False, 'changed': False}
        assert msg['changed'] is False
        assert msg['failed'] is False

    def test_run_idrac_timezone_config_success_case05(self, idrac_connection_configure_timezone_mock,
                                                      idrac_default_args, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": None,
                                   "enable_ntp": None, "ntp_server_1": None, "ntp_server_2": None,
                                   "ntp_server_3": None})
        message = {"changes_applicable": False, "Message": "No changes found to commit!", "changed": False,
                   "Status": "Success"}
        idrac_connection_configure_timezone_mock.config_mgr.configure_timezone.return_value = message
        idrac_connection_configure_timezone_mock.config_mgr.configure_ntp.return_value = message
        idrac_connection_configure_timezone_mock.config_mgr.apply_changes.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args)
        f_module.check_mode = False
        msg, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert msg == {'msg': {'Status': 'Success', 'Message': "No changes found to commit!", 'changed': False,
                               'changes_applicable': False}, 'failed': False, 'changed': False}
        assert msg['changed'] is False
        assert msg['failed'] is False

    def test_run_idrac_timezone_config_failed_case01(self, idrac_connection_configure_timezone_mock,
                                                     idrac_default_args, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": "setuptimezone",
                                   "enable_ntp": "Enabled", "ntp_server_1": "ntp server1",
                                   "ntp_server_2": "ntp server2", "ntp_server_3": "ntp server3"})
        message = {'Status': 'Failed', "Data": {'Message': 'status failed in checking Data'}}
        idrac_connection_configure_timezone_mock.file_share_manager.create_share_obj.return_value = "mnt/iso"
        idrac_connection_configure_timezone_mock.config_mgr.set_liason_share.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args)
        result, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert result == {'msg': 'status failed in checking Data', 'failed': True, 'changed': False}
        assert err is True

    def test_run_idrac_timezone_config_failed_case02(self, idrac_connection_configure_timezone_mock,
                                                     idrac_default_args, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": "setuptimezone",
                                   "enable_ntp": "Enabled", "ntp_server_1": "ntp server1",
                                   "ntp_server_2": "ntp server2", "ntp_server_3": "ntp server3"})
        message = {"changes_applicable": False, "Message": "No changes were applied", "changed": False,
                   "Status": "failed"}
        idrac_connection_configure_timezone_mock.config_mgr.apply_changes.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args)
        f_module.check_mode = False
        msg, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert msg == {'msg': {'Status': 'failed', 'Message': 'No changes were applied', 'changed': False,
                               'changes_applicable': False}, 'failed': True, 'changed': False}
        assert msg['changed'] is False
        assert msg['failed'] is True

    def test_run_idrac_timezone_config_failed_case03(self, idrac_connection_configure_timezone_mock,
                                                     idrac_default_args, idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename", "share_mnt": "mountname", "share_user": "shareuser",
                                   "share_password": "sharepassword", "setup_idrac_timezone": "setuptimezone",
                                   "enable_ntp": "Enabled", "ntp_server_1": "ntp server1",
                                   "ntp_server_2": "ntp server2", "ntp_server_3": "ntp server3"})
        message = {'Status': 'Failed', "Data": {'Message': "Failed to found changes"}}
        idrac_connection_configure_timezone_mock.file_share_manager.create_share_obj.return_value = "mnt/iso"
        idrac_connection_configure_timezone_mock.config_mgr.set_liason_share.return_value = message
        f_module = self.get_module_mock(params=idrac_default_args)
        msg, err = self.module.run_idrac_timezone_config(idrac_connection_configure_timezone_mock, f_module)
        assert msg == {'changed': False, 'failed': True, 'msg': 'Failed to found changes'}
        assert msg['changed'] is False
        assert msg['failed'] is True
        assert err is True

    def test_main_configure_timezone_failure_case(self, idrac_connection_configure_timezone_mock, idrac_default_args,
                                                  idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename"})
        error_msg = "Error in Runtime"
        obj2 = MagicMock()
        idrac_connection_configure_timezone_mock.file_share_manager = obj2
        idrac_connection_configure_timezone_mock.config_mgr = obj2
        type(obj2).create_share_obj = Mock(side_effect=Exception(error_msg))
        type(obj2).set_liason_share = Mock(side_effect=Exception(error_msg))
        msg = self._run_module_with_fail_json(idrac_default_args)
        assert msg['failed'] is True
        assert msg['msg'] == "Error: {0}".format(error_msg)

    @pytest.mark.parametrize("exc_type", [ImportError, ValueError, RuntimeError])
    def test_main_idrac_configure_timezone_exception_handling_case(self, exc_type, mocker, idrac_default_args,
                                                                   idrac_connection_configure_timezone_mock,
                                                                   idrac_file_manager_config_timesone_mock):
        idrac_default_args.update({"share_name": "sharename"})
        mocker.patch('ansible.modules.remote_management.dellemc.'
                     'dellemc_configure_idrac_timezone.run_idrac_timezone_config', side_effect=exc_type('test'))
        result = self._run_module_with_fail_json(idrac_default_args)
        assert 'msg' in result
        assert result['failed'] is True
