import random

dictionary = [line.rstrip('\r\n') for line in open('data/common/wordpool.txt', encoding="utf-8")] + \
             [line.rstrip('\r\n') for line in open('data/common/wordpool_addendum.txt', encoding="utf-8")]


def get_random_word():
    """
    Gets a random word from the dictionary.

    :return: A random word as a string.
    """

    return random.sample(dictionary, 1)[0]
