from vinfra.api import base


class RamReservationInfo(base.Resource):
    pass


class RamReservationInfoManager(base.Manager):
    resource_class = RamReservationInfo
    base_url = "/ram-reservation-info"

    def list(self):
        return self._list("{}/nodes".format(self.base_url))

    def get(self, node):
        node_id = base.get_id(node)
        return self._get("{}/nodes/{}".format(self.base_url, node_id))

    def get_total(self):
        return self._get("{}/total".format(self.base_url))
