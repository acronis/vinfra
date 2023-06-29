import argparse
import base64
import logging
import yaml

from vinfraclient import argtypes
from vinfraclient import compat
from vinfraclient import exceptions
from vinfraclient.cmd import base
from vinfraclient.utils import find_resource

LOG = logging.getLogger(__name__)


def _valate_members_addresses(load_balancer, members):
    try:
        address_version = compat.get_ipaddress_version(load_balancer.address)
    except ValueError as err:
        # no valid LB address? we will skip validation for that case
        LOG.warning('Invalid IP address for load balancer:: %s', err)
    else:
        for member in members:
            if address_version != compat.get_ipaddress_version(member['address']):
                raise exceptions.ValidationError(
                    'Invalid IP address "{}", only IPv{} members are allowed'
                    ''.format(member['address'], address_version))


def _parse_pools_config(config_path):
    try:
        with open(config_path, 'r') as conf_stream:
            data = yaml.safe_load(conf_stream)

            for pool in data:
                if 'certificate' in pool:
                    pool['certificate'] = _get_file_base64(pool['certificate'])
                if 'private_key' in pool:
                    pool['private_key'] = _get_file_base64(pool['private_key'])

            return data
    except Exception as err:
        raise argparse.ArgumentTypeError(
            "Failed to parse the pool configuration file:\n{!s}".format(err)
        )


def _get_file_base64(file_path):
    try:
        with open(file_path, 'r') as file_stream:
            return base64.b64encode(file_stream.read())
    except Exception as err:
        raise argparse.ArgumentTypeError(
            "Failed to read the certificate file:\n{!s}".format(err)
        )


def _load_balancer_arg(parser):
    parser.add_argument(
        "load_balancer",
        metavar="<load-balancer>",
        help="Load balancer ID or name"
    )


def _pool_arg(parser):
    parser.add_argument(
        "pool",
        metavar="<pool>",
        help="Load balancer pool ID or name"
    )


def _common_lb_args(parser):
    parser.add_argument(
        "--description",
        help="Load balancer description",
    )

    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument(
        "--enable",
        dest='enabled',
        action='store_true',
        default=None,
        help="Enable the load balancer."
    )
    enable_group.add_argument(
        "--disable",
        dest='enabled',
        action='store_false',
        default=None,
        help="Disable the load balancer."
    )


def _common_pool_args(parser, required):
    parser.add_argument(
        "--name",
        help="Pool name",
    )
    parser.add_argument(
        "--protocol",
        required=required,
        choices=["HTTP", "HTTPS", "TCP", "UDP"],
        help="The protocol for incoming connections",
    )
    parser.add_argument(
        "--port",
        required=required,
        type=int,
        help="The port for incoming connections",
    )
    parser.add_argument(
        "--algorithm",
        dest='lb_algorithm',
        required=required,
        choices=["LEAST_CONNECTIONS", "ROUND_ROBIN", "SOURCE_IP"],
        help="Load balancing algorithm",
    )
    parser.add_argument(
        "--backend-protocol",
        required=required,
        choices=["HTTP", "HTTPS", "TCP", "UDP"],
        help="The protocol for destination connections",
    )
    parser.add_argument(
        "--backend-port",
        required=required,
        type=int,
        help="The port for destination connections",
    )

    parser.add_argument(
        "--certificate-file",
        dest='certificate',
        type=_get_file_base64,
        help="An x.509 certificate file in the PEM format. Required for"
             " TLS-terminated HTTPS->HTTP load balancers.",
    )
    parser.add_argument(
        "--connection-limit",
        dest='connection_limit',
        type=int,
        help="The maximum number of connections permitted for this pool. "
             "The default value is -1 (infinite connections).",
    )
    parser.add_argument(
        "--description",
        help="Pool description",
    )
    parser.add_argument(
        "--healthmonitor",
        type=argtypes.struct(
            type=argtypes.choice(["HTTP", "HTTPS", "PING", "TCP", "UDP"]),
            url_path=str,
            delay=int,
            enabled=argtypes.boolean,
            max_retries=int,
            max_retries_down=int,
            timeout=int,
        ),
        metavar="type=<HTTP|HTTPS|PING|TCP|UDP>,"
                "[url_path=<str>,delay=<int>,enabled=<bool>,max_retries=<int>,"
                "max_retries_down=<int>,timeout=<int>]",
        help="Health monitor parameters:\n"
             "type: the health monitor type.\n"
             "url_path: the URL path to the health monitor.\n"
             "delay: the time, in seconds, between sending probes to members.\n"
             "enabled: declares whether the health monitor is enabled or not."
             " Can be 'true' or 'false'.\n"
             "max_retries: the number of successful checks required to change"
             " member status to 'HEALTHY'. Ranges from 1 to 10.\n"
             "max_retries_down: the number of unsuccessful checks required to"
             " change member status to 'UNHEALTHY'. Ranges from 1 to 10.\n"
             "timeout: the maximum time, in seconds, that a monitor waits to"
             " connect before it times out. This value must be less than the"
             " 'delay' value.",
    )
    parser.add_argument(
        "--member",
        dest='members',
        type=argtypes.struct(
            address=str,
            enabled=argtypes.boolean,
            weight=int,
        ),
        action='append',
        metavar="address=<str>,"
                "[enabled=<bool>,weight=<int>]",
        help="Member parameters:\n"
             "address: an IPv4 address of the compute server.\n"
             "enabled: declares whether the member is enabled or not."
             " Can be 'true' or 'false'.\n"
             "weight: determines the share of connections that the member"
             " services compared to the other pool members."
             " For example, a weight of 10 means that the member handles five"
             " times as many connections than a member with a weight of 2."
             " '0' means that the member does not receive new connections"
             " but continues to service existing ones."
             " Ranges from 0 to 256. The default value is 1.\n"
             "This option can be used multiple times.",
    )
    parser.add_argument(
        "--privatekey-file",
        dest='private_key',
        type=_get_file_base64,
        help="A private TLS key file in the PEM format. Required for"
             " TLS-terminated HTTPS->HTTP load balancers.",
    )

    enable_sticky_session_group = parser.add_mutually_exclusive_group()
    enable_sticky_session_group.add_argument(
        "--enable-sticky-session",
        dest='sticky_session',
        action='store_true',
        default=None,
        help="Enable session persistence."
    )
    enable_sticky_session_group.add_argument(
        "--disable-sticky-session",
        dest='sticky_session',
        action='store_false',
        default=None,
        help="Disable session persistence."
    )

    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument(
        "--enable",
        dest='enabled',
        action='store_true',
        default=None,
        help="Enable the pool."
    )
    enable_group.add_argument(
        "--disable",
        dest='enabled',
        action='store_false',
        default=None,
        help="Disable the pool."
    )


