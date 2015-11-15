# coding: utf-8

import asyncio

from client import Client
from commands.join import JoinCommand
from commands.nick import NickCommand
from commands.user import UserCommand
from message import Message
from config import *
from channel import Channel
from numeric_replies import *


class IrcServer:
    clients = {}
    channels = {}

    async def irc_server(self):
        await asyncio.start_server(self.handle_connection, SERVER, PORT)

    async def handle_connection(self, reader, writer):
        while True:
            data = await reader.read(8192)
            for command in data.decode('utf-8').rstrip().split('\r\n'):
                self.run_command(command, writer)

    def run_command(self, command, writer):
        command_name = command.split(' ')[0].lower()
        if command_name in COMMANDS:
            return self._get_command(command_name)(command, writer)

        else:
            writer.write(err_unknowncommand())

    def _get_command(self, command_name):
        command = getattr(self, command_name)
        return command

    def nick(self, command, writer):
        NickCommand(self.clients, command, writer).run_command()

    def user(self, command, writer):
        UserCommand(self.clients, command, writer).run_command()

    def join(self, command, writer):
        JoinCommand(self.clients, self.channels, command, writer)

    def privmsg(self, data, writer):
        # :Guest53954!~test3@122.96.145.130 PRIVMSG #ubuntu :exit
        # TODO Обработка ошибок
        # отправляем всем, остальным людям в канале
        client = self.clients[writer]
        args, msg_body = data.split(':')
        command, channel_name = args.rstrip().split(' ')
        channel = self.channels[channel_name]

        # TODO проверка наличия указанного канала
        prefix = '{}!{}'.format(client.nick, SERVER)
        for ch_client in channel.clients:
            if ch_client != client:
                ch_client.send(Message(prefix, 'PRIVMSG', str(channel), msg_body))
                
    def quit(self, data, writer):
        client = self.clients[writer]
        for ch in client.channels:
            client.send(Message(SERVER, 'PART', ch.name, "I'm out"))
        del self.clients[writer]


server = IrcServer()
loop = asyncio.get_event_loop()
loop.run_until_complete(server.irc_server())
try:
    loop.run_forever()
finally:
    loop.close()
