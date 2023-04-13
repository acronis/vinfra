from vinfra.api import base


class License(object):
    def __init__(self, cluster):
        self.cluster = cluster
        self.api = cluster.manager.api

    def cluster_prefix_url(self, url):
        return "/%s/%s" % (base.get_id(self.cluster), url.lstrip('/'))


class VirtuozzoLicense(License):
    def get(self):
        url = self.cluster_prefix_url('/license')
        return self.api.client.get(url)

    def register(self, key):
        url = self.cluster_prefix_url('/license/keys/register')
        return self.api.client.post(url, json={'key': key})

    def update(self, server=None):
        json = {}
        if server is not None:
            json['server'] = server
        url = self.cluster_prefix_url('/license/keys/update')
        return self.api.client.post(url, json=json)


class AcronisLicense(License):
    def get(self):
        url = self.cluster_prefix_url('/license/as')
        return self.api.client.get(url)

    def test(self, keys, license_type):
        json = {'keys': keys, 'license_type': license_type}
        url = self.cluster_prefix_url('/license/as/test')
        return self.api.client.get(url, params=json)

    def activate(self, keys, license_type):
        json = {'keys': keys, 'license_type': license_type}
        url = self.cluster_prefix_url('/license/as/activate')
        return self.api.client.post(url, json=json)

    def deactivate_spla(self):
        url = '/hci-spla'
        return self.api.client.delete(url)
