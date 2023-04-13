from vinfraclient.cmd.base import Lister, TaskCommand
from vinfraclient.exceptions import ValidationError
from vinfraclient.utils import find_resource, get_cluster


class ListSshKey(Lister):
    _description = "Show the list of added SSH public keys."
    _default_fields = ['id', 'key', 'label']

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        sshkeys = cluster.sshkeys.list()
        return sshkeys


class CreateSshKey(TaskCommand):
    _description = "Add an SSH public key from a file."

    def configure_parser(self, parser):
        parser.add_argument(
            "file",
            metavar="<file>",
            help="SSH public key file"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        try:
            key = open(parsed_args.file).read()
        except Exception as err:
            raise ValidationError(
                "Cannot read SSH key from file {}: {}".format(
                    parsed_args.file, err))
        task = cluster.sshkeys.create_async(key)
        return task


class DeleteSshKey(TaskCommand):
    _description = "Remove an SSH public key from storage cluster nodes."

    def configure_parser(self, parser):
        parser.add_argument(
            "sshkey",
            metavar="<sshkey>",
            help="SSH key value"
        )

    def do_action(self, parsed_args):
        cluster = get_cluster(self.app.vinfra)
        sshkey = find_resource(cluster.sshkeys, parsed_args.sshkey)
        return sshkey.delete_async()
