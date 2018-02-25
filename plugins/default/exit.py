"""
    Default exit plugin
"""


class ExitPlugin(object):
    def quit():
        pass


def setup(skye):
    exit_plugin = ExitPlugin(skye)
    skye.register_command('exit', quit)