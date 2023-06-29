import argparse
import base64
import logging
import re

from vinfra import api_versions
from vinfra.api.compute.servers import ServerVolumeManager
from vinfraclient.argtypes import parse_dict_options, parse_list_options, size_limited_string
from vinfraclient.cmd.base import (
    Command,
    Lister,
    ShowOne,
    TaskCommand,
    flatten_args,
    KeyValuePair
)
from vinfraclient.exceptions import CommandError, ValidationError
from vinfraclient.formatters import columns as fmt_columns
from vinfraclient import utils


LOG = logging.getLogger(__name__)


class FixedIpList(argparse.Action):
    def __init__(self, option_strings, dest, inline=False, **kwargs):
        super(FixedIpList, self).__init__(option_strings, dest, **kwargs)
        self.inline = inline

    def __call__(self, parser, namespace, values, option_string=None):
        fixed_ips = getattr(namespace, self.dest, []) or []
        if self.inline:
            if '@' in values:
                ip_address, subnet = values.split('@', 1)
                fixed_ips.append({'ip-address': ip_address,
                                  'subnet': subnet})
            else:
                fixed_ips.append({'ip-address': values})
        else:
            if ',' in values or '=' in values:
                fixed_ip = parse_dict_options(
                    values, optional_keys=['ip-address', 'subnet', 'ip-version'])
                fixed_ips.append(fixed_ip)
            else:
                fixed_ips.append({'ip-address': values})
        setattr(namespace, self.dest, fixed_ips)


def _add_network_options(parser):
    parser.add_argument(
        "--ip",
        dest="fixed_ip_deprecated",
        metavar="<ip-address>",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--fixed-ip",
        dest="fixed_ips",
        action=FixedIpList,
        metavar="<ip-address|ip-address=<ip-address>,subnet=<subnet>|ip-version=<ip-version>>",
        help="Desired IP address and/or subnet."
             "This option can be used multiple times.",
    )

    spoofing_protection_group = parser.add_mutually_exclusive_group()
    spoofing_protection_group.add_argument(
        "--spoofing-protection-enable",
        dest="spoofing_protection",
        action='store_const',
        const=True,
        help="Enable spoofing protection for the network interface.",
    )
    spoofing_protection_group.add_argument(
        "--spoofing-protection-disable",
        dest="spoofing_protection",
        action='store_const',
        const=False,
        help="Disable spoofing protection for the network interface.",
    )
    spoofing_protection_group.add_argument(
        "--spoofing-protection",
        dest="spoofing_protection_deprecated",
        choices=['on', 'off'],
        help=argparse.SUPPRESS,
    )

    secgroup_group = parser.add_mutually_exclusive_group()
    secgroup_group.add_argument(
        "--security-group",
        metavar="<security-group>",
        action='append',
        dest='security_groups',
        help="Security group ID or name. This option can be used multiple "
             "times.",
    )
    secgroup_group.add_argument(
        "--no-security-groups",
        dest="security_groups",
        action="store_const",
        const=[],
        help="Do not set security groups",
    )


def get_network_options_dict(parsed_args, network_id, vinfra):
    network = {}

    sp_deprecated = parsed_args.spoofing_protection_deprecated
    if sp_deprecated:
        LOG.warning('spoofing-protection option is deprecated and will be'
                    ' removed in the future')
        network['spoofing_protection'] = sp_deprecated == 'on'

    ip_deprecated = parsed_args.fixed_ip_deprecated
    if ip_deprecated:
        LOG.warning(
            'ip option is deprecated and will be removed in the future')
        network['fixed_ips'] = [ip_deprecated]

    for attr in ('mac_addr', 'fixed_ips', 'spoofing_protection',
                 'security_groups'):
        value = getattr(parsed_args, attr, None)
        if value is not None:
            network[attr] = value

    # pylint: disable=too-many-nested-blocks
    if 'fixed_ips' in network:
        log_warning = False
        for fixed_ip in network['fixed_ips']:
            addr = fixed_ip.pop('ip-address', None)
            if addr:
                fixed_ip['ip_address'] = addr

            filters = {'network_id': network_id}
            subnet = fixed_ip.pop('subnet', None)
            if subnet:
                subnet = utils.find_resource(vinfra.compute.subnets, subnet,
                                             filters=filters)
                fixed_ip['subnet_id'] = subnet.id

            if fixed_ip.get('ip_address') == 'None':
                del fixed_ip['ip_address']
                if 'subnet_id' not in fixed_ip:
                    if vinfra.api_version >= api_versions.HCI_VER_47:
                        # backward compatibility prior to 4.7
                        log_warning = True
                        subnets = vinfra.compute.subnets.list(filters=filters)
                        if not subnets:
                            raise ValidationError(
                                "Network {} has no subnets. Fixed IP address "
                                "can not be used.".format(network_id))
                        # Pick the first subnet:
                        fixed_ip['subnet_id'] = subnets[0].id
                    else:
                        fixed_ip['ip_address'] = None
            if 'ip-version' in fixed_ip:
                if fixed_ip['ip-version'] not in ['4', '6']:
                    raise ValidationError(
                        "Invalid ip-version: {!r}.".format(fixed_ip['ip-version']))

                fixed_ip['ip_version'] = fixed_ip.pop('ip-version')
        if log_warning:
            LOG.info('fixed-ip=None is deprecated and will be removed in '
                     'the future. You need to specifie subnet instead.')
    return network


