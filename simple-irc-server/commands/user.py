# coding: utf-8
"""
пример команды: USER nickname 0 * :Ivan Petrov
"""
from client import Client
from commands.base import BaseCommand
from config import SERVER, COMMANDS, START_TIME
from message import Message
from numeric_replies import err_needmoreparams, err_nosuchnick


class UserCommand(BaseCommand):
    def __init__(self, clients, command, writer):
        self.clients = clients
        self.command = command
        self.writer = writer
        self.nick = None

    def parse_command(self):
        args = self.command.split(' ')

        self.concat_after_colon(args)
        if len(args) == 5:
            self.nick = args[1]

    def validate(self):
        if self.nick is None:
            return err_needmoreparams(self.command)

        nicks = [c.nick for c in self.clients.values()]
        if self.nick not in nicks:
            return err_nosuchnick(self.nick)

    def run_command(self):
        self.parse_command()

        validation_error = self.validate()
        if validation_error:
            self.writer.write(bytes(validation_error))
            return

        client = Client(self.writer, self.nick)
        self.clients[self.writer] = client
        self.welcome_messages(self.clients[self.writer])

    @staticmethod
    def welcome_messages(client):
        client.send(Message(SERVER, '001', client.nick, 'Welcome to the Internet Relay Network'))
        client.send(Message(SERVER, '002', client.nick, 'Your host is running on test irc server'))
        client.send(Message(SERVER, '003', client.nick, 'This server was created at {}'.format(START_TIME)))
        client.send(Message(SERVER, '004', client.nick, 'Available commands: {}'.format(' '.join(COMMANDS))))
