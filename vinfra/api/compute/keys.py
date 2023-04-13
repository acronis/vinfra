from vinfra.api import base
from vinfra.api.compute.base import Manager


class ComputeSshKey(base.Resource):
    ID_ATTR = "name"

    def delete(self):
        return self.manager.delete(self)


class ComputeSshKeyManager(Manager):
    resource_class = ComputeSshKey
    base_url = "/compute/keys"

    def list(self):
        return self._list(self.base_url)

    def get(self, key):
        key_name = base.get_id(key)
        return self._get("{}/{}".format(self.base_url, key_name))

    def create(self, name, public_key, description=None):
        json = dict(
            name=name,
            public_key=public_key,
        )

        if description:
            json['description'] = description

        return self._post(self.base_url, json)

    def delete(self, key):
        key_name = base.get_id(key)
        return self._delete("{}/{}".format(self.base_url, key_name))
