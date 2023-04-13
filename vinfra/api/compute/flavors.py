from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra.utils import flatten_args


class Flavor(base.Resource):
    def __init__(self, manager, info):
        if 'traits' in info:
            info['placements'] = info.pop('traits')
        super(Flavor, self).__init__(manager, info)

    def delete(self):
        return self.manager.delete(self)


class FlavorManager(Manager):
    resource_class = Flavor
    base_url = "/compute/flavors"

    def list(self, filters=None):
        return self._list(self.base_url, filters=filters)

    def get(self, flavor):
        flavor_id = base.get_id(flavor)
        return self._get("{}/{}".format(self.base_url, flavor_id))

    def create(self, name, vcpus, ram, swap=None):
        json = dict(
            name=name,
            vcpus=vcpus,
            ram=ram
        )
        json.update(flatten_args(swap=swap))
        return self._post(self.base_url, json)

    def delete(self, flavor):
        flavor_id = base.get_id(flavor)
        return self._delete("{}/{}".format(self.base_url, flavor_id))
