# coding: utf-8

import asyncio
from client import Client
from message import Message

_COMMANDS = ['nick', 'user', 'quit']
_CAP_LS = 'CAP LS'
SERVER = 'localhost'
PORT = 8000


class IrcServer:
    _clients = {}

    async def irc_server(self):
        await asyncio.start_server(self.handle_connection, SERVER, PORT)

    async def handle_connection(self, reader, writer):
        while True:
            data = await reader.read(8192)
            for command in data.decode('utf-8').rstrip().split('\r\n'):
                self.run_command(command, writer)

    def run_command(self, data, writer):
        command = data.split(' ')[0].lower()
        if command in _COMMANDS:
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
        # TODO проверки на уникальность клиента
        # TODO получение реального имени?
        args = data.split(' ')
        command, nick = args[0], args[1]

        if writer in self._clients:
            self._clients[writer] = Client(writer, nick)
            welcome_messages(self._clients[writer])

    def quit(self, data, writer):
        print(self._clients)
        client = self._clients[writer]
        for ch in client.channels:
            client.send(Message(SERVER, 'PART', ch.name, "I'm out"))
        del self._clients[writer]
        print(self._clients)


def welcome_messages(client):
    client.send(Message(SERVER, '001', client.nick, 'Welcome to the Internet Relay Network'))
    client.send(Message(SERVER, '002', client.nick, 'Your host is running on test irc server'))
    client.send(Message(SERVER, '003', client.nick, 'This server was created')) #TODO дату
    client.send(Message(SERVER, '004', client.nick, 'Available commands: {}'.format(' '.join(_COMMANDS))))


server = IrcServer()
loop = asyncio.get_event_loop()
loop.run_until_complete(server.irc_server())
try:
    loop.run_forever()
finally:
    loop.close()
