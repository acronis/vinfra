from vinfra.api import base
from vinfra.api.compute.base import Manager, VinfraApi
from vinfra.consts import missing


def router_interfaces(method):
    def wrapper(manager, *args, **kwargs):
        ifaces = []

        data = method(manager, *args, **kwargs)

        ext_iface = data['external_interface']
        int_ifaces = data['internal_interfaces']

        if ext_iface:
            ext_iface['is_external'] = True
            ifaces.append(RouterInterface(manager, ext_iface))
        for int_iface in int_ifaces:
            int_iface['is_external'] = False
            ifaces.append(RouterInterface(manager, int_iface))
        return ifaces

    return wrapper


class Router(base.Resource):
    def __init__(self, manager, info):
        ext_gw_info = info['external_gateway_info']
        if ext_gw_info:
            for fip in ext_gw_info.pop('external_fixed_ips'):
                ips = ext_gw_info.setdefault('ip_addresses', [])
                ips.append(fip['ip_address'])

        super(Router, self).__init__(manager, info)
        self.interfaces = RouterInterfaceManager(manager.api, self)

    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)


class RouterInterface(base.Resource):
    def __init__(self, manager, info):
        for fip in info.pop('fixed_ips'):
            info.setdefault('ip_addresses', []).append(fip['ip_address'])
        super(RouterInterface, self).__init__(manager, info)


class RouterManager(Manager):
    resource_class = Router
    base_url = "/compute/routers"

    def list(self, limit=None, marker=None, filters=None, sort=None):
        return self._list(self.base_url, limit=limit, marker=marker,
                          filters=filters, sort=sort)

    def get(self, router):
        router_id = base.get_id(router)
        return self._get("{}/{}".format(self.base_url, router_id))

    def create(self, name, external_gateway_info=None,
               internal_interfaces=None):
        data = {'name': name}
        if external_gateway_info is not None:
            data['external_gateway_info'] = external_gateway_info
        if internal_interfaces is not None:
            data['internal_interfaces'] = internal_interfaces

        return self._post(self.base_url, json=data)

    def delete(self, router):
        router_id = base.get_id(router)
        return self._delete("{}/{}".format(self.base_url, router_id))

    def update(self, router, name=None, external_gateway_info=missing,
               routes=None):
        router_id = base.get_id(router)

        params = {}
        if name is not None:
            params['name'] = name
        # None is valid value if we need to remove external interface
        if external_gateway_info is not missing:
            params['external_gateway_info'] = external_gateway_info
        if routes is not None:
            params['routes'] = routes

        url = "{}/{}".format(self.base_url, router_id)
        return self._patch(url, json=params)


class RouterInterfaceManager(VinfraApi):
    def __init__(self, api, router):
        super(RouterInterfaceManager, self).__init__(api)
        self.router_id = base.get_id(router)
        self.base_url = "/compute/routers/{}/".format(self.router_id)

    @router_interfaces
    def list(self):
        url = "{}/{}".format(self.base_url, 'interfaces')
        return self.client.get(url)

    @router_interfaces
    def add(self, network, ip_address=None):
        params = {
            'network_id': base.get_id(network)
        }
        if ip_address is not None:
            params['ip_address'] = ip_address
        url = "{}/{}".format(self.base_url, 'add_interface')

        return self.client.put(url, json=params)

    @router_interfaces
    def remove(self, network):
        params = {
            'network_id': base.get_id(network)
        }
        url = "{}/{}".format(self.base_url, 'remove_interface')
        return self.client.put(url, json=params)
