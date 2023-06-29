import argparse
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import ShowOne, TaskCommand
from vinfraclient.utils import find_resource, find_resources


def parse_virtual_ip(value):
    args_count = value.count(':')
    if not args_count:
        raise argparse.ArgumentTypeError(
            "{!r} is not a valid <network:ip[:addr_type]> mapping"
            .format(value))

    elif args_count == 1:
        network, ipaddr = value.split(':')
        addr_type = None
    else:
        network, ipaddr, addr_type = value.split(':', 2)
    return network, ipaddr, addr_type


class HaShow(ShowOne):
    _description = "Display the HA configuration."

    def do_action(self, parsed_args):
        return self.app.vinfra.ha.get()


class HaCreate(TaskCommand):
    _description = "Create a HA configuration."

    def configure_parser(self, parser):
        parser.add_argument(
            "--virtual-ip",
            metavar="<network:ip[:addr-type]>",
            type=parse_virtual_ip,
            action="append",
            dest="virtual_ips",
            required=True,
            help="HA configuration mapping in the format:\n"
                 "network: network to include in the HA configuration "
                 "(must include at least one of these traffic types: "
                 "Internal management, Admin panel, Self-service panel or "
                 "Compute API);\n"
                 "ip: virtual IP address that will be used in the HA "
                 "configuration;\n"
                 "addr_type: virtual IP address type (supported starting "
                 "from 3.5 release) (optional).\n"
                 "Specify this option multiple times to create a HA "
                 "configuration for multiple networks."
        )
        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            required=True,
            help="A comma-separated list of node IDs or hostnames"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=None,
            help="Skip checks for minimal hardware requirements."
        )

    def do_action(self, parsed_args):
        nodes = [find_resource(self.app.vinfra.nodes, node)
                 for node in parsed_args.nodes]

        virtual_ips = []
        for network, ipaddr, addr_type in parsed_args.virtual_ips:
            net = find_resource(self.app.vinfra.networks, network)
            virtual_ips.append((net.id, ipaddr, addr_type))

        return self.app.vinfra.ha.create_async(nodes, virtual_ips,
                                               force=parsed_args.force)


class HaUpdate(TaskCommand):
    _description = "Update the HA configuration."

    def configure_parser(self, parser):
        parser.add_argument(
            "--virtual-ip",
            metavar="<network:ip[:addr-type]>",
            type=parse_virtual_ip,
            action="append",
            dest="virtual_ips",
            help="HA configuration mapping in the format:\n"
                 "network: network to include in the HA configuration "
                 "(must include at least one of these traffic types: "
                 "Internal management, Admin panel, Self-service panel or "
                 "Compute API);\n"
                 "ip: virtual IP address that will be used in the HA "
                 "configuration;\n"
                 "addr_type: virtual IP address type (supported starting "
                 "from 3.5 release) (optional).\n"
                 "This option can be used multiple times."
        )
        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            help="A comma-separated list of node IDs or hostnames"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=None,
            help="Skip checks for minimal hardware requirements."
        )

    def do_action(self, parsed_args):
        nodes = None
        if parsed_args.nodes:
            nodes = [find_resource(self.app.vinfra.nodes, node)
                     for node in parsed_args.nodes]

        virtual_ips = []
        if parsed_args.virtual_ips:
            for network, ipaddr, addr_type in parsed_args.virtual_ips:
                net = find_resource(self.app.vinfra.networks, network)
                virtual_ips.append((net.id, ipaddr, addr_type))

        return self.app.vinfra.ha.update_async(nodes=nodes,
                                               virtual_ips=virtual_ips,
                                               force=parsed_args.force)


class HaDelete(TaskCommand):
    _description = "Delete the HA configuration."

    def do_action(self, parsed_args):
        return self.app.vinfra.ha.delete_async()


class AddNodeToHA(TaskCommand):
    _description = "Add nodes to the HA configuration."

    def configure_parser(self, parser):
        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            required=True,
            help="A comma-separated list of node IDs or hostnames"
        )
        parser.add_argument(
            "--without-compute-controller",
            dest='without_controller_service',
            action="store_true",
            default=False,
            help="Deploy the management node without the compute controller "
                 "service"
        )

    def do_action(self, parsed_args):
        nodes = find_resources(self.app.vinfra.nodes, parsed_args.nodes)
        return self.app.vinfra.ha.add_node_async(
            nodes=nodes,
            without_controller_service=parsed_args.without_controller_service
        )


class RemoveNodeFromHA(TaskCommand):
    _description = "Remove node from the HA configuration."

    def configure_parser(self, parser):
        parser.add_argument(
            "nodes",
            metavar="<node>",
            nargs='+',
            help="Node ID or hostname to remove")
        parser.add_argument(
            "--force",
            action="store_true",
            default=None,
            help="Skip the compute cluster state and forcibly remove the node"
        )

    def do_action(self, parsed_args):
        nodes = find_resources(self.app.vinfra.nodes, parsed_args.nodes)
        return self.app.vinfra.ha.remove_node_async(nodes=nodes,
                                                    force=parsed_args.force)
