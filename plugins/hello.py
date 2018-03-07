from services.users import UserService

from rtmbot.core import Plugin

class SoulbotHelloPlugin(Plugin):
    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super().__init__(name=name, slack_client=slack_client, plugin_config=plugin_config)
        self.usersvc = UserService(client=slack_client)

    def process_message(self, data):
        if "hello" in data["text"]:
            self.outputs.append([
                data["channel"],
                "Hello, {}!".format(self.usersvc.get_user_name(data["user"]))
            ])


def get_module_help():
    return 'Any message with \'hello\': Get greeted.'
