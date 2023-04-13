import datetime
import time
import uuid

import progressbar as pb

from vinfra.exceptions import TimeoutError
from vinfraclient import utils
from vinfraclient.cmd.base import Command, ShowOne, TaskCommand
from vinfraclient.cmd.node.disk import DiskOption
from vinfraclient.exceptions import CommandError, AbortError


class ShowCluster(ShowOne):
    _description = "Show cluster details"

    def do_action(self, parsed_args):
        cluster = utils.get_cluster(self.app.vinfra)
        for node in cluster.nodes:
            node['id'] = str(uuid.UUID(node['id']))
        return cluster


class CreateCluster(TaskCommand):
    _description = "Create a storage cluster"

    def configure_parser(self, parser):
        parser.add_argument(
            "--tier-encryption",
            dest="encryptions",
            type=int,
            choices=range(0, 4),
            action="append",
            help="Enable encryption for storage cluster tiers. Encryption is "
                 "disabled by default. This option can be used multiple times."
        )
        parser.add_argument(
            "--disk",
            dest="disks",
            action="append",
            metavar=DiskOption.metavar,
            type=DiskOption.from_string,
            help=DiskOption.help,
        )
        parser.add_argument(
            "--node",
            metavar="<node>",
            required=True,
            help="Node ID or hostname"
        )
        parser.add_argument(
            "name",
            metavar="<cluster-name>",
            help="Storage cluster name"
        )

    def do_action(self, parsed_args):
        disks = None
        encryption = None

        node = utils.find_resource(self.app.vinfra.nodes, parsed_args.node)

        if parsed_args.encryptions:
            encryption = {}
            # NOTE(akurbatov): backend API requires all tiers to be specified
            for tier in range(0, 4):
                encryption['tier%s' % tier] = tier in parsed_args.encryptions

        if parsed_args.disks:
            disks = []
            for disk in parsed_args.disks:
                disk.disk = utils.find_resource(
                    node.disks_manager, disk.disk).id
                if disk.params.get('journal_disk_id'):
                    disk.params['journal_disk_id'] = utils.find_resource(
                        node.disks_manager, disk.params['journal_disk_id']).id
                disks.append(disk.to_dict())

        return self.app.vinfra.clusters.create_async(
            node.id, parsed_args.name, encryption=encryption, disks=disks)


class DeleteCluster(Command):
    _description = "Delete the storage cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--timeout",
            metavar="<seconds>",
            type=int,
            default=600,
            help="A timeout for the operation to complete, in seconds"
                 " (default: 600)"
        )

    def do_action(self, parsed_args):
        timeout = parsed_args.timeout
        cluster = utils.get_cluster(self.app.vinfra)

        def raise_timeout():
            raise CommandError("Operation timed out. Re-run the command "
                               "with the --timeout option.")

        def release_node(node_id, endtime):
            timeout = endtime - time.time()
            if timeout <= 0:
                raise_timeout()
            task = self.app.vinfra.nodes.release_async(node_id, force=True)
            try:
                task.wait(timeout=timeout)
            except TimeoutError:
                raise_timeout()

            while True:
                _node = None
                if endtime - time.time() < 0:
                    raise_timeout()
                for _node in self.app.vinfra.nodes.list():
                    if _node.id == str(uuid.UUID(node_id)):
                        break
                else:
                    raise AbortError("No node with id={}".format(node_id))
                if _node and not _node.is_assigned:
                    break
                time.sleep(1)

        def release_cluster():
            endtime = time.time() + timeout
            # Note(akurbatov): we can't remove node with last MDS if there
            # another cs nodes.
            mds_node_ids = []
            for node in cluster.nodes:
                disks = self.app.vinfra.node_obj(
                    node['id']).disks_manager.list()
                for disk in disks:
                    if 'mds' in disk.role:
                        mds_node_ids.append(node['id'])
                        break
                else:
                    release_node(node['id'], endtime)

            for node_id in mds_node_ids:
                release_node(node_id, endtime)

        self.app.print_message("Operation waiting ...")

        format_pattern = '[timeout: {}, elapsed time: %s]  '.format(
            datetime.timedelta(seconds=timeout))
        widgets = [pb.Timer(format=format_pattern), pb.AnimatedMarker()]

        pbar = pb.ProgressBar(maxval=80, term_width=80, widgets=widgets,
                              fd=self.app.stderr)
        with utils.progress_bar_context(self.app, pbar, timeout=timeout):
            release_cluster()


class Overview(ShowOne):
    _description = "Show storage cluster overview."

    def do_action(self, parsed_args):
        cluster = utils.get_cluster(self.app.vinfra)
        return cluster.overview()


class ShowPassword(ShowOne):
    _description = "Show storage cluster password."

    def do_action(self, parsed_args):
        cluster = utils.get_cluster(self.app.vinfra)
        return cluster.get_password()


class SetPassword(ShowOne):
    _description = "Set storage cluster password."

    def do_action(self, parsed_args):
        cluster = utils.get_cluster(self.app.vinfra)
        password = utils.get_password("Password: ")
        return cluster.set_password(password)


class GetJoinConfig(ShowOne):
    _description = "Get disk configurations for joining a node to the cluster"

    def configure_parser(self, parser):
        parser.add_argument(
            "node",
            metavar="<node>",
            help="Node ID or hostname"
        )

    def do_action(self, parsed_args):
        cluster = utils.get_cluster(self.app.vinfra)
        return cluster.get_join_config(parsed_args.node)


class SetJoinConfig(ShowOne):
    _description = "Set disk configurations for joining a node to the cluster"

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
        cluster = utils.get_cluster(self.app.vinfra)
        return cluster.set_join_config(parsed_args.node, parsed_args.disks)


class SwitchToIPv6(TaskCommand):
    _description = "Switch storage cluster to IPv6."

    def configure_parser(self, parser):
        parser.add_argument(
            "--reset",
            dest="reset",
            action="store_true",
            help="Reset cluster back to IPv4",
        )

    def do_action(self, parsed_args):
        if parsed_args.reset:
            return self.app.vinfra.clusters.reset_ipv6_async()
        return self.app.vinfra.clusters.switch_to_ipv6_async()
