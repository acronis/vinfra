from vinfraclient.cmd.base import ShowOne, Command, Lister
from vinfraclient.utils import find_resource

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


def _add_group_arg(parser):
    parser.add_argument(
        "group",
        metavar="<group>",
        help="Group ID or name"
    )


def _add_user_arg(parser):
    parser.add_argument(
        "user",
        metavar="<user>",
        help="User ID or name"
    )


def _add_group_set_options(parser, create=False):
    parser.add_argument(
        "--description",
        metavar="<description>",
        help="Group description",
    )

    parser.add_argument(
        "--assign",
        dest='assigned_projects',
        nargs=2,
        action='append',
        metavar=("<project>", "<role>"),
        help="Assign a group to a project with one or more permission sets."
             " Specify this option multiple times to assign the group"
             " to multiple projects.\n"
             "<project> - Project ID or name\n"
             "<role> - Group role in project",
    )
    if not create:
        parser.add_argument(
            "--unassign",
            dest='unassigned_projects',
            action='append',
            metavar="<project>",
            help="Unassign a group from a project."
                 " Specify this option multiple times to unassign the group"
                 " from multiple projects.\n"
                 "<project> - Project ID or name",
        )

    parser.add_argument(
        "--assign-domain",
        dest='assigned_domains',
        nargs=2,
        action='append',
        metavar=("<domain>", "<roles>"),
        help="Assign a group to a domain with one or more permission sets. "
             "Specify this option multiple times to assign the group "
             "to multiple domains. This option is only valid "
             "for service accounts.\n"
             "<domain> - Domain ID or name\n"
             "<roles> - A comma-separated list of service account roles",
    )

    if not create:
        parser.add_argument(
            "--unassign-domain",
            dest='unassigned_domains',
            action='append',
            metavar="<domain>",
            help="Unassign a group from a domain. "
                 "Specify this option multiple times to unassign the group "
                 " from multiple domains. This option is only valid "
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


class CreateDomainGroup(ShowOne):
    _description = "Create a new domain group."

    def configure_parser(self, parser):
        _add_group_set_options(parser, create=True)
        _add_domain_option(parser)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Group name",
        )

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        assigned_projects = utils.parse_assigned_projects(
            domain, parsed_args.assigned_projects)
        assigned_domains = utils.parse_assigned_domains(
            self.app.vinfra.domains,
            parsed_args.assigned_domains,
        )

        return domain.groups_manager.create(
            parsed_args.name,
            description=parsed_args.description,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
            domain_permissions=parsed_args.domain_permissions,
            system_permissions=parsed_args.system_permissions,
        )


class DeleteDomainGroup(Command):
    _description = "Remove a domain group."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_group_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        group = find_resource(domain.groups_manager, parsed_args.group)
        return group.delete()


class ListDomainGroup(Lister):
    _description = "List all groups in a domain."
    _default_fields = ['id', 'name', 'description',
                       'domain_permissions', 'assigned_projects']

    def configure_parser(self, parser):
        _add_domain_option(parser)
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of groups to list. To list all '
                 'groups, set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<group>',
            help='List groups after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List groups with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a group with the specified ID or list groups using '
                 'a filter.'
        )
        parser.add_argument(
            '--tags',
            metavar='<tag>[,<tag>,...]',
            action='filter',
            operators=('any', 'not_any'),
            help='List groups with the specified tags (comma-separated) '
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
        return domain.groups_manager.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)


class SetDomainGroup(ShowOne):
    _description = "Modify the parameters of a domain group."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="New group name",
        )

        _add_group_set_options(parser)
        _add_domain_option(parser)
        _add_group_arg(parser)

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
        group = find_resource(domain.groups_manager, parsed_args.group)

        return group.update(
            name=parsed_args.name,
            description=parsed_args.description,
            domain_permissions=parsed_args.domain_permissions,
            system_permissions=parsed_args.system_permissions,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
        )


class ShowDomainGroup(ShowOne):
    _description = "Display information about a domain group."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_group_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        group = find_resource(domain.groups_manager, parsed_args.group)
        return group


class ListDomainGroupUsers(Lister):
    _description = "List users of a group."
    _default_fields = ['id', 'name', 'description', 'role']

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_group_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        group = find_resource(domain.groups_manager, parsed_args.group)
        return group.list_users()


class RemoveDomainGroupUser(Command):
    _description = "Remove a user from a group."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_group_arg(parser)
        _add_user_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        group = find_resource(domain.groups_manager, parsed_args.group)
        user = find_resource(domain.users_manager, parsed_args.user)

        return group.delete_user(user)


class AddDomainGroupUser(Command):
    _description = "Add a user to a group."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_group_arg(parser)
        _add_user_arg(parser)

    def do_action(self, parsed_args):
        domain = find_resource(self.app.vinfra.domains, parsed_args.domain)
        group = find_resource(domain.groups_manager, parsed_args.group)
        user = find_resource(domain.users_manager, parsed_args.user)

        return group.add_user(user)
