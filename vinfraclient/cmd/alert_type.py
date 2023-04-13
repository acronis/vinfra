from vinfraclient.cmd.base import Lister


class ListAlertType(Lister):

    _description = "List alert types"
    _default_fields = ['type', 'group']

    def do_action(self, parsed_args):
        alert_types = self.app.vinfra.alert_types.list()
        return alert_types
