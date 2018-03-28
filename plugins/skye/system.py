"""
    Default System management plugin
"""
import logging


class SystemPlugin(object):
    """ Controls system features such as shutdown """

    def __init__(self, skye):
        self.skye = skye

    def shutdown_system(self):
        """Shuts down the host system
        """
        logging.debug("Rolling a dice")


def setup(skye):
    """Called when the plugin is set up. Used to register commands and other
    initializations

    Arguments:
        skye {Skye} -- The singleton Skye instance
    """
    system_plugin = SystemPlugin(skye)
    skye.register_command(("shutdown", "shut down", "turn off"),
                          system_plugin.shutdown_system)
