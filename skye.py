""" Skye, the modular virtual assistant """
import sys
import os
import pyaudio
import logging
import time
import shutil
import speech_recognition as sr
from pluginbase import PluginBase
from functools import partial
from playsound import playsound
from gtts import gTTS
from pocketsphinx import DefaultConfig, Decoder, get_model_path, get_data_path

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)
plugin_base = PluginBase(package='skye.plugins',
                         searchpath=['./plugins/default'])


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

    def begin_passive_listening(self):
        """ Uses PocketSphinx to listen for the wakeword and call the active
            listening function """
        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(get_model_path(), 'en-us'))
        config.set_string('-dict', os.path.join(get_model_path(),
                          'cmudict-en-us.dict'))
        config.set_string('-keyphrase', 'sky')
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
                playsound("assets/audio/alert.wav")
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
        try:
            with sr.Microphone() as source:
                logging.info("Ready for input")
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

    def speak(self, text_to_speak):
        timestamp = str(time.time())
        logging.debug(f"Speaking text: {text_to_speak}")
        gTTS(text=text_to_speak, lang='en').save(
             f"temp/voice_files/{timestamp}.mp3")
        playsound(f"temp/voice_files/{timestamp}.mp3")
        os.unlink(f"temp/voice_files/{timestamp}.mp3")

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

    # Call an instance of the main class, beginning initialization
    logging.info("Beginning initialization")
    SKYE = Skye()
    logging.info("Initialization complete")
    logging.info("Beginning passive listening")
    SKYE.begin_passive_listening()
