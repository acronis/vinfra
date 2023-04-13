from vinfra.api import base
from vinfra.api.compute.base import Manager


class SecurityGroup(base.Resource):
    def update(self, **params):
        return self.manager.update(self, **params)

    def delete(self):
        return self.manager.delete(self)


class SecurityGroupManager(Manager):
    resource_class = SecurityGroup
    base_url = "/compute/security-groups"

    def list(self, **list_params):
        return self._list(self.base_url, **list_params)

    def get(self, security_group):
        security_group_id = base.get_id(security_group)
        return self._get("{}/{}".format(self.base_url, security_group_id))

    def create(self, name, description=None):
        data = {'name': name}
        if description is not None:
            data['description'] = description
        return self._post(self.base_url, json=data)

    def delete(self, security_group):
        security_group_id = base.get_id(security_group)
        return self._delete("{}/{}".format(self.base_url, security_group_id))

    def update(self, security_group, name=None, description=None):
        security_group_id = base.get_id(security_group)

        params = {}
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description

        url = "{}/{}".format(self.base_url, security_group_id)
        return self._patch(url, json=params)


class SecurityGroupRule(base.Resource):
    def delete(self):
        return self.manager.delete(self)


class SecurityGroupRuleManager(Manager):
    resource_class = SecurityGroupRule
    base_url = "/compute/security-group-rules"

    def list(self, **list_params):
        return self._list(self.base_url, **list_params)

    def get(self, security_group):
        security_group_id = base.get_id(security_group)
        return self._get("{}/{}".format(self.base_url, security_group_id))

    def create(self, security_group, direction, remote_group=None,
               remote_ip_prefix=None, protocol=None, ethertype=None,
               port_range_max=None, port_range_min=None):
        data = {
            'security_group_id': base.get_id(security_group),
            'direction': direction,
        }
        if remote_group:
            data['remote_group_id'] = base.get_id(remote_group)
        if remote_ip_prefix:
            data['remote_ip_prefix'] = remote_ip_prefix
        if protocol:
            data['protocol'] = protocol
        if ethertype:
            data['ethertype'] = ethertype
        if port_range_max is not None:
            data['port_range_max'] = port_range_max
        if port_range_min is not None:
            data['port_range_min'] = port_range_min
        return self._post(self.base_url, json=data)

    def delete(self, security_group_rule):
        rule_id = base.get_id(security_group_rule)
        return self._delete("{}/{}".format(self.base_url, rule_id))
