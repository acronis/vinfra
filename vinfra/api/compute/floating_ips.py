from vinfra.api import base
from vinfra.api.compute.base import Manager


class FloatingIp(base.Resource):
    NAME_ATTR = "floating_ip_address"

    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)


class FloatingIpManager(Manager):
    resource_class = FloatingIp
    base_url = "/compute/floating_ips"

    @staticmethod
    def _get_payload(**kwargs):
        return dict((k, v) for (k, v) in kwargs.items() if v is not None)

    def list(self, limit=None, marker=None, filters=None, sort=None):
        return self._list(self.base_url, limit=limit, marker=marker,
                          filters=filters, sort=sort)

    def get(self, floating_ip):
        fip_id = base.get_id(floating_ip)
        return self._get("{}/{}".format(self.base_url, fip_id))

    def create(self, floating_network, subnet_id=None, port_id=None,
               floating_ip_address=None, fixed_ip_address=None,
               description=None):
        data = self._get_payload(subnet_id=subnet_id, port_id=port_id,
                                 floating_ip_address=floating_ip_address,
                                 fixed_ip_address=fixed_ip_address,
                                 description=description)
        floating_network_id = base.get_id(floating_network)
        data['floating_network_id'] = floating_network_id

        return self._post(self.base_url, json=data)

    def delete(self, floating_ip):
        fip_id = base.get_id(floating_ip)
        return self._delete("{}/{}".format(self.base_url, fip_id))

    def update(self, floating_ip, port_id=None, fixed_ip_address=None,
               description=None):
        fip_id = base.get_id(floating_ip)
        data = self._get_payload(port_id=port_id,
                                 fixed_ip_address=fixed_ip_address,
                                 description=description)

        url = "{}/{}".format(self.base_url, fip_id)
        return self._patch(url, json=data)
