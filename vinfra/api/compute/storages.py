from vinfra.api import base
from vinfra.utils import flatten_args


class ComputeStorage(base.Resource):
    ID_ATTR = 'name'

    def delete_async(self):
        return self.manager.delete_async(self)

    def update_async(self, **kwargs):
        return self.manager.update_async(self, **kwargs)


class ComputeStorageManager(base.Manager):
    resource_class = ComputeStorage

    @property
    def base_url(self):
        return "/compute/cluster/storages/"

    def list(self):
        return self._list(self.base_url)

    def create_async(self, **kwargs):
        return self.client.post_async(
            self.base_url, json=flatten_args(**kwargs))

    def delete_async(self, compute_storage):
        compute_storage_id = base.get_id(compute_storage)
        url = "{}{}/".format(self.base_url, compute_storage_id)
        return self.client.delete_async(url)

    def update_async(self, compute_storage, **kwargs):
        compute_storage_id = base.get_id(compute_storage)
        url = "{}{}/".format(self.base_url, compute_storage_id)
        return self.client.patch_async(url, json=flatten_args(**kwargs))
