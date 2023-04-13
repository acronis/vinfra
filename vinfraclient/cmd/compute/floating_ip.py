from vinfraclient import utils
from vinfraclient.cmd import base


def _add_common_set_options(parser):
    parser.add_argument(
        "--port-id",
        metavar="<port-id>",
        dest="port_id",
        help="ID of the port to be associated with the floating IP"
    )
    parser.add_argument(
        "--fixed-ip-address",
        metavar="<fixed-ip-address>",
        dest="fixed_ip_address",
        help="IP address of the port (only required if the port "
             "has multiple IPs)."
    )
    parser.add_argument(
        "--description",
        metavar="description",
        dest="description",
        help="Description of the floating IP"
    )


def _add_floatingip_argument(parser):
    parser.add_argument(
        "floatingip",
        metavar="<floatingip>",
        help="ID of the floating IP"
    )


class ListFloatingIps(base.Lister):
    _description = "List floating IPs."
    _default_fields = ['id', 'fixed_ip_address', 'floating_ip_address',
                       'port_id', 'floating_network_id', 'attached_to']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of floating IPs to list. To list all '
                 'floating IPs, set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<floating-ip>',
            help='List floating IPs after the marker.'
        )
        parser.add_argument(
            '--ip-address',
            metavar='<ip-address>',
            action='filter',
            operators='contains',
            help='List floating IPs with the specified IP address or use a '
                 'filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a floating IP with the specified ID or list floating '
                 'IPs using a filter.'
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            help='List floating IPs that have the specified network name '
                 'or ID.'
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            action='filter',
            operators='in',
            help='List floating ips that belong to projects with the specified names or IDs. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            "--domain",
            metavar="<domain>",
            help='List floating ips that belong to a domain with the specified name or ID. '
                 'Can only be performed by system administrators.'
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.ip_address:
            filters['floating_ip_address'] = parsed_args.ip_address
        if parsed_args.id:
            filters['id'] = parsed_args.id
        if parsed_args.network:
            network = utils.find_resource(self.app.vinfra.compute.networks,
                                          parsed_args.network)
            filters['floating_network_id'] = network.id
        if parsed_args.project:
            manager = self.app.vinfra.compute.projects
            filters['project_id'] = utils.validate_resources_from_operator(
                manager, parsed_args.project)
        if parsed_args.domain:
            domain = utils.find_resource(self.app.vinfra.domains, parsed_args.domain)
            filters['domain_id'] = domain.id

        data = self.app.vinfra.compute.floating_ips.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)
        return data


class ShowFloatingIp(base.ShowOne):
    _description = "Display information about a floating IP."

    def configure_parser(self, parser):
        _add_floatingip_argument(parser)

    def do_action(self, parsed_args):
        flavor = utils.find_resource(self.app.vinfra.compute.floating_ips,
                                     parsed_args.floatingip)
        return flavor


class CreateFloatingIp(base.ShowOne):
    _description = "Create a floating IP."

    def configure_parser(self, parser):
        _add_common_set_options(parser)
        parser.add_argument(
            "--floating-ip-address",
            metavar="<floating-ip-address>",
            dest="floating_ip_address",
            help="Floating IP address"
        )
        parser.add_argument(
            "--network",
            metavar="<network>",
            required=True,
            help="ID or name of the network from which to allocate "
                 "the floating IP"
        )

    def do_action(self, parsed_args):
        network = utils.find_resource(self.app.vinfra.compute.networks,
                                      parsed_args.network)

        return self.app.vinfra.compute.floating_ips.create(
            network, port_id=parsed_args.port_id,
            floating_ip_address=parsed_args.floating_ip_address,
            fixed_ip_address=parsed_args.fixed_ip_address,
            description=parsed_args.description)


class DeleteFloatingIp(base.Command):
    _description = "Delete a floating IP."

    def configure_parser(self, parser):
        _add_floatingip_argument(parser)

    def do_action(self, parsed_args):
        floating_ip = utils.find_resource(self.app.vinfra.compute.floating_ips,
                                          parsed_args.floatingip)
        return floating_ip.delete()


class SetFloatingIp(base.ShowOne):
    _description = "Modify a floating IP."

    def configure_parser(self, parser):
        _add_common_set_options(parser)
        _add_floatingip_argument(parser)

    def do_action(self, parsed_args):
        fip = utils.find_resource(self.app.vinfra.compute.floating_ips,
                                  parsed_args.floatingip)

        return fip.update(port_id=parsed_args.port_id,
                          fixed_ip_address=parsed_args.fixed_ip_address,
                          description=parsed_args.description)
