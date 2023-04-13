from vinfraclient import exceptions
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import TaskCommand, ShowOne, Lister
from vinfraclient.cmd.compute.storage_policy import storage_policy_options
from vinfraclient.exceptions import CommandError
from vinfraclient.utils import \
    find_resource, find_resources, get_cluster, get_password


class ShowS3(ShowOne):
    _description = "Show S3 cluster configuration."

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.s3.get()


class CreateCluster(TaskCommand):
    _description = "Create the S3 cluster."

    def configure_parser(self, parser):
        storage_policy_options(parser, required=False, use_defaults=True)

        ssl_group = parser.add_mutually_exclusive_group()
        ssl_group.add_argument(
            "--self-signed",
            action="store_true",
            default=True,
            help="Generate a new self-signed certificate (default)."
        )
        ssl_group.add_argument(
            "--no-ssl",
            dest='self_signed',
            action="store_false",
            help="Do not generate a self-signed certificate."
        )
        ssl_group.add_argument(
            "--cert-file",
            help="Path to a file with the new certificate."
        )

        parser.add_argument(
            "--insecure",
            action="store_true",
            help="Allow insecure connections in addition to secure ones (only "
                 "used with the --cert-file and --self-signed options)."
        )
        parser.add_argument(
            "--key-file",
            help="Path to a file with the private key (only used with the "
                 "--cert-file option)."
        )
        parser.add_argument(
            "--password",
            action="store_true",
            help="Read certificate password from stdin (only used with the "
                 "--cert-file option).",
        )

        parser.add_argument(
            "--np-uri",
            metavar="<np-uri>",
            help="Notary provider address (only used with --cert-file or "
                 "--self-signed and --np-user-key option).",
        )
        parser.add_argument(
            "--np-user-key",
            metavar="<np-user-key>",
            help="Notary user key (only used with --np-uri option).",
        )

        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            required=True,
            help="A comma-separated list of node hostnames or IDs"
        )
        parser.add_argument(
            "--s3gw-domain",
            metavar="<domain>",
            required=True,
            help="DNS name S3 endpoint"
        )
        parser.add_argument(
            "--os-count",
            dest="os_count",
            action="store",
            type=int,
            default=None,
            help="Amount of OS services in S3 cluster."
        )
        parser.add_argument(
            "--ns-count",
            dest="ns_count",
            action="store",
            type=int,
            default=None,
            help="Amount of NS services in S3 cluster."
        )
        parser.add_argument(
            "--force",
            dest="ignore_ram_reservation",
            action="store_true",
            default=None,
            help="Skip checks for minimal hardware requirements."
        )

    @staticmethod
    def _get_stream(file_name):
        try:
            return open(file_name, mode='rb')
        except Exception as err:
            raise exceptions.ValidationError(
                'Failed to open "{}" ({}).'.format(file_name, err))

    def do_action(self, parsed_args):
        if parsed_args.key_file and not parsed_args.cert_file:
            raise exceptions.ValidationError(
                "The --key-file option can only be used with the --cert-file "
                "option.")
        if parsed_args.password and not parsed_args.cert_file:
            raise exceptions.ValidationError(
                "The --password option can only be used with the --cert-file "
                "option.")
        if parsed_args.np_uri or parsed_args.np_user_key:
            if not (parsed_args.np_uri and parsed_args.np_user_key):
                raise exceptions.ValidationError(
                    "The --np-uri and --np-user-key options must used together."
                )
            if not (parsed_args.cert_file or parsed_args.self_signed):
                raise ValueError(
                    "The --np-uri option can only be used with --cert-file or"
                    " --self-signed options."
                )

        cluster = get_cluster(self.app.vinfra)
        nodes = [find_resource(self.app.vinfra.nodes, node)
                 for node in parsed_args.nodes]

        gen_cert = cert_stream = key_stream = password = None
        if parsed_args.cert_file:
            cert_stream = self._get_stream(parsed_args.cert_file)

            if parsed_args.key_file:
                key_stream = self._get_stream(parsed_args.key_file)

            if parsed_args.password:
                password = get_password("Certificate password: ")
                if not password:
                    raise exceptions.ValidationError(
                        "Password cannot be empty.")

        elif parsed_args.self_signed:
            gen_cert = True

        notary_provider = None
        if parsed_args.np_uri:
            notary_provider = {
                "uri": parsed_args.np_uri,
                "key": parsed_args.np_user_key,
            }

        return cluster.s3.create_async(
            nodes, parsed_args.s3gw_domain, parsed_args.tier,
            parsed_args.redundancy, parsed_args.failure_domain,
            gen_cert=gen_cert, cert=cert_stream, key=key_stream,
            password=password, insecure=parsed_args.insecure,
            notary_provider=notary_provider,
            n_os=parsed_args.os_count,
            n_ns=parsed_args.ns_count,
            ignore_ram_reservation=parsed_args.ignore_ram_reservation,
        )


