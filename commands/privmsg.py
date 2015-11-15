# coding: utf-8
"""
Пример команды PRIVMSG #room message
               PRIVMSG #room :first message
"""

from commands.base import BaseCommand
from config import SERVER
from message import Message
from numeric_replies import err_needmoreparams, err_notonchannel, err_nosuchchannel


class PrivmsgCommand(BaseCommand):
    def __init__(self, clients, channels, command, writer):
        self.clients = clients
        self.channels = channels
        self.command = command
        self.writer = writer
        self.message = None
        self.channel_name = None

    def parse_command(self):
        args = self.command.split(' ')

        self.concat_after_colon(args)
        if len(args) == 3:
            self.channel_name = args[1]
            self.message = args[2]

    def validate(self):
        # проверим, корректность команды
        if self.channel_name is None or self.message is None:
            return err_needmoreparams(self.command)
        client_channel_names = [ch.name for ch in self.clients[self.writer].channels]

        # проверим, есть ли такой канал
        if self.channel_name not in self.channels:
            return err_nosuchchannel(self.channel_name)

        # проверим, находится ли клиент на канале, в который пишет
        if self.channel_name not in client_channel_names:
            return err_notonchannel(self.channel_name)

    def run_command(self):
        client = self.clients[self.writer]

        self.parse_command()
        validation_error = self.validate()

        if validation_error:
            client.send(validation_error)
            return

        # отправляем сообщение всем остальным людям на канале
        channel = self.channels[self.channel_name]

        prefix = '{}!{}'.format(client.nick, SERVER)
        for ch_client in channel.clients:
            if ch_client != client:
                ch_client.send(Message(prefix, 'PRIVMSG', str(channel), self.message))