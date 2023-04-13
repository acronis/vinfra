from vinfra.api import base
from vinfra.utils import flatten_args


class Iscsi(base.Resource):
    ID_ATTR = "target_name"


class IscsiManager(base.Manager):
    resource_class = Iscsi

    def __init__(self, api, node):
        super(IscsiManager, self).__init__(api)
        self.node_id = base.get_id(node)

    def get(self):
        url = "/nodes/{}/iscsi-initiators/target".format(self.node_id)
        res = self.client.get(url)
        if not res:
            return None

        return self.resource_class(self, res)

    def connect_async(self, target_name, portals, auth_username=None,
                      auth_password=None):
        json = dict(portals=portals, target_name=target_name)
        json.update(flatten_args(
            auth_username=auth_username,
            auth_password=auth_password
        ))

        url = "/nodes/{}/iscsi-initiators/connect".format(self.node_id)
        return self._post_async(url, json=json)

    @base.async_wait
    def connect(self, *args, **kwargs):
        return self.connect_async(*args, **kwargs)

    def disconnect_async(self, target_name):
        json = {'target_name': target_name}
        url = "/nodes/{}/iscsi-initiators/disconnect".format(self.node_id)
        return self.client.post_async(url, json=json)

    @base.async_wait
    def disconnect(self, *args, **kwargs):
        return self.disconnect_async(*args, **kwargs)
