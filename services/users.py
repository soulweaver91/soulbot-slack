class UserService:
    def __init__(self, client=None):
        self.sc = client

    def get_user_name(self, user_id):
        """
        Retrieves a user's real name by their internal ID.

        :param user_id: The internal Slack user ID.
        :return: The user's set up real name, or if some reason one cannot be found, the same user ID returned back.
        """

        try:
            user = self.sc.server.users.find(user_id)
            return user.real_name
        except AttributeError:
            return user_id

    def get_channel_user_names(self, channel_id):
        """
        Retrieves the names of the users on a channel.

        :param channel_id: The internal Slack channel ID.
        :return: The real names of the users on the channel, if available. If the channel doesn't exist, an empty list.
        """

        try:
            channel_users = self.sc.server.channels.find(channel_id)
            return [self.get_user_name(user) for user in channel_users.members]
        except AttributeError:
            return []
