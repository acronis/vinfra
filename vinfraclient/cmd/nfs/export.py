from vinfra.api.nfs.exports import Client
from vinfraclient import exceptions, argtypes
from vinfraclient.argtypes import (parse_list_options, ValueType, ChoicesType,
                                   MultiChoicesType)
from vinfraclient.cmd.base import ShowOne, flatten_args, Lister, TaskCommand


def _share_name_option(parser):
    parser.add_argument(
        metavar='<share-name>',
        dest='share_name',
        help='NFS share name',
    )


def _export_name_option(parser):
    parser.add_argument(
        metavar='<export-name>',
        dest='export_name',
        help='NFS export name',
    )


class ClientType(ValueType):
    def __init__(self, access_types, security_types):
        self._access_types = ChoicesType(access_types)
        self._security_types = MultiChoicesType(security_types)

    def __call__(self, value):
        try:
            addr, access, security = value.split(':')
        except ValueError:
            raise exceptions.ValidationError(
                "Wrong format of the '--client' argument")
        return Client(
            addresses=parse_list_options(addr),
            access_type=self._access_types(access),
            security_types=self._security_types(security),
        )


def _export_common_option(parser, required=True):
    access_type = ['none', 'rw', 'ro']
    security_type = ['none', 'sys', 'krb5', 'krb5i', 'krb5p']
    squash = ['root_squash', 'root_id_squash', 'all_squash', 'none']

    parser.add_argument(
        '--path',
        metavar='<path>',
        required=required,
        help='Path to the NFS export',
    )
    parser.add_argument(
        '--access-type',
        metavar='<access-type>',
        dest='access_type',
        choices=access_type,
        required=required,
        help='Type of access to the NFS export (one of {!r})'.format(
            access_type),
    )
    parser.add_argument(
        '--security-types',
        metavar='<security-types>',
        dest='security_types',
        type=argtypes.MultiChoicesType(security_type),
        required=required,
        help='Types of NFS export security (one of {!r})'.format(security_type),
    )
    parser.add_argument(
        '--client',
        metavar='<address=ip_addresses:access=access_type:security='
                'security_types>',
        dest='clients',
        type=ClientType(access_type, security_type),
        action='append',
        required=False,
        help='Client access list of the NFS export',
    )
    parser.add_argument(
        '--squash',
        metavar='<squash>',
        choices=squash,
        required=False,
        help='NFS export squash (one of {!r})'.format(squash),
    )
    parser.add_argument(
        '--anonymous-gid',
        metavar='<anonymous-gid>',
        dest='anonymous_gid',
        required=False,
        help='Anonymous GID of the NFS export',
    )
    parser.add_argument(
        '--anonymous-uid',
        metavar='<anonymous-uid>',
        dest='anonymous_uid',
        required=False,
        help='Anonymous UID of the NFS export',
    )


class CreateExport(TaskCommand):
    _description = 'Create a new NFS export.'

    def configure_parser(self, parser):
        _share_name_option(parser)
        _export_name_option(parser)
        _export_common_option(parser)

    def do_action(self, parsed_args):
        args = [
            parsed_args.share_name,
            parsed_args.export_name,
            parsed_args.path,
            parsed_args.access_type,
            parsed_args.security_types,
        ]
        kwargs = flatten_args(
            parsed_args,
            ['clients', 'squash', 'anonymous_gid', 'anonymous_uid'])

        cluster = self.app.vinfra.get_cluster()
        export = cluster.nfs.export.create_async(*args, **kwargs)
        return export


class DeleteExport(TaskCommand):
    _description = 'Delete an NFS export.'

    def configure_parser(self, parser):
        _share_name_option(parser)
        _export_name_option(parser)

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        return cluster.nfs.export.delete_async(
            parsed_args.share_name, parsed_args.export_name)


class ListExport(Lister):
    _description = 'List NFS exports'
    _default_fields = ['name', 'path', 'access_type']

    def configure_parser(self, parser):
        parser.add_argument(
            '--share-name',
            metavar='<share-name>',
            dest='share_name',
            required=False,
            help='NFS share name',
        )

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        data = cluster.nfs.export.list(share_name=parsed_args.share_name)
        return data


class ShowExportInfo(ShowOne):
    _description = 'Show details of an NFS export.'

    def configure_parser(self, parser):
        _share_name_option(parser)
        _export_name_option(parser)

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        return cluster.nfs.export.get(
            parsed_args.share_name, parsed_args.export_name)


class SetExport(TaskCommand):
    _description = 'Modify an NFS export.'

    def configure_parser(self, parser):
        _share_name_option(parser)
        _export_name_option(parser)
        _export_common_option(parser, required=False)

    def do_action(self, parsed_args):
        args = (parsed_args.share_name, parsed_args.export_name)

        kwargs_names = [
            'path',
            'access_type',
            'security_types',
            'clients',
            'squash',
            'anonymous_gid',
            'anonymous_uid',
        ]
        kwargs = flatten_args(parsed_args, kwargs_names)
        cluster = self.app.vinfra.get_cluster()
        return cluster.nfs.export.update_async(*args, **kwargs)
