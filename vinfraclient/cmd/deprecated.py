from vinfraclient.cmd.node import iface
from vinfraclient.cmd.compute import cluster
from vinfraclient.cmd import abgw


class CreateBond(iface.CreateBond):
    deprecated = True
    deprecated_reason = "Please use 'node iface create-bond' command."


class DeleteBond(iface.DeleteBond):
    deprecated = True
    deprecated_reason = "Please use 'node iface delete' command."


class DeleteIface(iface.DeleteIface):
    deprecated = True
    deprecated_reason = "Please use 'node iface delete' command."


class DownIface(iface.DownIface):
    deprecated = True
    deprecated_reason = "Please use 'node iface down' command."


class ListIface(iface.ListIface):
    deprecated = True
    deprecated_reason = "Please use 'node iface list' command."


class ShowIface(iface.ShowIface):
    deprecated = True
    deprecated_reason = "Please use 'node iface show' command."


class SetIface(iface.SetIface):
    deprecated = True
    deprecated_reason = "Please use 'node iface set' command."


class UpIface(iface.UpIface):
    deprecated = True
    deprecated_reason = "Please use 'node iface up' command."


class CreateVlan(iface.CreateVlan):
    deprecated = True
    deprecated_reason = "Please use 'node iface create-vlan' command."


class DeleteVlan(iface.DeleteVlan):
    deprecated = True
    deprecated_reason = "Please use 'node iface delete' command."


class CreateCompute(cluster.CreateCompute):
    deprecated = True
    deprecated_reason = "Please use 'service compute create' command."


class DeleteCompute(cluster.DeleteCompute):
    deprecated = True
    deprecated_reason = "Please use 'service compute delete' command."


class SetCompute(cluster.SetCompute):
    deprecated = True
    deprecated_reason = "Please use 'service compute set' command."


class ShowCompute(cluster.ShowCompute):
    deprecated = True
    deprecated_reason = "Please use 'service compute show' command."


class ClusterStat(cluster.ClusterStat):
    deprecated = True
    deprecated_reason = "Please use 'service compute stat' command."


class RenewBackupCertificates(abgw.RenewBackupCertificates):
    deprecated = True
    deprecated_reason = "Please use 'service backup registration renew-certificates' command."
