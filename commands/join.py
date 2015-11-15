# coding: utf-8
"""
пример команды: JOIN #room #room2
"""
from channel import Channel
from commands.base import BaseCommand
from config import SERVER
from message import Message
from numeric_replies import err_notregistered, err_needmoreparams


class JoinCommand(BaseCommand):
    def __init__(self, clients, channels, command, writer):
        self.clients = clients
        self.channels = channels
        self.command = command
        self.writer = writer
        self.channel_names = None

    def parse_command(self):
        args = self.command.split(' ')
        if len(args) > 1:
            self.channel_names = args[1:]

    def validate(self):
        if not self.channel_names:
            return err_needmoreparams(self.command)

    def update_connected_clients(self, channel):
        for client in channel.clients:
            self.update_channel_users_messages(channel, client)

    def run_command(self):
        client = self.clients.get(self.writer)
        if client is None:
            self.writer.write(bytes(err_notregistered()))
            return

        self.parse_command()

        validation_error = self.validate()

        if validation_error:
            client.send(validation_error)
            return
        else:
            # подключение к каждому каналу
            for channel_name in self.channel_names:
                if channel_name in self.channels:
                    channel = self.channels[channel_name]
                    if client not in channel.clients:
                        self.channels[channel_name].clients.append(client)
                        client.channels.append(channel)
                        prefix = '{}!{}'.format(client.nick, SERVER)
                        client.send(Message(prefix, 'JOIN', str(channel)))
                        self.update_channel_users_messages(channel, client)
                        self.update_connected_clients(channel)
                else:
                    channel = Channel(channel_name, client)
                    self.channels[channel_name] = channel
                    client.channels.append(channel)
                    prefix = '{}!{}'.format(client.nick, SERVER)
                    client.send(Message(prefix, 'JOIN', str(channel)))
                    self.update_channel_users_messages(channel, client)