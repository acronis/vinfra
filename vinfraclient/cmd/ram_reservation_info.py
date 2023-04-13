from vinfraclient.cmd.base import Lister, ShowOne
from vinfraclient.utils import find_resource


def node_arg(parser):
    parser.add_argument(
        "node",
        metavar="<node>",
        help="Node ID or hostname"
    )


class ShowNodesRamReservationInfo(Lister):
    _description = "Show nodes ram reservation details"
    _default_fields = ['id', 'host', 'reservations', 'total']

    def do_action(self, parsed_args):
        nodes = self.app.vinfra.ram_reservation_info.list()
        return nodes


class ShowNodeRamReservationInfo(ShowOne):
    _description = "Show storage node ram reservation details."

    def configure_parser(self, parser):
        node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return self.app.vinfra.ram_reservation_info.get(node)


class ShowTotalRamReservationInfo(ShowOne):
    _description = "Show total ram reservation details"

    def do_action(self, parsed_args):
        return self.app.vinfra.ram_reservation_info.get_total()
