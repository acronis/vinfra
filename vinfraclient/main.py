import logging
import os
import signal
import sys
from argparse import ArgumentParser as _ArgumentParser

import pkg_resources
from cliff.app import App

from vinfra import log
from vinfra import Vinfra
from vinfraclient import commandmanager
from vinfraclient.compat import urlparse
from vinfraclient.session import CachedAuth
from vinfraclient.session import Session

LOG = logging.getLogger(__name__)


def normalize_portal(portal):
    parsed = urlparse(portal)
    if not parsed.scheme:
        parsed = urlparse("https://" + portal)
    elif parsed.scheme == 'http':
        sys.stderr.write(
            "'http' scheme is not supported, use 'https' instead.\n")
        sys.exit(2)
    if not parsed.port:
        parsed = parsed._replace(netloc="{}:8888".format(parsed.netloc))
    url = parsed.geturl()
    return url


def _description_from_file(lines):
    for line in lines:
        if line.lower().startswith('summary:'):
            _, _, description = line.partition(':')
            return description
    raise Exception('Summary is unset')


class ArgumentParser(_ArgumentParser):
    def parse_known_args(self, args=None, namespace=None):
        namespace, args = super(ArgumentParser, self).parse_known_args(
            args=args, namespace=namespace)

        # meet cliff parser requirements
        namespace.log_file = None
        namespace.debug = True

        return namespace, args


