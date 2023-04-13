from argparse import ArgumentTypeError

from vinfraclient.cmd.base import ShowOne, TaskCommand
from vinfraclient.utils import find_resource


def portal_parser(value):
    if ':' not in value:
        raise ArgumentTypeError('Invalid format: {}.'.format(value))
    address, port = value.split(':', 1)
    return {'address': address, 'port': port}


class ShowTarget(ShowOne):
    _description = "Show details of an iSCSI target on a node."

    def configure_parser(self, parser):
        parser.add_argument(
            "--node",
            required=True,
            metavar="<node>",
            help="Node ID or hostname"
        )

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return node.iscsi_manager.get()


class ConnectTarget(TaskCommand):
    _description = "Add an iSCSI target as a disk to a node."

    def configure_parser(self, parser):
        parser.add_argument(
            "--auth-username",
            metavar="<auth-username>",
            help="User name"
        )
        parser.add_argument(
            "--auth-password",
            metavar="<auth-password>",
            help="User password"
        )
        parser.add_argument(
            "--portal",
            metavar="<portal>",
            dest="portals",
            type=portal_parser,
            action="append",
            required=True,
            help="Portal IP address in the format IP:port (this option can be "
                 "specified multiple times)."
        )
        parser.add_argument(
            "--node",
            required=True,
            metavar="<node>",
            help="Node ID or hostname"
        )
        parser.add_argument(
            "target_name",
            metavar="<target-name>",
            help="Target name"
        )

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        task = node.iscsi_manager.connect_async(
            parsed_args.target_name, parsed_args.portals,
            auth_username=parsed_args.auth_username,
            auth_password=parsed_args.auth_password)
        return task


class DisconnectTarget(TaskCommand):
    _description = "Delete an iSCSI target from a node."

    def configure_parser(self, parser):
        parser.add_argument(
            "--node",
            required=True,
            metavar="<node>",
            help="Node ID or hostname"
        )
        parser.add_argument(
            "target_name",
            metavar="<target-name>",
            help="Target name"
        )

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        task = node.iscsi_manager.disconnect_async(parsed_args.target_name)
        return task
