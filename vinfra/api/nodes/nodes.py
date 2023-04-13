from vinfra.api import base
from vinfra.api.nodes.disks import DiskManager
from vinfra.api.nodes.ifaces import InterfaceManager
from vinfra.api.nodes.iscsi import IscsiManager
from vinfra.utils import flatten_args


class Node(base.Resource):
    NAME_ATTR = 'host'

    def __init__(self, manager, info):
        super(Node, self).__init__(manager, info)
        self.disks_manager = DiskManager(self.manager.api, self)
        self.ifaces_manager = InterfaceManager(self.manager.api, self)
        self.iscsi_manager = IscsiManager(self.manager.api, self)

    def release_async(self, force=False):
        return self.manager.release_async(self, force)

    def release(self, force=False):
        """ release node from cluster """
        return self.manager.release(self, force)

    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self):
        """ remove node from system """
        return self.manager.delete(self)

    def maintenance_start(self, **kwargs):
        return self.manager.maintenance_start(self, **kwargs)

    def maintenance_stop(self, **kwargs):
        return self.manager.maintenance_stop(self, **kwargs)

    def maintenance_precheck(self):
        return self.manager.maintenance_precheck(self)

    def maintenance_status(self):
        return self.manager.maintenance_status(self)


class NodeManager(base.Manager):
    resource_class = Node
    base_url = "/nodes"

    def list(self):
        return self._list(self.base_url)

    def get(self, node):
        node_id = base.get_id(node)
        return self._get("{}/{}".format(self.base_url, node_id))

    def release_async(self, node, force=None):
        """ release node from cluster """
        json = flatten_args(force=force)
        url = "{}/{}/release".format(self.base_url, base.get_id(node))
        return self.client.post_async(url, json=json)

    def maintenance_start(
            self, node, iscsi_mode=None, compute_mode=None,
            s3_mode=None, storage_mode=None,
            alua_mode=None, nfs_mode=None,
    ):
        data = {}
        if iscsi_mode is not None:
            data['iscsi_mode'] = iscsi_mode
        if compute_mode is not None:
            data['compute_mode'] = compute_mode
        if s3_mode is not None:
            data['s3_mode'] = s3_mode
        if storage_mode is not None:
            data['storage_mode'] = storage_mode
        if alua_mode is not None:
            data['alua_mode'] = alua_mode
        if nfs_mode is not None:
            data['nfs_mode'] = nfs_mode

        url = "{}/{}/maintenance/".format(self.base_url, base.get_id(node))
        return self.client.post_async(url, json=data)

    def maintenance_stop(self, node, ignore_compute=None):
        data = {}
        if ignore_compute:
            data['compute_mode'] = 'ignore'

        url = "{}/{}/maintenance".format(self.base_url, base.get_id(node))
        return self.client.delete_async(url, json=data)

    def maintenance_precheck(self, node):
        url = "{}/{}/maintenance/precheck".format(
            self.base_url, base.get_id(node)
        )
        return self.client.post_async(url)

    def maintenance_status(self, node):
        url = "{}/{}/maintenance".format(self.base_url, base.get_id(node))
        return self.client.get(url)

    @base.async_wait
    def release(self, node, **kwargs):
        return self.release_async(node, **kwargs)

    def delete_async(self, node):
        node_id = base.get_id(node)
        return self.client.delete_async("{}/{}".format(self.base_url, node_id))

    @base.async_wait
    def delete(self, node):
        return self.delete_async(node)

    def renew_ipsec_cert(self, node):
        url = "{}/{}/certificate/ipsec/".format(self.base_url, base.get_id(node))
        return self.client.post_async(url)
