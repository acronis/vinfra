import contextlib
import os
import sys

from requests.exceptions import HTTPError

from vinfra import session as vinfra_session
from vinfraclient import exceptions
from vinfraclient.compat import urlparse, cookielib
from vinfraclient.utils import get_password


@contextlib.contextmanager
def _reraise_vinfra_exception():
    try:
        yield
    except (OSError, IOError) as err:
        raise exceptions.VinfraError(err)


class Auth(vinfra_session.Auth):
    def __init__(self, username, password=None, domain=None, project=None):
        super(Auth, self).__init__(username, password,
                                   domain=domain, project=project)

    def make_authenticate(self, session):
        if not self.password:
            sys.stderr.write("Authentication user '{}' on {}:\n"
                             "".format(self.username, session.url))
            self.password = get_password("Password: ")
        try:
            super(Auth, self).make_authenticate(session)
        except HTTPError:
            # unset password to allow user repeat authenticate in the future
            # (e.g. in interact mode)
            self.password = None
            raise


class CachedAuth(Auth):

    def get_filename(self, session):
        hostname = urlparse(session.url).netloc.split(':')[0]
        dir_path = os.path.join(os.path.expanduser("~"), '.vinfra', hostname)
        filename = self.username
        if self.domain:
            filename += '.' + self.domain
        return os.path.join(dir_path, filename)

    def get_token_filename(self, session):
        filename = self.get_filename(session)
        return filename + '.' + self.project

    def _load_session_auth(self, session):
        filename = self.get_filename(session)
        if os.path.exists(filename):
            mz_cookie_jar = cookielib.MozillaCookieJar()
            try:
                mz_cookie_jar.load(filename=filename)
            except cookielib.LoadError:
                # file is empty or has a wrong format.
                return

            for cookie in mz_cookie_jar:
                session.cookies.set_cookie(cookie)

    def _load_project_auth(self, session):
        token_filename = self.get_token_filename(session)
        if os.path.exists(token_filename):
            with open(token_filename, 'r') as token_file:
                self.scoped_token = token_file.read()

    def _save_session_auth(self, session):
        filename = self.get_filename(session)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            with _reraise_vinfra_exception():
                os.makedirs(dirname, 0o700)
        mz_cookie_jar = cookielib.MozillaCookieJar()
        for cookie in session.cookies:
            mz_cookie_jar.set_cookie(cookie)

        with _reraise_vinfra_exception():
            mz_cookie_jar.save(filename)
            os.chmod(filename, 0o600)

    def _save_project_auth(self, session):
        token_filename = self.get_token_filename(session)

        with open(token_filename, 'w') as token_file:
            token_file.write(self.scoped_token)

        os.chmod(token_filename, 0o600)

    def needs_reauthenticate(self, session):
        need_reauth = super(CachedAuth, self).needs_reauthenticate(session)
        if need_reauth:
            self._load_session_auth(session)
            if self.project:
                self._load_project_auth(session)
        return super(CachedAuth, self).needs_reauthenticate(session)

    def make_authenticate(self, session):
        session.cookies.clear()
        super(CachedAuth, self).make_authenticate(session)

        self._save_session_auth(session)
        if self.project:
            self._save_project_auth(session)

    def save(self, session):
        self._save_session_auth(session)


class Session(vinfra_session.Session):
    def request(self, method, url, authenticated=True, **kwargs):  # pylint: disable=arguments-differ
        try:
            return super(Session, self).request(
                method, url, authenticated=authenticated, **kwargs)
        except HTTPError as exc:
            if not isinstance(self.auth, CachedAuth):
                raise

            elif (not authenticated or exc.response is None or
                  exc.response.status_code != 401):
                raise

            filename = self.auth.get_filename(self)
            if not os.path.exists(filename):
                raise

            if self.auth.project:
                filename = self.auth.get_token_filename(self)
                if not os.path.exists(filename):
                    raise

            # old cached session is loaded, needs reauthenticate
            self.auth.make_authenticate(self)
            return super(Session, self).request(method, url, **kwargs)
