from vinfraclient.cmd.base import Lister, ShowOne, Command
from vinfraclient.exceptions import ValidationError
from vinfraclient.utils import find_resource, get_password


def roles_parser(value):
    return [name.lower() for name in value.split(',')]


def user_arg(parser):
    parser.add_argument(
        "user",
        metavar="<user>",
        help="User ID or name"
    )


def _common_set_options(parser, create_command=True):
    parser.add_argument(
        "--description",
        metavar="<description>",
        help="User description",
    )
    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument(
        "--enable",
        dest="is_enabled",
        action="store_true",
        default=None,
        help="Enable user",
    )
    user_group.add_argument(
        "--disable",
        dest="is_enabled",
        action='store_false',
        default=None,
        help="Disable user",
    )
    if create_command:
        parser.add_argument(
            "--roles",
            metavar="<roles>",
            type=roles_parser,
            help="A comma-separated list of user roles",
        )
    else:  # set command
        roles_group = parser.add_mutually_exclusive_group()
        roles_group.add_argument(
            "--set-roles",
            metavar="<roles>",
            type=roles_parser,
            help="A comma-separated list of user roles to set "
                 "(overwrites the current user roles)"
        )
        roles_group.add_argument(
            "--add-roles",
            metavar="<roles>",
            type=roles_parser,
            help="A comma-separated list of user roles to add"
        )
        roles_group.add_argument(
            "--del-roles",
            metavar="<roles>",
            type=roles_parser,
            help="A comma separated list of user roles to remove"
        )
        parser.add_argument(
            "--password",
            action="store_true",
            help="Request the password from stdin.",
        )


class ListUser(Lister):
    _description = "List all admin panel users."
    _default_fields = ['id', 'name', 'is_enabled', 'is_superuser', 'roles']

    def do_action(self, parsed_args):
        users = self.app.vinfra.users.list()
        return users


class ShowUser(ShowOne):
    _description = "Show details of an admin panel user."

    def configure_parser(self, parser):
        user_arg(parser)

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.users, parsed_args.user)


class CreateUser(ShowOne):
    _description = "Add an admin panel user."

    def configure_parser(self, parser):
        _common_set_options(parser, create_command=True)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="User name",
        )

    def do_action(self, parsed_args):
        is_enabled = True
        if parsed_args.is_enabled is not None:
            is_enabled = parsed_args.is_enabled

        roles = parsed_args.roles or []

        password = get_password("New user password: ")
        return self.app.vinfra.users.create(
            parsed_args.name, password, roles, is_enabled,
            description=parsed_args.description)


class SetUser(ShowOne):
    _description = "Modify admin panel user parameters."

    def configure_parser(self, parser):
        _common_set_options(parser, create_command=False)
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the user",
        )
        user_arg(parser)

    def do_action(self, parsed_args):
        user = find_resource(self.app.vinfra.users, parsed_args.user)

        kwargs = {}
        if parsed_args.set_roles:
            kwargs['roles'] = parsed_args.set_roles
        elif parsed_args.del_roles or parsed_args.add_roles:
            # user.roles is None for superuser
            roles = set([r['id'] for r in user.roles or []])
            roles = roles.union(set(parsed_args.add_roles or []))
            roles = roles - set(parsed_args.del_roles or [])
            kwargs['roles'] = list(roles)

        kwargs.update(
            name=parsed_args.name,
            is_enabled=parsed_args.is_enabled,
            description=parsed_args.description)

        if parsed_args.password:
            whoami = self.app.vinfra.users.get_current()
            if user.name == whoami.name:
                raise ValidationError('To change user password, use '
                                      'the change-password subcommand')
            kwargs['password'] = get_password("User password: ")

        for v in kwargs.values():
            if v is not None:
                break
        else:
            raise ValidationError('No options are specified.')

        return user.update(**kwargs)


class DeleteUser(Command):
    _description = "Remove an admin panel user."

    def configure_parser(self, parser):
        user_arg(parser)

    def do_action(self, parsed_args):
        user = find_resource(self.app.vinfra.users, parsed_args.user)
        return user.delete()


class ChangePassword(ShowOne):
    _description = "Change password of an admin panel user."

    def do_action(self, parsed_args):
        current_password = get_password("Current password: ")
        new_password = get_password("New password: ")
        if get_password("Confirm password: ") != new_password:
            raise ValidationError("Passwords do not match")

        # Use current_password for session is there is no one:
        auth = self.app.vinfra.session.auth
        if not auth.password:
            auth.password = current_password

        user = self.app.vinfra.users.change_password(current_password,
                                                     new_password)
        auth.password = new_password
        return user


class ListRoles(Lister):
    _description = "List available user roles."
    _default_fields = ['id', 'name', 'description', 'scope']

    def do_action(self, parsed_args):
        roles = self.app.vinfra.users.get_available_roles()

        def _mapper(tag):
            mapper = {
                'admin': 'system',
            }
            return mapper.get(tag, tag)

        for role in roles:
            tags = role.pop('tags', [])
            tags = [_mapper(tag) for tag in tags]
            role['scope'] = tags

        return roles