def subparse_network(value):

    class _SubParser(argparse.ArgumentParser):

        def error(self, message):
            message = message.replace('--', '')
            raise argparse.ArgumentTypeError(message)

    network_parser = _SubParser(conflict_handler='resolve')
    network_parser.add_argument('--id', required=True)
    network_parser.add_argument('--type')
    network_parser.add_argument(
        "--mac",
        dest='mac_addr',
        metavar="<mac>",
        help="MAC address",
    )
    _add_network_options(network_parser)
    network_parser.add_argument(
        '--fixed-ip',
        dest='fixed_ips',
        action=FixedIpList,
        inline=True
    )

    if '=' in value:
        args = ['--' + arg for arg in value.split(',')]
    else:
        args = ['--id', value]
    return network_parser.parse_args(args)


def get_volume_from_dict(volume_dict):
    volume = {}
    mapping = {
        'source': 'source_type',
        'id': 'uuid',
        'size': 'volume_size',
        'bus': 'disk_bus',
        'type': 'device_type',
        'boot-index': 'boot_index',
        'rm': 'delete_on_termination',
        'storage-policy': 'storage_policy_name',
    }

    source = volume_dict.get('source')
    if source is None:
        raise ValidationError("--volume 'source' is required")
    if source not in ['volume', 'image', 'snapshot', 'blank']:
        raise ValidationError(
            "Invalid argument for --volume 'source': {!r}.".format(source))

    uuid = volume_dict.get('id')
    if source == 'blank' and uuid:
        raise ValidationError(
            "--volume source types 'blank' and 'id' are mutually exclusive")
    elif source != 'blank' and not uuid:
        raise ValidationError(
            "--volume 'id' is required for source type {!r}.".format(source))

    if source in ['image', 'blank'] and not volume_dict.get('size'):
        raise ValidationError(
            "--volume 'size' is required for source type {!r}.".format(source))

    bus = volume_dict.get('bus')
    if bus not in ['ide', 'usb', 'virtio', 'scsi', 'sata', None]:
        raise ValidationError(
            "Invalid argument for --volume 'bus': {!r}.".format(bus))

    volume_type = volume_dict.get('type')
    if volume_type not in ['disk', 'cdrom', None]:
        raise ValidationError(
            "Invalid argument for --volume 'type': {!r}.".format(volume_type))

    rm_value = volume_dict.get('rm')
    if rm_value in ['yes', 'no']:
        volume_dict['rm'] = rm_value == 'yes'
    elif rm_value:
        raise ValidationError(
            "Invalid argument for --volume 'rm': {!r}.".format(rm_value))

    for key, value in volume_dict.items():
        if key not in mapping:
            raise ValidationError(
                "unrecognized argument: {}".format(key))
        volume[mapping[key]] = value

    return volume


def _server_arg(parser):
    parser.add_argument(
        "server",
        metavar="<server>",
        help="Compute server ID or name"
    )


class NetworksColumn(fmt_columns.BaseColumn):
    def human_readable(self, value=None):
        networks = []
        for network in self._value:
            name = network['name']
            ips = ', '.join(network['ips'])
            if ips:
                networks.append("{}={}".format(name, ips))
            else:
                networks.append(name)
        return super(NetworksColumn, self).human_readable(value=networks)


