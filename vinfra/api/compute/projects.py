from vinfra.api import base


class Project(base.Resource):
    pass


class ProjectManager(base.Manager):
    resource_class = Project

    def list(self):
        return self._list('/compute/projects')
