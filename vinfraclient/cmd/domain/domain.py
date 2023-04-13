from vinfraclient.cmd.base import Command, Lister, ShowOne
from vinfraclient.utils import find_resource


def _domain_arg(parser):
    parser.add_argument(
        "domain",
        metavar="<domain>",
        help="Domain ID or name"
    )


def _common_set_options(parser):
    parser.add_argument(
        "--description",
        metavar="<description>",
        help="Domain description",
    )
    parser.add_argument(
        "--enable",
        dest="enabled",
        action="store_true",
        default=None,
        help="Enable domain",
    )
    parser.add_argument(
        "--disable",
        dest="enabled",
        action="store_false",
        default=None,
        help="Disable domain",
    )


class ListDomains(Lister):
    _description = "List all available domains."
    _default_fields = ['id', 'name', 'enabled', 'description']

    def do_action(self, parsed_args):
        return self.app.vinfra.domains.list()


class CreateDomain(ShowOne):
    _description = "Create a new domain."

    def configure_parser(self, parser):
        _common_set_options(parser)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Domain name",
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.domains.create(
            parsed_args.name,
            description=parsed_args.description,
            enabled=parsed_args.enabled)


class SetDomain(ShowOne):
    _description = "Modify an existing domain."

    def configure_parser(self, parser):
        _common_set_options(parser)
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="Domain name",
        )
        _domain_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        return domain.update(name=parsed_args.name,
                             description=parsed_args.description,
                             enabled=parsed_args.enabled)


class ShowDomain(ShowOne):
    _description = "Display information about a domain."

    def configure_parser(self, parser):
        _domain_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        return self.app.vinfra.domains.get(domain)


class DeleteDomain(Command):
    _description = "Delete a domain."

    def configure_parser(self, parser):
        _domain_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        return domain.delete()
