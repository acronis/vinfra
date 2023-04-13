# Administrator Command-Line Reference

This guide describes the syntax and parameters of the `vinfra` command-line tool that can be used to manage Hyper-Converged Infrastructure (HCI) from console and automate such management tasks.

The `vinfra` tool requires the following information:

- IP address or hostname of the management node (set to `backend-api.svc.vstoragedomain` by default)
- User name (`admin` by default)
- Password (created during installation of HCI)
- Domain name to authenticate with (`Default` by default)
- Project ID to authenticate with (`admin` by default)

This information can be supplied by using the following parameters with each command:

```
usage: vinfra <command> [--vinfra-portal <portal>] [--vinfra-username <username>] [--vinfra-password <password>] [--vinfra-domain <domain>] [--vinfra-project <project>]
```

Alternatively, you can supply custom credentials by setting the following environment variables (for example, in your `~/.bash_profile`): `VINFRA_PORTAL`, `VINFRA_USERNAME`, `VINFRA_PASSWORD`, `VINFRA_DOMAIN`, and `VINFRA_PROJECT`. In this case, you will be able to run the tool without specifying the command-line parameters.

If you run `vinfra` from the management node as the admin user, the only variable you need to set is the password. For example:

```
# export VINFRA_PASSWORD=12345
```

If you installed vinfra on a remote machine and/or run it as a different system administartor, you will need to additionally set `VINFRA_PORTAL` and/or `VINFRA_USERNAME` on that machine.

If you want to authenticate within a different project or/and domain, you will need to set two more environment variables: `VINFRA_PROJECT` and/or `VINFRA_DOMAIN`.

To get a list of all supported commands and their descriptions, you can run `vinfra help`. For help on a specific command, either run `vinfra help <command>` or `vinfra <command> --help`.

---

## vinfra usage

