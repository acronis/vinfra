from requests.exceptions import HTTPError

from vinfra.api.domains.users import ProjectRole, ServiceRole
from vinfraclient.utils import find_resource


def find_domain(client, domain):
    try:
        return find_resource(client.domains, domain)
    except HTTPError as err:
        if err.response.status_code == 403:
            # user don't have access to full list of domains
            # but it probably have access to some domains,
            # so it can find them in user domains list
            return find_resource(client.user_domains, domain)
        raise


def parse_unassigned_projects(domain, unassigned_projects):
    res = []
    if unassigned_projects is None:
        return res

    for project in unassigned_projects:
        project = find_resource(domain.projects_manager, project)
        res.append(ProjectRole(project, None))

    return res


def parse_assigned_projects(domain, assigned_projects):
    res = []
    if assigned_projects is None:
        return res

    for project, role in assigned_projects:
        project = find_resource(domain.projects_manager, project)
        res.append(ProjectRole(project, role))

    return res


def parse_assigned_domains(
        domain_manager, assigned_domains, unassigned_domains=None):
    if assigned_domains is None and unassigned_domains is None:
        return None

    res = []
    for domain, roles in assigned_domains or []:
        domain = find_resource(domain_manager, domain)
        res.append(ServiceRole(domain, roles.split(',')))
    for domain in unassigned_domains or []:
        domain = find_resource(domain_manager, domain)
        res.append(ServiceRole(domain, []))

    return res
