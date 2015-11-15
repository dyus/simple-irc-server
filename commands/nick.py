# coding: utf-8
"""
пример команды: NICK nickname
"""

from client import Client
from commands.base import BaseCommand
from numeric_replies import err_nonicknamegiven, err_erroneusnickname, err_nicknameinuse


class NickCommand(BaseCommand):
    def __init__(self, clients, writer, command):
        self.clients = clients
        self.writer = writer
        self.command = command
        self.nick = None

    def parse_command(self):
        args = self.command.split(' ')
        if args:
            self.nick = args[1]

    def validate_nick(self):
        if not self.nick:
            return err_nonicknamegiven()
        if len(self.nick) > 9:
            return err_erroneusnickname(self.nick)
        if self.nick in self.clients:
            return err_nicknameinuse(self.nick)

    def run_command(self):
        self.parse_command()

        validate_error = self.validate_nick()
        if validate_error is not None:
            self.writer.write(bytes(validate_error))
        else:
            self.clients[self.writer] = Client(self.writer, self.nick)

