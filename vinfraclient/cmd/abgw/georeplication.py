import os

from vinfraclient import exceptions
from vinfraclient.cmd.abgw import get_reg_password, ensure_abgw_exists
from vinfraclient.cmd.base import TaskCommand, ShowOne
from vinfraclient.utils import get_cluster, get_stream


class ShowGeoReplicationInfo(ShowOne):
    _description = "Display geo-replication configuration."

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.get()


class GeoReplicationPrimarySetup(TaskCommand):
    _description = "Configure geo-replication for the primary cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--primary-cluster-address",
            required=True, help="Primary cluster address."
        )
        parser.add_argument(
            "--secondary-cluster-address",
            required=True, help="Secondary cluster address."
        )
        parser.add_argument(
            "--secondary-cluster-uid",
            required=True, help="Secondary cluster UID"
        )
        parser.add_argument(
            "--account-server",
            required=True,
            help=(
                "URL of the cloud management portal or the hostname/IP "
                "address and port of the local management server."
            )
        )
        parser.add_argument(
            "--username",
            required=True,
            help=(
                "Partner account in the cloud or of an organization "
                "administrator on the local management server."
            )
        )
        parser.add_argument(
            "--stdin",
            action="store_true",
            help="Use for setting registration password from stdin"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.primary.setup(
            secondary_cluster_address=parsed_args.secondary_cluster_address,
            secondary_datacenter_uid=parsed_args.secondary_cluster_uid,
            primary_cluster_address=parsed_args.primary_cluster_address,
            account_server=parsed_args.account_server,
            username=parsed_args.username,
            password=get_reg_password(parsed_args),
        )


class GeoReplicationPrimaryDownloadConfigs(ShowOne):
    _description = (
        "Download the geo-replication configuration file of the primary cluster."
    )

    def configure_parser(self, parser):
        parser.add_argument(
            "--conf-file-path",
            dest="dc_config_file_path",
            metavar="<conf-file-path>",
            help=(
                "Path where the configuration file will be downloaded."
            )
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        if parsed_args.dc_config_file_path:
            if os.path.exists(parsed_args.dc_config_file_path):
                raise exceptions.ValidationError(
                    "Path already exists. Provide another path or the "
                    "existing file will be overwritten."
                )
            if os.path.isdir(parsed_args.dc_config_file_path):
                raise exceptions.ValidationError(
                    "The provided path is a directory. "
                    "Specify a file to download."
                )
            cluster.abgw.geo_replication.primary.download_configs_to_file(
                dc_config_file_path=parsed_args.dc_config_file_path
            )
        else:
            cluster.abgw.geo_replication.primary.download_configs_to_stdout()


class GeoReplicationPrimaryEstablish(TaskCommand):
    _description = (
        "Establish a connection between the primary and secondary "
        "clusters to enable geo-replication."
    )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.primary.establish()


class GeoReplicationPrimaryDisable(TaskCommand):
    _description = "Disable geo-replication on the primary cluster."

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.primary.disable()


class GeoReplicationPrimaryCancel(TaskCommand):
    _description = "Cancel geo-replication for the primary cluster."

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.primary.cancel()


class GeoReplicationSecondarySetup(TaskCommand):
    _description = "Configure geo-replication for the secondary cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--dc-config-file",
            required=True,
            help="Path to the configuration file of the primary cluster."
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.secondary.setup(
            dc_config_file=get_stream(parsed_args.dc_config_file)
        )


class GeoReplicationSecondaryPromoteToPrimary(TaskCommand):
    _description = (
        "Promote the secondary cluster to primary "
        "in the geo-replication configuration."
    )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.secondary.promote_to_primary()


class GeoReplicationSecondaryCancel(TaskCommand):
    _description = "Cancel geo-replication for the secondary cluster."

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.secondary.cancel()


class GeoReplicationMasterSetup(TaskCommand):
    """Not functional in 5.1.0 and newer versions.
    Presented for internal usage only."""

    _description = "Configure geo-replication for the primary cluster (deprecated)."

    def configure_parser(self, parser):
        parser.add_argument(
            "--slave-cluster-address",
            required=True, help="Slave cluster address."
        )
        parser.add_argument(
            "--slave-cluster-uid",
            required=True, help="Slave cluster UID"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        ensure_abgw_exists(cluster)
        return cluster.abgw.geo_replication.primary.setup(
            secondary_cluster_address=parsed_args.slave_cluster_address,
            secondary_datacenter_uid=parsed_args.slave_cluster_uid
        )
