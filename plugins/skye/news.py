"""
    Default news plugin
"""
import logging
import urllib.request
import shutil
from playsound import playsound

NEWS_URL = "https://video.news.sky.com/snr/news/snrnews.mp3"


class NewsPlugin(object):
    """ Removes temporary files and exits the program """

    def __init__(self, skye):
        self.skye = skye

    def play_bulletin(self):
        """ Plays an MP3 bulletin from Sky News """
        logging.info("Downloading news bulletin")
        self.skye.speak("Here's your 2 minute news bulletin.")
        with urllib.request.urlopen(NEWS_URL) as response, open(
                "temp/bulletin.mp3", 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        playsound("temp/bulletin.mp3")


def setup(skye):
    news_plugin = NewsPlugin(skye)
    skye.register_command(("news", "briefing", "flash briefing"),
                          news_plugin.play_bulletin)
