import subprocess
import sys

import os
import setuptools

VENDOR_ACRONIS = 'Acronis'
VENDOR_VIRTUOZZO = 'Virtuozzo'


def get_vendor():
    data = open('Makefile.incl').read()
    for line in data.splitlines():
        if line.startswith('VENDOR='):
            return line.split('=', 1)[-1]
    raise Exception('Vendor is not found')


vendor = get_vendor()


def install_requires(rfile):
    if not os.path.exists(rfile):
        return []
    pkgs = open(rfile).read().strip().splitlines()
    # NOTE(akurbatov): intentionally remove 'pycrypto' from requirements
    # because can't be installed on win32 without aditional C headers.
    if sys.platform == 'win32':
        pkgs = [pkg for pkg in pkgs if not pkg.startswith('cryptography')]
    return pkgs


def get_version():
    version = open('Makefile.version').read()
    if os.environ.get('RPM_BUILD_ROOT'):
        # it's rpm building
        return version
    if os.path.exists('.git'):
        # it's installation from sources
        args = ["git", "rev-parse", "--verify", "--short", "HEAD"]
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            shell=False,
        )
        out, err = p.communicate()
        ret = p.wait()
        if not ret:
            if isinstance(out, bytes):
                out = out.decode()
            return '{}+git.{}'.format(version, out.strip())
        elif ret == 127:  # no git tool
            return version
        sys.stderr.write(err + '\n')
        sys.exit(1)

    return version


def get_description():
    if vendor == VENDOR_VIRTUOZZO:
        return 'Command line client for Virtuozzo Infrastructure Platform'
    if vendor == VENDOR_ACRONIS:
        return 'Command line client for Acronis Cyber Infrastructure'

    raise NotImplementedError


