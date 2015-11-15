# coding: utf-8


class Client(object):
    def __init__(self, writer, nick):
        self.nick = nick
        self.writer = writer
        self.channels = []

    def send(self, message):
        self.writer.write(bytes(message))
