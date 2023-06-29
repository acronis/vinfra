from vinfra.consts import missing

from vinfraclient import exceptions
from vinfraclient import argtypes
from vinfraclient.cmd import base
from vinfraclient.cmd.node import utils as node_utils
from vinfraclient.utils import find_resource


DNS_TLD = '.vstoragedomain'
COMMON_SET_NAMES = [
    'ipv4', 'ipv6', 'gw4', 'gw6', 'dhcp4_enabled', 'dhcp6_enabled', 'mtu',
    'ignore_auto_routes_v4', 'ignore_auto_routes_v6'
]
BOND_TYPES = [
    'balance-rr', 'balance-xor', 'broadcast', '802.3ad',
    'balance-tlb', 'balance-alb'
]
OVS_BOND_TYPES = [
    'balance-tcp', 'active-backup'
]


def _add_common_set_options(parser):
    parser.add_argument(
        "--ipv4",
        metavar="<ipv4>",
        type=argtypes.parse_list_options,
        help="A comma-separated list of IPv4 addresses"
    )
    parser.add_argument(
        "--ipv6",
        metavar="<ipv6>",
        type=argtypes.parse_list_options,
        help="A comma-separated list of IPv6 addresses"
    )
    parser.add_argument(
        "--gw4",
        metavar="<gw4>",
        help="Gateway IPv4 address"
    )
    parser.add_argument(
        "--gw6",
        metavar="<gw6>",
        help="Gateway IPv6 address"
    )
    parser.add_argument(
        "--mtu",
        metavar="<mtu>",
        help="MTU interface value"
    )

    dhcpv4_group = parser.add_mutually_exclusive_group()
    dhcpv4_group.add_argument(
        "--dhcp4",
        action="store_true",
        dest="dhcp4_enabled",
        default=None,
        help="Enable DHCPv4."
    )
    dhcpv4_group.add_argument(
        "--no-dhcp4",
        action="store_false",
        dest="dhcp4_enabled",
        default=None,
        help="Disable DHCPv4."
    )

    dhcpv6_group = parser.add_mutually_exclusive_group()
    dhcpv6_group.add_argument(
        "--dhcp6",
        action="store_true",
        dest="dhcp6_enabled",
        default=None,
        help="Enable DHCPv6."
    )
    dhcpv6_group.add_argument(
        "--no-dhcp6",
        action="store_false",
        dest="dhcp6_enabled",
        default=None,
        help="Disable DHCPv6."
    )

    routesv4_group = parser.add_mutually_exclusive_group()
    routesv4_group.add_argument(
        "--auto-routes-v4",
        dest="ignore_auto_routes_v4",
        action="store_false",
        default=None,
        help="Enable automatic IPv4 routes."
    )
    routesv4_group.add_argument(
        "--ignore-auto-routes-v4",
        dest="ignore_auto_routes_v4",
        action="store_true",
        default=None,
        help="Ignore automatic IPv4 routes."
    )

    routesv6_group = parser.add_mutually_exclusive_group()
    routesv6_group.add_argument(
        "--auto-routes-v6",
        dest="ignore_auto_routes_v6",
        action="store_false",
        default=None,
        help="Enable automatic IPv6 routes."
    )
    routesv6_group.add_argument(
        "--ignore-auto-routes-v6",
        dest="ignore_auto_routes_v6",
        action="store_true",
        default=None,
        help="Ignore automatic IPv6 routes."
    )


def _add_network_option(parser):
    parser.add_argument(
        "--network",
        metavar="<network>",
        dest="network",
        help="Network ID or name"
    )


def _add_iface_argument(parser):
    parser.add_argument(
        "iface",
        metavar="<iface>",
        help="Network interface name"
    )


class ListIface(base.Lister):
    _description = "List node network interfaces."
    _default_fields = ["name", "node_id", "ipv4", "state", "network"]

    def configure_parser(self, parser):
        required = node_utils.is_remove_client()
        node_group = parser.add_mutually_exclusive_group(required=required)
        node_group.add_argument(
            "-a", "--all",
            action="store_true",
            help="List all network interfaces on all nodes."
        )
        node_utils.add_node_option(node_group, required=False)

    def do_action(self, parsed_args):
        if parsed_args.all:
            nodes = self.app.vinfra.nodes.list()
        else:
            nodes = [find_resource(self.app.vinfra.nodes, parsed_args.node)]

        # Note(akurbatov): extend the output with network name to make it a
        # little-bit user-friendly
        with_name = parsed_args.formatter in ['table', 'value']
        networks_by_id = {}
        if with_name:
            networks = self.app.vinfra.networks.list()
            networks_by_id = dict((net.id, net) for net in networks)

        ifaces = []
        for node in nodes:
            for iface in node.ifaces_manager.list():
                if with_name and iface.network and iface.network in networks_by_id:
                    args = (iface.network, networks_by_id[iface.network].name)
                    iface.set_info({'network': "{} ({})".format(*args)})

                ifaces.append(iface)
        return ifaces


class ShowIface(base.ShowOne):
    _description = "Show details of a network interface."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser, required=True)
        _add_iface_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        return iface


class UpIface(base.TaskCommand):
    _description = "Bring up a network interface."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser, required=True)
        _add_iface_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        return iface.up_async()


class DownIface(base.TaskCommand):
    _description = "Bring down a network interface."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser, required=True)
        _add_iface_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        return iface.down_async()


