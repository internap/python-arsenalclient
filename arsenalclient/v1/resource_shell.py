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

from arsenalclient.common import cliutils
from arsenalclient.common import utils
from arsenalclient.v1 import resource_fields as res_fields


def _print_resource_show(resource, fields=None, json=False):
    if fields is None:
        fields = res_fields.DETAILED_RESOURCE.fields

    data = dict([(f, getattr(resource, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg('resource', metavar='<resource>', help="UUID of the resource.")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more resource fields. Only these fields will be fetched from "
         "the server.")
def do_resource_show(cc, args):
    """Show detailed information about a resource."""
    utils.check_empty_arg(args.resource, '<resource>')
    fields = args.fields[0] if args.fields else None
    utils.check_for_invalid_fields(
        fields, res_fields.DETAILED_RESOURCE.fields)
    resource = cc.resource.get(args.resource, fields=fields)
    _print_resource_show(resource, fields=fields, json=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about the resource.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of resource to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the arsenal API Service.')
@cliutils.arg(
    '--marker',
    metavar='<resource>',
    help='Resource UUID (for example, of the last resource in the list '
         'from a previous request). Returns the list of resource '
         'after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Resource field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more resource fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
def do_resource_list(cc, args):
    """List the resource."""
    if args.detail:
        fields = res_fields.DETAILED_RESOURCE.fields
        field_labels = res_fields.DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.RESOURCE.fields
        field_labels = res_fields.RESOURCE.labels

    sort_fields = res_fields.DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.DETAILED_RESOURCE.sort_labels

    params = utils.common_params_for_list(args, sort_fields,
                                          sort_field_labels)

    resource = cc.resource.list(**params)
    cliutils.print_list(resource, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg(
    '-d', '--description',
    metavar='<description>',
    help='Description of the resource.')
@cliutils.arg(
    '-a', '--attributes',
    metavar="<key=value>",
    action='append',
    help="Record arbitrary key/value attributes. "
         "Can be specified multiple times.")
@cliutils.arg(
    '-u', '--uuid',
    metavar='<uuid>',
    help="UUID of the resource.")
def do_resource_create(cc, args):
    """Create a new resource."""
    field_list = ['description', 'attributes', 'uuid']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'attributes')
    resource = cc.resource.create(**fields)

    data = dict([(f, getattr(resource, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg(
    'resource',
    metavar='<resource>',
    nargs='+',
    help="UUID of the resource.")
def do_resource_delete(cc, args):
    """Delete a resource."""
    for c in args.resource:
        cc.resource.delete(c)
        print('Deleted resource %s' % c)


@cliutils.arg('resource', metavar='<resource>', help="UUID of the resource.")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operation: 'add', 'replace', or 'remove'.")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attribute to add, replace, or remove. Can be specified "
         "multiple times. For 'remove', only <path> is necessary.")
def do_resource_update(cc, args):
    """Update information about a resource."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    resource = cc.resource.update(args.resource, patch)
    _print_resource_show(resource, json=args.json)