class ListServer(Lister):
    _description = "List compute servers."
    _default_fields = ['id', 'name', 'status', 'host', 'networks']
    _formatters = {'networks': NetworksColumn}
    _sort_keys = ['name', 'host', 'project_id', 'task_state', 'vm_state', 'vcpus',
                  'cpu_usage', 'mem_total', 'mem_usage', 'block_capacity', 'block_usage',
                  'created_at', 'updated_at']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help="The maximum number of servers to list. To list all servers, "
                 "set the option to -1."
        )
        parser.add_argument(
            '--marker',
            metavar='<server>',
            help="List servers after the marker."
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List servers with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators=('in', 'contains'),
            help='Show a server with the specified ID or list servers using '
                 'a filter.'
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            action='filter',
            operators='in',
            help='List servers that belong to projects with the specified names or IDs. '
                 'Can only be performed by system administrators. '
                 'Specify multiple project IDs as a comma-separated list.'
        )
        parser.add_argument(
            "--domain",
            metavar="<domain>",
            help='List servers that belong to a domain with the specified name or ID. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help='List servers with the specified status.'
        )
        parser.add_argument(
            '--task-status',
            metavar='<task-status>',
            help='List servers that have the specified task status.'
        )
        parser.add_argument(
            '--host',
            metavar='<hostname>',
            help='List servers located on a node with the specified hostname.'
        )
        parser.add_argument(
            '--placement',
            metavar='<placement>',
            dest='traits',
            action='filter',
            operators='any',
            help='List servers added to a placement with the specified ID or '
                 'use a filter'
        )
        parser.add_argument(
            '--ip-address',
            metavar='<ip-address>',
            help='List servers that have the specified IP address'
        )
        parser.add_argument(
            '--sort',
            metavar='<sort>',
            help="List servers sorted by key.\n"
                 "The sorting format is <sort-key>:<order>. The order is 'asc' or 'desc'.\n"
                 "Supported sort keys: {}".format(', '.join(self._sort_keys))
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.name:
            filters['name'] = parsed_args.name
        if parsed_args.id:
            filters['id'] = parsed_args.id
        if parsed_args.project:
            manager = self.app.vinfra.compute.projects
            filters['project_id'] = utils.validate_resources_from_operator(
                manager, parsed_args.project)
        if parsed_args.domain:
            domain = utils.find_resource(self.app.vinfra.domains, parsed_args.domain)
            filters['domain_id'] = domain.id
        if parsed_args.status:
            filters['status'] = parsed_args.status
        if parsed_args.task_status:
            filters['task_status'] = parsed_args.task_status
        if parsed_args.host:
            filters['host'] = parsed_args.host
        if parsed_args.traits:
            filters['traits'] = parsed_args.traits
        if parsed_args.ip_address:
            filters['ip_address'] = parsed_args.ip_address
        if parsed_args.sort:
            filters['sort'] = parsed_args.sort

        data = self.app.vinfra.compute.servers.list(limit=parsed_args.limit,
                                                    marker=parsed_args.marker,
                                                    filters=filters)
        return data


class ShowServer(ShowOne):
    _description = "Display compute server details."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server_manager = self.app.vinfra.compute.servers
        server = utils.find_resource(server_manager, parsed_args.server)
        return server


class CreateServer(TaskCommand):
    _description = "Create a new compute server."

    def configure_parser(self, parser):
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Server description"
        )
        parser.add_argument(
            "--metadata",
            metavar="<metadata>",
            action=KeyValuePair,
            help="Server metadata in the format key=value. Specify this "
                 "option multiple times to create multiple metadata records."
        )
        parser.add_argument(
            "--user-data",
            metavar="<user-data>",
            help="User data file"
        )
        parser.add_argument(
            "--key-name",
            metavar="<key-name>",
            help="Key pair to inject"
        )
        parser.add_argument(
            "--config-drive",
            action="store_true",
            help="Use an ephemeral drive"
        )
        parser.add_argument(
            "--count",
            metavar="<count>",
            type=int,
            help="If count is specified and greater than 1, the 'name' "
                 "argument is treated as a naming pattern.",
        )
        parser.add_argument(
            "--network",
            metavar="id|<id=id[,mac=mac,fixed-ip=ip-addr[@subnet]>,"
                    "spoofing-protection-enable,spoofing-protection-disable,"
                    "security-group=secgroup,no-security-group]>",
            dest="networks",
            action='append',
            type=subparse_network,
            required=True,
            help="Create a compute server with a specified network. Specify "
                 "this option multiple times to create multiple networks.\n"
                 "id: attach network interface to a specified network (ID or "
                 "name);\n"
                 "mac: MAC address for network interface (optional);\n"
                 "fixed-ip: desired IP and/or subnet for network interface. "
                 "Set IP address to None to allocate IP from desired subnet. "
                 "(optional);\n"
                 "spoofing-protection-enable: enable spoofing protection "
                 "(optional);\n"
                 "spoofing-protection-disable: disable spoofing protection "
                 "(optional);\n"
                 "security-group: security group ID or name. This option can "
                 "be used multiple times (optional);\n"
                 "no-security-group: do not use security group (optional)."
        )
        parser.add_argument(
            '--volume',
            metavar="<source=source[,id=id,key1=value1,key2=value2...]>",
            dest='volumes',
            action='append',
            type=parse_dict_options,
            required=True,
            help="Create a compute server with a specified volume. Specify "
                 "this option multiple times to create multiple volumes.\n"
                 "source: source type ('volume', 'image', 'snapshot', or "
                 "'blank');\n"
                 "id: resource ID or name for the specified source type "
                 "(required for source types 'volume', 'image', and "
                 "'snapshot');\n"
                 "size: block device size, in gigabytes (required "
                 "for source types 'image' and 'blank');\n"
                 "boot-index: block device boot index (required for multiple "
                 "volumes with source type 'volume');\n"
                 "bus: block device controller type ('ide', 'usb', 'virtio', "
                 "'scsi, or 'sata') (optional);\n"
                 "type: block device type (disk or cdrom) (optional);\n"
                 "rm: remove block device on compute server termination "
                 "('yes' or 'no') (optional);\n"
                 "storage-policy: block device storage policy (optional)."
        )
        parser.add_argument(
            "--flavor",
            metavar="<flavor>",
            required=True,
            help="Flavor ID or name",
        )
        parser.add_argument(
            "name",
            metavar="<server-name>",
            help="A new name for the compute server"
        )
        parser.add_argument(
            "--ha-enabled",
            metavar="<ha_enabled>",
            help="Enable HA for the compute server"
        )
        parser.add_argument(
            "--placements",
            metavar="<placements>",
            type=parse_list_options,
            help="Names or IDs of placements to add the virtual machine to."
        )
        parser.add_argument(
            "--allow-live-resize",
            action='store_true',
            default=False,
            help="Allow online resize for the compute server"
        )
        parser.add_argument(
            "--uefi",
            action='store_true',
            default=False,
            help=(
                "Allow UEFI boot for the compute server. "
                "This option can be used for servers created from ISO images."
            )
        )

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute
        flavor = utils.find_resource(compute.flavors, parsed_args.flavor).id

        networks = []
        for parsed_network in parsed_args.networks:
            if parsed_network.type == 'port':
                network = {'port_id': parsed_network.id}
            else:
                net = utils.find_resource(compute.networks, parsed_network.id)
                net_opts = get_network_options_dict(
                    parsed_network, net.id, self.app.vinfra)
                if 'security_groups' in net_opts:
                    secgrpups = utils.find_resources(
                        compute.security_groups, net_opts['security_groups'])
                    net_opts['security_groups'] = [sg.id for sg in secgrpups]
                network = dict(network_id=net.id, **net_opts)
            networks.append(network)

        volumes = []
        for volume_dict in parsed_args.volumes:
            volume = get_volume_from_dict(volume_dict)
            manager = {
                'image': compute.images,
                'volume': compute.volumes,
            }.get(volume['source_type'])
            if manager:
                volume['uuid'] = utils.find_resource(manager, volume['uuid']).id
            volumes.append(volume)

        kwargs = {}
        if parsed_args.user_data:
            try:
                data = open(parsed_args.user_data).read()
            except IOError as err:
                args = parsed_args.user_data, err
                raise ValidationError('Failed to open {} ({})'.format(*args))
            kwargs['user_data'] = base64.b64encode(data)

        kwargs.update(
            flatten_args(parsed_args, ['description', 'metadata', 'key_name',
                                       'config_drive', 'count', 'ha_enabled',
                                       'placements', 'allow_live_resize', 'uefi'])
        )

        task = compute.servers.create_async(
            parsed_args.name, flavor, networks, volumes, **kwargs)
        return task


