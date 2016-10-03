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
from cellarclient.common import utils


def get_client(cellar_url=None, max_retries=None,
               retry_interval=None, **ignored_kwargs):
    """

    :param cellar_url: cellar API endpoint
    :param max_retries: Maximum number of retries in case of conflict error
    :param retry_interval: Amount of time (in seconds) between retries in case
        of conflict error
    :param ignored_kwargs: all the other params that are passed. Left for
        backwards compatibility. They are ignored.
    """
    kwargs = {
        'max_retries': max_retries,
        'retry_interval': retry_interval,
    }
    endpoint = cellar_url

    return Client('1', endpoint, **kwargs)


def Client(version, *args, **kwargs):
    module = utils.import_versioned_module(version, 'client')
    client_class = getattr(module, 'Client')
    return client_class(*args, **kwargs)