import copy
import logging
from argparse import ArgumentTypeError, SUPPRESS
from collections import defaultdict, namedtuple

import netaddr

from vinfra import exceptions as vinfra_exceptions
from vinfra.api import base as api_base
from vinfra.api.compute import networks as vinfra_networks

from vinfraclient import argtypes
from vinfraclient.cmd import base
from vinfraclient.exceptions import ValidationError
from vinfraclient import utils
from vinfraclient.formatters import columns as fmt_columns


LOG = logging.getLogger(__name__)
RbacEntry = namedtuple('RbacEntry', ['target', 'target_id', 'action'])


def log_subnet_deprecation_message(parsed_args):
    columns = parsed_args.columns or vinfra_networks.SUBNET_DEPRECATED_FIELDS
    subnet_deprecated_fields = (
        set(columns) & set(vinfra_networks.SUBNET_DEPRECATED_FIELDS))
    if subnet_deprecated_fields:
        LOG.info('Next columns are deprected: %s. Use subnets[] fields.',
                 ', '.join(subnet_deprecated_fields))


class AllocationPoolsColumn(fmt_columns.BaseColumn):
    def human_readable(self, value=None):
        pools = []
        for pool in self._value or []:
            pools.append('%s-%s' % (pool['start'], pool['end']))
        return super(AllocationPoolsColumn, self).human_readable(value=pools)


class SubnetsColumn(fmt_columns.BaseColumn):
    def human_readable(self, value=None):
        subnets = copy.deepcopy(self._value)
        for subnet in subnets:
            pools = []
            for pool in subnet['allocation_pools']:
                pools.append('%s-%s' % (pool['start'], pool['end']))
            subnet['allocation_pools'] = pools
        return super(SubnetsColumn, self).human_readable(value=subnets)


class RbacPolicies(object):
    VALID_RBAC_ACTIONS = {'routed', 'direct', 'full'}
    VALID_RBAC_TARGETS = {'domain', 'project'}

    def __call__(self, value):
        if value.lower() == 'none':
            return []

        # (target, target_id) => actions
        rbac_policies = defaultdict(set)
        for rbac in value.split(','):
            rbac = rbac.strip()
            try:
                rbac_entry = RbacEntry(*rbac.split(':', 2))
            except TypeError:
                raise ArgumentTypeError(
                    'Invalid RBAC format: <target>:<target_id>:<action>')

            if rbac_entry.target not in self.VALID_RBAC_TARGETS:
                raise ArgumentTypeError(
                    'Invalid RBAC target: %s' % rbac_entry.target)

            if rbac_entry.action not in self.VALID_RBAC_ACTIONS:
                raise ArgumentTypeError(
                    'Invalid RBAC action: %s' % rbac_entry.action)

            key = (rbac_entry.target, rbac_entry.target_id)
            if rbac_entry.action == 'full':
                # full = routed | direct
                rbac_policies[key].add('routed')
                rbac_policies[key].add('direct')
            else:
                rbac_policies[key].add(rbac_entry.action)

        return [
            {'target_%s' % target: target_id, 'actions': list(actions)}
            for (target, target_id), actions in rbac_policies.items()
        ]


def parse_allocation_pool(value):
    try:
        start, end = value.split('-')
    except ValueError:
        raise ArgumentTypeError('Incorrect IP address range: {}'.format(value))
    return {'start': start, 'end': end}