class DeleteServer(TaskCommand):
    _description = "Delete a compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        task = server.delete_async()
        return task


class SetServer(ShowOne):
    _description = "Modify compute server parameters."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help="A new name for the compute server"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            default=None,
            help="A new description for the compute server"
        )
        parser.add_argument(
            "--ha-enabled",
            metavar="<ha_enabled>",
            default=None,
            help="Enable HA for the compute server"
        )
        parser.add_argument(
            "--password",
            action="store_true",
            help="Request the password from stdin. "
                 "This option must be used separately from other options."
        )
        live_resize_group = parser.add_mutually_exclusive_group()
        live_resize_group.add_argument(
            "--allow-live-resize",
            dest="allow_live_resize",
            action='store_true',
            default=None,
            help="Allow online resize for the compute server"
        )
        live_resize_group.add_argument(
            "--deny-live-resize",
            dest="allow_live_resize",
            action="store_false",
            default=None,
            help="Deny online resize for the compute server"
        )
        placement_group = parser.add_mutually_exclusive_group()
        placement_group.add_argument(
            "--no-placements",
            dest="placements",
            action="store_const",
            const=[],
            help="Clean up placements"
        )
        placement_group.add_argument(
            "--placement",
            dest="placements",
            metavar="placement",
            action="append",
            help="Server placement name or ID. Specify this option multiple "
                 "times to create multiple placement records."
        )
        _server_arg(parser)

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute
        server = utils.find_resource(compute.servers, parsed_args.server)

        kwargs = {}
        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name
        if parsed_args.description is not None:
            kwargs['description'] = parsed_args.description
        if parsed_args.ha_enabled is not None:
            kwargs['ha_enabled'] = parsed_args.ha_enabled
        if parsed_args.allow_live_resize is not None:
            kwargs['allow_live_resize'] = parsed_args.allow_live_resize

        traits = parsed_args.placements
        if traits is not None:
            if traits:
                traits = utils.find_resources(compute.traits, traits)
            kwargs['traits'] = traits

        if parsed_args.password:
            if kwargs:
                raise CommandError(
                    "Password must be specified separately from other options"
                )
            password = utils.get_password()
            return server.set_password(password)

        res = server.update(**kwargs)
        return res


