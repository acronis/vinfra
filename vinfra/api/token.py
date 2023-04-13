import base64
import os
import sys
import time

from vinfra.api import base
from vinfra.api_versions import version_wrap

LINELEN = 64


# borrowed from backend sources:
def get_key_and_iv(password, salt, klen=32, ilen=16, msgdgst='md5'):
    mdf = getattr(__import__('hashlib', fromlist=[msgdgst]), msgdgst)
    password = password.encode('ascii', 'ignore')

    try:
        maxlen = klen + ilen
        keyiv = mdf(password + salt).digest()
        tmp = [keyiv]
        while len(tmp) < maxlen:
            tmp.append(mdf(tmp[-1] + password + salt).digest())
            keyiv += tmp[-1]
            key = keyiv[:klen]
            ivector = keyiv[klen:klen+ilen]
        return key, ivector
    except UnicodeDecodeError:
        return None, None


# borrowed from backend sources:
def encrypt(password, plaintext, chunk_it=True, msgdgst='md5'):
    '''
    Encription compatible with
    $ openssl enc -e -aes-256-cbc -base64 -salt  -pass pass:<password> -n \
      plaintext
    @param password text password
    @param input plaintext plain text to encode
    @returns base64 encoded string
    '''
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        if sys.platform == 'win32':
            sys.stderr.write('Please, make sure pycrypto is installed\n')
        raise

    salt = os.urandom(8)
    key, ivector = get_key_and_iv(password, salt, msgdgst=msgdgst)
    if key is None:
        return None

    # PKCS#7 padding
    padding_len = 16 - (len(plaintext) % 16)
    padded_plaintext = plaintext + (chr(padding_len) * padding_len)

    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(ivector))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Make openssl compatible.
    openssl_ciphertext = b'Salted__' + salt + ciphertext
    b64 = base64.b64encode(openssl_ciphertext)

    chunk = lambda s: '\n'.join(s[i: min(i + LINELEN, len(s))]
                                for i in range(0, len(s), LINELEN))
    return chunk(b64.decode()) if chunk_it else b64.decode()


# pylint: disable=function-redefined
class Token(base.VinfraApi):
    # @version_wrap("2.0", "2.latest")
    @version_wrap("2.0", "3.0.103")
    def get(self):
        return self.api.client.get("/nodes/registration/token")

    # @version_wrap("3.0")
    @version_wrap("3.0.104")
    def get(self):
        return self.api.client.post("/nodes/registration/token")

    # @version_wrap("2.0", "2.latest")
    @version_wrap("2.0", "3.0.103")
    def create(self, ttl=None):
        json = {'ttl': ttl}
        return self.api.client.post("/nodes/registration/token", json=json)

    # @version_wrap("3.0")
    @version_wrap("3.0.104")
    def create(self, ttl=None):
        json = {'ttl': ttl}
        return self.api.client.post("/nodes/registration/token/generation",
                                    json=json)

    def validate(self, token):
        plaintext = '{"stamp": "%s", "token": "%s"}' % (int(time.time()), token)
        json = {'data': encrypt(token, plaintext)}
        url = "/nodes/registration/token/validation"
        return self.api.client.post(url, json=json)