class ListLoadBalancers(base.Lister):
    _description = "List load balancers."
    _default_fields = [
        'id', 'name', 'status', 'address', 'project_id',
        'floating_ip', 'network_id',
    ]

    def do_action(self, parsed_args):
        data = self.app.vinfra.compute.load_balancers.list()
        return data


class ShowLoadBalancer(base.ShowOne):
    _description = "Display load balancer details."

    def configure_parser(self, parser):
        _load_balancer_arg(parser)

    def do_action(self, parsed_args):
        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      parsed_args.load_balancer)
        return load_balancer


class DeleteLoadBalancer(base.TaskCommand):
    _description = "Delete a load balancer."

    def configure_parser(self, parser):
        _load_balancer_arg(parser)

    def do_action(self, parsed_args):
        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      parsed_args.load_balancer)
        return load_balancer.delete_async()


class CreateLoadBalancer(base.TaskCommand):
    _description = "Create a load balancer."

    def configure_parser(self, parser):
        _common_lb_args(parser)

        parser.add_argument(
            "name",
            metavar="<name>",
            help="Load balancer name",
        )
        parser.add_argument(
            "network",
            metavar="<network>",
            help="The ID or name of network the load balancer will operate in.",
        )
        address_group = parser.add_mutually_exclusive_group()
        address_group.add_argument(
            "--address",
            help="The IP address the load balancer"
                 " will try to allocate in the network.",
        )
        address_group.add_argument(
            "--ip-version",
            type=int,
            choices=[4, 6],
            help="The IP version of the subnet the load balancer "
                 "will operate in."
        )
        parser.add_argument(
            "--floating-ip",
            help="The floating IP address that will be used to connect to"
                 " the load balancer from public networks."
        )
        parser.add_argument(
            "--pools-config",
            dest='pools',
            help="Pool configuration file",
            type=_parse_pools_config,
        )

        ha_enable_group = parser.add_mutually_exclusive_group()
        ha_enable_group.add_argument(
            "--enable-ha",
            dest='ha_enabled',
            action='store_true',
            default=None,
            help="Enable the load balancer HA."
        )
        ha_enable_group.add_argument(
            "--disable-ha",
            dest='ha_enabled',
            action='store_false',
            default=None,
            help="Disable the load balancer HA."
        )

    def do_action(self, parsed_args):
        network = find_resource(self.app.vinfra.compute.networks,
                                parsed_args.network)
        return self.app.vinfra.compute.load_balancers.create_async(
            parsed_args.name, network, address=parsed_args.address,
            description=parsed_args.description, enabled=parsed_args.enabled,
            floating_ip=parsed_args.floating_ip, pools=parsed_args.pools,
            ha_enabled=parsed_args.ha_enabled,
            ip_version=parsed_args.ip_version,
        )


