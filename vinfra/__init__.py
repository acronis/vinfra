from functools import partial

from vinfra import exceptions
from vinfra.api import base
from vinfra.api.alerts import AlertManager
from vinfra.api.alert_types import AlertTypeManager
from vinfra.api.auditlog import AuditLogManager
from vinfra.api.backup import BackupManager
from vinfra.api.clusters import ClusterManager
from vinfra.api.compute import Compute
from vinfra.api.cs.automatic_disk_replacement import AutomaticDiskReplacementSettings
from vinfra.api.cs.multiple_cses import MultipleCSesSettings
from vinfra.api.domains import DomainManager, UserDomainManager
from vinfra.api.domain_props import (
    DomainPropsManager, DomainPropsAccessManager, DomainsKeysManager
)
from vinfra.api.filebeat import FilebeatConfig
from vinfra.api.ha import HaConfig
from vinfra.api.locations import LocationsConfigManager, RoomsManager, RowsManager, RacksManager
from vinfra.api.logging_service import LogSeverityManager
from vinfra.api.memory_policies import (PerClusterMemoryPoliciesManager,
                                        PerNodeMemoryPoliciesManager)
from vinfra.api.misc import Dns
from vinfra.api.network import NetworkManager, TrafficTypeManager
from vinfra.api.nodes import NodeManager, Node
from vinfra.api.ram_reservation_info import RamReservationInfoManager
from vinfra.api.settings import LocaleManager, CsesConfigManager, NotificationsManager
from vinfra.api.software_updates import SoftwareUpdatesManager
from vinfra.api.ssl import Ssl
from vinfra.api.tasks import TaskManager
from vinfra.api.token import Token
from vinfra.api.users import UserManager
from vinfra.api_versions import APIVersion
from vinfra.client import Client
from vinfra.session import Session
from vinfra.utils import flatten_args


class _MemoryPoliciesManagerGroup(object):
    pass


class _AutomaticDiskReplacement(object):
    pass


class _MultipleCSes(object):
    pass


class _Locations(object):
    pass


class _LoggingService(object):
    pass


class _DomainProps(object):
    pass


class Vinfra(object):

    def _create_client(self, url, auth, session):
        if session is None:
            session = Session(url, auth=auth)
        elif not isinstance(session, Session):
            raise Exception("session must be Session type")
        self.session = session
        self.client = Client(self)

    def __init__(self, url, auth=None, session=None):
        self._create_client(url, auth, session)

        self.alerts = AlertManager(self)
        self.alert_types = AlertTypeManager(self)
        self.auditlog = AuditLogManager(self)
        self.backup = BackupManager(self)
        self.clusters = ClusterManager(self)
        self.compute = Compute(self)
        self.dns = Dns(self)
        self.domains = DomainManager(self)
        self.user_domains = UserDomainManager(self)
        self.email_notifications = NotificationsManager(self)
        self.filebeat = FilebeatConfig(self)
        self.ha = HaConfig(self)  # pylint: disable=invalid-name
        self.nodes = NodeManager(self)
        self.locales = LocaleManager(self)
        self.software_updates = SoftwareUpdatesManager(self)
        self.ssl = Ssl(self)
        self.tasks = TaskManager(self)
        self.token = Token(self)
        self.users = UserManager(self)

        self.networks = NetworkManager(self)
        self.traffic_types = TrafficTypeManager(self)

        self.memory_policies = _MemoryPoliciesManagerGroup()
        self.memory_policies.per_cluster = partial(PerClusterMemoryPoliciesManager, self)
        self.memory_policies.per_node = partial(PerNodeMemoryPoliciesManager, self)

        self.automatic_disk_replacement = _AutomaticDiskReplacement()
        self.automatic_disk_replacement.settings = AutomaticDiskReplacementSettings(self)
        self.multiple_cses = _MultipleCSes()
        self.multiple_cses.settings = MultipleCSesSettings(self)

        self.ram_reservation_info = RamReservationInfoManager(self)

        self.locations = _Locations()
        self.locations.configuration = LocationsConfigManager(self)
        self.locations.rooms = RoomsManager(self)
        self.locations.rows = RowsManager(self)
        self.locations.racks = RacksManager(self)

        self.logging_service = _LoggingService()
        self.logging_service.severity = LogSeverityManager(self)

        self.domain_props = _DomainProps()
        self.domain_props.properties = DomainPropsManager(self)
        self.domain_props.access = DomainPropsAccessManager(self)
        self.domain_props.keys = DomainsKeysManager(self)
        self.cses_config = CsesConfigManager(self)

        self._api_version = None
        self._backend_version = None
        self._request_id = None

    def node_obj(self, node_id):
        info = {"id": node_id}
        return Node(self.nodes, info)

    def get_cluster(self):
        clusters = self.clusters.list()
        if not clusters:
            raise exceptions.VinfraError("Cluster is not found")
        if len(clusters) > 1:
            raise exceptions.VinfraError("Several clusters found")
        return clusters[0]

    def get_api_version(self):
        storage_release = self.client.get("/about")['storage-release']
        if not storage_release:
            # i.e. local node is not registered
            raise exceptions.UnknownApiVersion(
                'Can not get backend API version.')
        return storage_release['version']

    def get_backend_version(self):
        return self.client.get("/version")["version"]

    @property
    def api_version(self):
        if not self._api_version:
            self._api_version = APIVersion(self.get_api_version())
        return self._api_version

    @property
    def backend_version(self):
        if not self._backend_version:
            self._backend_version = APIVersion(self.get_backend_version())
        return self._backend_version

    def report_async(self, send=None, contact_email=None,
                     problem_description=None, verbosity_level=None,
                     include_days=None, node_ids=None):
        json = flatten_args(send=send, contact_email=contact_email,
                            problem_description=problem_description,
                            verbosity_level=verbosity_level,
                            include_days=include_days, node_ids=node_ids)
        return self.client.post_async('/reports', json=json)

    def show_reports_settings(self):
        return self.client.get('/settings/reports/')

    def configure_report_async(self, report_type, enable=None, enable_sending=None, retry=None):
        command = ''
        if enable is True:
            command += 'enable'
        elif enable is False:
            command += 'disable'
        elif enable_sending is True:
            command += 'enable-sending'
        elif enable_sending is False:
            command += 'disable-sending'
        elif retry is True:
            command += 'retry'
        else:
            raise exceptions.VinfraError('Command is required')

        return self.client.post_async(
            '/settings/reports/{0}/{1}/'.format(report_type, command))

    @base.async_wait
    def report(self, **kwargs):
        return self.report_async(**kwargs)

    def get_meta(self):
        return self.client.get('/meta')
