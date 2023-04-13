from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import TaskCommand, Lister, ShowOne
from vinfraclient.cmd.compute.storage_policy import storage_policy_options
from vinfraclient.utils import find_resource, get_cluster
from vinfraclient import exceptions


def _force_option(parser, help_='Perform action forcibly.'):
    parser.add_argument(
        '--force',
        action='store_true',
        help=help_,
    )


def _node_option(parser):
    parser.add_argument(
        '--nodes',
        metavar='<node>[:<ip_address>]',
        type=parse_nodes,
        required=True,
        help='A comma-separated list of node hostnames or IDs'
    )


def parse_nodes(value):
    nodes = parse_list_options(value)
    res = []
    for node in nodes:
        host, __, address = node.partition(':')
        res.append(dict(host=host, ip_address=address))
    return res


class CreateCluster(TaskCommand):
    _description = 'Create the NFS cluster.'

    def configure_parser(self, parser):
        storage_policy_options(parser, required=False, use_defaults=True)
        _node_option(parser)

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        nodes = []
        for node_arg in parsed_args.nodes:
            nodes.append(dict(
                host=node_arg['host'],
                ip_address=node_arg['ip_address'],
                node=find_resource(self.app.vinfra.nodes, node_arg['host']),
            ))
        return cluster.nfs.create_async(nodes)


class DeleteCluster(TaskCommand):
    _description = 'Delete the NFS cluster.'

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        nodes = cluster.nfs.node.list()
        if nodes:
            return cluster.nfs.delete_async(nodes)
        raise exceptions.CommandError("The NFS cluster does not exist.")


class ListNodes(Lister):
    _description = 'List NFS cluster nodes.'
    _default_fields = ['id', 'ip_address', 'has_configd']

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        nodes = cluster.nfs.node.list()
        return nodes


class AddNode(TaskCommand):
    _description = 'Add one or more nodes to the NFS cluster.'

    def configure_parser(self, parser):
        _node_option(parser)

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        nodes = []
        for node_arg in parsed_args.nodes:
            nodes.append(dict(
                host=node_arg['host'],
                ip_address=node_arg['ip_address'],
                node=find_resource(self.app.vinfra.nodes, node_arg['host']),
            ))
        return cluster.nfs.node.assign_async(nodes)


class ReleaseNode(TaskCommand):
    _description = 'Release one or more nodes from the NFS cluster.'

    def configure_parser(self, parser):
        parser.add_argument(
            '--nodes',
            metavar='<nodes>',
            type=parse_list_options,
            required=True,
            help='A comma-separated list of node hostnames or IDs'
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        nodes = [find_resource(self.app.vinfra.nodes, node)
                 for node in parsed_args.nodes]
        return cluster.nfs.node.release_async(nodes)


class GetKrbAuthSettings(ShowOne):
    _description = "Get Kerberos authentication settings"

    def do_action(self, _parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.nfs.get_kerberos_settings()


class SetKrbAuthSettings(ShowOne):
    _description = "Set Kerberos authentication settings"

    def configure_parser(self, parser):
        parser.add_argument(
            "--realm",
            action="store",
            required=True,
            help="Realm name in uppercase letters"
        )
        parser.add_argument(
            "--kdc-service",
            action="store",
            required=True,
            help="DNS name or IP address of the KDC service"
        )
        parser.add_argument(
            "--kdc-admin-service",
            action="store",
            required=True,
            help="DNS name or IP address of the KDC administration service"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.nfs.set_kerberos_settings(
            realm=parsed_args.realm,
            kdc_service=parsed_args.kdc_service,
            kdc_admin_service=parsed_args.kdc_admin_service,
        )