# pylint: disable=line-too-long
vinfra_cli_cmds = [
    # locations
    'failure_domain_list = vinfraclient.cmd.location:ListFailureDomains',
    'failure_domain_rename = vinfraclient.cmd.location:ChangeFailureDomain',
    'location_list = vinfraclient.cmd.location:ListLocations',
    'location_create = vinfraclient.cmd.location:CreateLocation',
    'location_show = vinfraclient.cmd.location:ShowLocation',
    'location_rename = vinfraclient.cmd.location:UpdateLocation',
    'location_move = vinfraclient.cmd.location:MoveLocations',
    'location_delete = vinfraclient.cmd.location:DeleteLocation',

    # backup:
    'cluster_backup_create = vinfraclient.cmd.backup:CreateBackup',
    'cluster_backup_show = vinfraclient.cmd.backup:ShowBackup',

    # cluster:
    'cluster_create = vinfraclient.cmd.cluster:CreateCluster',
    'cluster_delete = vinfraclient.cmd.cluster:DeleteCluster',
    'cluster_overview = vinfraclient.cmd.cluster:Overview',
    'cluster_password_show = vinfraclient.cmd.cluster:ShowPassword',
    'cluster_password_reset = vinfraclient.cmd.cluster:SetPassword',
    'cluster_problem-report = vinfraclient.cmd.misc:ProblemReport',
    'cluster_show = vinfraclient.cmd.cluster:ShowCluster',
    'cluster_node_join-config_get = vinfraclient.cmd.cluster:GetJoinConfig',
    'cluster_node_join-config_set = vinfraclient.cmd.cluster:SetJoinConfig',
    'cluster_switch-to-ipv6 = vinfraclient.cmd.cluster:SwitchToIPv6',
    # cluster alerts
    'cluster_alert_delete = vinfraclient.cmd.alert:DeleteAlert',
    'cluster_alert_list = vinfraclient.cmd.alert:ListAlert',
    'cluster_alert_show = vinfraclient.cmd.alert:ShowAlert',
    # cluster alert types
    'cluster_alert_types_list = vinfraclient.cmd.alert_type:ListAlertType',
    # cluster auditlog
    'cluster_auditlog_list = vinfraclient.cmd.auditlog:ListAuditLog',
    'cluster_auditlog_show = vinfraclient.cmd.auditlog:ShowAuditLog',
    # ha
    'cluster_ha_show = vinfraclient.cmd.ha:HaShow',
    'cluster_ha_create = vinfraclient.cmd.ha:HaCreate',
    'cluster_ha_update = vinfraclient.cmd.ha:HaUpdate',
    'cluster_ha_delete = vinfraclient.cmd.ha:HaDelete',
    'cluster_ha_node_add = vinfraclient.cmd.ha:AddNodeToHA',
    'cluster_ha_node_remove = vinfraclient.cmd.ha:RemoveNodeFromHA',
    # cluster network (aka roles-sets)
    'cluster_network_create = vinfraclient.cmd.network:CreateNetwork',
    'cluster_network_delete = vinfraclient.cmd.network:DeleteNetwork',
    'cluster_network_list = vinfraclient.cmd.network:ListNetwork',
    'cluster_network_set = vinfraclient.cmd.network:SetNetwork',
    'cluster_network_set-bulk = vinfraclient.cmd.network:SetNetworkBulk',
    'cluster_network_show = vinfraclient.cmd.network:ShowNetwork',
    'cluster_network_migration_start = vinfraclient.cmd.network:NetworkMigrationStart',
    'cluster_network_migration_show = vinfraclient.cmd.network:NetworkMigrationDetails',
    'cluster_network_migration_apply = vinfraclient.cmd.network:NetworkMigrationApply',
    'cluster_network_migration_revert = vinfraclient.cmd.network:NetworkMigrationRevert',
    'cluster_network_migration_retry = vinfraclient.cmd.network:NetworkMigrationRetry',
    'cluster_network_migration_resume = vinfraclient.cmd.network:NetworkMigrationResume',
    'cluster_network_conversion_start = vinfraclient.cmd.network:NetworkConversionStart',
    'cluster_network_conversion_status = vinfraclient.cmd.network:NetworkConversionStatus',
    'cluster_network_conversion_precheck = vinfraclient.cmd.network:NetworkConversionPrecheck',
    'cluster_network_encryption_enable = vinfraclient.cmd.network:NetworkEncryptionEnable',
    'cluster_network_encryption_disable = vinfraclient.cmd.network:NetworkEncryptionDisable',
    'cluster_network_encryption_cancel = vinfraclient.cmd.network:NetworkEncryptionCancel',
    'cluster_network_encryption_status = vinfraclient.cmd.network:NetworkEncryptionStatus',
    'cluster_network_encryption_bypass_add = vinfraclient.cmd.network:NetworkEncryptionBypassAdd',
    'cluster_network_encryption_bypass_delete = vinfraclient.cmd.network:NetworkEncryptionBypassDel',
    'cluster_network_encryption_bypass_list = vinfraclient.cmd.network:NetworkEncryptionBypassList',
    'cluster_network_ipv6-prefix_assign = vinfraclient.cmd.network:AssignIPv6Prefix',
    'cluster_network_ipv6-prefix_remove = vinfraclient.cmd.network:RemoveIPv6Prefix',
    'cluster_network_ipv6-prefix_show = vinfraclient.cmd.network:IPv6Prefix',
    # cluster settings
    'cluster_settings_encryption_set = vinfraclient.cmd.settings:SetClusterEncryption',
    'cluster_settings_encryption_show = vinfraclient.cmd.settings:ShowClusterEncryption',
    'cluster_settings_dns_set = vinfraclient.cmd.settings:SetDns',
    'cluster_settings_dns_show = vinfraclient.cmd.settings:ShowDns',
    'cluster_settings_locale_list = vinfraclient.cmd.settings:ListLocale',
    'cluster_settings_locale_show = vinfraclient.cmd.settings:ShowLocale',
    'cluster_settings_locale_set = vinfraclient.cmd.settings:UpdateLocale',
    'cluster_settings_ssl_show = vinfraclient.cmd.ssl:ShowSsl',
    'cluster_settings_ssl_set = vinfraclient.cmd.ssl:SetSsl',
    'cluster_settings_automatic-disk-replacement_show = vinfraclient.cmd.cs.automatic_disk_replacement:ShowSettings',
    'cluster_settings_automatic-disk-replacement_set = vinfraclient.cmd.cs.automatic_disk_replacement:ChangeSettings',
    'cluster_settings_number-of-cses-per-disk_show = vinfraclient.cmd.cs.multiple_cses:ShowSettings',
    'cluster_settings_number-of-cses-per-disk_set = vinfraclient.cmd.cs.multiple_cses:ChangeSettings',
    'cluster_settings_report_set = vinfraclient.cmd.misc:SetReportSettings',
    'cluster_settings_report_show = vinfraclient.cmd.misc:ShowReportSettings',
    # cluster sshkey
    'cluster_sshkey_add = vinfraclient.cmd.sshkey:CreateSshKey',
    'cluster_sshkey_delete = vinfraclient.cmd.sshkey:DeleteSshKey',
    'cluster_sshkey_list = vinfraclient.cmd.sshkey:ListSshKey',
    # deprecated: cluster storage-policies
    'cluster_storage-policy_create = vinfraclient.cmd.compute.storage_policy:CreateStoragePolicy',
    'cluster_storage-policy_delete = vinfraclient.cmd.compute.storage_policy:DeleteStoragePolicy',
    'cluster_storage-policy_list = vinfraclient.cmd.compute.storage_policy:ListStoragePolicy',
    'cluster_storage-policy_set = vinfraclient.cmd.compute.storage_policy:SetStoragePolicy',
    'cluster_storage-policy_show = vinfraclient.cmd.compute.storage_policy:ShowStoragePolicy',
    # cluster traffic-type (aka roles)
    'cluster_traffic-type_create = vinfraclient.cmd.network:CreateTrafficType',
    'cluster_traffic-type_delete = vinfraclient.cmd.network:DeleteTrafficType',
    'cluster_traffic-type_list = vinfraclient.cmd.network:ListTrafficType',
    'cluster_traffic-type_set = vinfraclient.cmd.network:SetTrafficType',
    'cluster_traffic-type_show = vinfraclient.cmd.network:ShowTrafficType',
    'cluster_traffic-type_assignment_start = vinfraclient.cmd.network:TrafficTypeAssignmentStart',
    'cluster_traffic-type_assignment_show = vinfraclient.cmd.network:TrafficTypeAssignmentDetails',
    'cluster_traffic-type_assignment_apply = vinfraclient.cmd.network:TrafficTypeAssignmentApply',
    'cluster_traffic-type_assignment_revert = vinfraclient.cmd.network:TrafficTypeAssignmentRevert',
    'cluster_traffic-type_assignment_retry = vinfraclient.cmd.network:TrafficTypeAssignmentRetry',
    'cluster_network_reconfiguration_show = vinfraclient.cmd.network:NetworkReconfigurationDetails',
    # cluster users
    'cluster_user_create = vinfraclient.cmd.user:CreateUser',
    'cluster_user_change-password = vinfraclient.cmd.user:ChangePasword',
    'cluster_user_delete = vinfraclient.cmd.user:DeleteUser',
    'cluster_user_list = vinfraclient.cmd.user:ListUser',
    'cluster_user_list-available-roles = vinfraclient.cmd.user:ListRoles',
    'cluster_user_set = vinfraclient.cmd.user:SetUser',
    'cluster_user_show = vinfraclient.cmd.user:ShowUser',

    # domains
    'domain_delete = vinfraclient.cmd.domain:DeleteDomain',
    'domain_create = vinfraclient.cmd.domain:CreateDomain',
    'domain_list = vinfraclient.cmd.domain:ListDomains',
    'domain_set = vinfraclient.cmd.domain:SetDomain',
    'domain_show = vinfraclient.cmd.domain:ShowDomain',
    # domain idps
    'domain_idp_create = vinfraclient.cmd.domain.idp:CreateDomainIdP',
    'domain_idp_list = vinfraclient.cmd.domain.idp:ListDomainIdPs',
    'domain_idp_delete = vinfraclient.cmd.domain.idp:DeleteDomainIdP',
    'domain_idp_set = vinfraclient.cmd.domain.idp:SetDomainIdP',
    'domain_idp_show = vinfraclient.cmd.domain.idp:ShowDomainIdP',
    'domain_idp_login = vinfraclient.cmd.domain.idp:LoginDomainIdP',
    # domain projects
    'domain_project_create = vinfraclient.cmd.domain.project:CreateDomainProject',
    'domain_project_list = vinfraclient.cmd.domain.project:ListDomainProjects',
    'domain_project_delete = vinfraclient.cmd.domain.project:DeleteDomainProject',
    'domain_project_set = vinfraclient.cmd.domain.project:SetDomainProject',
    'domain_project_show = vinfraclient.cmd.domain.project:ShowDomainProject',
    # domain projects users
    'domain_project_user_list = vinfraclient.cmd.domain.project:ListProjectUsers',
    'domain_project_user_remove = vinfraclient.cmd.domain.project:RemoveProjectUser',
    # domain users
    'domain_user_create = vinfraclient.cmd.domain.user:CreateDomainUser',
    'domain_user_delete = vinfraclient.cmd.domain.user:DeleteDomainUser',
    'domain_user_list = vinfraclient.cmd.domain.user:ListDomainUser',
    'domain_user_set = vinfraclient.cmd.domain.user:SetDomainUser',
    'domain_user_show = vinfraclient.cmd.domain.user:ShowDomainUser',
    'domain_user_list-available-roles=vinfraclient.cmd.user:ListRoles',
    'domain_user_group_list = vinfraclient.cmd.domain.user:ListDomainUserGroups',
    'domain_user_unlock = vinfraclient.cmd.domain.user:UnlockDomainUser',
    # domain groups
    'domain_group_create = vinfraclient.cmd.domain.group:CreateDomainGroup',
    'domain_group_delete = vinfraclient.cmd.domain.group:DeleteDomainGroup',
    'domain_group_list = vinfraclient.cmd.domain.group:ListDomainGroup',
    'domain_group_set = vinfraclient.cmd.domain.group:SetDomainGroup',
    'domain_group_show = vinfraclient.cmd.domain.group:ShowDomainGroup',
    'domain_group_user_list = vinfraclient.cmd.domain.group:ListDomainGroupUsers',
    'domain_group_user_remove = vinfraclient.cmd.domain.group:RemoveDomainGroupUser',
    'domain_group_user_add = vinfraclient.cmd.domain.group:AddDomainGroupUser',
    # node:
    'node_forget = vinfraclient.cmd.node:ForgetNode',
    'node_join = vinfraclient.cmd.node:JoinNode',
    'node_list = vinfraclient.cmd.node:ListNode',
    'node_release = vinfraclient.cmd.node:ReleaseNode',
    'node_show = vinfraclient.cmd.node:ShowNode',
    # maintenance node
    'node_maintenance_status = vinfraclient.cmd.node:MaintenanceNodeStatus',
    'node_maintenance_start = vinfraclient.cmd.node:MaintenanceNodeStart',
    'node_maintenance_stop = vinfraclient.cmd.node:MaintenanceNodeStop',
    'node_maintenance_precheck = vinfraclient.cmd.node:MaintenanceNodePrecheck',
    # node disk
    'node_disk_assign = vinfraclient.cmd.node.disk:AssignDiskBulk',
    'node_disk_blink_on = vinfraclient.cmd.node.disk:StartBlinkDisk',
    'node_disk_blink_off = vinfraclient.cmd.node.disk:StopBlinkDisk',
    'node_disk_list = vinfraclient.cmd.node.disk:ListDisk',
    # 'node_disk_recover = vinfraclient.cmd.node.disk:RecoverDisk',
    'node_disk_release = vinfraclient.cmd.node.disk:ReleaseDisk',
    'node_disk_show = vinfraclient.cmd.node.disk:ShowDisk',
    'node_disk_show_diagnostic-info = vinfraclient.cmd.node.disk:ShowDiskDiagnosticInfo',
    # node network (deprecated)
    'node_network_bond_create = vinfraclient.cmd.deprecated:CreateBond',
    'node_network_bond_delete = vinfraclient.cmd.deprecated:DeleteBond',
    'node_network_iface_delete = vinfraclient.cmd.deprecated:DeleteIface',
    'node_network_iface_down = vinfraclient.cmd.deprecated:DownIface',
    'node_network_iface_list = vinfraclient.cmd.deprecated:ListIface',
    'node_network_iface_show = vinfraclient.cmd.deprecated:ShowIface',
    'node_network_iface_set = vinfraclient.cmd.deprecated:SetIface',
    'node_network_iface_up = vinfraclient.cmd.deprecated:UpIface',
    'node_network_vlan_create = vinfraclient.cmd.deprecated:CreateVlan',
    'node_network_vlan_delete = vinfraclient.cmd.deprecated:DeleteVlan',
    # node iface
    'node_iface_create-bond = vinfraclient.cmd.node.iface:CreateBond',
    'node_iface_create-vlan = vinfraclient.cmd.node.iface:CreateVlan',
    'node_iface_delete = vinfraclient.cmd.node.iface:DeleteIface',
    'node_iface_down = vinfraclient.cmd.node.iface:DownIface',
    'node_iface_list = vinfraclient.cmd.node.iface:ListIface',
    'node_iface_show = vinfraclient.cmd.node.iface:ShowIface',
    'node_iface_set = vinfraclient.cmd.node.iface:SetIface',
    'node_iface_up = vinfraclient.cmd.node.iface:UpIface',
    # node iscsi
    'node_iscsi_target_add = vinfraclient.cmd.node.iscsi:ConnectTarget',
    'node_iscsi_target_delete = vinfraclient.cmd.node.iscsi:DisconnectTarget',
    # 'node_iscsi_target_show = vinfraclient.cmd.node.iscsi:ShowTarget',
    # node token
    'node_token_create = vinfraclient.cmd.token:CreateToken',
    'node_token_show = vinfraclient.cmd.token:ShowToken',
    'node_token_validate = vinfraclient.cmd.token:ValidateToken',
    # node ram-reservation-info
    'node_ram-reservation_list = vinfraclient.cmd.ram_reservation_info:ShowNodesRamReservationInfo',
    'node_ram-reservation_show = vinfraclient.cmd.ram_reservation_info:ShowNodeRamReservationInfo',
    'node_ram-reservation_total = vinfraclient.cmd.ram_reservation_info:ShowTotalRamReservationInfo',
    # certificates
    'node_certificate_ipsec_renew = vinfraclient.cmd.node.certificate:RenewIPsecCert',
    # service compute
    'service_compute_create = vinfraclient.cmd.compute.cluster:CreateCompute',
    'service_compute_delete = vinfraclient.cmd.compute.cluster:DeleteCompute',
    'service_compute_set = vinfraclient.cmd.compute.cluster:SetCompute',
    'service_compute_show = vinfraclient.cmd.compute.cluster:ShowCompute',
    'service_compute_stat = vinfraclient.cmd.compute.cluster:ClusterStat',
    'service_compute_baseline-cpu = vinfraclient.cmd.compute.cluster:BaselineCPU',
    'service_compute_task_show = vinfraclient.cmd.compute.cluster:ShowTask',
    'service_compute_task_retry = vinfraclient.cmd.compute.cluster:RetryTask',
    'service_compute_task_abort = vinfraclient.cmd.compute.cluster:AbortTask',
    # compute cluster (deprecated):
    'service_compute_cluster_create = vinfraclient.cmd.deprecated:CreateCompute',
    'service_compute_cluster_delete = vinfraclient.cmd.deprecated:DeleteCompute',
    'service_compute_cluster_set = vinfraclient.cmd.deprecated:SetCompute',
    'service_compute_cluster_show = vinfraclient.cmd.deprecated:ShowCompute',
    'service_compute_cluster_stat = vinfraclient.cmd.deprecated:ClusterStat',
    # compute flavor
    'service_compute_flavor_create = vinfraclient.cmd.compute.flavor:CreateFlavor',
    'service_compute_flavor_delete = vinfraclient.cmd.compute.flavor:DeleteFlavor',
    'service_compute_flavor_list = vinfraclient.cmd.compute.flavor:ListFlavor',
    'service_compute_flavor_show = vinfraclient.cmd.compute.flavor:ShowFlavor',
    # compute image
    'service_compute_image_create = vinfraclient.cmd.compute.image:CreateImage',
    'service_compute_image_delete = vinfraclient.cmd.compute.image:DeleteImage',
    'service_compute_image_list = vinfraclient.cmd.compute.image:ListImage',
    'service_compute_image_set = vinfraclient.cmd.compute.image:SetImage',
    'service_compute_image_save = vinfraclient.cmd.compute.image:SaveImage',
    'service_compute_image_show = vinfraclient.cmd.compute.image:ShowImage',
    # compute ssh key
    'service_compute_key_create = vinfraclient.cmd.compute.key:CreateComputeSshKey',
    'service_compute_key_delete = vinfraclient.cmd.compute.key:DeleteComputeSshKey',
    'service_compute_key_list = vinfraclient.cmd.compute.key:ListComputeSshKey',
    'service_compute_key_show = vinfraclient.cmd.compute.key:ShowComputeSshKey',
    # compute network
    'service_compute_network_list = vinfraclient.cmd.compute.network:ListNetwork',
    'service_compute_network_create = vinfraclient.cmd.compute.network:CreateNetwork',
    'service_compute_network_delete = vinfraclient.cmd.compute.network:DeleteNetwork',
    'service_compute_network_set = vinfraclient.cmd.compute.network:SetNetwork',
    'service_compute_network_show = vinfraclient.cmd.compute.network:ShowNetwork',
    # compute subnet
    'service_compute_subnet_list = vinfraclient.cmd.compute.network:ListSubnet',
    'service_compute_subnet_create = vinfraclient.cmd.compute.network:CreateSubnet',
    'service_compute_subnet_delete = vinfraclient.cmd.compute.network:DeleteSubnet',
    'service_compute_subnet_set = vinfraclient.cmd.compute.network:SetSubnet',
    'service_compute_subnet_show = vinfraclient.cmd.compute.network:ShowSubnet',
    # compute floatingip
    'service_compute_floatingip_list = vinfraclient.cmd.compute.floating_ip:ListFloatingIps',
    'service_compute_floatingip_create = vinfraclient.cmd.compute.floating_ip:CreateFloatingIp',
    'service_compute_floatingip_delete = vinfraclient.cmd.compute.floating_ip:DeleteFloatingIp',
    'service_compute_floatingip_set = vinfraclient.cmd.compute.floating_ip:SetFloatingIp',
    'service_compute_floatingip_show = vinfraclient.cmd.compute.floating_ip:ShowFloatingIp',
    # compute router
    'service_compute_router_list = vinfraclient.cmd.compute.router:ListRouters',
    'service_compute_router_create = vinfraclient.cmd.compute.router:CreateRouter',
    'service_compute_router_delete = vinfraclient.cmd.compute.router:DeleteRouter',
    'service_compute_router_set = vinfraclient.cmd.compute.router:SetRouter',
    'service_compute_router_show = vinfraclient.cmd.compute.router:ShowRouter',
    # compute node
    'service_compute_node_list = vinfraclient.cmd.compute.node:ListNode',
    'service_compute_node_show = vinfraclient.cmd.compute.node:ShowNode',
    'service_compute_node_add = vinfraclient.cmd.compute.cluster:AddNode',
    'service_compute_node_release = vinfraclient.cmd.compute.cluster:DeleteNode',
    'service_compute_node_fence = vinfraclient.cmd.compute.node:FenceNode',
    'service_compute_node_unfence = vinfraclient.cmd.compute.node:UnfenceNode',
    # compute security-group
    'service_compute_security-group_list = vinfraclient.cmd.compute.security_group:ListSecurityGroup',
    'service_compute_security-group_create = vinfraclient.cmd.compute.security_group:CreateSecurityGroup',
    'service_compute_security-group_delete = vinfraclient.cmd.compute.security_group:DeleteSecurityGroup',
    'service_compute_security-group_set = vinfraclient.cmd.compute.security_group:SetSecurityGroup',
    'service_compute_security-group_show = vinfraclient.cmd.compute.security_group:ShowSecurityGroup',
    # compute security-group rule
    'service_compute_security-group_rule_list = vinfraclient.cmd.compute.security_group:ListSecurityGroupRule',
    'service_compute_security-group_rule_create = vinfraclient.cmd.compute.security_group:CreateSecurityGroupRule',
    'service_compute_security-group_rule_delete = vinfraclient.cmd.compute.security_group:DeleteSecurityGroupRule',
    'service_compute_security-group_rule_show = vinfraclient.cmd.compute.security_group:ShowSecurityGroupRule',
    # compute server
    'service_compute_server_console = vinfraclient.cmd.compute.server:ConsoleServer',
    'service_compute_server_create = vinfraclient.cmd.compute.server:CreateServer',
    'service_compute_server_delete = vinfraclient.cmd.compute.server:DeleteServer',
    'service_compute_server_evacuate = vinfraclient.cmd.compute.server:EvacuateServer',
    'service_compute_server_list = vinfraclient.cmd.compute.server:ListServer',
    'service_compute_server_log = vinfraclient.cmd.compute.server:LogServer',
    'service_compute_server_migrate = vinfraclient.cmd.compute.server:MigrateServer',
    'service_compute_server_pause = vinfraclient.cmd.compute.server:PauseServer',
    'service_compute_server_reboot = vinfraclient.cmd.compute.server:RebootServer',
    'service_compute_server_rescue = vinfraclient.cmd.compute.server:RescueServer',
    'service_compute_server_reset-state = vinfraclient.cmd.compute.server:ResetServerState',
    'service_compute_server_resize = vinfraclient.cmd.compute.server:ResizeServer',
    'service_compute_server_resume = vinfraclient.cmd.compute.server:ResumeServer',
    'service_compute_server_set = vinfraclient.cmd.compute.server:SetServer',
    'service_compute_server_shelve = vinfraclient.cmd.compute.server:ShelveServer',
    'service_compute_server_show = vinfraclient.cmd.compute.server:ShowServer',
    'service_compute_server_start = vinfraclient.cmd.compute.server:StartServer',
    'service_compute_server_stat = vinfraclient.cmd.compute.server:StatServer',
    'service_compute_server_stop = vinfraclient.cmd.compute.server:StopServer',
    'service_compute_server_cancel-stop = vinfraclient.cmd.compute.server:CancelStopServer',
    'service_compute_server_suspend = vinfraclient.cmd.compute.server:SuspendServer',
    'service_compute_server_unpause = vinfraclient.cmd.compute.server:UnpauseServer',
    'service_compute_server_unrescue = vinfraclient.cmd.compute.server:UnrescueServer',
    'service_compute_server_unshelve = vinfraclient.cmd.compute.server:UnshelveServer',
    # compute server iface
    'service_compute_server_iface_attach = vinfraclient.cmd.compute.server:NetworkAttach',
    'service_compute_server_iface_set = vinfraclient.cmd.compute.server:NetworkUpdate',
    'service_compute_server_iface_detach = vinfraclient.cmd.compute.server:NetworkDetach',
    'service_compute_server_iface_list = vinfraclient.cmd.compute.server:NetworkList',
    # compute server volume
    'service_compute_server_volume_attach = vinfraclient.cmd.compute.server:VolumeAttach',
    'service_compute_server_volume_detach = vinfraclient.cmd.compute.server:VolumeDetach',
    'service_compute_server_volume_show = vinfraclient.cmd.compute.server:VolumeShow',
    'service_compute_server_volume_list = vinfraclient.cmd.compute.server:VolumeList',
    # compute server metadata
    'service_compute_server_meta_set = vinfraclient.cmd.compute.server:MetadataSet',
    'service_compute_server_meta_unset = vinfraclient.cmd.compute.server:MetadataUnset',
    # compute server tag
    'service_compute_server_tag_add = vinfraclient.cmd.compute.server:TagAdd',
    'service_compute_server_tag_delete = vinfraclient.cmd.compute.server:TagDelete',
    'service_compute_server_tag_list = vinfraclient.cmd.compute.server:TagList',
    # compute server event
    'service_compute_server_event_list = vinfraclient.cmd.compute.server:EventList',
    'service_compute_server_event_show = vinfraclient.cmd.compute.server:EventShow',
    # compute volume
    'service_compute_volume_create = vinfraclient.cmd.compute.volume:CreateVolume',
    'service_compute_volume_delete = vinfraclient.cmd.compute.volume:DeleteVolume',
    'service_compute_volume_extend = vinfraclient.cmd.compute.volume:ExtendVolume',
    'service_compute_volume_list = vinfraclient.cmd.compute.volume:ListVolume',
    'service_compute_volume_show = vinfraclient.cmd.compute.volume:ShowVolume',
    'service_compute_volume_set = vinfraclient.cmd.compute.volume:SetVolume',
    'service_compute_volume_clone = vinfraclient.cmd.compute.volume:CloneVolume',
    'service_compute_volume_upload-to-image = vinfraclient.cmd.compute.volume:UploadToImage',
    'service_compute_volume_reset-state = vinfraclient.cmd.compute.volume:ResetVolumeState',
    # compute volume snapshot
    'service_compute_volume_snapshot_create = vinfraclient.cmd.compute.volume_snapshot:CreateVolumeSnapshot',
    'service_compute_volume_snapshot_delete = vinfraclient.cmd.compute.volume_snapshot:DeleteVolumeSnapshot',
    'service_compute_volume_snapshot_list = vinfraclient.cmd.compute.volume_snapshot:ListVolumeSnapshot',
    'service_compute_volume_snapshot_show = vinfraclient.cmd.compute.volume_snapshot:ShowVolumeSnapshot',
    'service_compute_volume_snapshot_set = vinfraclient.cmd.compute.volume_snapshot:SetVolumeSnapshot',
    'service_compute_volume_snapshot_upload-to-image = vinfraclient.cmd.compute.volume_snapshot:UploadToImage',
    'service_compute_volume_snapshot_reset-state = vinfraclient.cmd.compute.volume_snapshot:ResetVolumeSnapshotState',
    'service_compute_volume_snapshot_revert = vinfraclient.cmd.compute.volume_snapshot:RevertToSnapshot',
    # compute router iface
    'service_compute_router_iface_add = vinfraclient.cmd.compute.router:RouterInterfaceAdd',
    'service_compute_router_iface_remove = vinfraclient.cmd.compute.router:RouterInterfaceRemove',
    'service_compute_router_iface_list = vinfraclient.cmd.compute.router:RouterInterfaceList',
    # compute quotas
    'service_compute_quotas_show = vinfraclient.cmd.compute.quotas:ShowComputeQuotas',
    'service_compute_quotas_update = vinfraclient.cmd.compute.quotas:UpdateComputeQuotas',
    # compute k8saas
    'service_compute_k8saas_create = vinfraclient.cmd.compute.k8saas:CreateK8saasCluster',
    'service_compute_k8saas_delete = vinfraclient.cmd.compute.k8saas:DeleteK8saasCluster',
    'service_compute_k8saas_list = vinfraclient.cmd.compute.k8saas:ListK8saasCluster',
    'service_compute_k8saas_show = vinfraclient.cmd.compute.k8saas:ShowK8saasCluster',
    'service_compute_k8saas_config = vinfraclient.cmd.compute.k8saas:ShowK8saasClusterConfig',
    'service_compute_k8saas_set = vinfraclient.cmd.compute.k8saas:SetK8saasCluster',
    'service_compute_k8saas_rotate-ca = vinfraclient.cmd.compute.k8saas:RotateK8saasClusterCA',
    'service_compute_k8saas_upgrade = vinfraclient.cmd.compute.k8saas:UpgradeK8saasCluster',
    'service_compute_k8saas_health = vinfraclient.cmd.compute.k8saas:ShowK8saasClusterHealth',
    'service_compute_k8saas_defaults_show = vinfraclient.cmd.compute.k8saas:K8saasDefaultsShow',
    'service_compute_k8saas_defaults_set = vinfraclient.cmd.compute.k8saas:K8saasDefaultsSet',
    # compute k8saas workergroup
    'service_compute_k8saas_workergroup_create = vinfraclient.cmd.compute.k8saas:CreateK8saasWorkerGroup',
    'service_compute_k8saas_workergroup_delete = vinfraclient.cmd.compute.k8saas:DeleteK8saasWorkerGroup',
    'service_compute_k8saas_workergroup_list = vinfraclient.cmd.compute.k8saas:ListK8saasWorkerGroup',
    'service_compute_k8saas_workergroup_show = vinfraclient.cmd.compute.k8saas:ShowK8saasWorkerGroup',
    'service_compute_k8saas_workergroup_set = vinfraclient.cmd.compute.k8saas:SetK8saasWorkerGroup',
    'service_compute_k8saas_workergroup_upgrade = vinfraclient.cmd.compute.k8saas:UpgradeK8saasWorkerGroup',
    # compute load-balancer
    'service_compute_load-balancer_create = vinfraclient.cmd.compute.load_balancer:CreateLoadBalancer',
    'service_compute_load-balancer_list = vinfraclient.cmd.compute.load_balancer:ListLoadBalancers',
    'service_compute_load-balancer_show = vinfraclient.cmd.compute.load_balancer:ShowLoadBalancer',
    'service_compute_load-balancer_set = vinfraclient.cmd.compute.load_balancer:SetLoadBalancer',
    'service_compute_load-balancer_delete = vinfraclient.cmd.compute.load_balancer:DeleteLoadBalancer',
    'service_compute_load-balancer_stats = vinfraclient.cmd.compute.load_balancer:StatsLoadBalancer',
    'service_compute_load-balancer_recreate = vinfraclient.cmd.compute.load_balancer:RecreateLoadBalancer',
    'service_compute_load-balancer_failover = vinfraclient.cmd.compute.load_balancer:FailoverLoadBalancer',
    # compute load-balancer pool
    'service_compute_load-balancer_pool_create = vinfraclient.cmd.compute.load_balancer:CreatePool',
    'service_compute_load-balancer_pool_list = vinfraclient.cmd.compute.load_balancer:ListPools',
    'service_compute_load-balancer_pool_show = vinfraclient.cmd.compute.load_balancer:ShowPool',
    'service_compute_load-balancer_pool_set = vinfraclient.cmd.compute.load_balancer:SetPool',
    'service_compute_load-balancer_pool_delete = vinfraclient.cmd.compute.load_balancer:DeletePool',
    # compute placement
    'service_compute_placement_create = vinfraclient.cmd.compute.trait:CreateTrait',
    'service_compute_placement_delete = vinfraclient.cmd.compute.trait:DeleteTrait',
    'service_compute_placement_list = vinfraclient.cmd.compute.trait:ListTrait',
    'service_compute_placement_show = vinfraclient.cmd.compute.trait:ShowTrait',
    'service_compute_placement_update = vinfraclient.cmd.compute.trait:UpdateTrait',
    'service_compute_placement_assign = vinfraclient.cmd.compute.trait:AssignTrait',
    'service_compute_placement_delete-assign = vinfraclient.cmd.compute.trait:DeleteAssignTrait',
    # compute storage
    'service_compute_storage_add = vinfraclient.cmd.compute.cluster:AddComputeStorage',
    'service_compute_storage_remove = vinfraclient.cmd.compute.cluster:RemoveComputeStorage',
    'service_compute_storage_list = vinfraclient.cmd.compute.cluster:ListComputeStorage',
    'service_compute_storage_set = vinfraclient.cmd.compute.cluster:SetComputeStorage',
    'service_compute_storage_show = vinfraclient.cmd.compute.cluster:ShowComputeStorage',
    # compute storage-policies
    'service_compute_storage-policy_create = vinfraclient.cmd.compute.storage_policy:CreateStoragePolicy',
    'service_compute_storage-policy_delete = vinfraclient.cmd.compute.storage_policy:DeleteStoragePolicy',
    'service_compute_storage-policy_list = vinfraclient.cmd.compute.storage_policy:ListStoragePolicy',
    'service_compute_storage-policy_set = vinfraclient.cmd.compute.storage_policy:SetStoragePolicy',
    'service_compute_storage-policy_show = vinfraclient.cmd.compute.storage_policy:ShowStoragePolicy',
    # compute stacks
    'service_compute_stacks_create = vinfraclient.cmd.compute.stacks:CreateStack',
    'service_compute_stacks_delete = vinfraclient.cmd.compute.stacks:DeleteStack',
    'service_compute_stacks_list = vinfraclient.cmd.compute.stacks:ListStacks',
    'service_compute_stacks_show = vinfraclient.cmd.compute.stacks:ShowStack',
    'service_compute_stacks_resources_get = vinfraclient.cmd.compute.stacks:GetStackResources',
    'service_compute_stacks_template_params_get = vinfraclient.cmd.compute.stacks:GetTemplateParameters',
    # compute vpn
    'service_compute_vpn_endpoint-group_list = vinfraclient.cmd.compute.vpn:ListEndpointGroup',
    'service_compute_vpn_endpoint-group_show = vinfraclient.cmd.compute.vpn:ShowEndpointGroup',
    'service_compute_vpn_ike-policy_list = vinfraclient.cmd.compute.vpn:ListIkePolicy',
    'service_compute_vpn_ike-policy_show = vinfraclient.cmd.compute.vpn:ShowIkePolicy',
    'service_compute_vpn_ipsec-policy_list = vinfraclient.cmd.compute.vpn:ListIPsecPolicy',
    'service_compute_vpn_ipsec-policy_show = vinfraclient.cmd.compute.vpn:ShowIPsecPolicy',
    'service_compute_vpn_connection_show = vinfraclient.cmd.compute.vpn:ShowIPsecSiteConnection',
    'service_compute_vpn_connection_list = vinfraclient.cmd.compute.vpn:ListIPsecSiteConnection',
    'service_compute_vpn_connection_create = vinfraclient.cmd.compute.vpn:CreateIPsecSiteConnection',
    'service_compute_vpn_connection_set = vinfraclient.cmd.compute.vpn:SetIPsecSiteConnection',
    'service_compute_vpn_connection_delete = vinfraclient.cmd.compute.vpn:DeleteIPsecSiteConnection',
    'service_compute_vpn_connection_restart = vinfraclient.cmd.compute.vpn:RestartIPsecSiteConnection',
    # s3 service
    'service_s3_show = vinfraclient.cmd.s3:ShowS3',
    'service_s3_cluster_create = vinfraclient.cmd.s3:CreateCluster',
    'service_s3_cluster_change = vinfraclient.cmd.s3:ChangeCluster',
    'service_s3_cluster_delete = vinfraclient.cmd.s3:DeleteCluster',
    'service_s3_node_add = vinfraclient.cmd.s3:AddNode',
    'service_s3_node_release = vinfraclient.cmd.s3:ReleaseNode',
    'service_s3_replication_show = vinfraclient.cmd.s3:ShowS3GeoReplication',
    'service_s3_replication_show_token = vinfraclient.cmd.s3:ShowTokenS3GeoReplication',
    'service_s3_replication_list = vinfraclient.cmd.s3:ListS3GeoReplication',
    'service_s3_replication_add = vinfraclient.cmd.s3:AddS3GeoReplication',
    'service_s3_replication_delete = vinfraclient.cmd.s3:DeleteS3GeoReplication',
    # nfs service
    'service_nfs_kerberos_settings_show = vinfraclient.cmd.nfs:GetKrbAuthSettings',
    'service_nfs_kerberos_settings_set = vinfraclient.cmd.nfs:SetKrbAuthSettings',
    'service_nfs_cluster_create = vinfraclient.cmd.nfs:CreateCluster',
    'service_nfs_cluster_delete = vinfraclient.cmd.nfs:DeleteCluster',
    'service_nfs_node_list = vinfraclient.cmd.nfs:ListNodes',
    'service_nfs_node_add = vinfraclient.cmd.nfs:AddNode',
    'service_nfs_node_release = vinfraclient.cmd.nfs:ReleaseNode',
    # nfs share
    'service_nfs_share_create = vinfraclient.cmd.nfs.share:CreateShare',
    'service_nfs_share_delete = vinfraclient.cmd.nfs.share:DeleteShare',
    'service_nfs_share_list = vinfraclient.cmd.nfs.share:ListShare',
    'service_nfs_share_set = vinfraclient.cmd.nfs.share:SetShare',
    'service_nfs_share_show = vinfraclient.cmd.nfs.share:ShowShareInfo',
    'service_nfs_share_start = vinfraclient.cmd.nfs.share:StartShare',
    'service_nfs_share_stop = vinfraclient.cmd.nfs.share:StopShare',
    # nfs export
    'service_nfs_export_create = vinfraclient.cmd.nfs.export:CreateExport',
    'service_nfs_export_delete = vinfraclient.cmd.nfs.export:DeleteExport',
    'service_nfs_export_list = vinfraclient.cmd.nfs.export:ListExport',
    'service_nfs_export_set = vinfraclient.cmd.nfs.export:SetExport',
    'service_nfs_export_show = vinfraclient.cmd.nfs.export:ShowExportInfo',

    # memory policies
    'memory-policy_vstorage-services_per-cluster_show = vinfraclient.cmd.memory_policies.per_cluster:ShowParams',
    'memory-policy_vstorage-services_per-cluster_change = vinfraclient.cmd.memory_policies.per_cluster:ChangeParams',
    'memory-policy_vstorage-services_per-cluster_reset = vinfraclient.cmd.memory_policies.per_cluster:ResetParams',
    'memory-policy_vstorage-services_per-node_show = vinfraclient.cmd.memory_policies.per_node:ShowParams',
    'memory-policy_vstorage-services_per-node_change = vinfraclient.cmd.memory_policies.per_node:ChangeParams',
    'memory-policy_vstorage-services_per-node_reset = vinfraclient.cmd.memory_policies.per_node:ResetParams',

    # ABGW
    # abgw cluster commands
    'service_backup_cluster_deploy-standalone = vinfraclient.cmd.abgw:CreateBackupService',
    'service_backup_cluster_deploy-reverse-proxy = vinfraclient.cmd.abgw:DeployReverseProxyBackupGateway',
    'service_backup_cluster_deploy-upstream = vinfraclient.cmd.abgw:DeployUpstreamBackupGateway',
    'service_backup_cluster_turn-to-upstream = vinfraclient.cmd.abgw:TurnToUpstreamBackupGateway',
    'service_backup_cluster_add-upstream = vinfraclient.cmd.abgw:AddNewUpstream',
    'service_backup_cluster_process = vinfraclient.cmd.abgw:Process',
    'service_backup_cluster_download-upstream-info = vinfraclient.cmd.abgw:DownloadUpstreamInfo',
    'service_backup_cluster_create = vinfraclient.cmd.abgw:CreateBackupService',
    'service_backup_cluster_show = vinfraclient.cmd.abgw:ShowBackupService',
    'service_backup_cluster_renew-certificates = vinfraclient.cmd.deprecated:RenewBackupCertificates',
    'service_backup_cluster_release = vinfraclient.cmd.abgw:ReleaseBackupService',
    # abgw client limits commands
    'service_backup_limits-params_show = vinfraclient.cmd.abgw:ShowClientLimits',
    'service_backup_limits-params_change = vinfraclient.cmd.abgw:ChangeLimitsParams',
    # abgw storage params commands
    'service_backup_storage-params_show = vinfraclient.cmd.abgw:ShowStorageParams',
    'service_backup_storage-params_change = vinfraclient.cmd.abgw:ChangeStorageParams',
    # abgw volume params commands
    'service_backup_volume-params_show = vinfraclient.cmd.abgw:ShowVolumeParams',
    'service_backup_volume-params_change = vinfraclient.cmd.abgw:ChangeVolumeParams',
    # abgw sysinfo config commands
    'service_backup_monitoring_show = vinfraclient.cmd.abgw:ShowSysinfoConfig',
    'service_backup_monitoring_disable = vinfraclient.cmd.abgw:DisableSysinfoConfig',
    'service_backup_monitoring_enable = vinfraclient.cmd.abgw:EnableSysinfoConfig',
    'service_backup_monitoring_update = vinfraclient.cmd.abgw:UpdateSysinfoConfig',
    # abgw node commands
    'service_backup_node_add = vinfraclient.cmd.abgw:AddNodes',
    'service_backup_node_list = vinfraclient.cmd.abgw:ListNodes',
    'service_backup_node_release = vinfraclient.cmd.abgw:ReleaseNode',

    # abgw registration commands
    'service_backup_registration_list = vinfraclient.cmd.abgw.registrations:ListAbgwRegistration',
    'service_backup_registration_show = vinfraclient.cmd.abgw.registrations:ShowAbgwRegistration',
    'service_backup_registration_add = vinfraclient.cmd.abgw.registrations:CreateAbgwRegistration',
    'service_backup_registration_update = vinfraclient.cmd.abgw.registrations:UpdateAbgwRegistration',
    'service_backup_registration_renew-certificates = vinfraclient.cmd.abgw.registrations:RenewAbgwRegistration',
    'service_backup_registration_add-true-image = vinfraclient.cmd.abgw.registrations:CreateAbgwTrueImageRegistration',
    'service_backup_registration_renew-true-image-certs = vinfraclient.cmd.abgw.registrations:RenewTrueImageCertificates',
    'service_backup_registration_delete = vinfraclient.cmd.abgw.registrations:DeleteAbgwRegistration',

    # abgw geo-replication info commands
    'service_backup_geo-replication_show = vinfraclient.cmd.abgw.georeplication:ShowGeoReplicationInfo',
    # abgw geo-replication primary commands
    'service_backup_geo-replication_primary_setup = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimarySetup',
    'service_backup_geo-replication_primary_download-configs = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryDownloadConfigs',
    'service_backup_geo-replication_primary_establish = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryEstablish',
    'service_backup_geo-replication_primary_disable = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryDisable',
    'service_backup_geo-replication_primary_cancel = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryCancel',
    # abgw geo-replication secondary commands
    'service_backup_geo-replication_secondary_setup = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondarySetup',
    'service_backup_geo-replication_secondary_promote-to-primary = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondaryPromoteToPrimary',
    'service_backup_geo-replication_secondary_cancel = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondaryCancel',

    # abgw geo-replication primary compatibility commands
    'service_backup_geo-replication_master_setup = vinfraclient.cmd.abgw.georeplication:GeoReplicationMasterSetup',
    'service_backup_geo-replication_master_download-configs = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryDownloadConfigs',
    'service_backup_geo-replication_master_establish = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryEstablish',
    'service_backup_geo-replication_master_disable = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryDisable',
    'service_backup_geo-replication_master_cancel = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryCancel',
    # abgw geo-replication secondary compatibility commands
    'service_backup_geo-replication_slave_setup = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondarySetup',
    'service_backup_geo-replication_slave_promote-to-primary = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondaryPromoteToPrimary',
    'service_backup_geo-replication_slave_cancel = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondaryCancel',

    # software updates
    'software-updates_status = vinfraclient.cmd.software_updates:SoftwareUpdatesStatus',
    'software-updates_start = vinfraclient.cmd.software_updates:SoftwareUpdatesStart',
    'software-updates_resume = vinfraclient.cmd.software_updates:SoftwareUpdatesResume',
    'software-updates_download = vinfraclient.cmd.software_updates:SoftwareUpdatesDownload',
    'software-updates_check-for-updates = vinfraclient.cmd.software_updates:SoftwareUpdatesCheckForUpdates',
    'software-updates_eligibility-check = vinfraclient.cmd.software_updates:SoftwareUpdatesEligibilityCheck',
    'software-updates_pause = vinfraclient.cmd.software_updates:SoftwareUpdatesPause',
    'software-updates_cancel = vinfraclient.cmd.software_updates:SoftwareUpdatesCancel',

    # tasks
    'task_list = vinfraclient.cmd.task:ListTask',
    'task_show = vinfraclient.cmd.task:ShowTask',
    'task_wait = vinfraclient.cmd.task:WaitTask',

    # logging
    'logging_severity_show=vinfraclient.cmd.logging_service:GetLogLevel',
    'logging_severity_set=vinfraclient.cmd.logging_service:SetLogLevel',

    # domain props
    'domain_properties_show=vinfraclient.cmd.domain_props:GetDomainProps',
    'domain_properties_create=vinfraclient.cmd.domain_props:CreateDomainProps',
    'domain_properties_update=vinfraclient.cmd.domain_props:UpdateDomainProps',
    'domain_properties_delete=vinfraclient.cmd.domain_props:DeleteDomainProps',
    # domain access
    'domain_properties_access_list=vinfraclient.cmd.domain_props:ListDomainPropsAccess',
    'domain_properties_access_set=vinfraclient.cmd.domain_props:UpdateDomainPropsAccess',
    # domains keys
    'domain_properties_keys_list=vinfraclient.cmd.domain_props:ListDomainsKeys',

    # block-storage
    "service_block-storage_target-group_list = vinfraclient.cmd.block_storage:ListTargetGroups",
    "service_block-storage_target-group_show = vinfraclient.cmd.block_storage:ShowTargetGroup",
    "service_block-storage_target-group_create = vinfraclient.cmd.block_storage:CreateTargetGroup",
    "service_block-storage_target-group_delete = vinfraclient.cmd.block_storage:DeleteTargetGroup",
    "service_block-storage_target-group_start = vinfraclient.cmd.block_storage:StartTargetGroup",
    "service_block-storage_target-group_stop = vinfraclient.cmd.block_storage:StopTargetGroup",
    "service_block-storage_target-group_set = vinfraclient.cmd.block_storage:SetTargetGroup",
    "service_block-storage_target-group_target_list = vinfraclient.cmd.block_storage:ListTargets",
    "service_block-storage_target-group_target_show = vinfraclient.cmd.block_storage:ShowTarget",
    "service_block-storage_target-group_target_create = vinfraclient.cmd.block_storage:CreateTarget",
    "service_block-storage_target-group_target_delete = vinfraclient.cmd.block_storage:DeleteTarget",
    "service_block-storage_target-group_target_connection_list = vinfraclient.cmd.block_storage:ListTargetConnections",
    "service_block-storage_target-group_acl_list = vinfraclient.cmd.block_storage:ListACLs",
    "service_block-storage_target-group_acl_add = vinfraclient.cmd.block_storage:AddACL",
    "service_block-storage_target-group_acl_delete = vinfraclient.cmd.block_storage:DeleteACL",
    "service_block-storage_target-group_acl_set = vinfraclient.cmd.block_storage:SetACL",
    "service_block-storage_volume_list = vinfraclient.cmd.block_storage:ListVolumes",
    "service_block-storage_volume_show = vinfraclient.cmd.block_storage:ShowVolume",
    "service_block-storage_volume_set = vinfraclient.cmd.block_storage:SetVolume",
    "service_block-storage_volume_create = vinfraclient.cmd.block_storage:CreateVolume",
    "service_block-storage_volume_delete = vinfraclient.cmd.block_storage:DeleteVolume",
    "service_block-storage_target-group_volume_list = vinfraclient.cmd.block_storage:ListTargetGroupVolumes",
    "service_block-storage_target-group_volume_show = vinfraclient.cmd.block_storage:ShowTargetGroupVolume",
    "service_block-storage_target-group_volume_attach = vinfraclient.cmd.block_storage:AttachVolume",
    "service_block-storage_target-group_volume_detach = vinfraclient.cmd.block_storage:DetachVolume",
    "service_block-storage_user_list = vinfraclient.cmd.block_storage:ListUsers",
    "service_block-storage_user_show = vinfraclient.cmd.block_storage:ShowUser",
    "service_block-storage_user_create = vinfraclient.cmd.block_storage:CreateUser",
    "service_block-storage_user_delete = vinfraclient.cmd.block_storage:DeleteUser",
    "service_block-storage_user_set = vinfraclient.cmd.block_storage:UpdateUser",

    # CsConfig - For enable/disable RDMA
    "cses-config_show = vinfraclient.cmd.settings:ShowCsConfig",
    "cses-config_change = vinfraclient.cmd.settings:ChangeCsConfig",
]

