import ipaddress
import sys
import argparse
import logging

from vinfra import api_versions
from vinfra.api.network.networks import (
    TrafficTypeAssignmentManager, NetworkReconfiguration, NetworkMigrationManager,
    NetworkConversionManager, NETWORK_TASK_TIMEOUT)
from vinfraclient import exceptions
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import Command, Lister, ShowOne, TaskCommand
from vinfraclient.formatters import columns as fmt_columns
from vinfraclient.utils import (
    find_resource, find_resources, flat_and_combine_arg_list, ask_confirm
)


LOG = logging.getLogger(__name__)


def network_arg(parser):
    parser.add_argument(
        "network",
        metavar="<network>",
        help="Network ID or name"
    )


def parse_network_bulk(value):
    try:
        network, traffic_types = value.split(':', 2)
    except Exception:
        raise argparse.ArgumentTypeError("unrecognized format mapping")
    return (network, parse_list_options(traffic_types))


class ListNetwork(Lister):
    _description = "List available networks."
    _default_fields_before_46 = ['id', 'name', 'traffic_types', 'allow_list', 'deny_list']
    _default_fields = ['id', 'name', 'traffic_types',
                       'inbound_allow_list', 'inbound_deny_list',
                       'outbound_allow_list']
    _formatters = {'traffic_types': fmt_columns.ListColumn}

    def do_action(self, parsed_args):
        data = self.app.vinfra.networks.list()
        if self.app.vinfra.api_version < api_versions.HCI_VER_46:
            self._default_fields = self._default_fields_before_46
        return data


class ShowNetwork(ShowOne):
    _description = "Show details of a network."
    _formatters = {'traffic_types': fmt_columns.ListColumn}

    def configure_parser(self, parser):
        network_arg(parser)

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.networks, parsed_args.network)


