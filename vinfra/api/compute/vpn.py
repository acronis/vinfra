from vinfra.api import base
from vinfra.api.compute.base import Manager


class VpnManager(object):
    def __init__(self, api):
        self.vpnservices = VpnServiceManager(api)
        self.ipsec_site_connections = IPsecSiteConnectionManager(api)
        self.ikepolicies = IkePolicyManager(api)
        self.ipsecpolicies = IPsecPolicyManager(api)
        self.endpoint_groups = EndpointGroupManager(api)


class IPsecSiteConnection(base.Resource):
    def delete(self):
        return self.manager.delete(self)

    def update(self, *args, **params):
        return self.manager.update(self, *args, **params)

    def restart(self):
        return self.manager.restart(self)


class VpnService(base.Resource):
    pass


class IkePolicy(base.Resource):
    pass


class IPsecPolicy(base.Resource):
    pass


class EndpointGroup(base.Resource):
    pass


class _VpnBaseManager(Manager):
    base_url = None
    resource_class = None

    def list(self):
        return self._list(self.base_url)

    def get(self, endpoint_group):
        url = "{}/{}".format(self.base_url, base.get_id(endpoint_group))
        return self._get(url)


class IPsecSiteConnectionManager(_VpnBaseManager):
    resource_class = IPsecSiteConnection
    base_url = "/compute/vpn/ipsec-site-connections"

    def create(self, vpnservice, ipsec_site_connection, ikepolicy=None,
               ipsecpolicy=None, local_ep_group=None, peer_ep_group=None):
        data = {
            'vpnservice': vpnservice,
            'ipsec_site_connection': ipsec_site_connection,
        }
        if ikepolicy:
            data['ikepolicy'] = ikepolicy
        if ipsecpolicy:
            data['ipsecpolicy'] = ipsecpolicy
        if local_ep_group:
            data['local_ep_group'] = local_ep_group
        if peer_ep_group:
            data['peer_ep_group'] = peer_ep_group
        return self._post(self.base_url, json=data)

    def update(self, ipsec_site_connection, new_ipsec_site_connection,
               local_ep_group=None, peer_ep_group=None):
        data = {'ipsec_site_connection': new_ipsec_site_connection}
        if local_ep_group:
            data['local_ep_group'] = local_ep_group
        if peer_ep_group:
            data['peer_ep_group'] = peer_ep_group
        url = '{}/{}'.format(self.base_url, base.get_id(ipsec_site_connection))
        return self._patch(url, json=data)

    def delete(self, ipsec_site_connection):
        url = '{}/{}'.format(self.base_url, base.get_id(ipsec_site_connection))
        return self._delete(url)

    def restart(self, ipsec_site_connection):
        url = '{}/{}/restart'.format(self.base_url,
                                     base.get_id(ipsec_site_connection))
        return self._post(url)


class VpnServiceManager(_VpnBaseManager):
    resource_class = VpnService
    base_url = "/compute/vpn/vpnservices"


class IkePolicyManager(_VpnBaseManager):
    resource_class = IkePolicy
    base_url = "/compute/vpn/ikepolicies"


class IPsecPolicyManager(_VpnBaseManager):
    resource_class = IPsecPolicy
    base_url = "/compute/vpn/ipsecpolicies"


class EndpointGroupManager(_VpnBaseManager):
    resource_class = EndpointGroup
    base_url = "/compute/vpn/endpoint-groups"
