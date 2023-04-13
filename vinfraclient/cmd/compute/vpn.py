import argparse

from vinfraclient.cmd import base
from vinfraclient import utils


class InlineParser(argparse.ArgumentParser):
    def __init__(self):
        super(InlineParser, self).__init__(add_help=False)

    def error(self, message):
        message = message.replace('--', '')
        raise argparse.ArgumentTypeError(message)

    def parse_value(self, value):
        args = ['--{}'.format(arg) for arg in value.split(',')]
        return self.parse_args(args)

    def format_help(self):
        parts = []
        for action in self._optionals._group_actions:  # pylint: disable=protected-access
            if action.metavar is not None:
                value = action.metavar
            elif action.choices is not None:
                choice_strs = [str(choice) for choice in action.choices]
                value = '{%s}' % ','.join(choice_strs)
            else:
                value = '<{}>'.format(action.dest)

            key = action.option_strings[0].lstrip('-')
            item = '{}={}'.format(key, value)
            if action.help:
                item = '{}: {}'.format(item, action.help)
            parts.append(item)
        return ';\n'.join(parts)


class PolicyInlineParser(InlineParser):
    def __init__(self, pname):
        super(PolicyInlineParser, self).__init__()
        id_name_group = self.add_mutually_exclusive_group(required=True)
        id_name_group.add_argument(
            '--id',
            help='{} policy ID or name'.format(pname),
        )
        id_name_group.add_argument(
            '--name',
            help='{} policy name'.format(pname),
        )
        self.add_argument(
            '--auth-algorithm',
            choices=['sha1', 'sha256', 'sha384', 'sha512'],
            help='{} policy authentication algorithm'.format(pname),
        )
        self.add_argument(
            '--encryption-algorithm',
            choices=['aes-128', '3des', 'aes-192', 'aes-256'],
            help='{} policy encryption algorithm'.format(pname),
        )
        self.add_argument(
            '--pfs',
            choices=['group5', 'group2', 'group14'],
            help='{} Diffie-Hellman group'.format(pname),
        )
        self.add_argument(
            '--lifetime',
            metavar='<seconds>',
            type=self._lifetime,
            help='{} policy lifetime'.format(pname),
        )

    @staticmethod
    def _lifetime(value):
        try:
            value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                'invalid value: {!r}'.format(value))
        return {'value': value}

    def parse_value(self, value):
        if not '=' in value:
            value = 'id={}'.format(value)
        return super(PolicyInlineParser, self).parse_value(value)


class EndpointGroupInlineParser(InlineParser):
    def __init__(self, gtype='local'):
        super(EndpointGroupInlineParser, self).__init__()
        gname = {
            'local': 'local endpoint group',
            'peer': 'remote endpoint group'
        }[gtype]
        id_name_group = self.add_mutually_exclusive_group(required=True)
        id_name_group.add_argument(
            '--id',
            help='{} ID or name'.format(gname),
        )
        id_name_group.add_argument(
            '--name',
            help='{} name'.format(gname),
        )
        if gtype == 'local':
            self.add_argument(
                '--value',
                metavar='<subnet>',
                dest='endpoints',
                action='append',
                help='subnet ID (option can be repeated).',
            )
        else:
            self.add_argument(
                '--value',
                metavar='<cidr>',
                dest='endpoints',
                action='append',
                help='IP range in CIDR notation (option can be repeated).',
            )

    def parse_value(self, value):
        if not '=' in value:
            value = 'id={}'.format(value)
        parsed_args = super(EndpointGroupInlineParser, self).parse_value(value)
        if parsed_args.name and not parsed_args.endpoints:
            raise argparse.ArgumentTypeError(
                "The 'value' option is required when "
                "the 'name' option is specified")
        return parsed_args


class DpdInlineParser(InlineParser):
    def __init__(self):
        super(DpdInlineParser, self).__init__()
        self.add_argument(
            '--action',
            choices=['hold', 'clear', 'disabled', 'restart'],
            help='defines the action to take if the remote peer unexpectedly '
                 'closes',
        )
        self.add_argument(
            '--interval',
            metavar="<seconds>",
            type=int,
            help='defines the time interval with which messages '
                 'are sent to the peer',
        )
        self.add_argument(
            '--timeout',
            metavar="<seconds>",
            type=int,
            help='defines the timeout interval, after which connection to a '
                 'peer is considered down.',
        )


