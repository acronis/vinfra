from vinfra import api_versions
from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra import exceptions


missing = object()
SUBNET_DEPRECATED_FIELDS = [
    'cidr',
    'enable_dhcp',
    'gateway_ip',
    'dns_nameservers',
    'allocation_pools',
    'ip_version'
]


class Network(base.Resource):
    def __init__(self, manager, info):
        if 'subnets' in info:
            for subnet in info['subnets']:
                if subnet['ip_version'] == 4:
                    break
            else:
                subnet = {}
        else:
            subnet = info.pop('subnet') or {}
            info['subnets'] = [subnet] if subnet else []

        for field in SUBNET_DEPRECATED_FIELDS:
            info[field] = subnet.get(field)

        net_type = info.pop('type')
        if net_type in ['flat', 'vlan']:
            info['type'] = 'physical'
        elif net_type == 'vxlan':
            info['type'] = 'virtual'
        else:
            info['type'] = net_type

        super(Network, self).__init__(manager, info)

    def delete_async(self, **kwargs):
        return self.manager.delete_async(self, **kwargs)

    def delete(self):
        return self.manager.delete(self)

    def update(self, *args, **params):
        return self.manager.update(self, *args, **params)


class NetworkManager(Manager):
    resource_class = Network
    base_url = "/compute/networks"

    def list(self, limit=None, marker=None, filters=None, sort=None):
        return self._list(self.base_url, limit=limit, marker=marker,
                          filters=filters, sort=sort)

    def get(self, network):
        url = "{}/{}".format(self.base_url, base.get_id(network))
        return self._get(url)

    def create_async(self, name=None, physical_network=None, subnets=None,
                     vlan=None, vlan_network=None, rbac_policies=None,
                     default_vnic_type=None, mtu=None):
        data = {}
        if name:
            data['name'] = name
        if physical_network:
            data['physical_network'] = physical_network
        if vlan_network:
            data['vlan_network'] = vlan_network
        if physical_network or vlan_network:
            # A virtual network creation may lead to an ovs bridge creation on
            # compute nodes witch in turn may lead to connection break for a
            # while, that's why connect_retries is used here
            task_params = {
                'connect_retries': 8,
                'connect_retry_delay': 0.3,
            }
        else:
            raise exceptions.VinfraError(
                'Create async is not supported for virtual networks')
        if subnets:
            if self.api.api_version >= api_versions.HCI_VER_47:
                data['subnets'] = subnets
            elif len(subnets) > 1:
                raise exceptions.VinfraError(
                    'API %s supports only single subnet' %
                    self.api.api_version.version)
            else:
                data['subnet'] = subnets[0]
        if vlan is not None:
            data['vlan_id'] = vlan
        if rbac_policies:
            data['rbac_policies'] = rbac_policies
        if default_vnic_type:
            data['default_vnic_type'] = default_vnic_type
        if mtu:
            data['mtu'] = mtu

        return self._post_async(self.base_url, json=data,
                                task_params=task_params)

    def create(self, name=None, physical_network=None, subnets=None,
               vlan=None, vlan_network=None, rbac_policies=None,
               default_vnic_type=None, mtu=None):
        if physical_network or vlan_network:
            return base.async_wait(self.create_async)(
                name=name, physical_network=physical_network, subnets=subnets,
                vlan=vlan, vlan_network=vlan_network,
                rbac_policies=rbac_policies,
                default_vnic_type=default_vnic_type,
                mtu=mtu)

        # Virtual network is always created in sync mode
        data = {}
        if name:
            data['name'] = name
        if subnets:
            if self.api.api_version >= api_versions.HCI_VER_47:
                data['subnets'] = subnets
            elif len(subnets) > 1:
                raise exceptions.VinfraError(
                    'API %s supports only single subnet' %
                    self.api.api_version.version)
            else:
                data['subnet'] = subnets[0]
        if rbac_policies:
            data['rbac_policies'] = rbac_policies
        if mtu:
            data['mtu'] = mtu
        return self._post(self.base_url, json=data)

    def delete_async(self, network, delete_vlan_interfaces=None):
        url = "{}/{}".format(self.base_url, base.get_id(network))
        params = {}
        if delete_vlan_interfaces is not None:
            params['delete_vlan_interfaces'] = delete_vlan_interfaces
        return self._delete_async(url, params=params)

    def delete(self, *args, **kwargs):
        return self.delete_async(*args, **kwargs)

    def update(self, network, name=None, subnet=None, rbac_policies=None, mtu=None):
        network_id = base.get_id(network)
        data = {}
        if name:
            data['name'] = name
        if subnet:
            data['subnet'] = subnet
        if rbac_policies is not None:
            data['rbac_policies'] = rbac_policies
        if mtu:
            data['mtu'] = mtu

        url = "{}/{}".format(self.base_url, network_id)
        return self._patch(url, json=data)


class Subnet(base.Resource):
    def delete(self):
        return self.manager.delete(self)

    def update(self, *args, **kwargs):
        return self.manager.update(self, *args, **kwargs)


class SubnetManager(Manager):
    resource_class = Subnet
    base_url = "/compute/subnets"

    def list(self, filters=None):
        return self._list(self.base_url, filters=filters)

    def get(self, subnet):
        url = "{}/{}".format(self.base_url, base.get_id(subnet))
        return self._get(url)

    def create(self, network, cidr, enable_dhcp=None, dns_nameservers=None,
               allocation_pools=None, gateway_ip=missing, ipv6_ra_mode=None,
               ipv6_address_mode=None):
        data = {
            'network_id': base.get_id(network),
            'cidr': cidr
        }
        if enable_dhcp is not None:
            data['enable_dhcp'] = enable_dhcp
        if dns_nameservers is not None:
            data['dns_nameservers'] = dns_nameservers
        if allocation_pools is not None:
            data['allocation_pools'] = allocation_pools
        if gateway_ip is not missing:
            data['gateway_ip'] = gateway_ip
        if ipv6_ra_mode:
            data['ipv6_ra_mode'] = ipv6_ra_mode
        if ipv6_address_mode:
            data['ipv6_address_mode'] = ipv6_address_mode

        return self._post(self.base_url, json=data)

    def update(self, subnet, enable_dhcp=None, dns_nameservers=None,
               allocation_pools=None, gateway_ip=missing):
        data = {}
        if enable_dhcp is not None:
            data['enable_dhcp'] = enable_dhcp
        if dns_nameservers is not None:
            data['dns_nameservers'] = dns_nameservers
        if allocation_pools is not None:
            data['allocation_pools'] = allocation_pools
        if gateway_ip is not missing:
            data['gateway_ip'] = gateway_ip

        url = '{}/{}'.format(self.base_url, base.get_id(subnet))
        return self._patch(url, json=data)

    def delete(self, subnet):
        url = '{}/{}'.format(self.base_url, base.get_id(subnet))
        return self._delete(url)
