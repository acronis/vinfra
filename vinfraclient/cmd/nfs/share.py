from vinfraclient import argtypes, exceptions
from vinfraclient.cmd.base import ShowOne, flatten_args, Lister, TaskCommand
from vinfraclient.cmd.nfs import _force_option
from vinfraclient.cmd.compute.storage_policy import storage_policy_options
from vinfraclient.utils import find_resource, get_size_in_bytes, get_stream


def _share_name_option(parser):
    parser.add_argument(
        'name',
        help='NFS share name'
    )


def _share_size_option(parser, required=True):
    parser.add_argument(
        '--size',
        metavar='<size>',
        type=get_size_in_bytes,
        required=required,
        help=(
            'NFS share size, in bytes. You can also specify '
            'the following units: KiB for kibibytes, MiB for mebibytes, '
            'GiB for gibibytes, TiB for tebibytes, and PiB for pebibytes.'
        )
    )


def _share_keytab_option(parser, required=True):
    parser.add_argument(
        '--krb-keytab',
        metavar='<krb-keytab>',
        dest='krb_keytab',
        required=required,
        help='Kerberos keytab file'
    )


def _share_krb_auth_option(parser, required=True):
    parser.add_argument(
        '--krb-auth',
        metavar='<krb-auth>',
        dest='krb_auth_enabled',
        type=argtypes.boolean,
        required=required,
        help="Whether or not Kerberos authentication is enabled"
             " ('true' or 'false')."
    )


class CreateShare(TaskCommand):
    _description = 'Create an NFS share.'

    def configure_parser(self, parser):
        _share_name_option(parser)
        parser.add_argument(
            '--node',
            metavar='<node>',
            required=True,
            help='Node ID'
        )
        parser.add_argument(
            '--ip-address',
            metavar='<ip_address>',
            dest='ip_address',
            required=True,
            help='IP address of the NFS share'
        )
        _share_size_option(parser)
        storage_policy_options(parser, required=True)
        _share_keytab_option(parser, required=False)

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        node = find_resource(cluster.nfs.node, parsed_args.node)
        if not node:
            raise exceptions.ValidationError(
                "Invalid argument for the option '--node'")

        args = [
            parsed_args.name,
            parsed_args.ip_address,
            node,
            parsed_args.size,
            parsed_args.failure_domain,
            parsed_args.tier,
            parsed_args.redundancy,
        ]
        krb_keytab_stream = None
        if parsed_args.krb_keytab:
            krb_keytab_stream = get_stream(parsed_args.krb_keytab)

        share = cluster.nfs.share.create_async(
            *args, krb_keytab=krb_keytab_stream)
        return share


class DeleteShare(TaskCommand):
    _description = 'Delete an NFS share.'

    def configure_parser(self, parser):
        _share_name_option(parser)

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        return cluster.nfs.share.delete_async(parsed_args.name)


class ListShare(Lister):
    _description = 'List NFS shares.'
    _default_fields = ['name', 'ip_address', 'node']

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        data = cluster.nfs.share.list()
        return data


class ShowShareInfo(ShowOne):
    _description = 'Show details of an NFS share.'

    def configure_parser(self, parser):
        _share_name_option(parser)

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        return cluster.nfs.share.get(parsed_args.name)


class SetShare(TaskCommand):
    _description = 'Modify an NFS share.'

    def configure_parser(self, parser):
        storage_policy_options(parser, required=False)
        _share_size_option(parser, required=False)
        _share_keytab_option(parser, required=False)
        _share_krb_auth_option(parser, required=False)
        _share_name_option(parser)
        parser.add_argument(
            '--ip-address',
            metavar='<ip_address>',
            dest='ip_address',
            help='IP address of the NFS share'
        )

    def do_action(self, parsed_args):
        args = (parsed_args.name, )
        kwargs_names = [
            'size', 'failure_domain', 'tier', 'redundancy',
            'krb_keytab', 'krb_auth_enabled', 'ip_address'
        ]
        kwargs = flatten_args(parsed_args, kwargs_names)
        cluster = self.app.vinfra.get_cluster()

        krb_keytab_stream = None
        if parsed_args.krb_keytab:
            krb_keytab_stream = get_stream(parsed_args.krb_keytab)

        return cluster.nfs.share.update_async(
            *args, krb_keytab=krb_keytab_stream, **kwargs)


class StartShare(TaskCommand):
    _description = 'Start an NFS share.'

    def configure_parser(self, parser):
        _share_name_option(parser)

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        return cluster.nfs.share.start_async(parsed_args.name)


class StopShare(TaskCommand):
    _description = 'Stop an NFS share.'

    def configure_parser(self, parser):
        _force_option(parser, 'Stop the NFS share forcibly.')
        _share_name_option(parser)

    def do_action(self, parsed_args):
        kwargs = flatten_args(parsed_args, ['force'])
        cluster = self.app.vinfra.get_cluster()
        return cluster.nfs.share.stop_async(parsed_args.name, **kwargs)