class CreateUpdateMixin(object):
    @staticmethod
    def _add_mixin_arguments(parser, action='create'):
        parser.add_argument(
            "--peer-id",
            metavar="<peer-id>",
            help="Peer router identifier for authentication",
        )
        parser.add_argument(
            "--local-id",
            metavar="<local-id>",
            help="Local router identifier for authentication",
        )
        parser.add_argument(
            "--initiator",
            choices=['bi-directional', 'response-only'],
            help=argparse.SUPPRESS,
            # help="Initiator state",
        )
        dpd_inline_parser = DpdInlineParser()
        parser.add_argument(
            "--dpd",
            metavar="action=<action>,interval=<seconds>,timeout=<seconds>",
            type=dpd_inline_parser.parse_value,
            help=("Dead Peer Detection attributes:\n" +
                  dpd_inline_parser.format_help())
        )

        is_create = (action == 'create')
        parser.add_argument(
            "--peer-address",
            metavar="<peer-address>",
            required=is_create,
            help="Peer gateway public IPv4/IPv6 address or FQDN",
        )
        parser.add_argument(
            "--psk",
            metavar="<psk>",
            required=is_create,
            help="Pre-shared key string",
        )
        # local endpoint group:
        local_endpoint_group_parser = EndpointGroupInlineParser(gtype='local')
        parser.add_argument(
            "--local-endpoint-group",
            metavar="<id|name=<name>,value=<subnet>,...>",
            type=local_endpoint_group_parser.parse_value,
            required=is_create,
            help=('Local endpoint group parameters:\n' +
                  local_endpoint_group_parser.format_help())
        )
        # peer endpoint group:
        peer_endpoint_group_parser = EndpointGroupInlineParser(gtype='peer')
        parser.add_argument(
            "--peer-endpoint-group",
            metavar="<id|name=<name>,value=<cidr>,...>",
            type=peer_endpoint_group_parser.parse_value,
            required=is_create,
            help=("Remote endpoint group parameters:\n" +
                  peer_endpoint_group_parser.format_help())
        )


