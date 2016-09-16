# -*- coding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc
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

from arsenalclient.common import base
from arsenalclient.common.i18n import _
from arsenalclient.common import utils
from arsenalclient import exc


class Resource(base.Resource):
    def __repr__(self):
        return "<Resource %s>" % self._info


class ResourceManager(base.CreateManager):
    resource_class = Resource
    _resource_name = 'resources'
    _creation_attributes = ['description', 'type', 'attributes', 'uuid']

    def list(self, marker=None, limit=None, sort_key=None,
             sort_dir=None, detail=False, fields=None):
        """Retrieve a list of resources.

        :param marker: Optional, the UUID of a resource, eg the last
                       resource from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of resource to return.
            2) limit == 0, return the entire list of resources.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the arsenal API
               (see arsenal's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about resource.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :returns: A list of resources.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker, limit, sort_key, sort_dir,
                                       fields)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "resources")
        else:
            return self._list_pagination(self._path(path), "resources",
                                         limit=limit)

    def get(self, resource_id, fields=None):
        return self._get(resource_id=resource_id, fields=fields)

    def delete(self, resource_id):
        return self._delete(resource_id=resource_id)

    def update(self, resource_id, patch):
        return self._update(resource_id=resource_id, patch=patch)
