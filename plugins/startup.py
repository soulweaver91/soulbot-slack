from client import slack_client as sc
from services import users as usersvc

outputs = []


def load_users():
    """
    Loads the user list via the API and stores them in the user service.

    N.B.: It seems this cannot be stored directly in the plugin; internal state seemed to reset after processing the
    "hello" message. This is why services reside in a different directory instead.

    :return: None
    """
    usersvc.store_users(sc.api_call("users.list")["members"])


def process_hello(data):
    """
    Runs all tasks that need to be run when the bot first connects.

    :param data: Unused.
    :return: None
    """
    load_users()
