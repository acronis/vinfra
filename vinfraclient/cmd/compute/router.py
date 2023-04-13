import argparse

from vinfra.consts import missing

from vinfraclient import exceptions
from vinfraclient import utils
from vinfraclient.argtypes import parse_dict_options
from vinfraclient.cmd import base


def parse_internal_interface(value):
    if '=' not in value:
        return {'network_id': value}

    iface_dict = parse_dict_options(value)
    mapping = {
        'network': 'network_id',
        'ip-addr': 'ip_address',
    }

    if not iface_dict.get('network'):
        raise argparse.ArgumentTypeError("network is required")

    iface = {}
    for key, val in iface_dict.items():
        if key not in mapping:
            raise argparse.ArgumentTypeError(
                "unrecognized argument: {}".format(key))
        iface[mapping[key]] = val

    return iface


def _common_set_options(parser, router_update=True):
    if router_update:
        ext_gw_group = parser.add_mutually_exclusive_group()
        ext_gw_group.add_argument(
            "--external-gateway",
            metavar="<network>",
            default=missing,
            help="External network used as router's gateway (name or ID)."
        )
        ext_gw_group.add_argument(
            "--no-external-gateway",
            dest="external_gateway",
            action="store_const",
            const=None,
            default=missing,
            help="Remove external gateway from the router."
        )
    else:
        parser.add_argument(
            "--external-gateway",
            metavar="<network>",
            help="External network used as router's gateway (name or ID)."
        )
    snat_group = parser.add_mutually_exclusive_group()
    snat_group.add_argument(
        "--enable-snat",
        action="store_true",
        default=None,
        help="Enable source NAT on external gateway."
    )
    snat_group.add_argument(
        "--disable-snat",
        dest='enable_snat',
        action="store_false",
        default=None,
        help="Disable source NAT on external gateway."
    )
    parser.add_argument(
        "--fixed-ip",
        metavar="<fixid-ip>",
        default=None,
        help="Desired IP on external gateway."
    )


def _common_set_options_validate(app, parsed_args):
    if (not parsed_args.external_gateway or
            parsed_args.external_gateway is missing):
        if parsed_args.enable_snat is not None:
            raise exceptions.ValidationError(
                "--enable/--disable-snat requires --external-gateway option")
        if parsed_args.fixed_ip:
            raise exceptions.ValidationError(
                "--fixed-ip requires --external-gateway option")
        return parsed_args.external_gateway

    ex_gw_info = {}
    network = utils.find_resource(app.vinfra.compute.networks,
                                  parsed_args.external_gateway)
    ex_gw_info['network_id'] = network.id

    if parsed_args.enable_snat is not None:
        ex_gw_info['enable_snat'] = parsed_args.enable_snat
    if parsed_args.fixed_ip:
        ip_addr = {'ip_address': parsed_args.fixed_ip}
        ex_gw_info['external_fixed_ips'] = [ip_addr]

    return ex_gw_info


class ListRouters(base.Lister):
    _description = "List virtual routers."
    _default_fields = ['id', 'external_gateway_info', 'name', 'routes',
                       'project_id', 'status']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of routers to list. To list all routers, '
                 'set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<router>',
            help='List routers after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List routers with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a router with the specified ID or list routers using '
                 'a filter.'
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            action='filter',
            operators='in',
            help='List routers that belong to projects with the specified names or IDs. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            "--domain",
            metavar="<domain>",
            help='List routers that belong to a domain with the specified name or ID. '
                 'Can only be performed by system administrators.'
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

        data = self.app.vinfra.compute.routers.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)
        return data


class ShowRouter(base.ShowOne):
    _description = "Display information about a virtual router."

    def configure_parser(self, parser):
        parser.add_argument(
            "router",
            metavar="<router>",
            help="Virtual router ID"
        )

    def do_action(self, parsed_args):
        router = utils.find_resource(self.app.vinfra.compute.routers,
                                     parsed_args.router)
        return router


