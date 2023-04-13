# pylint: disable=no-member,arguments-differ
import marshmallow as ma

from vinfra.api import base
from vinfra.api.locations.bases import BaseResource

__all__ = ['DomainPropsManager']


class DomainProps(BaseResource):
    class Schema(ma.Schema):
        domain = ma.fields.String(required=True)
        key = ma.fields.String(required=True)
        data = ma.fields.Raw(required=True)

    def get(self):
        # noinspection PyUnresolvedReferences
        new = self.manager.get(self.domain, self.key)
        self._update_info({k: getattr(new, k) for k in self.schema().fields if hasattr(new, k)})
        return self


class DomainPropsManager(base.Manager):
    resource_class = DomainProps
    url = "/domains/{domain}/props/{key}"

    def get(self, domain, key):
        """
        :param domain: object
        :param key: str
        :return: DomainProps
        """
        rv = self.client.get(self.url.format(domain=domain.name, key=key))
        return self.resource_class(self, dict(domain=domain.name, key=key, data=rv))

    def create(self, domain, key, access, data):
        """
        :param domain: object
        :param key: str
        :param access: str
        :param data: dict
        """

        return self.client.post(
            url=self.url.format(domain=domain.name, key=key),
            json=dict(access=access, data=data))

    def update(self, domain, key, data):
        """
        :param domain: object
        :param key: str
        :param data: dict
        """
        return self.client.put(
            url=self.url.format(domain=domain.name, key=key),
            json=data)

    def delete(self, domain, key):
        """
        :param domain: object
        :param key: str
        """
        return self.client.delete(
            url=self.url.format(domain=domain.name, key=key))
