import json

from vinfra import exceptions
from vinfra.api import base


class Ssl(base.VinfraApi):
    def get(self):
        return self.client.get('/ssl')

    @staticmethod
    def _get_stream(stream):
        if not hasattr(stream, 'read'):
            try:
                stream = open(stream, 'rb')
            except Exception as err:
                raise exceptions.VinfraError(err)
        return stream

    def set(self, ssl, password=None, gen_cert=None, cert=None,
            key=None):
        data = {'ssl': ssl}
        if password:
            data['password'] = password
        if gen_cert:
            data['gen_cert'] = gen_cert

        # By default 'requests' treats files key as filename. Api needs 'form'
        # value, not 'file'. Forcing None as filename makes API be happy.
        files = {'json': (None, json.dumps(data))}

        if cert:
            files['cert'] = self._get_stream(cert)
        if key:
            files['key'] = self._get_stream(key)

        return self.client.put('/ssl', files=files)