class VinfraApp(App):
    DEFAULT_VERBOSE_LEVEL = 1

    def __init__(self):
        dist = pkg_resources.get_distribution('vinfraclient')
        description = _description_from_file(dist._get_metadata(dist.PKG_INFO))  # pylint: disable=protected-access

        super(VinfraApp, self).__init__(
            description=description,
            version=dist.version,
            command_manager=commandmanager.CommandManager(dist),
            deferred_help=True,
        )
        self.vinfra = None

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = ArgumentParser(description=description, add_help=False)
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
        )
        verbose_group = parser.add_mutually_exclusive_group()
        verbose_group.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        verbose_group.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )
        parser.add_argument(
            '-h', '--help',
            dest='deferred_help',
            action='store_true',
            help="Show help message and exit.",
        )

        parser.add_argument(
            '--vinfra-portal',
            metavar='<portal>',
            dest='portal',
            default=os.environ.get('VINFRA_PORTAL',
                                   'backend-api.svc.vstoragedomain'),
            help='backend hostname or IP address (default: '
                 'backend-api.svc.vstoragedomain) [Env: VINFRA_PORTAL]')
        parser.add_argument(
            '--vinfra-username',
            metavar='<username>',
            dest='username',
            default=os.environ.get('VINFRA_USERNAME', 'admin'),
            help='The user name to authenticate with (default: "admin")'
                 ' [Env: VINFRA_USERNAME]')
        parser.add_argument(
            '--vinfra-password',
            metavar='<password>',
            dest='password',
            default=os.environ.get('VINFRA_PASSWORD'),
            help='The user password to authenticate with'
                 ' [Env: VINFRA_PASSWORD]')
        parser.add_argument(
            '--vinfra-domain',
            metavar='<domain>',
            dest='domain',
            default=os.environ.get('VINFRA_DOMAIN'),
            help='The domain name to authenticate with [Env: VINFRA_DOMAIN]')
        parser.add_argument(
            '--vinfra-project',
            metavar='<project>',
            dest='project',
            default=os.environ.get('VINFRA_PROJECT'),
            help='The project ID to authenticate with [Env: VINFRA_PROJECT]')

        return parser

    def configure_logging(self):
        log_filename = self._get_log_filename()
        log_level = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG
        }.get(self.options.verbose_level, logging.DEBUG)

        log.setup(filename=log_filename,
                  stream=self.stderr,
                  log_level=log_level)

        # stop spamming from third party libs
        for name in ('requests.packages.urllib3.connectionpool',
                     'urllib3.connectionpool',
                     'stevedore.extension'):
            logging.getLogger(name).setLevel(logging.WARNING)

    def interact(self):
        self._init_vinfra()
        self._init_auth()
        super(VinfraApp, self).interact()

    def prepare_to_run_command(self, cmd):
        if not cmd.client_required:
            return

        self.vinfra = self._init_vinfra()
        if cmd.auth_required and self.vinfra.session.auth is None:
            self._init_auth()

    def run_subcommand(self, argv):
        if argv[0] == 'help':
            # WA cliff to be unable print help with optional command args
            for arg in list(argv):
                if arg.startswith('-'):
                    argv.remove(arg)
        return super(VinfraApp, self).run_subcommand(argv)

    def _init_vinfra(self):
        if not self.vinfra:
            url = normalize_portal(self.options.portal)
            self.vinfra = Vinfra(url, session=Session(url))
        self.command_manager.init_plugins(self.vinfra)
        return self.vinfra

    def _init_auth(self):
        assert self.vinfra
        self.vinfra.session.auth = self._get_auth()

        if os.environ.get('TEST_VINFRA_MODE'):
            self.stderr.write(
                "The environment variable 'TEST_VINFRA_MODE' is deprecated "
                "and will be removed in the further. Please use a "
                "'VINFRA_TEST_MODE' environment variable.\n")
            os.environ['VINFRA_TEST_MODE'] = os.environ['TEST_VINFRA_MODE']
        if os.environ.get('VINFRA_TEST_MODE'):
            # For TESTING only. Admin must be authorized early with session
            # cached. Change TaskManager's 'api' for checking a task status.
            # Added to perform testing domain users who haven't access to the
            # task_detail endpoint.
            self.vinfra.tasks.api = Vinfra(
                self.vinfra.session.url, auth=CachedAuth("admin"))

    def _get_auth(self):
        # NOTE(akurbatov): password can be None, it will be prompted
        # ones command needs it.
        if not self.options.username:
            sys.stderr.write("Username is not set.\n")
            sys.exit(2)
        return CachedAuth(
            self.options.username,
            password=self.options.password,
            domain=self.options.domain,
            project=self.options.project,
        )

    @staticmethod
    def _get_log_filename():
        log_file = os.path.join(os.path.expanduser("~"), 'vinfra.log')

        log_fd = None
        if sys.platform == 'linux2' and os.path.exists('/etc/hci-release'):
            # try system logs at first
            _log_file = '/var/log/vinfra.log'
            try:
                log_fd = open(_log_file, 'a')
                log_file = _log_file
            except IOError:
                pass

        if not log_fd:
            try:
                log_fd = open(log_file, 'a')
            except IOError as err:
                sys.stderr.write(
                    "Logging setup failed: can't open {} ({})\n".format(
                        log_file, err.strerror))
                sys.exit(2)

        log_fd.close()
        return log_file

    def print_message(self, message, *args):
        if self.stderr.isatty() and self.options.verbose_level:
            if args:
                message = message % args
            self.stderr.write(message + '\n')

    def save_session(self):
        auth = self.vinfra.session.auth or self._get_auth()
        auth.save(self.vinfra.session)


def sigint_handler(signalnum, frame):
    # pylint: disable=unused-argument
    LOG.debug("Command interrupted by SIGINT")
    sys.exit(1)


def sigpipe_handler(signalnum, frame):
    # pylint: disable=unused-argument
    LOG.debug("Command interrupted by SIGPIPE")
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGPIPE, sigpipe_handler)

    ret = VinfraApp().run(sys.argv[1:])

    # flush stdout to avoid interpretator fail on stdout descriptor closing
    # See https://pmc.acronis.com/browse/VSTOR-17997
    try:
        sys.stdout.flush()
    except IOError:
        pass

    return ret


if __name__ == '__main__':
    sys.exit(main())