class CreateRouter(base.ShowOne):
    _description = "Create a virtual router."

    def configure_parser(self, parser):
        _common_set_options(parser, router_update=False)

        parser.add_argument(
            "--internal-interface",
            metavar="<network=network,ip-addr=ip-addr>|<network>",
            dest="internal_interfaces",
            type=parse_internal_interface,
            action='append',
            help="Specify router interface. This option can be used multiple "
                 "times"
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Name of the router"
        )

    def do_action(self, parsed_args):
        ex_gw_info = _common_set_options_validate(self.app, parsed_args)

        if parsed_args.internal_interfaces:
            for iface in parsed_args.internal_interfaces:
                network = utils.find_resource(
                    self.app.vinfra.compute.networks, iface['network_id'])
                iface['network_id'] = network.id

        return self.app.vinfra.compute.routers.create(
            parsed_args.name, external_gateway_info=ex_gw_info,
            internal_interfaces=parsed_args.internal_interfaces)


class DeleteRouter(base.Command):
    _description = "Delete a virtual router."

    def configure_parser(self, parser):
        parser.add_argument(
            "router",
            metavar="<router>",
            help="Virtual router name or ID"
        )

    def do_action(self, parsed_args):
        router = utils.find_resource(self.app.vinfra.compute.routers,
                                     parsed_args.router)
        return router.delete()


class SetRouter(base.ShowOne):
    _description = "Modify a virtual router."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            help="Router name"
        )
        _common_set_options(parser, router_update=True)
        route_group = parser.add_mutually_exclusive_group()
        route_group.add_argument(
            "--route",
            type=parse_dict_options,
            metavar="<destination=destination,nexthop=nexthop>",
            action="append",
            dest="routes",
            help="Routes. This option can be used multiple times."
        )
        route_group.add_argument(
            "--no-route",
            dest='routes',
            action='store_const',
            const=[],
            help="Clear routes associated with the router."
        )
        parser.add_argument(
            "router",
            metavar="<router>",
            help="Virtual router name or ID"
        )

    def do_action(self, parsed_args):
        router = utils.find_resource(self.app.vinfra.compute.routers,
                                     parsed_args.router)
        ex_gw_info = _common_set_options_validate(self.app, parsed_args)

        return router.update(name=parsed_args.name,
                             external_gateway_info=ex_gw_info,
                             routes=parsed_args.routes)


_router_iface_lister_default_fields = [
    'network_id', 'is_external', 'ip_addresses', 'status',
]


class RouterInterfaceAdd(base.Lister):
    _description = "Add an interface to a virtual router."
    _default_fields = _router_iface_lister_default_fields

    def configure_parser(self, parser):
        parser.add_argument(
            "--ip-address",
            metavar="<ip-address>",
            help="IP address"
        )
        parser.add_argument(
            "--interface",
            metavar="<network>",
            help="Network name or ID",
            required=True,
        )
        parser.add_argument(
            "router",
            help="Virtual router name or ID",
        )

    def do_action(self, parsed_args):
        router = utils.find_resource(self.app.vinfra.compute.routers,
                                     parsed_args.router)
        network = utils.find_resource(self.app.vinfra.compute.networks,
                                      parsed_args.interface)

        return router.interfaces.add(network,
                                     ip_address=parsed_args.ip_address)


class RouterInterfaceRemove(base.Lister):
    _description = "Remove an interface from a virtual router."
    _default_fields = _router_iface_lister_default_fields

    def configure_parser(self, parser):
        parser.add_argument(
            "--interface",
            metavar="<network>",
            required=True,
            help="Network name or ID",
        )
        parser.add_argument(
            "router",
            help="Virtual router name or ID",
        )

    def do_action(self, parsed_args):
        router = utils.find_resource(self.app.vinfra.compute.routers,
                                     parsed_args.router)
        network = utils.find_resource(self.app.vinfra.compute.networks,
                                      parsed_args.interface)

        return router.interfaces.remove(network)


class RouterInterfaceList(base.Lister):
    _description = "List router interfaces."
    _default_fields = _router_iface_lister_default_fields

    def configure_parser(self, parser):
        parser.add_argument(
            "router",
            help="Virtual router name or ID",
        )

    def do_action(self, parsed_args):
        router = utils.find_resource(self.app.vinfra.compute.routers,
                                     parsed_args.router)
        ifaces = router.interfaces.list()

        # Note(akurbatov): extend the output with network name to make it a
        # little bit user friendly
        with_name = parsed_args.formatter == 'table'
        if with_name:
            networks = self.app.vinfra.compute.networks.list()
            networks_by_id = dict((net.id, net) for net in networks)

            for iface in ifaces:
                network_name = networks_by_id[iface.network_id].name
                network = '{} ({})'.format(iface.network_id, network_name)
                iface.set_info({'network_id': network})

        return ifaces
