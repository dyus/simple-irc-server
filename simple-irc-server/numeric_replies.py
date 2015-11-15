# coding: utf-8
"""
Цифровые ответы клиенту
"""
from config import SERVER
from message import Message


def err_unknowncommand():
    return Message(SERVER, '421', 'Unknown command')


def err_needmoreparams(command):
    return Message(SERVER, '461', command, 'Not enough parameters')


def err_nonicknamegiven():
    return Message(SERVER, '431', 'No nickname given')


def err_erroneusnickname(nick):
    return Message(SERVER, '432', nick, 'Erroneous nickname')


def err_nicknameinuse(nick):
    return Message(SERVER, '433', nick, 'Nickname is already in use')


def err_nosuchnick(nick):
    return Message(SERVER, '401', nick, 'No such nick')


def err_notregistered():
    return Message(SERVER, '451', 'You have not registered')


def err_notonchannel(channel_name):
    return Message(SERVER, '442', channel_name, "You're not on that channel")


def err_nosuchchannel(channel_name):
    return Message(SERVER, '401', channel_name, 'No such channel')
