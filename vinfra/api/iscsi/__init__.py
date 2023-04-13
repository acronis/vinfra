from vinfra.api import base
from vinfra.api.iscsi.targets import TargetManager
from vinfra.api.iscsi.users import UserManager


class Iscsi(object):

    def __init__(self, api, cluster):
        self.api = api
        self.targets = TargetManager(api, cluster)
        self.users = UserManager(api, cluster)
