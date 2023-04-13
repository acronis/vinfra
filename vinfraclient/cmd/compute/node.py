from vinfraclient.cmd.base import (
    Command,
    Lister,
    ShowOne,
)
from vinfraclient.exceptions import CommandError
from vinfraclient.utils import find_resource


def _node_arg(parser):
    parser.add_argument(
        "node",
        metavar="<node>",
        help="Node ID or hostname"
    )


class ListNode(Lister):
    _description = "List compute nodes."
    _default_fields = ['id', 'host', 'state', 'roles']

    def do_action(self, parsed_args):
        resp = self.app.vinfra.compute.cluster.get()
        if resp['status'] == "absent":
            raise CommandError("Compute cluster is absent.")
        nodes = self.app.vinfra.compute.nodes.list()
        return nodes


class ShowNode(ShowOne):
    _description = "Display compute node details."

    def configure_parser(self, parser):
        parser.add_argument(
            "--with-stats",
            action="store_true",
            default=False,
            help="Get node info with statistics.",
        )
        _node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return self.app.vinfra.compute.nodes.get(
            node.id, with_stats=parsed_args.with_stats)


class FenceNode(Command):
    _description = "Fence a compute node."

    def configure_parser(self, parser):
        parser.add_argument(
            "--force-down",
            action="store_true",
            default=True,
            help="Forcefully mark the node as down.",
        )
        parser.add_argument(
            "--reason",
            metavar="<reason>",
            help="The reason for disabling the compute node"
        )
        _node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.compute.nodes, parsed_args.node)
        return node.fence(force_down=parsed_args.force_down,
                          reason=parsed_args.reason)


class UnfenceNode(Command):
    _description = "Unfence a compute node."

    def configure_parser(self, parser):
        _node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.compute.nodes, parsed_args.node)
        return node.unfence()
