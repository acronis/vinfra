from vinfraclient.cmd import base


class ShowBackup(base.ShowOne):
    _description = "Show backup information"

    def do_action(self, parsed_args):
        return self.app.vinfra.backup.get()


class CreateBackup(base.TaskCommand):
    _description = "Create a backup"

    def do_action(self, parsed_args):
        return self.app.vinfra.backup.create_async()