vinfra_cli_cmds_hidden = [
    'service_compute_k8saas_workergroup_upgrade = vinfraclient.cmd.compute.k8saas:UpgradeK8saasWorkerGroup',
    'service_compute_k8saas_health = vinfraclient.cmd.compute.k8saas:ShowK8saasClusterHealth',
    'service_compute_stacks_create = vinfraclient.cmd.compute.stacks:CreateStack',
    'service_compute_stacks_delete = vinfraclient.cmd.compute.stacks:DeleteStack',
    'service_compute_stacks_list = vinfraclient.cmd.compute.stacks:ListStacks',
    'service_compute_stacks_show = vinfraclient.cmd.compute.stacks:ShowStack',
    'service_compute_stacks_resources_get = vinfraclient.cmd.compute.stacks:GetStackResources',
    'service_compute_stacks_template_params_get = vinfraclient.cmd.compute.stacks:GetTemplateParameters',
    # for tests only
    'domain_idp_login = vinfraclient.cmd.domain.idp:LoginDomainIdP',
    # abgw geo-replication primary compatibility commands
    'service_backup_geo-replication_master_setup = vinfraclient.cmd.abgw.georeplication:GeoReplicationMasterSetup',
    'service_backup_geo-replication_master_download-configs = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryDownloadConfigs',
    'service_backup_geo-replication_master_establish = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryEstablish',
    'service_backup_geo-replication_master_disable = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryDisable',
    'service_backup_geo-replication_master_cancel = vinfraclient.cmd.abgw.georeplication:GeoReplicationPrimaryCancel',
    # abgw geo-replication secondary compatibility commands
    'service_backup_geo-replication_slave_setup = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondarySetup',
    'service_backup_geo-replication_slave_promote-to-primary = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondaryPromoteToPrimary',
    'service_backup_geo-replication_slave_cancel = vinfraclient.cmd.abgw.georeplication:GeoReplicationSecondaryCancel',
    # abgw sysinfo config commands
    'service_backup_monitoring_show = vinfraclient.cmd.abgw:ShowSysinfoConfig',
    'service_backup_monitoring_disable = vinfraclient.cmd.abgw:DisableSysinfoConfig',
    'service_backup_monitoring_enable = vinfraclient.cmd.abgw:EnableSysinfoConfig',
    'service_backup_monitoring_update = vinfraclient.cmd.abgw:UpdateSysinfoConfig',
    # cluster license
    'cluster_license_spla-unregister = vinfraclient.cmd.license.acronis:UnregisterSPLALicense',
]

