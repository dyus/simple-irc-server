# coding: utf-8

import asyncio
from client import Client
from message import Message
from config import *
from channel import Channel


class IrcServer:
    _clients = {}
    _channels = {}

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
            return ':{} 431 * :Wrong command'.format(SERVER).encode('utf-8')

    def _get_command(self, command):
        command = getattr(self, command)
        return command

    def nick(self, data, writer):
        # TODO валидация ника
        try:
            command, nick = data.split(' ')
            if nick:
                if nick not in self._clients:
                    self._clients[writer] = (Client(writer, nick))
                else:
                    return "':{} 433 * {} : Nickname is already in use'".format(SERVER, nick).encode('utf-8')

        except ValueError:
            return "':{} 431 * : No nickname given'".format(SERVER).encode('utf-8')

    def user(self, data, writer):
        """
        :param data: USER user mode unused :realname
        :return:
        """
        args = data.split(' ')
        command, nick = args[0], args[1]

        if writer in self._clients:
            self._clients[writer] = Client(writer, nick)
            welcome_messages(self._clients[writer])

    def quit(self, data, writer):
        client = self._clients[writer]
        for ch in client.channels:
            client.send(Message(SERVER, 'PART', ch.name, "I'm out"))
        del self._clients[writer]

    def join(self, data, writer):
        # TODO пройтись еще раз убедиться что все сообщения соответсвуют формату ирк протокола
        # TODO при добавлении нового нужно отсылать сообщение с пересчетом списка всем участникам канала
        client = self._clients[writer]

        args = data.split(' ')
        if len(args) > 1:
            channel_names = args[1:]
            for channel_name in channel_names:
                if channel_name in self._channels:
                    channel = self._channels[channel_name]
                    if client not in channel.clients:
                        self._channels[channel_name].clients.append(client)
                        prefix = '{}!{}'.format(client.nick, SERVER)
                        client.send(Message(prefix, 'JOIN', str(channel)))
                        nicks = ' '.join(channel_client.nick for channel_client in channel.clients)
                        client.send(Message(SERVER, '353', client.nick, '=', str(channel), nicks))
                        client.send(Message(SERVER, '366', client.nick, 'End of /NAMES list'))
                else:
                    channel = Channel(channel_name, client)
                    self._channels[channel_name] = channel
                    client.channels.append(channel)
                    prefix = '{}!{}'.format(client.nick, SERVER)
                    client.send(Message(prefix, 'JOIN', str(channel)))
                    nicks = ' '.join(channel_client.nick for channel_client in channel.clients)
                    client.send(Message(SERVER, '353', client.nick, '=', str(channel), nicks))
                    client.send(Message(SERVER, '366', client.nick, 'End of /NAMES list'))
        else:
            client.send(SERVER, '461', 'JOIN', 'Not enough parameters')

    def privmsg(self, data, writer):
        # :Guest53954!~test3@122.96.145.130 PRIVMSG #ubuntu :exit
        # TODO Обработка ошибок
        # отправляем всем, остальным людям в канале
        client = self._clients[writer]
        args, msg_body = data.split(':')
        command, channel_name = args.rstrip().split(' ')
        channel = self._channels[channel_name]

        # TODO проверка наличия указанного канала
        prefix = '{}!{}'.format(client.nick, SERVER)
        for ch_client in channel.clients:
            if ch_client != client:
                ch_client.send(Message(prefix, 'PRIVMSG', str(channel), msg_body))


def welcome_messages(client):
    client.send(Message(SERVER, '001', client.nick, 'Welcome to the Internet Relay Network'))
    client.send(Message(SERVER, '002', client.nick, 'Your host is running on test irc server'))
    client.send(Message(SERVER, '003', client.nick, 'This server was created at {}'.format(start_time)))
    client.send(Message(SERVER, '004', client.nick, 'Available commands: {}'.format(' '.join(COMMANDS))))


server = IrcServer()
loop = asyncio.get_event_loop()
loop.run_until_complete(server.irc_server())
try:
    loop.run_forever()
finally:
    loop.close()
