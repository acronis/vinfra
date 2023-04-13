from vinfra.api import base


class AlertType(base.Resource):
    pass


class AlertTypeManager(base.Manager):
    resource_class = AlertType
    base_url = "/alerts/types"

    def list(self):
        url = self.base_url
        return self._list(url)
