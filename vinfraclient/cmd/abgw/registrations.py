import textwrap

from vinfraclient.cmd.abgw import get_reg_password, ensure_abgw_exists
from vinfraclient.cmd.base import TaskCommand, Lister, ShowOne

from vinfraclient.utils import find_resource, get_cluster, get_stream


class CreateAbgwRegistration(TaskCommand):

    _description = "Create a backup storage registration."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            required=True,
            help="Registration name."
        )
        parser.add_argument(
            "--address",
            metavar="<address>",
            required=True,
            help="Registration IP address."
        )
        parser.add_argument(
            "--account-server",
            required=True,
            help=(
                "URL of the cloud management portal or the hostname/IP "
                "address and port of the local management server."
            )
        )
        parser.add_argument(
            "--username",
            required=True,
            help=(
                "Partner account in the cloud or of an organization "
                "administrator on the local management server."
            )
        )
        parser.add_argument(
            "--stdin",
            action="store_true",
            help="Use for setting registration password from stdin"
        )
        parser.add_argument(
            "--location",
            metavar="<location>",
            help="Registration location."
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.registrations.create_async(
            name=parsed_args.name,
            address=parsed_args.address,
            account_server=parsed_args.account_server,
            username=parsed_args.username,
            password=get_reg_password(parsed_args),
            location=parsed_args.location,
        )


class ListAbgwRegistration(Lister):

    _description = "List backup storage registrations."
    _default_fields = [
        'id', 'name', 'address', 'type'
    ]

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.registrations.list()


class ShowAbgwRegistration(ShowOne):

    _description = "Display backup storage registration details."

    def configure_parser(self, parser):
        parser.add_argument(
            "registration",
            metavar="<registration>",
            help="Registration ID or name",
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return find_resource(
            cluster.abgw.registrations, parsed_args.registration)


class DeleteAbgwRegistration(TaskCommand):

    _description = "Delete a backup storage registration."

    def configure_parser(self, parser):
        parser.add_argument(
            "registration",
            metavar="<registration>",
            help="Registration ID or name",
        )
        parser.add_argument(
            "--username",
            required=False,
            help=(
                "Partner account in the cloud or of an organization "
                "administrator on the local management server."
            )
        )
        parser.add_argument(
            "--stdin",
            action="store_true",
            help="Use for setting registration password from stdin"
        )
        parser.add_argument(
            "--force", action="store_true", required=False,
            default=False
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        registration = find_resource(
            cluster.abgw.registrations,
            parsed_args.registration
        )
        kwargs = {}
        if parsed_args.username:
            kwargs['username'] = parsed_args.username
            kwargs['password'] = get_reg_password(parsed_args)
        if parsed_args.force:
            kwargs['force'] = parsed_args.force
        return registration.delete(**kwargs)


class UpdateAbgwRegistration(TaskCommand):

    _description = "Update a backup storage registration."

    def configure_parser(self, parser):
        parser.add_argument(
            "registration",
            metavar="<registration>",
            help="Registration ID or name.",
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the registration."
        )
        parser.add_argument(
            "--address",
            metavar="<address>",
            help="Registration IP address."
        )
        parser.add_argument(
            "--username",
            help=(
                "Partner account in the cloud or of an organization "
                "administrator on the local management server."
            )
        )
        parser.add_argument(
            "--stdin",
            action="store_true",
            help="Use for setting registration password from stdin"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        registration = find_resource(
            cluster.abgw.registrations,
            parsed_args.registration
        )
        kwargs = dict(
            name=parsed_args.name,
            address=parsed_args.address,
            username=parsed_args.username,
        )
        if parsed_args.username:
            kwargs['password'] = get_reg_password(parsed_args)
        return registration.update(**kwargs)


class RenewAbgwRegistration(TaskCommand):

    _description = textwrap.dedent("""\
    Update certificates for a backup storage registration.

    Please note that ABGW service will be restarted as a part of certificates update procedure.
    """)

    def configure_parser(self, parser):
        parser.add_argument(
            "registration",
            metavar="<registration>",
            help="Registration ID or name.",
        )
        parser.add_argument(
            "--username",
            required=True,
            help=(
                "Partner account in the cloud or of an organization "
                "administrator on the local management server."
            )
        )
        parser.add_argument(
            "--stdin",
            action="store_true",
            help="Use for setting registration password from stdin"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        registration = find_resource(
            cluster.abgw.registrations,
            parsed_args.registration
        )
        return cluster.abgw.registrations.renew_certificates(
            registration=registration,
            username=parsed_args.username,
            password=get_reg_password(parsed_args),
        )


class CreateAbgwTrueImageRegistration(TaskCommand):

    _description = "Create a true image registration for the backup storage."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            required=True,
            help="Registration name."
        )
        parser.add_argument(
            "--address",
            metavar="<address>",
            required=True,
            help="Registration IP address."
        )
        parser.add_argument(
            "--revocation-url",
            required=True,
            help=(
                "URL of the cloud management portal or the hostname/IP "
                "address and port of the local management server."
            )
        )
        parser.add_argument(
            "--certificates",
            dest="archived_certificates_chain",
            required=True,
            help="Path to the upstream certificate file for Acronis Cyber Protect Home Office."
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.registrations.create_true_image_async(
            name=parsed_args.name,
            address=parsed_args.address,
            revocation_url=parsed_args.revocation_url,
            archived_certificates_chain=get_stream(
                parsed_args.archived_certificates_chain
            ),
        )


class RenewTrueImageCertificates(TaskCommand):

    _description = "Update certificates for a true image registration."

    def configure_parser(self, parser):
        parser.add_argument(
            "registration",
            metavar="<registration>",
            help="Registration ID or name.",
        )
        parser.add_argument(
            "--certs",
            dest="archived_certificates_chain",
            required=True,
            help="Path to the upstream info file."
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        true_image_registration = find_resource(
            cluster.abgw.registrations,
            parsed_args.registration
        )
        return cluster.abgw.registrations.update_true_image(
            registration=true_image_registration,
            archived_certificates_chain=get_stream(
                parsed_args.archived_certificates_chain
            ),
        )
