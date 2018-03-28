"""
    Default Urban dictionary plugin
"""
import logging
import urllib.request
import json


class UrbanPlugin(object):
    """Finds a phrase definition from Urban Dictionary
    """

    def __init__(self, skye):
        self.skye = skye

    def get_definition(self, phrase):
        """Speaks the Urban Dictionary definitions of
        a phrase

        Arguments:
            phrase {string} -- The phrase to query
        """
        logging.debug("Querying Urban Dictionary")
        req = urllib.request.Request("https://mashape-community-urban"
                                     "-dictionary.p.mashape.com/define"
                                     "?term={0}".format(phrase))
        req.add_header('X-Mashape-Key',
                       self.skye.config.get("urban_dictionary", "api_key"))
        req.add_header('Content-Type', 'text/plain')
        request = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(request)
        definition = data["list"][0]["definition"]
        self.skye.speak(f"The definition for {phrase} is"
                        f"{definition}")

    def get_phrase(self):
        """Asks the user for a phrase and passes it to
        the get_definition function
        """
        if self.skye.config.get("urban_dictionary", "api_key") == "":
            self.skye.speak("No API key has been set in the config file.")
            return
        self.skye.speak("What phrase should I define?")
        word = self.skye.active_listen()
        if (word != -1 and
            word != -2 and
                word != -3):
            self.get_definition(word)
        else:
            self.skye.speak("Sorry, I didn't understand you.")


def setup(skye):
    """Called when the plugin is set up. Used to register commands and other
    initializations

    Arguments:
        skye {Skye} -- The singleton Skye instance
    """
    urban_plugin = UrbanPlugin(skye)
    skye.register_command(("urban", "urban dictionary"),
                          urban_plugin.get_phrase)
