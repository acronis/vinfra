from vinfra.api import base
from vinfra.utils import flatten_args


class Client(object):
    def __init__(self, addresses, access_type, security_types):
        self.addresses = addresses
        self.access_type = access_type
        self.security_types = security_types

    def to_dict(self):
        return {
            'addresses': self.addresses,
            'access_type': self.access_type,
            'security_types': self.security_types,
        }

    def __repr__(self):
        return repr(self.to_dict())


def get_api_clients(clients):
    res = []
    for client in clients or []:
        res.append(client.to_dict())
    return res


class Export(base.Resource):
    ID_ATTR = 'name'


class ExportManager(base.Manager):
    resource_class = Export

    def __init__(self, cluster):
        self.cluster = cluster
        super(ExportManager, self).__init__(cluster.manager.api)

    @property
    def base_url(self):
        return "/{}/nfs/shares/".format(base.get_id(self.cluster))

    def share_url(self, share_name):
        return "{}{}/exports/".format(self.base_url, share_name)

    def export_url(self, share_name, export_name):
        return "{}{}/".format(self.share_url(share_name), export_name)

    def list(self, share_name=None):
        url = self.base_url
        if share_name:
            url = '{}{}/'.format(url, share_name)
        data = self.client.get(url)

        if share_name:
            exports = data['exports']
        else:
            exports = []
            for item in data.get("data"):
                exports.extend(item['exports'])

        items = [self.resource_class(self, res) for res in exports]
        return items

    def get(self, share_name, export_name):
        return self._get(self.export_url(share_name, export_name))

    def create_async(
            self, share_name, export_name,
            path, access_type, security_types,
            clients=None, squash=None, anonymous_gid=None, anonymous_uid=None,
    ):
        data = dict(
            name=export_name,
            path=path,
            access_type=access_type,
            security_types=security_types,
            clients=get_api_clients(clients),
        )
        data.update(flatten_args(
            squash=squash,
            anonymous_gid=anonymous_gid,
            anonymous_uid=anonymous_uid,
        ))
        return self.client.post_async(
            self.share_url(share_name), json=data)

    def delete_async(self, share_name, export_name):
        return self.client.delete_async(self.export_url(
            share_name, export_name))

    def update_async(
            self, share_name, export_name,
            path=None, access_type=None, security_types=None,
            clients=None, squish=None, anonymous_gid=None, anonymous_uid=None,
    ):
        data = flatten_args(
            path=path,
            access_type=access_type,
            security_types=security_types,
            clients=get_api_clients(clients),
            squish=squish,
            anonymous_gid=anonymous_gid,
            anonymous_uid=anonymous_uid,
        )
        return self.client.put_async(
            self.export_url(share_name, export_name), json=data)