def _common_subnet_set_options(parser, deprecated=False):

    def help_msg(msg):
        return msg + " (DEPRECATED)" if deprecated else msg

    dhcp_group = parser.add_mutually_exclusive_group()
    dhcp_group.add_argument(
        "--dhcp",
        dest='enable_dhcp',
        action='store_true',
        default=None,
        help=help_msg("Enable DHCP")
    )
    dhcp_group.add_argument(
        "--no-dhcp",
        dest='enable_dhcp',
        action='store_false',
        default=None,
        help=help_msg("Disable DHCP")
    )
    parser.add_argument(
        "--dns-nameserver",
        metavar="<dns-nameserver>",
        dest="dns_nameservers",
        action="append",
        help=help_msg(
            "DNS server IP address. This option can be used multiple times.")
    )
    parser.add_argument(
        "--allocation-pool",
        metavar="<allocation-pool>",
        dest="allocation_pools",
        type=parse_allocation_pool,
        action="append",
        help=help_msg(
            "Allocation pool to create inside the network in the format: "
            "ip_addr_start-ip_addr_end. This option can be used multiple "
            "times.")
    )
    gateway_parser = parser.add_mutually_exclusive_group()
    gateway_parser.add_argument(
        "--gateway",
        metavar="<gateway>",
        dest="gateway_ip",
        help=help_msg("Gateway IP address.")
    )
    gateway_parser.add_argument(
        "--no-gateway",
        dest="gateway_ip",
        action="store_false",
        help=help_msg("Do not configure a gateway for this network")
    )


def _common_set_options(parser, subnet_deprecated=False):
    _common_subnet_set_options(parser, deprecated=subnet_deprecated)
    parser.add_argument(
        "--rbac-policies",
        metavar="<rbac-policies>",
        type=RbacPolicies(),
        help="Comma-separated list of RBAC policies in the format: "
             "<target>:<target_id>:<action> | none. Valid targets: {}. "
             "Valid actions: {}. '*' is valid target_id for all targets. "
             "Pass 'none' to clear out all existing policies. "
             "Example: domain:default:routed,project:uuid1:full".format(
                 ', '.join(RbacPolicies.VALID_RBAC_TARGETS),
                 ', '.join(RbacPolicies.VALID_RBAC_ACTIONS))
    )
    parser.add_argument(
        "--shared",
        metavar="<shared>",
        type=argtypes.boolean,
        help="Share the network between all tenants (DEPRECATED)"
    )


def _network_arg(parser):
    parser.add_argument(
        "network",
        metavar="<network>",
        help="Network ID or name"
    )


def _subnet_arg(parser):
    parser.add_argument(
        "subnet",
        metavar="<subnet>",
        help="Subnet ID"
    )


class ListNetwork(base.Lister):
    _description = "List compute networks."
    _default_fields = ['id', 'name', 'physical_network', 'cidr', 'enable_dhcp',
                       'gateway_ip', 'dns_nameservers', 'allocation_pools',
                       'rbac_policies']
    _formatters = {
        'allocation_pools': AllocationPoolsColumn,
        'subnets': SubnetsColumn
    }
    _sort_keys = ['id', 'name', 'status', 'admin_state_up', 'availability_zone_hints',
                  'mtu', 'tenant_id', 'project_id', 'type', 'created_at', 'updated_at']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of networks to list. To list all networks, '
                 'set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<network>',
            help='List networks after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List networks with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a network with the specified ID or list networks using '
                 'a filter.'
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            action='filter',
            operators='in',
            help='List networks that belong to projects with the specified names or IDs. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            "--domain",
            metavar="<domain>",
            help='List networks that belong to a domain with the specified name or ID. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            action='filter',
            operators='in',
            help='List networks with the specified type or use a filter.'
        )
        parser.add_argument(
            '--sort',
            metavar='<sort>',
            help="List networks sorted by key.\n"
                 "The sorting format is <sort-key>:<order>. The order is 'asc' or 'desc'.\n"
                 "Supported sort keys: {}".format(', '.join(self._sort_keys))
        )

    @staticmethod
    def _parse_type_filter(type_filter):
        if ':' in type_filter:
            op, vals = type_filter.split(':', 1)

            res_vals = []
            for val in vals.split(','):
                if val == 'virtual':
                    res_vals.append('vxlan')
                elif val == 'physical':
                    res_vals.extend(['flat', 'vlan'])
                else:
                    res_vals.append(val)

            return '{}:{}'.format(op, ','.join(res_vals))

        if type_filter == 'virtual':
            return 'vxlan'
        elif type_filter == 'physical':
            return 'in:flat,vlan'
        return type_filter

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
        if parsed_args.type:
            filters['type'] = self._parse_type_filter(parsed_args.type)
        if parsed_args.sort:
            filters['sort'] = parsed_args.sort

        networks = self.app.vinfra.compute.networks.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)

        log_subnet_deprecation_message(parsed_args)
        return networks


