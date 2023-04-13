from vinfra.api import base
from vinfra.api.iscsi.luns import LunManager
from vinfra.utils import flatten_args


class Target(base.Resource):
    ID_ATTR = 'iqn'

    def __init__(self, manager, info):
        super(Target, self).__init__(manager, info)
        self.luns_manager = LunManager(
            self.manager.api, self.manager.cluster_id, self)


class TargetManager(base.Manager):
    resource_class = Target

    def __init__(self, api, cluster):
        super(TargetManager, self).__init__(api)
        self.cluster_id = base.get_id(cluster)

    @property
    def base_url(self):
        return "/{}/iscsi/targets".format(self.cluster_id)

    def target_url(self, target):
        iqn = base.get_id(target)
        return "{}/{}".format(self.base_url, iqn)

    def list(self):
        return self._list(self.base_url)

    def get(self, target):
        return self._get(self.target_url(target))

    def create(self, name, node_id, portals, owner=None, mut_owner=None,
               limits=None):
        node_id = base.get_id(node_id)
        json = dict(name=name, node_id=node_id, portals=portals)
        json.update(flatten_args(
            owner=owner,
            mut_owner=mut_owner,
            limits=limits,
        ))
        return self._post(self.base_url, json=json)

    def delete(self, target):
        return self.client.delete(self.target_url(target))

    def update(self, target, portals=None, owner=None, mut_owner=None,
               force=None, limits=None):
        url = self.target_url(target)
        json = flatten_args(
            portals=portals,
            owner=owner,
            mut_owner=mut_owner,
            force=force,
            limits=limits,
        )
        return self._put(url, json=json)

    def start(self, target):
        url = "%s/start" % self.target_url(target)
        return self._post(url)

    def stop(self, target, force=None):
        json = flatten_args(force=force)
        url = "%s/stop" % self.target_url(target)
        return self._post(url, json=json)

    def initiators(self, target):
        url = "%s/initiators" % self.target_url(target)
        return self.client.get(url)

    def refresh(self):
        url = "%s/iscsi/refresh" % self.cluster_id
        return self.client.post(url)
