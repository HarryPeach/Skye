class SamplePlugin(object):
    """ A sample plugin to demonstrate the module system """
    def __init__(self, skye):
        self.skye = skye

    def sample_run(self):
        print("Sample plugin run")
        self.skye.speak("testing")


def setup(skye):
    sample_plugin = SamplePlugin(skye)
    skye.register_command('sample', sample_plugin.sample_run)
