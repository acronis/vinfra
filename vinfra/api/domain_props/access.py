# pylint: disable=no-member,arguments-differ,deprecated-lambda
import marshmallow as ma

from vinfra.api import base
from vinfra.api.locations.bases import BaseResource

__all__ = ['DomainPropsAccessManager']


class DomainPropsAccess(BaseResource):
    class Schema(ma.Schema):
        domain = ma.fields.String(required=True)
        key = ma.fields.String(required=True)
        access = ma.fields.String(required=True)

    def get(self):
        raise NotImplementedError


class DomainPropsAccessManager(base.Manager):
    resource_class = DomainPropsAccess
    props_url = "/domains/{domain}/props"
    access_url = props_url + "/{key}/access/"

    def list(self, domain):
        """
        :param domain: object
        :return: DomainPropsAccess
        """
        rv = self.client.get(self.props_url.format(domain=domain.name))
        return list(map(lambda e: self.resource_class(self, e),
                        map(lambda d: (d.update(dict(domain=domain.name)), d)[1],
                            rv)))

    def update(self, domain, key, access):
        """
        :param domain: object
        :param key: str
        :param access: str
        """
        return self.client.put(
            url=self.access_url.format(domain=domain.name, key=key),
            json=dict(access=access))
