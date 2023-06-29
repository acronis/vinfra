from vinfra.utils import flatten_args
from vinfra.api import base
from vinfra.api.abgw import AbgwApi
from vinfra.api.iscsi import Iscsi
from vinfra.api.license import VirtuozzoLicense, AcronisLicense
from vinfra.api.nfs import NfsManager
from vinfra.api.s3 import S3Api
from vinfra.api.block_storage import BlockStorageApi
from vinfra.api.sshkeys import SshKeyManager


class Cluster(base.Resource):
    def __init__(self, manager, info):
        # NOTE(akurbatov): cluster create task returns 'cluster_id'
        # instead of 'id'
        if 'cluster_id' in info:
            info['id'] = info.pop('cluster_id')
        super(Cluster, self).__init__(manager, info)

        self.acronis_license = AcronisLicense(self)
        self.virtuozzo_license = VirtuozzoLicense(self)

        self.block_storage = BlockStorageApi(self)
        self.iscsi = Iscsi(self.manager.api, self)
        self.sshkeys = SshKeyManager(self)
        self.s3 = S3Api(self)  # pylint: disable=invalid-name
        self.nfs = NfsManager(self)
        self.abgw = AbgwApi(self)

    def delete(self):
        return self.manager.delete(self)

    def join_node_async(self, node, **params):
        return self.manager.join_node_async(self, node, **params)

    def join_node(self, node, **params):
        return self.manager.join_node(self, node, **params)

    def get_settings(self):
        return self.manager.get_settings(self)

    def set_settings(self, **kwargs):
        return self.manager.set_settings(self, **kwargs)

    def overview(self):
        return self.manager.overview(self)

    def get_password(self):
        return self.manager.get_password(self)

    def set_password(self, *args):
        return self.manager.set_password(self, *args)

    def get_join_config(self, node):
        return self.manager.get_join_config(self, node)

    def set_join_config(self, node, disks):
        return self.manager.set_join_config(self, node, disks)


class ClusterManager(base.Manager):
    resource_class = Cluster

    def list(self):
        return self._list("/clusters")

    def get(self, cluster):
        cluster_id = base.get_id(cluster)
        return self._get("/clusters/{}".format(cluster_id))

    def create_async(self, node, cluster_name, disks=None, encryption=None):
        node_id = base.get_id(node)
        data = {
            'node_id': node_id,
            'cluster_name': cluster_name,
        }
        if disks is not None:
            data['disks'] = disks
        if encryption is not None:
            data['encryption'] = encryption
        return self._post_async('/clusters', json=data)

    @base.async_wait
    def create(self, node, cluster_name, **kwargs):
        return self.create_async(node, cluster_name, **kwargs)

    def join_node_async(self, cluster, node, disks=None):
        json = dict(node_id=base.get_id(node))

        if disks is not None:
            json['disks'] = disks

        url = "{}/nodes".format(base.get_id(cluster))
        return self.client.post_async(url, json=json)

    @base.async_wait
    def join_node(self, cluster, node, **params):
        return self.join_node_async(cluster, node, **params)

    def get_settings(self, cluster):
        url = "{}/settings".format(base.get_id(cluster))
        return self.client.get(url)

    def set_settings(self, cluster, encryption=None, rdma=None):
        data = {}
        if encryption is not None:
            data['encryption'] = encryption
        if rdma is not None:
            data['rdma'] = rdma

        url = "{}/settings".format(base.get_id(cluster))
        return self.client.put(url, json=data)

    def overview(self, cluster):
        cluster_id = base.get_id(cluster)
        return self.client.get('/overview/{}'.format(cluster_id))

    def get_password(self, cluster):
        cluster_id = base.get_id(cluster)
        return self.client.get('/clusters/{}/password'.format(cluster_id))

    def set_password(self, cluster, password):
        cluster_id = base.get_id(cluster)
        data = {'new_password': password}
        return self.client.put('/clusters/{}/password'.format(cluster_id),
                               json=data)

    def get_join_config(self, cluster, node):
        cluster_id = base.get_id(cluster)
        url = "{}/nodes/{}/make_join_config".format(cluster_id,
                                                    base.get_id(node))
        return self.client.get(url)

    def set_join_config(self, cluster, node, disks):
        json = flatten_args(disks=disks)
        cluster_id = base.get_id(cluster)
        url = "{}/nodes/{}/make_join_config".format(cluster_id,
                                                    base.get_id(node))
        return self.client.post(url, json=json)

    def switch_to_ipv6_async(self):
        url = "/switch-to-ipv6"
        return self.client.post_async(url)

    def reset_ipv6_async(self):
        url = "/switch-to-ipv6"
        return self.client.delete_async(url)
