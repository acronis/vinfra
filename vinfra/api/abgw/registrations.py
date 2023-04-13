
from vinfra.api import base


class AbgwRegistration(base.Resource):

    @property
    def base_url(self):
        return "/{}/abgw/registrations/{}".format(
            base.get_id(self.manager.cluster), base.get_id(self)
        )

    def update(
            self,
            name=None,  # type: str
            address=None,  # type: str
            username=None,  # type: str
            password=None,  # type: str
    ):
        data = {}
        if name is not None:
            data['name'] = name
        if address is not None:
            data['address'] = address
        if username is not None:
            data['username'] = username
        if password is not None:
            data['password'] = password
        return self.manager.client.patch_async(self.base_url, json=data)

    def delete(
            self,
            username=None,  # type: str
            password=None,  # type: str
            force=False,  # type: bool
    ):
        data = {}
        if force:
            data['force'] = force
        if username and password:
            data = {
                'username': username,
                'password': password,
            }
        return self.manager.client.delete_async(self.base_url, json=data)


class AbgwRegistrationsApi(base.Manager):

    resource_class = AbgwRegistration

    def __init__(self, cluster):
        self.cluster = cluster
        super(AbgwRegistrationsApi, self).__init__(cluster.manager.api)

    @property
    def base_url(self):
        return "/{}/abgw/registrations".format(base.get_id(self.cluster))

    def create_async(
            self,
            name,  # type: str
            address,  # type: str
            account_server,  # type: str
            username,  # type: str
            password,  # type: str
            location=None,  # type: str
    ):
        data = {
            'name': name,
            'address': address,
            'account_server': account_server,
            'username': username,
            'password': password,
        }
        if location is not None:
            data['location'] = location
        return self.client.post_async(self.base_url, json=data)

    def create_true_image_async(
            self,
            name,  # type: str
            address,  # type: str
            revocation_url,  # type: str
            archived_certificates_chain,  # type: stream
    ):
        headers = {
            'x-hci-true-image-name': name,
            'x-hci-true-image-address': address,
            'x-hci-true-image-revocation-url': revocation_url,
            'Content-Type': 'application/octet-stream',
        }
        url = "/{}/abgw/true-image/registrations".format(
            base.get_id(self.cluster))
        return self.client.post_async(
            url,
            headers=headers,
            data=archived_certificates_chain
        )

    def get(
            self,
            registration,  # type: AbgwRegistration
    ):
        registration_id = base.get_id(registration)
        return self._get("{}/{}".format(self.base_url, registration_id))

    def list(self):
        return self._list(self.base_url)

    def renew_true_image_certificates(
            self,
            registration,
            archived_certificates_chain  # type: stream
    ):
        url = "/{}/abgw/true-image/registrations/{}".format(
            base.get_id(self.cluster),
            base.get_id(registration)
        )
        headers = {
            'Content-Type': 'application/octet-stream',
        }
        return self.client.put_async(
            url,
            headers=headers,
            data=archived_certificates_chain
        )

    def renew_certificates(
            self,
            registration,
            username,  # type: str
            password,  # type: str
    ):
        registration_id = base.get_id(registration)
        data = {
            'username': username,
            'password': password,
        }
        url = "{}/{}/renew".format(self.base_url, registration_id)
        return self.client.post_async(url, json=data)
