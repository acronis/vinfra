# pylint: disable=line-too-long,abstract-method,no-member,useless-super-delegation,invalid-name,no-self-use

import uuid

from vinfra.api.logging_service import Severity
from vinfraclient.cmd.base import Lister, Command
from vinfraclient.utils import find_resource


class ManagerAccessor(object):
    def __init__(self, *args, **kwargs):
        super(ManagerAccessor, self).__init__(*args, **kwargs)

    @property
    def mgr(self):
        # noinspection PyUnresolvedReferences
        return self.app.vinfra.logging_service.severity


class NodeParams(object):
    def __init__(self, *args, **kwargs):
        super(NodeParams, self).__init__(*args, **kwargs)

    def configure_parser(self, parser):
        parser.add_argument(
            "--nodes",
            metavar="<nodes>", nargs='*', required=False,
            help="A space-separated or comma-separated list of node hostnames or IDs"
        )

    @staticmethod
    def _flatten(iterable):
        return filter(bool, (e.strip() for v in iterable for e in v.split(',')))

    def nodes(self, parsed_args):
        # noinspection PyUnresolvedReferences
        return [uuid.UUID(n.id) for n in (find_resource(self.app.vinfra.nodes, node)
                                          for node in self._flatten(parsed_args.nodes or ()))]


class GetLogLevel(NodeParams, ManagerAccessor, Lister):
    _description = "Show the logging severity for nodes specified by ID or host name."
    _default_fields = ["node_id", "host", "agent_level", "backend_level"]

    def __init__(self, *args, **kwargs):
        super(GetLogLevel, self).__init__(*args, **kwargs)

    def configure_parser(self, parser):
        super(GetLogLevel, self).configure_parser(parser)
        return parser

    def do_action(self, parsed_args):
        return self.mgr.get(self.nodes(parsed_args))


class SetLogLevel(NodeParams, ManagerAccessor, Command):
    _description = "Show the logging severity for nodes specified by ID or host name."

    def __init__(self, *args, **kwargs):
        super(SetLogLevel, self).__init__(*args, **kwargs)

    def configure_parser(self, parser):
        super(SetLogLevel, self).configure_parser(parser)
        parser.add_argument(
            "severity", choices=Severity.values(), help="Choose logging severity"
        )
        return parser

    def do_action(self, parsed_args):
        self.mgr.set(parsed_args.severity, self.nodes(parsed_args))
