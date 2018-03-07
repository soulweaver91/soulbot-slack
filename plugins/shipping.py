import re
import random

from services.words import WordService
from services.users import UserService

from rtmbot.core import Plugin


class SoulbotShippingPlugin(Plugin):
    wordsvc = WordService()

    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super().__init__(name=name, slack_client=slack_client, plugin_config=plugin_config)
        self.usersvc = UserService(client=slack_client)

    def process_message(self, data):
        """
        Creates a shipping name out of users of the channel or the given names.

        :param data: RTM message.
        :return: None
        """

        if data["soulbot_command"] == 'shipme':
            args = data["soulbot_args_shlex"]

            shipname = []
            for i in range(0, random.randint(1, 3)):
                shipname.append(self.wordsvc.get_random_word().capitalize())
            shipname.append('Shipping')
            shipname = ''.join(shipname)

            if len(args) == 0:
                args.append('2')

            if re.match(r'^\d+$', args[0]) and len(args) == 1:
                count = int(args[0])
                if count <= 1:
                    return self.outputs.append([data["channel"],
                                                'Please specify a number greater or equal to 2. :dansgame:'])

                users = self.usersvc.get_channel_user_names(data["channel"])
                own_name = self.usersvc.get_user_name(data["user"])

                try:
                    users.remove(own_name)
                except ValueError:
                    pass

                self.outputs.append([data["channel"], ' × '.join(
                    [own_name] + random.sample(users, min(len(users), count - 1))
                ) + ' = ' + shipname])
            elif len(args) > 1:
                self.outputs.append([data["channel"], ' × '.join(args) + ' = ' + shipname])
            else:
                self.outputs.append([data["channel"], 'Please name a partner for {} first :lenny:'.format(args[0])])


def get_module_help():
    return '\n'.join([
        '`!shipme`: Creates a new random parody shipping name between you and another person on the channel. '
        'Optionally, provide a number to ship that many people in total, including you, or provide a list of '
        'names to ship instead.'
    ])
