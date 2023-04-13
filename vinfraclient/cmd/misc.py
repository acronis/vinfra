from vinfra.api.base import get_id
from vinfraclient.cmd.base import TaskCommand, ShowOne, SuppressMixin
from vinfraclient.utils import find_resource


class ProblemReport(TaskCommand):
    _description = "Generate and send a problem report."

    def configure_parser(self, parser):
        parser.add_argument(
            "--email",
            metavar="<email>",
            dest="contact_email",
            help="Contact email address"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            dest="problem_description",
            help="Problem description"
        )
        parser.add_argument(
            "--send",
            action="store_true",
            help="Generate the problem report archive and"
                 "send it to the technical support team."
        )
        parser.add_argument(
            "--verbosity-level",
            dest="verbosity_level",
            choices=["minimal", "basic", "extended"],
            help="Set the desired verbosity level for a problem report. The default is 'basic'."
        )
        parser.add_argument(
            "--include-days",
            dest="include_days",
            type=int,
            help="Set last modification time threshold for logs. The default is 1."
        )
        parser.add_argument(
            "--node",
            dest='nodes',
            action='append',
            help="ID or hostname of the node to be included in a problem report. "
                 "This option can be used multiple times. "
                 "All cluster nodes are included if the parameter is omitted."
        )

    def do_action(self, parsed_args):
        if parsed_args.nodes:
            nodes = [find_resource(self.app.vinfra.nodes, node)
                     for node in parsed_args.nodes]
            node_ids = [get_id(node) for node in nodes]
        else:
            node_ids = None
        return self.app.vinfra.report_async(
            contact_email=parsed_args.contact_email,
            problem_description=parsed_args.problem_description,
            send=parsed_args.send,
            verbosity_level=parsed_args.verbosity_level, include_days=parsed_args.include_days,
            node_ids=node_ids
        )


class ShowReportSettings(SuppressMixin, ShowOne):
    _description = "Show reports settings."

    def do_action(self, parsed_args):
        return self.app.vinfra.show_reports_settings()


class SetReportSettings(SuppressMixin, TaskCommand):
    _description = "Set a report settings."

    def configure_parser(self, parser):
        parser.add_argument(
            "--report-type",
            choices=['cep', 'crash', 'problem'],
            metavar="<report-type>",
            required=True,
            dest="report_type",
            help="Report type",
        )
        commands = parser.add_mutually_exclusive_group(required=True)
        commands.add_argument(
            "--disable",
            action="store_true",
            help="Disable the report.",
        )
        commands.add_argument(
            "--enable",
            action="store_true",
            help="Enable the report.",
        )
        commands.add_argument(
            "--disable-sending",
            action="store_true",
            help="Disable the report's sending capabilities.",
        )
        commands.add_argument(
            "--enable-sending",
            action="store_true",
            help="Enable the report's sending capabilities.",
        )
        commands.add_argument(
            "--retry",
            action="store_true",
            default=False,
            help="Retry the last failed process.",
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.configure_report_async(
            parsed_args.report_type,
            enable=True if parsed_args.enable else (
                False if parsed_args.disable else None),
            enable_sending=True if parsed_args.enable_sending else (
                False if parsed_args.disable_sending else None),
            retry=parsed_args.retry)
