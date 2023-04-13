from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra.utils import flatten_args


class User(base.Resource):
    ID_ATTR = 'username'


class UserManager(Manager):
    resource_class = User

    def __init__(self, api, cluster):
        super(UserManager, self).__init__(api)
        self.cluster_id = base.get_id(cluster)

    @property
    def base_url(self):
        return "/{}/iscsi/users".format(self.cluster_id)

    def username_url(self, user):
        username = base.get_id(user)
        return "{}/{}".format(self.base_url, username)

    def list(self):
        return self._list(self.base_url)

    def get(self, user):
        return self._get(self.username_url(user))

    def create(self, username, password, is_enabled=None, description=None):
        json = dict(username=username, password=password)
        json.update(
            flatten_args(is_enabled=is_enabled, description=description))
        return self._post(self.base_url, json=json)

    def delete(self, user):
        return self.client.delete(self.username_url(user))

    def update(self, user, password=None, is_enabled=None, description=None):
        url = self.username_url(user)
        json = flatten_args(
            password=password,
            is_enabled=is_enabled,
            description=description
        )
        return self._put(url, json=json)
