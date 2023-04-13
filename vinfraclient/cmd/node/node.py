from vinfraclient.cmd.base import Lister, ShowOne, TaskCommand
from vinfraclient.cmd.node.disk import DiskOption
from vinfraclient.utils import get_cluster, find_resource


def node_arg(parser):
    parser.add_argument(
        "node",
        metavar="<node>",
        help="Node ID or hostname"
    )


class ListNode(Lister):
    _description = "List storage nodes."
    _default_fields = ['id', 'host', 'is_primary', 'is_online', 'is_assigned',
                       'is_in_ha']

    @staticmethod
    def find_network_name(networks, network_id):
        for network in networks:
            if network.id == network_id:
                return network.name
        return ''

    def do_action(self, parsed_args):
        nodes = self.app.vinfra.nodes.list()
        return nodes


class ShowNode(ShowOne):
    _description = "Show storage node details."

    def configure_parser(self, parser):
        node_arg(parser)

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.nodes, parsed_args.node)


class ForgetNode(TaskCommand):
    _description = "Remove a node from the storage cluster."

    def configure_parser(self, parser):
        node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        task = node.delete_async()
        return task


class JoinNode(TaskCommand):
    _description = "Join a node to the storage cluster"

    def configure_parser(self, parser):
        parser.add_argument(
            "--disk",
            dest="disks",
            action="append",
            metavar=DiskOption.metavar,
            type=DiskOption.from_string,
            help=DiskOption.help,
        )
        parser.add_argument(
            "node",
            metavar="<node>",
            help="Node ID or hostname"
        )

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)

        disks = None
        if parsed_args.disks:
            disks = []
            for disk in parsed_args.disks:
                disk.disk = find_resource(node.disks_manager, disk.disk).id
                if disk.params.get('journal_disk_id'):
                    disk.params['journal_disk_id'] = find_resource(
                        node.disks_manager, disk.params['journal_disk_id']).id
                disks.append(disk.to_dict())

        cluster = get_cluster(self.app.vinfra)
        return cluster.join_node_async(node.id, disks=disks)


class ReleaseNode(TaskCommand):
    _description = ("Release a node from the storage cluster.\n"
                    "Start data migration from the node as well as cluster "
                    "replication and rebalancing to meet the configured "
                    "redundancy level.")

    def configure_parser(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            default=None,
            help="Release node without data migration."
        )
        node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return node.release_async(force=parsed_args.force)


class MaintenanceNodeStatus(ShowOne):
    _description = "Show node maintenance details."

    def configure_parser(self, parser):
        node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return node.maintenance_status()


class MaintenanceNodeStart(TaskCommand):
    _description = "Start node maintenance."

    def configure_parser(self, parser):
        parser.add_argument(
            "--iscsi-mode",
            metavar='<mode>',
            choices=["ignore"],
            help="Ignore ISCSI evacuation during maintenance"
        )
        parser.add_argument(
            "--compute-mode",
            metavar='<mode>',
            choices=["ignore"],
            help="Ignore compute evacuation during maintenance"
        )
        parser.add_argument(
            "--s3-mode",
            metavar='<mode>',
            choices=["ignore"],
            help="Ignore S3 evacuation during maintenance"
        )
        parser.add_argument(
            "--storage-mode",
            metavar='<mode>',
            choices=["ignore"],
            help="Ignore storage evacuation during maintenance"
        )
        parser.add_argument(
            "--alua-mode",
            metavar='<mode>',
            choices=["ignore"],
            help="Ignore Block Storage target groups during maintenance"
        )
        parser.add_argument(
            "--nfs-mode",
            metavar='<mode>',
            choices=["ignore"],
            help="Ignore NFS evacuation during maintenance"
        )
        node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)

        return node.maintenance_start(
            iscsi_mode=parsed_args.iscsi_mode,
            compute_mode=parsed_args.compute_mode,
            s3_mode=parsed_args.s3_mode,
            storage_mode=parsed_args.storage_mode,
            alua_mode=parsed_args.alua_mode,
            nfs_mode=parsed_args.nfs_mode,
        )


class MaintenanceNodeStop(TaskCommand):
    _description = "Return node to operation."

    def configure_parser(self, parser):
        parser.add_argument(
            "--ignore-compute",
            action='store_true',
            default=False,
            help="Ignore compute resources while returning a node to operation"
        )
        node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return node.maintenance_stop(
            ignore_compute=parsed_args.ignore_compute
        )


class MaintenanceNodePrecheck(TaskCommand):
    _description = "Start node maintenance precheck."

    def configure_parser(self, parser):
        node_arg(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return node.maintenance_precheck()
