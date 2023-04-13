from vinfraclient.cmd.base import ShowOne, Command, Lister
from vinfraclient.exceptions import ValidationError
from vinfraclient.utils import find_resource, get_password

from . import utils


def _roles_parser(value):
    if not value:
        return []
    return [name.lower() for name in value.split(',')]


def _add_domain_option(parser):
    parser.add_argument(
        "--domain",
        metavar="<domain>",
        required=True,
        help="Domain name or ID",
    )


def _add_user_arg(parser):
    parser.add_argument(
        "user",
        metavar="<user>",
        help="User ID or name"
    )


def _add_user_set_options(parser, create=False):
    parser.add_argument(
        "--email",
        metavar="<name>",
        help="User email",
    )
    parser.add_argument(
        "--description",
        metavar="<description>",
        help="User description",
    )
    parser.add_argument(
        "--assign",
        dest='assigned_projects',
        nargs=2,
        action='append',
        metavar=("<project>", "<role>"),
        help="Assign a user to a project with one or more permission sets."
             " Specify this option multiple times to assign the user"
             " to multiple projects.\n"
             "<project> - Project ID or name\n"
             "<role> - user role in project",
    )
    if not create:
        parser.add_argument(
            "--unassign",
            dest='unassigned_projects',
            action='append',
            metavar="<project>",
            help="Unassign a user from a project."
                 " Specify this option multiple times to unassign the user"
                 " from multiple projects.\n"
                 "<project> - Project ID or name",
        )
    parser.add_argument(
        "--assign-domain",
        dest='assigned_domains',
        nargs=2,
        action='append',
        metavar=("<domain>", "<roles>"),
        help="Assign a user to a domain with one or more permission sets. "
             "Specify this option multiple times to assign the user "
             "to multiple domains. This option is only valid "
             "for service accounts.\n"
             "<domain> - Domain ID or name\n"
             "<roles> - a comma-separated list of service account roles",
    )

    if not create:
        parser.add_argument(
            "--unassign-domain",
            dest='unassigned_domains',
            action='append',
            metavar="<domain>",
            help="Unassign a user from a domain. "
                 "Specify this option multiple times to unassign the user from "
                 "multiple domains. This option is only valid "
                 "for service accounts.\n"
                 "<domain> - Domain ID or name",
        )

    parser.add_argument(
        "--domain-permissions",
        dest='domain_permissions',
        metavar="<domain_permissions>",
        type=_roles_parser,
        help="A comma-separated list of domain permissions",
    )
    parser.add_argument(
        "--system-permissions",
        dest='system_permissions',
        metavar="<system_permissions>",
        type=_roles_parser,
        help="A comma-separated list of system permissions",
    )
    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument(
        "--enable",
        dest="is_enabled",
        action="store_true",
        default=None,
        help="Enable user.",
    )
    enable_group.add_argument(
        "--disable",
        dest="is_enabled",
        action='store_false',
        default=None,
        help="Disable user.",
    )


class CreateDomainUser(ShowOne):
    _description = "Create a new domain user."

    def configure_parser(self, parser):
        _add_user_set_options(parser, create=True)
        _add_domain_option(parser)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="User name",
        )

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        assigned_projects = utils.parse_assigned_projects(
            domain, parsed_args.assigned_projects)
        assigned_domains = utils.parse_assigned_domains(
            self.app.vinfra.domains,
            parsed_args.assigned_domains,
        )
        password = get_password("New user password: ")

        return domain.users_manager.create(
            parsed_args.name, password,
            enabled=parsed_args.is_enabled,
            description=parsed_args.description,
            email=parsed_args.email,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
            domain_permissions=parsed_args.domain_permissions,
            system_permissions=parsed_args.system_permissions,
        )


class DeleteDomainUser(Command):
    _description = "Remove a domain user."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_user_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        user = find_resource(domain.users_manager, parsed_args.user)
        return user.delete()


class ListDomainUser(Lister):
    _description = "List all users in a domain."
    _default_fields = ['id', 'name', 'email', 'enabled', 'description',
                       'domain_permissions', 'assigned_projects']

    def configure_parser(self, parser):
        _add_domain_option(parser)
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of users to list. To list all '
                 'users, set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<user>',
            help='List users after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List users with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a user with the specified ID or list users using '
                 'a filter.'
        )
        parser.add_argument(
            '--tags',
            metavar='<tag>[,<tag>,...]',
            action='filter',
            operators=('any', 'not_any'),
            help='List users with the specified tags (comma-separated) '
                 'or use a filter.'
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.name:
            filters['name'] = parsed_args.name
        if parsed_args.id:
            if not parsed_args.id.startswith('in:'):
                parsed_args.id = 'in:{}'.format(parsed_args.id)
            filters['id'] = parsed_args.id
        if parsed_args.tags:
            filters['tags'] = parsed_args.tags

        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        return domain.users_manager.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)


class SetDomainUser(ShowOne):
    _description = "Modify the parameters of a domain user."

    def configure_parser(self, parser):
        parser.add_argument(
            "--password",
            action='store_true',
            default=None,
            help="Request the password from stdin."
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="New user name",
        )

        _add_user_set_options(parser)
        _add_domain_option(parser)
        _add_user_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)

        assigned_projects = (
            utils.parse_unassigned_projects(
                domain, parsed_args.unassigned_projects) +
            utils.parse_assigned_projects(
                domain, parsed_args.assigned_projects)
        )
        assigned_domains = utils.parse_assigned_domains(
            self.app.vinfra.domains,
            parsed_args.assigned_domains,
            parsed_args.unassigned_domains,
        )
        user = find_resource(domain.users_manager, parsed_args.user)
        password = None

        if parsed_args.password:
            whoami = self.app.vinfra.users.get_current()
            if user.name == whoami.name:
                raise ValidationError('To change user password, use '
                                      'the change-password subcommand')
            password = get_password("User password: ")

        return user.update(
            name=parsed_args.name,
            password=password,
            enabled=parsed_args.is_enabled,
            description=parsed_args.description,
            email=parsed_args.email,
            domain_permissions=parsed_args.domain_permissions,
            system_permissions=parsed_args.system_permissions,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
        )


class ShowDomainUser(ShowOne):
    _description = "Display information about a domain user."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_user_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        user = find_resource(domain.users_manager, parsed_args.user)
        return user


class ListDomainUserGroups(Lister):
    _description = "List users of a group."
    _default_fields = ['id', 'name', 'description', 'role']

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_user_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        user = find_resource(domain.users_manager, parsed_args.user)
        return user.list_groups()


class UnlockDomainUser(Command):
    _description = "Unlock a domain user"

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_user_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        user = find_resource(domain.users_manager, parsed_args.user)
        return user.unlock()
