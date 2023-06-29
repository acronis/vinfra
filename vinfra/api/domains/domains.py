from vinfra.api import base
from vinfra.api.domains.groups import GroupManager
from vinfra.api.domains.idps import IdPManager
from vinfra.api.domains.projects import ProjectManager
from vinfra.api.domains.users import UserManager
from vinfra.utils import flatten_args


class Domain(base.Resource):
    def __init__(self, manager, info):
        super(Domain, self).__init__(manager, info)

        self.users_manager = UserManager(self.manager.api, self)
        self.groups_manager = GroupManager(self.manager.api, self)
        self.projects_manager = ProjectManager(
            self.manager.api, self, self.users_manager)
        self.idps_manager = IdPManager(self.manager.api, self)

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def delete(self):
        return self.manager.delete(self)


class DomainManager(base.Manager):
    resource_class = Domain
    base_url = "/domains"

    def list(self):
        return self._list(self.base_url)

    def create(self, name, description=None, enabled=None):
        json = dict(name=name)
        json.update(flatten_args(description=description, enabled=enabled))
        return self._post(self.base_url, json=json)

    def update(self, domain, name=None, description=None, enabled=None):
        domain_id = base.get_id(domain)
        json = flatten_args(name=name, description=description,
                            enabled=enabled)
        return self._put("{}/{}".format(self.base_url, domain_id), json=json)

    def get(self, domain):
        domain_id = base.get_id(domain)
        return self._get("{}/{}".format(self.base_url, domain_id))

    def delete(self, domain):
        domain_id = base.get_id(domain)
        self._delete("{}/{}".format(self.base_url, domain_id))


class UserDomainManager(base.Manager):
    resource_class = Domain
    base_url = "/accounts/domains"

    def list(self):
        return self._list(self.base_url)
