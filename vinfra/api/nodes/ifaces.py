import socket

from vinfra.api import base
from vinfra.compat import urlparse
from vinfra.consts import missing


def is_management_iface(iface_manager, iface):
    ipv4_list = iface_manager.get(iface).ipv4
    parsed = urlparse(iface_manager.api.session.url)
    management_ip = socket.gethostbyname(parsed.netloc.split(':')[0])
    for ipv4 in ipv4_list:
        if ipv4.split('/')[0] == management_ip:
            return True
    return False


class Interface(base.Resource):
    ID_ATTR = "name"

    def __init__(self, manager, info):
        if 'roles_set' in info:
            info = dict(info)
            info['network'] = info.pop('roles_set')
        super(Interface, self).__init__(manager, info)

    def update_async(self, **kwargs):
        return self.manager.update_async(self, **kwargs)

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def delete(self):
        return self.manager.delete(self)

    def delete_async(self):
        return self.manager.delete_async(self)

    def down(self):
        return self.manager.down(self)

    def down_async(self):
        return self.manager.down_async(self)

    def up(self):  # pylint: disable=invalid-name
        return self.manager.up(self)

    def up_async(self):
        return self.manager.up_async(self)


class InterfaceManager(base.Manager):
    resource_class = Interface

    def __init__(self, api, node):
        super(InterfaceManager, self).__init__(api)
        self.node_id = base.get_id(node)

    @property
    def base_url(self):
        return "/nodes/{}/net/ifs".format(self.node_id)

    def list(self):
        return self._list(self.base_url)

    def get(self, iface):
        assert iface, "iface name can't be empty"
        # if iface="" just base_url will be used and you get all interfaces
        # for that case use list()
        iface_name = base.get_id(iface)
        return self._get("{}/{}".format(self.base_url, iface_name))

    def update_async(self, iface, ipv4=None, ipv6=None, gw4=None, gw6=None,
                     dhcp4_enabled=None, dhcp6_enabled=None, mtu=None,
                     network=missing, ignore_auto_routes_v4=None,
                     ignore_auto_routes_v6=None, connected_mode=None, ifaces=None,
                     bond_type=None):
        data = {}
        if ipv4 is not None:
            data['ipv4'] = ipv4
        if ipv6 is not None:
            data['ipv6'] = ipv6
        if gw4 is not None:
            data['gw4'] = gw4
        if gw6 is not None:
            data['gw6'] = gw6
        if dhcp4_enabled is not None:
            data['dhcp4_enabled'] = dhcp4_enabled
        if dhcp6_enabled is not None:
            data['dhcp6_enabled'] = dhcp6_enabled
        if mtu is not None:
            data['mtu'] = mtu
        if network is not missing:
            data['roles_set'] = base.get_id(network)
        if ignore_auto_routes_v4 is not None:
            data['ignore_auto_routes_v4'] = ignore_auto_routes_v4
        if ignore_auto_routes_v6 is not None:
            data['ignore_auto_routes_v6'] = ignore_auto_routes_v6
        if connected_mode is not None:
            data['connected_mode'] = connected_mode
        if ifaces is not None:
            data['ifaces'] = ifaces
        if bond_type is not None:
            data['bond_type'] = bond_type

        # Any changes on management interface may lead to connection abort
        task_params = None
        if is_management_iface(self, iface):
            task_params = {
                'connect_retries': 8,
                'connect_retry_delay': 0.3,
            }
        url = "{}/{}".format(self.base_url, base.get_id(iface))
        return self._patch_async(url, json=data, task_params=task_params)

    @base.async_wait
    def update(self, iface, **kwargs):
        return self.update_async(iface, **kwargs)

    def delete_async(self, iface):
        iface_name = base.get_id(iface)
        return self._delete_async("{}/{}".format(self.base_url, iface_name))

    @base.async_wait
    def delete(self, iface):
        return self.delete_async(iface)

    def down_async(self, iface):
        url = "{}/{}/down".format(self.base_url, base.get_id(iface))
        return self._post_async(url)

    @base.async_wait
    def down(self, iface):
        return self.down_async(iface)

    def up_async(self, iface):
        url = "{}/{}/up".format(self.base_url, base.get_id(iface))
        return self._post_async(url)

    @base.async_wait
    def up(self, iface):  # pylint: disable=invalid-name
        return self.up_async(iface)

    def create_vlan_async(self, iface, tag, ipv4=None, ipv6=None, gw4=None,
                          gw6=None, dhcp4_enabled=None, dhcp6_enabled=None,
                          mtu=None, network=None, ignore_auto_routes_v4=None,
                          ignore_auto_routes_v6=None):
        # NOTE(akurbatov): backened requires all params to be present
        data = {
            'iface': base.get_id(iface),
            'tag': tag,
            'ipv4': ipv4,
            'ipv6': ipv6,
            'gw4': gw4,
            'gw6': gw6,
            'dhcp4_enabled': dhcp4_enabled,
            'dhcp6_enabled': dhcp6_enabled,
            'mtu': mtu,
            'roles_set': base.get_id(network) if network else None,
            'ignore_auto_routes_v4': ignore_auto_routes_v4,
            'ignore_auto_routes_v6': ignore_auto_routes_v6,
        }
        url = "/nodes/{}/net/vlans".format(self.node_id)
        return self._post_async(url, json=data)

    @base.async_wait
    def create_vlan(self, iface, tag, **kwargs):
        return self.create_vlan_async(iface, tag, **kwargs)

    def create_bond_async(self, ifaces, bond_type, ipv4=None, ipv6=None,
                          gw4=None, gw6=None, dhcp4_enabled=None,
                          dhcp6_enabled=None, mtu=None, network=None,
                          ignore_auto_routes_v4=None,
                          ignore_auto_routes_v6=None,
                          bonding_opts=None, mac_addr=None):
        data = {
            'ifaces': [base.get_id(v) for v in ifaces],
            'bond_type': bond_type,
            'ipv4': ipv4,
            'ipv6': ipv6,
            'gw4': gw4,
            'gw6': gw6,
            'dhcp4_enabled': dhcp4_enabled,
            'dhcp6_enabled': dhcp6_enabled,
            'mtu': mtu,
            'roles_set': base.get_id(network) if network else None,
            'ignore_auto_routes_v4': ignore_auto_routes_v4,
            'ignore_auto_routes_v6': ignore_auto_routes_v6,
        }

        # API is definitely strange: bonding_opts & mac_addr can not be None
        if bonding_opts:
            data['bonding_opts'] = bonding_opts
        if mac_addr:
            data['mac_addr'] = mac_addr

        # Any changes on management interface may lead to connection abort
        # Any changes on management interface may lead to connection abort
        task_params = None
        for iface in ifaces:
            if is_management_iface(self, iface):
                task_params = {
                    'connect_retries': 8,
                    'connect_retry_delay': 0.3,
                }
                break

        url = "/nodes/{}/net/bonds".format(self.node_id)
        return self._post_async(url, json=data, task_params=task_params)

    @base.async_wait
    def create_bond(self, ifaces, bond_type, **kwargs):
        return self.create_bond_async(ifaces, bond_type, **kwargs)
