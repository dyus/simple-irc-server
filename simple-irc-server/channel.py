# coding: utf-8


class Channel:
    def __init__(self, name, client):
        self.clients = [client, ]
        self.name = name

    def __str__(self):
        return self.name
