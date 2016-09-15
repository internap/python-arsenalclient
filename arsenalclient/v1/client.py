# Copyright 2012 OpenStack LLC.
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
from arsenalclient.v1 import resource
from arsenalclient.common import filecache
from arsenalclient.common import http
from arsenalclient.common.http import DEFAULT_VER
from arsenalclient.common.i18n import _
from arsenalclient import exc


class Client(object):
    """Client for the Arsenal v1 API.

    :param string endpoint: A user-supplied endpoint URL for the arsenal
                            service.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, endpoint=None, *args, **kwargs):
        """Initialize a new client for the Arsenal v1 API."""
        if not endpoint:
            raise exc.EndpointException(
                _("Must provide 'endpoint' if os_arsenal_api_version "
                  "isn't specified"))

        # If the user didn't specify a version, use a cached version if
        # one has been stored
        host, netport = http.get_server(endpoint)
        saved_version = filecache.retrieve_data(host=host, port=netport)
        if saved_version:
            kwargs['api_version_select_state'] = "cached"
            kwargs['os_arsenal_api_version'] = saved_version
        else:
            kwargs['api_version_select_state'] = "default"
            kwargs['os_arsenal_api_version'] = DEFAULT_VER

        self.http_client = http._construct_http_client(
            endpoint, *args, **kwargs)

        self.resource = resource.ResourceManager(self.http_client)
