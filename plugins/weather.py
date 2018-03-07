import requests
import json

from rtmbot.core import Plugin, Job

API_URL = r'https://api.wunderground.com/api/'


class UnexpectedResponseError(RuntimeError):
    pass


class ClearCooldownJob(Job):
    parent = None

    def __new__(cls, parent_plugin, interval):
        return super(ClearCooldownJob, cls).__new__(cls)

    def __init__(self, parent_plugin, interval):
        super().__init__(interval)
        self.parent = parent_plugin

    def run(self, slack_client):
        self.parent.api_cooldown = 0
        print("cooldown cleared")


class SoulbotWeatherPlugin(Plugin):
    api_cooldown = 0

    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super().__init__(name=name, slack_client=slack_client, plugin_config=plugin_config)
        self.weather_config = plugin_config

    def register_jobs(self):
        self.jobs.append(ClearCooldownJob(self, 120))

    @staticmethod
    def get_forecast_emoji(condition_str):
        if condition_str in ['chanceflurries', 'flurries', 'chancesnow', 'snow', 'chancesleet', 'sleet']:
            return ':snow_cloud:'
        elif condition_str in ['chancerain', 'rain']:
            return ':rain_cloud:'
        elif condition_str in ['chancetstorms', 'tstorms']:
            return ':thunder_cloud_and_rain:'
        elif condition_str in ['clear', 'sunny']:
            return ':sunny:'
        elif condition_str == 'cloudy':
            return ':cloud:'
        elif condition_str in ['fog', 'hazy']:
            return ':fog:'
        elif condition_str == 'mostlycloudy':
            return ':barely_sunny:'
        elif condition_str == 'mostlysunny':
            return ':mostly_sunny:'
        elif condition_str in ['partlycloudy', 'partlysunny']:
            return ':partly_sunny:'
        else:
            return ':question:'

    @staticmethod
    def get_forecast_dict(title, conditions_icon, conditions, temp_low_c, temp_low_f, wind_dir, wind_kph, wind_mph,
                          prec_mm, prec_in, temp_high_c=None, temp_high_f=None):
        if temp_high_c is not None and temp_high_f is not None:
            temp_str = '{}–{}°C ({}–{}°F)'.format(temp_low_c, temp_high_c, temp_low_f, temp_high_f)
        else:
            temp_str = '{}°C ({}°F)'.format(temp_low_c, temp_low_f)

        return {
            "title": title,
            "value": '{} {}, {} :dash: From {} {}kph ({}mph) :droplet: {}mm ({}in)'.format(
                SoulbotWeatherPlugin.get_forecast_emoji(conditions_icon),
                conditions,
                temp_str,
                wind_dir,
                wind_kph,
                wind_mph,
                prec_mm,
                prec_in
            ),
            "short": False
        }

    @staticmethod
    def get_forecast_dict_for_current(data):
        return SoulbotWeatherPlugin.get_forecast_dict(
            title='Today',
            conditions=data["weather"],
            conditions_icon=data["icon"],
            temp_low_c=data["temp_c"],
            temp_low_f=data["temp_f"],
            wind_dir=data["wind_dir"],
            wind_kph=data["wind_kph"],
            wind_mph=data["wind_mph"],
            prec_mm=data["precip_today_metric"],
            prec_in=data["precip_today_in"]
        )

    @staticmethod
    def get_forecast_dict_for_day(data):
        return SoulbotWeatherPlugin.get_forecast_dict(
            title=data["date"]["weekday"],
            conditions=data["conditions"],
            conditions_icon=data["icon"],
            temp_low_c=data["low"]["celsius"],
            temp_low_f=data["low"]["fahrenheit"],
            temp_high_c=data["high"]["celsius"],
            temp_high_f=data["high"]["fahrenheit"],
            wind_dir=data["avewind"]["dir"],
            wind_kph=data["avewind"]["kph"],
            wind_mph=data["avewind"]["mph"],
            prec_mm=data["qpf_allday"]["mm"],
            prec_in=data["qpf_allday"]["in"]
        )

    def get_forecast(self, data):
        """
        Fetches a five-day forecast from Wunderground API.

        :param data: RTM message.
        :return: None
        """

        if "WUNDERGROUND_API_KEY" not in self.weather_config:
            return self.outputs.append([data["channel"], 'ERROR: The weather plugin is improperly configured.'])

        if self.api_cooldown >= 5:
            return self.outputs.append([data["channel"],
                                        'The weather API is rate limited. '
                                        'Please wait for a moment before making another request.'])

        if len(data["soulbot_args_shlex"]) > 0:
            location = data["soulbot_args_shlex"][0]

            r = requests.get(API_URL + self.weather_config["WUNDERGROUND_API_KEY"]
                             + '/geolookup/conditions/forecast/q/'
                             + location + '.json')
            self.api_cooldown += 1

            try:
                if r.status_code == 200:
                    forecast = r.json()

                    if 'location' in forecast and 'forecast' in forecast and 'current_observation' in forecast:
                        found_location = forecast["location"]

                        location_name = ':flag-{}: {}{}, {} ({:.2f}°{}, {:.2f}°{})'.format(
                            found_location["country_iso3166"].lower(),
                            found_location["city"],
                            (", " + found_location["state"] if len(found_location["state"]) > 0 else ""),
                            found_location["country_name"],
                            abs(float(found_location["lat"])),
                            ("N" if float(found_location["lat"]) > 0 else "S"),
                            abs(float(found_location["lon"])),
                            ("E" if float(found_location["lon"]) > 0 else "W")
                        )

                        forecast_dicts = \
                            [self.get_forecast_dict_for_current(forecast["current_observation"])] + \
                            [self.get_forecast_dict_for_day(day_data) for day_data in
                             forecast["forecast"]["simpleforecast"]["forecastday"]]

                        message_json = json.dumps([
                            {
                                "fallback": "Required plain-text summary of the attachment. TODO.",
                                "title": location_name,
                                "title_link": found_location["wuiurl"],
                                "fields": forecast_dicts,
                                "footer": "Weather Underground",
                                "ts": int(forecast["current_observation"]["local_epoch"])
                            }
                        ])

                        return self.slack_client.api_call('chat.postMessage', channel=data["channel"],
                                                          attachments=message_json, as_user=True)

                    elif 'response' in forecast and 'results' in forecast["response"]:
                        location_texts = [
                            '`zmw:{}`: :flag-{}: {}{}, {}'.format(
                                location["zmw"],
                                location["country_iso3166"].lower(),
                                location["name"],
                                (", " + location["state"] if len(location["state"]) > 0 else ""),
                                location["country_name"]
                            )
                            for location in forecast["response"]["results"]
                        ]

                        return self.outputs.append([
                            data["channel"],
                            'Multiple locations named \'{}\' were found.\n'.format(location) +
                            '\n'.join(location_texts)
                        ])
                    elif 'response' in forecast and 'error' in forecast["response"]:
                        if forecast["response"]["error"]["type"] == 'querynotfound':
                            return self.outputs.append([
                                data["channel"],
                                'No locations called \'{}\' were found.'.format(location)
                            ])

                raise UnexpectedResponseError
            except (KeyError, AttributeError, UnexpectedResponseError) as e:
                print(e)
                return self.outputs.append([data["channel"],
                                            'ERROR: Could not get the forecast :cry: Please try again later!'])
        else:
            return self.outputs.append([data["channel"], 'Please provide a location for the forecast first.'])

    def process_message(self, data):
        if data["soulbot_command"]  == 'weather':
            return self.get_forecast(data)


def get_module_help():
    return '\n'.join([
        '`!weather location` or `!weather zmw:00000.0.00000`: Get a five-day forecast in the given location. '
        'You can either use a location\'s name directly or a specific location code shown if the location name '
        'was ambiguous.'
    ])
