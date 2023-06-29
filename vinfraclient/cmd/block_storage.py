import argparse
import copy

from vinfraclient.cmd.base import TaskCommand, ShowOne, Lister
from vinfraclient.cmd.compute.storage_policy import storage_policy_options
from vinfraclient.exceptions import ValidationError
from vinfraclient.utils import (
    get_cluster, get_password, find_resource, SizeValue
)


IQN_PREFIX = "iqn.2014-06.com.vstorage:"


def _parse_target(value):
    name, _, value = value.partition(":")
    node, _, ips = value.partition(":")
    ips = ips.split(',')
    if not all([name, node, ips]):
        raise ValidationError(
            'Invalid target parameters: "{}"'.format(value))
    return name, node, ips


class ListTargetGroups(Lister):
    _description = "List target groups."
    _default_fields = ['id', 'name', 'type', 'state', 'running']

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.block_storage.target_groups.list()


class ShowTargetGroup(ShowOne):
    _description = "Show target group details."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        return target_group


class SetTargetGroup(TaskCommand):
    _description = "Set target group parameters."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        acl = parser.add_mutually_exclusive_group()
        acl.add_argument(
            "--enable-acl",
            dest="acl_enabled",
            action="store_true",
            default=None,
            help="Enable ACL",
        )
        acl.add_argument(
            "--disable-acl",
            dest="acl_enabled",
            action="store_false",
            default=None,
            help="Disable ACL",
        )
        chap = parser.add_mutually_exclusive_group()
        chap.add_argument(
            "--enable-chap",
            dest="chap_enabled",
            action="store_true",
            default=None,
            help="Enable CHAP",
        )
        chap.add_argument(
            "--disable-chap",
            dest="chap_enabled",
            action="store_false",
            default=None,
            help="Disable CHAP",
        )
        parser.add_argument(
            "--chap-user",
            metavar="<user-name>",
            help="CHAP user name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        kwargs = dict(
            chap_enabled=parsed_args.chap_enabled,
            chap_user=parsed_args.chap_user,
            acl_enabled=parsed_args.acl_enabled,
        )
        if all(value is None for value in kwargs.values()):
            # argparse don't have 'required=True' for subrparser before python 3.7
            raise ValidationError('At least one parameter must be specified.')
        return target_group.update_async(**kwargs)


class StopTargetGroup(TaskCommand):
    _description = "Stop a target group."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        return target_group.stop_async()


class StartTargetGroup(TaskCommand):
    _description = "Start a target group."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        return target_group.start_async()


class CreateTargetGroup(TaskCommand):
    _description = "Create a target group."

    def configure_parser(self, parser):
        parser.add_argument(
            "--type",
            metavar="<type>",
            required=True,
            choices=['iscsi', 'fc'],
            help="Type of targets in new target group",
        )
        parser.add_argument(
            "--target",
            action='append',
            dest='targets',
            metavar="<name:node:ip1,ip2...>",
            required=True,
            help="Target name, node and IP addresses"
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Target group name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        targets = [
            dict(
                iqn=IQN_PREFIX + name,
                node_id=find_resource(self.app.vinfra.nodes, node).id,
                portals=[dict(ipaddr=ip) for ip in ips],
            ) for name, node, ips in
            (_parse_target(t) for t in parsed_args.targets)
        ]
        return cluster.block_storage.target_groups.create_async(
            name=parsed_args.name, type=parsed_args.type,
            targets=targets)


class DeleteTargetGroup(TaskCommand):
    _description = "Remove a target group."

    def configure_parser(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forcibly remove a target",
        )
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        return target_group.delete_async(force=parsed_args.force)


class ListTargets(Lister):
    _description = "List targets."
    _default_fields = ['node_id', 'iqn', 'state', 'portals']

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)

        return target_group.targets.list()


class ShowTarget(ShowOne):
    _description = "Show target details."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "target",
            metavar="<target>",
            help="Target IQN",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        target = find_resource(target_group.targets, parsed_args.target)
        return target


