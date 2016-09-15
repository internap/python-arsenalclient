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

"""
Command-line interface to the Arsenal datatcenter API.
"""

from __future__ import print_function

import argparse
import sys

import six
from arsenalclient import client as arsclient
from arsenalclient import exc
from arsenalclient.common import cliutils
from arsenalclient.common import http
from arsenalclient.common import utils
from arsenalclient.common.i18n import _
from oslo_utils import encodeutils


LATEST_API_VERSION = ('1', 'latest')


class ArsenalShell(object):

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='arsenal',
            description=__doc__.strip(),
            epilog=_('See "arsenal help COMMAND" '
                     'for help on a specific command.'),
            add_help=False,
            formatter_class=HelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS,
                            )

        parser.add_argument('--json',
                            default=False,
                            action='store_true',
                            help=_('Print JSON response without formatting.'))

        parser.add_argument('-v', '--verbose',
                            default=False, action="store_true",
                            help=_('Print more verbose output'))

        parser.add_argument('--arsenal-url',
                            default=cliutils.env('ARSENAL_URL'),
                            help=_('Defaults to env[ARSENAL_URL]'))

        parser.add_argument('--arsenal_url',
                            help=argparse.SUPPRESS)

        msg = _('Maximum number of retries in case of conflict error '
                '(HTTP 409). Defaults to env[ARSENAL_MAX_RETRIES] or %d. '
                'Use 0 to disable retrying.') % http.DEFAULT_MAX_RETRIES
        parser.add_argument('--max-retries', type=int, help=msg,
                            default=cliutils.env(
                                'ARSENAL_MAX_RETRIES',
                                default=str(http.DEFAULT_MAX_RETRIES)))

        msg = _('Amount of time (in seconds) between retries '
                'in case of conflict error (HTTP 409). '
                'Defaults to env[ARSENAL_RETRY_INTERVAL] '
                'or %d.') % http.DEFAULT_RETRY_INTERVAL
        parser.add_argument('--retry-interval', type=int, help=msg,
                            default=cliutils.env(
                                'ARSENAL_RETRY_INTERVAL',
                                default=str(http.DEFAULT_RETRY_INTERVAL)))

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>',
                                           dest='subparser_name')
        submodule = utils.import_versioned_module(version, 'shell')
        submodule.enhance_parser(parser, subparsers, self.subcommands)
        utils.define_commands_from_module(subparsers, self, self.subcommands)
        return parser

    def main(self, argv):
        # Parse args once to find version
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)

        subcommand_parser = self.get_subcommand_parser('1')
        self.parser = subcommand_parser

        # Handle top-level --help/-h before attempting to parse
        # a command off the command line
        if options.help or not argv:
            self.do_help(options)
            return 0

        # Parse args again and call whatever callback was selected
        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with these commands right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0

        if not args.arsenal_url:
            raise exc.CommandError(_("@CHANGEME You must provide a username via "
                                         "either --os-username or via "
                                         "env[OS_USERNAME]"))

        if args.max_retries < 0:
            raise exc.CommandError(_("You must provide value >= 0 for "
                                     "--max-retries"))
        if args.retry_interval < 1:
            raise exc.CommandError(_("You must provide value >= 1 for "
                                     "--retry-interval"))
        client_args = (
            'arsenal_url', 'max_retries', 'retry_interval',
            'timeout', 'insecure'
        )
        kwargs = {}
        for key in client_args:
            kwargs[key] = getattr(args, key)
        client = arsclient.get_client()

        try:
            args.func(client, args)
        except exc.Unauthorized:
            raise exc.CommandError(_("Invalid OpenStack Identity credentials"))
        except exc.CommandError as e:
            subcommand_parser = self.subcommands[args.subparser_name]
            subcommand_parser.error(e)

    @cliutils.arg('command', metavar='<subcommand>', nargs='?',
                  help=_('Display help for <subcommand>'))
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError(_("'%s' is not a valid subcommand") %
                                       args.command)
        else:
            self.parser.print_help()


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


def main():
    try:
        ArsenalShell().main(sys.argv[1:])
    except KeyboardInterrupt:
        print(_("... terminating arsenal client"), file=sys.stderr)
        return 130
    except Exception as e:
        print(encodeutils.safe_encode(six.text_type(e)), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())