""" Skye, the modular virtual assistant """
import sys
import os
import pyaudio
import logging
import time
import shutil
import configparser
import speech_recognition as sr
from pluginbase import PluginBase
from functools import partial
from playsound import playsound
from gtts import gTTS
from utils.onboarding import Onboarding
from pocketsphinx import DefaultConfig, Decoder, get_model_path, get_data_path

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)
plugin_base = PluginBase(package='skye.plugins',
                         searchpath=['./plugins/skye'])
VERSION="2.0.0 alpha1 build 7"


class Skye(object):
    """ The core Skye class """

    def __init__(self):
        """ Initializes the program """
        logging.info("Preparing the plugin path")
        custom_dir_name = "custom"
        self.commands = {}
        self.source = plugin_base.make_plugin_source(
            searchpath=[get_path('./plugins/%s' % custom_dir_name)],
            identifier=custom_dir_name
        )

        logging.info("Cleaning leftover temporary files")
        if os.path.exists("temp"):
            shutil.rmtree("temp", ignore_errors=True)

        logging.info("Creating new temporary files")
        os.makedirs("temp/voice_files")

        logging.info("Loading config files")
        self.config = configparser.ConfigParser()
        self.config_location = "config/skye/"
        if os.path.exists(self.config_location + "config.ini"):
            self.config.read(self.config_location + "config.ini")
        else:
            logging.warn("No configuration exists, attempting to use "
                         "default config. This may cause issues.")
            if os.path.exists(self.config_location + "default_config.ini"):
                self.config.read(self.config_location + "default_config.ini")
            else:
                logging.fatal("No configuration files exist")
                exit()

        logging.info("Loading plugins")
        for plugin_name in self.source.list_plugins():
            logging.debug(f"Loading plugin: {plugin_name}")
            plugin = self.source.load_plugin(plugin_name)
            plugin.setup(self)

        self.r = sr.Recognizer()
        with sr.Microphone() as source:
            logging.info("Adjusting microphone to ambient noise")
            self.r.adjust_for_ambient_noise(source)
            logging.info("Microphone adjusted")
            self.r.pause_threshold = 0.6

        logging.debug("Checking whether to onboard the user")
        if self.config.getboolean("general", "onboarding"):
            onboarding_instance = Onboarding(self)
            onboarding_instance.onboard()

    def begin_passive_listening(self):
        """ Uses PocketSphinx to listen for the wakeword and call the active
            listening function """
        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(get_model_path(), 'en-us'))
        config.set_string('-dict', os.path.join(get_model_path(),
                          'cmudict-en-us.dict'))
        config.set_string('-keyphrase', self.config.get(
                          "general", "wake_word"))
        config.set_string('-logfn', 'nul')
        config.set_float('-kws_threshold', 1e-10)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=1024)
        stream.start_stream()

        decoder = Decoder(config)
        decoder.start_utt()

        while True:
            buf = stream.read(1024)
            decoder.process_raw(buf, False, False)
            if decoder.hyp() is not None:
                logging.debug("Wake word recognized")
                speech_input = self.active_listen()
                if (speech_input != -1 and
                    speech_input != -2 and
                        speech_input != -3):
                    for name, command in self.commands.items():
                        if speech_input in name:
                            command()
                elif speech_input == -1:
                    self.speak("Sorry, I didn't catch that.")
                decoder.end_utt()
                decoder.start_utt()
                logging.debug("Listening for wakeword again")

    def register_command(self, name, command):
        """ A function with plugins can use to register a command """
        self.commands[name] = command

    def active_listen(self):
        """ Begins listening for content after the wakeword """
        # If text entry mode is enabled, route to the debug function
        if self.config.getboolean("debug", "text_input"):
            return self.debug_get_text()
        try:
            with sr.Microphone() as source:
                logging.info("Listening for input")
                playsound("assets/audio/alert.wav")
                audio = self.r.listen(source, 3, phrase_time_limit=6)
            speech_input = self.r.recognize_google(audio)
            logging.debug(f"Recognised: {speech_input}")
            return speech_input
        except sr.UnknownValueError:
            logging.error("UnknownValue error")
            return -1
        except sr.RequestError as error:
            logging.error("Request error: {0}".format(error))
            return -2
        except sr.WaitTimeoutError:
            logging.error("WaitTimeout error")
            return -3

    def debug_text_input(self):
        speech_input = self.debug_get_text()
        for name, command in self.commands.items():
            if speech_input in name:
                command()
        self.debug_text_input()

    def debug_get_text(self):
        text = input("skye $ ")
        logging.debug(f"Ran manual command: {text}")
        return text

    def speak(self, text_to_speak):
        timestamp = str(time.time())
        logging.debug(f"Speaking text: {text_to_speak}")
        file_location = f"temp/voice_files/{timestamp}.mp3"
        gTTS(text=text_to_speak, lang='en').save(file_location)
        playsound(file_location)
        os.unlink(file_location)

if __name__ == '__main__':
    # Set up logging format
    log_format = logging.Formatter(
        "%(asctime)s [%(module)s] [%(levelname)s] %(message)s")
    base_logger = logging.getLogger()
    base_logger.setLevel(logging.DEBUG)

    file_output = logging.FileHandler("logs/{0}.log"
                                      .format(str(time.time())))
    file_output.setFormatter(log_format)
    base_logger.addHandler(file_output)

    console_output = logging.StreamHandler()
    console_output.setFormatter(log_format)
    base_logger.addHandler(console_output)

    # Print about banner
    logging.info("     _____ _")
    logging.info("    / ____| |")
    logging.info("   | (___ | | ___   _  ___")
    logging.info("    \\___ \\| |/ / | | |/ _ \\")
    logging.info("    ____) |   <| |_| |  __/")
    logging.info("   |_____/|_|\\_\\\\__, |\\___|")
    logging.info("                 __/ |")
    logging.info("                |___/")
    logging.info("")
    logging.info(f"Skye Assistant version {VERSION}")
    logging.info("")

    # Call an instance of the main class, beginning initialization
    logging.info("Beginning initialization")
    SKYE = Skye()
    logging.info("Initialization complete")
    logging.info("Beginning passive listening")

    # Checks whether the debug text input is enabled
    if SKYE.config.getboolean("debug", "text_input"):
        SKYE.debug_text_input()
    else:
        SKYE.begin_passive_listening()