- [vinfra output formatters](#vinfra-output-formatters)
- [vinfra cluster alert delete](#vinfra-cluster-alert-delete)
- [vinfra cluster alert list](#vinfra-cluster-alert-list)
- [vinfra cluster alert show](#vinfra-cluster-alert-show)
- [vinfra cluster alert types list](#vinfra-cluster-alert-types-list)
- [vinfra cluster auditlog list](#vinfra-cluster-auditlog-list)
- [vinfra cluster auditlog show](#vinfra-cluster-auditlog-show)
- [vinfra cluster backup create](#vinfra-cluster-backup-create)
- [vinfra cluster backup show](#vinfra-cluster-backup-show)
- [vinfra cluster create](#vinfra-cluster-create)
- [vinfra cluster delete](#vinfra-cluster-delete)
- [vinfra cluster ha create](#vinfra-cluster-ha-create)
- [vinfra cluster ha delete](#vinfra-cluster-ha-delete)
- [vinfra cluster ha node add](#vinfra-cluster-ha-node-add)
- [vinfra cluster ha node remove](#vinfra-cluster-ha-node-remove)
- [vinfra cluster ha show](#vinfra-cluster-ha-show)
- [vinfra cluster ha update](#vinfra-cluster-ha-update)
- [vinfra cluster license load](#vinfra-cluster-license-load)
- [vinfra cluster license show](#vinfra-cluster-license-show)
- [vinfra cluster license update](#vinfra-cluster-license-update)
- [vinfra cluster network conversion precheck](#vinfra-cluster-network-conversion-precheck)
- [vinfra cluster network conversion start](#vinfra-cluster-network-conversion-start)
- [vinfra cluster network conversion status](#vinfra-cluster-network-conversion-status)
- [vinfra cluster network create](#vinfra-cluster-network-create)
- [vinfra cluster network delete](#vinfra-cluster-network-delete)
- [vinfra cluster network encryption bypass add](#vinfra-cluster-network-encryption-bypass-add)
- [vinfra cluster network encryption bypass delete](#vinfra-cluster-network-encryption-bypass-delete)
- [vinfra cluster network encryption bypass list](#vinfra-cluster-network-encryption-bypass-list)
- [vinfra cluster network encryption cancel](#vinfra-cluster-network-encryption-cancel)
- [vinfra cluster network encryption disable](#vinfra-cluster-network-encryption-disable)
- [vinfra cluster network encryption enable](#vinfra-cluster-network-encryption-enable)
- [vinfra cluster network encryption status](#vinfra-cluster-network-encryption-status)
- [vinfra cluster network ipv6-prefix assign](#vinfra-cluster-network-ipv6-prefix-assign)
- [vinfra cluster network ipv6-prefix remove](#vinfra-cluster-network-ipv6-prefix-remove)
- [vinfra cluster network ipv6-prefix show](#vinfra-cluster-network-ipv6-prefix-show)
- [vinfra cluster network list](#vinfra-cluster-network-list)
- [vinfra cluster network migration apply](#vinfra-cluster-network-migration-apply)
- [vinfra cluster network migration resume](#vinfra-cluster-network-migration-resume)
- [vinfra cluster network migration retry](#vinfra-cluster-network-migration-retry)
- [vinfra cluster network migration revert](#vinfra-cluster-network-migration-revert)
- [vinfra cluster network migration show](#vinfra-cluster-network-migration-show)
- [vinfra cluster network migration start](#vinfra-cluster-network-migration-start)
- [vinfra cluster network reconfiguration show](#vinfra-cluster-network-reconfiguration-show)
- [vinfra cluster network set](#vinfra-cluster-network-set)
- [vinfra cluster network set-bulk](#vinfra-cluster-network-set-bulk)
- [vinfra cluster network show](#vinfra-cluster-network-show)
- [vinfra cluster node join-config get](#vinfra-cluster-node-join-config-get)
- [vinfra cluster node join-config set](#vinfra-cluster-node-join-config-set)
- [vinfra cluster overview](#vinfra-cluster-overview)
- [vinfra cluster password reset](#vinfra-cluster-password-reset)
- [vinfra cluster password show](#vinfra-cluster-password-show)
- [vinfra cluster problem-report](#vinfra-cluster-problem-report)
- [vinfra cluster settings automatic-disk-replacement set](#vinfra-cluster-settings-automatic-disk-replacement-set)
- [vinfra cluster settings automatic-disk-replacement show](#vinfra-cluster-settings-automatic-disk-replacement-show)
- [vinfra cluster settings dns set](#vinfra-cluster-settings-dns-set)
- [vinfra cluster settings dns show](#vinfra-cluster-settings-dns-show)
- [vinfra cluster settings encryption set](#vinfra-cluster-settings-encryption-set)
- [vinfra cluster settings encryption show](#vinfra-cluster-settings-encryption-show)
- [vinfra cluster settings locale list](#vinfra-cluster-settings-locale-list)
- [vinfra cluster settings locale set](#vinfra-cluster-settings-locale-set)
- [vinfra cluster settings locale show](#vinfra-cluster-settings-locale-show)
- [vinfra cluster settings number-of-cses-per-disk set](#vinfra-cluster-settings-number-of-cses-per-disk-set)
- [vinfra cluster settings number-of-cses-per-disk show](#vinfra-cluster-settings-number-of-cses-per-disk-show)
- [vinfra cluster settings ssl set](#vinfra-cluster-settings-ssl-set)
- [vinfra cluster settings ssl show](#vinfra-cluster-settings-ssl-show)
- [vinfra cluster show](#vinfra-cluster-show)
- [vinfra cluster sshkey add](#vinfra-cluster-sshkey-add)
- [vinfra cluster sshkey delete](#vinfra-cluster-sshkey-delete)
- [vinfra cluster sshkey list](#vinfra-cluster-sshkey-list)
- [vinfra cluster storage-policy create](#vinfra-cluster-storage-policy-create)
- [vinfra cluster storage-policy delete](#vinfra-cluster-storage-policy-delete)
- [vinfra cluster storage-policy list](#vinfra-cluster-storage-policy-list)
- [vinfra cluster storage-policy set](#vinfra-cluster-storage-policy-set)
- [vinfra cluster storage-policy show](#vinfra-cluster-storage-policy-show)
- [vinfra cluster switch-to-ipv6](#vinfra-cluster-switch-to-ipv6)
- [vinfra cluster traffic-type assignment apply](#vinfra-cluster-traffic-type-assignment-apply)
- [vinfra cluster traffic-type assignment retry](#vinfra-cluster-traffic-type-assignment-retry)
- [vinfra cluster traffic-type assignment revert](#vinfra-cluster-traffic-type-assignment-revert)
- [vinfra cluster traffic-type assignment show](#vinfra-cluster-traffic-type-assignment-show)
- [vinfra cluster traffic-type assignment start](#vinfra-cluster-traffic-type-assignment-start)
- [vinfra cluster traffic-type create](#vinfra-cluster-traffic-type-create)
- [vinfra cluster traffic-type delete](#vinfra-cluster-traffic-type-delete)
- [vinfra cluster traffic-type list](#vinfra-cluster-traffic-type-list)
- [vinfra cluster traffic-type set](#vinfra-cluster-traffic-type-set)
- [vinfra cluster traffic-type show](#vinfra-cluster-traffic-type-show)
- [vinfra cluster user change-password](#vinfra-cluster-user-change-password)
- [vinfra cluster user create](#vinfra-cluster-user-create)
- [vinfra cluster user delete](#vinfra-cluster-user-delete)
- [vinfra cluster user list](#vinfra-cluster-user-list)
- [vinfra cluster user list-available-roles](#vinfra-cluster-user-list-available-roles)
- [vinfra cluster user set](#vinfra-cluster-user-set)
- [vinfra cluster user show](#vinfra-cluster-user-show)
- [vinfra cses-config change](#vinfra-cses-config-change)
- [vinfra cses-config show](#vinfra-cses-config-show)
- [vinfra domain create](#vinfra-domain-create)
- [vinfra domain delete](#vinfra-domain-delete)
- [vinfra domain group create](#vinfra-domain-group-create)
- [vinfra domain group delete](#vinfra-domain-group-delete)
- [vinfra domain group list](#vinfra-domain-group-list)
- [vinfra domain group set](#vinfra-domain-group-set)
- [vinfra domain group show](#vinfra-domain-group-show)
- [vinfra domain group user add](#vinfra-domain-group-user-add)
- [vinfra domain group user list](#vinfra-domain-group-user-list)
- [vinfra domain group user remove](#vinfra-domain-group-user-remove)
- [vinfra domain idp create](#vinfra-domain-idp-create)
- [vinfra domain idp delete](#vinfra-domain-idp-delete)
- [vinfra domain idp list](#vinfra-domain-idp-list)
- [vinfra domain idp set](#vinfra-domain-idp-set)
- [vinfra domain idp show](#vinfra-domain-idp-show)
- [vinfra domain list](#vinfra-domain-list)
- [vinfra domain project create](#vinfra-domain-project-create)
- [vinfra domain project delete](#vinfra-domain-project-delete)
- [vinfra domain project list](#vinfra-domain-project-list)
- [vinfra domain project set](#vinfra-domain-project-set)
- [vinfra domain project show](#vinfra-domain-project-show)
- [vinfra domain project user list](#vinfra-domain-project-user-list)
- [vinfra domain project user remove](#vinfra-domain-project-user-remove)
- [vinfra domain properties access list](#vinfra-domain-properties-access-list)
- [vinfra domain properties access set](#vinfra-domain-properties-access-set)
- [vinfra domain properties create](#vinfra-domain-properties-create)
- [vinfra domain properties delete](#vinfra-domain-properties-delete)
- [vinfra domain properties keys list](#vinfra-domain-properties-keys-list)
- [vinfra domain properties show](#vinfra-domain-properties-show)
- [vinfra domain properties update](#vinfra-domain-properties-update)
- [vinfra domain set](#vinfra-domain-set)
- [vinfra domain show](#vinfra-domain-show)
- [vinfra domain user create](#vinfra-domain-user-create)
- [vinfra domain user delete](#vinfra-domain-user-delete)
- [vinfra domain user group list](#vinfra-domain-user-group-list)
- [vinfra domain user list](#vinfra-domain-user-list)
- [vinfra domain user list-available-roles](#vinfra-domain-user-list-available-roles)
- [vinfra domain user set](#vinfra-domain-user-set)
- [vinfra domain user show](#vinfra-domain-user-show)
- [vinfra domain user unlock](#vinfra-domain-user-unlock)
- [vinfra failure domain list](#vinfra-failure-domain-list)
- [vinfra failure domain rename](#vinfra-failure-domain-rename)
- [vinfra location create](#vinfra-location-create)
- [vinfra location delete](#vinfra-location-delete)
- [vinfra location list](#vinfra-location-list)
- [vinfra location move](#vinfra-location-move)
- [vinfra location rename](#vinfra-location-rename)
- [vinfra location show](#vinfra-location-show)
- [vinfra logging severity set](#vinfra-logging-severity-set)
- [vinfra logging severity show](#vinfra-logging-severity-show)
- [vinfra memory-policy vstorage-services per-cluster change](#vinfra-memory-policy-vstorage-services-per-cluster-change)
- [vinfra memory-policy vstorage-services per-cluster reset](#vinfra-memory-policy-vstorage-services-per-cluster-reset)
- [vinfra memory-policy vstorage-services per-cluster show](#vinfra-memory-policy-vstorage-services-per-cluster-show)
- [vinfra memory-policy vstorage-services per-node change](#vinfra-memory-policy-vstorage-services-per-node-change)
- [vinfra memory-policy vstorage-services per-node reset](#vinfra-memory-policy-vstorage-services-per-node-reset)
- [vinfra memory-policy vstorage-services per-node show](#vinfra-memory-policy-vstorage-services-per-node-show)
- [vinfra node certificate ipsec renew](#vinfra-node-certificate-ipsec-renew)
- [vinfra node disk assign](#vinfra-node-disk-assign)
- [vinfra node disk blink off](#vinfra-node-disk-blink-off)
- [vinfra node disk blink on](#vinfra-node-disk-blink-on)
- [vinfra node disk list](#vinfra-node-disk-list)
- [vinfra node disk release](#vinfra-node-disk-release)
- [vinfra node disk show](#vinfra-node-disk-show)
- [vinfra node disk show diagnostic-info](#vinfra-node-disk-show-diagnostic-info)
- [vinfra node forget](#vinfra-node-forget)
- [vinfra node iface create-bond](#vinfra-node-iface-create-bond)
- [vinfra node iface create-vlan](#vinfra-node-iface-create-vlan)
- [vinfra node iface delete](#vinfra-node-iface-delete)
- [vinfra node iface down](#vinfra-node-iface-down)
- [vinfra node iface list](#vinfra-node-iface-list)
- [vinfra node iface set](#vinfra-node-iface-set)
- [vinfra node iface show](#vinfra-node-iface-show)
- [vinfra node iface up](#vinfra-node-iface-up)
- [vinfra node iscsi target add](#vinfra-node-iscsi-target-add)
- [vinfra node iscsi target delete](#vinfra-node-iscsi-target-delete)
- [vinfra node join](#vinfra-node-join)
- [vinfra node list](#vinfra-node-list)
- [vinfra node maintenance precheck](#vinfra-node-maintenance-precheck)
- [vinfra node maintenance start](#vinfra-node-maintenance-start)
- [vinfra node maintenance status](#vinfra-node-maintenance-status)
- [vinfra node maintenance stop](#vinfra-node-maintenance-stop)
- [vinfra node ram-reservation list](#vinfra-node-ram-reservation-list)
- [vinfra node ram-reservation show](#vinfra-node-ram-reservation-show)
- [vinfra node ram-reservation total](#vinfra-node-ram-reservation-total)
- [vinfra node release](#vinfra-node-release)
- [vinfra node show](#vinfra-node-show)
- [vinfra node token create](#vinfra-node-token-create)
- [vinfra node token show](#vinfra-node-token-show)
- [vinfra node token validate](#vinfra-node-token-validate)
- [vinfra service backup cluster add-upstream](#vinfra-service-backup-cluster-add-upstream)
- [vinfra service backup cluster create](#vinfra-service-backup-cluster-create)
- [vinfra service backup cluster deploy-reverse-proxy](#vinfra-service-backup-cluster-deploy-reverse-proxy)
- [vinfra service backup cluster deploy-standalone](#vinfra-service-backup-cluster-deploy-standalone)
- [vinfra service backup cluster deploy-upstream](#vinfra-service-backup-cluster-deploy-upstream)
- [vinfra service backup cluster download-upstream-info](#vinfra-service-backup-cluster-download-upstream-info)
- [vinfra service backup cluster process](#vinfra-service-backup-cluster-process)
- [vinfra service backup cluster release](#vinfra-service-backup-cluster-release)
- [vinfra service backup cluster show](#vinfra-service-backup-cluster-show)
- [vinfra service backup cluster turn-to-upstream](#vinfra-service-backup-cluster-turn-to-upstream)
- [vinfra service backup geo-replication primary cancel](#vinfra-service-backup-geo-replication-primary-cancel)
- [vinfra service backup geo-replication primary disable](#vinfra-service-backup-geo-replication-primary-disable)
- [vinfra service backup geo-replication primary download-configs](#vinfra-service-backup-geo-replication-primary-download-configs)
- [vinfra service backup geo-replication primary establish](#vinfra-service-backup-geo-replication-primary-establish)
- [vinfra service backup geo-replication primary setup](#vinfra-service-backup-geo-replication-primary-setup)
- [vinfra service backup geo-replication secondary cancel](#vinfra-service-backup-geo-replication-secondary-cancel)
- [vinfra service backup geo-replication secondary promote-to-primary](#vinfra-service-backup-geo-replication-secondary-promote-to-primary)
- [vinfra service backup geo-replication secondary setup](#vinfra-service-backup-geo-replication-secondary-setup)
- [vinfra service backup geo-replication show](#vinfra-service-backup-geo-replication-show)
- [vinfra service backup node add](#vinfra-service-backup-node-add)
- [vinfra service backup node list](#vinfra-service-backup-node-list)
- [vinfra service backup node release](#vinfra-service-backup-node-release)
- [vinfra service backup registration add](#vinfra-service-backup-registration-add)
- [vinfra service backup registration add-true-image](#vinfra-service-backup-registration-add-true-image)
- [vinfra service backup registration delete](#vinfra-service-backup-registration-delete)
- [vinfra service backup registration list](#vinfra-service-backup-registration-list)
- [vinfra service backup registration renew-certificates](#vinfra-service-backup-registration-renew-certificates)
- [vinfra service backup registration renew-true-image-certs](#vinfra-service-backup-registration-renew-true-image-certs)
- [vinfra service backup registration show](#vinfra-service-backup-registration-show)
- [vinfra service backup registration update](#vinfra-service-backup-registration-update)
- [vinfra service backup storage-params change](#vinfra-service-backup-storage-params-change)
- [vinfra service backup storage-params show](#vinfra-service-backup-storage-params-show)
- [vinfra service backup volume-params change](#vinfra-service-backup-volume-params-change)
- [vinfra service backup volume-params show](#vinfra-service-backup-volume-params-show)
- [vinfra service block-storage target-group acl add](#vinfra-service-block-storage-target-group-acl-add)
- [vinfra service block-storage target-group acl delete](#vinfra-service-block-storage-target-group-acl-delete)
- [vinfra service block-storage target-group acl list](#vinfra-service-block-storage-target-group-acl-list)
- [vinfra service block-storage target-group acl set](#vinfra-service-block-storage-target-group-acl-set)
- [vinfra service block-storage target-group create](#vinfra-service-block-storage-target-group-create)
- [vinfra service block-storage target-group delete](#vinfra-service-block-storage-target-group-delete)
- [vinfra service block-storage target-group list](#vinfra-service-block-storage-target-group-list)
- [vinfra service block-storage target-group set](#vinfra-service-block-storage-target-group-set)
- [vinfra service block-storage target-group show](#vinfra-service-block-storage-target-group-show)
- [vinfra service block-storage target-group start](#vinfra-service-block-storage-target-group-start)
- [vinfra service block-storage target-group stop](#vinfra-service-block-storage-target-group-stop)
- [vinfra service block-storage target-group target connection list](#vinfra-service-block-storage-target-group-target-connection-list)
- [vinfra service block-storage target-group target create](#vinfra-service-block-storage-target-group-target-create)
- [vinfra service block-storage target-group target delete](#vinfra-service-block-storage-target-group-target-delete)
- [vinfra service block-storage target-group target list](#vinfra-service-block-storage-target-group-target-list)
- [vinfra service block-storage target-group target show](#vinfra-service-block-storage-target-group-target-show)
- [vinfra service block-storage target-group volume attach](#vinfra-service-block-storage-target-group-volume-attach)
- [vinfra service block-storage target-group volume detach](#vinfra-service-block-storage-target-group-volume-detach)
- [vinfra service block-storage target-group volume list](#vinfra-service-block-storage-target-group-volume-list)
- [vinfra service block-storage target-group volume show](#vinfra-service-block-storage-target-group-volume-show)
- [vinfra service block-storage user create](#vinfra-service-block-storage-user-create)
- [vinfra service block-storage user delete](#vinfra-service-block-storage-user-delete)
- [vinfra service block-storage user list](#vinfra-service-block-storage-user-list)
- [vinfra service block-storage user set](#vinfra-service-block-storage-user-set)
- [vinfra service block-storage user show](#vinfra-service-block-storage-user-show)
- [vinfra service block-storage volume create](#vinfra-service-block-storage-volume-create)
- [vinfra service block-storage volume delete](#vinfra-service-block-storage-volume-delete)
- [vinfra service block-storage volume list](#vinfra-service-block-storage-volume-list)
- [vinfra service block-storage volume set](#vinfra-service-block-storage-volume-set)
- [vinfra service block-storage volume show](#vinfra-service-block-storage-volume-show)
- [vinfra service compute baseline-cpu](#vinfra-service-compute-baseline-cpu)
- [vinfra service compute create](#vinfra-service-compute-create)
- [vinfra service compute delete](#vinfra-service-compute-delete)
- [vinfra service compute flavor create](#vinfra-service-compute-flavor-create)
- [vinfra service compute flavor delete](#vinfra-service-compute-flavor-delete)
- [vinfra service compute flavor list](#vinfra-service-compute-flavor-list)
- [vinfra service compute flavor show](#vinfra-service-compute-flavor-show)
- [vinfra service compute floatingip create](#vinfra-service-compute-floatingip-create)
- [vinfra service compute floatingip delete](#vinfra-service-compute-floatingip-delete)
- [vinfra service compute floatingip list](#vinfra-service-compute-floatingip-list)
- [vinfra service compute floatingip set](#vinfra-service-compute-floatingip-set)
- [vinfra service compute floatingip show](#vinfra-service-compute-floatingip-show)
- [vinfra service compute image create](#vinfra-service-compute-image-create)
- [vinfra service compute image delete](#vinfra-service-compute-image-delete)
- [vinfra service compute image list](#vinfra-service-compute-image-list)
- [vinfra service compute image save](#vinfra-service-compute-image-save)
- [vinfra service compute image set](#vinfra-service-compute-image-set)
- [vinfra service compute image show](#vinfra-service-compute-image-show)
- [vinfra service compute k8saas config](#vinfra-service-compute-k8saas-config)
- [vinfra service compute k8saas create](#vinfra-service-compute-k8saas-create)
- [vinfra service compute k8saas defaults set](#vinfra-service-compute-k8saas-defaults-set)
- [vinfra service compute k8saas defaults show](#vinfra-service-compute-k8saas-defaults-show)
- [vinfra service compute k8saas delete](#vinfra-service-compute-k8saas-delete)
- [vinfra service compute k8saas list](#vinfra-service-compute-k8saas-list)
- [vinfra service compute k8saas rotate-ca](#vinfra-service-compute-k8saas-rotate-ca)
- [vinfra service compute k8saas set](#vinfra-service-compute-k8saas-set)
- [vinfra service compute k8saas show](#vinfra-service-compute-k8saas-show)
- [vinfra service compute k8saas upgrade](#vinfra-service-compute-k8saas-upgrade)
- [vinfra service compute k8saas workergroup create](#vinfra-service-compute-k8saas-workergroup-create)
- [vinfra service compute k8saas workergroup delete](#vinfra-service-compute-k8saas-workergroup-delete)
- [vinfra service compute k8saas workergroup list](#vinfra-service-compute-k8saas-workergroup-list)
- [vinfra service compute k8saas workergroup set](#vinfra-service-compute-k8saas-workergroup-set)
- [vinfra service compute k8saas workergroup show](#vinfra-service-compute-k8saas-workergroup-show)
- [vinfra service compute key create](#vinfra-service-compute-key-create)
- [vinfra service compute key delete](#vinfra-service-compute-key-delete)
- [vinfra service compute key list](#vinfra-service-compute-key-list)
- [vinfra service compute key show](#vinfra-service-compute-key-show)
- [vinfra service compute load-balancer create](#vinfra-service-compute-load-balancer-create)
- [vinfra service compute load-balancer delete](#vinfra-service-compute-load-balancer-delete)
- [vinfra service compute load-balancer failover](#vinfra-service-compute-load-balancer-failover)
- [vinfra service compute load-balancer list](#vinfra-service-compute-load-balancer-list)
- [vinfra service compute load-balancer pool create](#vinfra-service-compute-load-balancer-pool-create)
- [vinfra service compute load-balancer pool delete](#vinfra-service-compute-load-balancer-pool-delete)
- [vinfra service compute load-balancer pool list](#vinfra-service-compute-load-balancer-pool-list)
- [vinfra service compute load-balancer pool set](#vinfra-service-compute-load-balancer-pool-set)
- [vinfra service compute load-balancer pool show](#vinfra-service-compute-load-balancer-pool-show)
- [vinfra service compute load-balancer recreate](#vinfra-service-compute-load-balancer-recreate)
- [vinfra service compute load-balancer set](#vinfra-service-compute-load-balancer-set)
- [vinfra service compute load-balancer show](#vinfra-service-compute-load-balancer-show)
- [vinfra service compute load-balancer stats](#vinfra-service-compute-load-balancer-stats)
- [vinfra service compute network create](#vinfra-service-compute-network-create)
- [vinfra service compute network delete](#vinfra-service-compute-network-delete)
- [vinfra service compute network list](#vinfra-service-compute-network-list)
- [vinfra service compute network set](#vinfra-service-compute-network-set)
- [vinfra service compute network show](#vinfra-service-compute-network-show)
- [vinfra service compute node add](#vinfra-service-compute-node-add)
- [vinfra service compute node fence](#vinfra-service-compute-node-fence)
- [vinfra service compute node list](#vinfra-service-compute-node-list)
- [vinfra service compute node release](#vinfra-service-compute-node-release)
- [vinfra service compute node show](#vinfra-service-compute-node-show)
- [vinfra service compute node unfence](#vinfra-service-compute-node-unfence)
- [vinfra service compute placement assign](#vinfra-service-compute-placement-assign)
- [vinfra service compute placement create](#vinfra-service-compute-placement-create)
- [vinfra service compute placement delete](#vinfra-service-compute-placement-delete)
- [vinfra service compute placement delete-assign](#vinfra-service-compute-placement-delete-assign)
- [vinfra service compute placement list](#vinfra-service-compute-placement-list)
- [vinfra service compute placement show](#vinfra-service-compute-placement-show)
- [vinfra service compute placement update](#vinfra-service-compute-placement-update)
- [vinfra service compute quotas show](#vinfra-service-compute-quotas-show)
- [vinfra service compute quotas update](#vinfra-service-compute-quotas-update)
- [vinfra service compute router create](#vinfra-service-compute-router-create)
- [vinfra service compute router delete](#vinfra-service-compute-router-delete)
- [vinfra service compute router iface add](#vinfra-service-compute-router-iface-add)
- [vinfra service compute router iface list](#vinfra-service-compute-router-iface-list)
- [vinfra service compute router iface remove](#vinfra-service-compute-router-iface-remove)
- [vinfra service compute router list](#vinfra-service-compute-router-list)
- [vinfra service compute router set](#vinfra-service-compute-router-set)
- [vinfra service compute router show](#vinfra-service-compute-router-show)
- [vinfra service compute security-group create](#vinfra-service-compute-security-group-create)
- [vinfra service compute security-group delete](#vinfra-service-compute-security-group-delete)
- [vinfra service compute security-group list](#vinfra-service-compute-security-group-list)
- [vinfra service compute security-group rule create](#vinfra-service-compute-security-group-rule-create)
- [vinfra service compute security-group rule delete](#vinfra-service-compute-security-group-rule-delete)
- [vinfra service compute security-group rule list](#vinfra-service-compute-security-group-rule-list)
- [vinfra service compute security-group rule show](#vinfra-service-compute-security-group-rule-show)
- [vinfra service compute security-group set](#vinfra-service-compute-security-group-set)
- [vinfra service compute security-group show](#vinfra-service-compute-security-group-show)
- [vinfra service compute server cancel-stop](#vinfra-service-compute-server-cancel-stop)
- [vinfra service compute server console](#vinfra-service-compute-server-console)
- [vinfra service compute server create](#vinfra-service-compute-server-create)
- [vinfra service compute server delete](#vinfra-service-compute-server-delete)
- [vinfra service compute server evacuate](#vinfra-service-compute-server-evacuate)
- [vinfra service compute server event list](#vinfra-service-compute-server-event-list)
- [vinfra service compute server event show](#vinfra-service-compute-server-event-show)
- [vinfra service compute server iface attach](#vinfra-service-compute-server-iface-attach)
- [vinfra service compute server iface detach](#vinfra-service-compute-server-iface-detach)
- [vinfra service compute server iface list](#vinfra-service-compute-server-iface-list)
- [vinfra service compute server iface set](#vinfra-service-compute-server-iface-set)
- [vinfra service compute server list](#vinfra-service-compute-server-list)
- [vinfra service compute server log](#vinfra-service-compute-server-log)
- [vinfra service compute server meta set](#vinfra-service-compute-server-meta-set)
- [vinfra service compute server meta unset](#vinfra-service-compute-server-meta-unset)
- [vinfra service compute server migrate](#vinfra-service-compute-server-migrate)
- [vinfra service compute server pause](#vinfra-service-compute-server-pause)
- [vinfra service compute server reboot](#vinfra-service-compute-server-reboot)
- [vinfra service compute server rescue](#vinfra-service-compute-server-rescue)
- [vinfra service compute server reset-state](#vinfra-service-compute-server-reset-state)
- [vinfra service compute server resize](#vinfra-service-compute-server-resize)
- [vinfra service compute server resume](#vinfra-service-compute-server-resume)
- [vinfra service compute server set](#vinfra-service-compute-server-set)
- [vinfra service compute server shelve](#vinfra-service-compute-server-shelve)
- [vinfra service compute server show](#vinfra-service-compute-server-show)
- [vinfra service compute server start](#vinfra-service-compute-server-start)
- [vinfra service compute server stat](#vinfra-service-compute-server-stat)
- [vinfra service compute server stop](#vinfra-service-compute-server-stop)
- [vinfra service compute server suspend](#vinfra-service-compute-server-suspend)
- [vinfra service compute server tag add](#vinfra-service-compute-server-tag-add)
- [vinfra service compute server tag delete](#vinfra-service-compute-server-tag-delete)
- [vinfra service compute server tag list](#vinfra-service-compute-server-tag-list)
- [vinfra service compute server unpause](#vinfra-service-compute-server-unpause)
- [vinfra service compute server unrescue](#vinfra-service-compute-server-unrescue)
- [vinfra service compute server unshelve](#vinfra-service-compute-server-unshelve)
- [vinfra service compute server volume attach](#vinfra-service-compute-server-volume-attach)
- [vinfra service compute server volume detach](#vinfra-service-compute-server-volume-detach)
- [vinfra service compute server volume list](#vinfra-service-compute-server-volume-list)
- [vinfra service compute server volume show](#vinfra-service-compute-server-volume-show)
- [vinfra service compute set](#vinfra-service-compute-set)
- [vinfra service compute show](#vinfra-service-compute-show)
- [vinfra service compute stat](#vinfra-service-compute-stat)
- [vinfra service compute storage add](#vinfra-service-compute-storage-add)
- [vinfra service compute storage list](#vinfra-service-compute-storage-list)
- [vinfra service compute storage remove](#vinfra-service-compute-storage-remove)
- [vinfra service compute storage set](#vinfra-service-compute-storage-set)
- [vinfra service compute storage show](#vinfra-service-compute-storage-show)
- [vinfra service compute storage-policy create](#vinfra-service-compute-storage-policy-create)
- [vinfra service compute storage-policy delete](#vinfra-service-compute-storage-policy-delete)
- [vinfra service compute storage-policy list](#vinfra-service-compute-storage-policy-list)
- [vinfra service compute storage-policy set](#vinfra-service-compute-storage-policy-set)
- [vinfra service compute storage-policy show](#vinfra-service-compute-storage-policy-show)
- [vinfra service compute subnet create](#vinfra-service-compute-subnet-create)
- [vinfra service compute subnet delete](#vinfra-service-compute-subnet-delete)
- [vinfra service compute subnet list](#vinfra-service-compute-subnet-list)
- [vinfra service compute subnet set](#vinfra-service-compute-subnet-set)
- [vinfra service compute subnet show](#vinfra-service-compute-subnet-show)
- [vinfra service compute task abort](#vinfra-service-compute-task-abort)
- [vinfra service compute task retry](#vinfra-service-compute-task-retry)
- [vinfra service compute task show](#vinfra-service-compute-task-show)
- [vinfra service compute volume clone](#vinfra-service-compute-volume-clone)
- [vinfra service compute volume create](#vinfra-service-compute-volume-create)
- [vinfra service compute volume delete](#vinfra-service-compute-volume-delete)
- [vinfra service compute volume extend](#vinfra-service-compute-volume-extend)
- [vinfra service compute volume list](#vinfra-service-compute-volume-list)
- [vinfra service compute volume reset-state](#vinfra-service-compute-volume-reset-state)
- [vinfra service compute volume set](#vinfra-service-compute-volume-set)
- [vinfra service compute volume show](#vinfra-service-compute-volume-show)
- [vinfra service compute volume snapshot create](#vinfra-service-compute-volume-snapshot-create)
- [vinfra service compute volume snapshot delete](#vinfra-service-compute-volume-snapshot-delete)
- [vinfra service compute volume snapshot list](#vinfra-service-compute-volume-snapshot-list)
- [vinfra service compute volume snapshot reset-state](#vinfra-service-compute-volume-snapshot-reset-state)
- [vinfra service compute volume snapshot revert](#vinfra-service-compute-volume-snapshot-revert)
- [vinfra service compute volume snapshot set](#vinfra-service-compute-volume-snapshot-set)
- [vinfra service compute volume snapshot show](#vinfra-service-compute-volume-snapshot-show)
- [vinfra service compute volume snapshot upload-to-image](#vinfra-service-compute-volume-snapshot-upload-to-image)
- [vinfra service compute volume upload-to-image](#vinfra-service-compute-volume-upload-to-image)
- [vinfra service compute vpn connection create](#vinfra-service-compute-vpn-connection-create)
- [vinfra service compute vpn connection delete](#vinfra-service-compute-vpn-connection-delete)
- [vinfra service compute vpn connection list](#vinfra-service-compute-vpn-connection-list)
- [vinfra service compute vpn connection restart](#vinfra-service-compute-vpn-connection-restart)
- [vinfra service compute vpn connection set](#vinfra-service-compute-vpn-connection-set)
- [vinfra service compute vpn connection show](#vinfra-service-compute-vpn-connection-show)
- [vinfra service compute vpn endpoint-group list](#vinfra-service-compute-vpn-endpoint-group-list)
- [vinfra service compute vpn endpoint-group show](#vinfra-service-compute-vpn-endpoint-group-show)
- [vinfra service compute vpn ike-policy list](#vinfra-service-compute-vpn-ike-policy-list)
- [vinfra service compute vpn ike-policy show](#vinfra-service-compute-vpn-ike-policy-show)
- [vinfra service compute vpn ipsec-policy list](#vinfra-service-compute-vpn-ipsec-policy-list)
- [vinfra service compute vpn ipsec-policy show](#vinfra-service-compute-vpn-ipsec-policy-show)
- [vinfra service nfs cluster create](#vinfra-service-nfs-cluster-create)
- [vinfra service nfs cluster delete](#vinfra-service-nfs-cluster-delete)
- [vinfra service nfs export create](#vinfra-service-nfs-export-create)
- [vinfra service nfs export delete](#vinfra-service-nfs-export-delete)
- [vinfra service nfs export list](#vinfra-service-nfs-export-list)
- [vinfra service nfs export set](#vinfra-service-nfs-export-set)
- [vinfra service nfs export show](#vinfra-service-nfs-export-show)
- [vinfra service nfs kerberos settings set](#vinfra-service-nfs-kerberos-settings-set)
- [vinfra service nfs kerberos settings show](#vinfra-service-nfs-kerberos-settings-show)
- [vinfra service nfs node add](#vinfra-service-nfs-node-add)
- [vinfra service nfs node list](#vinfra-service-nfs-node-list)
- [vinfra service nfs node release](#vinfra-service-nfs-node-release)
- [vinfra service nfs share create](#vinfra-service-nfs-share-create)
- [vinfra service nfs share delete](#vinfra-service-nfs-share-delete)
- [vinfra service nfs share list](#vinfra-service-nfs-share-list)
- [vinfra service nfs share set](#vinfra-service-nfs-share-set)
- [vinfra service nfs share show](#vinfra-service-nfs-share-show)
- [vinfra service nfs share start](#vinfra-service-nfs-share-start)
- [vinfra service nfs share stop](#vinfra-service-nfs-share-stop)
- [vinfra service s3 cluster change](#vinfra-service-s3-cluster-change)
- [vinfra service s3 cluster create](#vinfra-service-s3-cluster-create)
- [vinfra service s3 cluster delete](#vinfra-service-s3-cluster-delete)
- [vinfra service s3 node add](#vinfra-service-s3-node-add)
- [vinfra service s3 node release](#vinfra-service-s3-node-release)
- [vinfra service s3 replication add](#vinfra-service-s3-replication-add)
- [vinfra service s3 replication delete](#vinfra-service-s3-replication-delete)
- [vinfra service s3 replication list](#vinfra-service-s3-replication-list)
- [vinfra service s3 replication show](#vinfra-service-s3-replication-show)
- [vinfra service s3 replication show token](#vinfra-service-s3-replication-show-token)
- [vinfra service s3 show](#vinfra-service-s3-show)
- [vinfra software-updates cancel](#vinfra-software-updates-cancel)
- [vinfra software-updates check-for-updates](#vinfra-software-updates-check-for-updates)
- [vinfra software-updates download](#vinfra-software-updates-download)
- [vinfra software-updates eligibility-check](#vinfra-software-updates-eligibility-check)
- [vinfra software-updates pause](#vinfra-software-updates-pause)
- [vinfra software-updates resume](#vinfra-software-updates-resume)
- [vinfra software-updates start](#vinfra-software-updates-start)
- [vinfra software-updates status](#vinfra-software-updates-status)
- [vinfra task list](#vinfra-task-list)
- [vinfra task show](#vinfra-task-show)
- [vinfra task wait](#vinfra-task-wait)

---

## vinfra output formatters

### Output formatter options:

**-f {json,table,value,yaml}, --format {json,table,value,yaml}**  
The output format, defaults to `table`.

**-c COLUMN, --column COLUMN**  
Specify the column(s) to include. Can be repeated.

### Table formatter:

**--max-value-length MAX_VALUE_LENGTH**  
Maximum value length. Longer values will be truncated. Set this option to -1 to turn off value truncation. The default is 80.

---

## vinfra cluster alert delete

Remove an entry from the alert log.

```
usage: vinfra cluster alert delete <alert>
```

### Positional arguments:

**\<alert\>**  
Alert ID

---

## vinfra cluster alert list

List alert log entries.

```
usage: vinfra cluster alert list [--long] [--all] [--lang LANG]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--all**  
Show both enabled and disabled alerts.

**--lang LANG**  
Language of alert message. Supported values: en, de,es, ja, pt, ru, tr, zh.

---

## vinfra cluster alert show

Show details of the specified alert log entry.

```
usage: vinfra cluster alert show <alert>
```

### Positional arguments:

**\<alert\>**  
Alert ID

---

## vinfra cluster alert types list

List alert types.

```
usage: vinfra cluster alert types list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster auditlog list

List all audit log entries.

```
usage: vinfra cluster auditlog list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster auditlog show

Show details of an audit log entry.

```
usage: vinfra cluster auditlog show <auditlog>
```

### Positional arguments:

**\<auditlog\>**  
Audit log ID

---

## vinfra cluster backup create

Create a backup.

```
usage: vinfra cluster backup create [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster backup show

Show backup information.

```
usage: vinfra cluster backup show
```

---

## vinfra cluster create

Create a storage cluster.

```
usage: vinfra cluster create [--wait] [--timeout <seconds>]
                             [--tier-encryption {0,1,2,3}]
                             [--disk <disk>:<role>[:<key1=value1,key2=value2...>]]
                             --node <node> <cluster-name>
```

### Positional arguments:

**\<cluster-name\>**  
Storage cluster name

### Optional arguments:

**--tier-encryption {0,1,2,3}**  
Enable encryption for storage cluster tiers. Encryption is disabled by default. This option can be used multiple times.

**--disk \<disk\>:\<role\>[:\<key1=value1,key2=value2...\>]**  
Disk configuration in the format:  
**disk**: disk device ID or name;  
**role**: disk role ('cs', 'mds', 'journal', 'mds-journal', 'mds-system', 'cs-system', 'system');  
Comma-separated key=value pairs with keys (optional):  
**tier**: disk tier (0, 1, 2 or 3);  
**journal-tier**: journal (cache) disk tier (0, 1, 2 or 3);  
**journal-type**: journal (cache) disk type ('no_cache', 'inner_cache' or 'external_cache');  
**journal-disk**: journal (cache) disk ID or device name;  
**bind-address**: bind IP address for the metadata service;  
e.g., `sda:cs:tier=0,journal-type=inner_cache` (this option can be used multiple times).

**--node \<node\>**  
Node ID or hostname

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster delete

Delete the storage cluster.

```
usage: vinfra cluster delete [--timeout <seconds>]
```

### Optional arguments:

**--timeout \<seconds\>**  
A timeout for the operation to complete, in seconds (default: 600)

---

## vinfra cluster ha create

Create a HA configuration.

```
usage: vinfra cluster ha create [--wait] [--timeout <seconds>]
                                --virtual-ip <network:ip[:addr-type]>
                                --nodes <nodes> [--force]
```

### Optional arguments:

**--virtual-ip \<network:ip[:addr-type]\>**  
HA configuration mapping in the format:  
**network**: network to include in the HA configuration (must include at least one of these traffic types: Internal management, Admin panel, Self-service panel or Compute API);  
**ip**: virtual IP address that will be used in the HA configuration;  
**addr_type**: virtual IP address type (supported starting from 3.5 release) (optional).  
Specify this option multiple times to create a HA configuration for multiple networks.

**--nodes \<nodes\>**  
A comma-separated list of node IDs or hostnames

**--force**  
Skip checks for minimal hardware requirements.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster ha delete

Delete the HA configuration.

```
usage: vinfra cluster ha delete [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster ha node add

Add nodes to the HA configuration.

```
usage: vinfra cluster ha node add [--wait] [--timeout <seconds>]
                                  --nodes <nodes> [--without-compute-controller]
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node IDs or hostnames

**--without-compute-controller**  
Deploy the management node without the compute controller service.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster ha node remove

Remove a node from the HA configuration.

```
usage: vinfra cluster ha node remove [--wait] [--timeout <seconds>]
                                     <node> [--force]
```

### Positional arguments:

**\<node\>**  
Node ID or hostname to remove

### Optional arguments:

**--force**  
Skip the compute cluster state and forcibly remove the node.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster ha show

Display the HA configuration.

```
usage: vinfra cluster ha show
```

---

## vinfra cluster ha update

Update the HA configuration.

```
usage: vinfra cluster ha update [--wait] [--timeout <seconds>]
                                [--virtual-ip <network:ip[:addr-type]>]
                                [--nodes <nodes>] [--force]
```

### Optional arguments:

**--virtual-ip \<network:ip[:addr-type]\>**  
HA configuration mapping in the format:  
**network**: network to include in the HA configuration (must include at least one of these traffic types: Internal management, Admin panel, Self-service panel or Compute API);  
**ip**: virtual IP address that will be used in the HA configuration;  
**addr_type**: virtual IP address type (supported starting from 3.5 release) (optional).  
This option can be used multiple times.

**--nodes \<nodes\>**  
A comma-separated list of node IDs or hostnames

**--force**  
Skip checks for minimal hardware requirements.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster license load

Load a license from a key.

```
usage: vinfra cluster license load <license-key>
```

### Positional arguments:

**\<license-key\>**  
License key to register

---

## vinfra cluster license show

Show details of the installed license.

```
usage: vinfra cluster license show
```

---

## vinfra cluster license update

Update the installed license.

```
usage: vinfra cluster license update [--server <ka-server>]
```

### Optional arguments:

**--server \<ka-server\>**  
Hostname[:port] of the key administration server

---

## vinfra cluster network conversion precheck

Check VLAN network interfaces to Open vSwitch VLAN conversion.

```
usage: vinfra cluster network conversion precheck --network <network>
                                                  [--physical-network-name <name>]
```

### Optional arguments:

**--network \<network\>**  
The ID or name of the network, which is connected to VLAN interface

**--physical-network-name \<name\>**  
New network name for parent interfaces

---

## vinfra cluster network conversion start

Convert VLAN network interfaces to Open vSwitch VLAN, and connect a new network to physical interfaces if they have no assignment.

```
usage: vinfra cluster network conversion start [--wait] [--timeout <seconds>]
                                               --network <network>
                                               [--physical-network-name <name>]
```

### Optional arguments:

**--network \<network\>**  
The ID or name of the network, which is connected to VLAN interfaces

**--physical-network-name \<name\>**  
New network name for parent interfaces

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network conversion status

Get VLAN network interfaces conversion status.

```
usage: vinfra cluster network conversion status [--wait] [--timeout <seconds>]
                                                <task>
```

### Positional arguments:

**\<task\>**  
Task ID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network create

Create a new network.

```
usage: vinfra cluster network create [--traffic-types <traffic-types>]
                                     [--inbound-allow-list <addresses>]
                                     [--inbound-deny-list <addresses>]
                                     [--outbound-allow-list <rules>]
                                     <network-name>
```

### Positional arguments:

**\<network-name\>**  
Network name

### Optional arguments:

**--traffic-types \<traffic-types\>**  

A comma-separated list of traffic type IDs or names

**--inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

**--outbound-allow-list \<rules\>**  
A comma-separated list of allow rules

---

## vinfra cluster network delete

Delete a network.

```
usage: vinfra cluster network delete <network>
```

### Positional arguments:

**\<network\>**  
Network ID or name

---

## vinfra cluster network encryption bypass add

Add exception for traffic encryption.

```
usage: vinfra cluster network encryption bypass add <subnet> <port>
```

### Positional arguments:

**\<subnet\>**  
CIDR or single address

**\<port\>**  
Port number

---

## vinfra cluster network encryption bypass delete

Delete exception for traffic encryption.

```
usage: vinfra cluster network encryption bypass delete <subnet> <port>
```

### Positional arguments:

**\<subnet\>**  
CIDR or single address

**\<port\>**  
Port number

---

## vinfra cluster network encryption bypass list

List exceptions for traffic encryption.

```
usage: vinfra cluster network encryption bypass list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster network encryption cancel

Cancel enabling/disabling of traffic encryption.

```
usage: vinfra cluster network encryption cancel
```

---

## vinfra cluster network encryption disable

Disable traffic encryption.

```
usage: vinfra cluster network encryption disable [--wait] [--timeout <seconds>]
                                                 <network> [<network> ...]
```

### Positional arguments:

**\<network\>**  
Network ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network encryption enable

Enable traffic encryption.

```
usage: vinfra cluster network encryption enable [--wait] [--timeout <seconds>]
                                                [--no-switch-storage-ipv6]
                                                <network> [<network> ...]
```

### Positional arguments:

**\<network\>**  
Network ID or name

### Optional arguments:

**--no-switch-storage-ipv6**  
Do not switch CSes to IPv6 addresses

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network encryption status

Get status of traffic encryption.

```
usage: vinfra cluster network encryption status [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster network ipv6-prefix assign

Assign IPv6 prefix.

```
usage: vinfra cluster network ipv6-prefix assign [--wait] [--timeout <seconds>]
                                                 [--force] <prefix>
```

### Positional arguments:

**\<prefix\>**  
IPv6 prefix

### Optional arguments:

**--force**  
Skip checks and forcibly assign the IPv6 prefix.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network ipv6-prefix remove

Remove IPv6 prefix.

```
usage: vinfra cluster network ipv6-prefix remove [--wait] [--timeout <seconds>]
                                                 [--force]
```

### Optional arguments:

**--force**  
Skip checks and forcibly remove the IPv6 prefix.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network ipv6-prefix show

Show IPv6 prefix.

```
usage: vinfra cluster network ipv6-prefix show
```

---

## vinfra cluster network list

List available networks.

```
usage: vinfra cluster network list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster network migration apply

Continue network migration to apply the new network configuration.

```
usage: vinfra cluster network migration apply [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network migration resume

Resume network migration after the cluster shutdown.

```
usage: vinfra cluster network migration resume [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network migration retry

Retry an operation for network migration.

```
usage: vinfra cluster network migration retry [--wait] [--timeout <seconds>]
                                              [--subnet <subnet>]
                                              [--netmask <netmask>]
                                              [--node <node> <address>]
```

### Optional arguments:

**--subnet \<subnet\>**  
New network subnet

**--netmask \<netmask\>**  
New network mask

**--node \<node\> \<address\>**  
New node address in the format:  
**node**: node ID or hostname;  
**address**: IPv4 address.  
This option can be used multiple times.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network migration revert

Revert network migration.

```
usage: vinfra cluster network migration revert [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network migration show

Display network migration details.

```
usage: vinfra cluster network migration show [--full] [--task-id <task-id>]
```

### Optional arguments:

**--full**  
Show full information

**--task-id \<task-id\>**  
The task ID of network migration

---

## vinfra cluster network migration start

Start network migration.

```
usage: vinfra cluster network migration start [--wait] [--timeout <seconds>]
                                              --network <network>
                                              [--subnet <subnet>]
                                              [--netmask <netmask>]
                                              [--gateway <gateway>]
                                              [--shutdown]
                                              [--node <node> <address>]
```

### Optional arguments:

**--network \<network\>**  
Network ID or name

**--subnet \<subnet\>**  
New network subnet

**--netmask \<netmask\>**  
New network mask

**--gateway \<gateway\>**  
New network gateway

**--shutdown**  
Prepare the cluster to be shutdown manually for relocation

**--node \<node\> \<address\>**  
New node address in the format:  
**node**: node ID or hostname;  
**address**: IPv4 address.  
This option can be used multiple times.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network reconfiguration show

Display network reconfiguration details.

```
usage: vinfra cluster network reconfiguration show
```

---

## vinfra cluster network set

Modify network parameters.

```
usage: vinfra cluster network set [--wait] [--timeout <seconds>]
                                  [--name <network-name>]
                                  [--traffic-types <traffic-types> | --add-traffic-types <traffic-types> | --del-traffic-types <traffic-types>]
                                  [--inbound-allow-list <addresses> | --add-inbound-allow-list <addresses> | --del-inbound-allow-list <addresses> | --clear-inbound-allow-list]
                                  [--inbound-deny-list <addresses> | --add-inbound-deny-list <addresses> | --del-inbound-deny-list <addresses> | --clear-inbound-deny-list]
                                  [--outbound-allow-list <rules> | --add-outbound-allow-list <rules> | --del-outbound-allow-list <rules> | --clear-outbound-allow-list | --restore-default-outbound-allow-list]
                                  [-y] <network>
```

### Positional arguments:

**\<network\>**  
Network ID or name

### Optional arguments:

**--name \<network-name\>**  
Network name

**--traffic-types \<traffic-types\>**  
A comma-separated list of traffic type names (overwrites network's current traffic types)

**--add-traffic-types \<traffic-types\>**  
A comma-separated list of traffic type names (adds the specified traffic types to the network)

**--del-traffic-types \<traffic-types\>**  
A comma-separated list of traffic type names (removes the specified traffic types from the network)

**--inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--add-inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--del-inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--clear-inbound-allow-list**  
Clear all inbound allow rules

**--inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

**--add-inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

**--del-inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

**--clear-inbound-deny-list**  
Clear all inbound deny rules

**--outbound-allow-list \<rules\>**  
A comma-separated list of allow rules

**--add-outbound-allow-list \<rules\>**  
A comma-separated list of allow rules

**--del-outbound-allow-list \<rules\>**  
A comma-separated list of allow rules

**--clear-outbound-allow-list**  
Clear all outbound allow rules, need confirmation

**--restore-default-outbound-allow-list**  
Restore default outbound allow rules

**-y, --yes**  
Skip yes/no prompt (assume yes)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network set-bulk

Modify traffic types of multiple networks.

```
usage: vinfra cluster network set-bulk [--wait] [--timeout <seconds>]
                                       --network <network>:<traffic-types>
```

### Optional arguments:

**--network \<network\>:\<traffic-types\>**  
Network configuration in the format:  
**network**: network ID or name;  
**traffic-types**: a comma-separated list of traffic type names.  
This option can be used multiple times.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster network show

Show details of a network.

```
usage: vinfra cluster network show <network>
```

### Positional arguments:

**\<network\>**  
Network ID or name

---

## vinfra cluster node join-config get

Get disk configurations for joining a node to the cluster.

```
usage: vinfra cluster node join-config get <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

---

## vinfra cluster node join-config set

Set disk configurations for joining a node to the cluster.

```
usage: vinfra cluster node join-config set [--disk <disk>:<role>[:<key1=value1,key2=value2...>]]
                                           <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Optional arguments:

**--disk \<disk\>:\<role\>[:\<key1=value1,key2=value2...\>]**  
Disk configuration in the format:  
**disk**: disk device ID or name;  
**role**: disk role ('cs', 'mds', 'journal', 'mds-journal', 'mds-system', 'cs-system', 'system');  
Comma-separated key=value pairs with keys (optional):  
**tier**: disk tier (0, 1, 2 or 3);  
**journal-tier**: journal (cache) disk tier (0, 1, 2 or 3);  
**journal-type**: journal (cache) disk type ('no_cache', 'inner_cache' or 'external_cache');  
**journal-disk**: journal (cache) disk ID or device name;  
**bind-address**: bind IP address for the metadata service;  
e.g., `sda:cs:tier=0,journal-type=inner_cache` (this option can be used multiple times).

---

## vinfra cluster overview

Show storage cluster overview.

```
usage: vinfra cluster overview
```

---

## vinfra cluster password reset

Set storage cluster password.

```
usage: vinfra cluster password reset
```

---

## vinfra cluster password show

Show storage cluster password.

```
usage: vinfra cluster password show
```

---

## vinfra cluster problem-report

Generate and send a problem report.

```
usage: vinfra cluster problem-report [--wait] [--timeout <seconds>]
                                     [--email <email>]
                                     [--description <description>] [--send]
                                     [--verbosity-level {minimal,basic,extended}]
                                     [--include-days INCLUDE_DAYS]
                                     [--node NODES]
```

### Optional arguments:

**--email \<email\>**  
Contact email address

**--description \<description\>**  
Problem description

**--send**  
Generate the problem report archive andsend it to the technical support team.

**--verbosity-level {minimal,basic,extended}**  
Set the desired verbosity level for a problem report. The default is 'basic'.

**--include-days INCLUDE_DAYS**  
Set last modification time threshold for logs. The default is 1.

**--node NODES**  
ID or hostname of the node to be included in a problem report. This option can be used multiple times. All cluster nodes are included if the parameter is omitted.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster settings automatic-disk-replacement set

Change automatic disk replacement settings.

```
usage: vinfra cluster settings automatic-disk-replacement set [--tier0 {on,off}] [--tier1 {on,off}]
                                                              [--tier2 {on,off}] [--tier3 {on,off}]
```

### Optional arguments:

**--tier0 {on,off}**  
Enable or disable automatic disk replacement for tier 0

**--tier1 {on,off}**  
Enable or disable automatic disk replacement for tier 1

**--tier2 {on,off}**  
Enable or disable automatic disk replacement for tier 2

**--tier3 {on,off}**  
Enable or disable automatic disk replacement for tier 3

---

## vinfra cluster settings automatic-disk-replacement show

Show automatic disk replacement settings.

```
usage: vinfra cluster settings automatic-disk-replacement show
```

---

## vinfra cluster settings dns set

Set DNS servers.

```
usage: vinfra cluster settings dns set --nameservers <nameservers>
```

### Optional arguments:

**--nameservers \<nameservers\>**  
A comma-separated list of DNS servers

---

## vinfra cluster settings dns show

Display DNS servers.

```
usage: vinfra cluster settings dns show
```

---

## vinfra cluster settings encryption set

Set storage tiers encyption.

```
usage: vinfra cluster settings encryption set [--tier-enable {0,1,2,3}]
                                              [--tier-disable {0,1,2,3}]
```

### Optional arguments:

**--tier-enable {0,1,2,3}**  
Enable encryption for storage tiers. This option can be used multiple times.

**--tier-disable {0,1,2,3}**  
Disable encryption for storage tiers. This option can be used multiple times.

---

## vinfra cluster settings encryption show

Display storage tiers encyption.

```
usage: vinfra cluster settings encryption show
```

---

## vinfra cluster settings locale list

List locales.

```
usage: vinfra cluster settings locale list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster settings locale set

Update locale settings.

```
usage: vinfra cluster settings locale set [--enable | --disable] [--default]
                                          <locale>
```

### Positional arguments:

**\<locale\>**  
Locale language

### Optional arguments:

**--enable**  
Enable the locale.

**--disable**  
Disable the locale.

**--default**  
Set locale as default.

---

## vinfra cluster settings locale show

Display locale information.

```
usage: vinfra cluster settings locale show <locale>
```

### Positional arguments:

**\<locale\>**  
Locale language

---

## vinfra cluster settings number-of-cses-per-disk set

Enabling/Disabling NVMe performance.

```
usage: vinfra cluster settings number-of-cses-per-disk set [--tier0 <number>]
                                                           [--tier1 <number>]
                                                           [--tier2 <number>]
                                                           [--tier3 <number>]
```

### Optional arguments:

**--tier0 \<number\>**  
Set number of CSes per disk for tier 0

**--tier1 \<number\>**  
Set number of CSes per disk for tier 1

**--tier2 \<number\>**  
Set number of CSes per disk for tier 2

**--tier3 \<number\>**  
Set number of CSes per disk for tier 3

---

## vinfra cluster settings number-of-cses-per-disk show

Show NVMe performance settings.

```
usage: vinfra cluster settings number-of-cses-per-disk show
```

---

## vinfra cluster settings ssl set

Update the SSL certificate.

```
usage: vinfra cluster settings ssl set (--self-signed | --cert-file CERT_FILE)
                                       [--key-file KEY_FILE] [--password]
```

### Optional arguments:

**--self-signed**  
Generate a new self-signed certificate.

**--cert-file CERT_FILE**  
Path to a file with the new certificate.

**--key-file KEY_FILE**  
Path to a file with the private key (only used with the `--cert-file` option).

**--password**  
Read certificate password from stdin (only used with the `--cert-file` option).

---

## vinfra cluster settings ssl show

Display SSL configuration.

```
usage: vinfra cluster settings ssl show
```

---

## vinfra cluster show

Show cluster details.

```
usage: vinfra cluster show
```

---

## vinfra cluster sshkey add

Add an SSH public key from a file.

```
usage: vinfra cluster sshkey add [--wait] [--timeout <seconds>]
                                 <file>
```

### Positional arguments:

**\<file\>**  
SSH public key file

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster sshkey delete

Remove an SSH public key from storage cluster nodes.

```
usage: vinfra cluster sshkey delete [--wait] [--timeout <seconds>]
                                    <sshkey>
```

### Positional arguments:

**\<sshkey\>**  
SSH key value

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster sshkey list

Show the list of added SSH public keys.

```
usage: vinfra cluster sshkey list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster storage-policy create

Create a new storage policy.

```
usage: vinfra cluster storage-policy create [--tier {0,1,2,3}]
                                            [--replicas <norm> | --encoding <M>+<N>]
                                            [--failure-domain {0,1,2,3,4}]
                                            [--write-bytes-sec-per-gb <limit>]
                                            [--write-bytes-sec <limit>]
                                            [--read-iops-sec-per-gb <limit>]
                                            [--total-iops-sec <limit>]
                                            [--total-bytes-sec-per-gb-min <limit>]
                                            [--read-iops-sec-per-gb-min <limit>]
                                            [--write-bytes-sec-per-gb-min <limit>]
                                            [--total-bytes-sec-per-gb <limit>]
                                            [--write-iops-sec-per-gb-min <limit>]
                                            [--read-bytes-sec-per-gb-min <limit>]
                                            [--read-bytes-sec-per-gb <limit>]
                                            [--total-iops-sec-per-gb <limit>]
                                            [--read-iops-sec <limit>]
                                            [--read-bytes-sec <limit>]
                                            [--write-iops-sec-per-gb <limit>]
                                            [--write-iops-sec <limit>]
                                            [--total-iops-sec-per-gb-min <limit>]
                                            [--total-bytes-sec <limit>]
                                            [--storage <storage-name>]
                                            [--params <param=value>[,<param2=value2>]
                                            [--params <param3=value3>] ...]
                                            <name>
```

### Positional arguments:

**\<name\>**  
Storage policy name

### Optional arguments:

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--write-bytes-sec-per-gb \<limit\>**  
Write number of bytes per second per GB

**--write-bytes-sec \<limit\>**  
Write number of bytes per second

**--read-iops-sec-per-gb \<limit\>**  
Read number of I/O operations per second per GB

**--total-iops-sec \<limit\>**  
Total number of I/O operations per second

**--total-bytes-sec-per-gb-min \<limit\>**  
Total number of bytes per second per GB (min)

**--read-iops-sec-per-gb-min \<limit\>**  
Read number of I/O operations per second per GB (min)

**--write-bytes-sec-per-gb-min \<limit\>**  
Write number of bytes per second per GB (min)

**--total-bytes-sec-per-gb \<limit\>**  
Total number of bytes per second per GB

**--write-iops-sec-per-gb-min \<limit\>**  
Write number of I/O operations per second per GB (min)

**--read-bytes-sec-per-gb-min \<limit\>**  
Read number of bytes per second per GB (min)

**--read-bytes-sec-per-gb \<limit\>**  
Read number of bytes per second per GB

**--total-iops-sec-per-gb \<limit\>**  
Total number of I/O operations per second per GB

**--read-iops-sec \<limit\>**  
Read number of I/O operations per second

**--read-bytes-sec \<limit\>**  
Read number of bytes per second

**--write-iops-sec-per-gb \<limit\>**  
Write number of I/O operations per second per GB

**--write-iops-sec \<limit\>**  
Write number of I/O operations per second

**--total-iops-sec-per-gb-min \<limit\>**  
Total number of I/O operations per second per GB (min)

**--total-bytes-sec \<limit\>**  
Total number of bytes per second

**--storage \<storage-name\>**  
Compute storage name

**--params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
Custom parameters

---

## vinfra cluster storage-policy delete

Remove an existing storage policy.

```
usage: vinfra cluster storage-policy delete <storage-policy>
```

### Positional arguments:

**\<storage-policy\>**  
Storage policy ID or name

---

## vinfra cluster storage-policy list

List existing storage policies.

```
usage: vinfra cluster storage-policy list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster storage-policy set

Modify storage policy parameters.

```
usage: vinfra cluster storage-policy set [--name <name>] [--tier {0,1,2,3}]
                                         [--replicas <norm> | --encoding <M>+<N>]
                                         [--failure-domain {0,1,2,3,4}]
                                         [--write-bytes-sec-per-gb <limit>]
                                         [--write-bytes-sec <limit>]
                                         [--read-iops-sec-per-gb <limit>]
                                         [--total-iops-sec <limit>]
                                         [--total-bytes-sec-per-gb-min <limit>]
                                         [--read-iops-sec-per-gb-min <limit>]
                                         [--write-bytes-sec-per-gb-min <limit>]
                                         [--total-bytes-sec-per-gb <limit>]
                                         [--write-iops-sec-per-gb-min <limit>]
                                         [--read-bytes-sec-per-gb-min <limit>]
                                         [--read-bytes-sec-per-gb <limit>]
                                         [--total-iops-sec-per-gb <limit>]
                                         [--read-iops-sec <limit>]
                                         [--read-bytes-sec <limit>]
                                         [--write-iops-sec-per-gb <limit>]
                                         [--write-iops-sec <limit>]
                                         [--total-iops-sec-per-gb-min <limit>]
                                         [--total-bytes-sec <limit>]
                                         [--storage <storage-name>]
                                         [--params <param=value>[,<param2=value2>]
                                         [--params <param3=value3>] ...]
                                         [--unset-params <params>]
                                         <storage-policy>
```

### Positional arguments:

**\<storage-policy\>**  
Storage policy ID or name

### Optional arguments:

**--name \<name\>**  
A new name for the storage policy

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--write-bytes-sec-per-gb \<limit\>**  
Write number of bytes per second per GB

**--write-bytes-sec \<limit\>**  
Write number of bytes per second

**--read-iops-sec-per-gb \<limit\>**  
Read number of I/O operations per second per GB

**--total-iops-sec \<limit\>**  
Total number of I/O operations per second

**--total-bytes-sec-per-gb-min \<limit\>**  
Total number of bytes per second per GB (min)

**--read-iops-sec-per-gb-min \<limit\>**  
Read number of I/O operations per second per GB (min)

**--write-bytes-sec-per-gb-min \<limit\>**  
Write number of bytes per second per GB (min)

**--total-bytes-sec-per-gb \<limit\>**  
Total number of bytes per second per GB

**--write-iops-sec-per-gb-min \<limit\>**  
Write number of I/O operations per second per GB (min)

**--read-bytes-sec-per-gb-min \<limit\>**  
Read number of bytes per second per GB (min)

**--read-bytes-sec-per-gb \<limit\>**  
Read number of bytes per second per GB

**--total-iops-sec-per-gb \<limit\>**  
Total number of I/O operations per second per GB

**--read-iops-sec \<limit\>**  
Read number of I/O operations per second

**--read-bytes-sec \<limit\>**  
Read number of bytes per second

**--write-iops-sec-per-gb \<limit\>**  
Write number of I/O operations per second per GB

**--write-iops-sec \<limit\>**  
Write number of I/O operations per second

**--total-iops-sec-per-gb-min \<limit\>**  
Total number of I/O operations per second per GB (min)

**--total-bytes-sec \<limit\>**  
Total number of bytes per second

**--storage \<storage-name\>**  
Compute storage name

**--params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
Custom parameters

**--unset-params \<params\>**  
A comma-separated list of parameters to unset

---

## vinfra cluster storage-policy show

Show details of a storage policy.

```
usage: vinfra cluster storage-policy show <storage-policy>
```

### Positional arguments:

**\<storage-policy\>**  
Storage policy ID or name

---

## vinfra cluster switch-to-ipv6

Switch storage cluster to IPv6.

```
usage: vinfra cluster switch-to-ipv6 [--wait] [--timeout <seconds>] [--reset]
```

### Optional arguments:

**--reset**  
Reset cluster back to IPv4

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster traffic-type assignment apply

Continue traffic type assignment to apply the new network configuration.

```
usage: vinfra cluster traffic-type assignment apply [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster traffic-type assignment retry

Retry an operation for traffic type assignment.

```
usage: vinfra cluster traffic-type assignment retry [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster traffic-type assignment revert

Revert traffic type assignment.

```
usage: vinfra cluster traffic-type assignment revert [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster traffic-type assignment show

Display traffic type assignment details.

```
usage: vinfra cluster traffic-type assignment show [--full] [--task-id <task-id>]
```

### Optional arguments:

**--full**  
Show full information

**--task-id \<task-id\>**  
The task ID of traffic type assignment

---

## vinfra cluster traffic-type assignment start

Start traffic type assignment.

```
usage: vinfra cluster traffic-type assignment start [--wait] [--timeout <seconds>]
                                                    --traffic-type <traffic-type>
                                                    --target-network <target-network>
```

### Optional arguments:

**--traffic-type \<traffic-type\>**  
Traffic type name

**--target-network \<target-network\>**  
Target network ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster traffic-type create

Create a new traffic type.

```
usage: vinfra cluster traffic-type create --port <port>
                                          [--inbound-allow-list <addresses>]
                                          [--inbound-deny-list <addresses>]
                                          <traffic-type-name>
```

### Positional arguments:

**\<traffic-type-name\>**  
Traffic type name

### Optional arguments:

**--port \<port\>**  
Traffic type port

**--inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

---

## vinfra cluster traffic-type delete

Delete a traffic type.

```
usage: vinfra cluster traffic-type delete <traffic-type>
```

### Positional arguments:

**\<traffic-type\>**  
Traffic type name

---

## vinfra cluster traffic-type list

List available traffic types.

```
usage: vinfra cluster traffic-type list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster traffic-type set

Modify traffic type parameters.

```
usage: vinfra cluster traffic-type set [--wait] [--timeout <seconds>]
                                       [--name <name>] [--port <port>]
                                       [--inbound-allow-list <addresses> | --add-inbound-allow-list <addresses> | --del-inbound-allow-list <addresses> | --clear-inbound-allow-list]
                                       [--inbound-deny-list <addresses> | --add-inbound-deny-list <addresses> | --del-inbound-deny-list <addresses> | --clear-inbound-deny-list]
                                       <traffic-type>
```

### Positional arguments:

**\<traffic-type\>**  
Traffic type name

### Optional arguments:

**--name \<name\>**  
A new name for the traffic type

**--port \<port\>**  
A new port for the traffic type

**--inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--add-inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--del-inbound-allow-list \<addresses\>**  
A comma-separated list of IP addresses

**--clear-inbound-allow-list**  
Clear all inbound allow rules

**--inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

**--add-inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

**--del-inbound-deny-list \<addresses\>**  
A comma-separated list of IP addreses

**--clear-inbound-deny-list**  
Clear all inbound deny rules

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cluster traffic-type show

Show details of a traffic type.

```
usage: vinfra cluster traffic-type show <traffic-type>
```

### Positional arguments:

**\<traffic-type\>**  
Traffic type name

---

## vinfra cluster user change-password

Change password of an admin panel user.

```
usage: vinfra cluster user change-password
```

---

## vinfra cluster user create

Add an admin panel user.

```
usage: vinfra cluster user create [--description <description>]
                                  [--enable | --disable] [--roles <roles>]
                                  <name>
```

### Positional arguments:

**\<name\>**  
User name

### Optional arguments:

**--description \<description\>**  
User description

**--enable**  
Enable user

**--disable**  
Disable user

**--roles \<roles\>**  
A comma-separated list of user roles

---

## vinfra cluster user delete

Remove an admin panel user.

```
usage: vinfra cluster user delete <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

---

## vinfra cluster user list

List all admin panel users.

```
usage: vinfra cluster user list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster user list-available-roles

List available user roles.

```
usage: vinfra cluster user list-available-roles [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra cluster user set

Modify admin panel user parameters.

```
usage: vinfra cluster user set [--description <description>]
                               [--enable | --disable]
                               [--set-roles <roles> | --add-roles <roles> | --del-roles <roles>]
                               [--password] [--name <name>]
                               <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

### Optional arguments:

**--description \<description\>**  
User description

**--enable**  
Enable user

**--disable**  
Disable user

**--set-roles \<roles\>**  
A comma-separated list of user roles to set (overwrites the current user roles)

**--add-roles \<roles\>**  
A comma-separated list of user roles to add

**--del-roles \<roles\>**  
A comma separated list of user roles to remove

**--password**  
Request the password from stdin.

**--name \<name\>**  
A new name for the user

---

## vinfra cluster user show

Show details of an admin panel user.

```
usage: vinfra cluster user show <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

---

## vinfra cses-config change

Change CS config.

```
usage: vinfra cses-config change [--wait] [--timeout <seconds>] [--enable]
                                 [--disable]
```

### Optional arguments:

**--enable**  
Enable RDMA

**--disable**  
Disable RDMA

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra cses-config show

Show CS config.

```
usage: vinfra cses-config show
```

---

## vinfra domain create

Create a new domain.

```
usage: vinfra domain create [--description <description>] [--enable]
                            [--disable] <name>
```

### Positional arguments:

**\<name\>**  
Domain name

### Optional arguments:

**--description \<description\>**  
Domain description

**--enable**  
Enable domain

**--disable**  
Disable domain

---

## vinfra domain delete

Delete a domain.

```
usage: vinfra domain delete <domain>
```

### Positional arguments:

**\<domain\>**  
Domain ID or name

---

## vinfra domain group create

Create a new domain group.

```
usage: vinfra domain group create [--description <description>]
                                  [--assign <project> <role>]
                                  [--assign-domain <domain> <roles>]
                                  [--domain-permissions <domain_permissions>]
                                  [--system-permissions <system_permissions>]
                                  --domain <domain> <name>
```

### Positional arguments:

**\<name\>**  
Group name

### Optional arguments:

**--description \<description\>**  
Group description

**--assign \<project\> \<role\>**  
Assign a group to a project with one or more permission sets. Specify this option multiple times to assign the group to multiple projects.  
**project**: project ID or name;  
**role**: group role in project.

**--assign-domain \<domain\> \<roles\>**  
Assign a group to a domain with one or more permission sets. Specify this option multiple times to assign the group to multiple domains. This option is only valid for service accounts.  
**domain**: domain ID or name;  
**roles**: a comma-separated list of service account roles.

**--domain-permissions \<domain_permissions\>**  
A comma-separated list of domain permissions

**--system-permissions \<system_permissions\>**  
A comma-separated list of system permissions

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain group delete

Remove a domain group.

```
usage: vinfra domain group delete --domain <domain> <group>
```

### Positional arguments:

**\<group\>**  
Group ID or name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain group list

List all groups in a domain.

```
usage: vinfra domain group list [--long] --domain <domain> [--limit <num>]
                                [--marker <group>] [--name <name>] [--id <id>]
                                [--tags <tag>[,<tag>,...]]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--domain \<domain\>**  
Domain name or ID

**--limit \<num\>**  
The maximum number of groups to list. To list all groups, set the option to -1.

**--marker \<group\>**  
List groups after the marker.

**--name \<name\>**  
List groups with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a group with the specified ID or list groups using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--tags \<tag\>[,\<tag\>,...]**  
List groups with the specified tags (comma-separated) or use a filter. Supported filter operators: any, not_any. The filter format is `<operator>:<value1>[,<value2>,...]`.

---

## vinfra domain group set

Modify the parameters of a domain group.

```
usage: vinfra domain group set [--name <name>] [--description <description>]
                               [--assign <project> <role>]
                               [--unassign <project>]
                               [--assign-domain <domain> <roles>]
                               [--unassign-domain <domain>]
                               [--domain-permissions <domain_permissions>]
                               [--system-permissions <system_permissions>]
                               --domain <domain>
                               <group>
```

### Positional arguments:

**\<group\>**  
Group ID or name

### Optional arguments:

**--name \<name\>**  
New group name

**--description \<description\>**  
Group description

**--assign \<project\> \<role\>**  
Assign a group to a project with one or more permission sets. Specify this option multiple times to assign the group to multiple projects.  
**project**: project ID or name;  
**role**: group role in project.

**--unassign \<project\>**  
Unassign a group from a project. Specify this option multiple times to unassign the group from multiple projects.  
**project**: project ID or name.

**--assign-domain \<domain\> \<roles\>**  
Assign a group to a domain with one or more permission sets. Specify this option multiple times to assign the group to multiple domains. This option is only valid for service accounts.  
**domain**: domain ID or name;  
**roles**: a comma-separated list of service account roles.

**--unassign-domain \<domain\>**  
Unassign a group from a domain. Specify this option multiple times to unassign the group from multiple domains. This option is only valid for service accounts.  
**domain**: domain ID or name.

**--domain-permissions \<domain_permissions\>**  
A comma-separated list of domain permissions

**--system-permissions \<system_permissions\>**  
A comma-separated list of system permissions

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain group show

Display information about a domain group.

```
usage: vinfra domain group show --domain <domain> <group>
```

### Positional arguments:

**\<group\>**  
Group ID or name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain group user add

Add a user to a group.

```
usage: vinfra domain group user add --domain <domain> <group> <user>
```

### Positional arguments:

**\<group\>**  
Group ID or name

**\<user\>**  
User ID or name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain group user list

List users of a group.

```
usage: vinfra domain group user list [--long] --domain <domain> <group>
```

### Positional arguments:

**\<group\>**  
Group ID or name

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain group user remove

Remove a user from a group.

```
usage: vinfra domain group user remove --domain <domain> <group> <user>
```

### Positional arguments:

**\<group\>**  
Group ID or name

**\<user\>**  
User ID or name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain idp create

Create a new domain identity provider.

```
usage: vinfra domain idp create --domain <domain> --issuer <issuer> --scope <issuer>
                                [--response-type <response-type>]
                                [--metadata-url <metadata-url>]
                                [--client-id <client-id>]
                                [--client-secret <client-secret>]
                                [--mapping <path>] [--enable] [--disable] <name>
```

### Positional arguments:

**\<name\>**  
Identity provider name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

**--issuer \<issuer\>**  
Identity provider issuer

**--scope \<issuer\>**  
Scope that define what user identity data will be shared by the identity provider during authentication

**--response-type \<response-type\>**  
Response type to be used in authorization flow

**--metadata-url \<metadata-url\>**  
Metadata URL of the identity provider's dicovery endpoint

**--client-id \<client-id\>**  
Client ID to access the identity provider

**--client-secret \<client-secret\>**  
Client secret to access the identity provider

**--mapping \<path\>**  
Path to the mapping configuration file.

**--enable**  
Enable identity provider

**--disable**  
Disable identity provider

---

## vinfra domain idp delete

Delete a domain identity provider.

```
usage: vinfra domain idp delete --domain <domain> <idp>
```

### Positional arguments:

**\<idp\>**  
Identity provider name or ID

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain idp list

List domain identity providers.

```
usage: vinfra domain idp list [--long] --domain <domain>
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain idp set

Modify an existing domain identity provider.

```
usage: vinfra domain idp set [--issuer <issuer>] [--scope <issuer>]
                             [--response-type <response-type>]
                             [--metadata-url <metadata-url>]
                             [--client-id <client-id>]
                             [--client-secret <client-secret>]
                             [--mapping <path>] [--enable] [--disable]
                             [--name <name>] --domain <domain> <idp>
```

### Positional arguments:

**\<idp\>**  
Identity provider name or ID

### Optional arguments:

**--issuer \<issuer\>**  
Identity provider issuer

**--scope \<issuer\>**  
Scope that define what user identity data will be shared by the identity provider during authentication

**--response-type \<response-type\>**  
Response type to be used in authorization flow

**--metadata-url \<metadata-url\>**  
Metadata URL of the identity provider's dicovery endpoint

**--client-id \<client-id\>**  
Client ID to access the identity provider

**--client-secret \<client-secret\>**  
Client secret to access the identity provider

**--mapping \<path\>**  
Path to the mapping configuration file.

**--enable**  
Enable identity provider

**--disable**  
Disable identity provider

**--name \<name\>**  
A new name for the identity provider

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain idp show

Show details of a domain identity provider.

```
usage: vinfra domain idp show --domain <domain> <idp>
```

### Positional arguments:

**\<idp\>**  
Identity provider name or ID

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain list

List all available domains.

```
usage: vinfra domain list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra domain project create

Create a new domain project.

```
usage: vinfra domain project create [--description <description>]
                                    [--enable | --disable] --domain <domain>
                                    <name>
```

### Positional arguments:

**\<name\>**  
Project name

### Optional arguments:

**--description \<description\>**  
Project description

**--enable**  
Enable project

**--disable**  
Disable project

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain project delete

Delete a domain project.

```
usage: vinfra domain project delete --domain <domain> <project>
```

### positional arguments:

**\<project\>**  
Project name or ID

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain project list

List domain projects.

```
usage: vinfra domain project list [--long] --domain <domain> [--limit <num>]
                                  [--marker <project>] [--name <name>]
                                  [--id <id>] [--tags <tag>[,<tag>,...]]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--domain \<domain\>**  
Domain name or ID

**--limit \<num\>**  
The maximum number of projects to list. To list all projects, set the option to -1.

**--marker \<project\>**  
List projects after the marker.

**--name \<name\>**  
List projects with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a project with the specified ID or list projects using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--tags \<tag\>[,\<tag\>,...]**  
List projects with the specified tags (comma-separated) or use a filter. Supported filter operators: any, not_any. The filter format is `<operator>:<value1>[,<value2>,...]`.

---

## vinfra domain project set

Modify an existing domain project.

```
usage: vinfra domain project set [--description <description>]
                                 [--enable | --disable] [--name <name>]
                                 --domain <domain> <project>
```

### Positional arguments:

**\<project\>**  
Project name or ID

### Optional arguments:

**--description \<description\>**  
Project description

**--enable**  
Enable project

**--disable**  
Disable project

**--name \<name\>**  
New project name

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain project show

Show details of a domain project.

```
usage: vinfra domain project show --domain <domain> <project>
```

### Positional arguments:

**\<project\>**  
Project name or ID

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain project user list

List users of a project.

```
usage: vinfra domain project user list [--long] --domain <domain>
                                       <project>
```

### Positional arguments:

**\<project\>**  
Project name or ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain project user remove

Remove a user from a project.

```
usage: vinfra domain project user remove --user <user> --domain <domain>
                                         <project>
```

### Positional arguments:

**\<project\>**  
Project name or ID

### Optional arguments:

**--user \<user\>**  
User name or ID

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain properties access list

List key and access rights of all property sheets of the domain specified by ID or name.

```
usage: vinfra domain properties access list [--long] <domain>
```

### Positional arguments:

**\<domain\>**  
Domain name or domain ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra domain properties access set

Update an access rights of the property sheet of the domain specified by ID or name and key.

```
usage: vinfra domain properties access set [--access <access>]
                                           [--key <key>] <domain>
```

### Positional arguments:

**\<domain\>**  
Domain name or domain ID

### Optional arguments:

**--access \<access\>**  
Access type

**--key \<key\>**  
Key name

---

## vinfra domain properties create

Create a property sheet for the domain specified by ID or name and key.

```
usage: vinfra domain properties create --key <key> --data <data>
                                       [--access <access>] <domain>
```

### Positional arguments:

**\<domain\>**  
Domain name or domain ID

### Optional arguments:

**--key \<key\>**  
Key name

**--data \<data\>**  
Property sheet. Should be a valid JSON object.

**--access \<access\>**  
Access type

---

## vinfra domain properties delete

Delete a property sheet of the domain specified by ID or name and key.

```
usage: vinfra domain properties delete --key <key> <domain>
```

### Positional arguments:

**\<domain\>**  
Domain name or domain ID

### Optional arguments:

**--key \<key\>**  
Key name

---

## vinfra domain properties keys list

Show all available keys for each known domain.

```
usage: vinfra domain properties keys list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra domain properties show

Show a property sheet of the domain specified by ID or name and key.

```
usage: vinfra domain properties show --key <key> <domain>
```

### Positional arguments:

**\<domain\>**  
Domain name or domain ID

### Optional arguments:

**--key \<key\>**  
Key name

---

## vinfra domain properties update

Update a property sheet of the domain specified by ID or name and key.

```
usage: vinfra domain properties update --key <key> --data <data>
                                       [--access <access>] <domain>
```

### Positional arguments:

**\<domain\>**  
Domain name or domain ID

### Optional arguments:

**--key \<key\>**  
Key name

**--data \<data\>**  
Property sheet. Should be a valid JSON object.

**--access \<access\>**  
Access type

---

## vinfra domain set

Modify an existing domain.

```
usage: vinfra domain set [--description <description>] [--enable] [--disable]
                         [--name <name>] <domain>
```

### Positional arguments:

**\<domain\>**  
Domain ID or name

### Optional arguments:

**--description \<description\>**  
Domain description

**--enable**  
Enable domain

**--disable**  
Disable domain

**--name \<name\>**  
Domain name

---

## vinfra domain show

Display information about a domain.

```
usage: vinfra domain show <domain>
```

### Positional arguments:

**\<domain\>**  
Domain ID or name

---

## vinfra domain user create

Create a new domain user.

```
usage: vinfra domain user create [--email <name>] [--description <description>]
                                 [--assign <project> <role>]
                                 [--assign-domain <domain> <roles>]
                                 [--domain-permissions <domain_permissions>]
                                 [--system-permissions <system_permissions>]
                                 [--enable | --disable] --domain <domain>
                                 <name>
```

### Positional arguments:

**\<name\>**  
User name

### Optional arguments:

**--email \<name\>**  
User email

**--description \<description\>**  
User description

**--assign \<project\> \<role\>**  
Assign a user to a project with one or more permission sets. Specify this option multiple times to assign the user to multiple projects.  
**project**: project ID or name;  
**role**: user role in project.

**--assign-domain \<domain\> \<roles\>**  
Assign a user to a domain with one or more permission sets. Specify this option multiple times to assign the user to multiple domains. This option is only valid for service accounts.  
**domain**: domain ID or name;  
**roles**: a comma-separated list of service account roles.

**--domain-permissions \<domain_permissions\>**  
A comma-separated list of domain permissions

**--system-permissions \<system_permissions\>**  
A comma-separated list of system permissions

**--enable**  
Enable user

**--disable**  
Disable user

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain user delete

Remove a domain user.

```
usage: vinfra domain user delete --domain <domain> <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain user group list

List users of a group.

```
usage: vinfra domain user group list [--long] --domain <domain>
                                     <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain user list

List all users in a domain.

```
usage: vinfra domain user list [--long] --domain <domain> [--limit <num>]
                               [--marker <user>] [--name <name>] [--id <id>]
                               [--tags <tag>[,<tag>,...]]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--domain \<domain\>**  
Domain name or ID

**--limit \<num\>**  
The maximum number of users to list. To list all users, set the option to -1.

**--marker \<user\>**  
List users after the marker.

**--name \<name\>**  
List projects with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a user with the specified ID or list users using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--tags \<tag\>[,\<tag\>,...]**  
List users with the specified tags (comma-separated) or use a filter. Supported filter operators: any, not_any. The filter format is `<operator>:<value1>[,<value2>,...]`.

---

## vinfra domain user list-available-roles

List available user roles.

```
usage: vinfra domain user list-available-roles [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra domain user set

Modify the parameters of a domain user.

```
usage: vinfra domain user set [--password] [--name <name>] [--email <name>]
                              [--description <description>]
                              [--assign <project> <role>]
                              [--unassign <project>]
                              [--assign-domain <domain> <roles>]
                              [--unassign-domain <domain>]
                              [--domain-permissions <domain_permissions>]
                              [--system-permissions <system_permissions>]
                              [--enable | --disable] --domain <domain>
                              <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

### Optional arguments:

**--password**  
Request the password from stdin.

**--name \<name\>**  
New user name

**--email \<name\>**  
User email

**--description \<description\>**  
User description

**--assign \<project\> \<role\>**  
Assign a user to a project with one or more permission sets. Specify this option multiple times to assign the user to multiple projects.  
**project**: project ID or name;  
**role**: user role in project.

**--unassign \<project\>**  
Unassign a user from a project. Specify this option multiple times to unassign the user from multiple projects.  
**project**: project ID or name.

**--assign-domain \<domain\> \<roles\>**  
Assign a user to a domain with one or more permission sets. Specify this option multiple times to assign the user to multiple domains. This option is only valid for service accounts.  
**domain**: domain ID or name;  
**roles**: a comma-separated list of service account roles.

**--unassign-domain \<domain\>**  
Unassign a user from a domain. Specify this option multiple times to unassign the user from multiple domains. This option is only valid for service accounts.  
**domain**: domain ID or name.

**--domain-permissions \<domain_permissions\>**  
A comma-separated list of domain permissions

**--system-permissions \<system_permissions\>**  
A comma-separated list of system permissions

**--enable**  
Enable user

**--disable**  
Disable user

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain user show

Display information about a domain user.

```
usage: vinfra domain user show --domain <domain> <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra domain user unlock

Unlock a domain user.

```
usage: vinfra domain user unlock --domain <domain> <user>
```

### Positional arguments:

**\<user\>**  
User ID or name

### Optional arguments:

**--domain \<domain\>**  
Domain name or ID

---

## vinfra failure domain list

Show available failure domains.

```
usage: vinfra failure domain list [--long]
```

Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra failure domain rename

Set names for failure domain levels, which define the storage location. These four levels are 1=host, 2=rack, 3=row, 4=room. The names for levels 2, 3 and 4 can be changed.

```
usage: vinfra failure domain rename {2,3,4} <singular-name> <plural-name>
```

### Positional arguments:

**{2,3,4}**  
Failure domain ID

**\<singular-name\>**  
Singular name of the specified failure domain

**\<plural-name\>**  
Plural name of the specified failure domain

---

## vinfra location create

Create a new child location of the specified failure domain within the parent location identified by ID.

```
usage: vinfra location create --fd <fd> --name <location-name> [--parent-id <parent-id>]
```

### Optional arguments:

**--fd \<fd\>**  
Failure domain ID

**--name \<location-name\>**  
Name of the location to be created

**--parent-id \<parent-id\>**  
ID of the parent location where the child location should be created in

---

## vinfra location delete

Delete the location of specified failure domain and identified by ID.

```
usage: vinfra location delete --fd <fd> --id <location-id>
```

### Optional arguments:

**--fd \<fd\>**  
Failure domain ID

**--id \<location-id\>**  
ID of the location to delete

---

## vinfra location list

List locations of the specified failure domain.

```
usage: vinfra location list [--long] --fd <fd>
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--fd \<fd\>**  
Failure domain ID

---

## vinfra location move

Move locations identified by IDs to the parent location of the specified failure domain and identified by ID.

```
usage: vinfra location move --children <children> [<children> ...]
                            --parent-fd <parent-fd> --parent-id <parent-id>
```

### Optional arguments:

**--children \<children\> [\<children\> ...]**  
IDs of locations to be moved to the parent location.

**--parent-fd \<parent-fd\>**  
The failure domain of the parent location.

**--parent-id \<parent-id\>**  
ID of the parent location

---

## vinfra location rename

Change the name of the location of the specified failure domain and identified by ID.

```
usage: vinfra location rename --fd <fd> --id <location-id>
                              --name <location-name>
```

### Optional arguments:

**--fd \<fd\>**  
Failure domain ID

**--id \<location-id\>**  
ID of the location to rename

**--name \<location-name\>**  
The new location name.

---

## vinfra location show

Show the location of the specified failure domain and identified by ID.

```
usage: vinfra location show --fd <fd> --id <location-id>
```

### Optional arguments:

**--fd \<fd\>**  
Failure domain ID

**--id \<location-id\>**  
ID of the location to show

---

## vinfra logging severity set

Show the logging severity for nodes specified by ID or host name.

```
usage: vinfra logging severity set [--nodes [<nodes> <nodes> ...]]
                                   {INFO,WARNING,TRACE,CRITICAL,ERROR,DEBUG,NOTSET}
```

### Positional arguments:

**{INFO,WARNING,TRACE,CRITICAL,ERROR,DEBUG,NOTSET}**  
Choose logging severity

### Optional arguments:

**--nodes \<nodes\> [\<nodes\> ...]**  
A space-separated or comma-separated list of node hostnames or IDs

---

## vinfra logging severity show

Show the logging severity for nodes specified by ID or host name.

```
usage: vinfra logging severity show [--long] [--nodes <nodes> [<nodes> ...]]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--nodes \<nodes\> [\<nodes\> ...]**  
A space-separated or comma-separated list of node hostnames or IDs

---

## vinfra memory-policy vstorage-services per-cluster change

Change per-cluster memory parameters.

```
usage: vinfra memory-policy vstorage-services per-cluster change [--guarantee <guarantee>] [--swap <swap>]
                                                                 [--cache-ratio <cache-ratio>]
                                                                 [--cache-minimum <cache-minimum>]
                                                                 [--cache-maximum <cache-maximum>]
```

### Optional arguments:

**--guarantee \<guarantee\>**  
Guarantee, in bytes

**--swap \<swap\>**  
Swap size, in bytes, or -1 if unlimited

**--cache-ratio \<cache-ratio\>**  
Cache ratio from 0 to 1 inclusive

**--cache-minimum \<cache-minimum\>**  
Min. cache, in bytes

**--cache-maximum \<cache-maximum\>**  
Max. cache, in bytes

---

## vinfra memory-policy vstorage-services per-cluster reset

Reset per-cluster parameters to default.

```
usage: vinfra memory-policy vstorage-services per-cluster reset [--guarantee] [--swap] [--cache]
```

### Optional arguments:

**--guarantee**  
Reset the guarantee size

**--swap**  
Reset the swap size

**--cache**  
Reset the cache size

---

## vinfra memory-policy vstorage-services per-cluster show

Show per-cluster memory parameters.

```
usage: vinfra memory-policy vstorage-services per-cluster show
```

---

## vinfra memory-policy vstorage-services per-node change

Change per-node memory parameters.

```
usage: vinfra memory-policy vstorage-services per-node change --node <node>
                                                              [--guarantee <guarantee>] [--swap <swap>]
                                                              [--cache-ratio <cache-ratio>]
                                                              [--cache-minimum <cache-minimum>]
                                                              [--cache-maximum <cache-maximum>]
```

### Optional arguments:

**--node \<node\>**  
Node ID or hostname

**--guarantee \<guarantee\>**  
Guarantee, in bytes

**--swap \<swap\>**  
Swap size, in bytes, or -1 if unlimited

**--cache-ratio \<cache-ratio\>**  
Cache ratio from 0 to 1 inclusive

**--cache-minimum \<cache-minimum\>**  
Min. cache, in bytes

**--cache-maximum \<cache-maximum\>**  
Max. cache, in bytes

---

## vinfra memory-policy vstorage-services per-node reset

Reset per-node memory parameters to defaults.

```
usage: vinfra memory-policy vstorage-services per-node reset --node <node> [--guarantee]
                                                             [--swap] [--cache]
```

### Optional arguments:

**--node \<node\>**  
Node ID or hostname

**--guarantee**  
Reset the guarantee size

**--swap**  
Reset the swap size

**--cache**  
Reset the cache size

---

## vinfra memory-policy vstorage-services per-node show

Show per-node memory parameters.

```
usage: vinfra memory-policy vstorage-services per-node show --node <node>
```

### Optional arguments:

**--node \<node\>**  
Node ID or hostname

---

## vinfra node certificate ipsec renew

Generate new IPsec certificate for node.

```
usage: vinfra node certificate ipsec renew [--wait] [--timeout <seconds>]
                                           <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node disk assign

Add multiple disks to the storage cluster.

```
usage: vinfra node disk assign [--wait] [--timeout <seconds>]
                               --disk <disk>:<role>[:<key1=value1,key2=value2...>]
                               [--node <node>]
```

### Optional arguments:

**--disk \<disk\>:\<role\>[:\<key1=value1,key2=value2...\>]**  
Disk configuration in the format:  
**disk**: disk device ID or name;  
**role**: disk role ('cs', 'mds', 'journal', 'mds-journal', 'mds-system', 'cs-system', 'system');  
Comma-separated key=value pairs with keys (optional):  
**tier**: disk tier (0, 1, 2 or 3);  
**journal-tier**: journal (cache) disk tier (0, 1, 2 or 3);  
**journal-type**: journal (cache) disk type ('no_cache', 'inner_cache' or 'external_cache');  
**journal-disk**: journal (cache) disk ID or device name;  
**bind-address**: bind IP address for the metadata service;  
e.g., `sda:cs:tier=0,journal-type=inner_cache` (this option can be used multiple times).

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node disk blink off

Stop blinking the specified disk bay.

```
usage: vinfra node disk blink off [--node <node>] <disk>
```

### Positional arguments:

**\<disk\>**  
Disk ID or device name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

---

## vinfra node disk blink on

Start blinking the specified disk bay to identify disk for maintenance purposes.

```
usage: vinfra node disk blink on [--node <node>] <disk>
```

### Positional arguments:

**\<disk\>**  
Disk ID or device name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

---

## vinfra node disk list

List node disks.

```
usage: vinfra node disk list [--long] [-a | --node <node>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**-a, --all**  
List disks on all nodes.

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

---

## vinfra node disk release

Release disk(s) from the storage cluster. Start data migration from the node as well as cluster replication and rebalancing to meet the configured redundancy level.

```
usage: vinfra node disk release [--wait] [--timeout <seconds>] [--force]
                                [--node <node>] [--disk <disk>]
                                [<disk>]
```

### Positional arguments:

**\<disk\>**  
Disk ID or device name (DEPRECATED)

### Optional arguments:

**--force**  
Release without data migration.

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

**--disk \<disk\>**  
Disk ID or device name (this option can be used multiple times)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node disk show

Show details of a disk.

```
usage: vinfra node disk show [--node <node>] <disk>
```

### Positional arguments:

**\<disk\>**  Disk ID or device name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

---

## vinfra node disk show diagnostic-info

Show diagnostic information of a disk.

```
usage: vinfra node disk show diagnostic-info [--long] [--node <node>]
                                             <disk>
```

### Positional arguments:

**\<disk\>**  
Disk ID or device name

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

---

## vinfra node forget

Remove a node from the storage cluster.

```
usage: vinfra node forget [--wait] [--timeout <seconds>]
                          <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iface create-bond

Create a network bonding.

```
usage: vinfra node iface create-bond [--wait] [--timeout <seconds>]
                                     [--ipv4 <ipv4>] [--ipv6 <ipv6>]
                                     [--gw4 <gw4>] [--gw6 <gw6>] [--mtu <mtu>]
                                     [--dhcp4 | --no-dhcp4]
                                     [--dhcp6 | --no-dhcp6]
                                     [--auto-routes-v4 | --ignore-auto-routes-v4]
                                     [--auto-routes-v6 | --ignore-auto-routes-v6]
                                     [--network <network>]
                                     [--bonding-opts <bonding_opts>]
                                     [--node <node>] --bond-type <bond-type>
                                     --ifaces <ifaces>
```

### Optional arguments:

**--ipv4 \<ipv4\>**  
A comma-separated list of IPv4 addresses

**--ipv6 \<ipv6\>**  
A comma-separated list of IPv6 addresses

**--gw4 \<gw4\>**  
Gateway IPv4 address

**--gw6 \<gw6\>**  
Gateway IPv6 address

**--mtu \<mtu\>**  
MTU interface value

**--dhcp4**  
Enable DHCPv4

**--no-dhcp4**  
Disable DHCPv4

**--dhcp6**  
Enable DHCPv6

**--no-dhcp6**  
Disable DHCPv6

**--auto-routes-v4**  
Enable automatic IPv4 routes

**--ignore-auto-routes-v4**  
Ignore automatic IPv4 routes

**--auto-routes-v6**  
Enable automatic IPv6 routes

**--ignore-auto-routes-v6**  
Ignore automatic IPv6 routes

**--network \<network\>**  
Network ID or name

**--bonding-opts \<bonding_opts\>**  
Additional bonding options

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

**--bond-type \<bond-type\>**  
Bond type ('balance-rr', 'balance-xor', 'broadcast', '802.3ad', 'balance-tlb', 'balance-alb');  
OVS Bond type for OVS interface ('balance-tcp', 'active-backup').

**--ifaces \<ifaces\>**  
A comma-separated list of network interface names, e.g., `iface1,iface2,...,ifaceN`

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iface create-vlan

Create a VLAN.

```
usage: vinfra node iface create-vlan [--wait] [--timeout <seconds>]
                                     [--ipv4 <ipv4>] [--ipv6 <ipv6>]
                                     [--gw4 <gw4>] [--gw6 <gw6>] [--mtu <mtu>]
                                     [--dhcp4 | --no-dhcp4]
                                     [--dhcp6 | --no-dhcp6]
                                     [--auto-routes-v4 | --ignore-auto-routes-v4]
                                     [--auto-routes-v6 | --ignore-auto-routes-v6]
                                     [--network <network>] [--node <node>]
                                     --iface <iface> --tag <tag>
```

### Optional arguments:

**--ipv4 \<ipv4\>**  
A comma-separated list of IPv4 addresses

**--ipv6 \<ipv6\>**  
A comma-separated list of IPv6 addresses

**--gw4 \<gw4\>**  
Gateway IPv4 address

**--gw6 \<gw6\>**  
Gateway IPv6 address

**--mtu \<mtu\>**  
MTU interface value

**--dhcp4**  
Enable DHCPv4

**--no-dhcp4**  
Disable DHCPv4

**--dhcp6**  
Enable DHCPv6

**--no-dhcp6**  
Disable DHCPv6

**--auto-routes-v4**  
Enable automatic IPv4 routes

**--ignore-auto-routes-v4**  
Ignore automatic IPv4 routes

**--auto-routes-v6**  
Enable automatic IPv6 routes

**--ignore-auto-routes-v6**  
Ignore automatic IPv6 routes

**--network \<network\>**  
Network ID or name

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

**--iface \<iface\>**  
Interface name

**--tag \<tag\>**  
VLAN tag number

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iface delete

Delete a network interface.

```
usage: vinfra node iface delete [--wait] [--timeout <seconds>]
                                [--node <node>] <iface>
```

### Positional arguments:

**\<iface\>**  
Network interface name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iface down

Bring down a network interface.

```
usage: vinfra node iface down [--wait] [--timeout <seconds>]
                              [--node <node>] <iface>
```

### Positional arguments:

**\<iface\>**  
Network interface name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iface list

List node network interfaces.

```
usage: vinfra node iface list [--long] [-a | --node <node>]
```

optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**-a, --all**  
List all network interfaces on all nodes.

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

---

## vinfra node iface set

Modify network interface parameters (overwrites omitted options to interace default values).

```
usage: vinfra node iface set [--wait] [--timeout <seconds>] [--ipv4 <ipv4>]
                             [--ipv6 <ipv6>] [--gw4 <gw4>] [--gw6 <gw6>]
                             [--mtu <mtu>] [--dhcp4 | --no-dhcp4]
                             [--dhcp6 | --no-dhcp6]
                             [--auto-routes-v4 | --ignore-auto-routes-v4]
                             [--auto-routes-v6 | --ignore-auto-routes-v6]
                             [--network <network> | --no-network]
                             [--connected-mode | --datagram-mode]
                             [--ifaces <ifaces>] [--bond-type <bond-type>]
                             [--node <node>] <iface>
```

### Positional arguments:

**\<iface\>**  
Network interface name

### Optional arguments:

**--ipv4 \<ipv4\>**  
A comma-separated list of IPv4 addresses

**--ipv6 \<ipv6\>**  
A comma-separated list of IPv6 addresses

**--gw4 \<gw4\>**  
Gateway IPv4 address

**--gw6 \<gw6\>**  
Gateway IPv6 address

**--mtu \<mtu\>**  
MTU interface value

**--dhcp4**  
Enable DHCPv4

**--no-dhcp4**  
Disable DHCPv4

**--dhcp6**  
Enable DHCPv6

**--no-dhcp6**  
Disable DHCPv6

**--auto-routes-v4**  
Enable automatic IPv4 routes

**--ignore-auto-routes-v4**  
Ignore automatic IPv4 routes

**--auto-routes-v6**  
Enable automatic IPv6 routes

**--ignore-auto-routes-v6**  
Ignore automatic IPv6 routes

**--network \<network\>**  
Network ID or name

**--no-network**  
Remove a network from the interface

**--connected-mode**  
Enable connected mode (InfiniBand interfaces only).

**--datagram-mode**  
Enable datagram mode (InfiniBand interfaces only).

**--ifaces \<ifaces\>**  
A comma-separated list of network interface names, e.g., `iface1,iface2,...,ifaceN`

**--bond-type \<bond-type\>**  
Bond type ('balance-rr', 'balance-xor', 'broadcast', '802.3ad', 'balance-tlb', 'balance-alb');  
Bond type for OVS interface ('balance-tcp', 'active-backup').

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iface show

Show details of a network interface.

```
usage: vinfra node iface show [--node <node>] <iface>
```

### Positional arguments:

**\<iface\>**  
Network interface name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

---

## vinfra node iface up

Bring up a network interface.

```
usage: vinfra node iface up [--wait] [--timeout <seconds>]
                            [--node <node>] <iface>
```

### Positional arguments:

**\<iface\>**  
Network interface name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname (default: `backend-api.svc.vstoragedomain`)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iscsi target add

Add an iSCSI target as a disk to a node.

```
usage: vinfra node iscsi target add [--wait] [--timeout <seconds>]
                                    [--auth-username <auth-username>]
                                    [--auth-password <auth-password>]
                                     --portal portal> --node <node>
                                    <target-name>
```

### Positional arguments:

**\<target-name\>**  
Target name

### Optional arguments:

**--auth-username \<auth-username\>**  
User name

**--auth-password \<auth-password\>**  
User password

**--portal \<portal\>**  
Portal IP address in the format `<IP address>:<port>` (this option can be specified multiple times).

**--node \<node\>**  Node ID or hostname

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node iscsi target delete

Delete an iSCSI target from a node.

```
usage: vinfra node iscsi target delete [--wait] [--timeout <seconds>]
                                       --node <node> <target-name>
```

### Positional arguments:

**\<target-name\>**  
Target name

### Optional arguments:

**--node \<node\>**  
Node ID or hostname

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node join

Join a node to the storage cluster

```
usage: vinfra node join [--wait] [--timeout <seconds>]
                        [--disk <disk>:<role>[:<key1=value1,key2=value2...>]]
                        <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Optional arguments:

**--disk \<disk\>:\<role\>[:\<key1=value1,key2=value2...\>]**  
Disk configuration in the format:  
**disk**: disk device ID or name;  
**role**: disk role ('cs', 'mds', 'journal', 'mds-journal', 'mds-system', 'cs-system', 'system');  
Comma-separated key=value pairs with keys (optional):  
**tier**: disk tier (0, 1, 2 or 3);  
**journal-tier**: journal (cache) disk tier (0, 1, 2 or 3);  
**journal-type**: journal (cache) disk type ('no_cache', 'inner_cache' or 'external_cache');  
**journal-disk**: journal (cache) disk ID or device name;  
**bind-address**: bind IP address for the metadata service;  
e.g., `sda:cs:tier=0,journal-type=inner_cache` (this option can be used multiple times).

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node list

List storage nodes.

```
usage: vinfra node list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra node maintenance precheck

Start node maintenance precheck.

```
usage: vinfra node maintenance precheck [--wait] [--timeout <seconds>]
                                        <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node maintenance start

Start node maintenance.

```
usage: vinfra node maintenance start [--wait] [--timeout <seconds>]
                                     [--iscsi-mode <mode>]
                                     [--compute-mode <mode>]
                                     [--s3-mode <mode>]
                                     [--storage-mode <mode>]
                                     [--alua-mode <mode>] [--nfs-mode <mode>]
                                     <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Optional arguments:

**--iscsi-mode \<mode\>**  
Ignore ISCSI evacuation during maintenance

**--compute-mode \<mode\>**  
Ignore compute evacuation during maintenance

**--s3-mode \<mode\>**  
Ignore S3 evacuation during maintenance

**--storage-mode \<mode\>**  
Ignore storage evacuation during maintenance

**--alua-mode \<mode\>**  
Ignore Block Storage target groups during maintenance

**--nfs-mode \<mode\>**  
Ignore NFS evacuation during maintenance

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node maintenance status

Show node maintenance details.

```
usage: vinfra node maintenance status <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

---

## vinfra node maintenance stop

Return node to operation.

```
usage: vinfra node maintenance stop [--wait] [--timeout <seconds>]
                                    [--ignore-compute] <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Optional arguments:

**--ignore-compute**  
Ignore compute resources while returning a node to operation

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node ram-reservation list

Show nodes ram reservation details.

```
usage: vinfra node ram-reservation list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra node ram-reservation show

Show storage node ram reservation details.

```
usage: vinfra node ram-reservation show <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

---

## vinfra node ram-reservation total

Show total ram reservation details.

```
usage: vinfra node ram-reservation total
```

---

## vinfra node release

Release a node from the storage cluster. Start data migration from the node as well as cluster replication and rebalancing to meet the configured redundancy level.

```
usage: vinfra node release [--wait] [--timeout <seconds>]
                           [--force] <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Optional arguments:

**--force**  Release node without data migration.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra node show

Show storage node details.

```
usage: vinfra node show <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

---

## vinfra node token create

Create the backend token.

```
usage: vinfra node token create [--ttl <ttl>]
```

### Optional arguments:

**--ttl \<ttl\>**  
Token TTL, in seconds

---

## vinfra node token show

Display the backend token.

```
usage: vinfra node token show
```

---

## vinfra node token validate

Validate the backend token.

```
usage: vinfra node token validate <token>
```

### Positional arguments:

**\<token\>**  
Token value

---

## vinfra service backup cluster add-upstream

Add new upstream to Reverse Proxy Backup Gateway.

```
usage: vinfra service backup cluster add-upstream [--wait] [--timeout <seconds>]
                                                  --upstream-info-file UPSTREAM_INFO_FILE
```

### Optional arguments:

**--upstream-info-file UPSTREAM_INFO_FILE**  
Upstream info file path

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup cluster create

Create the backup cluster.

```
usage: vinfra service backup cluster create [--wait] [--timeout <seconds>]
                                            --nodes <nodes> [--name <name>]
                                            [--address <address>]
                                            [--location <location>]
                                            [--username <username>]
                                            [--account-server <account-server>]
                                            [--tier {0,1,2,3}]
                                            [--encoding <M>+<N>]
                                            [--failure-domain {0,1,2,3,4}]
                                            [--nfs-host <HOST>]
                                            [--nfs-export <EXPORT>]
                                            [--nfs-version <VERSION>]
                                            [--s3-flavor <FLAVOR>]
                                            [--s3-region <REGION>]
                                            [--s3-bucket <BUCKET>]
                                            [--s3-endpoint <ENDPOINT>]
                                            [--s3-access-key-id <ACCESS-KEY-ID>]
                                            [--s3-secret-key-id <SECRET-KEY-ID>]
                                            [--s3-cert-verify <CERT-VERIFY>]
                                            [--swift-auth-url <AUTH-URL>]
                                            [--swift-auth-version <AUTH-VERSION>]
                                            [--swift-user-name <USER-NAME>]
                                            [--swift-api-key <API-KEY>]
                                            [--swift-domain <DOMAIN>]
                                            [--swift-domain-id <DOMAIN-ID>]
                                            [--swift-tenant <TENANT>]
                                            [--swift-tenant-id <TENANT-ID>]
                                            [--swift-tenant-domain <TENANT-DOMAIN>]
                                            [--swift-tenant-domain-id <TENANT-DOMAIN-ID>]
                                            [--swift-trust-id <TRUST-ID>]
                                            [--swift-region <REGION>]
                                            [--swift-internal <INTERNAL>]
                                            [--swift-container <CONTAINER>]
                                            [--swift-cert-verify <CERT-VERIFY>]
                                            [--azure-endpoint <ENDPOINT>]
                                            [--azure-container <CONTAINER>]
                                            [--azure-account-name <ACCOUNT-NAME>]
                                            [--azure-account-key <ACCOUNT-KEY>]
                                            [--google-bucket <BUCKET>]
                                            [--google-credentials <CREDENTIALS>]
                                            --storage-type {local,nfs,s3,swift,azure,google}
                                            [--stdin] [--domain <domain>]
                                            [--reg-account <reg-account>]
                                            [--reg-server <reg-server>]
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

**--name \<name\>**  
Backup registration name

**--address \<address\>**  
Backup registration address

**--location \<location\>**  
Backup registration location

**--username \<username\>**  
Partner account in the cloud or of an organization administrator on the local management server

**--account-server \<account-server\>**  
URL of the cloud management portal or the hostname/IP address and port of the local management server

**--tier {0,1,2,3}**  
Storage tier

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--storage-type {local,nfs,s3,swift,azure,google}**  
Choose storage type

**--stdin**  
Use for setting registration password from stdin

**--domain \<domain\>**  
Domain name for the backup cluster (DEPRECATED)

**--reg-account \<reg-account\>**  
Partner account in the cloud or of an organization administrator on the local management server (DEPRECATED)

**--reg-server \<reg-server\>**  
URL of the cloud management portal or the hostname/IP address and port of the local management server (DEPRECATED)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

### Storage params for 'nfs' storage:

Create backup service on Network File System (NFS).

**--nfs-host \<HOST\>**  
NFS hostname or IP. Required for 'nfs' storage type.

**--nfs-export \<EXPORT\>**  
Export name. Required for 'nfs' storage type.

**--nfs-version \<VERSION\>**  
Nfs version. Required for 'nfs' storage type.

### Storage params for 's3' storage:

Create backup service on public S3 cloud.

**--s3-flavor \<FLAVOR\>**  
Flavor name

**--s3-region \<REGION\>**  
Set region for Amazon S3

**--s3-bucket \<BUCKET\>**  
Bucket name. Required for 's3' storage type.

**--s3-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 's3' storage type.

**--s3-access-key-id \<ACCESS-KEY-ID\>**  
Access Key ID. Required for 's3' storage type.

**--s3-secret-key-id \<SECRET-KEY-ID\>**  
Secret Key ID. Required for 's3' storage type.

**--s3-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of S3 endpoint

### Storage params for 'swift' storage:

Create backup service on public Swift cloud.

**--swift-auth-url \<AUTH-URL\>**  
Authentication (keystone) URL. Required for 'swift' storage type.

**--swift-auth-version \<AUTH-VERSION\>**  
Authentication protocol version

**--swift-user-name \<USER-NAME\>**  
User name. Required for 'swift' storage type.

**--swift-api-key \<API-KEY\>**  
API key (password). Required for 'swift' storage type.

**--swift-domain \<DOMAIN\>**  
Domain name

**--swift-domain-id \<DOMAIN-ID\>**  
Domain ID

**--swift-tenant \<TENANT\>**  
Tenant name

**--swift-tenant-id \<TENANT-ID\>**  
Tenant ID

**--swift-tenant-domain \<TENANT-DOMAIN\>**  
Tenant domain name

**--swift-tenant-domain-id \<TENANT-DOMAIN-ID\>**  
Tenant domain ID

**--swift-trust-id \<TRUST-ID\>**  
Trust ID

**--swift-region \<REGION\>**  
Region name

**--swift-internal \<INTERNAL\>**
Internal parameter

**--swift-container \<CONTAINER\>**  
Container name

**--swift-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of Swift endpoint

### Storage params for 'azure' storage:

Create backup service on public Azure cloud.

**--azure-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 'azure' storage type.

**--azure-container \<CONTAINER\>**  
Container. Required for 'azure' storage type.

**--azure-account-name \<ACCOUNT-NAME\>**  
Account name. Required for 'azure' storage type.

**--azure-account-key \<ACCOUNT-KEY\>**  
Account key. Required for 'azure' storage type.

### Storage params for 'google' storage:

Create backup service on public Google cloud.

**--google-bucket \<BUCKET\>**  
Google bucket name. Required for 'google' storage type.

**--google-credentials \<CREDENTIALS\>**  
Path of google credentials file. Required for 'google' storage type.

---

## vinfra service backup cluster deploy-reverse-proxy

Create Reverse Proxy Backup Gateway.

```
usage: vinfra service backup cluster deploy-reverse-proxy [--wait] [--timeout <seconds>]
                                                          --nodes <nodes>
                                                          [--tier {0,1,2,3}]
                                                          [--encoding <M>+<N>]
                                                          [--failure-domain {0,1,2,3,4}]
                                                          [--nfs-host <HOST>]
                                                          [--nfs-export <EXPORT>]
                                                          [--nfs-version <VERSION>]
                                                          [--s3-flavor <FLAVOR>]
                                                          [--s3-region <REGION>]
                                                          [--s3-bucket <BUCKET>]
                                                          [--s3-endpoint <ENDPOINT>]
                                                          [--s3-access-key-id <ACCESS-KEY-ID>]
                                                          [--s3-secret-key-id <SECRET-KEY-ID>]
                                                          [--s3-cert-verify <CERT-VERIFY>]
                                                          [--swift-auth-url <AUTH-URL>]
                                                          [--swift-auth-version <AUTH-VERSION>]
                                                          [--swift-user-name <USER-NAME>]
                                                          [--swift-api-key <API-KEY>]
                                                          [--swift-domain <DOMAIN>]
                                                          [--swift-domain-id <DOMAIN-ID>]
                                                          [--swift-tenant <TENANT>]
                                                          [--swift-tenant-id <TENANT-ID>]
                                                          [--swift-tenant-domain <TENANT-DOMAIN>]
                                                          [--swift-tenant-domain-id <TENANT-DOMAIN-ID>]
                                                          [--swift-trust-id <TRUST-ID>]
                                                          [--swift-region <REGION>]
                                                          [--swift-internal <INTERNAL>]
                                                          [--swift-container <CONTAINER>]
                                                          [--swift-cert-verify <CERT-VERIFY>]
                                                          [--azure-endpoint <ENDPOINT>]
                                                          [--azure-container <CONTAINER>]
                                                          [--azure-account-name <ACCOUNT-NAME>]
                                                          [--azure-account-key <ACCOUNT-KEY>]
                                                          [--google-bucket <BUCKET>]
                                                          [--google-credentials <CREDENTIALS>]
                                                          --storage-type {local,nfs,s3,swift,azure,google}
                                                          --upstream-info-file UPSTREAM_INFO_FILE
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

**--tier {0,1,2,3}**  
Storage tier

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--storage-type {local,nfs,s3,swift,azure,google}**  
Choose storage type

**--upstream-info-file UPSTREAM_INFO_FILE**  
Upstream info file path

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

### Storage params for 'nfs' storage:

Create backup service on Network File System (NFS).

**--nfs-host \<HOST\>**  
NFS hostname or IP. Required for 'nfs' storage type.

**--nfs-export \<EXPORT\>**  
Export name. Required for 'nfs' storage type.

**--nfs-version \<VERSION\>**  
Nfs version. Required for 'nfs' storage type.

### Storage params for 's3' storage:

Create backup service on public S3 cloud.

**--s3-flavor \<FLAVOR\>**  
Flavor name

**--s3-region \<REGION\>**  
Set region for Amazon S3

**--s3-bucket \<BUCKET\>**  
Bucket name. Required for 's3' storage type.

**--s3-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 's3' storage type.

**--s3-access-key-id \<ACCESS-KEY-ID\>**  
Access Key ID. Required for 's3' storage type.

**--s3-secret-key-id \<SECRET-KEY-ID\>**  
Secret Key ID. Required for 's3' storage type.

**--s3-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of S3 endpoint

### Storage params for 'swift' storage:

Create backup service on public Swift cloud.

**--swift-auth-url \<AUTH-URL\>**  
Authentication (keystone) URL. Required for 'swift' storage type.

**--swift-auth-version \<AUTH-VERSION\>**  
Authentication protocol version

**--swift-user-name \<USER-NAME\>**  
User name. Required for 'swift' storage type.

**--swift-api-key \<API-KEY\>**  
API key (password). Required for 'swift' storage type.

**--swift-domain \<DOMAIN\>**  
Domain name

**--swift-domain-id \<DOMAIN-ID\>**  
Domain ID

**--swift-tenant \<TENANT\>**  
Tenant name

**--swift-tenant-id \<TENANT-ID\>**  
Tenant ID

**--swift-tenant-domain \<TENANT-DOMAIN\>**  
Tenant domain name

**--swift-tenant-domain-id \<TENANT-DOMAIN-ID\>**  
Tenant domain ID

**--swift-trust-id \<TRUST-ID\>**  
Trust ID

**--swift-region \<REGION\>**  
Region name

**--swift-internal \<INTERNAL\>**
Internal parameter

**--swift-container \<CONTAINER\>**  
Container name

**--swift-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of Swift endpoint

### Storage params for 'azure' storage:

Create backup service on public Azure cloud.

**--azure-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 'azure' storage type.

**--azure-container \<CONTAINER\>**  
Container. Required for 'azure' storage type.

**--azure-account-name \<ACCOUNT-NAME\>**  
Account name. Required for 'azure' storage type.

**--azure-account-key \<ACCOUNT-KEY\>**  
Account key. Required for 'azure' storage type.

### Storage params for 'google' storage:

Create backup service on public Google cloud.

**--google-bucket \<BUCKET\>**  
Google bucket name. Required for 'google' storage type.

**--google-credentials \<CREDENTIALS\>**  
Path of google credentials file. Required for 'google' storage type.

---

## vinfra service backup cluster deploy-standalone

Create the backup cluster.

```
usage: vinfra service backup cluster deploy-standalone [--wait] [--timeout <seconds>]
                                                       --nodes <nodes>
                                                       [--name <name>]
                                                       [--address <address>]
                                                       [--location <location>]
                                                       [--username <username>]
                                                       [--account-server <account-server>]
                                                       [--tier {0,1,2,3}]
                                                       [--encoding <M>+<N>]
                                                       [--failure-domain {0,1,2,3,4}]
                                                       [--nfs-host <HOST>]
                                                       [--nfs-export <EXPORT>]
                                                       [--nfs-version <VERSION>]
                                                       [--s3-flavor <FLAVOR>]
                                                       [--s3-region <REGION>]
                                                       [--s3-bucket <BUCKET>]
                                                       [--s3-endpoint <ENDPOINT>]
                                                       [--s3-access-key-id <ACCESS-KEY-ID>]
                                                       [--s3-secret-key-id <SECRET-KEY-ID>]
                                                       [--s3-cert-verify <CERT-VERIFY>]
                                                       [--swift-auth-url <AUTH-URL>]
                                                       [--swift-auth-version <AUTH-VERSION>]
                                                       [--swift-user-name <USER-NAME>]
                                                       [--swift-api-key <API-KEY>]
                                                       [--swift-domain <DOMAIN>]
                                                       [--swift-domain-id <DOMAIN-ID>]
                                                       [--swift-tenant <TENANT>]
                                                       [--swift-tenant-id <TENANT-ID>]
                                                       [--swift-tenant-domain <TENANT-DOMAIN>]
                                                       [--swift-tenant-domain-id <TENANT-DOMAIN-ID>]
                                                       [--swift-trust-id <TRUST-ID>]
                                                       [--swift-region <REGION>]
                                                       [--swift-internal <INTERNAL>]
                                                       [--swift-container <CONTAINER>]
                                                       [--swift-cert-verify <CERT-VERIFY>]
                                                       [--azure-endpoint <ENDPOINT>]
                                                       [--azure-container <CONTAINER>]
                                                       [--azure-account-name <ACCOUNT-NAME>]
                                                       [--azure-account-key <ACCOUNT-KEY>]
                                                       [--google-bucket <BUCKET>]
                                                       [--google-credentials <CREDENTIALS>]
                                                       --storage-type {local,nfs,s3,swift,azure,google}
                                                       [--stdin]
                                                       [--domain <domain>]
                                                       [--reg-account <reg-account>]
                                                       [--reg-server <reg-server>]
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

**--name \<name\>**  
Backup registration name

**--address \<address\>**  
Backup registration address

**--location \<location\>**  
Backup registration location

**--username \<username\>**  
Partner account in the cloud or of an organization administrator on the local management server

**--account-server \<account-server\>**  
URL of the cloud management portal or the hostname/IP address and port of the local management server

**--tier {0,1,2,3}**  
Storage tier

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--storage-type {local,nfs,s3,swift,azure,google}**  
Choose storage type

**--stdin**  
Use for setting registration password from stdin

**--domain \<domain\>**  
Domain name for the backup cluster (DEPRECATED)

**--reg-account \<reg-account\>**  
Partner account in the cloud or of an organization administrator on the local management server (DEPRECATED)

**--reg-server \<reg-server\>**  
URL of the cloud management portal or the hostname/IP address and port of the local management server (DEPRECATED)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

### Storage params for 'nfs' storage:

Create backup service on Network File System (NFS).

**--nfs-host \<HOST\>**  
NFS hostname or IP. Required for 'nfs' storage type.

**--nfs-export \<EXPORT\>**  
Export name. Required for 'nfs' storage type.

**--nfs-version \<VERSION\>**  
Nfs version. Required for 'nfs' storage type.

### Storage params for 's3' storage:

Create backup service on public S3 cloud.

**--s3-flavor \<FLAVOR\>**  
Flavor name

**--s3-region \<REGION\>**  
Set region for Amazon S3

**--s3-bucket \<BUCKET\>**  
Bucket name. Required for 's3' storage type.

**--s3-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 's3' storage type.

**--s3-access-key-id \<ACCESS-KEY-ID\>**  
Access Key ID. Required for 's3' storage type.

**--s3-secret-key-id \<SECRET-KEY-ID\>**  
Secret Key ID. Required for 's3' storage type.

**--s3-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of S3 endpoint

### Storage params for 'swift' storage:

Create backup service on public Swift cloud.

**--swift-auth-url \<AUTH-URL\>**  
Authentication (keystone) URL. Required for 'swift' storage type.

**--swift-auth-version \<AUTH-VERSION\>**  
Authentication protocol version

**--swift-user-name \<USER-NAME\>**  
User name. Required for 'swift' storage type.

**--swift-api-key \<API-KEY\>**  
API key (password). Required for 'swift' storage type.

**--swift-domain \<DOMAIN\>**  
Domain name

**--swift-domain-id \<DOMAIN-ID\>**  
Domain ID

**--swift-tenant \<TENANT\>**  
Tenant name

**--swift-tenant-id \<TENANT-ID\>**  
Tenant ID

**--swift-tenant-domain \<TENANT-DOMAIN\>**  
Tenant domain name

**--swift-tenant-domain-id \<TENANT-DOMAIN-ID\>**  
Tenant domain ID

**--swift-trust-id \<TRUST-ID\>**  
Trust ID

**--swift-region \<REGION\>**  
Region name

**--swift-internal \<INTERNAL\>**
Internal parameter

**--swift-container \<CONTAINER\>**  
Container name

**--swift-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of Swift endpoint

### Storage params for 'azure' storage:

Create backup service on public Azure cloud.

**--azure-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 'azure' storage type.

**--azure-container \<CONTAINER\>**  
Container. Required for 'azure' storage type.

**--azure-account-name \<ACCOUNT-NAME\>**  
Account name. Required for 'azure' storage type.

**--azure-account-key \<ACCOUNT-KEY\>**  
Account key. Required for 'azure' storage type.

### Storage params for 'google' storage:

Create backup service on public Google cloud.

**--google-bucket \<BUCKET\>**  
Google bucket name. Required for 'google' storage type.

**--google-credentials \<CREDENTIALS\>**  
Path of google credentials file. Required for 'google' storage type.

---

## vinfra service backup cluster deploy-upstream

Create Upstream Backup Gateway for Reverse Proxy.

```
usage: vinfra service backup cluster deploy-upstream [--wait] [--timeout <seconds>]
                                                     --nodes <nodes>
                                                     [--tier {0,1,2,3}]
                                                     [--encoding <M>+<N>]
                                                     [--failure-domain {0,1,2,3,4}]
                                                     [--nfs-host <HOST>]
                                                     [--nfs-export <EXPORT>]
                                                     [--nfs-version <VERSION>]
                                                     [--s3-flavor <FLAVOR>]
                                                     [--s3-region <REGION>]
                                                     [--s3-bucket <BUCKET>]
                                                     [--s3-endpoint <ENDPOINT>]
                                                     [--s3-access-key-id <ACCESS-KEY-ID>]
                                                     [--s3-secret-key-id <SECRET-KEY-ID>]
                                                     [--s3-cert-verify <CERT-VERIFY>]
                                                     [--swift-auth-url <AUTH-URL>]
                                                     [--swift-auth-version <AUTH-VERSION>]
                                                     [--swift-user-name <USER-NAME>]
                                                     [--swift-api-key <API-KEY>]
                                                     [--swift-domain <DOMAIN>]
                                                     [--swift-domain-id <DOMAIN-ID>]
                                                     [--swift-tenant <TENANT>]
                                                     [--swift-tenant-id <TENANT-ID>]
                                                     [--swift-tenant-domain <TENANT-DOMAIN>]
                                                     [--swift-tenant-domain-id <TENANT-DOMAIN-ID>]
                                                     [--swift-trust-id <TRUST-ID>]
                                                     [--swift-region <REGION>]
                                                     [--swift-internal <INTERNAL>]
                                                     [--swift-container <CONTAINER>]
                                                     [--swift-cert-verify <CERT-VERIFY>]
                                                     [--azure-endpoint <ENDPOINT>]
                                                     [--azure-container <CONTAINER>]
                                                     [--azure-account-name <ACCOUNT-NAME>]
                                                     [--azure-account-key <ACCOUNT-KEY>]
                                                     [--google-bucket <BUCKET>]
                                                     [--google-credentials <CREDENTIALS>]
                                                     --storage-type {local,nfs,s3,swift,azure,google}
                                                     --address <address>
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

**--tier {0,1,2,3}**  
Storage tier

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--storage-type {local,nfs,s3,swift,azure,google}**  
Choose storage type

**--address \<address\>**  
Address of Upstream Backup Gateway

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

### Storage params for 'nfs' storage:

Create backup service on Network File System (NFS).

**--nfs-host \<HOST\>**  
NFS hostname or IP. Required for 'nfs' storage type.

**--nfs-export \<EXPORT\>**  
Export name. Required for 'nfs' storage type.

**--nfs-version \<VERSION\>**  
Nfs version. Required for 'nfs' storage type.

### Storage params for 's3' storage:

Create backup service on public S3 cloud.

**--s3-flavor \<FLAVOR\>**  
Flavor name

**--s3-region \<REGION\>**  
Set region for Amazon S3

**--s3-bucket \<BUCKET\>**  
Bucket name. Required for 's3' storage type.

**--s3-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 's3' storage type.

**--s3-access-key-id \<ACCESS-KEY-ID\>**  
Access Key ID. Required for 's3' storage type.

**--s3-secret-key-id \<SECRET-KEY-ID\>**  
Secret Key ID. Required for 's3' storage type.

**--s3-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of S3 endpoint

### Storage params for 'swift' storage:

Create backup service on public Swift cloud.

**--swift-auth-url \<AUTH-URL\>**  
Authentication (keystone) URL. Required for 'swift' storage type.

**--swift-auth-version \<AUTH-VERSION\>**  
Authentication protocol version

**--swift-user-name \<USER-NAME\>**  
User name. Required for 'swift' storage type.

**--swift-api-key \<API-KEY\>**  
API key (password). Required for 'swift' storage type.

**--swift-domain \<DOMAIN\>**  
Domain name

**--swift-domain-id \<DOMAIN-ID\>**  
Domain ID

**--swift-tenant \<TENANT\>**  
Tenant name

**--swift-tenant-id \<TENANT-ID\>**  
Tenant ID

**--swift-tenant-domain \<TENANT-DOMAIN\>**  
Tenant domain name

**--swift-tenant-domain-id \<TENANT-DOMAIN-ID\>**  
Tenant domain ID

**--swift-trust-id \<TRUST-ID\>**  
Trust ID

**--swift-region \<REGION\>**  
Region name

**--swift-internal \<INTERNAL\>**
Internal parameter

**--swift-container \<CONTAINER\>**  
Container name

**--swift-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of Swift endpoint

### Storage params for 'azure' storage:

Create backup service on public Azure cloud.

**--azure-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 'azure' storage type.

**--azure-container \<CONTAINER\>**  
Container. Required for 'azure' storage type.

**--azure-account-name \<ACCOUNT-NAME\>**  
Account name. Required for 'azure' storage type.

**--azure-account-key \<ACCOUNT-KEY\>**  
Account key. Required for 'azure' storage type.

### Storage params for 'google' storage:

Create backup service on public Google cloud.

**--google-bucket \<BUCKET\>**  
Google bucket name. Required for 'google' storage type.

**--google-credentials \<CREDENTIALS\>**  
Path of google credentials file. Required for 'google' storage type.

---

## vinfra service backup cluster download-upstream-info

Download Upstream Backup Gateway info.

```
usage: vinfra service backup cluster download-upstream-info [--output-file <output-filepath>]
```

### Optional arguments:

**--output-file \<output-filepath\>**  
Path where the configuration file will be downloaded

---

## vinfra service backup cluster process

Backup Gateway process inspection/manipulation.

```
usage: vinfra service backup cluster process [--show | --retry]
                                             [--process-id PROCESS_ID]
```

### Optional arguments:

**--show**  
Show state of the Backup Gateway process.

**--retry**  
Retry a suspended Backup Gateway process.

**--process-id PROCESS_ID**  
Backup Gateway process ID

---

## vinfra service backup cluster release

Delete the backup cluster.

```
usage: vinfra service backup cluster release [--wait] [--timeout <seconds>]
                                             [--reg-account REG_ACCOUNT]
                                             [--force] [--stdin]
```

### Optional arguments:

**--reg-account REG_ACCOUNT**  
Partner account in the cloud or of an organization administrator on the local management server

**--force**  
Forcibly release the backup cluster

**--stdin**  
Use for setting registration password from stdin

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup cluster show

Display backup cluster details.

```
usage: vinfra service backup cluster show
```

---

## vinfra service backup cluster turn-to-upstream

Turn the existing Standalone Backup Gateway to Upstream.

```
usage: vinfra service backup cluster turn-to-upstream [--wait] [--timeout <seconds>]
                                                      --address <address>
```

### Optional arguments:

**--address \<address\>**  
Address of Upstream Backup Gateway

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication primary cancel

Cancel geo-replication for the primary cluster.

```
usage: vinfra service backup geo-replication primary cancel [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication primary disable

Disable geo-replication on the primary cluster.

```
usage: vinfra service backup geo-replication primary disable [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication primary download-configs

Download the geo-replication configuration file of the primary cluster.

```
usage: vinfra service backup geo-replication primary download-configs [--conf-file-path <conf-file-path>]
```

### Optional arguments:

**--conf-file-path \<conf-file-path\>**  
Path where the configuration file will be downloaded

---

## vinfra service backup geo-replication primary establish

Establish a connection between the primary and secondary clusters to enable geo-replication.

```
usage: vinfra service backup geo-replication primary establish [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication primary setup

Configure geo-replication for the primary cluster.

```
usage: vinfra service backup geo-replication primary setup [--wait] [--timeout <seconds>]
                                                           --primary-cluster-address PRIMARY_CLUSTER_ADDRESS
                                                           --secondary-cluster-address SECONDARY_CLUSTER_ADDRESS
                                                           --secondary-cluster-uid SECONDARY_CLUSTER_UID
                                                           --account-server ACCOUNT_SERVER
                                                           --username USERNAME [--stdin]
```

### Optional arguments:

**--primary-cluster-address PRIMARY_CLUSTER_ADDRESS**  
Primary cluster address

**--secondary-cluster-address SECONDARY_CLUSTER_ADDRESS**  
Secondary cluster address

**--secondary-cluster-uid SECONDARY_CLUSTER_UID**  
Secondary cluster UID

**--account-server ACCOUNT_SERVER**  
URL of the cloud management portal or the hostname/IP address and port of the local management server

**--username USERNAME**  
Partner account in the cloud or of an organization administrator on the local management server

**--stdin**  
Use for setting registration password from stdin

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication secondary cancel

Cancel geo-replication for the secondary cluster.

```
usage: vinfra service backup geo-replication secondary cancel [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication secondary promote-to-primary

Promote the secondary cluster to primary in the geo-replication configuration.

```
usage: vinfra service backup geo-replication secondary promote-to-primary [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication secondary setup

Configure geo-replication for the secondary cluster.

```
usage: vinfra service backup geo-replication secondary setup [--wait] [--timeout <seconds>]
                                                             --dc-config-file DC_CONFIG_FILE
```

### Optional arguments:

**--dc-config-file DC_CONFIG_FILE**  
Path to the configuration file of the primary cluster

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup geo-replication show

Display geo-replication configuration.

```
usage: vinfra service backup geo-replication show
```

---

## vinfra service backup node add

Add list of nodes to backup cluster.

```
usage: vinfra service backup node add [--wait] [--timeout <seconds>]
                                      --nodes <nodes>
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup node list

List backup nodes.

```
usage: vinfra service backup node list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service backup node release

Release list of nodes from backup cluster.

```
usage: vinfra service backup node release [--wait] [--timeout <seconds>]
                                          --nodes <nodes>
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup registration add

Create a backup storage registration.

```
usage: vinfra service backup registration add [--wait] [--timeout <seconds>]
                                              --name <name> --address <address>
                                              --account-server <account_server>
                                              --username <username> [--stdin]
                                              [--location <location>]
```

### Optional arguments:

**--name \<name\>**  
Registration name

**--address \<address\>**  
Registration IP address

**--account-server \<account_server\>**  
URL of the cloud management portal or the hostname/IP address and port of the local management server

**--username \<username\>**  
Partner account in the cloud or of an organization administrator on the local management server

**--stdin**  
Use for setting registration password from stdin

**--location \<location\>**  
Registration location

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup registration add-true-image

Create a true image registration for the backup storage.

```
usage: vinfra service backup registration add-true-image [--wait] [--timeout <seconds>]
                                                         --name <name>
                                                         --address <address>
                                                         --revocation-url <revocation_url>
                                                         --certificates <archived_cert_chain>
```

### Optional arguments:

**--name \<name\>**  
Registration name

**--address \<address\>**  
Registration IP address

**--revocation-url \<revocation_url\>**  
URL of the cloud management portal or the hostname/IP address and port of the local management server

**--certificates \<archived_cert_chain\>**  
Path to the upstream certificate file for Acronis Cyber Protect Home Office

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup registration delete

Delete a backup storage registration.

```
usage: vinfra service backup registration delete [--wait] [--timeout <seconds>]
                                                 [--username <username>]
                                                 [--stdin] [--force]
                                                 <registration>
```

### Positional arguments:

**\<registration\>**  
Registration ID or name

### Optional arguments:

**--username \<username\>**  
Partner account in the cloud or of an organization administrator on the local management server

**--stdin**  
Use for setting registration password from stdin

**--force**  
Forcibly delete the registration

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup registration list

List backup storage registrations.

```
usage: vinfra service backup registration list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service backup registration renew-certificates

Update certificates for a backup storage registration. Please note that ABGW service will be restarted as a part of certificates update procedure.

```
usage: vinfra service backup registration renew-certificates [--wait] [--timeout <seconds>]
                                                             --username <username> [--stdin]
                                                             <registration>
```

### Positional arguments:

**\<registration\>**  
Registration ID or name

### Optional arguments:

**--username \<username\>**  
Partner account in the cloud or of an organization administrator on the local management server

**--stdin**  
Use for setting registration password from stdin

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup registration renew-true-image-certs

Update certificates for a true image registration.

```
usage: vinfra service backup registration renew-true-image-certs [--wait] [--timeout <seconds>]
                                                                 --certs <archived_cert_chain>
                                                                 <registration>
```

### Positional arguments:

**\<registration\>**  
Registration ID or name

### Optional arguments:

**-certs \<archived_cert_chain\>**  
Path to the upstream info file

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup registration show

Display backup storage registration details.

```
usage: vinfra service backup registration show <registration>
```

### Positional arguments:

**\<registration\>**  
Registration ID or name

---

## vinfra service backup registration update

Update a backup storage registration.

```
usage: vinfra service backup registration update [--wait] [--timeout <seconds>]
                                                 [--name <name>] [--address <address>]
                                                 [--username <username>] [--stdin]
                                                 <registration>
```

### Positional arguments:

**\<registration\>**  
Registration ID or name

### Optional arguments:

**--name \<name\>**  
A new name for the registration

**--address \<address\>**  
Registration IP address

**--username \<username\>**  
Partner account in the cloud or of an organization administrator on the local management server

**--stdin**  
Use for setting registration password from stdin

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup storage-params change

Modify storage parameters.

```
usage: vinfra service backup storage-params change [--nfs-host <HOST>]
                                                   [--nfs-export <EXPORT>]
                                                   [--nfs-version <VERSION>]
                                                   [--s3-flavor <FLAVOR>]
                                                   [--s3-region <REGION>]
                                                   [--s3-bucket <BUCKET>]
                                                   [--s3-endpoint <ENDPOINT>]
                                                   [--s3-access-key-id <ACCESS-KEY-ID>]
                                                   [--s3-secret-key-id <SECRET-KEY-ID>]
                                                   [--s3-cert-verify <CERT-VERIFY>]
                                                   [--swift-auth-url <AUTH-URL>]
                                                   [--swift-auth-version <AUTH-VERSION>]
                                                   [--swift-user-name <USER-NAME>]
                                                   [--swift-api-key <API-KEY>]
                                                   [--swift-domain <DOMAIN>]
                                                   [--swift-domain-id <DOMAIN-ID>]
                                                   [--swift-tenant <TENANT>]
                                                   [--swift-tenant-id <TENANT-ID>]
                                                   [--swift-tenant-domain <TENANT-DOMAIN>]
                                                   [--swift-tenant-domain-id <TENANT-DOMAIN-ID>]
                                                   [--swift-trust-id <TRUST-ID>]
                                                   [--swift-region <REGION>]
                                                   [--swift-internal <INTERNAL>]
                                                   [--swift-container <CONTAINER>]
                                                   [--swift-cert-verify <CERT-VERIFY>]
                                                   [--azure-endpoint <ENDPOINT>]
                                                   [--azure-container <CONTAINER>]
                                                   [--azure-account-name <ACCOUNT-NAME>]
                                                   [--azure-account-key <ACCOUNT-KEY>]
                                                   [--google-bucket <BUCKET>]
                                                   [--google-credentials <CREDENTIALS>]
                                                   --storage-type {local,nfs,s3,swift,azure,google}
```

### Optional arguments:

**--storage-type {local,nfs,s3,swift,azure,google}**  
Choose storage type

### Storage params for 'nfs' storage:

Create backup service on Network File System (NFS).

**--nfs-host \<HOST\>**  
NFS hostname or IP. Required for 'nfs' storage type.

**--nfs-export \<EXPORT\>**  
Export name. Required for 'nfs' storage type.

**--nfs-version \<VERSION\>**  
Nfs version. Required for 'nfs' storage type.

### Storage params for 's3' storage:

Create backup service on public S3 cloud.

**--s3-flavor \<FLAVOR\>**  
Flavor name

**--s3-region \<REGION\>**  
Set region for Amazon S3

**--s3-bucket \<BUCKET\>**  
Bucket name. Required for 's3' storage type.

**--s3-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 's3' storage type.

**--s3-access-key-id \<ACCESS-KEY-ID\>**  
Access Key ID. Required for 's3' storage type.

**--s3-secret-key-id \<SECRET-KEY-ID\>**  
Secret Key ID. Required for 's3' storage type.

**--s3-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of S3 endpoint

### Storage params for 'swift' storage:

Create backup service on public Swift cloud.

**--swift-auth-url \<AUTH-URL\>**  
Authentication (keystone) URL. Required for 'swift' storage type.

**--swift-auth-version \<AUTH-VERSION\>**  
Authentication protocol version

**--swift-user-name \<USER-NAME\>**  
User name. Required for 'swift' storage type.

**--swift-api-key \<API-KEY\>**  
API key (password). Required for 'swift' storage type.

**--swift-domain \<DOMAIN\>**  
Domain name

**--swift-domain-id \<DOMAIN-ID\>**  
Domain ID

**--swift-tenant \<TENANT\>**  
Tenant name

**--swift-tenant-id \<TENANT-ID\>**  
Tenant ID

**--swift-tenant-domain \<TENANT-DOMAIN\>**  
Tenant domain name

**--swift-tenant-domain-id \<TENANT-DOMAIN-ID\>**  
Tenant domain ID

**--swift-trust-id \<TRUST-ID\>**  
Trust ID

**--swift-region \<REGION\>**  
Region name

**--swift-internal \<INTERNAL\>**
Internal parameter

**--swift-container \<CONTAINER\>**  
Container name

**--swift-cert-verify \<CERT-VERIFY\>**  
Allow self-signed certificate of Swift endpoint

### Storage params for 'azure' storage:

Create backup service on public Azure cloud.

**--azure-endpoint \<ENDPOINT\>**  
Endpoint URL. Required for 'azure' storage type.

**--azure-container \<CONTAINER\>**  
Container. Required for 'azure' storage type.

**--azure-account-name \<ACCOUNT-NAME\>**  
Account name. Required for 'azure' storage type.

**--azure-account-key \<ACCOUNT-KEY\>**  
Account key. Required for 'azure' storage type.

### Storage params for 'google' storage:

Create backup service on public Google cloud.

**--google-bucket \<BUCKET\>**  
Google bucket name. Required for 'google' storage type.

**--google-credentials \<CREDENTIALS\>**  
Path of google credentials file. Required for 'google' storage type.

---

## vinfra service backup storage-params show

Display storage parameters.

```
usage: vinfra service backup storage-params show
```

---

## vinfra service backup volume-params change

Modify volume parameters.

```
usage: vinfra service backup volume-params change [--wait] [--timeout <seconds>]
                                                  [--tier {0,1,2,3}]
                                                  [--encoding <M>+<N>]
                                                  [--failure-domain {0,1,2,3,4}]
```

### Optional arguments:

**--tier {0,1,2,3}**  
Storage tier

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service backup volume-params show

Display volume parameters.

```
usage: vinfra service backup volume-params show
```

---

## vinfra service block-storage target-group acl add

Add a target group ACL rule.

```
usage: vinfra service block-storage target-group acl add [--wait] [--timeout <seconds>]
                                                         [--alias <alias>]
                                                         [--lun <lun>]
                                                         <target-group> <wwn>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<wwn\>**  
WWN

### Optional arguments:

**--alias \<alias\>**  
Initiator name

**--lun \<lun\>**  
LUN ID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group acl delete

Remove a target group ACL rule.

```
usage: vinfra service block-storage target-group acl delete [--wait] [--timeout <seconds>]
                                                            <target-group> <wwn>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<wwn\>**  
WWN

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group acl list

List target group ACL rules.

```
usage: vinfra service block-storage target-group acl list [--long] <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service block-storage target-group acl set

Set target group ACL parameters.

```
usage: vinfra service block-storage target-group acl set [--wait] [--timeout <seconds>]
                                                         (--lun <lun> | --no-luns)
                                                         <target-group> <wwn>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<wwn\>**  
WWN

### Optional arguments:

**--lun \<lun\>**  
LUN ID

**--no-luns**  
No LUNs

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group create

Create a target group.

```
usage: vinfra service block-storage target-group create [--wait] [--timeout <seconds>]
                                                        --type <type> --target <name:node:ip1,ip2...>
                                                        <name>
```

### Positional arguments:

**\<name\>**  
Target group name

### Optional arguments:

**--type \<type\>**  
Type of targets in new target group

**--target \<name:node:ip1,ip2...\>**  
Target name, node and IP addresses

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group delete

Remove a target group.

```
usage: vinfra service block-storage target-group delete [--wait] [--timeout <seconds>]
                                                        [--force] <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

### Optional arguments:

**--force**  
Forcibly remove a target

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group list

List target groups.

```
usage: vinfra service block-storage target-group list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service block-storage target-group set

Set target group parameters.

```
usage: vinfra service block-storage target-group set [--wait] [--timeout <seconds>]
                                                     [--enable-acl | --disable-acl]
                                                     [--enable-chap | --disable-chap]
                                                     [--chap-user <user-name>]
                                                     <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

### Optional arguments:

**--enable-acl**  
Enable ACL

**--disable-acl**  
Disable ACL

**--enable-chap**  
Enable CHAP

**--disable-chap**  
Disable CHAP

**--chap-user \<user-name\>**  
CHAP user name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group show

Show target group details.

```
usage: vinfra service block-storage target-group show <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

---

## vinfra service block-storage target-group start

Start a target group.

```
usage: vinfra service block-storage target-group start [--wait] [--timeout <seconds>]
                                                       <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group stop

Stop a target group.

```
usage: vinfra service block-storage target-group stop [--wait] [--timeout <seconds>]
                                                      <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group target connection list

List target connections.

```
usage: vinfra service block-storage target-group target connection list [--long]
                                                                        <target-group> <target>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<target\>**  
Target IQN

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service block-storage target-group target create

Create a target.

```
usage: vinfra service block-storage target-group target create [--wait] [--timeout <seconds>]
                                                               --node <node> --ip <ip>
                                                               <target-group> <name>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<name\>**  
Target name

### Optional arguments:

**--node \<node\>**  
Target node

**--ip \<ip\>**  
Target IP address

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group target delete

Remove a target.

```
usage: vinfra service block-storage target-group target delete [--wait] [--timeout <seconds>]
                                                               [--force] <target-group> <target>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<target\>**  
Target IQN

### Optional arguments:

**--force**  
Forcibly remove a target

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group target list

List targets.

```
usage: vinfra service block-storage target-group target list [--long] <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service block-storage target-group target show

Show target details.

```
usage: vinfra service block-storage target-group target show <target-group> <target>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<target\>**  
Target IQN

---

## vinfra service block-storage target-group volume attach

Attach a volume to a target group.

```
usage: vinfra service block-storage target-group volume attach [--wait] [--timeout <seconds>]
                                                               [--lun <lun>] <target-group> <name>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<name\>**  
Volume name or ID

### Optional arguments:

**--lun \<lun\>**  
Lun ID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group volume detach

Detach a volume from a target group.

```
usage: vinfra service block-storage target-group volume detach [--wait] [--timeout <seconds>]
                                                               <target-group> <volume>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<volume\>**  
Volume name or ID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage target-group volume list

List target group volumes.

```
usage: vinfra service block-storage target-group volume list [--long] <target-group>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service block-storage target-group volume show

Show target group volume details.

```
usage: vinfra service block-storage target-group volume show <target-group> <volume>
```

### Positional arguments:

**\<target-group\>**  
Target group name or ID

**\<volume\>**  
Volume name or ID

---

## vinfra service block-storage user create

Create a user.

```
usage: vinfra service block-storage user create [--wait] [--timeout <seconds>]
                                                [--description <description>]
                                                <name>
```

### Positional arguments:

**\<name\>**  
User name

### Optional arguments:

**--description \<description\>**  
User desription

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage user delete

Remove a user.

```
usage: vinfra service block-storage user delete [--wait] [--timeout <seconds>]
                                                <user>
```

### Positional arguments:

**\<user\>**  
User name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage user list

List users.

```
usage: vinfra service block-storage user list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service block-storage user set

Update a user.

```
usage: vinfra service block-storage user set [--wait] [--timeout <seconds>]
                                             [--description <description>]
                                             [--password] <name>
```

### Positional arguments:

**\<name\>**  
User name

### Optional arguments:

**--description \<description\>**  
User description

**--password**  
Change user password

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage user show

Show user details.

```
usage: vinfra service block-storage user show <user>
```

### Positional arguments:

**\<user\>**  
User name

---

## vinfra service block-storage volume create

Create a volume.

```
usage: vinfra service block-storage volume create [--wait] [--timeout <seconds>]
                                                  --size <size> --tier {0,1,2,3}
                                                  (--replicas <norm> | --encoding <M>+<N>)
                                                  --failure-domain {0,1,2,3,4}
                                                  <name>
```

### Positional arguments:

**\<name\>**  
Volume name

### Optional arguments:

**--size \<size\>**  
Volume size, in bytes

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage volume delete

Remove a volume.

```
usage: vinfra service block-storage volume delete [--wait] [--timeout <seconds>]
                                                  <volume>
```

### Positional arguments:

**\<volume\>**  
Volume name or ID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage volume list

List volumes.

```
usage: vinfra service block-storage volume list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service block-storage volume set

Set volume parameters.

```
usage: vinfra service block-storage volume set [--wait] [--timeout <seconds>]
                                               [--read-ops-limit <iops>]
                                               [--write-ops-limit <iops>]
                                               [--read-bps-limit <MiB/s>]
                                               [--write-bps-limit <MiB/s>]
                                               <volume>
```

### Positional arguments:

**\<volume\>**  
Volume name or ID

### Optional arguments:

**--read-ops-limit \<iops\>**  
Number of read operations per second

**--write-ops-limit \<iops\>**  
Number of write operations per second

**--read-bps-limit \<MiB/s\>**  
Number of mebibytes read per second

**--write-bps-limit \<MiB/s\>**  
Number of mebibytes written per second

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service block-storage volume show

Show volume details.

```
usage: vinfra service block-storage volume show <volume>
```

### Positional arguments:

**\<volume\>**  
Volume name or ID

---

## vinfra service compute baseline-cpu

Determine baseline CPU models for the compute cluster

```
usage: vinfra service compute baseline-cpu [--nodes <nodes>]
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node IDs or hostnames.

---

## vinfra service compute create

Create compute cluster.

```
usage: vinfra service compute create [--wait] [--timeout <seconds>]
                                     --nodes <nodes> [--public-network <network>]
                                     [--subnet cidr=CIDR[,key1=value1,key2=value2...]]
                                     [--vlan-id <vlan-id>] [--mtu <mtu>]
                                     [--force] [--cpu-model <cpu-model>]
                                     [--cpu-features <cpu-features>]
                                     [--enable-k8saas] [--enable-lbaas]
                                     [--enable-metering]
                                     [--notification-forwarding <transport-url>]
                                     [--disable-notification-forwarding]
                                     [--endpoint-hostname <hostname>]
                                     [--pci-passthrough-config <path>]
                                     [--scheduler-config <path>]
                                     [--custom-param <service_name> <config_file> <section> <property> <value>]
                                     [--nova-scheduler-ram-weight-multiplier <value>]
                                     [--nova-compute-cpu-allocation-ratio <value>]
                                     [--k8s-default-quota <value>]
                                     [--nova-compute-ram-allocation-ratio <value>]
                                     [--neutron-openvswitch-vxlan-port <value>]
                                     [--nova-scheduler-host-subset-size <value>]
                                     [--load-balancer-default-quota <value>]
                                     [--placement-default-quota <value>]
                                     [--default-storage-policy-tier {0,1,2,3}]
                                     [--default-storage-policy-replicas <norm> | --default-storage-policy-encoding <M>+<N>]
                                     [--default-storage-policy-failure-domain {0,1,2,3,4}]
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node IDs or hostnames

**--public-network \<network\>**  
A physical network to connect the public virtual network to. It must include the 'VM public' traffic type.

**--subnet cidr=CIDR[,key1=value1,key2=value2...]**  
Subnet for IP address management in the public virtual network (the --public-network option is required):  
**cidr**: subnet range in CIDR notation;  
**gateway**: gateway IP address (optional);  
**dhcp**: enable/disable the virtual DHCP server (optional);  
**allocation-pool**: allocation pool of IP addresses from CIDR in the format `ip1-ip2`, where `ip1` and `ip2` are starting and ending IP addresses correspondingly. Specify the key multiple times to create multiple IP pools (optional);  
**dns-server**: DNS server IP address, specify multiple times to set multiple DNS servers (optional).  
Example: `--subnet cidr=192.168.5.0/24,dhcp=enable`

**--vlan-id \<vlan-id\>**  
Create VLAN based public network by given VLAN id.

**--mtu \<mtu\>**  
MTU value of public network

**--force**  
Skip checks for minimal hardware requirements.

**--cpu-model \<cpu-model\>**  
CPU model for virtual machines

**--cpu-features \<cpu-features\>**  
A comma-separated list of CPU features to enable or disable for virtual machines. For example, `ssbd,+vmx,-mpx` will enable ssbd and vmx and disable mpx.

**--enable-k8saas**  
Enable Kubernetes-as-a-Service services.

**--enable-lbaas**  
Enable Load-Balancing-as-a-Service services.

**--enable-metering**  
Enable metering services.

**--notification-forwarding \<transport-url\>**  
Enable notification forwarding through the specified transport URL.  
Transport URL format: `driver://[user:pass@]host:port[,[userN:passN@]hostN:portN]?query`  
Supported drivers: ampq, kafka, rabbit.  
Query params: topic - topic name, driver - messaging driver, possible values are messaging, messagingv2, routing, log, test, noop.  
Example: `kafka://10.10.10.10:9092?topic=notifications`

**--disable-notification-forwarding**  
Disable notification forwarding

**--endpoint-hostname \<hostname\>**  
Use given hostname for public endpoint. Specify empty value in quotes to use raw IP.

**--pci-passthrough-config \<path\>**  
Path to the PCI passthrough configuration file

**--scheduler-config \<path\>**  
Path to the scheduler configuration file

**--custom-param \<service_name\> \<config_file\> \<section\> \<property\> \<value\>**  
OpenStack custom parameters

**--nova-scheduler-ram-weight-multiplier \<value\>**  
(DEPRECATED) Use `--scheduler-config`

**--nova-compute-cpu-allocation-ratio \<value\>**  
Shortcut for `--custom-param nova-compute nova.conf DEFAULT cpu_allocation_ratio <value>`

**--k8s-default-quota \<value\>**  
Shortcut for `--custom-param magnum-api magnum.conf quotas max_clusters_per_project <value>`

**--nova-compute-ram-allocation-ratio \<value\>**  
Shortcut for `--custom-param nova-compute nova.conf DEFAULT ram_allocation_ratio <value>`

**--neutron-openvswitch-vxlan-port \<value\>**  
Shortcut for `--custom-param neutron-openvswitch-agent ml2_conf.ini agent vxlan_udp_port <value>`

**--nova-scheduler-host-subset-size \<value\>**  
Shortcut for `--custom-param nova-scheduler nova.conf DEFAULT scheduler_host_subset_size <value>`

**--load-balancer-default-quota \<value\>**  
Shortcut for `--custom-param octavia-api octavia.conf quotas default_load_balancer_quota <value>`

**--placement-default-quota \<value\>**  
Shortcut for `--custom-param placement-api placement.conf quota default_trait_quota <value>`

**--default-storage-policy-tier {0,1,2,3}**  
Storage tier

**--default-storage-policy-replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--default-storage-policy-encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--default-storage-policy-failure-domain {0,1,2,3,4}**  
Storage failure domain

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute delete

Delete a node from the compute cluster.

```
usage: vinfra service compute delete [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute flavor create

Create a new compute flavor.

```
usage: vinfra service compute flavor create [--swap <size-mb>] --vcpus <vcpus>
                                            --ram <size-mb> <flavor-name>
```

### Positional arguments:

**\<flavor-name\>**  
Flavor name

### Optional arguments:

**--swap \<size-mb\>**  
Swap space size, in megabytes

**--vcpus \<vcpus\>**  
Number of virtual CPUs

**--ram \<size-mb\>**  
Memory size, in megabytes

---

## vinfra service compute flavor delete

Delete a compute flavor.

```
usage: vinfra service compute flavor delete <flavor>
```

### Positional arguments:

**\<flavor\>**  
Flavor ID or name

---

## vinfra service compute flavor list

List compute flavors.

```
usage: vinfra service compute flavor list [--long] [--placement <placement>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--placement \<placement\>**  
List flavors added to a placement with the specified ID or use a filter. Supported filter operator: any. The filter format is `<operator>:<value1>[,<value2>,...]`.

---

## vinfra service compute flavor show

Display compute flavor details.

```
usage: vinfra service compute flavor show <flavor>
```

### Positional arguments:

**\<flavor\>**  
Flavor ID or name

---

## vinfra service compute floatingip create

Create a floating IP.

```
usage: vinfra service compute floatingip create [--port-id <port-id>]
                                                [--fixed-ip-address <fixed-ip-address>]
                                                [--description <description>]
                                                [--floating-ip-address <floating-ip-address>]
                                                --network <network>
```

### Optional arguments:

**--port-id \<port-id\>**  
ID of the port to be associated with the floating IP

**--fixed-ip-address \<fixed-ip-address\>**  
IP address of the port (only required if the port has multiple IPs)

**--description \<description\>**  
Description of the floating IP

**--floating-ip-address \<floating-ip-address\>**  
Floating IP address

**--network \<network\>**  
ID or name of the network from which to allocate the floating IP

---

## vinfra service compute floatingip delete

Delete a floating IP.

```
usage: vinfra service compute floatingip delete <floatingip>
```

### Positional arguments:

**\<floatingip\>**  
ID of the floating IP

---

## vinfra service compute floatingip list

List floating IPs.

```
usage: vinfra service compute floatingip list [--long] [--limit <num>]
                                              [--marker <floating-ip>]
                                              [--ip-address <ip-address>]
                                              [--id <id>]
                                              [--network <network>]
                                              [--project <project>]
                                              [--domain <domain>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of floating IPs to list. To list all floating IPs, set the option to -1.

**--marker \<floating-ip\>**  
List floating IPs after the marker.

**--ip-address \<ip-address\>**  
List floating IPs with the specified IP address or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a floating IP with the specified ID or list floating IPs using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--network \<network\>**  
List floating IPs that have the specified network name or ID.

**--project \<project\>**  
List floating ips that belong to projects with the specified names or IDs. Can only be performed by system administrators. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--domain \<domain\>**  
List floating ips that belong to a domain with the specified name or ID. Can only be performed by system administrators.

---

## vinfra service compute floatingip set

Modify a floating IP.

```
usage: vinfra service compute floatingip set [--port-id <port-id>]
                                             [--fixed-ip-address <fixed-ip-address>]
                                             [--description <description>]
                                             <floatingip>
```

### Positional arguments:

**\<floatingip\>**  
ID of the floating IP

### Optional arguments:

**--port-id \<port-id\>**  
ID of the port to be associated with the floating IP

**--fixed-ip-address \<fixed-ip-address\>**  
IP address of the port (only required if the port has multiple IPs)

**--description \<description\>**  
Description of the floating IP

---

## vinfra service compute floatingip show

Display information about a floating IP.

```
usage: vinfra service compute floatingip show <floatingip>
```

### Positional arguments:

**\<floatingip\>**  
ID of the floating IP

---

## vinfra service compute image create

Create a new compute image.

```
usage: vinfra service compute image create [--wait] [--timeout <seconds>]
                                           [--min-disk <size-gb>]
                                           [--min-ram <size-mb>]
                                           [--os-distro <os-distro>]
                                           [--protected] [--unprotected]
                                           [--public] [--private]
                                           [--disk-format <disk_format>]
                                           [--container-format <format>]
                                           [--tags <tags>] [--verify] --file
                                           <file> [--uefi] <image-name>
```

### Positional arguments:

**\<image-name\>**  
Image name

### Optional arguments:

**--min-disk \<size-gb\>**  
Minimum disk size required to boot from image, in gigabytes

**--min-ram \<size-mb\>**  
Minimum RAM size required to boot from image, in megabytes

**--os-distro \<os-distro\>**  
OS distribution. To list available distributions, run `vinfra service compute show`.

**--protected**  
Protect image from deletion.

**--unprotected**  
Allow image to be deleted.

**--public**  
Make image accessible to all users.

**--private**  
Make image accessible only to the owners.

**--disk-format \<disk_format\>**  
Disk format aki, ami, ari, detect, iso, ploop, qcow2, raw, vdi, vhd, vhdx, vmdk (default: detect)

**--container-format \<format\>**  
Container format: aki, ami, ari, bare, docker, ovf, ova (default: bare)

**--tags \<tags\>**  
A comma-separated list of tags

**--verify**  
Verify the checksum of the uploaded image

**--file \<file\>**  
Create image from a local file

**--uefi**  
Create image with UEFI.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute image delete

Delete a compute image.

```
usage: vinfra service compute image delete <image>
```

### Positional arguments:

**\<image\>**  
Image ID or name

---

## vinfra service compute image list

List compute images.

```
usage: vinfra service compute image list [--long] [--limit <num>]
                                         [--marker <image>] [--name <name>]
                                         [--id <id>] [--status <status>]
                                         [--placement <placement>]
                                         [--disk-format <disk-format>]
                                         [--project <project>]
                                         [--domain <domain>] [--sort <sort>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of images to list. To list all images, set the option to -1.

**--marker \<floating-ip\>**  
List images after the marker.

**--ip-address \<ip-address\>**  
List images with the specified IP address or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show an image with the specified ID or list images using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--placement \<placement\>**  
List images added to a placement with the specified ID or use a filter. Supported filter operator: any. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--disk-format \<disk-format\>**  
List images with the specified disk format.

**--project \<project\>**  
List images that belong to projects with the specified names or IDs. Can only be performed by system administrators. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--domain \<domain\>**  
List images that belong to a domain with the specified name or ID. Can only be performed by system administrators.

**--sort \<sort\>**  
List images sorted by key. The sorting format is `<sort-key>:<order>`. The order is 'asc' or 'desc'. Supported sort keys: id, name, status, created_at, updated_atsize, disk_format.

---

## vinfra service compute image save

Download a compute image.

```
usage: vinfra service compute image save [--file <filename>] <image>
```

### Positional arguments:

**\<image\>**  
Image ID or name

### Optional arguments:

**--file \<filename\>**  
File to save the image to (default: stdout)

---

## vinfra service compute image set

Modify compute image parameters.

```
usage: vinfra service compute image set [--min-disk <size-gb>]
                                        [--min-ram <size-mb>]
                                        [--os-distro <os-distro>]
                                        [--protected] [--unprotected]
                                        [--public] [--private] [--name <name>]
                                        <image>
```

### Positional arguments:

**\<image\>**  
Image ID or name

### Optional arguments:

**--min-disk \<size-gb\>**  
Minimum disk size required to boot from image, in gigabytes

**--min-ram \<size-mb\>**  
Minimum RAM size required to boot from image, in megabytes

**--os-distro \<os-distro\>**  
OS distribution. To list available distributions, run `vinfra service compute show`.

**--protected**  
Protect image from deletion.

**--unprotected**  
Allow image to be deleted.

**--public**  
Make image accessible to all users.

**--private**  
Make image accessible only to the owners.

**--name \<name\>**  
Image name

---

## vinfra service compute image show

Display compute image details.

```
usage: vinfra service compute image show <image>
```

### Positional arguments:

**\<image\>**  
Image ID or name

---

## vinfra service compute k8saas config

Display Kubernetes cluster config.

```
usage: vinfra service compute k8saas config <cluster>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

---

## vinfra service compute k8saas create

Create a new Kubernetes cluster.

```
usage: vinfra service compute k8saas create [--wait] [--timeout <seconds>]
                                            [--master-node-count <count>]
                                            [--node-count <count>]
                                            [--min-node-count <count>]
                                            [--max-node-count <count>]
                                            [--volume-storage-policy <policy>]
                                            [--kubernetes-version <version>]
                                            --master-flavor <flavor> --flavor <flavor>
                                            [--volume-size <size>]
                                            --external-network <network>
                                            [--network <network>] --key-name <key-name>
                                            [--use-floating-ip <use-floating-ip>]
                                            [--enable-public-access]
                                            [--api-lb-flavor <api-lb-flavor>]
                                            [--default-lb-flavor <default-lb-flavor>]
                                            [--monitoring-enabled]
                                            [--labels <key1=value1,key2=value2,key3=value3...>]
                                            [--containers-network-cidr <cidr>]
                                            [--containers-network-node-subnet-prefix-length <prefix_length>]
                                            [--service-network-cidr <cidr>]
                                            [--dns-service-ip <ip>] <name>
```

### Positional arguments:

**\<name\>**  
Kubernetes cluster name

### Optional arguments:

**--master-node-count \<count\>**  
The amount of master nodes in the Kubernetes cluster

**--node-count \<count\>**  
The amount of worker nodes in the Kubernetes cluster

**--min-node-count \<count\>**  
The minimum amount of worker nodes in the Kubernetes cluster

**--max-node-count \<count\>**  
The maximum amount of worker nodes in the Kubernetes cluster

**--volume-storage-policy \<policy\>**  
The name of the storage policy for the volume where containers will reside

**--kubernetes-version \<version\>**  
Kubernetes version

**--master-flavor \<flavor\>**  
The flavor to be used for Kubernetes master nodes

**--flavor \<flavor\>**  
The flavor to be used for Kubernetes worker nodes

**--volume-size \<size\>**  
The storage size of containers on each Kubernetes node

**--external-network \<network\>**  
The ID or name of the network that will provide Internet access to Kubernetes nodes

**--network \<network\>**  
The ID or name of the network that will provide networking to Kubernetes nodes

**--key-name \<key-name\>**  
The key pair to use for accessing the Kubernetes nodes

**--use-floating-ip \<use-floating-ip\>**  
Use floating IP addresses for all Kubernetes nodes ('true' or 'false').

**--enable-public-access**  
Use floating IP addresses for Kubernetes API ('true' or 'false').

**--api-lb-flavor \<api-lb-flavor\>**  
The ID or name of octavia flavor to use for API and ETCD loadbalancers

**--default-lb-flavor \<default-lb-flavor\>**  
The ID or name of octavia flavor to use as default for openstack-provider-created loadbalancers

**--monitoring-enabled**  
Enable installation of cluster monitoring.

**--labels \<key1=value1,key2=value2,key3=value3...\>**  
Arbitrary labels in the form of key=value pairs to associate with a cluster

**--containers-network-cidr \<cidr\>**  
Container network range in CIDR notation

**--containers-network-node-subnet-prefix-length \<prefix_length\>**  
The prefix length of a container subnet allocated to each Kubernetes node

**--service-network-cidr \<cidr\>**  
Kubernetes service network range in CIDR notation

**--dns-service-ip \<ip\>**  
DNS service IP address

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas defaults set

Manage default Kubernetes parameters values.

```
usage: vinfra service compute k8saas defaults set [--labels <key1=value1,key2=value2,key3=value3...>]
                                                  [--master-flavor <flavor>]
                                                  [--flavor <flavor>]
                                                  [--dns-nameserver <dns-nameserver>]
                                                  [--discovery-url <discovery-url>]
                                                  [--clear] [<version>]
```

### Positional arguments:

**\<version\>**  
Kubernetes version

### Optional arguments:

**--labels \<key1=value1,key2=value2,key3=value3...\>**  
Arbitrary labels in the form of key=value pairs to associate with a cluster

**--master-flavor \<flavor\>**  
The flavor to be used for Kubernetes master nodes

**--flavor \<flavor\>**  
The flavor to be used for Kubernetes worker nodes

**--dns-nameserver \<dns-nameserver\>**  
The DNS nameserver to use for clusters

**--discovery-url \<discovery-url\>**  
Specifies custom delivery url for node discovery

**--clear**  
Clear existing defaults associated with the version

---

## vinfra service compute k8saas defaults show

Show default Kubernetes parameters values.

```
usage: vinfra service compute k8saas defaults show [<version>]
```

### Positional arguments:

**\<version\>**  
Kubernetes version

---

## vinfra service compute k8saas delete

Delete a Kubernetes cluster.

```
usage: vinfra service compute k8saas delete [--wait] [--timeout <seconds>]
                                            <cluster>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas list

List Kubernetes clusters.

```
usage: vinfra service compute k8saas list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute k8saas rotate-ca

Rotate Kubernetes cluster CA certificates.

```
usage: vinfra service compute k8saas rotate-ca [--wait] [--timeout <seconds>]
                                               <cluster>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas set

Modify Kubernetes cluster parameters.

```
usage: vinfra service compute k8saas set [--wait] [--timeout <seconds>]
                                         [--node-count <count>]
                                         <cluster>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

### Optional arguments:

**--node-count \<count\>**  
The amount of worker nodes in the Kubernetes cluster

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas show

Display Kubernetes cluster details.

```
usage: vinfra service compute k8saas show <cluster>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

---

## vinfra service compute k8saas upgrade

Upgrade Kubernetes cluster.

```
usage: vinfra service compute k8saas upgrade [--wait] [--timeout <seconds>]
                                             <cluster> <version>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

**\<version\>**  
Kubernetes version

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas workergroup create

Create a new Kubernetes worker group.

```
usage: vinfra service compute k8saas workergroup create [--wait] [--timeout <seconds>]
                                                        --flavor <flavor>
                                                        [--node-count <count>]
                                                        [--min-node-count <count>]
                                                        [--max-node-count <count>]
                                                        [--labels <key1=value1,key2=value2,key3=value3...>]
                                                        <cluster> <name>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

**\<name\>**  
Kubernetes worker group name

### Optional arguments:

**--flavor \<flavor\>**  
The flavor to be used for Kubernetes worker group

**--node-count \<count\>**  
The amount of worker nodes in the Kubernetes worker group

**--min-node-count \<count\>**  
The minimum amount of worker nodes in the Kubernetes cluster

**--max-node-count \<count\>**  
The maximum amount of worker nodes in the Kubernetes cluster

**--labels \<key1=value1,key2=value2,key3=value3...\>**  
Arbitrary labels in the form of key=value pairs to associate with a cluster

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas workergroup delete

Delete a Kubernetes worker group.

```
usage: vinfra service compute k8saas workergroup delete [--wait] [--timeout <seconds>]
                                                        <cluster> <worker-group>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

**\<worker-group\>**  
Worker group ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas workergroup list

List Kubernetes worker groups.

```
usage: vinfra service compute k8saas workergroup list [--long] <cluster>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

---

## vinfra service compute k8saas workergroup set

Modify Kubernetes worker group parameters.

```
usage: vinfra service compute k8saas workergroup set [--wait] [--timeout <seconds>]
                                                     [--node-count <count>]
                                                     [--min-node-count <count>]
                                                     [--max-node-count <count>]
                                                     [--remove-node <id>]
                                                     <cluster> <worker-group>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

**\<worker-group\>**  
Worker group ID or name

### Optional arguments:

**--node-count \<count\>**  
The amount of worker nodes in the Kubernetes worker group

**--min-node-count \<count\>**  
The minimum amount of worker nodes in the Kubernetes cluster

**--max-node-count \<count\>**  
The maximum amount of worker nodes in the Kubernetes cluster

**--remove-node \<id\>**  
The ID of worker node to remove

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute k8saas workergroup show

Display Kubernetes worker group details.

```
usage: vinfra service compute k8saas workergroup show <cluster> <worker-group>
```

### Positional arguments:

**\<cluster\>**  
Cluster ID or name

**\<worker-group\>**  
Worker group ID or name

---

## vinfra service compute key create

Create new compute ssh key.

```
usage: vinfra service compute key create --public-key <public-key>
                                         [--description <description>]
                                         <ssh-key>
```

### Positional arguments:

**\<ssh-key\>**  
SSH key name

### Optional arguments:

**--public-key \<public-key\>**  
Public key from stdin (specify '-') or filename path

**--description \<description\>**  
SSH key description

---

## vinfra service compute key delete

Delete compute ssh key.

```
usage: vinfra service compute key delete <ssh-key>
```

### Positional arguments:

**\<ssh-key\>**  
SSH key name

---

## vinfra service compute key list

List compute ssh keys.

```
usage: vinfra service compute key list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute key show

Display compute ssh key details.

```
usage: vinfra service compute key show <ssh-key>
```

### Positional arguments:

**\<ssh-key\>**  
SSH key name

---

## vinfra service compute load-balancer create

Create a load balancer.

```
usage: vinfra service compute load-balancer create [--wait] [--timeout <seconds>]
                                                   [--description DESCRIPTION]
                                                   [--enable | --disable]
                                                   [--address ADDRESS | --ip-version {4,6}]
                                                   [--floating-ip FLOATING_IP]
                                                   [--pools-config POOLS]
                                                   [--enable-ha | --disable-ha]
                                                   <name> <network>
```

### Positional arguments:

**\<name\>**  
Load balancer name

**\<network\>**  
The ID or name of network the load balancer will operate in

### Optional arguments:

**--description DESCRIPTION**  
Load balancer description

**--enable**  
Enable the load balancer

**--disable**  
Disable the load balancer

**--address ADDRESS**  
The IP address the load balancer will try to allocate in the network

**--ip-version {4,6}**  
The IP version of the subnet the load balancer will operate in

**--floating-ip FLOATING_IP**  
The floating IP address that will be used to connect to the load balancer from public networks

**--pools-config POOLS**  
Pool configuration file

**--enable-ha**  
Enable the load balancer HA

**--disable-ha**  
Disable the load balancer HA

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute load-balancer delete

Delete a load balancer.

```
usage: vinfra service compute load-balancer delete [--wait] [--timeout <seconds>]
                                                   <load-balancer>
```

### Positional arguments:

**\<load-balancer\>**  
Load balancer ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute load-balancer failover

Failover a load balancer.

```
usage: vinfra service compute load-balancer failover [--wait] [--timeout <seconds>]
                                                     <load-balancer>
```

### Positional arguments:

**\<load-balancer\>**  
Load balancer ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute load-balancer list

List load balancers.

```
usage: vinfra service compute load-balancer list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute load-balancer pool create

Create a load balancer pool.

```
usage: vinfra service compute load-balancer pool create [--wait] [--timeout <seconds>] [--name NAME]
                                                        --protocol {HTTP,HTTPS,TCP,UDP} --port PORT
                                                        --algorithm {LEAST_CONNECTIONS,ROUND_ROBIN,SOURCE_IP}
                                                        --backend-protocol {HTTP,HTTPS,TCP,UDP}
                                                        --backend-port BACKEND_PORT
                                                        [--certificate-file CERTIFICATE]
                                                        [--connection-limit CONNECTION_LIMIT]
                                                        [--description DESCRIPTION]
                                                        [--healthmonitor type=<HTTP|HTTPS|PING|TCP|UDP>,[url_path=<str>,delay=<int>,enabled=<bool>,max_retries=<int>,max_retries_down=<int>,timeout=<int>]]
                                                        [--member address=<str>,[enabled=<bool>,weight=<int>]]
                                                        [--privatekey-file PRIVATE_KEY]
                                                        [--enable-sticky-session | --disable-sticky-session]
                                                        [--enable | --disable]
                                                        <load-balancer>
```

### Positional arguments:

**\<load-balancer\>**  
Load balancer ID or name

### Optional arguments:

**--name NAME**  
Pool name

**--protocol {HTTP,HTTPS,TCP,UDP}**  
The protocol for incoming connections

**--port PORT**  
The port for incoming connections

**--algorithm {LEAST_CONNECTIONS,ROUND_ROBIN,SOURCE_IP}**  
Load balancing algorithm

**--backend-protocol {HTTP,HTTPS,TCP,UDP}**  
The protocol for destination connections

**--backend-port BACKEND_PORT**  
The port for destination connections

**--certificate-file CERTIFICATE**  
An x.509 certificate file in the PEM format. Required for TLS-terminated HTTPS->HTTP load balancers.

**--connection-limit CONNECTION_LIMIT**  
The maximum number of connections permitted for this pool. The default value is -1 (infinite connections).

**--description DESCRIPTION**  
Pool description

**--healthmonitor type=\<HTTP|HTTPS|PING|TCP|UDP\>,[url_path=\<str\>,delay=\<int\>,enabled=\<bool\>,max_retries=\<int\>,max_retries_down=\<int\>,timeout=\<int\>]**  
Health monitor parameters:  
**type**: the health monitor type;  
**url_path**: the URL path to the health monitor;  
**delay**: the time, in seconds, between sending probes to members;  
**enabled**: declares whether the health monitor is enabled or not. Can be 'true' or 'false';  
**max_retries**: the number of successful checks required to change member status to 'HEALTHY'. Ranges from 1 to 10.  
**max_retries_down**: the number of unsuccessful checks required to change member status to 'UNHEALTHY'. Ranges from 1 to 10.  
**timeout**: the maximum time, in seconds, that a monitor waits to connect before it times out. This value must be less than the 'delay' value.

**--member address=\<str\>,[enabled=\<bool\>,weight=\<int\>]**  
Member parameters:  
**address**: an IPv4 address of the compute server;  
**enabled**: declares whether the member is enabled or not. Can be 'true' or 'false';  
**weight**: determines the share of connections that the member services compared to the other pool members. For example, a weight of 10 means that the member handles five times as many connections than a member with a weight of 2. '0' means that the member does not receive new connections but continues to service existing ones. Ranges from 0 to 256. The default value is 1.  
This option can be used multiple times.

**--privatekey-file PRIVATE_KEY**  
A private TLS key file in the PEM format. Required for TLS-terminated HTTPS->HTTP load balancers.

**--enable-sticky-session**  
Enable session persistence

**--disable-sticky-session**  
Disable session persistence

**--enable**  
Enable the pool

**--disable**  
Disable the pool

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute load-balancer pool delete

Delete a load balancer pool.

```
usage: vinfra service compute load-balancer pool delete <pool>
```

### Positional arguments:

**\<pool\>**  
Load balancer pool ID or name

---

## vinfra service compute load-balancer pool list

List load balancer pools.

```
usage: vinfra service compute load-balancer pool list [--long] [--load-balancer LOAD_BALANCER]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--load-balancer LOAD_BALANCER**  
Load balancer ID or name

---

## vinfra service compute load-balancer pool set

Modify a load balancer pool.

```
usage: vinfra service compute load-balancer pool set [--wait] [--timeout <seconds>] [--name NAME]
                                                     [--protocol {HTTP,HTTPS,TCP,UDP}] [--port PORT]
                                                     [--algorithm {LEAST_CONNECTIONS,ROUND_ROBIN,SOURCE_IP}]
                                                     [--backend-protocol {HTTP,HTTPS,TCP,UDP}]
                                                     [--backend-port BACKEND_PORT]
                                                     [--certificate-file CERTIFICATE]
                                                     [--connection-limit CONNECTION_LIMIT]
                                                     [--description DESCRIPTION]
                                                     [--healthmonitor type=<HTTP|HTTPS|PING|TCP|UDP>,[url_path=<str>,delay=<int>,enabled=<bool>,max_retries=<int>,max_retries_down=<int>,timeout=<int>]]
                                                     [--member address=<str>,[enabled=<bool>,weight=<int>]]
                                                     [--privatekey-file PRIVATE_KEY]
                                                     [--enable-sticky-session | --disable-sticky-session]
                                                     [--enable | --disable]
                                                     <pool>
```

### Positional arguments:

**\<pool\>**  
Load balancer pool ID or name

### Optional arguments:

**--name NAME**  
Pool name

**--protocol {HTTP,HTTPS,TCP,UDP}**  
The protocol for incoming connections

**--port PORT**  
The port for incoming connections

**--algorithm {LEAST_CONNECTIONS,ROUND_ROBIN,SOURCE_IP}**  
Load balancing algorithm

**--backend-protocol {HTTP,HTTPS,TCP,UDP}**  
The protocol for destination connections

**--backend-port BACKEND_PORT**  
The port for destination connections

**--certificate-file CERTIFICATE**  
An x.509 certificate file in the PEM format. Required for TLS-terminated HTTPS->HTTP load balancers.

**--connection-limit CONNECTION_LIMIT**  
The maximum number of connections permitted for this pool. The default value is -1 (infinite connections).

**--description DESCRIPTION**  
Pool description

**--healthmonitor type=\<HTTP|HTTPS|PING|TCP|UDP\>,[url_path=\<str\>,delay=\<int\>,enabled=\<bool\>,max_retries=\<int\>,max_retries_down=\<int\>,timeout=\<int\>]**  
Health monitor parameters:  
**type**: the health monitor type;  
**url_path**: the URL path to the health monitor;  
**delay**: the time, in seconds, between sending probes to members;  
**enabled**: declares whether the health monitor is enabled or not. Can be 'true' or 'false';  
**max_retries**: the number of successful checks required to change member status to 'HEALTHY'. Ranges from 1 to 10.  
**max_retries_down**: the number of unsuccessful checks required to change member status to 'UNHEALTHY'. Ranges from 1 to 10.  
**timeout**: the maximum time, in seconds, that a monitor waits to connect before it times out. This value must be less than the 'delay' value.

**--member address=\<str\>,[enabled=\<bool\>,weight=\<int\>]**  
Member parameters:  
**address**: an IPv4 address of the compute server;  
**enabled**: declares whether the member is enabled or not. Can be 'true' or 'false';  
**weight**: determines the share of connections that the member services compared to the other pool members. For example, a weight of 10 means that the member handles five times as many connections than a member with a weight of 2. '0' means that the member does not receive new connections but continues to service existing ones. Ranges from 0 to 256. The default value is 1.  
This option can be used multiple times.

**--privatekey-file PRIVATE_KEY**  
A private TLS key file in the PEM format. Required for TLS-terminated HTTPS->HTTP load balancers.

**--enable-sticky-session**  
Enable session persistence

**--disable-sticky-session**  
Disable session persistence

**--enable**  
Enable the pool

**--disable**  
Disable the pool

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute load-balancer pool show

Display load balancer pool details.

```
usage: vinfra service compute load-balancer pool show <pool>
```

### Positional arguments:

**\<pool\>**  
Load balancer pool ID or name

---

## vinfra service compute load-balancer recreate

Recreate a load balancer.

```
usage: vinfra service compute load-balancer recreate [--wait] [--timeout <seconds>]
                                                     <load-balancer>
```

### Positional arguments:

**\<load-balancer\>**  
Load balancer ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute load-balancer set

Modify a load balancer.

```
usage: vinfra service compute load-balancer set [--wait] [--timeout <seconds>]
                                                [--description DESCRIPTION]
                                                [--enable | --disable]
                                                [--name NAME]
                                                <load-balancer>
```

### Positional arguments:

**\<load-balancer\>**  
Load balancer ID or name

### Optional arguments:

**--description DESCRIPTION**  
Load balancer description

**--enable**  
Enable the load balancer

**--disable**  
Disable the load balancer

**--name NAME**  
Load balancer name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute load-balancer show

Display load balancer details.

```
usage: vinfra service compute load-balancer show <load-balancer>
```

### Positional arguments:

**\<load-balancer\>**  
Load balancer ID or name

---

## vinfra service compute load-balancer stats

Show statistics for a load balancer.

```
usage: vinfra service compute load-balancer stats <load-balancer>
```

### Positional arguments:

**\<load-balancer\>**  
Load balancer ID or name

---

## vinfra service compute network create

Create a compute network.

```
usage: vinfra service compute network create [--wait] [--timeout <seconds>]
                                             [--dhcp | --no-dhcp]
                                             [--dns-nameserver <dns-nameserver>]
                                             [--allocation-pool <allocation-pool>]
                                             [--gateway <gateway> | --no-gateway]
                                             [--rbac-policies <rbac-policies>]
                                             [--shared <shared>]
                                             [--physical-network <physical-network>]
                                             [--default-vnic-type {normal,direct}]
                                             [--vlan-network <vlan-network>]
                                             [--cidr <cidr>] [--vlan <vlan>] [--mtu <mtu>]
                                             [--ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}]
                                             <network-name>
```

### Positional arguments:

**\<network-name\>**  
Network name

### Optional arguments:

**--dhcp**  
Enable DHCP

**--no-dhcp**  
Disable DHCP

**--dns-nameserver \<dns-nameserver\>**  
DNS server IP address. This option can be used multiple times.

**--allocation-pool \<allocation-pool\>**  
Allocation pool to create inside the network in the format: `ip_addr_start-ip_addr_end`. This option can be used multiple times.

**--gateway \<gateway\>**  
Gateway IP address

**--no-gateway**  
Do not configure a gateway for this network

**--rbac-policies \<rbac-policies\>**  
Comma-separated list of RBAC policies in the format: `<target>:<target_id>:<action> | none`. Valid targets: project, domain. Valid actions: full, direct, routed. '*' is valid target_id for all targets. Pass 'none' to clear out all existing policies.  
Example: `domain:default:routed,project:uuid1:full`

**--shared \<shared\>**  
Share the network between all tenants (DEPRECATED)

**--physical-network \<physical-network\>**  
A physical network to link to a flat network

**--default-vnic-type {normal,direct}**  
Virtual port will inherit specified vnic_type from network

**--vlan-network \<vlan-network\>**  
A VLAN network to link

**--cidr \<cidr\>**  
Subnet range in CIDR notation

**--vlan \<vlan\>**  
Virtual network VLAN ID

**--mtu \<mtu\>**  
MTU Value

**--ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}**  
IPv6 address mode. Valid modes: dhcpv6-stateful, dhcpv6-stateless, slaac.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600). Supported only in the admin scope.

---

## vinfra service compute network delete

Delete a compute network.

```
usage: vinfra service compute network delete [--wait] [--timeout <seconds>]
                                             [--delete-vlan-interfaces]
                                             <network>
```

### Positional arguments:

**\<network\>**  
Network ID or name

### Optional arguments:

**--delete-vlan-interfaces**  
Delete node VLAN interfaces along with the compute VLAN network.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute network list

List compute networks.

```
usage: vinfra service compute network list [--long] [--limit <num>]
                                           [--marker <network>]
                                           [--name <name>] [--id <id>]
                                           [--project <project>]
                                           [--domain <domain>] [--type <type>]
                                           [--sort <sort>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of networks to list. To list all networks, set the option to -1.

**--marker \<network\>**  
List networks after the marker.

**--name \<name\>**  
List networks with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a network with the specified ID or list networks using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--project \<project\>**  
List networks that belong to projects with the specified names or IDs. Can only be performed by system administrators. Supported filter operators: in, contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--domain \<domain\>**  
List networks that belong to a domain with the specified name or ID. Can only be performed by system administrators.

**--type \<type\>**  
List networks with the specified type or use a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--sort \<sort\>**  
List networks sorted by key. The sorting format is `<sort-key>:<order>`. The order is 'asc' or 'desc'. Supported sort keys: id, name, status, admin_state_up, availability_zone_hints, mtu, tenant_id, project_id, type, created_at, updated_at.

---

## vinfra service compute network set

Modify compute network parameters.

```
usage: vinfra service compute network set [--dhcp | --no-dhcp]
                                          [--dns-nameserver <dns-nameserver>]
                                          [--allocation-pool <allocation-pool>]
                                          [--gateway <gateway> | --no-gateway]
                                          [--rbac-policies <rbac-policies>]
                                          [--shared <shared>] [--name <name>]
                                          [--mtu <mtu>]
                                          <network>
```

### Positional arguments:

**\<network-name\>**  
Network name

### Optional arguments:

**--dhcp**  
Enable DHCP

**--no-dhcp**  
Disable DHCP

**--dns-nameserver \<dns-nameserver\>**  
DNS server IP address. This option can be used multiple times. (DEPRECATED)

**--allocation-pool \<allocation-pool\>**  
Allocation pool to create inside the network in the format: `ip_addr_start-ip_addr_end`. This option can be used multiple times. (DEPRECATED)

**--gateway \<gateway\>**  
Gateway IP address (DEPRECATED)

**--no-gateway**  
Do not configure a gateway for this network (DEPRECATED)

**--rbac-policies \<rbac-policies\>**  
Comma-separated list of RBAC policies in the format: `<target>:<target_id>:<action> | none`. Valid targets: project, domain. Valid actions: full, direct, routed. '*' is valid target_id for all targets. Pass 'none' to clear out all existing policies.  
Example: `domain:default:routed,project:uuid1:full`

**--shared \<shared\>**  
Share the network between all tenants (DEPRECATED)

**--name \<name\>**  
A new name for the network

**--mtu \<mtu\>**  
MTU Value

---

## vinfra service compute network show

Display compute network details.

```
usage: vinfra service compute network show <network>
```

### Positional arguments:

**\<network\>**  
Network ID or name

---

## vinfra service compute node add

Add a node to the compute cluster.

```
usage: vinfra service compute node add [--wait] [--timeout <seconds>]
                                       [--compute] [--controller] [--force]
                                       <node> [<node> ...]
```

### Positional arguments:

**\<node\>**  
ID or hostname of the compute node

### Optional arguments:

**--compute**  
Compute node role

**--controller**  
Compute controller node role

**--force**  
Skip checks for minimal hardware requirements.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute node fence

Fence a compute node.

```
usage: vinfra service compute node fence [--force-down] [--reason <reason>]
                                         <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Optional arguments:

**--force-down**  
Forcefully mark the node as down.

**--reason \<reason\>**  
The reason for disabling the compute node

---

## vinfra service compute node list

List compute nodes.

```
usage: vinfra service compute node list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute node release

Release a node from the compute cluster.

```
usage: vinfra service compute node release [--wait] [--timeout <seconds>]
                                           [--compute] [--controller]
                                           <node> [<node> ...]
```

### Positional arguments:

**\<node\>**  
ID or hostname of the compute node

### Optional arguments:

**--compute**  
Compute node role

**--controller**  
Compute controller node role

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute node show

Display compute node details.

```
usage: vinfra service compute node show [--with-stats] <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

### Optional arguments:

**--with-stats**  
Get node info with statistics.

---

## vinfra service compute node unfence

Unfence a compute node.

```
usage: vinfra service compute node unfence <node>
```

### Positional arguments:

**\<node\>**  
Node ID or hostname

---

## vinfra service compute placement assign

Assign images and nodes to a compute placement.

```
usage: vinfra service compute placement assign (--images <images> | --nodes <nodes> | --flavors <flavors>)
                                               <placement>
```

### Positional arguments:

**\<placement\>**  
Placement ID or name

### Optional arguments:

**--images \<images\>**  
A comma-separated list of image names or IDs to assign to a compute placement

**--nodes \<nodes\>**  
A comma-separated list of compute node hosts or IDs to assign to a compute placement

**--flavors \<flavors\>**  
A comma-separated list of flavor names or IDs to assign to a compute placement

---

## vinfra service compute placement create

Create a new compute placement.

```
usage: vinfra service compute placement create [--isolated | --non-isolated]
                                               [--description <description>]
                                               [--nodes <nodes>]
                                               [--images <images>]
                                               [--flavors <flavors>]
                                               <placement-name>
```

### Positional arguments:

**\<placement-name\>**  
Placement name

### Optional arguments:

**--isolated**  
Create isolated placement (hard policy, default)

**--non-isolated**  
Create non-isolated placement (soft policy)

**--description \<description\>**  
Placement description

**--nodes \<nodes\>**  
A comma-separated list of compute node hosts or IDs to assign to a compute placement

**--images \<images\>**  
A comma-separated list of image names or IDs to assign to a compute placement

**--flavors \<flavors\>**  
A comma-separated list of flavor names or IDs to assign to a compute placement

---

## vinfra service compute placement delete

Delete a compute placement.

```
usage: vinfra service compute placement delete <placement>
```

### Positional arguments:

**\<placement\>**  
Placement ID or name

---

## vinfra service compute placement delete-assign

Remove images and nodes from a compute placement.

```
usage: vinfra service compute placement delete-assign (--image <image> | --node <node> | --flavor <flavor>)
                                                      <placement>
```

### Positional arguments:

**\<placement\>**  
Placement ID or name

### Optional arguments:

**--image \<image\>**  
An image name or ID to remove from a compute placement

**--node \<node\>**  
A compute node host or ID to remove from a compute placement

**--flavor \<flavor\>**  
A flavor name or ID to remove from a compute placement

---

## vinfra service compute placement list

List compute placements.

```
usage: vinfra service compute placement list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute placement show

Display compute placement details.

```
usage: vinfra service compute placement show <placement>
```

### Positional arguments:

**\<placement\>**  
Placement ID or name

---

## vinfra service compute placement update

Update a compute placement.

```
usage: vinfra service compute placement update [--name <placement-name>]
                                               [--description <placement-description>]
                                               [--non-isolated | --isolated]
                                               <placement>
```

### Positional arguments:

**\<placement\>**  
Placement ID or name

### Optional arguments:

**--name \<placement-name\>**  
A new name for the placement

**--description \<placement-description\>**  
A new description for the placement

**--non-isolated**  
Make placement non-isolated (soft policy)

**--isolated**  
Make placement isolated (hard policy)

---

## vinfra service compute quotas show

List compute quotas.

```
usage: vinfra service compute quotas show [--usage] <project_id>
```

### Positional arguments:

**\<project_id\>**  
Project ID

### Optional arguments:

**--usage**  
Include quota usage

---

## vinfra service compute quotas update

Update compute quotas.

```
usage: vinfra service compute quotas update [--cores <cores>]
                                            [--ram <ram>] [--ram-size <ram>]
                                            [--floatingip <floatingip>]
                                            [--ipsec-site-connection <ipsec-site-connection>]
                                            [--gigabytes <gigabytes> | --storage-policy <storage_policy>]
                                            [--k8saas-cluster <cluster>]
                                            [--lbaas-loadbalancer <load_balancer>]
                                            [--placement <placement>] <project_id>
```

### Positional arguments:

**\<project_id\>**  
Project ID

### Optional arguments:

**--cores \<cores\>**  
Number of cores

**--ram \<ram\>**  
Amount of RAM, in megabytes (DEPRECATED)

**--ram-size \<ram\>**  
Amount of RAM

**--floatingip \<floatingip\>**  
Number of floating IP addresses

**--ipsec-site-connection \<ipsec-site-connection\>**  
Number of VPN IPsec site connections

**--gigabytes \<gigabytes\>**  
Comma-separated list of `<storage_policy>:<size>` (DEPRECATED)

**--storage-policy \<storage_policy\>**  
Storage policy in the format `<storage_policy>:<size>` (this option can be used multiple times).

**--k8saas-cluster \<cluster\>**  
The new value for the Kubernetes clusters quota limit

**--lbaas-loadbalancer \<load_balancer\>**  
The new value for the load balancer quota limit. The value -1 means unlimited.

**--placement \<placement\>**  
Comma-separated list of `<placement_id>:<size>`

---

## vinfra service compute router create

Create a virtual router.

```
usage: vinfra service compute router create [--external-gateway <network>]
                                            [--enable-snat | --disable-snat]
                                            [--fixed-ip <fixid-ip>]
                                            [--internal-interface <network=network,ip-addr=ip-addr>|<network>]
                                            <name>
```

### Positional arguments:

**\<name\>**  
Name of the router

### Optional arguments:

**--external-gateway \<network\>**  
External network used as router's gateway (name or ID)

**--enable-snat**  
Enable source NAT on external gateway

**--disable-snat**  
Disable source NAT on external gateway

**--fixed-ip \<fixid-ip\>**  
Desired IP on external gateway

**--internal-interface \<network=network,ip-addr=ip-addr\>|\<network\>**  
Specify router interface. This option can be used multiple times.

---

## vinfra service compute router delete

Delete a virtual router.

```
usage: vinfra service compute router delete <router>
```

### Positional arguments:

**\<router\>**  
Virtual router name or ID

---

## vinfra service compute router iface add

Add an interface to a virtual router.

```
usage: vinfra service compute router iface add [--long] [--ip-address <ip-address>]
                                               --interface <network> <router>
```

### Positional arguments:

**\<router\>**  
Virtual router name or ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--ip-address \<ip-address\>**  
IP address

**--interface \<network\>**  
Network name or ID

---

## vinfra service compute router iface list

List router interfaces.

```
usage: vinfra service compute router iface list [--long] <router>
```

### Positional arguments:

**\<router\>**  
Virtual router name or ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute router iface remove

Remove an interface from a virtual router.

```
usage: vinfra service compute router iface remove [--long] --interface <network>
                                                  <router>
```

### Positional arguments:

**\<router\>**  
Virtual router name or ID

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--interface \<network\>**  
Network name or ID

---

## vinfra service compute router list

List virtual routers.

```
usage: vinfra service compute router list [--long] [--limit <num>]
                                          [--marker <router>] [--name <name>]
                                          [--id <id>] [--project <project>]
                                          [--domain <domain>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of routers to list. To list all routers, set the option to -1.

**--marker \<router\>**  
List routers after the marker.

**--name \<name\>**  
List routers with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a router with the specified ID or list routers using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--project \<project\>**  
List routers that belong to projects with the specified names or IDs. Can only be performed by system administrators. Supported filter operators: in, contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--domain \<domain\>**  
List routers that belong to a domain with the specified name or ID. Can only be performed by system administrators.

---

## vinfra service compute router set

Modify a virtual router.

```
usage: vinfra service compute router set [--name <name>]
                                         [--external-gateway <network> | --no-external-gateway]
                                         [--enable-snat | --disable-snat]
                                         [--fixed-ip <fixid-ip>]
                                         [--route <destination=destination,nexthop=nexthop> | --no-route]
                                         <router>
```

### Positional arguments:

**\<router\>**  
Virtual router name or ID

### Optional arguments:

**--name \<name\>**  
Router name

**--external-gateway \<network\>**  
External network used as router's gateway (name or ID)

**--no-external-gateway**  
Remove external gateway from the router

**--enable-snat**  
Enable source NAT on external gateway

**--disable-snat**  
Disable source NAT on external gateway

**--fixed-ip \<fixid-ip\>**  
Desired IP on external gateway

**--route \<destination=destination,nexthop=nexthop\>**  
Routes. This option can be used multiple times.

**--no-route**  
Clear routes associated with the router

---

## vinfra service compute router show

Display information about a virtual router.

```
usage: vinfra service compute router show <router>
```

### Positional arguments:

**\<router\>**  
Virtual router ID

---

## vinfra service compute security-group create

Create a security group.

```
usage: vinfra service compute security-group create [--description <description>]
                                                    <name>
```

### Positional arguments:

**\<name\>**  
Security group name

### Optional arguments:

**--description \<description\>**  
Security group description

---

## vinfra service compute security-group delete

Delete a security group.

```
usage: vinfra service compute security-group delete <security-group>
```

### Positional arguments:

**\<security-group\>**  
Security group name or ID

---

## vinfra service compute security-group list

List security groups.

```
usage: vinfra service compute security-group list [--long] [--limit <num>]
                                                  [--marker <marker>]
                                                  [--name <name>] [--id <id>]
                                                  [--project <project>]
                                                  [--domain <domain>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of security groups to list. To list all security groups, set the option to -1.

**--marker \<marker\>**  
List security groups after the marker.

**--name \<name\>**  
List security groups with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a security group with the specified ID or list security groups using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--project \<project\>**  
List security groups that belong to projects with the specified names or IDs. Can only be performed by system administrators. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--domain \<domain\>**  
List security groups that belong to a domain with the specified name or ID. Can only be performed by system administrators.

---

## vinfra service compute security-group rule create

Create a security group rule.

```
usage: vinfra service compute security-group rule create [--remote-group <remote-group>]
                                                         [--remote-ip <ip-address>]
                                                         [--ethertype <ethertype>]
                                                         [--protocol <protocol>]
                                                         [--port-range-max <port-range-max>]
                                                         [--port-range-min <port-range-min>]
                                                         (--ingress | --egress)
                                                         <security-group>
```

### Positional arguments:

**\<security-group\>**  
Security group name or ID to create the rule in

### Optional arguments:

**--remote-group \<remote-group\>**  
Remote security group name or ID

**--remote-ip \<ip-address\>**  
Remote IP address block in CIDR notation

**--ethertype \<ethertype\>**  
Ethertype of network traffic: IPv4 or IPv6

**--protocol \<protocol\>**  
IP protocol: tcp, udp, icmp, vrrp and others

**--port-range-max \<port-range-max\>**  
The maximum port number in the port range that satisfies the security group rule

**--port-range-min \<port-range-min\>**  
The minimum port number in the port range that satisfies the security group rule

**--ingress**  
Rule for incoming network traffic

**--egress**  
Rule for outgoing network traffic

---

## vinfra service compute security-group rule delete

Delete a security group rule.

```
usage: vinfra service compute security-group rule delete <security-group-rule>
```

### Positional arguments:

**\<security-group-rule\>**  
Security group rule name or ID

---

## vinfra service compute security-group rule list

List security group rules.

```
usage: vinfra service compute security-group rule list [--long] [--limit <num>]
                                                       [--marker <marker>]
                                                       [--id <id>] [<group>]
```

### Positional arguments:

**\<group\>**  
List security group rules in a particular security group specified by name or ID.

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of security group rules to list. To list all security group rules, set the option to -1.

**--marker \<marker\>**  
List security group rules after the marker.

**--id \<id\>**  
Show a security group rule with the specified ID or list security group rules using a filter. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

---

## vinfra service compute security-group rule show

Display information about a security group rule.

```
usage: vinfra service compute security-group rule show <security-group-rule>
```

### Positional arguments:

**\<security-group-rule\>**  
Security group rule ID

---

## vinfra service compute security-group set

Modify a security group.

```
usage: vinfra service compute security-group set [--name <name>]
                                                 [--description <description>]
                                                 <security-group>
```

### Positional arguments:

**\<security-group\>**  
Security group name or ID

### Optional arguments:

**--name \<name\>**  
Security group name

**--description \<description\>**  
Security group description

---

## vinfra service compute security-group show

Display information about a security group.

```
usage: vinfra service compute security-group show <security-group>
```

### Positional arguments:

**\<security-group\>**  
Security group name or ID

---

## vinfra service compute server cancel-stop

Cancel shutdown for a compute server.

```
usage: vinfra service compute server cancel-stop <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

---

## vinfra service compute server console

Display compute server console.

```
usage: vinfra service compute server console <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

---

## vinfra service compute server create

Create a new compute server.

```
usage: vinfra service compute server create [--wait] [--timeout <seconds>]
                                            [--description <description>]
                                            [--metadata <metadata>]
                                            [--user-data <user-data>]
                                            [--key-name <key-name>]
                                            [--config-drive] [--count <count>]
                                            --network id|<id=id[,mac=mac,fixed-ip=ip-addr[@subnet]>,
                                            spoofing-protection-enable,spoofing-protection-disable,
                                            security-group=secgroup,no-security-group]>
                                            --volume <source=source[,id=id,key1=value1,key2=value2...]>
                                            --flavor <flavor>
                                            [--ha-enabled <ha_enabled>]
                                            [--placements <placements>]
                                            [--allow-live-resize] [--uefi]
                                            <server-name>
```

### Positional arguments:

**\<server-name\>**  
A new name for the compute server

### Optional arguments:

**--description \<description\>**  
Server description

**--metadata \<metadata\>**  
Server metadata in the format `key=value`. Specify this option multiple times to create multiple metadata records.

**--user-data \<user-data\>**  
User data file

**--key-name \<key-name\>**  
Key pair to inject

**--config-drive**  
Use an ephemeral drive

**--count \<count\>**  
If count is specified and greater than 1, the 'name' argument is treated as a naming pattern.

**--network id|\<id=id[,mac=mac,fixed-ip=ip-addr[@subnet]\>,spoofing-protection-enable,spoofing-protection-disable,security-group=secgroup,no-security-group]>**  
Create a compute server with a specified network. Specify this option multiple times to create multiple networks.  
**id**: attach network interface to a specified network (ID or name);  
**mac**: MAC address for network interface (optional);  
**fixed-ip**: desired IP and/or subnet for network interface. Set IP address to None to allocate IP from desired subnet (optional);  
**spoofing-protection-enable**: enable spoofing protection (optional);  
**spoofing-protection-disable**: disable spoofing protection (optional);  
**security-group**: security group ID or name. This option can be used multiple times (optional);  
**no-security-group**: do not use security group (optional).

**--volume \<source=source[,id=id,key1=value1,key2=value2...]\>**  
Create a compute server with a specified volume. Specify this option multiple times to create multiple volumes.  
**source**: source type ('volume', 'image', 'snapshot', or 'blank');  
**id**: resource ID or name for the specified source type (required for source types 'volume', 'image', and 'snapshot');  
**size**: block device size, in gigabytes (required for source types 'image' and 'blank');  
**boot-index**: block device boot index (required for multiple volumes with source type 'volume');  
**bus**: block device controller type ('ide', 'usb', 'virtio', 'scsi, or 'sata') (optional);  
**type**: block device type (disk or cdrom) (optional);  
**rm**: remove block device on compute server termination ('yes' or 'no') (optional);  
**storage-policy**: block device storage policy (optional).

**--flavor \<flavor\>**  
Flavor ID or name

**--ha-enabled \<ha_enabled\>**  
Enable HA for the compute server

**--placements \<placements\>**  
Names or IDs of placements to add the virtual machine to

**--allow-live-resize**  
Allow online resize for the compute server

**--uefi**  
Allow UEFI boot for the compute server. This option can be used for servers created from ISO images.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server delete

Delete a compute server.

```
usage: vinfra service compute server delete [--wait] [--timeout <seconds>]
                                            <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server evacuate

Evacuate a stopped compute server from a failed host.

```
usage: vinfra service compute server evacuate [--wait] [--timeout <seconds>]
                                              <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server event list

List compute server events.

```
usage: vinfra service compute server event list [--long] --server <server>
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--server \<server\>**  
Server ID or name

---

## vinfra service compute server event show

Show details of a compute server event.

```
usage: vinfra service compute server event show --server <server>
                                                <event>
```

### Positional arguments:

**\<event\>**  
Event ID or name

### Optional arguments:

**--server \<server\>**  
Server ID or name

---

## vinfra service compute server iface attach

Attach a network to a compute server.

```
usage: vinfra service compute server iface attach [--fixed-ip <ip-address|ip-address=<ip-address>,subnet=<subnet>|ip-version=<ip-version>>]
                                                  [--spoofing-protection-enable | --spoofing-protection-disable]
                                                  [--security-group <security-group> | --no-security-groups]
                                                  [--mac <mac>] --server <server> --network <network>
```

### Optional arguments:

**--fixed-ip \<ip-address|ip-address=\<ip-address\>,subnet=\<subnet\>|ip-version=\<ip-version\>\>**  
Desired IP address and/or subnet.This option can be used multiple times.

**--spoofing-protection-enable**  
Enable spoofing protection for the network interface.

**--spoofing-protection-disable**  
Disable spoofing protection for the network interface.

**--security-group \<security-group\>**  
Security group ID or name. This option can be used multiple times.

**--no-security-groups**  
Do not set security groups

**--mac \<mac\>**  
MAC address

**--server \<server\>**  
Compute server ID or name

**--network \<network\>**  
Network ID or name

---

## vinfra service compute server iface detach

Detach a network interface from a compute server.

```
usage: vinfra service compute server iface detach --server <server>
                                                  <interface>
```

### Positional arguments:

**\<interface\>**  
Network interface ID

### Optional arguments:

**--server \<server\>**  
Compute server ID or name

---

## vinfra service compute server iface list

List compute server networks.

```
usage: vinfra service compute server iface list [--long] --server <server>
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--server \<server\>**  
Compute server ID or name

---

## vinfra service compute server iface set

Update a network interface of a compute server.

```
usage: vinfra service compute server iface set [--fixed-ip <ip-address|ip-address=<ip-address>,subnet=<subnet>|ip-version=<ip-version>>]
                                               [--spoofing-protection-enable | --spoofing-protection-disable]
                                               [--security-group <security-group> | --no-security-groups]
                                               --server <server> <interface>
```

### Positional arguments:

**\<interface\>**  
Network interface ID

### Optional arguments:

**--fixed-ip \<ip-address|ip-address=\<ip-address\>,subnet=\<subnet\>|ip-version=\<ip-version\>\>**  
Desired IP address and/or subnet.This option can be used multiple times.

**--spoofing-protection-enable**  
Enable spoofing protection for the network interface.

**--spoofing-protection-disable**  
Disable spoofing protection for the network interface.

**--security-group \<security-group\>**  
Security group ID or name. This option can be used multiple times.

**--no-security-groups**  
Do not set security groups

**--server \<server\>**  
Compute server ID or name

---

## vinfra service compute server list

List compute servers.

```
usage: vinfra service compute server list [--long] [--limit <num>]
                                          [--marker <server>] [--name <name>]
                                          [--id <id>] [--project <project>]
                                          [--domain <domain>]
                                          [--status <status>]
                                          [--task-status <task-status>]
                                          [--host <hostname>]
                                          [--placement <placement>]
                                          [--ip-address <ip-address>]
                                          [--sort <sort>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of servers to list. To list all servers, set the option to -1.

**--marker \<server\>**  
List servers after the marker.

**--name \<name\>**  
List servers with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a server with the specified ID or list servers using a filter. Supported filter operators: in, contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--project \<project\>**  
List servers that belong to projects with the specified names or IDs. Can only be performed by system administrators. Specify multiple project IDs as a comma-separated list. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--domain \<domain\>**  
List servers that belong to a domain with the specified name or ID. Can only be performed by system administrators.

**--status \<status\>**  
List servers with the specified status.

**--task-status \<task-status\>**  
List servers that have the specified task status.

**--host \<hostname\>**  
List servers located on a node with the specified hostname.

**--placement \<placement\>**  
List servers added to a placement with the specified ID or use a filter. Supported filter operator: any. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--ip-address \<ip-address\>**  
List servers that have the specified IP address

**--sort \<sort\>**  
List servers sorted by key. The sorting format is <sort-key>:<order>. The order is 'asc' or 'desc'. Supported sort keys: name, host, project_id, task_state, vm_state, vcpus, cpu_usage, mem_total, mem_usage, block_capacity, block_usage, created_at, updated_at.

---

## vinfra service compute server log

Display compute server log.

```
usage: vinfra service compute server log <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

---

## vinfra service compute server meta set

Set compute server metadata.

```
usage: vinfra service compute server meta set --server <server>
                                              <metadata> [<metadata> ...]
```

### Positional arguments:

**\<metadata\>**  
One or more key=value pairs separated by space

### Optional arguments:

**--server \<server\>**  
Server ID or name

---

## vinfra service compute server meta unset

Unset compute server metadata.

```
usage: vinfra service compute server meta unset --server <server>
                                                <metadata> [<metadata> ...]
```

### Positional arguments:

**\<metadata\>**  
One or more key=value pairs separated by space

### Optional arguments:

**--server \<server\>**  
Server ID or name

---

## vinfra service compute server migrate

Migrate a compute server to another host.

```
usage: vinfra service compute server migrate [--cold] [--node <node>]
                                             <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Optional arguments:

**--cold**  
Perform cold migration. If not set, try to determine migration type automatically.

**--node \<node\>**  
Destination node ID or hostname

---

## vinfra service compute server pause

Pause a compute server.

```
usage: vinfra service compute server pause [--wait] [--timeout <seconds>]
                                           <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server reboot

Reboot a compute server.

```
usage: vinfra service compute server reboot [--wait] [--timeout <seconds>]
                                            [--hard] <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Optional arguments:

**--hard**  
Perform hard reboot.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server rescue

Start server rescue mode.

```
usage: vinfra service compute server rescue [--wait] [--timeout <seconds>]
                                            [--image <image>] <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Optional arguments:

**--image \<image\>  
Boot from image ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server reset-state

Reset compute server state.

```
usage: vinfra service compute server reset-state [--wait] [--timeout <seconds>]
                                                 [--state-error] <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Optional arguments:

**--state-error**  
Reset server to 'ERROR' state

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server resize

Resize a compute server.

```
usage: vinfra service compute server resize [--wait] [--timeout <seconds>]
                                            --flavor <flavor> <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Optional arguments:

**--flavor \<flavor\>**  
Apply flavor with ID or name.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server resume

Resume a compute server.

```
usage: vinfra service compute server resume [--wait] [--timeout <seconds>]
                                            <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server set

Modify compute server parameters.

```
usage: vinfra service compute server set [--name <name>]
                                         [--description <description>]
                                         [--ha-enabled <ha_enabled>]
                                         [--allow-live-resize | --deny-live-resize]
                                         [--no-placements | --placement <placement>]
                                         <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Optional arguments:

**--name \<name\>**  
A new name for the compute server

**--description \<description\>**  
A new description for the compute server

**--ha-enabled \<ha_enabled\>**  
Enable HA for the compute server

**--allow-live-resize**  
Allow online resize for the compute server

**--deny-live-resize**  
Deny online resize for the compute server

**--no-placements**  
Clean up placements

**--placement \<placement\>**  
Server placement name or ID. Specify this option multiple times to create multiple placement records.

---

## vinfra service compute server shelve

Shelve compute server.

```
usage: vinfra service compute server shelve [--wait] [--timeout <seconds>]
                                            <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server show

Display compute server details.

```
usage: vinfra service compute server show <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

---

## vinfra service compute server start

Start a compute server.

```
usage: vinfra service compute server start [--wait] [--timeout <seconds>]
                                           <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server stat

Display compute server statistics.

```
usage: vinfra service compute server stat <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

---

## vinfra service compute server stop

Shut down a compute server.

```
usage: vinfra service compute server stop [--wait] [--timeout <seconds>]
                                          [--hard | --wait-time <seconds>]
                                          <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Optional arguments:

**--hard**  
Power off a compute server.

**--wait-time \<seconds\>**  
Shutdown timeout, after which a compute server will be powered off. Specify '-1' to set an infinite timeout.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server suspend

Suspend a compute server.

```
usage: vinfra service compute server suspend [--wait] [--timeout <seconds>]
                                             <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server tag add

Add a tag to a compute server.

```
usage: vinfra service compute server tag add --server <server> <tag>
```

### Positional arguments:

**\<tag\>**  
Server tag

### Optional arguments:

**--server \<server\>**  
Server ID or name

---

## vinfra service compute server tag delete

Delete a tag from a compute server.

```
usage: vinfra service compute server tag delete --server <server> <tag>
```

### Positional arguments:

**\<tag\>**  
Server tag

### Optional arguments:

**--server \<server\>**  
Server ID or name

---

## vinfra service compute server tag list

List compute server tags.

```
usage: vinfra service compute server tag list <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

---

## vinfra service compute server unpause

Unpause a compute server.

```
usage: vinfra service compute server unpause [--wait] [--timeout <seconds>]
                                             <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server unrescue

Exit server from rescue mode.

```
usage: vinfra service compute server unrescue [--wait] [--timeout <seconds>]
                                              <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server unshelve

Unshelve compute server.

```
usage: vinfra service compute server unshelve [--wait] [--timeout <seconds>]
                                              <server>
```

### Positional arguments:

**\<server\>**  
Compute server ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute server volume attach

Attach a volume to a compute server.

```
usage: vinfra service compute server volume attach --server <server> <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Optional arguments:

**--server \<server\>**  
Compute server ID or name

---

## vinfra service compute server volume detach

Detach a volume from a compute server.

```
usage: vinfra service compute server volume detach [--force] --server <server>
                                                   <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Optional arguments:

**--force**  
Detach a volume without checking if either the volume or server exists. When specifying the volume and server, use their IDs. No name lookup is performed.

**--server \<server\>**  
Compute server ID or name

---

## vinfra service compute server volume list

List compute server volumes.

```
usage: vinfra service compute server volume list [--long] --server <server>
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--server \<server\>**  
Compute server ID or name

---

## vinfra service compute server volume show

Show details of a compute server volume.

```
usage: vinfra service compute server volume show --server <server> <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Optional arguments:

**--server \<server\>**  
Compute server ID or name

---

## vinfra service compute set

Change compute cluster parameters.

```
usage: vinfra service compute set [--wait] [--timeout <seconds>] [--force]
                                  [--cpu-model <cpu-model>]
                                  [--cpu-features <cpu-features>]
                                  [--enable-k8saas] [--enable-lbaas]
                                  [--enable-metering]
                                  [--notification-forwarding <transport-url>]
                                  [--disable-notification-forwarding]
                                  [--endpoint-hostname <hostname>]
                                  [--pci-passthrough-config <path>]
                                  [--scheduler-config <path>]
                                  [--custom-param <service_name> <config_file> <section> <property> <value>]
                                  [--nova-scheduler-ram-weight-multiplier <value>]
                                  [--nova-compute-cpu-allocation-ratio <value>]
                                  [--k8s-default-quota <value>]
                                  [--nova-compute-ram-allocation-ratio <value>]
                                  [--neutron-openvswitch-vxlan-port <value>]
                                  [--nova-scheduler-host-subset-size <value>]
                                  [--load-balancer-default-quota <value>]
                                  [--placement-default-quota <value>]
```

### Optional arguments:

**--force**  
Skip checks for minimal hardware requirements.

**--cpu-model \<cpu-model\>**  
CPU model for virtual machines

**--cpu-features \<cpu-features\>**  
A comma-separated list of CPU features to enable or disable for virtual machines. For example, `ssbd,+vmx,-mpx` will enable ssbd and vmx and disable mpx.

**--enable-k8saas**  
Enable Kubernetes-as-a-Service services.

**--enable-lbaas**  
Enable Load-Balancing-as-a-Service services.

**--enable-metering**  
Enable metering services.

**--notification-forwarding \<transport-url\>**  
Enable notification forwarding through the specified transport URL.  
Transport URL format: `driver://[user:pass@]host:port[,[userN:passN@]hostN:portN]?query`  
Supported drivers: ampq, kafka, rabbit.  
Query params: topic - topic name, driver - messaging driver, possible values are messaging, messagingv2, routing, log, test, noop.  
Example: `kafka://10.10.10.10:9092?topic=notifications`

**--disable-notification-forwarding**  
Disable notification forwarding

**--endpoint-hostname \<hostname\>**  
Use given hostname for public endpoint. Specify empty value in quotes to use raw IP.

**--pci-passthrough-config \<path\>**  
Path to the PCI passthrough configuration file

**--scheduler-config \<path\>**  
Path to the scheduler configuration file

**--custom-param \<service_name\> \<config_file\> \<section\> \<property\> \<value\>**  
OpenStack custom parameters

**--nova-scheduler-ram-weight-multiplier \<value\>**  
(DEPRECATED) Use `--scheduler-config`

**--nova-compute-cpu-allocation-ratio \<value\>**  
Shortcut for `--custom-param nova-compute nova.conf DEFAULT cpu_allocation_ratio <value>`

**--k8s-default-quota \<value\>**  
Shortcut for `--custom-param magnum-api magnum.conf quotas max_clusters_per_project <value>`

**--nova-compute-ram-allocation-ratio \<value\>**  
Shortcut for `--custom-param nova-compute nova.conf DEFAULT ram_allocation_ratio <value>`

**--neutron-openvswitch-vxlan-port \<value\>**  
Shortcut for `--custom-param neutron-openvswitch-agent ml2_conf.ini agent vxlan_udp_port <value>`

**--nova-scheduler-host-subset-size \<value\>**  
Shortcut for `--custom-param nova-scheduler nova.conf DEFAULT scheduler_host_subset_size <value>`

**--load-balancer-default-quota \<value\>**  
Shortcut for `--custom-param octavia-api octavia.conf quotas default_load_balancer_quota <value>`

**--placement-default-quota \<value\>**  
Shortcut for `--custom-param placement-api placement.conf quota default_trait_quota <value>`

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute show

Display compute cluster details.

```
usage: vinfra service compute show
```

---

## vinfra service compute stat

Display compute cluster statistics.

```
usage: vinfra service compute stat
```

---

## vinfra service compute storage add

Add a compute storage.

```
usage: vinfra service compute storage add [--max-value-length MAX_VALUE_LENGTH]
                                          [--wait] [--timeout <seconds>]
                                          [--params <param=value>[,<param2=value2>]
                                          [--params <param3=value3>] ...]
                                          [--secret-params <param=value>[,<param2=value2>]
                                          [--secret-params <param3=value3>] ...]
                                          [--enable | --disable] <name>
```

### Positional arguments:

**\<name\>**  
Compute storage name

### Optional arguments:

**--params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
A comma-separated list of parameters in the format `key=value`. This option can be used multiple times.

**--secret-params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
A comma-separated list of secret parameters in the format `key=value`. This option can be used multiple times.

**--enable**  
Enable the compute storage

**--disable**  
Disable the compute storage

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute storage list

List existing compute storages.

```
usage: vinfra service compute storage list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute storage remove

Remove a compute storage.

```
usage: vinfra service compute storage remove [--wait] [--timeout <seconds>]
                                             <name>
```

### Positional arguments:

**\<name\>**  
Compute storage name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute storage set

Modify compute storage parameters.

```
usage: vinfra service compute storage set [--wait] [--timeout <seconds>]
                                          [--params <param=value>[,<param2=value2>]
                                          [--params <param3=value3>] ...]
                                          [--secret-params <param=value>[,<param2=value2>]
                                          [--secret-params <param3=value3>] ...]
                                          [--enable | --disable]
                                          [--unset-params <params>]
                                          [--unset-secret-params <params>]
                                          <name>
```

### Positional arguments:

**\<name\>**  
Compute storage name

### Optional arguments:

**--params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
A comma-separated list of parameters in the format `key=value`. This option can be used multiple times.

**--secret-params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
A comma-separated list of secret parameters in the format `key=value`. This option can be used multiple times.

**--enable**  
Enable the compute storage

**--disable**  
Disable the compute storage

**--unset-params \<params\>**  
A comma-separated list of parameters to unset

**--unset-secret-params \<params\>**  
A comma-separated list of secret parameters to unset

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute storage show

Show details of a compute storage.

```
usage: vinfra service compute storage show <name>
```

### Positional arguments:

**\<name\>**  
Compute storage name

---

## vinfra service compute storage-policy create

Create a new storage policy.

```
usage: vinfra service compute storage-policy create [--tier {0,1,2,3}]
                                                    [--replicas <norm> | --encoding <M>+<N>]
                                                    [--failure-domain {0,1,2,3,4}]
                                                    [--write-bytes-sec-per-gb <limit>]
                                                    [--write-bytes-sec <limit>]
                                                    [--read-iops-sec-per-gb <limit>]
                                                    [--total-iops-sec <limit>]
                                                    [--total-bytes-sec-per-gb-min <limit>]
                                                    [--read-iops-sec-per-gb-min <limit>]
                                                    [--write-bytes-sec-per-gb-min <limit>]
                                                    [--total-bytes-sec-per-gb <limit>]
                                                    [--write-iops-sec-per-gb-min <limit>]
                                                    [--read-bytes-sec-per-gb-min <limit>]
                                                    [--read-bytes-sec-per-gb <limit>]
                                                    [--total-iops-sec-per-gb <limit>]
                                                    [--read-iops-sec <limit>]
                                                    [--read-bytes-sec <limit>]
                                                    [--write-iops-sec-per-gb <limit>]
                                                    [--write-iops-sec <limit>]
                                                    [--total-iops-sec-per-gb-min <limit>]
                                                    [--total-bytes-sec <limit>]
                                                    [--storage <storage-name>]
                                                    [--params <param=value>[,<param2=value2>]
                                                    [--params <param3=value3>] ...]
                                                    <name>
```

### Positional arguments:

**\<storage-policy\>**  
Storage policy ID or name

### Optional arguments:

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--write-bytes-sec-per-gb \<limit\>**  
Write number of bytes per second per GB

**--write-bytes-sec \<limit\>**  
Write number of bytes per second

**--read-iops-sec-per-gb \<limit\>**  
Read number of I/O operations per second per GB

**--total-iops-sec \<limit\>**  
Total number of I/O operations per second

**--total-bytes-sec-per-gb-min \<limit\>**  
Total number of bytes per second per GB (min)

**--read-iops-sec-per-gb-min \<limit\>**  
Read number of I/O operations per second per GB (min)

**--write-bytes-sec-per-gb-min \<limit\>**  
Write number of bytes per second per GB (min)

**--total-bytes-sec-per-gb \<limit\>**  
Total number of bytes per second per GB

**--write-iops-sec-per-gb-min \<limit\>**  
Write number of I/O operations per second per GB (min)

**--read-bytes-sec-per-gb-min \<limit\>**  
Read number of bytes per second per GB (min)

**--read-bytes-sec-per-gb \<limit\>**  
Read number of bytes per second per GB

**--total-iops-sec-per-gb \<limit\>**  
Total number of I/O operations per second per GB

**--read-iops-sec \<limit\>**  
Read number of I/O operations per second

**--read-bytes-sec \<limit\>**  
Read number of bytes per second

**--write-iops-sec-per-gb \<limit\>**  
Write number of I/O operations per second per GB

**--write-iops-sec \<limit\>**  
Write number of I/O operations per second

**--total-iops-sec-per-gb-min \<limit\>**  
Total number of I/O operations per second per GB (min)

**--total-bytes-sec \<limit\>**  
Total number of bytes per second

**--storage \<storage-name\>**  
Compute storage name

**--params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
Custom parameters

---

## vinfra service compute storage-policy delete

Remove an existing storage policy.

```
usage: vinfra service compute storage-policy delete <storage-policy>
```

### Positional arguments:

**\<storage-policy\>**  
Storage policy ID or name

---

## vinfra service compute storage-policy list

List existing storage policies.

```
usage: vinfra service compute storage-policy list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute storage-policy set

Modify storage policy parameters.

```
usage: vinfra service compute storage-policy set [--name <name>]
                                                 [--tier {0,1,2,3}]
                                                 [--replicas <norm> | --encoding <M>+<N>]
                                                 [--failure-domain {0,1,2,3,4}]
                                                 [--write-bytes-sec-per-gb <limit>]
                                                 [--write-bytes-sec <limit>]
                                                 [--read-iops-sec-per-gb <limit>]
                                                 [--total-iops-sec <limit>]
                                                 [--total-bytes-sec-per-gb-min <limit>]
                                                 [--read-iops-sec-per-gb-min <limit>]
                                                 [--write-bytes-sec-per-gb-min <limit>]
                                                 [--total-bytes-sec-per-gb <limit>]
                                                 [--write-iops-sec-per-gb-min <limit>]
                                                 [--read-bytes-sec-per-gb-min <limit>]
                                                 [--read-bytes-sec-per-gb <limit>]
                                                 [--total-iops-sec-per-gb <limit>]
                                                 [--read-iops-sec <limit>]
                                                 [--read-bytes-sec <limit>]
                                                 [--write-iops-sec-per-gb <limit>]
                                                 [--write-iops-sec <limit>]
                                                 [--total-iops-sec-per-gb-min <limit>]
                                                 [--total-bytes-sec <limit>]
                                                 [--storage <storage-name>]
                                                 [--params <param=value>[,<param2=value2>]
                                                 [--params <param3=value3>] ...]
                                                 [--unset-params <params>]
                                                 <storage-policy>
```

### Positional arguments:

**\<storage-policy\>**  
Storage policy ID or name

### Optional arguments:

**--name \<name\>**  
A new name for the storage policy

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--write-bytes-sec-per-gb \<limit\>**  
Write number of bytes per second per GB

**--write-bytes-sec \<limit\>**  
Write number of bytes per second

**--read-iops-sec-per-gb \<limit\>**  
Read number of I/O operations per second per GB

**--total-iops-sec \<limit\>**  
Total number of I/O operations per second

**--total-bytes-sec-per-gb-min \<limit\>**  
Total number of bytes per second per GB (min)

**--read-iops-sec-per-gb-min \<limit\>**  
Read number of I/O operations per second per GB (min)

**--write-bytes-sec-per-gb-min \<limit\>**  
Write number of bytes per second per GB (min)

**--total-bytes-sec-per-gb \<limit\>**  
Total number of bytes per second per GB

**--write-iops-sec-per-gb-min \<limit\>**  
Write number of I/O operations per second per GB (min)

**--read-bytes-sec-per-gb-min \<limit\>**  
Read number of bytes per second per GB (min)

**--read-bytes-sec-per-gb \<limit\>**  
Read number of bytes per second per GB

**--total-iops-sec-per-gb \<limit\>**  
Total number of I/O operations per second per GB

**--read-iops-sec \<limit\>**  
Read number of I/O operations per second

**--read-bytes-sec \<limit\>**  
Read number of bytes per second

**--write-iops-sec-per-gb \<limit\>**  
Write number of I/O operations per second per GB

**--write-iops-sec \<limit\>**  
Write number of I/O operations per second

**--total-iops-sec-per-gb-min \<limit\>**  
Total number of I/O operations per second per GB (min)

**--total-bytes-sec \<limit\>**  
Total number of bytes per second

**--storage \<storage-name\>**  
Compute storage name

**--params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...**  
Custom parameters

**--unset-params \<params\>**  
A comma-separated list of parameters to unset

---

## vinfra service compute storage-policy show

Show details of a storage policy.

```
usage: vinfra service compute storage-policy show <storage-policy>
```

### Positional arguments:

**\<storage-policy\>**  
Storage policy ID or name

---

## vinfra service compute subnet create

Create a compute network subnet.

```
usage: vinfra service compute subnet create [--dhcp | --no-dhcp]
                                            [--dns-nameserver <dns-nameserver>]
                                            [--allocation-pool <allocation-pool>]
                                            [--gateway <gateway> | --no-gateway]
                                            --network <network> --cidr <cidr>
                                            [--ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}]
```

### Optional arguments:

**--dhcp**  
Enable DHCP

**--no-dhcp**  
Disable DHCP

**--dns-nameserver \<dns-nameserver\>**  
DNS server IP address. This option can be used multiple times.

**--allocation-pool \<allocation-pool\>**  
Allocation pool to create inside the network in the format: `ip_addr_start-ip_addr_end`. This option can be used multiple times.

**--gateway \<gateway\>**  
Gateway IP address

**--no-gateway**  
Do not configure a gateway for this network

**--network \<network\>**  
Network ID or name

**--cidr \<cidr\>**  
Subnet range in CIDR notation

**--ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}**  
IPv6 address mode. Valid modes: dhcpv6-stateful, dhcpv6-stateless, slaac.

---

## vinfra service compute subnet delete

Delete a compute network subnet.

```
usage: vinfra service compute subnet delete <subnet>
```

### Positional arguments:

**\<subnet\>**  
Subnet ID

---

## vinfra service compute subnet list

List compute networks subnets.

```
usage: vinfra service compute subnet list [--long] --network <type>
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--network \<type\>**  
Network ID or name

---

## vinfra service compute subnet set

Modify compute network subnet parameters.

```
usage: vinfra service compute subnet set [--dhcp | --no-dhcp]
                                         [--dns-nameserver <dns-nameserver>]
                                         [--allocation-pool <allocation-pool>]
                                         [--gateway <gateway> | --no-gateway]
                                         <subnet>
```

### Positional arguments:

**\<subnet\>**  
Subnet ID

### Optional arguments:

**--dhcp**  
Enable DHCP

**--no-dhcp**  
Disable DHCP

**--dns-nameserver \<dns-nameserver\>**  
DNS server IP address. This option can be used multiple times.

**--allocation-pool \<allocation-pool\>**  
Allocation pool to create inside the network in the format: `ip_addr_start-ip_addr_end`. This option can be used multiple times.

**--gateway \<gateway\>**  
Gateway IP address

**--no-gateway**  
Do not configure a gateway for this network

---

## vinfra service compute subnet show

Display compute network subnet details.

```
usage: vinfra service compute subnet show <subnet>
```

### Positional arguments:

**\<subnet\>**  
Subnet ID

---

## vinfra service compute task abort

Abort a failed compute task.

```
usage: vinfra service compute task abort [--task-id TASK_ID]
```

### Optional arguments:

**--task-id TASK_ID**  
Compute task ID

---

## vinfra service compute task retry

Retry a failed compute task.

```
usage: vinfra service compute task retry [--task-id TASK_ID]
```

### Optional arguments:

**--task-id TASK_ID**  
Compute task ID

---

## vinfra service compute task show

Show compute task details.

```
usage: vinfra service compute task show [--task-id TASK_ID]
```

### Optional arguments:

**--task-id TASK_ID**  
Compute task ID

---

## vinfra service compute volume clone

Create a new compute volume from a compute volume.

```
usage: vinfra service compute volume clone [--wait] [--timeout <seconds>]
                                           --name <name> [--size <size-gb>]
                                           [--storage-policy <storage_policy>]
                                           <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Optional arguments:

**--name \<name\>**  
New volume name

**--size \<size-gb\>**  
Volume size, in gigabytes

**--storage-policy \<storage_policy\>**  
Storage policy ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume create

Create a new compute volume.

```
usage: vinfra service compute volume create [--wait] [--timeout <seconds>]
                                            [--description <description>]
                                            [--network-install <network_install>]
                                            [--image <image>]
                                            [--snapshot <snapshot>]
                                            --storage-policy <storage_policy>
                                            --size <size-gb> <volume-name>
```

### Positional arguments:

**\<volume-name\>**  
Volume name

### Optional arguments:

**--description \<description\>**  
Volume description

**--network-install \<network_install\>**  
Perform network install ('true' or 'false').

**--image \<image\>**  
Source compute image ID or name

**--snapshot \<snapshot\>**  
Source compute volume snapshot ID or name

**--storage-policy \<storage_policy\>**
Storage policy ID or name

**--size \<size-gb\>**  
Volume size, in gigabytes

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume delete

Delete a compute volume.

```
usage: vinfra service compute volume delete [--wait] [--timeout <seconds>]
                                            <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume extend

Extend a compute volume.

```
usage: vinfra service compute volume extend [--wait] [--timeout <seconds>]
                                            --size <size_gb> <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Optional arguments:

**--size \<size_gb\>**  
Size to extend to

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume list

List compute volumes.

```
usage: vinfra service compute volume list [--long] [--limit <num>]
                                          [--marker <volume>] [--name <name>]
                                          [--id <id>] [--project <project>]
                                          [--domain <domain>]
                                          [--status <status>] [--size <size>]
                                          [--storage-policy <storage_policy>]
                                          [--volume-type <type>]
                                          [--sort <sort>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--limit \<num\>**  
The maximum number of volumes to list. To list all volumes, set the option to -1.

**--marker \<volume\>**  
List volumes after the marker.

**--name \<name\>**  
List volumes with the specified name or use a filter. Supported filter operator: contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--id \<id\>**  
Show a volume with the specified ID or list volumes using a filter. Supported filter operators: in, contains. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--project \<project\>**  
List volumes that belong to projects with the specified names or IDs. Can only be performed by system administrators. Supported filter operator: in. The filter format is `<operator>:<value1>[,<value2>,...]`.

**--domain \<domain\>**  
List volumes that belong to a domain with the specified name or ID. Can only be performed by system administrators.

**--status \<status\>**  
List volumes with the specified status.

**--size \<size\>**  
List volumes with the specified size.

**--storage-policy \<storage_policy\>**  
List volumes with the specified storage policy name or ID.

**--volume-type \<type\>**  
List volumes with the specified type.

**--sort \<sort\>**  
List volumes sorted by key. The sorting format is <sort-key>:<order>. The order is 'asc' or 'desc'. Supported sort keys: id, name, size, status, created_at.

---

## vinfra service compute volume reset-state

Reset compute volume state.

```
usage: vinfra service compute volume reset-state [--wait] [--timeout <seconds>]
                                                 <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume set

Modify volume parameters

```
usage: vinfra service compute volume set [--description <description>]
                                         [--network-install <network_install>]
                                         [--storage-policy <storage_policy>]
                                         [--bootable <bootable>]
                                         [--name <name>] [--no-placements]
                                         <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Optional arguments:

**--description \<description\>**  
Volume description

**--network-install \<network_install\>**  
Perform network install ('true' or 'false').

**--storage-policy \<storage_policy\>**  
Storage policy ID or name

**--bootable \<bootable\>**  
Make bootable ('true' or 'false').

**--name \<name\>**  
A new name for the volume

**--no-placements**  
Clean up placements

---

## vinfra service compute volume show

Display compute volume details.

```
usage: vinfra service compute volume show <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

---

## vinfra service compute volume snapshot create

Create a new compute volume snapshot.

```
usage: vinfra service compute volume snapshot create [--wait] [--timeout <seconds>]
                                                     [--description <description>]
                                                     --volume <volume>
                                                     <volume-snapshot-name>
```

### Positional arguments:

**\<volume-snapshot-name\>**  
Volume snapshot name

### Optional arguments:

**--description \<description\>**  
Volume snapshot description

**--volume \<volume\>**  
Volume ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume snapshot delete

Delete a compute volume snapshot.

```
usage: vinfra service compute volume snapshot delete [--wait] [--timeout <seconds>]
                                                     <volume-snapshot>
```

### Positional arguments:

**\<volume-snapshot\>**  
Volume snapshot ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume snapshot list

List compute volume snapshots.

```
usage: vinfra service compute volume snapshot list [--long] [--volume <volume>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--volume \<volume\>**  
Volume ID or name

---

## vinfra service compute volume snapshot reset-state

Reset the state of a compute volume snapshot.

```
usage: vinfra service compute volume snapshot reset-state [--wait] [--timeout <seconds>]
                                                          <volume-snapshot>
```

### Positional arguments:

**\<volume-snapshot\>**  
Volume snapshot ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume snapshot revert

Revert a compute volume to a snapshot.

```
usage: vinfra service compute volume snapshot revert [--wait] [--timeout <seconds>]
                                                     <volume-snapshot>
```

### Positional arguments:

**\<volume-snapshot\>**  
Volume snapshot ID or name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume snapshot set

Modify a volume snapshot.

```
usage: vinfra service compute volume snapshot set [--description <description>]
                                                  [--name <name>] <volume-snapshot>
```

### Positional arguments:

**\<volume-snapshot\>**  
Volume snapshot ID or name

### Optional arguments:

**--description \<description\>**  
Volume snapshot description

**--name \<name\>**  
A new name for the volume snapshot

---

## vinfra service compute volume snapshot show

Show details of a compute volume snapshot.

```
usage: vinfra service compute volume snapshot show <volume-snapshot>
```

### Positional arguments:

**\<volume-snapshot\>**  
Volume snapshot ID or name

---

## vinfra service compute volume snapshot upload-to-image

Create a compute image from a compute volume snapshot.

```
usage: vinfra service compute volume snapshot upload-to-image [--wait] [--timeout <seconds>]
                                                              [--name <name>] <volume-snapshot>
```

### Positional arguments:

**\<volume-snapshot\>**  
Volume snapshot ID or name

### Optional arguments:

**--name \<name\>**  
Image name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute volume upload-to-image

Create a compute image from a compute volume.

```
usage: vinfra service compute volume upload-to-image [--wait] [--timeout <seconds>]
                                                     [--name <name>] <volume>
```

### Positional arguments:

**\<volume\>**  
Volume ID or name

### Optional arguments:

**--name \<name\>**  
Image name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service compute vpn connection create

Create a compute VPN connection.

```
usage: vinfra service compute vpn connection create [--peer-id <peer-id>] [--local-id <local-id>]
                                                    [--dpd action=<action>,interval=<seconds>,timeout=<seconds>]
                                                    --peer-address <peer-address> --psk <psk>
                                                    --local-endpoint-group <id|name=<name>,value=<subnet>,...>
                                                    --peer-endpoint-group <id|name=<name>,value=<cidr>,...>
                                                    --ikepolicy <id|name=<name>[,auth-algorithm=<algorithm>,encryption-algorithm=<algorithm>,pfs=<pfs>,lifetime=<seconds>,ike-version=<ver>]>
                                                    --ipsecpolicy <id|name=<name>[,auth-algorithm=<algorithm>,encryption-algorithm=<algorithm>,pfs=<pfs>,lifetime=<seconds>]>
                                                    --router <router><connection-name>
```

### Positional arguments:

**\<connection-name\>**  
Name of the VPN connection

### Optional arguments:

**--peer-id \<peer-id\>**  
Peer router identifier for authentication

**--local-id \<local-id\>**  
Local router identifier for authentication

**--dpd action=\<action\>,interval=\<seconds\>,timeout=\<seconds\>**  
Dead Peer Detection attributes:  
**action={hold,clear,disabled,restart}**: defines the action to take if the remote peer unexpectedly closes;  
**interval=\<seconds\>**: defines the time interval with which messages are sent to the peer;  
**timeout=\<seconds\>**: defines the timeout interval, after which connection to a peer is considered down.

**--peer-address \<peer-address\>**  
Peer gateway public IPv4/IPv6 address or FQDN

**--psk \<psk\>**  
Pre-shared key string

**--local-endpoint-group \<id|name=\<name\>,value=\<subnet\>,...\>**  
Local endpoint group parameters:  
**id=\<id\>**: local endpoint group ID or name;  
**name=\<name\>**: local endpoint group name;  
**value=\<subnet\>**: subnet ID (option can be repeated).

**--peer-endpoint-group \<id|name=\<name\>,value=\<cidr\>,...\>**  
Remote endpoint group parameters:  
**id=\<id\>**: remote endpoint group ID or name;  
**name=\<name\>**: remote endpoint group name;  
**value=\<cidr\>**: IP range in CIDR notation (option can be repeated).

**--ikepolicy \<id|name=\<name\>[,auth-algorithm=\<algorithm\>,encryption-algorithm=\<algorithm\>,pfs=\<pfs\>,lifetime=\<seconds\>,ike-version=\<ver\>]\>**  
IKE policy parameters:  
**id=\<id\>**: IKE policy ID or name;  
**name=\<name\>**: IKE policy name;  
**auth-algorithm={sha1,sha256,sha384,sha512}**: IKE policy authentication algorithm;  
**encryption-algorithm={aes-128,3des,aes-192,aes-256}**: IKE policy encryption algorithm;  
**pfs={group5,group2,group14}**: IKE Diffie-Hellman group;  
**lifetime=\<seconds\>**: IKE policy lifetime;  
**ike-version={v1,v2}**: IKE version.

**--ipsecpolicy \<id|name=\<name\>[,auth-algorithm=\<algorithm\>,encryption-algorithm=\<algorithm\>,pfs=\<pfs\>,lifetime=\<seconds\>]\>**  
IPsec policy parameters:  
**id=\<id\>**: IPsec policy ID or name;  
**name=\<name\>**: IPsec policy name;  
**auth-algorithm={sha1,sha256,sha384,sha512}**: IPsec policy authentication algorithm;  
**encryption-algorithm={aes-128,3des,aes-192,aes-256}**: IPsec policy encryption algorithm;  
**pfs={group5,group2,group14}**: IPsec Diffie-Hellman group;  
**lifetime=\<seconds\>**: IPsec policy lifetime.

**--router \<router\>**  
Router ID or name

---

## vinfra service compute vpn connection delete

Delete a compute VPN connection.

```
usage: vinfra service compute vpn connection delete <connection>
```

### Positional arguments:

**\<connection\>**  
VPN connection name or ID

---

## vinfra service compute vpn connection list

List compute VPN connections.

```
usage: vinfra service compute vpn connection list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute vpn connection restart

Reset a compute VPN connection.

```
usage: vinfra service compute vpn connection restart <connection>
```

### Positional arguments:

**\<connection\>**  
VPN connection name or ID

---

## vinfra service compute vpn connection set

Modify a compute VPN connection.

```
usage: vinfra service compute vpn connection set [--peer-id <peer-id>] [--local-id <local-id>]
                                                 [--dpd action=<action>,interval=<seconds>,timeout=<seconds>]
                                                 [--peer-address <peer-address>] [--psk <psk>]
                                                 [--local-endpoint-group <id|name=<name>,value=<subnet>,...>]
                                                 [--peer-endpoint-group <id|name=<name>,value=<cidr>,...>]
                                                 [--name <name>] <connection>
```

### Positional arguments:

**\<connection\>**  
VPN connection name or ID

### Optional arguments:

**--peer-id \<peer-id\>**  
Peer router identifier for authentication

**--local-id \<local-id\>**  
Local router identifier for authentication

**--dpd action=\<action\>,interval=\<seconds\>,timeout=\<seconds\>**  
Dead Peer Detection attributes:  
**action={hold,clear,disabled,restart}**: defines the action to take if the remote peer unexpectedly closes;  
**interval=\<seconds\>**: defines the time interval with which messages are sent to the peer;  
**timeout=\<seconds\>**: defines the timeout interval, after which connection to a peer is considered down.

**--peer-address \<peer-address\>**  
Peer gateway public IPv4/IPv6 address or FQDN

**--psk \<psk\>**  
Pre-shared key string

**--local-endpoint-group \<id|name=\<name\>,value=\<subnet\>,...\>**  
Local endpoint group parameters:  
**id=\<id\>**: local endpoint group ID or name;  
**name=\<name\>**: local endpoint group name;  
**value=\<subnet\>**: subnet ID (option can be repeated).

**--peer-endpoint-group \<id|name=\<name\>,value=\<cidr\>,...\>**  
Remote endpoint group parameters:  
**id=\<id\>**: remote endpoint group ID or name;  
**name=\<name\>**: remote endpoint group name;  
**value=\<cidr\>**: IP range in CIDR notation (option can be repeated).

**--name \<name\>**  
A new name for the VPN connection

---

## vinfra service compute vpn connection show

Display compute VPN connection details.

```
usage: vinfra service compute vpn connection show <connection>
```

### Positional arguments:

**\<connection\>**  
VPN connection name or ID

---

## vinfra service compute vpn endpoint-group list

List compute VPN endpoint groups.

```
usage: vinfra service compute vpn endpoint-group list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute vpn endpoint-group show

Display compute VPN endpoint group details.

```
usage: vinfra service compute vpn endpoint-group show <endpoint-group>
```

### Positional arguments:

**\<endpoint-group\>**  
Endpoint group ID or name

---

## vinfra service compute vpn ike-policy list

List compute VPN IKE policies.

```
usage: vinfra service compute vpn ike-policy list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute vpn ike-policy show

Display compute VPN IKE policy details.

```
usage: vinfra service compute vpn ike-policy show <ike-policy>
```

### Positional arguments:

**\<ike-policy\>**  
IKE policy ID or name

---

## vinfra service compute vpn ipsec-policy list

List compute VPN IPsec policies.

```
usage: vinfra service compute vpn ipsec-policy list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service compute vpn ipsec-policy show

Display compute VPN IPsec policy details.

```
usage: vinfra service compute vpn ipsec-policy show <ipsec-policy>
```

### Positional arguments:

**\<ipsec-policy\>**  
IPsec policy ID or name

---

## vinfra service nfs cluster create

Create the NFS cluster.

```
usage: vinfra service nfs cluster create [--wait] [--timeout <seconds>]
                                         [--tier {0,1,2,3}]
                                         [--replicas <norm> | --encoding <M>+<N>]
                                         [--failure-domain {0,1,2,3,4}]
                                         --nodes <node>[:<ip_address>]
```

### Optional arguments:

**--tier {0,1,2,3}**  
Storage tier (default: 0)

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain (default: 1)

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain (default: 0)

**--nodes \<node\>[:\<ip_address\>]**  
A comma-separated list of node hostnames or IDs

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs cluster delete

Delete the NFS cluster.

```
usage: vinfra service nfs cluster delete [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs export create

Create a new NFS export.

```
usage: vinfra service nfs export create [--wait] [--timeout <seconds>]
                                        --path <path> --access-type <access-type>
                                        --security-types <security-types>
                                        [--client <address=ip_addresses:access=access_type:security=security_types>]
                                        [--squash <squash>] [--anonymous-gid <anonymous-gid>]
                                        [--anonymous-uid <anonymous-uid>] <share-name> <export-name>
```

### Positional arguments:

**\<share-name\>**  
NFS share name

**\<export-name\>**  
NFS export name

### Optional arguments:

**--path \<path\>**  
Path to the NFS export

**--access-type \<access-type\>**  
Type of access to the NFS export ('none', 'rw', or 'ro')

**--security-types \<security-types\>**  
Types of NFS export security ('none', 'sys', 'krb5', 'krb5i', or 'krb5p')

**--client \<address=ip_addresses:access=access_type:security=security_types\>**  
Client access list of the NFS export

**--squash \<squash\>**  
NFS export squash ('root_squash', 'root_id_squash', 'all_squash', or 'none')

**--anonymous-gid \<anonymous-gid\>**  
Anonymous GID of the NFS export

**--anonymous-uid \<anonymous-uid\>**  
Anonymous UID of the NFS export

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs export delete

Delete an NFS export.

```
usage: vinfra service nfs export delete [--wait] [--timeout <seconds>]
                                        <share-name> <export-name>
```

### Positional arguments:

**\<share-name\>**  
NFS share name

**\<export-name\>**  
NFS export name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs export list

List NFS exports.

```
usage: vinfra service nfs export list [--long] [--share-name <share-name>]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

**--share-name \<share-name\>**  
NFS share name

---

## vinfra service nfs export set

Modify an NFS export.

```
usage: vinfra service nfs export set [--wait] [--timeout <seconds>]
                                     [--path <path>] [--access-type <access-type>]
                                     [--security-types <security-types>]
                                     [--client <address=ip_addresses:access=access_type:security=security_types>]
                                     [--squash <squash>] [--anonymous-gid <anonymous-gid>]
                                     [--anonymous-uid <anonymous-uid>] <share-name> <export-name>
```

### Positional arguments:

**\<share-name\>**  
NFS share name

**\<export-name\>**  
NFS export name

### Optional arguments:

**--path \<path\>**  
Path to the NFS export

**--access-type \<access-type\>**  
Type of access to the NFS export ('none', 'rw', or 'ro')

**--security-types \<security-types\>**  
Types of NFS export security ('none', 'sys', 'krb5', 'krb5i', or 'krb5p')

**--client \<address=ip_addresses:access=access_type:security=security_types\>**  
Client access list of the NFS export

**--squash \<squash\>**  
NFS export squash ('root_squash', 'root_id_squash', 'all_squash', or 'none')

**--anonymous-gid \<anonymous-gid\>**  
Anonymous GID of the NFS export

**--anonymous-uid \<anonymous-uid\>**  
Anonymous UID of the NFS export

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs export show

Show details of an NFS export.

```
usage: vinfra service nfs export show <share-name> <export-name>
```

### Positional arguments:

**\<share-name\>**  
NFS share name

**\<export-name\>**  
NFS export name

---

## vinfra service nfs kerberos settings set

Set Kerberos authentication settings.

```
usage: vinfra service nfs kerberos settings set --realm REALM --kdc-service KDC_SERVICE
                                                --kdc-admin-service KDC_ADMIN_SERVICE
```

### Optional arguments:

**--realm REALM**  
Realm name in uppercase letters

**--kdc-service KDC_SERVICE**  
DNS name or IP address of the KDC service

**--kdc-admin-service KDC_ADMIN_SERVICE**  
DNS name or IP address of the KDC administration service

---

## vinfra service nfs kerberos settings show

Get Kerberos authentication settings.

```
usage: vinfra service nfs kerberos settings show
```

---

## vinfra service nfs node add

Add one or more nodes to the NFS cluster.

```
usage: vinfra service nfs node add [--wait] [--timeout <seconds>]
                                   --nodes <node>[:<ip_address>]
```

### Optional arguments:

**--nodes \<node\>[:\<ip_address\>]**  
A comma-separated list of node hostnames or IDs

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs node list

List NFS cluster nodes.

```
usage: vinfra service nfs node list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service nfs node release

Release one or more nodes from the NFS cluster.

```
usage: vinfra service nfs node release [--wait] [--timeout <seconds>]
                                       --nodes <nodes>
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs share create

Create an NFS share.

```
usage: vinfra service nfs share create [--wait] [--timeout <seconds>]
                                       --node <node> --ip-address <ip_address>
                                       --size <size> --tier {0,1,2,3}
                                       (--replicas <norm> | --encoding <M>+<N>)
                                       --failure-domain {0,1,2,3,4}
                                       [--krb-keytab <krb-keytab>] <name>
```

### Positional arguments:

**\<name\>**  
NFS share name

### Optional arguments:

**--node \<node\>**  
Node ID

**--ip-address \<ip_address\>**  
IP address of the NFS share

**--size \<size\>**  
NFS share size, in bytes. You can also specify the following units: KiB for kibibytes, MiB for mebibytes, GiB for gibibytes, TiB for tebibytes, and PiB for pebibytes.

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--krb-keytab \<krb-keytab\>**  
Kerberos keytab file

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs share delete

Delete an NFS share.

```
usage: vinfra service nfs share delete [--wait] [--timeout <seconds>]
                                       <name>
```

### Positional arguments:

**\<name\>**  
NFS share name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs share list

List NFS shares.

```
usage: vinfra service nfs share list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service nfs share set

Modify an NFS share.

```
usage: vinfra service nfs share set [--wait] [--timeout <seconds>]
                                    [--tier {0,1,2,3}] [--replicas <norm> | --encoding <M>+<N>]
                                    [--failure-domain {0,1,2,3,4}] [--size <size>]
                                    [--krb-keytab <krb-keytab>] [--krb-auth <krb-auth>]
                                    [--ip-address <ip_address>] <name>
```

### Positional arguments:

**\<name\>**  
NFS share name

### Optional arguments:

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--size \<size\>**  
NFS share size, in bytes. You can also specify the following units: KiB for kibibytes, MiB for mebibytes, GiB for gibibytes, TiB for tebibytes, and PiB for pebibytes.

**--krb-keytab \<krb-keytab\>**  
Kerberos keytab file

**--krb-auth \<krb-auth\>**  
Whether or not Kerberos authentication is enabled ('true' or 'false')

**--ip-address \<ip_address\>**  
IP address of the NFS share

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs share show

Show details of an NFS share.

```
usage: vinfra service nfs share show <name>
```

### Positional arguments:

**\<name\>**  
NFS share name

---

## vinfra service nfs share start

Start an NFS share.

```
usage: vinfra service nfs share start [--wait] [--timeout <seconds>]
                                      <name>
```

### Positional arguments:

**\<name\>**  
NFS share name

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service nfs share stop

Stop an NFS share.

```
usage: vinfra service nfs share stop [--wait] [--timeout <seconds>]
                                     [--force] <name>
```

### Positional arguments:

**\<name\>**  
NFS share name

### Optional arguments:

**--force**  
Stop the NFS share forcibly.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 cluster change

Change the S3 cluster.

```
usage: vinfra service s3 cluster change [--wait] [--timeout <seconds>]
                                        [--tier {0,1,2,3}]
                                        [--replicas <norm> | --encoding <M>+<N>]
                                        [--failure-domain {0,1,2,3,4}]
                                        [--self-signed | --no-ssl | --cert-file <cert_file>]
                                        [--insecure] [--key-file <key_file>]
                                        [--password] [--np-uri <np-uri>]
                                        [--np-user-key <np-user-key>]
```

### Optional arguments:

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--self-signed**  
Generate a new self-signed certificate (default).

**--no-ssl**  
Do not generate a self-signed certificate.

**--cert-file \<cert_file\>**  
Path to a file with the new certificate

**--insecure**  
Allow insecure connections in addition to secure ones (only used with the `--cert-file` and `--self-signed` options).

**--key-file \<key_file\>**  
Path to a file with the private key (only used with the `--cert-file` option)

**--password**  
Read certificate password from stdin (only used with the `--cert-file` option).

**--np-uri \<np-uri\>**  
Notary provider address (only used with `--cert-file` or `--self-signed` and `--np-user-key` option)

**--np-user-key \<np-user-key\>**  
Notary user key (only used with `--np-uri` option)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 cluster create

Create the S3 cluster.

```
usage: vinfra service s3 cluster create [--wait] [--timeout <seconds>]
                                        [--tier {0,1,2,3}]
                                        [--replicas <norm> | --encoding <M>+<N>]
                                        [--failure-domain {0,1,2,3,4}]
                                        [--self-signed | --no-ssl | --cert-file <cert_file>]
                                        [--insecure] [--key-file <key_file>]
                                        [--password] [--np-uri <np-uri>]
                                        [--np-user-key <np-user-key>]
                                        --nodes <nodes> --s3gw-domain <domain>
                                        [--os-count <os_count>]
                                        [--ns-count <ns_count>] [--force]
```

### Optional arguments:

**--tier {0,1,2,3}**  
Storage tier

**--replicas \<norm\>**  
Storage replication mapping in the format:  
**norm**: the number of replicas to maintain.

**--encoding \<M\>+\<N\>**  
Storage erasure encoding mapping in the format:  
**M**: the number of data blocks;  
**N**: the number of parity blocks.

**--failure-domain {0,1,2,3,4}**  
Storage failure domain

**--self-signed**  
Generate a new self-signed certificate (default).

**--no-ssl**  
Do not generate a self-signed certificate.

**--cert-file \<cert_file\>**  
Path to a file with the new certificate

**--insecure**  
Allow insecure connections in addition to secure ones (only used with the `--cert-file` and `--self-signed` options).

**--key-file \<key_file\>**  
Path to a file with the private key (only used with the `--cert-file` option)

**--password**  
Read certificate password from stdin (only used with the `--cert-file` option).

**--np-uri \<np-uri\>**  
Notary provider address (only used with `--cert-file` or `--self-signed` and `--np-user-key` option)

**--np-user-key \<np-user-key\>**  
Notary user key (only used with `--np-uri` option)

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

**--s3gw-domain \<domain\>**  
DNS name S3 endpoint

**--os-count \<os_count\>**  
Amount of OS services in S3 cluster

**--ns-count \<ns_count\>**  
Amount of NS services in S3 cluster

**--force**  
Skip checks for minimal hardware requirements.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 cluster delete

Delete the S3 cluster.

```
usage: vinfra service s3 cluster delete [--wait] [--timeout <seconds>]
                                        [--force]
```

### Optional arguments:

**--force**  
Forcibly delete the S3 cluster.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 node add

Add one or more nodes to the S3 cluster.

```
usage: vinfra service s3 node add [--wait] [--timeout <seconds>]
                                  --nodes <nodes> [--force]
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

**--force**  
Skip checks for minimal hardware requirements.

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 node release

Release one or more nodes from the S3 cluster.

```
usage: vinfra service s3 node release [--wait] [--timeout <seconds>]
                                      --nodes <nodes>
```

### Optional arguments:

**--nodes \<nodes\>**  
A comma-separated list of node hostnames or IDs

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 replication add

Add S3 geo-replication site.

```
usage: vinfra service s3 replication add [--wait] [--timeout <seconds>]
                                         --token <site_token>
```

### Optional arguments:

**--token \<site_token\>**  
Remote S3 site token

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 replication delete

Delete S3 geo-replication site by ID.

```
usage: vinfra service s3 replication delete [--wait] [--timeout <seconds>]
                                            --id <site_id>
```

### Optional arguments:

**--id \<site_id\>**  
S3 site UID

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra service s3 replication list

List registered site for S3 geo-replication.

```
usage: vinfra service s3 replication list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra service s3 replication show

Show details about registered site for S3 geo-replication or self site.

```
usage: vinfra service s3 replication show [--id <site_id>]
```

### Optional arguments:

**--id \<site_id\>**  
S3 site UID

---

## vinfra service s3 replication show token

Get S3 geo-replication token.

```
usage: vinfra service s3 replication show token
```

---

## vinfra service s3 show

Show S3 cluster configuration.

```
usage: vinfra service s3 show
```

---

## vinfra software-updates cancel

Cancel software updates.

```
usage: vinfra software-updates cancel [--wait] [--timeout <seconds>]
                                      [--maintenance-mode {exit,exit-keep-resources,hold}]
```

### Optional arguments:

**--maintenance-mode {exit,exit-keep-resources,hold}**  
Maintenance mode: exit, exit-keep-resources, hold (default: exit-keep-resources)

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra software-updates check-for-updates

Check for software updates.

```
usage: vinfra software-updates check-for-updates [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra software-updates download

Download software updates.

```
usage: vinfra software-updates download [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra software-updates eligibility-check

Check nodes' update eligibility.

```
usage: vinfra software-updates eligibility-check [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra software-updates pause

Pause software updates.

```
usage: vinfra software-updates pause [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra software-updates resume

Resume the software update procedure.

```
usage: vinfra software-updates resume [--wait] [--timeout <seconds>]
```

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra software-updates start

Start the software update procedure.

```
usage: vinfra software-updates start [--wait] [--timeout <seconds>]
                                     [--maintenance <enabled=enabled[,key1=value1,key2=value2...]>]
                                     [--mode {stop,skip,force,no_maintenance}]
                                     [--accept-eula] [--nodes <nodes>] [--skip-control-plane]
```

### Optional arguments:

**--maintenance \<enabled=enabled[,key1=value1,key2=value2...]\>**  
Specify maintenance parameters:  
**enabled**: enter maintenance during the upgrade ('yes' or 'no');  
**on-fail**: choose how to proceed with the update if maintenance fails ('stop', 'skip' or 'force');  
**compute-mode**: choose how to proceed with the update if a VM cannot be live migrated ('strict', 'ignore' or 'ignore_ext').

**--mode {stop,skip,force,no_maintenance}**  
Update mode: stop, skip, force, no_maintenance (default: stop) (DEPRECATED)

**--accept-eula**  
Accept EULA

**--nodes \<nodes\>**  
A comma-separated list of node IDs or hostnames

**--skip-control-plane**  
Skip Control plane upgrade

### Command run options:

Additional command options

**--wait**  
Wait for the operation to complete (synchronous mode).

**--timeout \<seconds\>**  
A timeout for the operation to complete if `--wait` is specified, in seconds (default: 600)

---

## vinfra software-updates status

Show software updates status.

```
usage: vinfra software-updates status
```

---

## vinfra task list

List tasks.

```
usage: vinfra task list [--long]
```

### Optional arguments:

**--long**  
Enable access and listing of all fields of objects.

---

## vinfra task show

Show task details.

```
usage: vinfra task show [--debug] <task>
```

### Positional arguments:

**\<task\>**  
Task ID

### Optional arguments:

**--debug**  
Show all task fields (for debug only).

---

## vinfra task wait

Wait for the task to complete.

```
usage: vinfra task wait [--timeout <seconds>] <task_id>
```

### Positional arguments:

**\<task_id\>**  
Task ID

### Optional arguments:

**--timeout \<seconds\>**  
A timeout for the task to complete, in seconds (default: 600)