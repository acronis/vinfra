import argparse
import logging
import sys

from vinfraclient.argtypes import parse_dict_options
from vinfraclient.cmd import base
from vinfraclient.cmd.node import utils as node_utils
from vinfraclient.utils import get_cluster, find_resource, find_resources


LOG = logging.getLogger(__name__)


class DiskOption(object):
    metavar = "<disk>:<role>[:<key1=value1,key2=value2...>]"
    help = ("Disk configuration in the format:\n"
            "disk: disk device ID or name;\n"
            "role: disk role ('cs', 'mds', 'journal', 'mds-journal', "
            "'mds-system', 'cs-system', 'system');\n"
            "Comma-separated key=value pairs with keys (optional):\n"
            "tier: disk tier (0, 1, 2 or 3);\n"
            "journal-tier: journal (cache) disk tier (0, 1, 2 or 3);\n"
            "journal-type: journal (cache) disk type ('no_cache', "
            "'inner_cache' or 'external_cache');\n"
            "journal-disk: journal (cache) disk ID or device name;\n"
            "bind-address: bind IP address for the metadata service;\n"
            "e.g., sda:cs:tier=0,journal-type=inner_cache\n"
            "(this option can be used multiple times).")

    def __init__(self, disk, role, params):
        self.disk = disk
        self.role = role
        self.params = params

    @classmethod
    def from_string(cls, value):
        if ':' not in value:
            raise argparse.ArgumentTypeError("unrecognized format mapping")

        options = {}
        disk, role = value.split(':', 1)
        if ':' in role:
            role, other = role.split(':', 1)
            options = parse_dict_options(other)

        if role not in ['cs', 'mds', 'journal', 'mds-journal',
                        'mds-system', 'cs-system', 'system']:
            raise argparse.ArgumentTypeError(
                "Invalid 'role' choice: {!r}.".format(role))

        params = {}
        mapping = {
            'tier': 'tier',
            'journal-tier': 'journal_tier',
            'journal-type': 'journal_type',
            'journal-disk': 'journal_disk_id',
            'journal-size': 'journal_data_size',
            'bind-address': 'bind_address',
        }

        for key, val in options.items():
            if key not in mapping:
                raise argparse.ArgumentTypeError(
                    "unrecognized argument: {}".format(key))
            params[mapping[key]] = val

        return cls(disk, role, params)

    def to_dict(self):
        return {
            'id': self.disk,
            'role': self.role,
            'service_params': self.params
        }


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def _format_disk(disk, formatter):
    new_info = {}
    unavail = disk.disk_status == 'unavail'
    for attr in ('used', 'size'):
        if unavail:
            new_info[attr] = 'unavail'
        else:
            new_info[attr] = disk.space[attr]
            if formatter == 'table':
                new_info[attr] = sizeof_fmt(new_info[attr])

    if formatter == 'table':
        if unavail:
            physical_size = service_params = 'unavail'
        else:
            physical_size = disk.physical_size and sizeof_fmt(disk.physical_size)
            service_params = ','.join(
                "%s=%s" % kv for kv in disk.service_params.items())
        new_info.update({
            'service_params': service_params,
            'physical_size': physical_size,
        })

    disk.set_info(new_info)
    return disk


def _add_disk_argument(parser):
    parser.add_argument(
        "disk",
        metavar="<disk>",
        help="Disk ID or device name"
    )


class ListDisk(base.Lister):
    _description = "List node disks."
    _default_fields = [
        'id', 'device', 'type', 'role', 'disk_status', 'used', 'size', 'physical_size',
        'service_id', 'service_status',
    ]

    def configure_parser(self, parser):
        required = node_utils.is_remove_client()
        node_group = parser.add_mutually_exclusive_group(required=required)
        node_group.add_argument(
            "-a", "--all",
            action="store_true",
            help="List disks on all nodes."
        )
        node_utils.add_node_option(node_group, required=False)

    def do_action(self, parsed_args):
        if parsed_args.all:
            nodes = self.app.vinfra.nodes.list()
        else:
            nodes = [find_resource(self.app.vinfra.nodes, parsed_args.node)]

        disks = []
        for node in nodes:
            for disk in node.disks_manager.list():
                disks.append(_format_disk(disk, parsed_args.formatter))
        return disks


class ShowDiskDiagnosticInfo(base.Lister):

    _description = "Show diagnostic information of a disk"
    _default_fields = ["command", "stdout"]

    def configure_parser(self, parser):
        node_utils.add_node_option(parser)
        _add_disk_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        disk = find_resource(node.disks_manager, parsed_args.disk)
        return node.disks_manager.get_diagnostic_info(disk)


class ShowDisk(base.ShowOne):
    _description = "Show details of a disk."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser)
        _add_disk_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        disk = find_resource(node.disks_manager, parsed_args.disk)
        return disk


class AssignDiskBulk(base.TaskCommand):
    _description = "Add multiple disks to the storage cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--disk",
            dest="disks",
            action="append",
            required=True,
            metavar=DiskOption.metavar,
            type=DiskOption.from_string,
            help=DiskOption.help,
        )
        node_utils.add_node_option(parser)

    def do_action(self, parsed_args):
        disks = []
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        for disk in parsed_args.disks:
            disk.disk = find_resource(node.disks_manager, disk.disk).id
            if disk.params.get('journal_disk_id'):
                disk.params['journal_disk_id'] = find_resource(
                    node.disks_manager, disk.params['journal_disk_id']).id
            disks.append(disk.to_dict())

        cluster = get_cluster(self.app.vinfra)
        return node.disks_manager.assign_bulk_async(disks, cluster=cluster)


class ReleaseDisk(base.TaskCommand):
    _description = """Release disk(s) from the storage cluster.
                      Start data migration from the node as well as cluster
                      replication and rebalancing to meet the configured
                      redundancy level."""

    def configure_parser(self, parser):
        parser.add_argument(
            "--force",
            action='store_true',
            help="Release without data migration."
        )
        node_utils.add_node_option(parser)
        parser.add_argument(
            "--disk",
            dest="disks",
            action="append",
            metavar="<disk>",
            help=(
                "Disk ID or device name\n"
                "(this option can be used multiple times)."
            ),
        )
        parser.add_argument(
            "disk",
            nargs="?",
            metavar="<disk>",
            help="Disk ID or device name (deprecated)"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)

        disks = []
        if parsed_args.disks is not None:
            disks += find_resources(node.disks_manager, parsed_args.disks)
        if parsed_args.disk is not None:
            LOG.info("Positional argument is deprecated. Use --disk instead.")
            disks += [find_resource(node.disks_manager, parsed_args.disk)]

        if not disks:
            LOG.error("No disks to release.")
            sys.exit(1)

        return node.disks_manager.release_bulk_async(
            disks, force=parsed_args.force, cluster=cluster
        )


class RecoverDisk(base.Command):
    _description = "Recover a disk."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser)
        _add_disk_argument(parser)

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        disk = find_resource(node.disks_manager, parsed_args.disk)
        return disk.recover(cluster=cluster)


class StartBlinkDisk(base.Command):
    _description = ("Start blinking the specified disk bay to "
                    "identify disk for maintenance purposes.")

    def configure_parser(self, parser):
        node_utils.add_node_option(parser)
        _add_disk_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        disk = find_resource(node.disks_manager, parsed_args.disk)
        return disk.blink_start()


class StopBlinkDisk(base.Command):
    _description = "Stop blinking the specified disk bay."

    def configure_parser(self, parser):
        node_utils.add_node_option(parser)
        _add_disk_argument(parser)

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        disk = find_resource(node.disks_manager, parsed_args.disk)
        return disk.blink_stop()