class ShowNetwork(base.ShowOne):
    _description = "Display compute network details."
    _formatters = {
        'allocation_pools': AllocationPoolsColumn,
        'subnets': SubnetsColumn
    }

    def configure_parser(self, parser):
        _network_arg(parser)

    def do_action(self, parsed_args):
        network = utils.find_resource(self.app.vinfra.compute.networks,
                                      parsed_args.network)

        log_subnet_deprecation_message(parsed_args)
        return network


class ComputeNetworkWrapTask(api_base.Task):
    def __init__(self, data):
        super(ComputeNetworkWrapTask, self).__init__()
        self.data = data

    def wait(self, timeout=None):
        raise vinfra_exceptions.VinfraError(
            "Wait is not implemented for virtual networks")

    def get_info(self):
        return self.data


class ComputeNetworkContext(object):
    """ContextManager for switching base_url on Compute.NetworkManager.

    Added for self-service, where domain_admin can create/delete only
    private networks, and have different urls for this actions.
    """

    _NETWORK_TYPE_TO_URL = {
        'physical': 'public',
        'virtual': 'private',
        'vlan': 'vlan',
    }

    def __init__(self, app, parsed_args, network_type):
        self.app = app
        self.original = self.app.vinfra.compute.networks.base_url
        self.parsed_args = parsed_args
        self._network_type = network_type

    def _is_self_service_context(self):
        return any([self.app.vinfra.session.auth.project,
                    self.app.vinfra.session.auth.domain])

    def _validate(self):
        # if user has project/domain set in auth,
        # he can work only with private networks.
        if self._is_self_service_context() and self._network_type in ('physical', 'vlan'):
            raise vinfra_exceptions.VinfraError(
                "Cannot operate physical networks in the self service scope.")

        # vxlan network creation doesn't use tasks
        if self.parsed_args.wait and self._network_type == 'virtual':
            raise vinfra_exceptions.VinfraError(
                "The --wait option is not supported for virtual networks.")

    def __enter__(self):
        self._validate()
        self.app.vinfra.compute.networks.base_url = "{}/{}".format(
            self.original, self._NETWORK_TYPE_TO_URL[self._network_type])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.app.vinfra.compute.networks.base_url = self.original


class NetworkMixin(object):
    _formatters = {
        'allocation_pools': AllocationPoolsColumn,
        'subnets': SubnetsColumn
    }

    @staticmethod
    def _validate_network_args(network_type, parsed_args):
        if (parsed_args.rbac_policies is not None and
                network_type == 'virtual'):
            raise ValidationError('The --rbac-policies option is not '
                                  'supported for virtual networks.')

        default_vnic_type = getattr(parsed_args, 'default_vnic_type', None)
        if default_vnic_type and network_type != 'physical':
            raise ValidationError('The --default-vnic-type is not '
                                  'supported for %s networks.' % network_type)


