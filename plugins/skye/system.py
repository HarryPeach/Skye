"""
    Default System management plugin
"""
import logging
import subprocess


class SystemPlugin(object):
    """ Controls system features such as shutdown """

    def __init__(self, skye):
        self.skye = skye

    def shutdown_system(self):
        """Shuts down the host system
        """
        if self.confirm_action("shut down"):
            logging.debug("Performing shutdown action")
            self.skye.speak("Shutting down system")
            subprocess.call(["shutdown", "/s"])
        else:
            logging.debug("Shutdown action cancelled by user")
            self.skye.speak("Action cancelled")

    def logout_system(self):
        """Logs out the host system
        """
        if self.confirm_action("log out"):
            logging.debug("Performing logout action")
            self.skye.speak("Logging out of system")
            subprocess.call(["shutdown", "/l"])
        else:
            logging.debug("Logout action cancelled by user")
            self.skye.speak("Action cancelled")

    def restart_system(self):
        """Restarts the host system
        """
        if self.confirm_action("restart"):
            logging.debug("Performing restart action")
            self.skye.speak("Restarting system")
            subprocess.call(["shutdown", "/r"])
        else:
            logging.debug("Restart action cancelled by user")
            self.skye.speak("Action cancelled")

    def confirm_action(self, action):
        """Asks a user for confirmation before performing
        an action

        Arguments:
            action {string} -- The action to be performed

        Returns:
            boolean -- Whether the user confirmed the action or not
        """
        self.skye.speak(f"Are you sure you want to {action}?")
        word = self.skye.active_listen()
        if (word != -1 and
            word != -2 and
                word != -3):
            if word == "yes":
                return True
            elif word == "no":
                return False
        else:
            self.skye.speak("There was an error understanding you.")


def setup(skye):
    """Called when the plugin is set up. Used to register commands and other
    initializations

    Arguments:
        skye {Skye} -- The singleton Skye instance
    """
    system_plugin = SystemPlugin(skye)
    skye.register_command(("shutdown", "shut down", "turn off"),
                          system_plugin.shutdown_system)
    skye.register_command(("logout", "log out"),
                          system_plugin.logout_system)
    skye.register_command(("restart", "reboot"),
                          system_plugin.restart_system)
