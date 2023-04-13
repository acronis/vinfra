# pylint: disable=no-member,arguments-differ,deprecated-lambda
import marshmallow as ma

from vinfra.api import base
from vinfra.api.locations.bases import BaseResource

__all__ = ['DomainsKeysManager']


class DomainsKeys(BaseResource):
    class Schema(ma.Schema):
        domain = ma.fields.String(required=True)
        keys = ma.fields.List(ma.fields.String(required=False), required=True)

    def get(self):
        raise NotImplementedError


class DomainsKeysManager(base.Manager):
    resource_class = DomainsKeys
    url = "/domains/props"

    def list(self):
        """
        :return: list of DomainsKeys
        """
        return list(map(lambda e: self.resource_class(self, e), self.client.get(self.url)))