class StartServer(TaskCommand):
    _description = "Start a compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(
            self.app.vinfra.compute.servers, parsed_args.server)
        task = server.start_async()
        return task


class StopServer(TaskCommand):
    _description = "Shut down a compute server."

    def configure_parser(self, parser):
        stop_group = parser.add_mutually_exclusive_group()
        stop_group.add_argument(
            "--hard",
            action="store_true",
            help="Power off a compute server.",
        )
        stop_group.add_argument(
            "--wait-time",
            metavar="<seconds>",
            type=int,
            dest="waittime",
            help="Shutdown timeout, after which a compute server will be\n"
                 "powered off. Specify '-1' to set an infinite timeout.",
        )
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        waittime = parsed_args.waittime
        hard = parsed_args.hard

        task = server.stop_async(hard=hard, timeout=waittime)
        return task


class CancelStopServer(Command):
    _description = "Cancel shutdown for a compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.cancel_stop()


class RebootServer(TaskCommand):
    _description = "Reboot a compute server."
    action = "reboot"

    def configure_parser(self, parser):
        parser.add_argument(
            "--hard",
            action="store_true",
            help="Perform hard reboot.",
        )
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.reboot_async(hard=parsed_args.hard)


class PauseServer(TaskCommand):
    _description = "Pause a compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(
            self.app.vinfra.compute.servers, parsed_args.server)
        return server.pause_async()


class UnpauseServer(TaskCommand):
    _description = "Unpause a compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.unpause_async()


class SuspendServer(TaskCommand):
    _description = "Suspend a compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(
            self.app.vinfra.compute.servers, parsed_args.server)
        return server.suspend_async()


class ResumeServer(TaskCommand):
    _description = "Resume a compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.resume_async()


