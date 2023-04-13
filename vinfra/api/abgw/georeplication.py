import sys

from vinfra.api import base


class GeoReplication(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw/geo-replication".format(
            base.get_id(self.cluster))
        super(GeoReplication, self).__init__(cluster.manager.api)
        self.primary = GeoReplicationPrimary(self.cluster)
        self.secondary = GeoReplicationSecondary(self.cluster)

    def get(self):
        return self.client.get(self.base_url)


class GeoReplicationPrimary(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw/geo-replication/master".format(
            base.get_id(self.cluster))
        super(GeoReplicationPrimary, self).__init__(cluster.manager.api)

    def setup(
            self,
            secondary_cluster_address,  # type: str
            secondary_datacenter_uid,  # type: str
            primary_cluster_address=None,  # type: Optional[str]
            account_server=None,  # type: Optional[str]
            username=None,  # type: Optional[str]
            password=None,  # type: Optional[str]
    ):
        return self.client.post_async(
            url="{}/set-up/".format(self.base_url),
            json={
                "slave_cluster_address": secondary_cluster_address,
                "slave_datacenter_uid": secondary_datacenter_uid,
                "master_cluster_address": primary_cluster_address,
                "account_server": account_server,
                "username": username,
                "password": password,
            }
        )

    def establish(self):
        return self.client.post_async(
            url="{}/establish/".format(self.base_url))

    def disable(self):
        return self.client.post_async(url="{}/disable/".format(self.base_url))

    def cancel(self):
        return self.client.post_async(url="{}/cancel/".format(self.base_url))

    def _get_download_primary_config_stream(self):
        return self.client.send_request_raw(
            method="get",
            url="{}/download-configs/".format(self.base_url),
            stream=True
        )

    def download_configs_to_file(self, dc_config_file_path):
        with open(dc_config_file_path, 'wb') as dc_config_file_obj:
            for chunk in self._get_download_primary_config_stream():
                dc_config_file_obj.write(chunk)

    def download_configs_to_stdout(self):
        for chunk in self._get_download_primary_config_stream():
            sys.stdout.write(chunk)


class GeoReplicationSecondary(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw/geo-replication/slave".format(
            base.get_id(self.cluster))
        super(GeoReplicationSecondary, self).__init__(cluster.manager.api)

    def setup(self, dc_config_file):
        return self.client.post_async(
            url="{}/set-up/".format(self.base_url),
            data=dc_config_file,
            headers={
                'Content-Type': 'application/octet-stream',
            }
        )

    def promote_to_primary(self):
        return self.client.post_async(
            url="{}/promote-to-master/".format(self.base_url))

    def cancel(self):
        return self.client.post_async(url="{}/cancel/".format(self.base_url))