class SetIface(base.TaskCommand):
    _description = ("Modify network interface parameters\n"
                    "(overwrites omitted options to "
                    "interace default values).")

    def configure_parser(self, parser):
        _add_common_set_options(parser)

        network_group = parser.add_mutually_exclusive_group()
        network_group.add_argument(
            "--network",
            metavar="<network>",
            dest="network",
            default=missing,
            help="Network ID or name"
        )
        network_group.add_argument(
            "--no-network",
            dest="network",
            action="store_const",
            const=None,
            default=missing,
            help="Remove a network from the interface"
        )

        infiniband = parser.add_mutually_exclusive_group()
        infiniband.add_argument(
            "--connected-mode",
            dest="connected_mode",
            action="store_true",
            default=None,
            help="Enable connected mode (InfiniBand interfaces only)."
        )
        infiniband.add_argument(
            "--datagram-mode",
            dest="connected_mode",
            action="store_false",
            default=None,
            help="Enable datagram mode (InfiniBand interfaces only)."
        )

        parser.add_argument(
            "--ifaces",
            metavar="<ifaces>",
            type=argtypes.parse_list_options,
            required=False,
            help="A comma-separated list of network interface names, e.g., "
                 "'iface1,iface2,...,ifaceN'"
        )
        parser.add_argument(
            "--bond-type",
            metavar="<bond-type>",
            choices=BOND_TYPES + OVS_BOND_TYPES,
            required=False,
            help="Bond type (%s);\nBond type for OVS interface (%s)" % (
                ', '.join([repr(t) for t in BOND_TYPES]),
                ", ".join([repr(t) for t in OVS_BOND_TYPES])
            )
        )
        node_utils.add_node_option(parser, required=True)
        _add_iface_argument(parser)

    def do_action(self, parsed_args):
        kwargs = base.flatten_args(parsed_args, COMMON_SET_NAMES)
        if parsed_args.connected_mode in (True, False):
            kwargs['connected_mode'] = parsed_args.connected_mode
        if parsed_args.ifaces and parsed_args.ifaces is not missing:
            kwargs['ifaces'] = parsed_args.ifaces
        if parsed_args.bond_type and parsed_args.bond_type is not missing:
            kwargs['bond_type'] = parsed_args.bond_type

        if parsed_args.network is not missing:
            kwargs['network'] = (find_resource(self.app.vinfra.networks,
                                               parsed_args.network)
                                 if parsed_args.network else None)

        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        return iface.update_async(**kwargs)


class DeleteIface(base.TaskCommand):
    _description = "Delete a network interface."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser, required=True)
        _add_iface_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        return iface.delete_async()


class CreateVlan(base.TaskCommand):
    _description = "Create a VLAN"

    def configure_parser(self, parser):
        _add_common_set_options(parser)
        _add_network_option(parser)

        node_utils.add_node_option(parser, required=True)
        parser.add_argument(
            "--iface",
            metavar="<iface>",
            type=argtypes.non_empty_string,
            required=True,
            help="Interface name"
        )
        parser.add_argument(
            "--tag",
            metavar="<tag>",
            type=int,
            required=True,
            help="VLAN tag number"
        )

    def do_action(self, parsed_args):
        kwargs = base.flatten_args(parsed_args, COMMON_SET_NAMES)

        if parsed_args.network:
            kwargs['network'] = find_resource(self.app.vinfra.networks,
                                              parsed_args.network)

        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        return node.ifaces_manager.create_vlan_async(
            iface, parsed_args.tag, **kwargs)


class DeleteVlan(base.TaskCommand):
    _description = "Delete a VLAN."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser, required=True)
        _add_iface_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        if iface.type != 'vlan':
            raise exceptions.ValidationError("Interface {} is not VLAN type.")
        return iface.delete_async()


class CreateBond(base.TaskCommand):
    _description = "Create a network bonding."

    def configure_parser(self, parser):
        _add_common_set_options(parser)
        _add_network_option(parser)

        parser.add_argument(
            "--bonding-opts",
            metavar="<bonding_opts>",
            type=argtypes.StructTypeSkipCheck(),
            help="Additional bonding options"
        )

        node_utils.add_node_option(parser, required=True)
        parser.add_argument(
            "--bond-type",
            metavar="<bond-type>",
            choices=BOND_TYPES + OVS_BOND_TYPES,
            required=True,
            help="Bond type (%s);\nOVS Bond type for OVS interface (%s)" % (
                ', '.join([repr(t) for t in BOND_TYPES]),
                ", ".join([repr(t) for t in OVS_BOND_TYPES])
            )
        )
        parser.add_argument(
            "--ifaces",
            metavar="<ifaces>",
            type=argtypes.parse_list_options,
            required=True,
            help="A comma-separated list of network interface names, e.g., "
                 "'iface1,iface2,...,ifaceN'"
        )

    def do_action(self, parsed_args):
        kwargs_names = list(COMMON_SET_NAMES)
        kwargs_names.append('bonding_opts')
        kwargs = base.flatten_args(parsed_args, kwargs_names)

        if parsed_args.network:
            kwargs['network'] = find_resource(self.app.vinfra.networks,
                                              parsed_args.network)

        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        ifaces = [find_resource(node.ifaces_manager, iface)
                  for iface in parsed_args.ifaces]
        return node.ifaces_manager.create_bond_async(
            ifaces, parsed_args.bond_type, **kwargs)


class DeleteBond(base.TaskCommand):
    _description = "Delete a network bonding."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser, required=True)
        _add_iface_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        iface = find_resource(node.ifaces_manager, parsed_args.iface)
        if iface.type != 'bonding':
            raise exceptions.ValidationError(
                "Interface {} is not a bonding.".format(parsed_args.iface))
        return iface.delete_async()
