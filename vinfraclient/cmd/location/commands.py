# pylint: disable=line-too-long,abstract-method,no-member,useless-super-delegation,invalid-name,no-self-use
import uuid

from vinfraclient import argtypes
from vinfraclient import exceptions
from vinfraclient.cmd.base import Lister, ShowOne, Command

__all__ = [
    'ListFailureDomains', 'ChangeFailureDomain', 'ListLocations',
    'ShowLocation', 'UpdateLocation', 'DeleteLocation',
    'MoveLocations', 'CreateLocation'
]

NR_LOCATIONS = 5
CHOICES = range(2, 5)


class Configurable(object):
    def __init__(self, *args, **kwargs):
        super(Configurable, self).__init__(*args, **kwargs)

    @property
    def config(self):
        # noinspection PyUnresolvedReferences
        return self.app.vinfra.locations.configuration


class ListFailureDomains(Configurable, Lister):
    _description = "Show available failure domains."
    _default_fields = ["id", "singular", "plural"]

    def __init__(self, *args, **kwargs):
        super(ListFailureDomains, self).__init__(*args, **kwargs)

    def do_action(self, parsed_args):
        return self.config.list()


class ChangeFailureDomain(Configurable, Command):
    _description = "Set names for failure domain levels, " \
                   "which define the storage location. " \
                   "These four levels are 1=host, 2=rack, 3=row, 4=room. " \
                   "The names for levels 2, 3 and 4 can be changed."

    def __init__(self, *args, **kwargs):
        super(ChangeFailureDomain, self).__init__(*args, **kwargs)

    def configure_parser(self, parser):
        parser.add_argument(
            'id', type=int, choices=CHOICES,
            help="Failure domain ID")
        parser.add_argument(
            'singular', metavar="<singular-name>",
            type=lambda x: argtypes.size_limited_string(x, chars_limit=32),
            help="Singular name of the specified failure domain.")
        parser.add_argument(
            'plural', metavar="<plural-name>",
            type=lambda x: argtypes.size_limited_string(x, chars_limit=32),
            help="Plural name of the specified failure domain.")

    def do_action(self, parsed_args):
        self.config.set(
            level=parsed_args.id, singular=parsed_args.singular, plural=parsed_args.plural)


class ManagerAccessor(object):
    def __init__(self, *args, **kwargs):
        super(ManagerAccessor, self).__init__(*args, **kwargs)

    @property
    def locations(self):
        # noinspection PyUnresolvedReferences
        return self.app.vinfra.locations

    @property
    def _managers(self):
        return (self.locations.racks,
                self.locations.rows,
                self.locations.rooms)

    def _manager(self, level):
        data = {e.index(): e for e in self._managers}
        rv = data.get(level)
        if rv is None:
            raise exceptions.ValidationError(
                "Location's level '{}' is out of range of '{}'.".format(
                    level, tuple(data.keys())))
        return rv


class ParserAccessor(object):
    def __init__(self, *args, **kwargs):
        super(ParserAccessor, self).__init__(*args, **kwargs)

    def configure_parser(self, parser):
        # noinspection PyUnresolvedReferences
        self._configure_parser(parser)

    def _configure_parser(self, parser):
        parser.add_argument(
            "--fd", dest="level", metavar="<fd>", type=int, required=True,
            choices=CHOICES, help="Failure domain ID")
        return parser


class LevelAwareAction(ManagerAccessor, ParserAccessor):
    def __init__(self, *args, **kwargs):
        super(LevelAwareAction, self).__init__(*args, **kwargs)
        self.__level = None

    @property
    def level(self):
        return self.__level

    @property
    def mgr(self):
        return self._manager(self.level)

    def do_action(self, parsed_args):
        self.__level = parsed_args.level
        return self._internal_do_action(parsed_args)

    def _internal_do_action(self, parsed_args):
        raise NotImplementedError


