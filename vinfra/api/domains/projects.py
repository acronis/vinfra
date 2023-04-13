from vinfra.api import base
from vinfra.utils import flatten_args


class Project(base.Resource):
    def delete(self):
        self.manager.delete(self)

    def list_users(self):
        return self.manager.list_users(self)

    def delete_users(self, users):
        self.manager.delete_users(self, users)

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)


class ProjectManager(base.Manager):
    resource_class = Project

    def __init__(self, api, domain, user_manager):
        super(ProjectManager, self).__init__(api)
        self.domain_id = base.get_id(domain)
        self.user_manager = user_manager

    def delete(self, projects):
        if not isinstance(projects, list):
            projects = [projects]

        projects = [base.get_id(p) for p in projects]

        self.client.delete(
            '/domains/{}/projects'.format(self.domain_id),
            json={'uuids': projects}
        )

    def list(self, limit=None, marker=None, filters=None, sort=None):
        url = '/domains/{}/projects'.format(self.domain_id)
        return self._list(url, limit=limit, marker=marker, filters=filters,
                          sort=sort)

    def create(self, name, description=None, enabled=None, parent=None):
        json = dict(name=name)
        json.update(flatten_args(description=description, enabled=enabled,
                                 parent_id=base.get_id(parent)))
        return self._post(
            '/domains/{}/projects'.format(self.domain_id), json=json
        )

    def update(self, project, name=None, description=None, enabled=None):
        json = flatten_args(
            name=name, description=description, enabled=enabled
        )
        project_id = base.get_id(project)
        return self._patch(
            'domains/{}/projects/{}'.format(self.domain_id, project_id),
            json=json
        )

    def get(self, project):
        project_id = base.get_id(project)
        return self._get(
            'domains/{}/projects/{}'.format(self.domain_id, project_id)
        )

    def list_users(self, project):
        project_id = base.get_id(project)

        data = self.client.get(
            '/domains/{}/projects/{}/users'.format(self.domain_id, project_id)
        )
        data = data['data']

        return [self.user_manager.create_resource(info) for info in data]

    def delete_users(self, project, users):
        project_id = base.get_id(project)

        if not isinstance(users, list):
            users = [users]
        user_ids = [base.get_id(user) for user in users]

        self.client.delete(
            '/domains/{}/projects/{}/users'.format(self.domain_id, project_id),
            json={'uuids': user_ids},
        )