class CreateNetwork(base.TaskCommand, NetworkMixin):
    _description = "Create a compute network."

    def _configure_parser_inner(self, parser):
        task_group = parser.add_argument_group(
            title="command run options",
            description='additional command options',
        )
        task_group.add_argument(
            "--wait",
            action="store_true",
            help="Wait for the operation to complete (synchronous mode)."
                 "Supported only in the admin scope."
        )
        task_group.add_argument(
            "--timeout",
            metavar="<seconds>",
            type=int,
            default=600,
            help="A timeout for the operation to complete if --wait is "
                 "specified, in seconds (default: 600). "
                 "Supported only in the admin scope."
        )
        _common_set_options(parser)
        parser.add_argument(
            "--ip-version",
            metavar="<ip-version>",
            help=SUPPRESS  # backend hasn't fully support of IPv6 yet
        )
        parser.add_argument(
            "--physical-network",
            metavar="<physical-network>",
            help="A physical network to link to a flat network"
        )
        parser.add_argument(
            "--default-vnic-type",
            choices=["normal", "direct"],
            help="Virtual port will inherit specified vnic_type from network"
        )
        parser.add_argument(
            "--vlan-network",
            metavar="<vlan-network>",
            help="A VLAN network to link"
        )
        parser.add_argument(
            "--cidr",
            metavar="<cidr>",
            help="Subnet range in CIDR notation"
        )
        parser.add_argument(
            "name",
            metavar="<network-name>",
            help="Network name"
        )
        parser.add_argument(
            "--type",
            choices=['vxlan', 'flat', 'vlan'],
            help=SUPPRESS,
        )
        parser.add_argument(
            "--vlan",
            metavar="<vlan>",
            type=int,
            help='Virtual network VLAN ID',
        )
        parser.add_argument(
            "--mtu",
            metavar="<mtu>",
            type=int,
            help='MTU Value',
        )
        # NOTE(akurbatov): suppress ipv6 RA mode while we don't support ipv6
        # for vxlan networks. And there is no use case to create a flat network
        # with internal RA management, because we agreed that adding a flat
        # network to the router as internal port is not a use case.
        # parser.add_argument(
        #     "--ipv6-ra-mode",
        #     choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
        #     help="IPv6 RA (Router Advertisement) mode, valid modes: "
        #          "[dhcpv6-stateful, dhcpv6-stateless, slaac]"
        # )
        parser.add_argument(
            "--ipv6-address-mode",
            choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
            help="IPv6 address mode, valid modes: "
                 "[dhcpv6-stateful, dhcpv6-stateless, slaac]"
        )

    def do_action(self, parsed_args):
        # See comment above with suppressing ipv6-ra-mode
        parsed_args.ipv6_ra_mode = None

        network_manager = self.app.vinfra.compute.networks

        subnets = []
        subnet_options = [
            'cidr', 'enable_dhcp', 'dns_nameservers', 'allocation_pools',
            'gateway_ip', 'ip_version', 'ipv6_ra_mode', 'ipv6_address_mode'
        ]
        subnet = base.flatten_args(parsed_args, subnet_options)
        if subnet:
            if 'cidr' not in subnet:
                options = ['--' + opt.replace('_', '-').rstrip('s')
                           for opt in subnet]
                raise ValidationError(
                    'The next options cannot be used without cidr specifying: '
                    + ', '.join(options))
            CreateSubnet.validate_args(parsed_args)
            if subnet.get('gateway_ip') is False:
                subnet['gateway_ip'] = None
            subnets.append(subnet)

        if parsed_args.type:
            LOG.warning('The --type option is deprecated. '
                        'The network type will be detected automatically.')

        if parsed_args.shared is not None:
            LOG.warning('The --shared option is deprecated. '
                        'Please use --rbac-policies instead.')

        if parsed_args.vlan_network and not parsed_args.vlan:
            raise ValidationError("--vlan must be specified for VLAN network")

        network_type = (
            'vlan' if parsed_args.vlan else
            'physical' if parsed_args.physical_network else
            'virtual'
        )

        self._validate_network_args(network_type, parsed_args)

        with ComputeNetworkContext(self.app, parsed_args, network_type):
            params = dict(
                name=parsed_args.name,
                subnets=subnets,
                mtu=parsed_args.mtu,
            )
            if network_type == 'virtual':
                network = network_manager.create(**params)
                log_subnet_deprecation_message(parsed_args)
                return ComputeNetworkWrapTask(network)

            params.update(
                physical_network=parsed_args.physical_network,
                vlan=parsed_args.vlan,
                vlan_network=parsed_args.vlan_network,
                rbac_policies=parsed_args.rbac_policies,
                default_vnic_type=parsed_args.default_vnic_type,
            )
            return network_manager.create_async(**params)


