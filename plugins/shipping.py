#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import shlex
import re
import random

from services import words as wordsvc, users as usersvc
from client import slack_client as sc

outputs = []


def process_message(data):
    """
    Creates a shipping name out of users of the channel or the given names.

    :param data: RTM message.
    :return: None
    """

    cmd = data["text"].split()[0]

    if cmd == '!shipme':
        args = shlex.split(' '.join(data["text"].split(' ')[1:]))
        shipname = []
        for i in range(0, random.randint(1, 3)):
            shipname.append(wordsvc.get_random_word().capitalize())
        shipname.append('Shipping')
        shipname = ''.join(shipname)

        if len(args) == 0:
            args.append('2')

        if re.match(r'^\d+$', args[0]) and len(args) == 1:
            count = int(args[0])
            if count <= 1:
                return outputs.append([data["channel"], 'Please specify a number greater or equal to 2. :dansgame:'])

            users = [usersvc.get_user_name(user) for
                     user in sc.api_call('channels.info', channel=data["channel"])["channel"]["members"]]

            own_name = usersvc.get_user_name(data["user"])
            try:
                users.remove(own_name)
            except ValueError:
                pass

            outputs.append([data["channel"], ' × '.join([own_name] + random.sample(users, min(len(users), count - 1))) +
                            ' = ' + shipname])
        elif len(args) > 1:
            outputs.append([data["channel"], ' × '.join(args) + ' = ' + shipname])
        else:
            outputs.append([data["channel"], 'Please name a partner for {} first :lenny:'.format(args[0])])


def get_module_help():
    return '\n'.join([
        '`!shipme`: Creates a new random parody shipping name between you and another person on the channel. '
        'Optionally, provide a number to ship that many people in total, including you, or provide a list of '
        'names to ship instead.'
    ])
