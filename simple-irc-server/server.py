# coding: utf-8

import asyncio

from commands.join import JoinCommand
from commands.nick import NickCommand
from commands.privmsg import PrivmsgCommand
from commands.quit import QuitCommand
from commands.user import UserCommand
from config import SERVER, PORT, COMMANDS
from numeric_replies import err_unknowncommand


class IrcServer:
    clients = {}
    channels = {}

    async def irc_server(self):
        await asyncio.start_server(self.handle_connection, SERVER, PORT)

    async def handle_connection(self, reader, writer):
        while True:
            data = await reader.read(8192)
            if not data:
                break
            for command in data.decode('utf-8').rstrip().split('\r\n'):
                self.run_command(command, writer)

    def run_command(self, command, writer):
        command_name = command.split(' ')[0].lower()
        if command_name in COMMANDS:
            return self._get_command(command_name)(command, writer)

        else:
            writer.write(bytes(err_unknowncommand()))

    def _get_command(self, command_name):
        command = getattr(self, command_name)
        return command

    def nick(self, command, writer):
        NickCommand(self.clients, command, writer).run_command()

    def user(self, command, writer):
        UserCommand(self.clients, command, writer).run_command()

    def join(self, command, writer):
        JoinCommand(self.clients, self.channels, command, writer).run_command()

    def privmsg(self, command, writer):
        PrivmsgCommand(self.clients, self.channels, command, writer).run_command()

    def quit(self, command, writer):
        QuitCommand(self.clients, command, writer).run_command()


server = IrcServer()
loop = asyncio.get_event_loop()
loop.run_until_complete(server.irc_server())
try:
    loop.run_forever()
finally:
    loop.close()