class StatsLoadBalancer(base.ShowOne):
    _description = "Show statistics for a load balancer."

    def configure_parser(self, parser):
        _load_balancer_arg(parser)

    def do_action(self, parsed_args):
        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      parsed_args.load_balancer)
        return load_balancer.stats()


class RecreateLoadBalancer(base.TaskCommand):
    _description = "Recreate a load balancer."

    def configure_parser(self, parser):
        _load_balancer_arg(parser)

    def do_action(self, parsed_args):
        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      parsed_args.load_balancer)
        return load_balancer.recreate_async()


class FailoverLoadBalancer(base.TaskCommand):
    _description = "Failover a load balancer."

    def configure_parser(self, parser):
        _load_balancer_arg(parser)

    def do_action(self, parsed_args):
        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      parsed_args.load_balancer)
        return load_balancer.failover_async()


class SetLoadBalancer(base.TaskCommand):
    _description = "Modify a load balancer."

    def configure_parser(self, parser):
        _load_balancer_arg(parser)
        _common_lb_args(parser)

        parser.add_argument(
            "--name",
            help="Load balancer name",
        )

    def do_action(self, parsed_args):
        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      parsed_args.load_balancer)

        return load_balancer.update_async(
            name=parsed_args.name, description=parsed_args.description,
            enabled=parsed_args.enabled,
        )


class CreatePool(base.TaskCommand):
    _description = "Create a load balancer pool."

    def configure_parser(self, parser):
        _load_balancer_arg(parser)
        _common_pool_args(parser, True)

    def do_action(self, parsed_args):
        if parsed_args.healthmonitor:
            if 'type' not in parsed_args.healthmonitor:
                raise exceptions.ValidationError(
                    'Health monitor type is required.')
        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      parsed_args.load_balancer)

        if parsed_args.members:
            _valate_members_addresses(load_balancer, parsed_args.members)

        return self.app.vinfra.compute.load_balancer_pools.create_async(
            load_balancer, parsed_args.name, parsed_args.protocol,
            parsed_args.port, parsed_args.lb_algorithm,
            parsed_args.backend_protocol, parsed_args.backend_port,
            certificate=parsed_args.certificate,
            connection_limit=parsed_args.connection_limit,
            description=parsed_args.description, enabled=parsed_args.enabled,
            healthmonitor=parsed_args.healthmonitor,
            members=parsed_args.members, private_key=parsed_args.private_key,
            sticky_session=parsed_args.sticky_session,
        )


class ListPools(base.Lister):
    _description = "List load balancer pools."
    _default_fields = [
        'id', 'name', 'loadbalancer_id', 'protocol', 'protocol_port',
        'backend_protocol', 'backend_protocol_port', 'status', 'lb_algorithm',
        'project_id',
    ]

    def configure_parser(self, parser):
        parser.add_argument(
            "--load-balancer",
            help="Load balancer ID or name",
        )

    def do_action(self, parsed_args):
        pools = self.app.vinfra.compute.load_balancer_pools.list()

        if parsed_args.load_balancer:
            load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                          parsed_args.load_balancer)
            pools = [pool for pool in pools
                     if pool.loadbalancer_id == load_balancer.id]

        return pools


class ShowPool(base.ShowOne):
    _description = "Display load balancer pool details."

    def configure_parser(self, parser):
        _pool_arg(parser)

    def do_action(self, parsed_args):
        pool = find_resource(self.app.vinfra.compute.load_balancer_pools,
                             parsed_args.pool)
        return pool


class SetPool(base.TaskCommand):
    _description = "Modify a load balancer pool."

    def configure_parser(self, parser):
        _pool_arg(parser)
        _common_pool_args(parser, False)

    def do_action(self, parsed_args):
        pool = find_resource(self.app.vinfra.compute.load_balancer_pools,
                             parsed_args.pool)

        load_balancer = find_resource(self.app.vinfra.compute.load_balancers,
                                      pool.loadbalancer_id)
        if parsed_args.members:
            _valate_members_addresses(load_balancer, parsed_args.members)

        return pool.update(
            certificate=parsed_args.certificate,
            connection_limit=parsed_args.connection_limit,
            backend_protocol=parsed_args.backend_protocol,
            backend_port=parsed_args.backend_port,
            description=parsed_args.description, enabled=parsed_args.enabled,
            healthmonitor=parsed_args.healthmonitor,
            lb_algorithm=parsed_args.lb_algorithm, members=parsed_args.members,
            name=parsed_args.name, private_key=parsed_args.private_key,
            protocol=parsed_args.protocol, protocol_port=parsed_args.port,
            sticky_session=parsed_args.sticky_session,
        )


class DeletePool(base.Command):
    _description = "Delete a load balancer pool."

    def configure_parser(self, parser):
        _pool_arg(parser)

    def do_action(self, parsed_args):
        pool = find_resource(self.app.vinfra.compute.load_balancer_pools,
                             parsed_args.pool)
        return pool.delete()