class CreateIPsecSiteConnection(base.ShowOne, CreateUpdateMixin):
    _description = "Create a compute VPN connection."

    def configure_parser(self, parser):
        self._add_mixin_arguments(parser, action='create')
        ikepolicy_inline_parser = PolicyInlineParser('IKE')
        ikepolicy_inline_parser.add_argument(
            '--ike-version',
            choices=['v1', 'v2'],
            help='IKE version',
        )
        parser.add_argument(
            "--ikepolicy",
            metavar=('<id|name=<name>[,auth-algorithm=<algorithm>,'
                     'encryption-algorithm=<algorithm>,' 'pfs=<pfs>,'
                     'lifetime=<seconds>,ike-version=<ver>]>'),
            type=ikepolicy_inline_parser.parse_value,
            required=True,
            help=("IKE policy parameters:\n" +
                  ikepolicy_inline_parser.format_help())
        )
        ipsecpolicy_inline_parser = PolicyInlineParser('IPsec')
        parser.add_argument(
            "--ipsecpolicy",
            metavar=('<id|name=<name>[,auth-algorithm=<algorithm>,'
                     'encryption-algorithm=<algorithm>,pfs=<pfs>,'
                     'lifetime=<seconds>]>'),
            type=ipsecpolicy_inline_parser.parse_value,
            required=True,
            help=("IPsec policy parameters:\n" +
                  ipsecpolicy_inline_parser.format_help())
        )
        parser.add_argument(
            "--router",
            metavar="<router>",
            required=True,
            help="Router ID or name",
        )
        parser.add_argument(
            "name",
            metavar="<connection-name>",
            help="Name of the VPN connection",
        )

    def do_action(self, parsed_args):
        router = utils.find_resource(self.app.vinfra.compute.routers,
                                     parsed_args.router)

        params = {}
        vpnservice = {'router_id': router.id}
        ipsec_site_connection = {
            'name': parsed_args.name,
            'peer_address': parsed_args.peer_address,
            'psk': parsed_args.psk,
        }
        options_args = base.flatten_args(parsed_args,
                                         ['peer_id', 'local_id', 'initiator'])
        if parsed_args.dpd:
            options_args['dpd'] = base.flatten_args(parsed_args.dpd,
                                                    parsed_args.dpd.__dict__)
        ipsec_site_connection.update(options_args)

        ikepolicy_ns = parsed_args.ikepolicy
        if ikepolicy_ns.id:
            obj = utils.find_resource(
                self.app.vinfra.compute.vpn.ikepolicies, ikepolicy_ns.id)
            ipsec_site_connection['ikepolicy_id'] = obj.id
        else:
            params['ikepolicy'] = base.flatten_args(
                ikepolicy_ns, ikepolicy_ns.__dict__.keys())

        ipsecpolicy_ns = parsed_args.ipsecpolicy
        if ipsecpolicy_ns.id:
            obj = utils.find_resource(
                self.app.vinfra.compute.vpn.ipsecpolicies, ipsecpolicy_ns.id)
            ipsec_site_connection['ipsecpolicy_id'] = obj.id
        else:
            params['ipsecpolicy'] = base.flatten_args(
                ipsecpolicy_ns, ipsecpolicy_ns.__dict__.keys())

        local_ep_ns = parsed_args.local_endpoint_group
        if local_ep_ns.id:
            obj = utils.find_resource(
                self.app.vinfra.compute.vpn.endpoint_groups, local_ep_ns.id)
            ipsec_site_connection['local_ep_group_id'] = obj.id
        else:
            params['local_ep_group'] = local_ep_ns.__dict__
            params['local_ep_group']['type'] = 'subnet'

        peer_ep_ns = parsed_args.peer_endpoint_group
        if peer_ep_ns.id:
            obj = utils.find_resource(
                self.app.vinfra.compute.vpn.endpoint_groups, peer_ep_ns.id)
            ipsec_site_connection['peer_ep_group_id'] = obj.id
        else:
            params['peer_ep_group'] = peer_ep_ns.__dict__
            params['peer_ep_group']['type'] = 'cidr'

        return self.app.vinfra.compute.vpn.ipsec_site_connections.create(
            vpnservice, ipsec_site_connection, **params)


class SetIPsecSiteConnection(base.ShowOne, CreateUpdateMixin):
    _description = "Modify a compute VPN connection."

    def configure_parser(self, parser):
        self._add_mixin_arguments(parser, action='update')
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the VPN connection",
        )
        parser.add_argument(
            "ipsec_site_connection",
            metavar="<connection>",
            help="VPN connection name or ID",
        )

    def do_action(self, parsed_args):
        ipsec_site_connection = utils.find_resource(
            self.app.vinfra.compute.vpn.ipsec_site_connections,
            parsed_args.ipsec_site_connection)

        new_ipsec_site_connection = base.flatten_args(
            parsed_args,
            ['name', 'peer_address', 'peer_id', 'local_id', 'initiator', 'psk'])
        if parsed_args.dpd:
            new_ipsec_site_connection['dpd'] = (
                base.flatten_args(parsed_args.dpd, parsed_args.dpd.__dict__))

        params = {}
        local_ep_ns = parsed_args.local_endpoint_group
        if local_ep_ns and local_ep_ns.id:
            obj = utils.find_resource(
                self.app.vinfra.compute.vpn.endpoint_groups, local_ep_ns.id)
            new_ipsec_site_connection['local_ep_group_id'] = obj.id
        elif local_ep_ns:
            params['local_ep_group'] = local_ep_ns.__dict__
            params['local_ep_group']['type'] = 'subnet'

        peer_ep_group_ns = parsed_args.peer_endpoint_group
        if peer_ep_group_ns and peer_ep_group_ns.id:
            obj = utils.find_resource(
                self.app.vinfra.compute.vpn.endpoint_groups,
                peer_ep_group_ns.id)
            new_ipsec_site_connection['local_ep_group_id'] = obj.id
        elif peer_ep_group_ns:
            params['peer_ep_group'] = peer_ep_group_ns.__dict__
            params['peer_ep_group']['type'] = 'cidr'

        return ipsec_site_connection.update(
            new_ipsec_site_connection, **params)


