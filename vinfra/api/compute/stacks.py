from vinfra.api import base
from vinfra.api.compute import base as compute_base


class Stack(base.Resource):

    NAME_ATTR = "stack_name"

    def delete(self):
        return self.manager.delete(self)

    def get_resources(self):
        return self.manager.get_resources(self)


class StackManager(compute_base.Manager):

    resource_class = Stack
    base_url = "/compute/stacks"

    def create(self, name, template, params):
        payload = {
            "stack_name": name,
            "template_name": template,
            "params": params
        }
        return self.client.post(self.base_url, json=payload)

    def delete(self, stack):
        url = "{}/{}/".format(self.base_url, stack.id)
        return self._delete(url)

    def list(self):
        return self._list(self.base_url)

    def get(self, stack):
        url = "{}/{}/".format(self.base_url, stack.id)
        return self._get(url)


class StackResourcesManager(compute_base.VinfraApi):

    base_url = "/compute/stacks"

    def get_resources(self, stack):
        url = "{}/{}/resources/".format(self.base_url, stack.id)
        return self.client.get(url)


class StackTemplateManager(compute_base.VinfraApi):

    base_url = "/compute/stacks/templates"

    def get_template_parameters(self, template_name):
        url = "{}/{}/parameters/".format(self.base_url, template_name)
        return self.client.get(url)