class ResizeServer(TaskCommand):
    _description = "Resize a compute server."
    action = "resize"

    def configure_parser(self, parser):
        parser.add_argument(
            "--flavor",
            metavar="<flavor>",
            required=True,
            help="Apply flavor with ID or name.",
        )
        _server_arg(parser)

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute
        server = utils.find_resource(compute.servers, parsed_args.server)
        flavor = utils.find_resource(compute.flavors, parsed_args.flavor)
        return server.resize_async(flavor.id)


class ConsoleServer(ShowOne):
    _description = "Display compute server console."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.console()


class StatServer(ShowOne):
    _description = "Display compute server statistics."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.stat()


class LogServer(Command):
    _description = "Display compute server log."

    def configure_parser(self, parser):
        _server_arg(parser)

    # NOTE(akurbatov): override take_action to not produce
    # "Operation successful" on stdout.
    def take_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        data = server.log()
        self.app.stdout.write(data + '\n')


class ResetServerState(TaskCommand):
    _description = "Reset compute server state."

    def configure_parser(self, parser):
        parser.add_argument(
            "--state-error",
            action="store_true",
            help="Reset server to 'ERROR' state",
        )
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        state = 'ERROR' if parsed_args.state_error else 'ACTIVE'
        return server.reset_state_async(state=state)


class MigrateServer(Command):
    _description = "Migrate a compute server to another host."

    def configure_parser(self, parser):
        parser.add_argument(
            "--cold",
            action="store_true",
            default=None,
            help="Perform cold migration. If not set, try to determine "
                 "migration type automatically.",
        )
        parser.add_argument(
            "--node",
            help="Destination node ID or hostname",
        )
        _server_arg(parser)

    def do_action(self, parsed_args):
        node = None
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        if parsed_args.node:
            node = utils.find_resource(self.app.vinfra.nodes, parsed_args.node)
        server.migrate(node=node, cold=parsed_args.cold)


class EvacuateServer(TaskCommand):
    _description = "Evacuate a stopped compute server from a failed host."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.evacuate_async()


class ShelveServer(TaskCommand):
    _description = "Shelve compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.shelve_async()


class UnshelveServer(TaskCommand):
    _description = "Unshelve compute server."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.unshelve_async()


class RescueServer(TaskCommand):
    _description = "Start server rescue mode."

    def configure_parser(self, parser):
        parser.add_argument(
            "--image",
            metavar="<image>",
            help="Boot from image ID or name",
        )
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        image = None
        if parsed_args.image:
            image = utils.find_resource(self.app.vinfra.compute.images,
                                        parsed_args.image)
        task = server.rescue_async(image=image)
        return task


class UnrescueServer(TaskCommand):
    _description = "Exit server from rescue mode."

    def configure_parser(self, parser):
        _server_arg(parser)

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        task = server.unrescue_async()
        return task


class NetworkList(Lister):
    _description = "List compute server networks."
    _default_fields = ['id', 'network_id', 'mac_addr', 'fixed_ips',
                       'spoofing_protection']

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        data = server.networks_manager.list()
        return data


class NetworkAttach(ShowOne):
    _description = "Attach a network to a compute server."

    def configure_parser(self, parser):
        _add_network_options(parser)
        parser.add_argument(
            "--mac",
            dest='mac_addr',
            metavar="<mac>",
            help="MAC address",
        )
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )
        parser.add_argument(
            "--network",
            metavar="<network>",
            required=True,
            help="Network ID or name",
        )

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute

        server = utils.find_resource(compute.servers, parsed_args.server)
        network = utils.find_resource(compute.networks, parsed_args.network)

        net_opts = get_network_options_dict(
            parsed_args, network.id, self.app.vinfra)
        if 'security_groups' in net_opts:
            secgrpups = utils.find_resources(compute.security_groups,
                                             net_opts['security_groups'])
            net_opts['security_groups'] = [sg.id for sg in secgrpups]
        return server.networks_manager.attach(network, **net_opts)


class NetworkUpdate(ShowOne):
    _description = "Update a network interface of a compute server."

    def get_parser(self, prog_name):
        parser = super(NetworkUpdate, self).get_parser(prog_name)
        _add_network_options(parser)
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )
        parser.add_argument(
            "interface",
            metavar="<interface>",
            help="Network interface ID",
        )
        return parser

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute

        server = utils.find_resource(compute.servers, parsed_args.server)
        interface = utils.find_resource(server.networks_manager, parsed_args.interface)

        net_opts = get_network_options_dict(
            parsed_args, interface.network_id, self.app.vinfra)
        if 'security_groups' in net_opts:
            secgrpups = utils.find_resources(compute.security_groups,
                                             net_opts['security_groups'])
            net_opts['security_groups'] = [sg.id for sg in secgrpups]

        return server.networks_manager.update(parsed_args.interface, **net_opts)


