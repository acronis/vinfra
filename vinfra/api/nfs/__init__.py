from vinfra.api import base

from vinfra.api.nfs.exports import ExportManager
from vinfra.api.nfs.nodes import NodeManager
from vinfra.api.nfs.shares import ShareManager


class NfsManager(base.Manager):

    @property
    def base_url(self):
        return "/{}/nfs".format(base.get_id(self.cluster))

    def __init__(self, cluster):
        self.cluster = cluster
        super(NfsManager, self).__init__(cluster.manager.api)
        self.node = NodeManager(cluster)
        self.share = ShareManager(cluster)
        self.export = ExportManager(cluster)

    def create_async(self, nodes):
        return self.node.assign_async(nodes)

    def delete_async(self, nodes):
        return self.node.release_async(nodes)

    def get_kerberos_settings(self):
        url = "{}/auth/krb-settings".format(self.base_url)
        return self.client.get(url)

    def set_kerberos_settings(
            self,
            realm,  # type: str
            kdc_service,  # type: str
            kdc_admin_service,  # type: str
    ):
        data = {
            'realm': realm,
            'kdc_service': kdc_service,
            'kdc_admin_service': kdc_admin_service,
        }
        url = "{}/auth/krb-settings".format(self.base_url)
        return self.client.post(url, json=data)
