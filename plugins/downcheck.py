import requests
import re

from rtmbot.core import Plugin

API_URL = r'https://downforeveryoneorjustme.com/'


class UnexpectedResponseError(RuntimeError):
    pass


class SoulbotDownCheckPlugin(Plugin):
    def isup_site(self, data):
        """
        Checks whether the given domain (or URL) is down by using the isup.me site.

        :param data: RTM message.
        :return: None
        """

        if len(data["soulbot_args_shlex"]) > 0:
            location = data["soulbot_args_shlex"][0]

            # Remove the protocol from the request, as isup.me doesn't understand them properly,
            # and then remove everything starting from the first slash
            # urllib.parse.urlparse doesn't work well for us here because if no protocol is specified
            # it won't parse the domain as its own (because it seems like a relative url instead)
            # Also, Slack's link format probably kicks in with most links anyway, which we're also dealing here.
            location = re.sub(r'^<([^|]+)(\|.+?>)?', r'\1', location)
            location = re.sub(r'^[a-z]+://', '', location)
            location = re.sub(r'/.+', '', location)

            r = requests.get(API_URL + requests.utils.quote(location))

            try:
                if r.status_code == 200:

                    status = r.text

                    if "It's just you" in status or "If you can see this page and still think we're down" in status:
                        return self.outputs.append([data["channel"],
                                                   '{} seems to be *up*, so it\'s just you. :+1:'.format(location)])
                    elif "looks down from here" in status:
                        return self.outputs.append([data["channel"],
                                                   '{} seems to be *down*, not just for you. :-1:'.format(location)])

                raise UnexpectedResponseError
            except (KeyError, AttributeError, UnexpectedResponseError):
                return self.outputs.append([data["channel"], 'ERROR: Check failed :cry: Please try again later!'])
        else:
            return self.outputs.append([data["channel"], 'Please tell me the site to check first.'])

    def process_message(self, data):
        if data["soulbot_command"] in ['isup', 'isdown', 'down']:
            return self.isup_site(data)


def get_module_help():
    return '\n'.join([
        '`!down domain`, `!isup domain` or `!isdown domain`: Check if a domain is accessible from another network '
        'than your own.'
    ])
