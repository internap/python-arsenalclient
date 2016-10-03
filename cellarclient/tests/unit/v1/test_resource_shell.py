# Copyright 2013 IBM Corp
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import mock

from oslo_utils import uuidutils

from cellarclient.common.apiclient import exceptions
from cellarclient.common import cliutils
from cellarclient.common import utils as commonutils
from cellarclient.tests.unit import utils
import cellarclient.v1.resource_shell as r_shell


class ResourceShellTest(utils.BaseTestCase):
    def _get_client_mock_args(self, resource=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False,
                              fields=None, json=False):
        args = mock.MagicMock(spec=True)
        args.resource = resource
        args.marker = marker
        args.limit = limit
        args.sort_dir = sort_dir
        args.sort_key = sort_key
        args.detail = detail
        args.fields = fields
        args.json = json

        return args

    def test_resource_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            resource = object()
            r_shell._print_resource_show(resource)
        exp = ['created_at', 'description', 'type', 'relations', 'attributes', 'updated_at', 'uuid']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_resource_show_space_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = '   '
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_show,
                          client_mock, args)

    def test_do_resource_show_empty_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = ''
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_show,
                          client_mock, args)

    def test_do_resource_show_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = 'resource_uuid'
        args.fields = [['uuid', 'description']]
        args.json = False
        r_shell.do_resource_show(client_mock, args)
        client_mock.resource.get.assert_called_once_with(
            'resource_uuid', fields=['uuid', 'description'])

    def test_do_resource_show_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = 'resource_uuid'
        args.fields = [['foo', 'bar']]
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_show,
                          client_mock, args)

    def test_do_resource_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        r_shell.do_resource_list(client_mock, args)
        client_mock.resource.list.assert_called_once_with(detail=False)

    def test_do_resource_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        r_shell.do_resource_list(client_mock, args)
        client_mock.resource.list.assert_called_once_with(detail=True)

    def test_do_resource_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='created_at',
                                          detail=False)

        r_shell.do_resource_list(client_mock, args)
        client_mock.resource.list.assert_called_once_with(sort_key='created_at',
                                                         detail=False)

    def test_do_resource_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='attributes',
                                          detail=False)
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_list,
                          client_mock, args)
        self.assertFalse(client_mock.resource.list.called)

    def test_do_resource_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='created_at',
                                          detail=True)

        r_shell.do_resource_list(client_mock, args)
        client_mock.resource.list.assert_called_once_with(sort_key='created_at',
                                                         detail=True)

    def test_do_resource_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='attributes',
                                          detail=True)

        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_list,
                          client_mock, args)
        self.assertFalse(client_mock.resource.list.called)

    def test_do_resource_list_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='desc',
                                          detail=False)

        r_shell.do_resource_list(client_mock, args)
        client_mock.resource.list.assert_called_once_with(sort_dir='desc',
                                                         detail=False)

    def test_do_resource_list_detail_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='asc',
                                          detail=True)

        r_shell.do_resource_list(client_mock, args)
        client_mock.resource.list.assert_called_once_with(sort_dir='asc',
                                                         detail=True)

    def test_do_resource_list_wrong_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='abc',
                                          detail=False)
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_list,
                          client_mock, args)
        self.assertFalse(client_mock.resource.list.called)

    def test_do_resource_list_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['uuid', 'description']])
        r_shell.do_resource_list(client_mock, args)
        client_mock.resource.list.assert_called_once_with(
            fields=['uuid', 'description'], detail=False)

    def test_do_resource_list_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['foo', 'bar']])
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_list,
                          client_mock, args)

    def test_do_resource_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.json = False
        r_shell.do_resource_create(client_mock, args)
        client_mock.resource.create.assert_called_once_with()

    def test_do_resource_create_with_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.uuid = uuidutils.generate_uuid()
        args.json = False

        r_shell.do_resource_create(client_mock, args)
        client_mock.resource.create.assert_called_once_with(uuid=args.uuid)

    def test_do_resource_create_valid_type(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.type = 'switch'
        args.description = 'desc'
        args.json = False
        r_shell.do_resource_create(client_mock, args)
        client_mock.resource.create.assert_called_once_with(type='switch',
                                                           description='desc')

    def test_do_resource_create_valid_field(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.type = 'server'
        args.attributes = ["key1=val1", "key2=val2"]
        args.description = 'desc'
        args.json = False
        r_shell.do_resource_create(client_mock, args)
        client_mock.resource.create.assert_called_once_with(type='server',
                                                            attributes={
                                                                'key1': 'val1',
                                                                'key2': 'val2'},
                                                           description='desc')

    def test_do_resource_create_wrong_attributes_field(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.type = 'pdu'
        args.attributes = ["foo"]
        args.description = 'desc'
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_create, client_mock, args)

    def test_do_resource_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = ['resource_uuid']
        r_shell.do_resource_delete(client_mock, args)
        client_mock.resource.delete.assert_called_once_with('resource_uuid')

    def test_do_resource_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = ['resource_uuid1', 'resource_uuid2']
        r_shell.do_resource_delete(client_mock, args)
        client_mock.resource.delete.assert_has_calls([
            mock.call('resource_uuid1'), mock.call('resource_uuid2')])

    def test_do_resource_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = 'resource_uuid'
        args.op = 'add'
        args.type = 'switch'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        args.json = False
        r_shell.do_resource_update(client_mock, args)
        patch = commonutils.args_array_to_patch(args.op, args.attributes[0])
        client_mock.resource.update.assert_called_once_with('resource_uuid',
                                                           patch)

    def test_do_resource_update_wrong_op(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.resource = 'resource_uuid'
        args.op = 'foo'
        args.type = ''
        args.attributes = [['arg1=val1', 'arg2=val2']]
        self.assertRaises(exceptions.CommandError,
                          r_shell.do_resource_update,
                          client_mock, args)
        self.assertFalse(client_mock.resource.update.called)
