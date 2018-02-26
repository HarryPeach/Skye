class SamplePlugin(object):
    """ A sample plugin to demonstrate the module system """
    def __init__(self, skye):
        self.skye = skye

    def sample_run(self):
        self.skye.speak("Say a word")
        word = self.skye.active_listen()
        if (word != -1 and
            word != -2 and
                word != -3):
            self.skye.speak(f"You said: {word}")
        else:
            self.skye.speak("There was an error understanding you.")


def setup(skye):
    sample_plugin = SamplePlugin(skye)
    skye.register_command(("test", "sample"), sample_plugin.sample_run)
