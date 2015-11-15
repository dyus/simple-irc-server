# coding: utf-8

import asyncio

from client import Client
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

    def run_command(self, data, writer):
        command = data.split(' ')[0].lower()
        if command in COMMANDS:
            return self._get_command(command)(data, writer)

        else:
            writer.write(err_unknowncommand())

    def _get_command(self, command):
        command = getattr(self, command)
        return command

    def nick(self, data, writer):
        NickCommand(self.clients, writer, data).run_command()

    def user(self, data, writer):
        UserCommand(self.clients, writer, data).run_command()

    def quit(self, data, writer):
        client = self.clients[writer]
        for ch in client.channels:
            client.send(Message(SERVER, 'PART', ch.name, "I'm out"))
        del self.clients[writer]

    def join(self, data, writer):
        # TODO пройтись еще раз убедиться что все сообщения соответсвуют формату ирк протокола
        # TODO при добавлении нового нужно отсылать сообщение с пересчетом списка всем участникам канала
        client = self.clients[writer]

        args = data.split(' ')
        if len(args) > 1:
            channel_names = args[1:]
            for channel_name in channel_names:
                if channel_name in self.channels:
                    channel = self.channels[channel_name]
                    if client not in channel.clients:
                        self.channels[channel_name].clients.append(client)
                        prefix = '{}!{}'.format(client.nick, SERVER)
                        client.send(Message(prefix, 'JOIN', str(channel)))
                        nicks = ' '.join(channel_client.nick for channel_client in channel.clients)
                        client.send(Message(SERVER, '353', client.nick, '=', str(channel), nicks))
                        client.send(Message(SERVER, '366', client.nick, 'End of /NAMES list'))
                else:
                    channel = Channel(channel_name, client)
                    self.channels[channel_name] = channel
                    client.channels.append(channel)
                    prefix = '{}!{}'.format(client.nick, SERVER)
                    client.send(Message(prefix, 'JOIN', str(channel)))
                    nicks = ' '.join(channel_client.nick for channel_client in channel.clients)
                    client.send(Message(SERVER, '353', client.nick, '=', str(channel), nicks))
                    client.send(Message(SERVER, '366', client.nick, 'End of /NAMES list'))
        else:
            client.send(Message(SERVER, '461', 'JOIN', 'Not enough parameters'))

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


server = IrcServer()
loop = asyncio.get_event_loop()
loop.run_until_complete(server.irc_server())
try:
    loop.run_forever()
finally:
    loop.close()
