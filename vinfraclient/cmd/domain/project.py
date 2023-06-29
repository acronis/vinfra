import argparse

from vinfraclient.cmd.base import Command, Lister, ShowOne
from vinfraclient.utils import find_resource

from .utils import find_domain


def _roles_parser(value):
    return [name.lower() for name in value.split(',')]


def _add_domain_option(parser):
    parser.add_argument(
        "--domain",
        metavar="<domain>",
        required=True,
        help="Domain name or ID",
    )


def _add_project_arg(parser):
    parser.add_argument(
        "project",
        metavar="<project>",
        help="Project name or ID",
    )


def _add_project_set_optional(parser):
    parser.add_argument(
        "--description",
        metavar="<description>",
        help="Project description",
    )
    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument(
        "--enable",
        dest="is_enabled",
        action="store_true",
        default=None,
        help="Enable project.",
    )
    enable_group.add_argument(
        "--disable",
        dest="is_enabled",
        action='store_false',
        default=None,
        help="Disable project.",
    )


def _add_user_option(parser):
    parser.add_argument(
        "--user",
        metavar="<user>",
        required=True,
        help="User name or ID",
    )


class ListDomainProjects(Lister):
    _description = "List domain projects."
    _default_fields = ['id', 'name', 'enabled', 'description', 'domain_id']

    def configure_parser(self, parser):
        _add_domain_option(parser)
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of projects to list. To list all '
                 'projects, set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<project>',
            help='List projects after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List projects with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a project with the specified ID or list projects using '
                 'a filter.'
        )
        parser.add_argument(
            '--tags',
            metavar='<tag>[,<tag>,...]',
            action='filter',
            operators=('any', 'not_any'),
            help='List projects with the specified tags (comma-separated) '
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

        domain = find_domain(self.app.vinfra, parsed_args.domain)
        return domain.projects_manager.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)


class ShowDomainProject(ShowOne):
    _description = "Show details of a domain project."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_project_arg(parser)

    def do_action(self, parsed_args):
        domain = find_domain(self.app.vinfra, parsed_args.domain)
        project = find_resource(domain.projects_manager, parsed_args.project)
        return project


class CreateDomainProject(ShowOne):
    _description = "Create a new domain project."

    def configure_parser(self, parser):
        _add_project_set_optional(parser)
        parser.add_argument(
            "--parent",
            metavar="<parent>",
            help=argparse.SUPPRESS,
        )
        _add_domain_option(parser)
        parser.add_argument(
            "name",
            help="Project name",
        )

    def do_action(self, parsed_args):
        domain = find_domain(self.app.vinfra, parsed_args.domain)
        parent = None
        if parsed_args.parent:
            parent = find_resource(domain.projects_manager, parsed_args.parent)
        return domain.projects_manager.create(
            parsed_args.name, description=parsed_args.description,
            enabled=parsed_args.is_enabled, parent=parent,
        )


class DeleteDomainProject(Command):
    _description = "Delete a domain project."

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_project_arg(parser)

    def do_action(self, parsed_args):
        domain = find_domain(self.app.vinfra, parsed_args.domain)
        project = find_resource(domain.projects_manager, parsed_args.project)
        return domain.projects_manager.delete(project)


class SetDomainProject(ShowOne):
    _description = "Modify an existing domain project."

    def configure_parser(self, parser):
        _add_project_set_optional(parser)
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="New project name",
        )
        _add_domain_option(parser)
        _add_project_arg(parser)

    def do_action(self, parsed_args):
        domain = find_domain(self.app.vinfra, parsed_args.domain)
        project = find_resource(domain.projects_manager, parsed_args.project)
        return project.update(
            name=parsed_args.name, description=parsed_args.description,
            enabled=parsed_args.is_enabled
        )


class ListProjectUsers(Lister):
    _description = "List users of a project."
    _default_fields = ['id', 'name', 'description', 'role']

    def configure_parser(self, parser):
        _add_domain_option(parser)
        _add_project_arg(parser)

    def do_action(self, parsed_args):
        domain = find_domain(self.app.vinfra, parsed_args.domain)
        project = find_resource(domain.projects_manager, parsed_args.project)
        return project.list_users()


class RemoveProjectUser(Command):
    _description = "Remove a user from a project."

    def configure_parser(self, parser):
        _add_user_option(parser)
        _add_domain_option(parser)
        _add_project_arg(parser)

    def do_action(self, parsed_args):
        domain = find_domain(self.app.vinfra, parsed_args.domain)
        project = find_resource(domain.projects_manager, parsed_args.project)
        user = find_resource(domain.users_manager, parsed_args.user)

        return project.delete_users(user)
