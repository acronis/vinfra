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


def _prep_group_args(name=None, enabled=None, description=None,
                     email=None, domain_permissions=None,
                     assigned_projects=None, assigned_domains=None,
                     system_permissions=None):
    json = flatten_args(
        name=name,
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


class Group(base.Resource):
    def delete(self):
        self.manager.delete(self)

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def list_users(self):
        return self.manager.list_users(self)

    def delete_user(self, user):
        self.manager.delete_user(self, user)

    def add_user(self, user):
        self.manager.add_user(self, user)


class GroupManager(base.Manager):
    resource_class = Group

    def __init__(self, api, domain):
        super(GroupManager, self).__init__(api)
        self.domain_id = base.get_id(domain)
        self.domain = domain

    def create(self, name, enabled=None, description=None,
               email=None, domain_permissions=None,
               assigned_projects=None, assigned_domains=None,
               system_permissions=None):
        json = _prep_group_args(
            name=name, enabled=enabled,
            description=description, email=email,
            domain_permissions=domain_permissions,
            system_permissions=system_permissions,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
        )

        return self._post('/domains/{}/groups'.format(self.domain_id),
                          json=json, log=False)

    def delete(self, group):
        group_id = base.get_id(group)
        self._delete('/domains/{}/groups/{}'.format(self.domain_id, group_id))

    def list(self, limit=None, marker=None, filters=None, sort=None):
        url = '/domains/{}/groups'.format(self.domain_id)
        return self._list(url, limit=limit, marker=marker, filters=filters,
                          sort=sort)

    def update(self, group, name=None, enabled=None,
               description=None, domain_permissions=None, email=None,
               assigned_projects=None, assigned_domains=None,
               system_permissions=None):
        json = _prep_group_args(
            name=name, enabled=enabled,
            description=description, email=email,
            domain_permissions=domain_permissions,
            system_permissions=system_permissions,
            assigned_projects=assigned_projects,
            assigned_domains=assigned_domains,
        )

        group_id = base.get_id(group)

        url = '/domains/{}/groups/{}'.format(self.domain_id, group_id)
        return self._patch(url, json=json)

    def get(self, group):
        group_id = base.get_id(group)
        return self._get(
            '/domains/{}/groups/{}'.format(self.domain_id, group_id)
        )

    def list_users(self, group):
        group_id = base.get_id(group)

        data = self.client.get(
            '/domains/{}/groups/{}/users/'.format(self.domain_id, group_id)
        )
        data = data['data']

        return [self.domain.users_manager.create_resource(info)
                for info in data]

    def delete_user(self, group, user):
        group_id = base.get_id(group)
        user_id = base.get_id(user)

        self.client.delete(
            '/domains/{}/groups/{}/users/'.format(self.domain_id, group_id),
            json={'uuids': [user_id]},
        )

    def add_user(self, group, user):
        group_id = base.get_id(group)
        user_id = base.get_id(user)

        self.client.post(
            '/domains/{}/groups/{}/users/'.format(self.domain_id, group_id),
            json={'uuids': [user_id]},
        )
