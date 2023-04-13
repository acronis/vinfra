from vinfraclient.cmd.base import ShowOne, Command


class ShowLicense(ShowOne):
    _description = "Show details of the installed license."

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        lic = cluster.acronis_license.get()
        return lic


class LoadLicense(ShowOne):
    _description = "Load a license from a key."

    def configure_parser(self, parser):
        parser.add_argument(
            "--key",
            metavar="<license-key>",
            action="append",
            dest="keys",
            required=True,
            help="License key to register. Specify this option multiple times "
                 "to register multiple keys."
        )
        parser.add_argument(
            "--type",
            metavar="<license-type>",
            choices=['prolong', 'upgrade'],
            required=True,
            help="License type ('prolong' or 'upgrade')"
        )

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        lic = cluster.acronis_license.activate(parsed_args.keys,
                                               parsed_args.type)
        return lic


class TestLicense(ShowOne):
    _description = "Test a license key."

    def configure_parser(self, parser):
        parser.add_argument(
            "--key",
            metavar="<license-key>",
            action="append",
            dest="keys",
            required=True,
            help="License key to register. Specify this option multiple times "
                 "to test multiple keys."
        )
        parser.add_argument(
            "--type",
            metavar="<license-type>",
            choices=['prolong', 'upgrade'],
            required=True,
            help="License type ('prolong' or 'upgrade')"
        )

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        lic = cluster.acronis_license.test(parsed_args.keys,
                                           parsed_args.type)
        return lic


class UnregisterSPLALicense(Command):
    _description = "Deactivate the SPLA and unregister the cluster."

    def do_action(self, parsed_args):
        cluster = self.app.vinfra.get_cluster()
        return cluster.acronis_license.deactivate_spla()
