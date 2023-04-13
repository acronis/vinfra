from vinfra.api import base


class SshKey(base.Resource):
    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self):
        return self.manager.delete(self)


class SshKeyManager(base.Manager):
    resource_class = SshKey

    def __init__(self, cluster):
        self.cluster = cluster
        super(SshKeyManager, self).__init__(cluster.manager.api)

    @property
    def base_url(self):
        return "/{}/ssh-keys".format(base.get_id(self.cluster))

    def list(self):
        return self._list(self.base_url)

    def get(self, ssh_key):
        ssh_key_id = base.get_id(ssh_key)
        return self._get("{}/{}".format(self.base_url, ssh_key_id))

    def create_async(self, key):
        return self._post_async(self.base_url, json={'key': key})

    @base.async_wait
    def create(self, key):
        return self.create_async(key)

    def delete_async(self, ssh_key):
        ssh_key_id = base.get_id(ssh_key)
        return self._delete_async("{}/{}".format(self.base_url, ssh_key_id))

    @base.async_wait
    def delete(self, ssh_key):
        return self.delete_async(ssh_key)
