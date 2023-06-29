from vinfra.api import base
from vinfra.utils import flatten_args


class Filebeat(base.Resource):
    ID_ATTR = 'id'
    NAME_ATTR = 'name'


class FilebeatConfig(base.Manager):
    resource_class = Filebeat
    base_url = "/filebeat/nodes/config"
    base_url_advanced = "/filebeat/nodes/config/advanced"
    base_url_node = "/filebeat/nodes/{}/config"
    base_url_node_advanced = "/filebeat/nodes/{}/config/advanced"

    def list(self):
        return self._list(self.base_url)

    def get(self, node):
        node_id = base.get_id(node)
        return self._get(self.base_url_node.format(node_id))

    def put_elasticsearch_option_all_nodes(self, host, port, username, password):
        json = flatten_args(host=host, port=port, username=username, password=password)
        return self.client.put(self.base_url, json=json)

    def put_elasticsearch_option_one_node(self, node, host, port, username, password):
        node_id = base.get_id(node)
        json = flatten_args(host=host, port=port, username=username, password=password)
        return self._put(self.base_url_node.format(node_id), json=json)

    def put_raw_config_all_nodes(self, config):
        return self.client.put(self.base_url_advanced, json=config)

    def put_raw_config_one_node(self, node, config):
        node_id = base.get_id(node)
        return self._put(self.base_url_node_advanced.format(node_id), json=config)
