import yaml

from vinfra import exceptions as vinfra_exceptions
from vinfraclient import utils
from vinfraclient.cmd import base


def node_arg(parser):
    parser.add_argument(
        "node",
        metavar="<node>",
        help="Node ID or hostname."
    )


def elasticsearch_options(parser):
    parser.add_argument(
        "--node",
        metavar="<node>",
        help="Node ID or hostname.",
        default=None
    )
    parser.add_argument(
        "--host",
        metavar="<host>",
        help="Elasticsearch hostname or ip address."
    )
    parser.add_argument(
        "--port",
        metavar="<port>",
        default="9200",
        help="Elasticsearch port (default is 9200)."
    )
    parser.add_argument(
        "--username",
        metavar="<username>",
        help="Elasticsearch username."
    )
    parser.add_argument(
        "--password",
        metavar="<password>",
        help="Elasticsearch password."
    )


def filebeat_filename_arg(parser):
    parser.add_argument(
        "--node",
        metavar="<node>",
        help="Node ID or hostname.",
        default=None
    )
    parser.add_argument(
        "--filename",
        metavar="<filename>",
        help="Filebeat config filename (path to file) to upload."
    )


class ListFilebeatConfig(base.Lister):
    _description = "List Filebeat config."
    _default_fields = ['id', 'name', 'config']

    def do_action(self, parsed_args):
        filebeat_configs = self.app.vinfra.filebeat.list()
        return filebeat_configs


class ShowFilebeatConfig(base.Lister):
    _description = "Show Filebeat config."
    _default_fields = ['id', 'name', 'config']

    def configure_parser(self, parser):
        node_arg(parser)

    def do_action(self, parsed_args):
        return [self.app.vinfra.filebeat.get(parsed_args.node)]


class SetFilebeatConfig(base.Lister):
    _description = 'Set Filebeat config.'
    _default_fields = ['id', 'name', 'config']

    def configure_parser(self, parser):
        elasticsearch_options(parser)

    def do_action(self, parsed_args):
        if parsed_args.node:
            node = utils.find_resource(self.app.vinfra.nodes, parsed_args.node)
            fb_config = self.app.vinfra.filebeat.put_elasticsearch_option_one_node(
                node, parsed_args.host, parsed_args.port,
                parsed_args.username, parsed_args.password
            )
            return [fb_config]
        return self.app.vinfra.filebeat.put_elasticsearch_option_all_nodes(
            parsed_args.host, parsed_args.port,
            parsed_args.username, parsed_args.password
        )


class SetFilebeatConfigAdvanced(base.Lister):
    _description = 'Set Filebeat config.'
    _default_fields = ['id', 'name', 'config']

    def configure_parser(self, parser):
        filebeat_filename_arg(parser)

    def do_action(self, parsed_args):
        try:
            with open(parsed_args.filename) as stream:
                config = yaml.safe_load(stream)
        except IOError as err:
            raise vinfra_exceptions.VinfraError(
                'Cannot open Filebeat configuration file {}: {}'.format(
                    parsed_args.filename, err
                )
            )
        if parsed_args.node:
            node = utils.find_resource(self.app.vinfra.nodes, parsed_args.node)
            fb_config = self.app.vinfra.filebeat.put_raw_config_one_node(
                node, config
            )
            return [fb_config]
        return self.app.vinfra.filebeat.put_raw_config_all_nodes(config)
