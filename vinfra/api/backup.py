from vinfra.api import base


class Backup(base.Resource):
    pass


class BackupManager(base.Manager):
    base_url = "/backup"
    resource_class = Backup

    def create_async(self):
        return self._post_async(self.base_url)

    def get(self):
        return self._get(self.base_url)
