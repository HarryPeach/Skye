"""
    Default weather plugin using OpenWeatherMap
"""
import shutil
import logging
import os
import requests
import json


class WeatherPlugin(object):
    """ Gets the current weather and reads it out """

    def __init__(self, skye):
        self.skye = skye

    def get_weather(self, location):
        """ Get the weather and speak it """
        try:
            logging.info("Beginning weather request"
                         "for location: {0}".format(location))
            logging.debug("Connecting to openweathermap API")
            url = ("http://api.openweathermap.org/data/2.5/weather?q="
                   "{0}&appid={1}&units=metric"
                   .format(location,
                           self.skye.config.get("weather", "api_key")))
            request = requests.get(url)
            data = json.loads(request.content.decode('utf-8'))
            forecast = data['weather'][0]['description']
            average_temp = data['main']['temp']
            max_temp = data['main']['temp_max']
            min_temp = data['main']['temp_min']
            logging.debug("Speaking weather data")
            self.skye.speak("The weather for {0} is {1} with a temperature"
                            "of {2} degrees, a maximum of {3} and a"
                            "minimum of {4}.".format(location, forecast,
                                                     round(average_temp),
                                                     max_temp, min_temp))
        except ConnectionError as connection_error:
            logging.error(connection_error)
            self.skye.speak("There was a connection error, "
                            "please try again later.")
        except TimeoutError as timeout_error:
            logging.error(timeout_error)
            self.skye.speak("The connection timed out, "
                            "please try again later.")

    def get_location(self):
        if self.skye.config.get("weather", "api_key") == "":
            self.skye.speak("No API key has been set in the config file.")
            return
        self.skye.speak("Where should I get weather data for?")
        word = self.skye.active_listen()
        if (word != -1 and
            word != -2 and
                word != -3):
            self.get_weather(word)
        else:
            self.skye.speak("Sorry, I didn't understand you.")


def setup(skye):
    """Called when the plugin is set up. Used to register commands and other
    initializations

    Arguments:
        skye {Skye} -- The singleton Skye instance
    """
    weather_plugin = WeatherPlugin(skye)
    skye.register_command(("weather"),
                          weather_plugin.get_location)
