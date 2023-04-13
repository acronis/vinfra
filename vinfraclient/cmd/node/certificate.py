from vinfraclient.cmd import base
from vinfraclient.utils import find_resource


class RenewIPsecCert(base.TaskCommand):
    _description = "Generate new IPsec certificate for node"

    def configure_parser(self, parser):
        parser.add_argument(
            "node",
            help="Node ID or hostname"
        )

    def do_action(self, parsed_args):
        node = find_resource(self.app.vinfra.nodes, parsed_args.node)
        return self.app.vinfra.nodes.renew_ipsec_cert(node)