class DeleteNetwork(base.TaskCommand):
    _description = "Delete a compute network."

    def configure_parser(self, parser):
        parser.add_argument(
            "--delete-vlan-interfaces",
            action="store_true",
            default=None,
            help="Delete node VLAN interfaces along with the compute "
                 "VLAN network."
        )
        _network_arg(parser)

    def do_action(self, parsed_args):
        network = utils.find_resource(
            self.app.vinfra.compute.networks, parsed_args.network)

        network_type = network.type
        if network_type == 'physical' and network.vlan_id:
            network_type = 'vlan'

        if parsed_args.delete_vlan_interfaces and network_type != 'vlan':
            raise ValidationError("The --delete-vlan-interfaces option "
                                  "only works for VLAN networks.")

        with ComputeNetworkContext(self.app, parsed_args, network_type):
            return network.delete_async(
                delete_vlan_interfaces=parsed_args.delete_vlan_interfaces)


class SetNetwork(base.ShowOne, NetworkMixin):
    _description = "Modify compute network parameters."

    def configure_parser(self, parser):
        _common_set_options(parser, subnet_deprecated=True)
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the network"
        )
        parser.add_argument(
            "--mtu",
            metavar="<mtu>",
            type=int,
            help='MTU Value',
        )
        _network_arg(parser)

    def do_action(self, parsed_args):
        if parsed_args.shared is not None:
            LOG.warning('The --shared option is deprecated. '
                        'Please use --rbac-policies instead.')

        network = utils.find_resource(
            self.app.vinfra.compute.networks, parsed_args.network)

        self._validate_network_args(network.type, parsed_args)

        subnet_args = ['enable_dhcp', 'dns_nameservers', 'allocation_pools',
                       'gateway_ip']
        subnet = base.flatten_args(parsed_args, subnet_args)
        if subnet:
            if subnet.get('gateway_ip') is False:
                subnet['gateway_ip'] = None

            subnets = self.app.vinfra.compute.subnets.list(
                filters={'network_id': network.id})
            if not subnets:
                raise ValidationError('Network has no subnets.')
            elif len(subnets) > 1:
                raise ValidationError("Network has more than one subnet.")

            subnet_id = subnets[0].id
            self.app.vinfra.compute.subnets.update(
                subnet_id, **subnet)

        log_subnet_deprecation_message(parsed_args)
        return network.update(
            name=parsed_args.name,
            rbac_policies=parsed_args.rbac_policies,
            mtu=parsed_args.mtu
        )