class ListIPsecSiteConnection(base.Lister):
    _description = "List compute VPN connections."
    _default_fields = ['id', 'name', 'status', 'peer_address']

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.vpn.ipsec_site_connections.list()


class DeleteIPsecSiteConnection(base.Command):
    _description = "Delete a compute VPN connection."

    def configure_parser(self, parser):
        parser.add_argument(
            "ipsec_site_connection",
            metavar="<connection>",
            help="VPN connection name or ID",
        )

    def do_action(self, parsed_args):
        ipsec_site_connection = utils.find_resource(
            self.app.vinfra.compute.vpn.ipsec_site_connections,
            parsed_args.ipsec_site_connection)
        ipsec_site_connection.delete()


class RestartIPsecSiteConnection(base.ShowOne):
    _description = "Reset a compute VPN connection."

    def configure_parser(self, parser):
        parser.add_argument(
            "ipsec_site_connection",
            metavar="<connection>",
            help="VPN connection name or ID",
        )

    def do_action(self, parsed_args):
        ipsec_site_connection = utils.find_resource(
            self.app.vinfra.compute.vpn.ipsec_site_connections,
            parsed_args.ipsec_site_connection)
        return ipsec_site_connection.restart()


class ShowIPsecSiteConnection(base.ShowOne):
    _description = "Display compute VPN connection details."

    def configure_parser(self, parser):
        parser.add_argument(
            "ipsec_site_connection",
            metavar="<connection>",
            help="VPN connection ID or name"
        )

    def do_action(self, parsed_args):
        ipsec_site_connection = utils.find_resource(
            self.app.vinfra.compute.vpn.ipsec_site_connections,
            parsed_args.ipsec_site_connection)
        vpnservice = self.app.vinfra.compute.vpn.vpnservices.get(
            ipsec_site_connection.vpnservice_id)

        ipsec_site_connection = ipsec_site_connection.to_dict()
        ipsec_site_connection['router_id'] = vpnservice.router_id
        return ipsec_site_connection


class ListIkePolicy(base.Lister):
    _description = "List compute VPN IKE policies."
    _default_fields = ['id', 'name', 'auth_algorithm', 'encryption_algorithm',
                       'pfs', 'ike_version']

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.vpn.ikepolicies.list()


class ShowIkePolicy(base.ShowOne):
    _description = "Display compute VPN IKE policy details."

    def configure_parser(self, parser):
        parser.add_argument(
            "ikepolicy",
            metavar="<ike-policy>",
            help="IKE policy ID or name"
        )

    def do_action(self, parsed_args):
        return utils.find_resource(
            self.app.vinfra.compute.vpn.ikepolicies, parsed_args.ikepolicy)


class ListIPsecPolicy(base.Lister):
    _description = "List compute VPN IPsec policies."
    _default_fields = ['id', 'name', 'auth_algorithm', 'encryption_algorithm',
                       'pfs']

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.vpn.ipsecpolicies.list()


class ShowIPsecPolicy(base.ShowOne):
    _description = "Display compute VPN IPsec policy details."

    def configure_parser(self, parser):
        parser.add_argument(
            "ipsecpolicy",
            metavar="<ipsec-policy>",
            help="IPsec policy ID or name"
        )

    def do_action(self, parsed_args):
        return utils.find_resource(
            self.app.vinfra.compute.vpn.ipsecpolicies, parsed_args.ipsecpolicy)


class ListEndpointGroup(base.Lister):
    _description = "List compute VPN endpoint groups."
    _default_fields = ['id', 'name', 'type', 'endpoints']

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.vpn.endpoint_groups.list()


class ShowEndpointGroup(base.ShowOne):
    _description = "Display compute VPN endpoint group details."

    def configure_parser(self, parser):
        parser.add_argument(
            "endpoint_group",
            metavar="<endpoint-group>",
            help="Endpoint group ID or name"
        )

    def do_action(self, parsed_args):
        return utils.find_resource(
            self.app.vinfra.compute.vpn.endpoint_groups,
            parsed_args.endpoint_group)
