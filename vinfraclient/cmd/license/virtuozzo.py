from vinfraclient.cmd.base import ShowOne


class ShowLicense(ShowOne):
    _description = "Show details of the installed license."

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        lic = cluster.virtuozzo_license.get()
        return lic


class LoadLicense(ShowOne):
    _description = "Load a license from a key."

    def configure_parser(self, parser):
        parser.add_argument(
            "key",
            metavar="<license-key>",
            help="License key to register",
        )

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        lic = cluster.virtuozzo_license.register(parsed_args.key)
        return lic


class UpdateLicense(ShowOne):
    _description = "Update the installed license."

    def configure_parser(self, parser):
        parser.add_argument(
            "--server",
            metavar="<ka-server>",
            help="Hostname[:port] of the key administration server"
        )

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        lic = cluster.virtuozzo_license.update(server=parsed_args.server)
        return lic
