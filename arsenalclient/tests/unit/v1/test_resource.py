# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy

import testtools
from testtools.matchers import HasLength

from arsenalclient import exc
from arsenalclient.tests.unit import utils
import arsenalclient.v1.resource

RESOURCE = {'id': 42,
           'uuid': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
           'ironic_driver': 'unestring',
           'description': 'data-center-1-resource'}

RESOURCE2 = {'id': 43,
            'uuid': 'eeeeeeee-dddd-cccc-bbbb-aaaaaaaaaaaa',
            'ironic_driver': 'unestring',
            'description': 'data-center-1-resource'}

CREATE_RESOURCE = copy.deepcopy(RESOURCE)
del CREATE_RESOURCE['id']
del CREATE_RESOURCE['uuid']

CREATE_WITH_UUID = copy.deepcopy(RESOURCE)
del CREATE_WITH_UUID['id']

UPDATED_RESOURCE = copy.deepcopy(RESOURCE)
NEW_DESCR = 'new-description'
UPDATED_RESOURCE['description'] = NEW_DESCR

fake_responses = {
    '/v1/resources':
    {
        'GET': (
            {},
            {"resource": [RESOURCE]},
        ),
        'POST': (
            {},
            CREATE_RESOURCE,
        ),
    },
    '/v1/resources/detail':
    {
        'GET': (
            {},
            {"resource": [RESOURCE]},
        ),
    },
    '/v1/resources/?fields=uuid,ironic_driver':
    {
        'GET': (
            {},
            {"resource": [RESOURCE]},
        ),
    },
    '/v1/resources/%s' % RESOURCE['uuid']:
    {
        'GET': (
            {},
            RESOURCE,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_RESOURCE,
        ),
    },
    '/v1/resources/%s?fields=uuid,description' % RESOURCE['uuid']:
    {
        'GET': (
            {},
            RESOURCE,
        ),
    },
}

fake_responses_pagination = {
    '/v1/resources':
    {
        'GET': (
            {},
            {"resource": [RESOURCE],
             "next": "http://127.0.0.1:6385/v1/resources/?limit=1"}
        ),
    },
    '/v1/resources/?limit=1':
    {
        'GET': (
            {},
            {"resource": [RESOURCE2]}
        ),
    },
    '/v1/resources/?marker=%s' % RESOURCE['uuid']:
    {
        'GET': (
            {},
            {"resource": [RESOURCE2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/resources/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"resource": [RESOURCE2]}
        ),
    },
    '/v1/resources/?sort_dir=desc':
    {
        'GET': (
            {},
            {"resource": [RESOURCE2]}
        ),
    },
}


class ResourceManagerTest(testtools.TestCase):

    def setUp(self):
        super(ResourceManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = arsenalclient.v1.resource.ResourceManager(self.api)

    def test_resource_list(self):
        resource = self.mgr.list()
        expect = [
            ('GET', '/v1/resources', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(resource))

    def test_resource_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = arsenalclient.v1.resource.ResourceManager(self.api)
        resource = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/resources/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(resource, HasLength(1))

    def test_resource_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = arsenalclient.v1.resource.ResourceManager(self.api)
        resource = self.mgr.list(marker=RESOURCE['uuid'])
        expect = [
            ('GET', '/v1/resources/?marker=%s' % RESOURCE['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(resource, HasLength(1))

    def test_resource_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = arsenalclient.v1.resource.ResourceManager(self.api)
        resource = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/resources', {}, None),
            ('GET', '/v1/resources/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(resource, HasLength(2))

    def test_resource_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = arsenalclient.v1.resource.ResourceManager(self.api)
        resource = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/resources/?sort_key=updated_at', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(resource, HasLength(1))

    def test_resource_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = arsenalclient.v1.resource.ResourceManager(self.api)
        resource = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/resources/?sort_dir=desc', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(resource, HasLength(1))

    def test_resource_list_detail(self):
        resource = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/resources/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(resource))

    def test_resource_list_fields(self):
        nodes = self.mgr.list(fields=['uuid', 'ironic_driver'])
        expect = [
            ('GET', '/v1/resources/?fields=uuid,ironic_driver', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(nodes))

    def test_resource_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.list,
                          detail=True, fields=['uuid', 'ironic_driver'])

    def test_resource_show(self):
        resource = self.mgr.get(RESOURCE['uuid'])
        expect = [
            ('GET', '/v1/resources/%s' % RESOURCE['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(RESOURCE['uuid'], resource.uuid)
        self.assertEqual(RESOURCE['description'], resource.description)

    def test_resource_show_fields(self):
        resource = self.mgr.get(RESOURCE['uuid'], fields=['uuid', 'description'])
        expect = [
            ('GET', '/v1/resources/%s?fields=uuid,description' %
             RESOURCE['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(RESOURCE['uuid'], resource.uuid)
        self.assertEqual(RESOURCE['description'], resource.description)

    def test_create(self):
        resource = self.mgr.create(**CREATE_RESOURCE)
        expect = [
            ('POST', '/v1/resources', {}, CREATE_RESOURCE),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(resource)

    def test_create_with_uuid(self):
        resource = self.mgr.create(**CREATE_WITH_UUID)
        expect = [
            ('POST', '/v1/resources', {}, CREATE_WITH_UUID),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(resource)

    def test_delete(self):
        resource = self.mgr.delete(resource_id=RESOURCE['uuid'])
        expect = [
            ('DELETE', '/v1/resources/%s' % RESOURCE['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(resource)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_DESCR,
                 'path': '/description'}
        resource = self.mgr.update(resource_id=RESOURCE['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/resources/%s' % RESOURCE['uuid'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_DESCR, resource.description)