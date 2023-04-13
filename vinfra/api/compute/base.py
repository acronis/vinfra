from vinfra.api import base
from vinfra.client import Client as BaseClient


class VinfraApi(base.VinfraApi):
    @property
    def client(self):
        return BaseClient(self.api)


class Manager(base.Manager):
    @property
    def client(self):
        return BaseClient(self.api)
