"""
    The Onboarding Utilities Class
"""

class Onboarding(object):
    def __init__(self, skye):
        self.skye = skye

    def onboard(self):
        """ Function to manage onboarding features """
        wake_word = self.skye.config.get("general", "wake_word")

        # Introduce self to the user
        self.skye.speak("Hi, I'm Skye, your open virtual assistant.")
        self.skye.speak("Let's set up a few things before we begin.")
        self.skye.speak("Your current wake word is: " + wake_word)

        # Try a sample command with the wake word
        self.skye.speak("Let's try a sample command.")
        self.skye.speak(f"Say: {wake_word} hello")
        success_flag = False
        while not success_flag:
            words = self.skye.active_listen()
            if (words != -1 and
                words != -2 and
                    words != -3):
                if words == f"{wake_word} hello":
                    self.skye.speak("Good, the command was a success.")
                    success_flag = True
            else:
                self.skye.speak("Sorry, I didn't understand you.")
        self.skye.speak("That's it! Setup was successful.")

        # Change onboarding config option
        self.skye.config.set("general", "onboarding", "False")
        with open(self.skye.config_location + "config.ini", 'w') as config_file:
            self.skye.config.write(config_file)