class ListSubnet(base.Lister):
    _description = "List compute networks subnets."
    _default_fields = ['id', 'network_id', 'cidr', 'enable_dhcp', 'gateway_ip',
                       'dns_nameservers', 'allocation_pools']
    _formatters = {'allocation_pools': AllocationPoolsColumn}

    def configure_parser(self, parser):
        parser.add_argument(
            '--network',
            metavar='<type>',
            required=True,
            help='Network ID or name.'
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.network:
            network = utils.find_resource(self.app.vinfra.compute.networks,
                                          parsed_args.network)
            filters['network_id'] = network.id

        networks = self.app.vinfra.compute.subnets.list(filters=filters)
        return networks


class ShowSubnet(base.ShowOne):
    _description = "Display compute network subnet details."
    _formatters = {'allocation_pools': AllocationPoolsColumn}

    def configure_parser(self, parser):
        _subnet_arg(parser)

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.subnets.get(parsed_args.subnet)


class SetSubnet(base.ShowOne):
    _description = "Modify compute network subnet parameters."

    def configure_parser(self, parser):
        _common_subnet_set_options(parser)
        _subnet_arg(parser)

    def do_action(self, parsed_args):
        subnet_args = ['enable_dhcp', 'dns_nameservers', 'allocation_pools',
                       'gateway_ip']
        subnet = base.flatten_args(parsed_args, subnet_args)
        if subnet:
            if subnet.get('gateway_ip') is False:
                subnet['gateway_ip'] = None

        gateway_ip_params = {}
        if parsed_args.gateway_ip is False:
            gateway_ip_params['gateway_ip'] = None
        elif parsed_args.gateway_ip:
            gateway_ip_params['gateway_ip'] = parsed_args.gateway_ip

        return self.app.vinfra.compute.subnets.update(
            parsed_args.subnet,
            enable_dhcp=parsed_args.enable_dhcp,
            dns_nameservers=parsed_args.dns_nameservers,
            allocation_pools=parsed_args.allocation_pools,
            **gateway_ip_params
        )


class CreateSubnet(base.ShowOne):
    _description = "Create a compute network subnet."

    def configure_parser(self, parser):
        _common_subnet_set_options(parser)
        parser.add_argument(
            "--network",
            metavar="<network>",
            required=True,
            help="Network ID or name"
        )
        parser.add_argument(
            "--cidr",
            metavar="<cidr>",
            required=True,
            help="Subnet range in CIDR notation"
        )
        # NOTE(akurbatov): suppress ipv6 RA mode while we don't support ipv6
        # for vxlan networks. And there is no use case to create a flat network
        # with internal RA management, because we agreed that adding a flat
        # network to the router as internal port is not a use case.
        # parser.add_argument(
        #     "--ipv6-ra-mode",
        #     choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
        #     help="IPv6 RA (Router Advertisement) mode, valid modes: "
        #          "[dhcpv6-stateful, dhcpv6-stateless, slaac]"
        # )
        parser.add_argument(
            "--ipv6-address-mode",
            choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
            help="IPv6 address mode, valid modes: "
                 "[dhcpv6-stateful, dhcpv6-stateless, slaac]"
        )

    @staticmethod
    def validate_args(parsed_args):
        if parsed_args.ipv6_address_mode and parsed_args.enable_dhcp is False:
            raise ValidationError("ipv6_address_mode cannot be set when "
                                  "enable_dhcp is set to False")
        try:
            cidr = netaddr.IPNetwork(parsed_args.cidr)
        except netaddr.AddrFormatError:
            raise ValidationError('Invalid CIDR %s' % parsed_args.cidr)
        else:
            if (cidr.version == 6 and cidr.prefixlen < 64 and
                    parsed_args.enable_dhcp is not False):
                raise ValidationError("IPv6 subnet prefix length must be "
                                      "at least 64 if DHCP is enabled")

    def do_action(self, parsed_args):
        # See comment above with suppressing ipv6-ra-mode
        parsed_args.ipv6_ra_mode = None
        self.validate_args(parsed_args)

        network = utils.find_resource(self.app.vinfra.compute.networks,
                                      parsed_args.network)

        gateway_ip_params = {}
        if parsed_args.gateway_ip is False:
            gateway_ip_params['gateway_ip'] = None
        elif parsed_args.gateway_ip:
            gateway_ip_params['gateway_ip'] = parsed_args.gateway_ip

        return self.app.vinfra.compute.subnets.create(
            network, parsed_args.cidr,
            enable_dhcp=parsed_args.enable_dhcp,
            dns_nameservers=parsed_args.dns_nameservers,
            allocation_pools=parsed_args.allocation_pools,
            ipv6_ra_mode=parsed_args.ipv6_ra_mode,
            ipv6_address_mode=parsed_args.ipv6_address_mode,
            **gateway_ip_params
        )


class DeleteSubnet(base.Command):
    _description = "Delete a compute network subnet."

    def configure_parser(self, parser):
        _subnet_arg(parser)

    def do_action(self, parsed_args):
        self.app.vinfra.compute.subnets.delete(parsed_args.subnet)
