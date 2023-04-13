# pylint: disable=no-member,arguments-differ
import marshmallow as ma
from marshmallow.validate import OneOf

from vinfra.api import base
from vinfra.api.locations.bases import BaseResource

__all__ = ['LogSeverityManager', 'Severity']


class Severity(object):
    __VALUES = frozenset((
        'CRITICAL',
        'ERROR',
        'WARNING',
        'INFO',
        'DEBUG',
        'TRACE',
        'NOTSET',
    ))

    @classmethod
    def values(cls):
        return cls.__VALUES


class NodesListSchema(ma.Schema):
    nodes = ma.fields.List(
        ma.fields.UUID(required=True, allow_none=False), required=False, allow_none=False)


class LogLevelSchema(ma.Schema):
    log_level = ma.fields.String(
        required=True, allow_none=False, allow_empty=False, validate=OneOf(Severity.values()))
    nodes = ma.fields.List(
        ma.fields.UUID(required=True, allow_none=False), required=False, allow_none=False)


class LogSeverity(BaseResource):
    class Schema(ma.Schema):
        node_id = ma.fields.UUID(required=True)
        host = ma.fields.String(required=True)
        agent_level = ma.fields.String(required=True)
        backend_level = ma.fields.String(required=True)

    def get(self):
        new = self.manager.get(nodes=[str(self.node_id)])
        self._update_info({k: getattr(new, k) for k in self.schema().fields if hasattr(new, k)})
        return self


class LogSeverityManager(base.Manager):
    resource_class = LogSeverity
    base_url = "/logging/"

    @property
    def url(self):
        return self.base_url

    def get(self, nodes=None):
        """
        :param nodes: List[UUID]
        :return: List
        """
        if nodes:
            query_params = NodesListSchema(strict=True).dump(dict(nodes=nodes)).data
            rv = self.client.get(self.url, params=query_params)
        else:
            rv = self.client.get(self.url)

        return [self.resource_class(self, e) for e in rv]

    def set(self, severity, nodes=None):
        if nodes:
            data = LogLevelSchema(strict=True).dump(dict(log_level=severity, nodes=nodes)).data
        else:
            data = LogLevelSchema(strict=True).dump(dict(log_level=severity)).data

        self.client.put(self.url, json=data)
