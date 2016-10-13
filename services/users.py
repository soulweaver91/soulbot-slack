state = {
    "users": {}
}


def get_user_name(user_id):
    """
    Retrieves a user's real name by their internal ID.

    :param user_id: The internal Slack user ID.
    :return: The user's set up real name, or if some reason one cannot be found, the same user ID returned back.
    """

    try:
        user = state["users"].get(user_id, None)
        return user["real_name"]
    except KeyError:
        return user_id


def store_users(new_users):
    """
    Replaces the memorized user list with a new one.

    :param new_users: The new user list as a dict received from the Slack API.
    :return: None
    """

    old_users = state["users"].copy()
    state["users"].clear()

    try:
        for user in new_users:
            state["users"][user["id"]] = user
    except KeyError:
        state["users"] = old_users