# noinspection PyAbstractClass
class ObservableAction(LevelAwareAction):
    def __init__(self, *args, **kwargs):
        super(ObservableAction, self).__init__(*args, **kwargs)

    @property
    def _default_fields(self):
        return {
            self.locations.rooms.index(): ('id', 'name', 'children'),
            self.locations.racks.index(): ('id', 'name', 'parent', 'nodes'),
        }.get(self.level, ('id', 'name', 'parent', 'children'))


class ListLocations(ObservableAction, Lister):
    _description = "List locations of the specified failure domain."

    def _internal_do_action(self, parsed_args):
        return self.mgr.list()


class ShowLocation(ObservableAction, ShowOne):
    _description = "Show the location of the specified failure domain and identified by ID."

    def _configure_parser(self, parser):
        super(ShowLocation, self)._configure_parser(parser)
        parser.add_argument(
            "--id", metavar="<location-id>", type=int, required=True,
            help="ID of the location to show")
        return parser

    def _internal_do_action(self, parsed_args):
        return self.mgr.get(parsed_args.id)


class CreateLocation(ObservableAction, ShowOne):
    _description = "Create a new child location of the specified failure domain within the " \
                   "parent location identified by ID."

    def _configure_parser(self, parser):
        super(CreateLocation, self)._configure_parser(parser)
        parser.add_argument(
            "--name", metavar="<location-name>",
            type=lambda x: argtypes.size_limited_string(x, chars_limit=32),
            required=True,
            help="Name of the location to be created.")
        parser.add_argument(
            "--parent-id", dest="parent_id", metavar="<parent-id>", type=int, required=False, default=None,
            help="ID of the parent location where the child location should be created in.")
        return parser

    def _internal_do_action(self, parsed_args):
        return self.mgr.create(parsed_args.parent_id, parsed_args.name)


class UpdateLocation(LevelAwareAction, Command):
    _description = "Change the name of the location of the specified failure domain and identified by ID."

    def _configure_parser(self, parser):
        super(UpdateLocation, self)._configure_parser(parser)
        parser.add_argument(
            "--id", metavar="<location-id>", type=int, required=True,
            help="ID of the location to rename.")
        parser.add_argument(
            "--name", metavar="<location-name>",
            type=lambda x: argtypes.size_limited_string(x, chars_limit=32),
            required=True,
            help="The new location name.")
        return parser

    def _internal_do_action(self, parsed_args):
        self.mgr.update(parsed_args.id, parsed_args.name)


class MoveLocations(LevelAwareAction, Command):
    _description = "Move locations identified by IDs to the parent location " \
                   "of the specified failure domain and identified by ID."

    def _configure_parser(self, parser):
        parser.add_argument(
            "--children", metavar="<children>", type=str, nargs="+", required=True,
            help="IDs of locations to be moved to the parent location.")
        parser.add_argument(
            "--parent-fd", dest="level", metavar="<parent-fd>", type=int, required=True,
            choices=CHOICES, help="The failure domain of the parent location.")
        parser.add_argument(
            "--parent-id", metavar="<parent-id>", type=int, required=True, help="ID of the parent location")
        return parser

    @staticmethod
    def to_i(s):
        try:
            return int(s)
        except ValueError:
            raise exceptions.ValidationError(
                "Invalid input. Expected INTEGER got '{}'".format(s))

    @staticmethod
    def to_uuid(s):
        try:
            return uuid.UUID(s)
        except ValueError:
            raise exceptions.ValidationError(
                "Invalid input. Expected UUID got '{}'".format(s))

    def children(self, parsed_args):
        return list(map(self.to_uuid, parsed_args.children)
                    if self.locations.racks.index() == self.level else
                    map(self.to_i, parsed_args.children))

    def _internal_do_action(self, parsed_args):
        self.mgr.add_children(parsed_args.parent_id, *self.children(parsed_args))


class DeleteLocation(LevelAwareAction, Command):
    _description = "Delete the location of specified failure domain and identified by ID."

    def _configure_parser(self, parser):
        super(DeleteLocation, self)._configure_parser(parser)
        parser.add_argument(
            "--id", metavar="<location-id>", type=int, required=True,
            help="ID of the location to delete.")
        return parser

    def _internal_do_action(self, parsed_args):
        self.mgr.delete(parsed_args.id)
