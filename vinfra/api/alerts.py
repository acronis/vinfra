from vinfra.api import base
from vinfra.utils import flatten_args


class Alert(base.Resource):
    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)


class AlertManager(base.Manager):
    resource_class = Alert
    base_url = "/alerts"

    def list(self, enabled=False, lang='en'):
        url = self.base_url
        if not enabled:
            url += '?params={"filters":{"enabled":"False"}}'
        return self._list(url, cookies={'WebCP-Language': '{lang}'.format(lang=lang)})

    def update(self, alert, suspended=None, enabled=None):
        alert_id = base.get_id(alert)
        json = flatten_args(suspended=suspended, enabled=enabled)
        return self._put("{}/{}".format(self.base_url, alert_id), json)
