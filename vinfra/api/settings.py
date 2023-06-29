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


class Notification(base.Resource):
    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)


class NotificationsManager(base.Manager):
    resource_class = Notification
    base_url = "/notifications/"

    def get(self):
        return self._get(self.base_url)

    def update(self, from_, sender_name, email_recipients_list, smtp_server, smtp_port,
               security, alerts_severities, user_account=None, user_password=None):
        json = {
            'notification_settings': {
                'from': from_,
                'alerts_severities': alerts_severities,
                'sender_name': sender_name,
                'email_recipients_list': email_recipients_list,
            },
            'smtp_settings': {
                'port': smtp_port,
                'connection_security': security,
                'smtp_server': smtp_server,
            },
        }
        if user_account:
            json['smtp_settings']['account_name'] = user_account
        if user_password:
            json['smtp_settings']['password'] = user_password

        return self._put(self.base_url, json=json)

    def patch(self, alert_severities):
        json = {
            'notification_settings': {
                'alerts_severities': alert_severities
            }
        }
        return self._put(self.base_url, json=json)
