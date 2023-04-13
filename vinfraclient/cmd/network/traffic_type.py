import argparse
import logging

from vinfra import api_versions
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import Command, Lister, ShowOne, TaskCommand
from vinfraclient.utils import find_resource, flat_and_combine_arg_list


LOG = logging.getLogger(__name__)


def _traffic_type_arg(parser):
    parser.add_argument(
        "traffic_type",
        metavar="<traffic-type>",
        help="Traffic type name"
    )


class ListTrafficType(Lister):
    _description = "List available traffic types."
    _default_fields_before_46 = ['name', 'type', 'exclusive', 'port',
                                 'allow_list', 'deny_list']
    _default_fields = ['name', 'type', 'exclusive', 'port',
                       'inbound_allow_list', 'inbound_deny_list']
    def do_action(self, parsed_args):
        data = self.app.vinfra.traffic_types.list()
        # show elements that do not have 'hidden' attr or hidden=False
        data = [traffic_type for traffic_type in data
                if not getattr(traffic_type, 'hidden', False)]
        if self.app.vinfra.api_version < api_versions.HCI_VER_46:
            self._default_fields = self._default_fields_before_46
        return data


class ShowTrafficType(ShowOne):
    _description = "Show details of a traffic type."

    def configure_parser(self, parser):
        _traffic_type_arg(parser)

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.traffic_types,
                             parsed_args.traffic_type)


class CreateTrafficType(ShowOne):
    _description = "Create a new traffic type."

    def configure_parser(self, parser):
        parser.add_argument(
            "name",
            metavar="<traffic-type-name>",
            help="Traffic type name"
        )
        parser.add_argument(
            "--port",
            metavar="<port>",
            required=True,
            help="Traffic type port"
        )
        inbound_allow_group = parser.add_mutually_exclusive_group()
        inbound_allow_group.add_argument(
            "--allow-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help=argparse.SUPPRESS
        )
        inbound_allow_group.add_argument(
            "--inbound-allow-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addresses"
        )
        inbound_deny_group = parser.add_mutually_exclusive_group()
        inbound_deny_group.add_argument(
            "--deny-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help=argparse.SUPPRESS
        )
        inbound_deny_group.add_argument(
            "--inbound-deny-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addreses"
        )

    def do_action(self, parsed_args):
        if parsed_args.allow_list is not None:
            LOG.warning('The --allow-list option is deprecated. '
                        'Please use --inbound-allow-list instead.')
            parsed_args.inbound_allow_list = parsed_args.allow_list

        if parsed_args.deny_list is not None:
            LOG.warning('The --deny-list option is deprecated. '
                        'Please use --inbound-deny-list instead.')
            parsed_args.inbound_deny_list = parsed_args.deny_list

        parsed_args.inbound_allow_list = flat_and_combine_arg_list(parsed_args.inbound_allow_list)
        parsed_args.inbound_deny_list = flat_and_combine_arg_list(parsed_args.inbound_deny_list)

        return self.app.vinfra.traffic_types.create(
            name=parsed_args.name,
            port=parsed_args.port,
            inbound_allow_list=parsed_args.inbound_allow_list,
            inbound_deny_list=parsed_args.inbound_deny_list)


class SetTrafficType(TaskCommand):
    _description = "Modify traffic type parameters."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the traffic type"
        )
        parser.add_argument(
            "--port",
            metavar="<port>",
            help="A new port for the traffic type"
        )
        inbound_allow_group = parser.add_mutually_exclusive_group()
        inbound_allow_group.add_argument(
            "--allow-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help=argparse.SUPPRESS
        )
        inbound_allow_group.add_argument(
            "--inbound-allow-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addresses"
        )
        inbound_allow_group.add_argument(
            "--add-inbound-allow-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addresses"
        )
        inbound_allow_group.add_argument(
            "--del-inbound-allow-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addresses"
        )
        inbound_allow_group.add_argument(
            "--clear-inbound-allow-list",
            action="store_true",
            default=False,
            help="Clear all inbound allow rules"
        )
        inbound_deny_group = parser.add_mutually_exclusive_group()
        inbound_deny_group.add_argument(
            "--deny-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help=argparse.SUPPRESS
        )
        inbound_deny_group.add_argument(
            "--inbound-deny-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addreses"
        )
        inbound_deny_group.add_argument(
            "--add-inbound-deny-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addreses"
        )
        inbound_deny_group.add_argument(
            "--del-inbound-deny-list",
            metavar="<addresses>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of IP addreses"
        )
        inbound_deny_group.add_argument(
            "--clear-inbound-deny-list",
            action="store_true",
            default=False,
            help="Clear all inbound deny rules"
        )
        _traffic_type_arg(parser)

    def do_action(self, parsed_args):
        traffic_type = find_resource(self.app.vinfra.traffic_types,
                                     parsed_args.traffic_type)
        if (self.app.vinfra.api_version >= api_versions.HCI_VER_45 and
                self.app.vinfra.api_version < api_versions.HCI_VER_46):
            traffic_type.inbound_allow_list = traffic_type.allow_list
            traffic_type.inbound_deny_list = traffic_type.deny_list

        if parsed_args.allow_list is not None:
            LOG.warning('The --allow-list option is deprecated. '
                        'Please use --inbound-allow-list instead.')
            parsed_args.inbound_allow_list = parsed_args.allow_list

        if parsed_args.deny_list is not None:
            LOG.warning('The --deny-list option is deprecated. '
                        'Please use --inbound-deny-list instead.')
            parsed_args.inbound_deny_list = parsed_args.deny_list

        if parsed_args.inbound_allow_list is not None:
            parsed_args.inbound_allow_list = flat_and_combine_arg_list(
                parsed_args.inbound_allow_list)
        elif parsed_args.add_inbound_allow_list:
            current = traffic_type.inbound_allow_list
            adding = flat_and_combine_arg_list(parsed_args.add_inbound_allow_list)
            parsed_args.inbound_allow_list = current + adding
        elif parsed_args.del_inbound_allow_list:
            current = traffic_type.inbound_allow_list
            removing = flat_and_combine_arg_list(parsed_args.del_inbound_allow_list)
            parsed_args.inbound_allow_list = [entry for entry in current if entry not in removing]
        elif parsed_args.clear_inbound_allow_list:
            parsed_args.inbound_allow_list = []

        if parsed_args.inbound_deny_list is not None:
            parsed_args.inbound_deny_list = flat_and_combine_arg_list(
                parsed_args.inbound_deny_list)
        elif parsed_args.add_inbound_deny_list:
            current = traffic_type.inbound_deny_list
            adding = flat_and_combine_arg_list(parsed_args.add_inbound_deny_list)
            parsed_args.inbound_deny_list = current + adding
        elif parsed_args.del_inbound_deny_list:
            current = traffic_type.inbound_deny_list
            removing = flat_and_combine_arg_list(parsed_args.del_inbound_deny_list)
            parsed_args.inbound_deny_list = [entry for entry in current if entry not in removing]
        elif parsed_args.clear_inbound_deny_list:
            parsed_args.inbound_deny_list = []

        return traffic_type.update_async(name=parsed_args.name,
                                         port=parsed_args.port,
                                         inbound_allow_list=parsed_args.inbound_allow_list,
                                         inbound_deny_list=parsed_args.inbound_deny_list)


class DeleteTrafficType(Command):
    _description = "Delete a traffic type."

    def configure_parser(self, parser):
        _traffic_type_arg(parser)

    def do_action(self, parsed_args):
        traffic_type = find_resource(self.app.vinfra.traffic_types,
                                     parsed_args.traffic_type)
        return traffic_type.delete()
