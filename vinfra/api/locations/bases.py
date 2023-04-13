import marshmallow as ma

from vinfra.api import base

__all__ = ['BaseResource']


class BaseResource(base.Resource):
    class Schema(ma.Schema):
        pass

    @classmethod
    def schema(cls, strict=True):
        return cls.Schema(strict=strict)

    # pylint: disable=super-init-not-called
    # noinspection PyMissingConstructor
    def __init__(self, manager, info):
        self.manager = manager
        self.set_info(info)

    def __repr__(self):
        attrs = ", ".join("%s=%s" % (k, getattr(self, k)) for k in self.schema().fields)
        return "<{} {}>".format(self.__class__.__name__, attrs)

    def set_info(self, info):
        self.__dict__.update(self.schema().load(info).data)

    def _update_info(self, info):
        for k in self.schema().fields:
            delattr(self, k)
        self.set_info(info)

    def get(self):
        new = self.manager.get(getattr(self, self.ID_ATTR))
        self._update_info({k: getattr(new, k) for k in self.schema().fields if hasattr(new, k)})
        return self

    def to_dict(self):
        return self.schema().dump(self).data
