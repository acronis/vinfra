from vinfra.api import base
from vinfra.utils import flatten_args


class IdP(base.Resource):
    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)


class IdPManager(base.Manager):
    resource_class = IdP

    def __init__(self, api, domain):
        super(IdPManager, self).__init__(api)
        self.domain_id = base.get_id(domain)

    def delete(self, idp):
        idp = base.get_id(idp)

        self.client.delete(
            '/domains/{}/idp/{}'.format(self.domain_id, idp))

    def list(self, limit=None, marker=None, filters=None, sort=None):
        url = '/domains/{}/idp'.format(self.domain_id)
        return self._list(url, limit=limit, marker=marker, filters=filters,
                          sort=sort)

    def create(self, name, issuer, scope, **kwargs):
        json = dict(name=name, issuer=issuer, scope=scope)
        json.update(flatten_args(**kwargs))
        return self._post(
            '/domains/{}/idp'.format(self.domain_id), json=json)

    def update(self, idp, **kwargs):
        json = flatten_args(**kwargs)
        idp_id = base.get_id(idp)
        return self._patch(
            'domains/{}/idp/{}'.format(self.domain_id, idp_id), json=json)

    def get(self, idp):
        idp_id = base.get_id(idp)
        return self._get(
            'domains/{}/idp/{}'.format(self.domain_id, idp_id))
