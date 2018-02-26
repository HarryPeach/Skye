"""
    Default exit plugin
"""
import shutil
import logging
import os


class ExitPlugin(object):
    """ Removes temporary files and exits the program """

    def __init__(self, skye):
        self.skye = skye

    def close_program(self):
        """ Closes the program """
        self.skye.speak("Goodbye")
        logging.debug("Removing temporary folders")
        if os.path.exists("temp"):
            shutil.rmtree("temp", ignore_errors=True)
        logging.info("Exiting")
        quit()


def setup(skye):
    exit_plugin = ExitPlugin(skye)
    skye.register_command(("exit", "leave", "quit", "stop"),
                          exit_plugin.close_program)
