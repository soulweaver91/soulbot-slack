import importlib
import os

outputs = []


def process_message(data):
    """
    Retrieves the help text from each module and prints them.

    The help text must be returned from a function called "get_module_help".
    If the function is not found, no help for that module will be printed.

    :param data: RTM message.
    :return: None
    """

    if data["soulbot_command"] == 'help':
        help_strs = []

        for module in os.listdir('plugins'):
            if module[-3:] == '.py':
                mod = importlib.import_module('plugins.' + module[:-3])
                if getattr(mod, 'get_module_help', None) is not None:
                    help_strs.append('_Module \'' + module[:-3] + '\':_\n' + mod.get_module_help())

        outputs.append([
            data["channel"],
            '*SoulBot Commands*\n' + '\n\n'.join(help_strs)
        ])


def get_module_help():
    return '`!help`: Print this help.'
