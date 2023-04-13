# pylint: disable=line-too-long,no-self-use,no-member,useless-super-delegation

from vinfraclient.cmd.base import Lister

__all__ = ['ListDomainsKeys']


class ListDomainsKeys(Lister):
    _description = "Show all available keys for each known domain."
    _default_fields = ["domain", "keys"]

    @property
    def mgr(self):
        # noinspection PyUnresolvedReferences
        return self.app.vinfra.domain_props.keys

    def do_action(self, parsed_args):
        return self.mgr.list()
