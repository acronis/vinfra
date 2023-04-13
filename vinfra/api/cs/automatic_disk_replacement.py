from vinfra.api import base


class AutomaticDiskReplacementSettings(base.VinfraApi):

    __rel_path = '/cses/automatic-disk-replacement/settings/'

    def show_params(self):
        return self.client.get(self.__rel_path)

    def change_params(self, tier0=None, tier1=None, tier2=None, tier3=None):
        body = {}
        for tier, enabled in enumerate((tier0, tier1, tier2, tier3)):
            if enabled is None:
                continue
            body['tier%d' % tier] = enabled

        return self.client.put(self.__rel_path, json=body)
