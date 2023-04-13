# pylint: disable=line-too-long,no-self-use,no-member,useless-super-delegation

from vinfraclient.cmd.base import Lister, Command
from vinfraclient.utils import find_resource

__all__ = ['ListDomainPropsAccess', 'UpdateDomainPropsAccess', 'ACCESS_TYPES']

ACCESS_TYPES = ['pub', 'auth', 'domain']


class ManagerAccessor(object):
    def __init__(self, *args, **kwargs):
        super(ManagerAccessor, self).__init__(*args, **kwargs)

    @property
    def mgr(self):
        # noinspection PyUnresolvedReferences
        return self.app.vinfra.domain_props.access


class DomainParams(object):
    def __init__(self, *args, **kwargs):
        super(DomainParams, self).__init__(*args, **kwargs)

    def configure_parser(self, parser):
        parser.add_argument(
            "domain",
            metavar="<domain>",
            help="Domain name or domain ID"
        )

    def domain(self, parsed_args):
        # noinspection PyUnresolvedReferences
        return find_resource(self.app.vinfra.domains, parsed_args.domain)


class ListDomainPropsAccess(DomainParams, ManagerAccessor, Lister):
    _description = "List key and access rights of all property sheets of the domain specified by ID or name."
    _default_fields = ["domain", "key", "access"]

    def do_action(self, parsed_args):
        return self.mgr.list(self.domain(parsed_args))


class UpdateDomainPropsAccess(DomainParams, ManagerAccessor, Command):
    _description = "Update an access rights of the property sheet of the domain specified " \
                   "by ID or name and key."

    def configure_parser(self, parser):
        super(UpdateDomainPropsAccess, self).configure_parser(parser)
        parser.add_argument(
            "--access",
            default=ACCESS_TYPES[0],
            metavar="<access>",
            help="Access type"
        )

        parser.add_argument(
            "--key",
            metavar="<key>",
            help="Key name"
        )

    def do_action(self, parsed_args):
        self.mgr.update(self.domain(parsed_args), parsed_args.key, parsed_args.access)
