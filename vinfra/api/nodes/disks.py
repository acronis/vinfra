from vinfra.api import base


class Disk(base.Resource):
    NAME_ATTR = 'device'

    def assign_async(self, *args, **kwargs):
        return self.manager.assign_async(self, *args, **kwargs)

    def assign(self, *args, **kwargs):
        return self.manager.assign(self, *args, **kwargs)

    def release(self, *args, **kwargs):
        return self.manager.release(self, *args, **kwargs)

    def release_async(self, *args, **kwargs):
        return self.manager.release_async(self, *args, **kwargs)

    def recover(self):
        return self.manager.recover(self)

    def blink_start(self):
        return self.manager.blink_start(self)

    def blink_stop(self):
        return self.manager.blink_stop(self)


class DiskManager(base.Manager):
    resource_class = Disk

    def __init__(self, api, node):
        super(DiskManager, self).__init__(api)
        self.node_id = base.get_id(node)

    def list(self):
        return self._list("/nodes/{}/disks".format(self.node_id))

    def get(self, disk):
        disk_id = base.get_id(disk)
        return self._get("/nodes/{}/disks/{}".format(self.node_id, disk_id))

    def assign_async(self, disk, role, service_params=None, cluster=None):
        disk_id = base.get_id(disk)

        data = {'id': disk_id, 'role': role}
        if service_params:
            data['service_params'] = service_params

        return self.assign_bulk_async([data], cluster=cluster)

    @base.async_wait
    def assign(self, disk, role, **kwargs):
        return self.assign_async(disk, role, **kwargs)

    def assign_bulk_async(self, disks, cluster=None):
        # disks: [{'id': uuid, 'role': role, 'service_params': data}]
        if cluster is None:
            cluster = self.api.get_cluster()
        cluster_id = base.get_id(cluster)

        json = {'disks': disks}
        url = "/{}/nodes/{}/disks".format(cluster_id, self.node_id)
        return self.client.post_async(url, json=json)

    @base.async_wait
    def assign_bulk(self, disks, **kwargs):
        return self.assign_bulk_async(disks, **kwargs)

    def release_async(self, disk, force=None, cluster=None):
        return self.release_bulk_async([disk], force, cluster)

    @base.async_wait
    def release(self, disk, **kwargs):
        return self.release_async(disk, **kwargs)

    def release_bulk_async(self, disks, force=False, cluster=None):
        if cluster is None:
            cluster = self.api.get_cluster()

        cluster_id = base.get_id(cluster)
        disk_ids = [base.get_id(disk) for disk in disks]

        json = {'disks': disk_ids}
        if force is not None:
            json['force'] = force

        url = "/{}/nodes/{}/disks/release".format(cluster_id, self.node_id)
        return self.client.post_async(url, json=json)

    @base.async_wait
    def release_bulk(self, disks, **kwargs):
        return self.release_bulk_async(disks, **kwargs)

    def recover(self, disk, cluster=None):
        disk_id = base.get_id(disk)
        if cluster is None:
            cluster = self.api.get_cluster()
        cluster_id = base.get_id(cluster)
        url = "/{}/nodes/{}/disks/{}/recover/".format(cluster_id, self.node_id,
                                                      disk_id)
        return self._post(url)

    def make_disks_available_roles(self, disks_to_assign, disks=None):
        json = {
            "node_id": self.node_id,
            "disks_to_assign": disks_to_assign
        }
        if disks is not None:
            json['disks'] = disks

        url = "/nodes/{}/disks/make_disks_available_roles".format(self.node_id)
        return self.client.post(url, json=json)

    def blink_start(self, disk):
        disk_id = base.get_id(disk)
        url = "/nodes/{}/disks/{}/blink".format(self.node_id, disk_id)
        return self.client.post(url)

    def blink_stop(self, disk):
        disk_id = base.get_id(disk)
        url = "/nodes/{}/disks/{}/blink_stop".format(self.node_id, disk_id)
        return self.client.post(url)

    def get_diagnostic_info(self, disk):
        disk_id = base.get_id(disk)
        url = "/nodes/{}/disks/{}/diagnostic-info/".format(self.node_id, disk_id)
        return self.client.get(url)
