import json

from vinfra.api import base, failure_domains
from vinfra.api.compute.storage_policies import get_api_redundancy
from vinfra.utils import flatten_args, get_stream


class Share(base.Resource):
    ID_ATTR = 'name'


class ShareManager(base.Manager):
    resource_class = Share

    def __init__(self, cluster):
        self.cluster = cluster
        super(ShareManager, self).__init__(cluster.manager.api)

    @property
    def base_url(self):
        return "/{}/nfs/shares/".format(base.get_id(self.cluster))

    def share_url(self, name):
        name = base.get_id(name)
        return "{}/{}".format(self.base_url, name)

    def list(self):
        with failure_domains.api_version(self.client):
            return self._list(self.base_url)

    def get(self, name):
        with failure_domains.api_version(self.client):
            return self._get(self.share_url(name))

    def create_async(
            self, name, ip_address, node, size,
            failure_domain, tier, redundancy, krb_keytab=None,
    ):
        redundancy = get_api_redundancy(redundancy)

        data = {
            'name': name,
            'ip_address': ip_address,
            'node_id': node.id,
            'total_space': size,
            'tier': tier,
            'redundancy': redundancy,
            'failure_domain': failure_domain,
        }
        files = {'json': (None, json.dumps(data))}
        if krb_keytab:
            files['krb_keytab'] = get_stream(krb_keytab)

        return self.client.post_async(self.base_url, files=files)

    def delete_async(self, name):
        return self.client.delete_async(self.share_url(name))

    def update_async(
            self, name,
            size=None, failure_domain=None, tier=None, redundancy=None,
            krb_auth_enabled=None, krb_keytab=None, ip_address=None
    ):
        url = self.share_url(name)
        redundancy = get_api_redundancy(redundancy)

        data = flatten_args(
            total_space=size,
            failure_domain=failure_domain,
            tier=tier,
            redundancy=redundancy,
            krb_auth_enabled=krb_auth_enabled,
            ip_address=ip_address
        )
        files = {'json': (None, json.dumps(data))}
        if krb_keytab:
            files['krb_keytab'] = get_stream(krb_keytab)

        return self._put_async(url, files=files)

    def start_async(self, share):
        url = "%s/start" % self.share_url(share)
        return self.client.post_async(url)

    def stop_async(self, share, force=None):
        data = flatten_args(force=force)
        url = "%s/stop" % self.share_url(share)
        return self.client.post_async(url, json=data)
