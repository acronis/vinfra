# pylint: disable=no-member,arguments-differ
import marshmallow as ma

from vinfra.api import base
from .bases import BaseResource

__all__ = ['LocationsConfig', 'LocationsConfigManager']


class LocationsConfig(BaseResource):
    nr_locations = 5

    class Schema(ma.Schema):
        s = ma.fields.List(ma.fields.String(required=True, allow_none=False))
        p = ma.fields.List(ma.fields.String(required=True, allow_none=False))

        @staticmethod
        def validate(value):
            if len(value) != LocationsConfig.nr_locations:
                raise ma.ValidationError(
                    'API error: expected a list containing {} names, got {}'.format(
                        LocationsConfig.nr_locations, value))

        @ma.validates("s")
        def validate_s(self, value):
            self.validate(value)

        @ma.validates("p")
        def validate_p(self, value):
            self.validate(value)


class LocationsConfigManager(base.Manager):
    resource_class = LocationsConfig
    base_url = "/locations/configuration"

    @property
    def nr_locations(self):
        return self.resource_class.nr_locations

    def get(self):
        return self._get(self.base_url)

    def update(self, singulars, plurals):
        self.client.post(
            self.base_url,
            json={"s": singulars, "p": plurals}
        )
        return self.get()

    def list(self):
        cfg = self.get()
        return tuple(dict(
            id=n, singular=cfg.s[n], plural=cfg.p[n])
                     for n in xrange(0, self.nr_locations))

    def set(self, level, singular, plural):
        cfg = self.get()
        cfg.s[level], cfg.p[level] = singular, plural
        self.update(singulars=cfg.s, plurals=cfg.p)
