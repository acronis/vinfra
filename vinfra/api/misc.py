class Dns(object):
    def __init__(self, api):
        self.api = api

    def get(self):
        return self.api.client.get("/dns")

    def update(self, nameservers):
        json = {'nameservers': nameservers}
        return self.api.client.put("/dns", json=json)
