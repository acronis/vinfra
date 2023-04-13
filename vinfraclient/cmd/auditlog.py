from vinfraclient.cmd.base import Lister, ShowOne
from vinfraclient.formatters import columns as fmt_columns
from vinfraclient.utils import find_resource


class ListAuditLog(Lister):
    _description = "List all audit log entries."
    _default_fields = ['id', 'username', 'type', 'activity', 'timestamp']
    _formatters = {'timestamp': fmt_columns.DatetimeColumn}

    def do_action(self, parsed_args):
        auditlogs = self.app.vinfra.auditlog.list()
        return auditlogs


class ShowAuditLog(ShowOne):
    _description = "Show details of an audit log entry."
    _formatters = {'timestamp': fmt_columns.DatetimeColumn}

    def configure_parser(self, parser):
        parser.add_argument(
            "auditlog",
            type=int,
            metavar="<auditlog>",
            help="Audit log ID"
        )

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.auditlog, parsed_args.auditlog)
