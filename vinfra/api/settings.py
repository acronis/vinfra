from vinfra.api import base


class Locale(base.Resource):
    ID_ATTR = 'language'

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)


class LocaleManager(base.Manager):
    resource_class = Locale
    base_url = "/settings/locales"

    def list(self):
        return self._list(self.base_url, authenticated=False)

    def get(self, locale):
        locale_id = base.get_id(locale)
        return self._get("{}/{}".format(self.base_url, locale_id),
                         authenticated=False)

    def update(self, locale, enabled=None, is_default=None):
        locale_id = base.get_id(locale)

        data = {}
        if enabled is not None:
            data['enabled'] = enabled
        if is_default is not None:
            data['is_default'] = is_default

        url = "{}/{}".format(self.base_url, locale_id)
        return self._patch(url, json=data)


class CsesConfigManager(base.Manager):

    base_url = "/cses/config"

    def get(self):
        return self._get(self.base_url)

    def change_async(self, enable):
        return self._post_async(self.base_url, json={'rdma': enable})
