from vinfraclient import exceptions
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import ShowOne, Lister, TaskCommand
from vinfraclient.formatters import columns as fmt_columns
from vinfraclient.utils import find_resource, get_cluster


class ShowClusterEncryption(ShowOne):
    _description = "Display storage tiers encyption."

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.get_settings()['encryption']


class SetClusterEncryption(ShowOne):
    _description = "Set storage tiers encyption."

    def configure_parser(self, parser):
        # NOTE(akurbatov): it's better to keep formatters group at the end
        parser.add_argument(
            "--tier-enable",
            dest="encryptions",
            type=int,
            choices=range(0, 4),
            action="append",
            default=[],
            help="Enable encryption for storage tiers. "
                 "This option can be used multiple times."
        )
        parser.add_argument(
            "--tier-disable",
            dest="no_encryptions",
            type=int,
            choices=range(0, 4),
            action="append",
            default=[],
            help="Disable encryption for storage tiers. "
                 "This option can be used multiple times."
        )

    def do_action(self, parsed_args):
        if set(parsed_args.encryptions) & set(parsed_args.no_encryptions):
            raise exceptions.ValidationError('Encryption options conflict')

        cluster = get_cluster(self.app.vinfra)

        encryption = {}
        for tier in parsed_args.encryptions:
            encryption['tier%s' % tier] = True
        for tier in parsed_args.no_encryptions:
            encryption['tier%s' % tier] = False
        if encryption and len(encryption) != 4:
            set_encryption = dict(encryption)
            # NOTE(akurbatov): backend API requires all tiers to be set
            encryption = cluster.get_settings()['encryption']
            encryption.update(set_encryption)

        settings = cluster.set_settings(encryption=encryption)
        return settings['encryption']


class ShowDns(ShowOne):
    _description = "Display DNS servers."
    _formatters = {
        'nameservers': fmt_columns.ListColumn,
        'dhcp_nameservers': fmt_columns.ListColumn,
    }

    def do_action(self, parsed_args):
        return self.app.vinfra.dns.get()


class SetDns(ShowOne):
    _description = "Set DNS servers."
    _formatters = {
        'nameservers': fmt_columns.ListColumn,
        'dhcp_nameservers': fmt_columns.ListColumn,
    }

    def configure_parser(self, parser):
        parser.add_argument(
            "--nameservers",
            metavar="<nameservers>",
            type=parse_list_options,
            required=True,
            help="A comma-separated list of DNS servers"
        )

    def do_action(self, parsed_args):
        self.app.vinfra.dns.update(parsed_args.nameservers)
        return self.app.vinfra.dns.get()


class ListLocale(Lister):
    _description = "List locales."
    _default_fields = ['language', 'english_name', 'display_name', 'enabled',
                       'is_default']
    auth_required = False

    def do_action(self, parsed_args):
        return self.app.vinfra.locales.list()


class ShowLocale(ShowOne):
    _description = "Display locale information."

    def configure_parser(self, parser):
        parser.add_argument(
            "locale",
            metavar="<locale>",
            help="Locale language"
        )

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.locales, parsed_args.locale)


class UpdateLocale(ShowOne):
    _description = "Update locale settings."

    def configure_parser(self, parser):
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            "--enable",
            dest='enabled',
            action='store_true',
            default=None,
            help="Enable the locale."
        )
        enable_group.add_argument(
            "--disable",
            dest='enabled',
            action='store_false',
            default=None,
            help="Disable the locale."
        )

        parser.add_argument(
            "--default",
            dest='default',
            action='store_true',
            default=None,
            help="Set locale as default."
        )

        parser.add_argument(
            "locale",
            metavar="<locale>",
            help="Locale language"
        )

    def do_action(self, parsed_args):
        locale = find_resource(self.app.vinfra.locales, parsed_args.locale)
        return locale.update(
            enabled=parsed_args.enabled, is_default=parsed_args.default)


class ShowCsConfig(ShowOne):

    _description = "Show CS config."

    def do_action(self, parsed_args):
        return self.app.vinfra.cses_config.get()


class ChangeCsConfig(TaskCommand):

    _description = "Change CS config."

    def configure_parser(self, parser):
        parser.add_argument(
            "--enable",
            dest="enable",
            action="store_true",
            help="Enable RDMA."
        )
        parser.add_argument(
            "--disable",
            dest="enable",
            action="store_false",
            help="Disable RDMA."
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.cses_config.change_async(
            enable=parsed_args.enable
        )


def _smtp_client_settings(parser):
    parser.add_argument(
        "--user-account",
        metavar="<user-account>",
        help="User account of the notification sender"
    )
    parser.add_argument(
        "--user-password",
        metavar="<user-password>",
        help="Password for the user account"
    )
    parser.add_argument(
        "--smtp-server",
        metavar="<smtp-server>",
        required=True,
        help="DNS name of the SMTP server"
    )
    parser.add_argument(
        "--smtp-port",
        metavar="<smtp-port>",
        required=True,
        help="SMTP port used by the SMTP server"
    )
    parser.add_argument(
        "--security",
        dest="security",
        required=True,
        choices=["SSL", "STARTTLS"],
        help="Security protocol of the SMTP server"
    )


def _notification_settings(parser):
    severity_group = parser.add_mutually_exclusive_group(required=True)
    severity_group.add_argument(
        '--severity',
        dest="severities",
        action='append',
        choices=["error", "warning", "info"],
        help='Severity type of email notifications. This option can be used multiple times.'
    )
    parser.add_argument(
        "--from",
        dest="from_",
        metavar="<from>",
        help="Email address of the notification sender"
    )
    parser.add_argument(
        "--sender-name",
        dest="sender_name",
        metavar="<sender-name>",
        help="Notification sender name"
    )
    parser.add_argument(
        "--email-recipients-list",
        dest="email_recipients_list",
        metavar="<email-recipients-list>",
        type=parse_list_options,
        help="A comma-separated list of notification recipients' emails"
    )


class SetEmailNotifications(ShowOne):
    _description = "Enable email notifications."

    def configure_parser(self, parser):
        _smtp_client_settings(parser)
        _notification_settings(parser)

    def do_action(self, parsed_args):
        return self.app.vinfra.email_notifications.update(parsed_args.from_,
                                                          parsed_args.sender_name,
                                                          parsed_args.email_recipients_list,
                                                          parsed_args.smtp_server,
                                                          parsed_args.smtp_port,
                                                          parsed_args.security,
                                                          alerts_severities=parsed_args.severities,
                                                          user_account=parsed_args.user_account,
                                                          user_password=parsed_args.user_password)


class ShowEmailNotificationsSettings(ShowOne):

    _description = "Display email notification settings."

    def do_action(self, parsed_args):
        return self.app.vinfra.email_notifications.get()


class DisableEmailNotifications(ShowOne):

    _description = "Disable email notifications."

    def do_action(self, parsed_args):
        alert_severities = []

        return self.app.vinfra.email_notifications.patch(alert_severities)
