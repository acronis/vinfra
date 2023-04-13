from vinfra.api import base


class AuditLog(base.Resource):
    pass


class AuditLogManager(base.Manager):
    resource_class = AuditLog

    def list(self):
        return self._list('/audit_log')
