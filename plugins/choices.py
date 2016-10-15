import random

outputs = []

helpful_replies = [line.rstrip('\r\n') for line in open('data/choices/helpfuls.txt')]
hazy_replies    = [line.rstrip('\r\n') for line in open('data/choices/hazies.txt')]
helpful_ratio   = 0.95


def random_choice(data):
    """
    Chooses a random item from a slash-delimitered list.

    :param data: RTM message.
    :return: None
    """

    items = list(filter(None, [s.strip() for s in data["soulbot_args_shlex"]]))

    if len(items) > 1 and random.random() > helpful_ratio:
        reply = random.choice(hazy_replies)
    else:
        reply = random.choice(helpful_replies)

    if len(items) > 1:
        return outputs.append([data["channel"], reply.format(random.choice(items))])
    elif len(items) == 1:
        return outputs.append([data["channel"], reply.format('Try more options next time')])
    else:
        return outputs.append([data["channel"], reply.format('Give me something to choose from first')])


def throw_dice(data):
    """
    Throws an n-sided die.

    :param data: RTM message
    :return: None
    """

    if len(data["soulbot_args_space"]) > 0:
        try:
            sides = int(data["soulbot_args_space"][0])
        except (TypeError, ValueError):
            return outputs.append([data["channel"], "That doesn't seem like a number of sides."])
    else:
        sides = 6

    if sides <= 0:
        return outputs.append([data["channel"], "Please provide a positive number of sides."])

    return outputs.append([data["channel"], "You rolled a {}!".format(random.randint(1, sides))])


def process_message(data):
    if data["soulbot_command"] in ['choose', 'choice']:
        return random_choice(data)
    elif data["soulbot_command"] in ['die', 'dice']:
        return throw_dice(data)


def get_module_help():
    return '\n'.join([
        '`!choice` or `!choose`: Pick a random item. Use quotes for choices with multiple words.',
        '`!die` or `!dice`: Throw a die. Optionally, provide the number of sides: `!die 20`'
    ])
