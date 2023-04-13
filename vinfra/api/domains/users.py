from vinfra.api import base
from vinfra.utils import flatten_args


class ProjectRole(object):
    def __init__(self, project, role):
        self.project_id = base.get_id(project)
        self.role = role


class ServiceRole(object):
    def __init__(self, domain, roles):
        self.domain_id = base.get_id(domain)
        self.roles = roles


def _prep_user_args(name=None, password=None, enabled=None, description=None,
                    email=None, domain_permissions=None,
                    assigned_projects=None, assigned_domains=None,
                    system_permissions=None):
    json = flatten_args(
        name=name,
        password=password,
        enabled=enabled,
        description=description,
        email=email,
        domain_permissions=domain_permissions,
        system_permissions=system_permissions,
    )

    if assigned_projects is not None:
        if not isinstance(assigned_projects, list):
            assigned_projects = [assigned_projects]

        json['assigned_projects'] = [
            dict(project_id=p.project_id, role=p.role)
            for p in assigned_projects
        ]

    if assigned_domains is not None:
        if not isinstance(assigned_domains, list):
            assigned_domains = [assigned_domains]

        json['assigned_domains'] = [
            dict(domain_id=d.domain_id, roles=d.roles)
            for d in assigned_domains
        ]

    return json


class User(base.Resource):
    def delete(self):
        self.manager.delete(self)

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def list_groups(self):
        return self.manager.list_groups(self)

    def unlock(self):
        self.manager.unlock(self)


class UserManager(base.Manager):
    resource_class = User

    def __init__(self, api, domain):
        super(UserManager, self).__init__(api)
        self.domain_id = base.get_id(domain)
        self.domain = domain

    def create(self, name, password, enabled=None, description=None,
               email=None, domain_permissions=None,
               assigned_projects=None, assigned_domains=None,
               system_permissions=None):
        json = _prep_user_args(
            name=name, password=password, enabled=enabled,
            description=description, email=email,
            domain_permissions=domain_permissions,
            system_permissions=system_permissions,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
        )

        return self._post('/domains/{}/users'.format(self.domain_id),
                          json=json, log=False)

    def delete(self, user):
        user_id = base.get_id(user)
        self._delete('/domains/{}/users/{}'.format(self.domain_id, user_id))

    def list(self, limit=None, marker=None, filters=None, sort=None):
        url = '/domains/{}/users'.format(self.domain_id)
        return self._list(url, limit=limit, marker=marker, filters=filters,
                          sort=sort)

    def list_groups(self, user):
        user_id = base.get_id(user)

        data = self.client.get(
            '/domains/{}/users/{}/groups/'.format(self.domain_id, user_id)
        )
        data = data['data']

        return [self.domain.groups_manager.create_resource(info)
                for info in data]

    def update(self, user, name=None, password=None, enabled=None,
               description=None, domain_permissions=None, email=None,
               assigned_projects=None, assigned_domains=None,
               system_permissions=None):
        json = _prep_user_args(
            name=name, password=password, enabled=enabled,
            description=description, email=email,
            domain_permissions=domain_permissions,
            system_permissions=system_permissions,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
        )

        user_id = base.get_id(user)

        log = False if password else True
        url = '/domains/{}/users/{}'.format(self.domain_id, user_id)
        return self._patch(url, json=json, log=log)

    def get(self, user):
        user_id = base.get_id(user)
        return self._get(
            '/domains/{}/users/{}'.format(self.domain_id, user_id)
        )

    def unlock(self, user):
        user_id = base.get_id(user)
        return self._patch(
            '/domains/{}/users/{}/unlock'.format(self.domain_id, user_id)
        )
