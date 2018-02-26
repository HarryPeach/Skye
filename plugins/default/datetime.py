"""
    Default date time plugin
    Date suffix courtesy of 'Acorn' on StackOverflow:
        https://stackoverflow.com/a/5891598
"""
import datetime
import logging


class DateTimePlugin(object):
    """ Tells the user the current date or time """

    def __init__(self, skye):
        self.skye = skye

    def suffix(self, d):
        """ Chooses the date suffix based on its value. """
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd',
                                           3: 'rd'}.get(d % 10, 'th')

    def custom_strftime(self, format, t):
        """ Custom string-time format to add date suffixes """
        return t.strftime(format).replace('{S}', str(t.day) +
                                          self.suffix(t.day))

    def get_date(self):
        """ Gets the date in an understandable format and reads
            it to the user """
        date = self.custom_strftime("The date today is %A, {S} "
                                    "of %B, %Y", datetime.date.today())
        logging.debug("Speaking current date")
        self.skye.speak(date)

    def get_time(self):
        """ Gets the time in an understandable format and reads
            it to the user """
        time = datetime.datetime.now().strftime("The current time is %I:%M")
        logging.debug("Speaking current time")
        self.skye.speak(time)


def setup(skye):
    datetime_plugin = DateTimePlugin(skye)
    skye.register_command(("date", "what's the date", "what day is it",
                          "what is the day", "what's the day",
                           "what is the date"), datetime_plugin.get_date)
    skye.register_command(("time", "what's the time", "what time is it",
                           "what is the time"), datetime_plugin.get_time)
