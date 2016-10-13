import random

outputs = []

helpful_replies = [line.rstrip('\r\n') for line in open('data/choices/helpfuls.txt')]
hazy_replies    = [line.rstrip('\r\n') for line in open('data/choices/hazies.txt')]
helpful_ratio   = 0.95


def process_message(data):
    """
    Chooses a random item from a slash-delimitered list.

    :param data: RTM message.
    :return: None
    """

    if data["text"][:7] in ['!choose', '!choice']:
        items = list(filter(None, [s.strip() for s in data["text"][7:].split('/')]))

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


def get_module_help():
    return '`!choice` or `!choose`: Pick a random item from a slash-delimitered list.'
