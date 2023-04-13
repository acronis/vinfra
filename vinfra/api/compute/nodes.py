from vinfra.api import base


class Node(base.Resource):
    NAME_ATTR = 'host'

    def __init__(self, manager, info):
        info['placements'] = info.pop('traits')
        super(Node, self).__init__(manager, info)

    def fence(self, **kwargs):
        return self.manager.fence(self, **kwargs)

    def unfence(self):
        return self.manager.unfence(self)

    def delete(self, **kwargs):
        return self.manager.delete([self], **kwargs)

    def delete_async(self):
        return self.manager.delete_async([self])


class NodeManager(base.Manager):
    resource_class = Node
    base_url = "/compute/nodes"

    def _action(self, node, action, data=None):
        url = "{}/{}/{}".format(self.base_url, base.get_id(node), action)
        return self.client.post(url, json=data or {})

    def list(self):
        return self._list(self.base_url)

    def get(self, node, with_stats=False):
        node_id = base.get_id(node)
        url = "{}/{}".format(self.base_url, node_id)
        if with_stats:
            url += '?params={"with_stats":true}'
        return self._get(url)

    def add_async(self, nodes, roles, hypervisor_type=None, force=None):
        node_list = []
        for node in nodes:
            node_cfg = {
                'node_id': base.get_id(node),
                'roles': roles
            }
            if hypervisor_type is not None:
                node_cfg['hypervisor_type'] = hypervisor_type

            node_list.append(
                node_cfg
            )

        data = {'nodes': node_list}
        if force is not None:
            data['force'] = force
        task = self.client.put_async(self.base_url, json=data)
        return task

    @base.async_wait
    def add(self, *args, **kwargs):
        return self.add_async(*args, **kwargs)

    def delete_async(self, nodes, roles=None):
        node_list = []
        for node in nodes:
            node_list.append(
                {
                    'node_id': base.get_id(node),
                }
            )

        data = {'nodes': node_list}
        if roles:
            for _node in data['nodes']:
                _node['roles'] = roles

        task = self.client.delete_async(self.base_url, json=data)
        return task

    @base.async_wait
    def delete(self, nodes, roles):
        return self.delete_async(nodes, roles)

    def fence(self, node, reason=None, force_down=False):
        data = {}
        if reason:
            data['reason'] = reason
        if force_down:
            data['force_down'] = force_down
        return self._action(node, "fence", data=data)

    def unfence(self, node):
        return self._action(node, "unfence")
