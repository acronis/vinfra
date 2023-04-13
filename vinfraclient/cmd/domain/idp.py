from datetime import datetime
import json

from vinfraclient import exceptions
from vinfraclient.cmd.base import Command, Lister, ShowOne
from vinfraclient.compat import parse_qs, urlparse
from vinfraclient.utils import find_resource, get_json


def _add_domain_option(parser):
    parser.add_argument(
        "--domain",
        metavar="<domain>",
        required=True,
        help="Domain name or ID",
    )


def _add_idp_arg(parser):
    parser.add_argument(
        "idp",
        metavar="<idp>",
        help="Identity provider name or ID",
    )


def _add_idp_main(parser, required=True):
    parser.add_argument(
        "--issuer",
        required=required,
        metavar="<issuer>",
        help="Identity provider issuer",
    )
    parser.add_argument(
        "--scope",
        required=required,
        metavar="<issuer>",
        help="Scope that define what user identity data will be shared by "
             "the identity provider during authentication",
    )


def _add_idp_optional(parser):
    parser.add_argument(
        "--response-type",
        metavar="<response-type>",
        choices=['code', 'id_token'],
        default='id_token',
        help="Response type to be used in authorization flow",
    )
    parser.add_argument(
        "--metadata-url",
        metavar="<metadata-url>",
        help="Metadata URL of the identity provider's dicovery endpoint",
    )
    parser.add_argument(
        "--client-id",
        metavar="<client-id>",
        help="Client ID to access the identity provider",
    )
    parser.add_argument(
        "--client-secret",
        metavar="<client-secret>",
        help="Client secret to access the identity provider",
    )
    parser.add_argument(
        "--mapping",
        metavar="<path>",
        type=get_json,
        default=None,
        help="Path to the mapping configuration file."
    )
    parser.add_argument(
        "--enable",
        dest="enabled",
        action="store_true",
        default=None,
        help="Enable identity provider",
    )
    parser.add_argument(
        "--disable",
        dest="enabled",
        action='store_false',
        default=None,
        help="Disable identity provider",
    )


class ListDomainIdPs(Lister):
    _description = "List domain identity providers."
    _default_fields = ['id', 'name', 'issuer', 'scope', 'domain_id']

    def configure_parser(self, parser):
        _add_domain_option(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        return domain.idps_manager.list()


class ShowDomainIdP(ShowOne):
    _description = "Show details of a domain identity provider."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_idp_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        idp = find_resource(domain.idps_manager, parsed_args.idp)
        return idp


class CreateDomainIdP(ShowOne):
    _description = "Create a new domain identity provider."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_idp_main(parser)
        _add_idp_optional(parser)
        parser.add_argument(
            "name",
            help="Identity provider name",
        )

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        return domain.idps_manager.create(
            parsed_args.name,
            parsed_args.issuer,
            parsed_args.scope,
            response_type=parsed_args.response_type,
            metadata_url=parsed_args.metadata_url,
            client_id=parsed_args.client_id,
            client_secret=parsed_args.client_secret,
            mapping=parsed_args.mapping,
            enabled=parsed_args.enabled,
        )


class DeleteDomainIdP(Command):
    _description = "Delete a domain identity provider."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_idp_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        idp = find_resource(domain.idps_manager, parsed_args.idp)
        return domain.idps_manager.delete(idp)


class SetDomainIdP(ShowOne):
    _description = "Modify an existing domain identity provider."

    def configure_parser(self, parser):
        _add_idp_main(parser, required=False)
        _add_idp_optional(parser)
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the identity provider",
        )
        _add_domain_option(parser)
        _add_idp_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        idp = find_resource(domain.idps_manager, parsed_args.idp)
        return idp.update(
            name=parsed_args.name,
            issuer=parsed_args.issuer,
            scope=parsed_args.scope,
            response_type=parsed_args.response_type,
            metadata_url=parsed_args.metadata_url,
            client_id=parsed_args.client_id,
            client_secret=parsed_args.client_secret,
            mapping=parsed_args.mapping,
            enabled=parsed_args.enabled,
        )


class LoginDomainIdP(Command):
    _description = "Sign in using Identity provider private key."
    auth_required = False

    def configure_parser(self, parser):
        parser.add_argument(
            "--issuer",
            required=True,
            metavar="<issuer>",
            help="Identity provider issuer",
        )
        parser.add_argument(
            "--private-key",
            metavar="<path>",
            required=True,
            help="Private key file in X.509 PEM Format",
        )
        parser.add_argument(
            "--kid",
            metavar="<kid>",
            required=True,
            help="Key ID in Identity provider JWKSet",
        )
        parser.add_argument(
            "--user-data",
            metavar="<json>",
            required=True,
            help="User data in JSON format",
        )
        parser.add_argument(
            "idp",
            metavar="<idp>",
            help="Identity provider ID",
        )

    def do_action(self, parsed_args):
        try:
            # the command is for testing purposes only
            # we don't want to extend vinfra dependencies
            # thus this imports are not in global scope
            from cryptography.hazmat.primitives import serialization  # pylint: disable=import-error
            from cryptography.hazmat.backends import default_backend  # pylint: disable=import-error
            import jwt  # pylint: disable=import-error
        except Exception as err:
            raise exceptions.VinfraError('Import exception: {}'.format(err))

        query_params = {}
        if self.app.options.domain:
            query_params['domain'] = self.app.options.domain

        idps = self.app.vinfra.client.get(
            'login/', query_params=query_params,
            authenticated=False).get('idps', [])
        idp = next((x for x in idps if x['id'] == parsed_args.idp), None)
        if not idp:
            raise exceptions.VinfraError("Identity Provider is not found")

        resp = self.app.vinfra.session.get(
            idp['url'], authenticated=False, allow_redirects=False)
        try:
            params = parse_qs(urlparse(resp.headers['Location']).query)
            state = params['state'][0]
            nonce = params['nonce'][0]
            client_id = params['client_id'][0]
        except Exception as err:
            raise exceptions.VinfraError(
                'Unable to parse redirect to identity provider: {}'.format(err))

        try:
            with open(parsed_args.private_key, 'rb') as private_key_file:
                private_key = serialization.load_pem_private_key(
                    private_key_file.read(),
                    password=None, backend=default_backend())
        except Exception as err:
            raise exceptions.VinfraError(
                'Unable to load private key: {}'.format(err))

        timestamp = \
            int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

        # minimal openid connect token
        token = {
            'aud': client_id,
            'exp': timestamp,
            'iat': timestamp,
            'iss': parsed_args.issuer,
            'nonce': nonce,
            'sub': 'sub',
        }
        try:
            token.update(json.loads(parsed_args.user_data))
        except Exception as err:
            raise exceptions.VinfraError(
                'Unable to parse user data: {}'.format(err))

        id_token = jwt.encode(
            token, private_key, algorithm="RS256",
            headers={"kid":  parsed_args.kid})

        resp = self.app.vinfra.client.send_request_raw(
            'post', '/login/idp/', allow_redirects=False, authenticated=False,
            data={'id_token': id_token, 'state': state})

        if resp.status_code != 302 or \
                'success' not in resp.headers['Location']:
            raise exceptions.VinfraError('Login failed')

        self.app.save_session()