class CreateTarget(TaskCommand):
    _description = "Create a target."

    def configure_parser(self, parser):
        parser.add_argument(
            "--node",
            metavar="<node>",
            required=True,
            help="Target node",
        )
        parser.add_argument(
            "--ip",
            action='append',
            dest='ips',
            metavar="<ip>",
            required=True,
            help="Target IP address"
        )
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Target name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target = dict(
            wwn=IQN_PREFIX + parsed_args.name,
            node_id=find_resource(self.app.vinfra.nodes, parsed_args.node).id,
            portals=[dict(ipaddr=ip) for ip in parsed_args.ips],
        )
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)

        return target_group.targets.create_async(**target)


class DeleteTarget(TaskCommand):
    _description = "Remove a target."

    def configure_parser(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forcibly remove a target",
        )
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "target",
            metavar="<target>",
            help="Target IQN",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        target = find_resource(target_group.targets, parsed_args.target)
        return target.delete_async(force=parsed_args.force)


class ListVolumes(Lister):
    _description = "List volumes."
    _default_fields = ['id', 'serial', 'name', 'size', 'used_size',
                       'grp_name', 'grp_id', 'lun']

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.block_storage.volumes.list()


class ShowVolume(ShowOne):
    _description = "Show volume details."

    def configure_parser(self, parser):
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return find_resource(cluster.block_storage.volumes,
                             parsed_args.volume)


class SetVolume(TaskCommand):
    _description = "Set volume parameters."

    def configure_parser(self, parser):
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume name or ID",
        )

        parser.add_argument(
            "--read-ops-limit",
            type=int,
            metavar="<iops>",
            help="Number of read operations per second",
        )
        parser.add_argument(
            "--write-ops-limit",
            type=int,
            metavar="<iops>",
            help="Number of write operations per second",
        )
        parser.add_argument(
            "--read-bps-limit",
            type=int,
            metavar="<MiB/s>",
            help="Number of mebibytes read per second",
        )
        parser.add_argument(
            "--write-bps-limit",
            type=int,
            metavar="<MiB/s>",
            help="Number of mebibytes written per second",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)

        volume = find_resource(cluster.block_storage.volumes,
                               parsed_args.volume)
        limits = copy.deepcopy(volume.limits)
        for op in ('read', 'write'):
            val = getattr(parsed_args, '{}_ops_limit'.format(op), None)
            if val is not None:
                limits[op]['ops'] = val
            val = getattr(parsed_args, '{}_bps_limit'.format(op), None)
            if val is not None:
                limits[op]['bps'] = 1024 ** 2 * val
        return volume.update_async(limits=limits)


class CreateVolume(TaskCommand):
    _description = "Create a volume."

    @staticmethod
    def _parse_volume_size(value):
        try:
            return SizeValue(value.strip()).value
        except ValueError:
            raise argparse.ArgumentTypeError(
                'Invalid --size format')

    def configure_parser(self, parser):
        parser.add_argument(
            "--size",
            metavar="<size>",
            type=self._parse_volume_size,
            required=True,
            help="Volume size, in bytes"
        )
        storage_policy_options(parser, required=True)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Volume name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        kwargs = {
            param: getattr(parsed_args, param, None) for param in [
                'name', 'size', 'tier', 'redundancy', 'failure_domain',
            ]
        }
        return cluster.block_storage.volumes.create_async(**kwargs)


class DeleteVolume(TaskCommand):
    _description = "Remove a volume."

    def configure_parser(self, parser):
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        volume = find_resource(cluster.block_storage.volumes,
                               parsed_args.volume)
        return volume.delete_async()


class AttachVolume(TaskCommand):
    _description = "Attach a volume to a target group."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "volume",
            metavar="<name>",
            help="Volume name or ID",
        )
        parser.add_argument(
            "--lun",
            metavar="<lun>",
            type=int,
            help="Lun ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        volume = find_resource(cluster.block_storage.volumes,
                               parsed_args.volume)

        return target_group.volumes.attach_async(
            volume_id=volume.id, lun_id=parsed_args.lun,
        )


