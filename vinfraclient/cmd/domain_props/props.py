# pylint: disable=line-too-long,no-self-use,no-member,useless-super-delegation

import json

from vinfraclient.cmd.base import ShowOne, Command
from vinfraclient import exceptions
from vinfraclient.utils import find_resource
from .access import ACCESS_TYPES

__all__ = ['CreateDomainProps', 'GetDomainProps', 'UpdateDomainProps', 'DeleteDomainProps']


class ManagerAccessor(object):
    def __init__(self, *args, **kwargs):
        super(ManagerAccessor, self).__init__(*args, **kwargs)

    @property
    def mgr(self):
        # noinspection PyUnresolvedReferences
        return self.app.vinfra.domain_props.properties


class DomainKeyParams(object):
    def __init__(self, *args, **kwargs):
        super(DomainKeyParams, self).__init__(*args, **kwargs)

    def configure_parser(self, parser):
        parser.add_argument(
            "domain",
            metavar="<domain>",
            help="Domain name or domain ID"
        )
        parser.add_argument(
            "--key",
            required=True,
            metavar="<key>",
            help="Key name"
        )

    def domain(self, parsed_args):
        # noinspection PyUnresolvedReferences
        return find_resource(self.app.vinfra.domains, parsed_args.domain)

    def key(self, parsed_args):
        # noinspection PyUnresolvedReferences
        return parsed_args.key


class CreateDomainProps(DomainKeyParams, ManagerAccessor, Command):
    _description = "Create a property sheet for the domain specified by ID or name and key."

    def configure_parser(self, parser):
        super(CreateDomainProps, self).configure_parser(parser)
        parser.add_argument(
            "--data",
            required=True,
            metavar="<data>",
            help="Property sheet. Should be a valid JSON object"
        )
        parser.add_argument(
            "--access",
            default=ACCESS_TYPES[0],
            metavar="<access>",
            help="Access type"
        )

    def data(self, parsed_args):
        try:
            return json.loads(parsed_args.data)
        except ValueError:
            raise exceptions.ValidationError("data should be a valid JSON object")

    def do_action(self, parsed_args):
        self.mgr.create(self.domain(parsed_args), self.key(parsed_args), parsed_args.access, self.data(parsed_args))


class UpdateDomainProps(CreateDomainProps):
    _description = "Update a property sheet of the domain specified by ID or name and key."

    def do_action(self, parsed_args):
        self.mgr.update(self.domain(parsed_args), self.key(parsed_args), self.data(parsed_args))


class GetDomainProps(DomainKeyParams, ManagerAccessor, ShowOne):
    _description = "Show a property sheet of the domain specified by ID or name and key."
    _default_fields = ["domain", "key", "data"]

    def do_action(self, parsed_args):
        return self.mgr.get(self.domain(parsed_args), self.key(parsed_args))


class DeleteDomainProps(DomainKeyParams, ManagerAccessor, Command):
    _description = "Delete a property sheet of the domain specified by ID or name and key."

    def do_action(self, parsed_args):
        return self.mgr.delete(self.domain(parsed_args), self.key(parsed_args))
