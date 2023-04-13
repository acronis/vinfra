import socket

DNS_TLD = '.vstoragedomain'


def is_local_client():
    return socket.gethostname().endswith(DNS_TLD)


def is_remove_client():
    return not is_local_client()


def add_node_option(parser, required=True):
    hostname = socket.gethostname()
    if hostname.endswith(DNS_TLD):
        parser.add_argument(
            '--node',
            metavar="<node>",
            default=hostname,
            help="Node ID or hostname (default: {})".format(hostname)
        )
    elif required:
        parser.add_argument(
            '--node',
            metavar="<node>",
            required=True,
            help="Node ID or hostname"
        )
    else:
        parser.add_argument(
            '--node',
            metavar="<node>",
            help="Node ID or hostname"
        )