class DeleteCluster(TaskCommand):
    _description = "Delete the S3 cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forcibly delete the S3 cluster."
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        # Note(akurbatov): there is no a separate API to delete s3 cluster.
        # Do it using additional API call to get all s3 nodes:
        s3_cluster_info = cluster.s3.get()
        if not parsed_args.force and s3_cluster_info['nusers']:
            raise exceptions.CommandError(
                "The S3 cluster has users which may have data. "
                "If you are completely sure that you want to delete the S3 "
                "cluster along with the users and their data, use the "
                "'--force' parameter. Otherwise relocate user data and "
                "remove the users before deleting the S3 cluster."
            )
        nodes = [find_resource(self.app.vinfra.nodes, node['id'])
                 for node in s3_cluster_info['nodes']]
        return cluster.s3.release_nodes_async(nodes)


class AddNode(TaskCommand):
    _description = "Add one or more nodes to the S3 cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            required=True,
            help="A comma-separated list of node hostnames or IDs"
        )
        parser.add_argument(
            "--force",
            dest="ignore_ram_reservation",
            action="store_true",
            default=None,
            help="Skip checks for minimal hardware requirements."
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        nodes = [find_resource(self.app.vinfra.nodes, node)
                 for node in parsed_args.nodes]
        return cluster.s3.assign_nodes_async(nodes, parsed_args.ignore_ram_reservation)


class ReleaseNode(TaskCommand):
    _description = "Release one or more nodes from the S3 cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            required=True,
            help="A comma-separated list of node hostnames or IDs"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        s3_cluster_info = cluster.s3.get()

        s3_nodes = [
            n.id for n in find_resources(self.app.vinfra.nodes, [
                n_['id'] for n_ in s3_cluster_info['nodes']
            ])
        ]

        nodes = [
            n.id for n in find_resources(
                self.app.vinfra.nodes, parsed_args.nodes)
        ]

        if sorted(s3_nodes) == sorted(nodes):
            raise exceptions.CommandError(
                "To release all nodes from the S3 cluster "
                "(and thus delete the S3 cluster itself), "
                "use the '(vinfra) service s3 cluster delete' command."
            )

        return cluster.s3.release_nodes_async(nodes)


class ShowS3GeoReplication(ShowOne):
    _description = "Show details about registered site for S3 geo-replication or self site."

    def configure_parser(self, parser):
        parser.add_argument(
            "--id",
            metavar="<site_id>",
            help="S3 site UID"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        if parsed_args.id:
            rv = cluster.s3.replication.geo_replication_show_site(parsed_args.id)
        else:
            rv = cluster.s3.replication.geo_replication_show_self()
        return rv


class ListS3GeoReplication(Lister):
    _description = "List registered site for S3 geo-replication."
    _default_fields = ['uid', 'readable_name', 'url', 'is_self', 'user_key_id', 'user_secret_key']

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.s3.replication.geo_replication_list()


class ShowTokenS3GeoReplication(ShowOne):
    _description = "Get S3 geo-replication token."

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.s3.replication.get_replication_token()


class AddS3GeoReplication(TaskCommand):
    _description = "Add S3 geo-replication site."

    def configure_parser(self, parser):
        parser.add_argument(
            "--token",
            metavar="<site_token>",
            required=True,
            help="Remote S3 site token"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        return cluster.s3.replication.get_replication_add_site(parsed_args.token)


class DeleteS3GeoReplication(TaskCommand):
    _description = "Delete S3 geo-replication site by id."

    def configure_parser(self, parser):
        parser.add_argument(
            "--id",
            metavar="<site_id>",
            required=True,
            help="S3 site UID"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        self_cluster = cluster.s3.replication.geo_replication_show_self()
        if self_cluster['uid'] == parsed_args.id:
            raise CommandError("Can't delete self cluster from configuration.")
        return cluster.s3.replication.get_replication_delete_site(parsed_args.id)


class ChangeCluster(TaskCommand):

    _description = "Change the S3 cluster."

    def configure_parser(self, parser):
        storage_policy_options(parser, required=False, use_defaults=False)
        ssl_group = parser.add_mutually_exclusive_group()
        ssl_group.add_argument(
            "--self-signed",
            action="store_true",
            help="Generate a new self-signed certificate (default).",
            default=None
        )
        ssl_group.add_argument(
            "--no-ssl",
            dest='self_signed',
            action="store_false",
            help="Do not generate a self-signed certificate.",
            default=None
        )
        ssl_group.add_argument(
            "--cert-file",
            help="Path to a file with the new certificate.",
            default=None
        )
        parser.add_argument(
            "--insecure",
            action="store_true",
            help="Allow insecure connections in addition to secure ones (only "
                 "used with the --cert-file and --self-signed options).",
            default=None
        )
        parser.add_argument(
            "--key-file",
            help="Path to a file with the private key (only used with the "
                 "--cert-file option).",
            default=None
        )
        parser.add_argument(
            "--password",
            action="store_true",
            help="Read certificate password from stdin (only used with the "
                 "--cert-file option).",
            default=None
        )
        parser.add_argument(
            "--np-uri",
            metavar="<np-uri>",
            help="Notary provider address (only used with --cert-file or "
                 "--self-signed and --np-user-key option).",
            default=None
        )
        parser.add_argument(
            "--np-user-key",
            metavar="<np-user-key>",
            help="Notary user key (only used with --np-uri option).",
            default=None
        )

    @staticmethod
    def _get_stream(file_name):
        try:
            return open(file_name, mode='rb')
        except Exception as err:
            raise exceptions.ValidationError(
                'Failed to open "{}" ({}).'.format(file_name, err))

    def do_action(self, parsed_args):
        if all(parsed_arg is None for parsed_arg in (
                parsed_args.failure_domain, parsed_args.tier, parsed_args.redundancy,
                parsed_args.self_signed, parsed_args.insecure,
                parsed_args.key_file, parsed_args.cert_file, parsed_args.password,
                parsed_args.np_uri, parsed_args.np_user_key,
        )):
            raise exceptions.ValidationError('Nothing to change. Parameters are empty.')
        if parsed_args.key_file and not parsed_args.cert_file:
            raise exceptions.ValidationError(
                "The --key-file option can only be used with the --cert-file "
                "option.")
        if parsed_args.password and not parsed_args.cert_file:
            raise exceptions.ValidationError(
                "The --password option can only be used with the --cert-file "
                "option.")
        gen_cert = cert_stream = key_stream = password = None
        if parsed_args.cert_file:
            cert_stream = self._get_stream(parsed_args.cert_file)

            if parsed_args.key_file:
                key_stream = self._get_stream(parsed_args.key_file)

            if parsed_args.password:
                password = get_password("Certificate password: ")
                if not password:
                    raise exceptions.ValidationError(
                        "Password cannot be empty.")
        elif parsed_args.self_signed:
            gen_cert = True
        notary_provider = None
        if parsed_args.np_uri:
            notary_provider = {
                "uri": parsed_args.np_uri,
                "key": parsed_args.np_user_key,
            }
        cluster = get_cluster(self.app.vinfra)
        return cluster.s3.change(
            failure_domain=parsed_args.failure_domain,
            tier=parsed_args.tier,
            redundancy=parsed_args.redundancy,
            gen_cert=gen_cert, cert=cert_stream, key=key_stream,
            password=password, insecure=parsed_args.insecure,
            notary_provider=notary_provider
        )