if vendor == VENDOR_VIRTUOZZO:
    vinfra_cli_cmds.extend([
        'cluster_license_load = vinfraclient.cmd.license.virtuozzo:LoadLicense',
        'cluster_license_show = vinfraclient.cmd.license.virtuozzo:ShowLicense',
        'cluster_license_update = vinfraclient.cmd.license.virtuozzo:UpdateLicense',
    ])
elif vendor == VENDOR_ACRONIS:
    vinfra_cli_cmds.extend([
        'cluster_license_load = vinfraclient.cmd.license.acronis:LoadLicense',
        'cluster_license_show = vinfraclient.cmd.license.acronis:ShowLicense',
        'cluster_license_test = vinfraclient.cmd.license.acronis:TestLicense',
        'cluster_license_spla-unregister = vinfraclient.cmd.license.acronis:UnregisterSPLALicense',
    ])
else:
    raise NotImplementedError
# pylint: enable=line-too-long


setuptools.setup(
    name='vinfraclient',
    version=get_version(),
    description=get_description(),
    packages=setuptools.find_packages(exclude=['tests*']),
    install_requires=install_requires('requirements.txt'),
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'vinfra = vinfraclient.main:main'
        ],
        'vinfra.formatter.list': [
            'json = vinfraclient.formatters.json_format:JSONFormatter',
            'table = vinfraclient.formatters.table:TableFormatter',
            'value = cliff.formatters.value:ValueFormatter',
            'yaml = cliff.formatters.yaml_format:YAMLFormatter',
        ],
        'vinfra.formatter.show': [
            'json = vinfraclient.formatters.json_format:JSONFormatter',
            'table = vinfraclient.formatters.table:TableFormatter',
            'value = cliff.formatters.value:ValueFormatter',
            'yaml = cliff.formatters.yaml_format:YAMLFormatter',
        ],
        'vinfra.cli': vinfra_cli_cmds,
        'vinfra.cli.hidden': vinfra_cli_cmds_hidden,
    }
)