class NetworkDetach(Command):
    _description = "Detach a network interface from a compute server."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )
        parser.add_argument(
            "interface",
            metavar="<interface>",
            help="Network interface ID",
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.networks_manager.detach(parsed_args.interface)


class VolumeList(Lister):
    _description = "List compute server volumes."
    _default_fields = ['id', 'device']

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.volumes_manager.list()


class VolumeShow(ShowOne):
    _description = "Show details of a compute server volume."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume ID or name",
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return utils.find_resource(server.volumes_manager, parsed_args.volume)


class VolumeAttach(ShowOne):
    _description = "Attach a volume to a compute server."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume ID or name",
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        return server.volumes_manager.attach(volume)


class VolumeDetach(Command):
    _description = "Detach a volume from a compute server."

    def configure_parser(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            default=None,
            help=("Detach a volume without checking if either the volume "
                  "or server exists. When specifying the volume and server, "
                  "use their IDs. No name lookup is performed.")
        )
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Compute server ID or name",
        )
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help="Volume ID or name",
        )

    def do_action(self, parsed_args):
        if parsed_args.force:
            # use the values given without lookup
            volume_manager = ServerVolumeManager(
                self.app.vinfra.compute.servers.api,
                parsed_args.server,
                force_detach=True)
            return volume_manager.detach(parsed_args.volume)

        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.volumes_manager.detach(volume)


def key_value_pair(value):
    try:
        k, v = value.split('=', 1)
    except ValueError:
        raise argparse.ArgumentTypeError('Invalid format. Expected: key=value')
    return k, v


class MetadataSet(ShowOne):
    _description = "Set compute server metadata."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Server ID or name"
        )
        parser.add_argument(
            "metadata",
            metavar="<metadata>",
            nargs="+",
            type=key_value_pair,
            help="One or more key=value pairs separated by space"
        )

    def do_action(self, parsed_args):
        metadata = {}
        for k, v in parsed_args.metadata:
            metadata[k] = v

        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.metadata_manager.set(metadata)


class MetadataUnset(ShowOne):
    _description = "Unset compute server metadata."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Server ID or name"
        )
        parser.add_argument(
            "metadata",
            metavar="<metadata>",
            nargs="+",
            help="One or more keys separated by space"
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.metadata_manager.unset(parsed_args.metadata)


def tag_validator(value):
    if not re.match('^[^,/]*$', value):
        raise argparse.ArgumentTypeError('Invalid tag. It cannot contain slashes and commas.')
    return size_limited_string(value, 60)


class TagAdd(ShowOne):
    _description = "Add a tag to a compute server."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Server ID or name"
        )
        parser.add_argument(
            "tag",
            metavar="<tag>",
            type=tag_validator,
            help="Server tag"
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.add_tag(parsed_args.tag)


class TagDelete(ShowOne):
    _description = "Delete a tag from a compute server."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Server ID or name"
        )
        parser.add_argument(
            "tag",
            metavar="<tag>",
            type=tag_validator,
            help="Server tag"
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.delete_tag(parsed_args.tag)


class TagList(ShowOne):
    _description = "List compute server tags."

    def configure_parser(self, parser):
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server ID or name"
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return {'tags': server.list_tags()}


class EventList(Lister):
    _description = "List compute server events."
    _default_fields = ['project_id', 'server_id', 'request_id', 'action',
                       'start_time', 'user_id', 'username', 'status']

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Server ID or name",
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.events_manager.list()


class EventShow(ShowOne):
    _description = "Show details of a compute server event."
    _default_fields = ['project_id', 'server_id', 'request_id', 'action',
                       'start_time', 'user_id', 'username', 'status']

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<server>",
            required=True,
            help="Server ID or name",
        )
        parser.add_argument(
            "event",
            metavar="<event>",
            help="Event ID or name",
        )

    def do_action(self, parsed_args):
        server = utils.find_resource(self.app.vinfra.compute.servers,
                                     parsed_args.server)
        return server.events_manager.get(parsed_args.event)
