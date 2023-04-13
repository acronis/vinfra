from vinfra.api import base
from vinfra.consts import missing


class AbstractPerClusterMemoryPoliciesManager(base.VinfraApi):

    url_template = ''

    def __init__(self, api, cluster):
        super(AbstractPerClusterMemoryPoliciesManager, self).__init__(api)
        self.url_arguments = {
            'cluster_id': base.get_id(cluster),
        }

    def base_url(self):
        return self.url_template.format(**self.url_arguments)

    def show_params(self):
        return self.client.get(self.base_url())

    def reset_params(self):
        return self.client.delete(self.base_url())

    def change_params(self, guarantee=missing, swap=missing,
                      cache_ratio=missing, cache_minimum=missing,
                      cache_maximum=missing):

        def cache():
            if cache_ratio is None and cache_minimum is None and cache_maximum is None:
                return None

            rv = {}

            if cache_ratio is not missing:
                rv['ratio'] = cache_ratio

            if cache_minimum is not missing:
                rv['minimum'] = cache_minimum

            if cache_maximum is not missing:
                rv['maximum'] = cache_maximum

            return rv or missing

        json = {}

        if guarantee is not missing:
            json['guarantee'] = guarantee

        if swap is not missing:
            json['swap'] = swap

        cache_val = cache()
        if cache_val is not missing:
            json['cache'] = cache_val

        return self.client.put(self.base_url(), json=json)


class PerClusterMemoryPoliciesManager(AbstractPerClusterMemoryPoliciesManager):

    url_template = '/{cluster_id}/memory-policies/vstorage-services/'


class PerNodeMemoryPoliciesManager(AbstractPerClusterMemoryPoliciesManager):

    url_template = '/{cluster_id}/memory-policies/vstorage-services/nodes/{node_id}/'

    def __init__(self, api, cluster, node):
        super(PerNodeMemoryPoliciesManager, self).__init__(api, cluster)
        self.url_arguments.update({
            'node_id': base.get_id(node),
        })
