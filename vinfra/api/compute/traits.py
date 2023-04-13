from vinfra.api import base
from vinfra.utils import flatten_args


class Trait(base.Resource):
    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)

    def assign(self, *args, **params):
        return self.manager.assign(self, *args, **params)

    def delete_assign(self, *args, **params):
        return self.manager.delete_assign(self, *args, **params)


class TraitManager(base.Manager):
    resource_class = Trait
    base_url = "/compute/traits"

    def list(self):
        return self._list(self.base_url)

    def get(self, trait):
        return self._get("{}/{}".format(self.base_url, base.get_id(trait)))

    def create(self, name, description=None, nodes=None, images=None,
               flavors=None, isolated=None):
        json = dict(
            name=name
        )
        json.update(
            flatten_args(
                description=description,
                nodes=[base.get_id(node) for node in nodes or []],
                images=[base.get_id(image) for image in images or []],
                flavors=[base.get_id(flavor) for flavor in flavors or []],
                isolated=isolated,
            )
        )
        return self._post(self.base_url, json)

    def update(self, trait, name=None, description=None, isolated=None):
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if isolated is not None:
            data['isolated'] = isolated

        url = "{}/{}".format(self.base_url, base.get_id(trait))
        return self._patch(url, json=data)

    def delete(self, trait):
        return self._delete("{}/{}".format(self.base_url, base.get_id(trait)))

    def assign(self, trait, kind, resources):
        data = {kind: [base.get_id(res) for res in resources]}
        url = "{}/{}/{}".format(self.base_url, base.get_id(trait), kind)
        self._put(url, json=data)

    def delete_assign(self, trait, kind, resource):
        resource_id = base.get_id(resource)
        self._delete(
            "{}/{}/{}/{}".format(
                self.base_url, base.get_id(trait), kind, resource_id
            )
        )
