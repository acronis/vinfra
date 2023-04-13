from vinfraclient.cmd.base import Lister, ShowOne
from vinfraclient.formatters import columns as fmt_columns
from vinfraclient.utils import find_resource


def _alert_arg(parser):
    parser.add_argument(
        "alert",
        type=int,
        metavar="<alert>",
        help="Alert ID"
    )


class ListAlert(Lister):
    _description = "List alert log entries"
    _default_fields = ['id', 'type', 'datetime', 'severity', 'enabled']
    _formatters = {'datetime': fmt_columns.DatetimeColumn}

    def configure_parser(self, parser):
        parser.add_argument(
            "--all",
            dest="all",
            action="store_true",
            help="Show both enabled and disabled alerts."
        )
        parser.add_argument(
            "--lang",
            type=str,
            default='en',
            help="Language of alert message. Supported values: en, de, es, ja, pt, ru, tr, zh"
        )

    def do_action(self, parsed_args):
        enabled = not parsed_args.all
        lang = parsed_args.lang
        alerts = self.app.vinfra.alerts.list(enabled=enabled, lang=lang)
        return alerts


class ShowAlert(ShowOne):
    _description = "Show details of the specified alert log entry."
    _formatters = {'datetime': fmt_columns.DatetimeColumn}

    def configure_parser(self, parser):
        _alert_arg(parser)

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.alerts, parsed_args.alert)


class DeleteAlert(ShowOne):
    _description = "Remove an entry from the alert log."
    _formatters = {'datetime': fmt_columns.DatetimeColumn}

    def configure_parser(self, parser):
        _alert_arg(parser)

    def do_action(self, parsed_args):
        alert = find_resource(self.app.vinfra.alerts, parsed_args.alert)
        return alert.update(enabled=False)
