from vinfra.api import base
from vinfra.utils import flatten_args


class User(base.Resource):
    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def delete(self):
        return self.manager.delete(self)


class UserManager(base.Manager):
    resource_class = User
    base_url = "/accounts"

    def list(self):
        return self._list(self.base_url)

    def get(self, user):
        user_id = base.get_id(user)
        return self._get("{}/{}".format(self.base_url, user_id))

    # for ldap user creation needs additional method
    def create(self, name, password, roles, is_enabled, description=None):
        json = dict(name=name, password=password, roles=roles,
                    is_enabled=is_enabled, is_group=False)
        json.update(flatten_args(description=description))
        json = [json]  # see endpoint in backend
        users = self.client.post(self.base_url, json=json, log=False)
        return self.resource_class(self, users[0])

    def update(self, user, name=None, password=None, is_enabled=None,
               description=None, roles=None):
        user_id = base.get_id(user)
        json = flatten_args(name=name, password=password,
                            is_enabled=is_enabled, description=description,
                            roles=roles)
        log = False if password else True
        url = "{}/{}".format(self.base_url, user_id)
        return self._put(url, json=json, log=log)

    def delete(self, user):
        user_id = base.get_id(user)
        url = "{}/{}".format(self.base_url, user_id)
        self._delete(url)

    def change_password(self, current_password, new_password):
        json = dict(current_password=current_password,
                    new_password=new_password)
        return self._put('/accounts/change-password', json=json, log=False)

    def get_current(self):
        return self._get("{}/whoami".format(self.base_url))

    def get_available_roles(self):
        return self.client.get('/accounts/access-roles')
