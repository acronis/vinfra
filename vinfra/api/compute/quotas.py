import collections
import json

from vinfra.api import base


class QuotasManager(base.Manager):
    base_url = "/compute/quotas"

    def show(self, project_id, usage=False):
        url = "{}/{}".format(self.base_url, project_id)
        if usage:
            params = {'usage': usage}
            url += "?params={}".format(json.dumps(params))

        return self._get(url)

    def update(self, project_id, compute_cores=None, compute_ram=None,
               network_floatingip=None, network_ipsec_site_connection=None,
               storage_policies=None, k8saas_cluster=None,
               lbaas_loadbalancer=None, placement=None):
        nested_dict = lambda: collections.defaultdict(nested_dict)
        payload = nested_dict()

        if compute_cores is not None:
            payload['compute']['cores']['limit'] = compute_cores
        if compute_ram is not None:
            payload['compute']['ram']['limit'] = compute_ram
        if network_floatingip is not None:
            payload['network']['floatingip'] = {'limit': network_floatingip}
        if network_ipsec_site_connection is not None:
            payload['network']['ipsec_site_connection'] = {
                'limit': network_ipsec_site_connection
            }
        if storage_policies:
            for spolicy, limit in storage_policies:
                payload['storage']['storage_policies'][spolicy]['limit'] = limit
        if k8saas_cluster is not None:
            payload['k8saas']['cluster'] = {'limit': k8saas_cluster}
        if lbaas_loadbalancer is not None:
            payload['lbaas']['loadbalancer'] = {'limit': lbaas_loadbalancer}
        if placement is not None:
            payload['placement'] = placement
        return self._post("{}/{}".format(self.base_url, project_id),
                          json=payload)
