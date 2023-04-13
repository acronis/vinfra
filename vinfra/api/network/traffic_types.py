from vinfra import api_versions
from vinfra.api import base


class TrafficType(base.Resource):
    ID_ATTR = "name"

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def update_async(self, **kwargs):
        return self.manager.update_async(self, **kwargs)

    def delete(self):
        return self.manager.delete(self)


class TrafficTypeManager(base.Manager):
    resource_class = TrafficType
    base_url = "/network/interface/roles"

    def list(self):
        return self._list(self.base_url)

    def get(self, traffic_type):
        role_name = base.get_id(traffic_type)
        return self._get("{}/{}".format(self.base_url, role_name))

    def create(self, name, port, inbound_allow_list=None, inbound_deny_list=None):
        data = {'name': name, 'port': port}
        if inbound_allow_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_allow_list'] = inbound_allow_list
            else:
                data['allow_list'] = inbound_allow_list
        if inbound_deny_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_deny_list'] = inbound_deny_list
            else:
                data['deny_list'] = inbound_deny_list

        return self._post(self.base_url, json=data)

    @base.async_wait
    def update(self, traffic_type, **kwargs):
        return self.update_async(traffic_type, **kwargs)

    def update_async(self, traffic_type, name=None, port=None,
                     inbound_allow_list=None, inbound_deny_list=None):
        data = {}
        if name is not None:
            data['new_name'] = name
        if port is not None:
            data['port'] = port
        if inbound_allow_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_allow_list'] = inbound_allow_list
            else:
                data['allow_list'] = inbound_allow_list
        if inbound_deny_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_deny_list'] = inbound_deny_list
            else:
                data['deny_list'] = inbound_deny_list

        url = "{}/{}".format(self.base_url, base.get_id(traffic_type))
        return self._put_async(url, json=data)

    def delete(self, traffic_type):
        url = "{}/{}".format(self.base_url, base.get_id(traffic_type))
        return self._delete(url)
