from vinfra.api import base
from vinfra.utils import flatten_args


class Lun(base.Resource):
    ID_ATTR = 'lunno'


class LunManager(base.Manager):
    resource_class = Lun

    def __init__(self, api, cluster, target):
        super(LunManager, self).__init__(api)
        self.cluster_id = base.get_id(cluster)
        self.iqn = base.get_id(target)

    @property
    def base_url(self):
        return "/{}/iscsi/targets/{}/luns".format(self.cluster_id, self.iqn)

    def lun_url(self, lun):
        lunno = base.get_id(lun)
        return "{}/{}".format(self.base_url, lunno)

    def list(self):
        return self._list(self.base_url)

    def get(self, lun):
        return self._get(self.lun_url(lun))

    def create(self, lunno, size, tier, redundancy, failure_domain,
               description=None):
        json = dict(lunno=lunno, size=size, tier=tier, redundancy=redundancy,
                    failure_domain=failure_domain)
        json.update(flatten_args(description=description))
        return self._post(self.base_url, json=json)

    def delete(self, lun):
        return self.client.delete(self.lun_url(lun))

    def update(self, lun, size=None, tier=None, redundancy=None,
               failure_domain=None, description=None):
        url = self.lun_url(lun)
        json = flatten_args(
            size=size,
            tier=tier,
            redundancy=redundancy,
            failure_domain=failure_domain,
            description=description,
        )
        return self._put(url, json=json)

    def details(self, lun):
        url = "%s/details" % self.lun_url(lun)
        return self._get(url)

    def stats(self, lun):
        url = "%s/stats" % self.lun_url(lun)
        return self.client.get(url)