class CreateNetwork(ShowOne):
    _description = "Create a new network."
    _formatters = {'traffic_types': fmt_columns.ListColumn}

    def configure_parser(self, parser):
        parser.add_argument(
            "--traffic-types",
            metavar="<traffic-types>",
            type=parse_list_options,
            help="A comma-separated list of traffic type IDs or names"
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
        parser.add_argument(
            "--outbound-allow-list",
            metavar="<rules>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of allow rules"
        )
        parser.add_argument(
            "name",
            metavar="<network-name>",
            help="Network name"
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

        parsed_args.inbound_allow_list = flat_and_combine_arg_list(
            parsed_args.inbound_allow_list)
        parsed_args.inbound_deny_list = flat_and_combine_arg_list(
            parsed_args.inbound_deny_list)
        parsed_args.outbound_allow_list = flat_and_combine_arg_list(
            parsed_args.outbound_allow_list)

        return self.app.vinfra.networks.create(
            parsed_args.name, traffic_types=parsed_args.traffic_types,
            inbound_allow_list=parsed_args.inbound_allow_list,
            inbound_deny_list=parsed_args.inbound_deny_list,
            outbound_allow_list=parsed_args.outbound_allow_list)


class SetNetwork(TaskCommand):
    _description = "Modify network parameters."
    _formatters = {'traffic_types': fmt_columns.ListColumn}

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<network-name>",
            help="Network name"
        )
        traffic_types_group = parser.add_mutually_exclusive_group()
        traffic_types_group.add_argument(
            "--traffic-types",
            metavar="<traffic-types>",
            type=parse_list_options,
            help="A comma-separated list of traffic type names "
                 "(overwrites network's current traffic types)"
        )
        traffic_types_group.add_argument(
            "--add-traffic-types",
            metavar="<traffic-types>",
            type=parse_list_options,
            dest="add_traffic_types",
            help="A comma-separated list of traffic type names "
                 "(adds the specified traffic types to the network)"
        )
        traffic_types_group.add_argument(
            "--del-traffic-types",
            metavar="<traffic-types>",
            type=parse_list_options,
            dest="del_traffic_types",
            help="A comma-separated list of traffic type names "
                 "(removes the specified traffic types from the network)"
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
        outbound_allow_group = parser.add_mutually_exclusive_group()
        outbound_allow_group.add_argument(
            "--outbound-allow-list",
            metavar="<rules>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of allow rules"
        )
        outbound_allow_group.add_argument(
            "--add-outbound-allow-list",
            metavar="<rules>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of allow rules"
        )
        outbound_allow_group.add_argument(
            "--del-outbound-allow-list",
            metavar="<rules>",
            type=parse_list_options,
            action='append',
            help="A comma-separated list of allow rules"
        )
        outbound_allow_group.add_argument(
            "--clear-outbound-allow-list",
            action="store_true",
            default=False,
            help="Clear all outbound allow rules, need confirmation"
        )
        outbound_allow_group.add_argument(
            "--restore-default-outbound-allow-list",
            action="store_true",
            default=False,
            help="Restore default outbound allow rules"
        )
        parser.add_argument(
            '-y', '--yes',
            action='store_true',
            help='Skip yes/no prompt (assume yes)'
        )

        network_arg(parser)

    @staticmethod
    def _has_allow_all_rule(rules):
        for rule in rules:
            if rule.split(':')[:3] == ['0.0.0.0', 'any', '0']:  # nosec
                return True
        return False

    def do_action(self, parsed_args):
        network = find_resource(self.app.vinfra.networks, parsed_args.network)
        if (self.app.vinfra.api_version >= api_versions.HCI_VER_45 and
                self.app.vinfra.api_version < api_versions.HCI_VER_46):
            network.inbound_allow_list = network.allow_list
            network.inbound_deny_list = network.deny_list

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name

        if parsed_args.allow_list is not None:
            LOG.warning('The --allow-list option is deprecated. '
                        'Please use --inbound-allow-list instead.')
            parsed_args.inbound_allow_list = parsed_args.allow_list

        if parsed_args.deny_list is not None:
            LOG.warning('The --deny-list option is deprecated. '
                        'Please use --inbound-deny-list instead.')
            parsed_args.inbound_deny_list = parsed_args.deny_list

        if parsed_args.inbound_allow_list is not None:
            kwargs['inbound_allow_list'] = flat_and_combine_arg_list(
                parsed_args.inbound_allow_list)
        elif parsed_args.add_inbound_allow_list:
            current = network.inbound_allow_list
            adding = flat_and_combine_arg_list(parsed_args.add_inbound_allow_list)
            kwargs['inbound_allow_list'] = current + adding
        elif parsed_args.del_inbound_allow_list:
            current = network.inbound_allow_list
            removing = flat_and_combine_arg_list(parsed_args.del_inbound_allow_list)
            kwargs['inbound_allow_list'] = [entry for entry in current if entry not in removing]
        elif parsed_args.clear_inbound_allow_list:
            kwargs['inbound_allow_list'] = []

        if parsed_args.inbound_deny_list is not None:
            kwargs['inbound_deny_list'] = flat_and_combine_arg_list(parsed_args.inbound_deny_list)
        elif parsed_args.add_inbound_deny_list:
            current = network.inbound_deny_list
            adding = flat_and_combine_arg_list(parsed_args.add_inbound_deny_list)
            kwargs['inbound_deny_list'] = current + adding
        elif parsed_args.del_inbound_deny_list:
            current = network.inbound_deny_list
            removing = flat_and_combine_arg_list(parsed_args.del_inbound_deny_list)
            kwargs['inbound_deny_list'] = [entry for entry in current if entry not in removing]
        elif parsed_args.clear_inbound_deny_list:
            kwargs['inbound_deny_list'] = []

        if parsed_args.outbound_allow_list is not None:
            kwargs['outbound_allow_list'] = flat_and_combine_arg_list(
                parsed_args.outbound_allow_list)
        elif parsed_args.add_outbound_allow_list:
            current = network.outbound_allow_list
            adding = flat_and_combine_arg_list(parsed_args.add_outbound_allow_list)
            kwargs['outbound_allow_list'] = current + adding
        elif parsed_args.del_outbound_allow_list:
            def drop_description(rule):
                parts = rule.split(':', 3)
                return ':'.join(parts[0:3])
            removing = [drop_description(rule.lower())
                        for rule in flat_and_combine_arg_list(parsed_args.del_outbound_allow_list)]
            kwargs['outbound_allow_list'] = [rule for rule in network.outbound_allow_list
                                             if drop_description(rule) not in removing]
        elif parsed_args.clear_outbound_allow_list:
            kwargs['outbound_allow_list'] = []
        elif parsed_args.restore_default_outbound_allow_list:
            kwargs['outbound_allow_list'] = 'default'

        if parsed_args.traffic_types:
            kwargs['traffic_types'] = parsed_args.traffic_types
        elif parsed_args.add_traffic_types:
            current = network.traffic_types
            adding = parsed_args.add_traffic_types
            kwargs['traffic_types'] = list(set(current) | set(adding))
        elif parsed_args.del_traffic_types:
            current = network.traffic_types
            removing = parsed_args.del_traffic_types
            kwargs['traffic_types'] = list(set(current) - set(removing))

        if 'outbound_allow_list' in kwargs:
            if (not self._has_allow_all_rule(kwargs['outbound_allow_list']) and
                    self._has_allow_all_rule(network.outbound_allow_list)):
                # a user is going to remove allow all rule
                message = (
                    'Proceed only if you have specified all the required '
                    'outbound allow rules, as described in "Restricting '
                    'outbound traffic from cluster nodes" in the '
                    'Administrator Command Line Guide.\n'
                    'Are you sure you want to confirm the action? [y/N]')
                if not parsed_args.yes and not ask_confirm(message):
                    LOG.info('Operation not confirmed')
                    sys.exit(0)

        return network.update_async(**kwargs)


class SetNetworkBulk(TaskCommand):
    _description = "Modify traffic types of multiple networks."

    def configure_parser(self, parser):
        parser.add_argument(
            "--network",
            metavar="<network>:<traffic-types>",
            dest="networks",
            type=parse_network_bulk,
            action="append",
            required=True,
            help="Network configuration in the format:\n"
                 "network: network ID or name;\n"
                 "traffic-types: a comma-separated list of traffic type names;"
                 "\n"
                 "(this option can be used multiple times)."
        )

    def task_wait(self, *args, **kwargs):  # pylint: disable=arguments-differ
        super(SetNetworkBulk, self).task_wait(*args, **kwargs)
        # NOTE(akurbatov): the result of operation is the list of networks
        # While TaskCommand is based on ShowOne class we shouldn't return list
        return None

    def do_action(self, parsed_args):
        network_traffic_type_list = []
        for network, traffic_types in parsed_args.networks:
            network = find_resource(self.app.vinfra.networks, network)
            network_traffic_type_list.append((network.id, traffic_types))

        return self.app.vinfra.networks.update_bulk_async(
            network_traffic_type_list)


class DeleteNetwork(Command):
    _description = "Delete a network."

    def configure_parser(self, parser):
        network_arg(parser)

    def do_action(self, parsed_args):
        network = find_resource(self.app.vinfra.networks, parsed_args.network)
        return network.delete()


class NetworkReconfigurationDetails(ShowOne):
    _description = "Display network reconfiguration details."

    def do_action(self, parsed_args):
        return NetworkReconfiguration(self.app.vinfra).get_reconfiguration()


class _NetworkMigrationMixin(object):
    def get_migration(self, task_id=None, full=False, stat=False):
        if not task_id:
            details = NetworkReconfiguration(self.app.vinfra).get_reconfiguration()
            task_id = details['task_id']
            if not task_id:
                raise exceptions.CommandError('No networks are being migrated.')

        migration = NetworkMigrationManager(
            self.app.vinfra).get_resource(task_id, full=full, stat=stat)
        return migration


class NetworkMigrationStart(TaskCommand):
    _description = "Start network migration."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def configure_parser(self, parser):
        parser.add_argument(
            "--network",
            metavar="<network>",
            required=True,
            help="Network ID or name"
        )

        parser.add_argument(
            "--subnet",
            metavar="<subnet>",
            required=False,
            help="New network subnet"
        )

        parser.add_argument(
            "--netmask",
            metavar="<netmask>",
            required=False,
            help="New network mask"
        )

        parser.add_argument(
            "--gateway",
            metavar="<gateway>",
            required=False,
            help="New network gateway"
        )

        parser.add_argument(
            "--shutdown",
            action="store_true",
            default=False,
            help="Prepare the cluster to be shutdown manually for relocation"
        )

        parser.add_argument(
            "--node",
            metavar=("<node>", "<address>"),
            action="append",
            nargs=2,
            required=False,
            help="New node address in the format:\n"
                 "node: node ID or hostname;\n"
                 "address: IPv4 address;"
                 "\n"
                 "(this option can be used multiple times)."
        )

    def do_action(self, parsed_args):
        network_id = find_resource(self.app.vinfra.networks, parsed_args.network).id
        nodes = [{'node_id': find_resource(self.app.vinfra.nodes, entry[0]).id,
                  'address': entry[1]}
                 for entry in parsed_args.node] if parsed_args.node else None

        return NetworkMigrationManager(self.app.vinfra).start(
            network_id=network_id,
            subnet=parsed_args.subnet,
            netmask=parsed_args.netmask,
            gateway=parsed_args.gateway,
            shutdown=parsed_args.shutdown,
            nodes=nodes)


class NetworkMigrationDetails(ShowOne, _NetworkMigrationMixin):
    _description = "Display network migration details."

    def configure_parser(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            default=False,
            help="Show full information"
        )
        parser.add_argument(
            "--task-id",
            metavar="<task-id>",
            help="The task ID of network migration"
        )
        parser.add_argument(
            "--stat",
            action="store_true",
            default=False,
            help=argparse.SUPPRESS
        )

    def do_action(self, parsed_args):
        return self.get_migration(task_id=parsed_args.task_id,
                                  full=parsed_args.full,
                                  stat=parsed_args.stat)


class NetworkMigrationApply(TaskCommand, _NetworkMigrationMixin):
    _description = "Continue network migration to apply the new network configuration."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def do_action(self, parsed_args):
        migration = self.get_migration()
        return migration.apply()


class NetworkMigrationRevert(TaskCommand, _NetworkMigrationMixin):
    _description = "Revert network migration."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def do_action(self, parsed_args):
        migration = self.get_migration()
        return migration.revert()


class NetworkMigrationRetry(TaskCommand, _NetworkMigrationMixin):
    _description = "Retry an operation for network migration."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def configure_parser(self, parser):
        parser.add_argument(
            "--subnet",
            metavar="<subnet>",
            required=False,
            help="New network subnet"
        )

        parser.add_argument(
            "--netmask",
            metavar="<netmask>",
            required=False,
            help="New network mask"
        )

        parser.add_argument(
            "--node",
            metavar=("<node>", "<address>"),
            action="append",
            nargs=2,
            required=False,
            help="New node address in the format:\n"
                 "node: node ID or hostname;\n"
                 "address: IPv4 address;"
                 "\n"
                 "(this option can be used multiple times)."
        )

    def do_action(self, parsed_args):
        nodes = [{'node_id': find_resource(self.app.vinfra.nodes, entry[0]).id,
                  'address': entry[1]}
                 for entry in parsed_args.node] if parsed_args.node else None
        migration = self.get_migration()
        return migration.retry(
            subnet=parsed_args.subnet,
            netmask=parsed_args.netmask,
            nodes=nodes)


class NetworkMigrationResume(TaskCommand, _NetworkMigrationMixin):
    _description = "Resume network migration after the cluster shutdown."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def do_action(self, parsed_args):
        migration = self.get_migration()
        return migration.resume()


class TrafficTypeAssignmentStart(TaskCommand):
    _description = "Start traffic type assignment."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def configure_parser(self, parser):
        parser.add_argument(
            "--traffic-type",
            metavar="<traffic-type>",
            required=True,
            help="Traffic type name"
        )
        parser.add_argument(
            "--target-network",
            metavar="<target-network>",
            required=True,
            help="Target network ID or name'"
        )

    def do_action(self, parsed_args):
        target_network = find_resource(self.app.vinfra.networks, parsed_args.target_network)
        manager = TrafficTypeAssignmentManager(self.app.vinfra)
        return manager.start(parsed_args.traffic_type, target_network.id)


class _AssignmentMixin(object):
    def get_assignment(self, task_id=None, full=False, stat=False):
        if not task_id:
            details = NetworkReconfiguration(self.app.vinfra).get_reconfiguration()
            task_id = details['task_id']
            if not task_id:
                raise exceptions.CommandError('No networks are being reconfigured.')

        assignment = TrafficTypeAssignmentManager(
            self.app.vinfra).get_resource(task_id, full=full, stat=stat)
        return assignment


class TrafficTypeAssignmentDetails(ShowOne, _AssignmentMixin):
    _description = "Display traffic type assignment details."

    def configure_parser(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            default=False,
            help="Show full information"
        )
        parser.add_argument(
            "--task-id",
            metavar="<task-id>",
            help="The task ID of traffic type assignment"
        )
        parser.add_argument(
            "--stat",
            action="store_true",
            default=False,
            help=argparse.SUPPRESS
        )

    def do_action(self, parsed_args):
        assignment = self.get_assignment(task_id=parsed_args.task_id,
                                         full=parsed_args.full,
                                         stat=parsed_args.stat)
        return assignment


class TrafficTypeAssignmentApply(TaskCommand, _AssignmentMixin):
    _description = "Continue traffic type assignment to apply the new network configuration."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def do_action(self, parsed_args):
        assignment = self.get_assignment()
        return assignment.apply()


class TrafficTypeAssignmentRevert(TaskCommand, _AssignmentMixin):
    _description = "Revert traffic type assignment."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def do_action(self, parsed_args):
        assignment = self.get_assignment()
        return assignment.revert()


class TrafficTypeAssignmentRetry(TaskCommand, _AssignmentMixin):
    _description = "Retry an operation for traffic type assignment."
    _default_timeout = NETWORK_TASK_TIMEOUT

    def do_action(self, parsed_args):
        assignment = self.get_assignment()
        return assignment.retry()


class NetworkConversionStart(TaskCommand):
    _description = "Convert VLAN network interfaces to Open vSwitch VLAN, " \
                   "and connect a new network to physical interfaces if " \
                   "they have no assignment"

    def configure_parser(self, parser):
        parser.add_argument(
            "--network",
            metavar="<network>",
            required=True,
            help="The ID or name of the network, which is connected to VLAN "
                 "interfaces"
        )

        parser.add_argument(
            "--physical-network-name",
            metavar="<name>",
            required=False,
            help="New network name for parent interfaces"
        )

    def do_action(self, parsed_args):
        target_network = find_resource(
            self.app.vinfra.networks, parsed_args.network)
        return NetworkConversionManager(self.app.vinfra).start(
            target_network.id, parsed_args.physical_network_name)


class NetworkConversionPrecheck(ShowOne):
    _description = "Check VLAN network interfaces to Open vSwitch VLAN " \
                   "conversion"

    def configure_parser(self, parser):
        parser.add_argument(
            "--network",
            metavar="<network>",
            required=True,
            help="The ID or name of the network, which is connected to VLAN "
                 "interface"
        )

        parser.add_argument(
            "--physical-network-name",
            metavar="<name>",
            required=False,
            help="New network name for parent interfaces"
        )

    def do_action(self, parsed_args):
        target_network = find_resource(
            self.app.vinfra.networks, parsed_args.network)
        return NetworkConversionManager(self.app.vinfra).precheck(
            target_network.id, parsed_args.physical_network_name)


class NetworkConversionStatus(TaskCommand):
    _description = "Get VLAN network interfaces conversion status"

    def configure_parser(self, parser):
        parser.add_argument(
            "task",
            metavar="<task>",
            help="Task ID"
        )

    def do_action(self, parsed_args):
        return NetworkConversionManager(
            self.app.vinfra).get_status(parsed_args.task)


class NetworkEncryptionEnable(TaskCommand):
    _description = "Enable traffic encryption"

    def configure_parser(self, parser):
        parser.add_argument(
            "networks",
            metavar="<network>",
            nargs="+",
            help="Network ID or name"
        )

        parser.add_argument(
            "--no-switch-storage-ipv6",
            action="store_false",
            required=False,
            default=True,
            dest="switch_storage_ipv6",
            help="Do not switch CSes to IPv6 addresses"
        )

    def do_action(self, parsed_args):
        networks = find_resources(self.app.vinfra.networks, parsed_args.networks)
        return self.app.vinfra.networks.ipsec.enable(networks,
                                                     parsed_args.switch_storage_ipv6)


class NetworkEncryptionDisable(TaskCommand):
    _description = "Disable traffic encryption"

    def configure_parser(self, parser):
        parser.add_argument(
            "networks",
            metavar="<network>",
            nargs="+",
            help="Network ID or name"
        )

    def do_action(self, parsed_args):
        networks = find_resources(self.app.vinfra.networks, parsed_args.networks)
        return self.app.vinfra.networks.ipsec.disable(networks)


class NetworkEncryptionCancel(Command):
    _description = "Cancel enabling/disabling of traffic encryption"

    def do_action(self, parsed_args):
        return self.app.vinfra.networks.ipsec.cancel()


class NetworkEncryptionBypassBase(Command):
    @staticmethod
    def parse_cidr(arg):
        try:
            return str(ipaddress.ip_network(arg.decode()))
        except ValueError as exc:
            raise exceptions.ValidationError(exc)


class NetworkEncryptionBypassAdd(NetworkEncryptionBypassBase):
    _description = "Add exception for traffic encryption"

    def configure_parser(self, parser):
        parser.add_argument(
            "subnet",
            metavar="<subnet>",
            help="CIDR or single address"
        )
        parser.add_argument(
            "port",
            metavar="<port>",
            type=int,
            help="Port number",
        )

    def do_action(self, parsed_args):
        subnet = self.parse_cidr(parsed_args.subnet)
        port = parsed_args.port
        return self.app.vinfra.networks.ipsec.add_bypass([subnet], [port])


class NetworkEncryptionBypassDel(NetworkEncryptionBypassBase):
    _description = "Delete exception for traffic encryption"

    def configure_parser(self, parser):
        parser.add_argument(
            "subnet",
            metavar="<subnet>",
            help="CIDR or single address"
        )
        parser.add_argument(
            "port",
            metavar="<port>",
            type=int,
            help="Port number",
        )

    def do_action(self, parsed_args):
        subnet = self.parse_cidr(parsed_args.subnet)
        port = parsed_args.port
        return self.app.vinfra.networks.ipsec.del_bypass([subnet], [port])


class NetworkEncryptionBypassList(Lister):
    _description = "List exceptions for traffic encryption"
    _default_fields = ['subnet', 'port']

    def do_action(self, parsed_args):
        return self.app.vinfra.networks.ipsec.get_bypass()


class SubnetColumn(fmt_columns.BaseColumn):
    def human_readable(self, value=None):
        value = ['{:10} {}'.format(x['status'], x['cidr']) for x in self._value]
        return super(SubnetColumn, self).human_readable(value=value)


class NetworkEncryptionStatus(Lister):
    _description = "Get status of traffic encryption"
    _default_fields = ['id', 'name', 'status', 'subnets']
    _formatters = {'subnets': SubnetColumn}

    def do_action(self, parsed_args):
        def make_obj(net):
            return {
                'id': net.id,
                'name': net.name,
                'status': net.encryption['status'],
                'subnets': net.encryption['subnets'],
            }

        return [make_obj(n) for n in self.app.vinfra.networks.list()]


class AssignIPv6Prefix(TaskCommand):
    _description = "Assign IPv6 prefix"

    def configure_parser(self, parser):
        parser.add_argument(
            "prefix",
            metavar="<prefix>",
            help="IPv6 prefix"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.networks.ipv6_prefix.assign(
            parsed_args.prefix, parsed_args.force)


class RemoveIPv6Prefix(TaskCommand):
    _description = "Remove IPv6 prefix"

    def configure_parser(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            default=False
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.networks.ipv6_prefix.remove(
            parsed_args.force)


class IPv6Prefix(ShowOne):
    _description = "Show IPv6 prefix"

    def do_action(self, parsed_args):
        return self.app.vinfra.networks.ipv6_prefix.get_prefix()
