from client import slack_client as sc


def get_user_name(user_id):
    """
    Retrieves a user's real name by their internal ID.

    :param user_id: The internal Slack user ID.
    :return: The user's set up real name, or if some reason one cannot be found, the same user ID returned back.
    """

    try:
        user = sc.server.users.find(user_id)
        return user.real_name
    except AttributeError:
        return user_id
