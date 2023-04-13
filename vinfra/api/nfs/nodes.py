from vinfra import exceptions
from vinfra.api import base
from vinfra.utils import first


def get_api_nodes(nodes):
    res = []
    for node in nodes or []:
        res.append({
            'id': node['id'],
            'private_ip_address': node['ip_address'],
        })
    return res


class NfsNode(base.Resource):
    ID_ATTR = 'id'
    NAME_ATTR = 'ip_address'


class NodeManager(base.Manager):
    resource_class = NfsNode
    _ostor_private_traffic_type = 'OSTOR private'

    def __init__(self, cluster):
        self.cluster = cluster
        super(NodeManager, self).__init__(cluster.manager.api)

    @property
    def base_url(self):
        return "/{}/nfs/".format(base.get_id(self.cluster))

    def list(self):
        data = self.client.get(self.base_url)
        if isinstance(data, dict):
            data = data.get("nodes")
        nodes = [self.resource_class(self, res) for res in data or []]
        return nodes

    def get(self, node):
        node_id = base.get_id(node)
        return self._get("{}/{}".format(self.base_url, node_id))

    def assign_async(self, nodes):
        data = {
            'nodes': get_api_nodes(self._adjust_nodes(nodes))
        }
        url = "{}/assign-nodes".format(self.base_url)
        return self.client.post_async(url, json=data)

    def release_async(self, nodes):
        data = {
            'nodes': [
                {'id': base.get_id(node)} for node in nodes
            ],
        }
        url = "{}/release-nodes".format(self.base_url)
        return self.client.post_async(url, json=data)

    def _get_ostor_private_network(self):
        ostor_private_network = first(
            network for network in self.api.networks.list()
            if self._ostor_private_traffic_type in network.traffic_types
        )
        if not ostor_private_network:
            msg = "Network with traffic type {!r} not found".format(
                self._ostor_private_traffic_type)
            raise exceptions.VinfraError(msg)
        return ostor_private_network

    def _get_private_address(self, node, ostor_private_network):
        priv_iface = first(
            iface for iface in node.ifaces_manager.list()
            if iface.network == ostor_private_network.id
        )

        if not priv_iface:
            msg = "Traffic type {!r} is not assigned on node {!r}".format(
                self._ostor_private_traffic_type, node)
            raise exceptions.VinfraError(msg)

        if not priv_iface.ipv4:
            msg = "Interface {!r} on node {!r} does not have an " \
                  "IP address".format(priv_iface, node)
            raise exceptions.VinfraError(msg)

        if len(priv_iface.ipv4) > 1:
            msg = "Interface {!r} on node {!r} has a several IP addresses. " \
                  "Specify which one to use.".format(priv_iface, node)
            raise exceptions.VinfraError(msg)
        return priv_iface.ipv4[0].split('/')[0]

    def _adjust_nodes(self, nodes):
        for item in nodes:
            item['id'] = base.get_id(item['node'])

        if all((item['ip_address'] for item in nodes)):
            return nodes

        ostor_private_network = self._get_ostor_private_network()
        for item in nodes:
            if item['ip_address']:
                continue
            item['ip_address'] = self._get_private_address(
                item['node'], ostor_private_network)
        return nodes
