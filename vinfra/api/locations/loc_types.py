# pylint: disable=no-member
import marshmallow as ma

from vinfra.api import base
from .bases import BaseResource

__all__ = ['RoomsManager', 'RowsManager', 'RacksManager']


class Location(BaseResource):
    class Schema(ma.Schema):
        id = ma.fields.Integer(required=True)
        name = ma.fields.String(required=True)

    @classmethod
    def index(cls):
        """
        returns an integer index of a location
        """
        raise NotImplementedError

    def update(self, new_name):
        # noinspection PyUnresolvedReferences
        self.manager.update(self, self.id, new_name)

    def add_children(self, *children):
        """
        add children to the location
        :children: list of children`s ids
        """
        # noinspection PyUnresolvedReferences
        self.manager.add_children(self.id, *children)

    def rm_children(self, *children):
        """
        remove children from the location
        :children: list of children`s ids
        """
        # noinspection PyUnresolvedReferences
        return self.manager.rm_children(self.id, *children)


class Room(Location):
    class Schema(Location.Schema):
        children = ma.fields.List(ma.fields.Integer(), required=False, missing=[])

    @classmethod
    def index(cls):
        return 4


class Row(Location):
    class Schema(Location.Schema):
        parent = ma.fields.Integer(required=True)
        children = ma.fields.List(ma.fields.Integer(), required=False, missing=[])

    @classmethod
    def index(cls):
        return 3


class Rack(Location):
    class Schema(Location.Schema):
        parent = ma.fields.Integer(required=True)
        children = ma.fields.List(ma.fields.UUID(), dump_to='nodes', required=False, missing=[])

    @property
    def nodes(self):
        # noinspection PyUnresolvedReferences
        return self.children

    @classmethod
    def index(cls):
        return 2


class LocationsManager(base.Manager):
    resource_class = Room
    base_url = "/locations/"

    @classmethod
    def index(cls):
        return cls.resource_class.index()

    @classmethod
    def _url(cls, location_id=None):
        return (
            "{}/{}".format(cls.base_url, cls.index())
            if location_id is None else
            "{}/{}/{}/".format(cls.base_url, cls.index(), location_id)
        )

    @classmethod
    def _parent_url(cls, parent_id):
        return (lambda index: "{}/{}/{}/{}/".format(cls.base_url, index + 1, parent_id, index))(
            cls.index()
        )

    @classmethod
    def _children_url(cls, location_id):
        return (lambda index: "{}/{}/{}/{}/".format(cls.base_url, index, location_id, index - 1))(
            cls.index()
        )

    def list(self):
        return self._list(self._url())

    def create(self, parent_id, name):
        return self._post(
            self._parent_url(parent_id),
            json={"name": name}
        )

    def get(self, location_id):
        return self._get(self._url(location_id))

    def update(self, location_id, new_name):
        self.client.patch(
            self._url(location_id),
            json={"name": new_name}
        )

    def delete(self, location_id):
        self.client.delete(self._url(location_id))

    def add_children(self, location_id, *children_ids):
        self.client.put(
            self._children_url(location_id),
            json=children_ids
        )


class RoomsManager(LocationsManager):
    resource_class = Room

    @classmethod
    def _parent_url(cls, parent_id):
        return cls._url()


class RowsManager(LocationsManager):
    resource_class = Row


class RacksManager(LocationsManager):
    resource_class = Rack

    @classmethod
    def _children_url(cls, location_id):
        return "{}/{}/{}/nodes/".format(cls.base_url, cls.index(), location_id)

    def add_children(self, location_id, *children_ids):
        self.client.put(
            self._children_url(location_id),
            json=list(map(str, children_ids))
        )