class ListTargetGroupVolumes(Lister):
    _description = "List target group volumes."
    _default_fields = ['id', 'serial', 'name', 'size', 'used_size']

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)

        return target_group.volumes.list()


class ShowTargetGroupVolume(ShowOne):
    _description = "Show target group volume details."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        return find_resource(target_group.volumes, parsed_args.volume)


class DetachVolume(TaskCommand):
    _description = "Detach a volume from a target group."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        volume = find_resource(target_group.volumes, parsed_args.volume)
        return target_group.volumes.detach_async(volume)


class ListUsers(Lister):
    _description = "List users."
    _default_fields = ['name']

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.block_storage.users.list()


class ShowUser(ShowOne):
    _description = "Show user details."

    def configure_parser(self, parser):
        parser.add_argument(
            "user",
            metavar="<user>",
            help="User name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return find_resource(cluster.block_storage.users,
                             parsed_args.user)


class CreateUser(TaskCommand):
    _description = "Create a user."

    def configure_parser(self, parser):
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="User desription",
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help="User name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        password = get_password("New user password: ")
        return cluster.block_storage.users.create_async(
            name=parsed_args.name, description=parsed_args.description,
            password=password)


class DeleteUser(TaskCommand):
    _description = "Remove a user."

    def configure_parser(self, parser):
        parser.add_argument(
            "user",
            metavar="<user>",
            help="User name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        user = find_resource(cluster.block_storage.users,
                             parsed_args.user)
        return user.delete_async()


class UpdateUser(TaskCommand):
    _description = "Update a user."

    def configure_parser(self, parser):
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="User description.",
        )
        parser.add_argument(
            "--password",
            action='store_true',
            default=False,
            help="Change user password.",
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help="User name.",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        password = None
        if parsed_args.password:
            password = get_password("New user password: ")
        kwargs = dict(
            description=parsed_args.description,
            password=password
        )
        return cluster.block_storage.users.update_async(
            parsed_args.name, **kwargs)


class ListACLs(Lister):
    _description = "List target group ACL rules."
    _default_fields = ['wwn', 'alias', 'luns']

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)

        return target_group.acls.list()


class AddACL(TaskCommand):
    _description = "Add a target group ACL rule."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "wwn",
            metavar="<wwn>",
            help="WWN",
        )
        parser.add_argument(
            "--alias",
            metavar="<alias>",
            help="Initiator name",
        )
        parser.add_argument(
            "--lun",
            type=int,
            action='append',
            dest='luns',
            metavar="<lun>",
            help="LUN ID"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)

        return target_group.acls.create_async(
            wwn=parsed_args.wwn, alias=parsed_args.alias,
            luns=parsed_args.luns)


class DeleteACL(TaskCommand):
    _description = "Remove a target group ACL rule."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "wwn",
            metavar="<wwn>",
            help="WWN",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)

        return target_group.acls.delete_async(parsed_args.wwn)


class SetACL(TaskCommand):
    _description = "Set target group ACL parameters."

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "wwn",
            metavar="<wwn>",
            help="WWN",
        )
        luns = parser.add_mutually_exclusive_group(required=True)
        luns.add_argument(
            "--lun",
            type=int,
            action='append',
            dest='luns',
            metavar="<lun>",
            help="LUN ID"
        )
        luns.add_argument(
            '--no-luns',
            dest='luns',
            action='store_const',
            const=[],
            help="No LUNs"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)

        return target_group.acls.update_async(
            parsed_args.wwn, luns=parsed_args.luns)


class ListTargetConnections(Lister):
    _description = "List target connections."
    _default_fields = ["ip_addr", "initiator", "target"]

    def configure_parser(self, parser):
        parser.add_argument(
            "target_group",
            metavar="<target-group>",
            help="Target group name or ID",
        )
        parser.add_argument(
            "target",
            metavar="<target>",
            help="Target IQN",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        target_group = find_resource(cluster.block_storage.target_groups,
                                     parsed_args.target_group)
        target = find_resource(target_group.targets, parsed_args.target)
        return target.connections.list()
