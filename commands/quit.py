# coding: utf-8
"""
пример команды QUIT message
               QUIT :I'm out
"""
from commands.base import BaseCommand
from config import SERVER
from message import Message


class QuitCommand(BaseCommand):
    def __init__(self, clients, command, writer):
        self.clients = clients
        self.command = command
        self.writer = writer
        self.message = ''

    def parse_command(self):
        args = self.command.split(' ')
        self.concat_after_colon(args)
        if len(args) == 2:
            self.message = args[1]

    def validate(self):
        pass

    def run_command(self):
        self.parse_command()

        client = self.clients[self.writer]
        for ch in client.channels:
            client.send(Message(SERVER, 'PART', ch.name, self.message))

            ch.clients.remove(client)
            for ch_client in ch.clients:
                self.update_channel_users_messages(ch, ch_client)

        del self.clients[self.writer]
