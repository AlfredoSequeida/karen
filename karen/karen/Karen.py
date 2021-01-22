import speech_recognition as sr

from utils import setup
from utils.voice import Voice

CONFIG_PATH = "config.json"
ADDONS_DIR = "addons"


class Karen:

    """
    main Karen instance
    """

    def __init__(self, config_file_path: str = CONFIG_PATH):
        """
        config_file_path: file path for config file
        """

        self.config_file_path = config_file_path

        self.setup()

        self.config = setup.load_config(self.config_file_path)
        self.settings = self.config["settings"]

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.names = self.settings["names"]

        # voice intance
        self.voice_instance = Voice(self.config_file_path)

    def setup(self):
        """
        setting up Karen
        """

        # create config file
        setup.create_config()

        # check config global file
        setup.check_global_config(self.config_file_path)

        # load addons
        setup.load_addons(self.config_file_path, ADDONS_DIR)

    def parse_args(self, command: str, keyword: str) -> list:
        """
        parse command arguments

        command: the command to parse
        keyword: the keyword that activated the command

        example: play song_name
        using keyword: play
        returns: [song_name]

        another example: play song_name by artist
        using keyword: play
        returns: [song_name, by, artist]
        """

        command_without_keywords = command.replace(keyword, "").strip()
        return command_without_keywords.split()

    def execute_command(self, command: str):
        """
        execute user command

        command: the command to execute
        """

        print(f"Executing {command}")
        command_executed = False
        addons = self.config["addons"]

        # match command to addon
        for addon in addons:
            for command_to_listen_for in addon["commands"]:
                if command_to_listen_for in command:

                    addon = __import__(
                        f"{ADDONS_DIR}.{addon['developer']}_{addon['name']}.{addon['entry-point']}",
                        fromlist=["addons"],
                    )

                    # any possible errors should be handeled by developers
                    # within their addons, if an error is encountered, they
                    # will be ignored as to not halt/break the main instance
                    try:
                        addon.run(
                            command_to_listen_for,
                            self.parse_args(command, command_to_listen_for),
                            self.voice_instance,
                        )
                    except:
                        pass

                    command_executed = True

        if not command_executed:
            self.voice_instance.say("Sorry, I didn't understand that")

    def parse_command(self, voice_input: str) -> str:
        """
        get command from user voice input

        voice_input: the user input as text
        """

        command = ""

        # check for name keyword
        for name in self.names:
            if name in voice_input:
                command = voice_input.split(name)[1].strip()
            else:
                print(f"{name} has not been called")

        return command

    def run(self):
        """
        run instance
        """

        try:
            while True:
                # adjusting for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    print("Say something!")
                    audio = self.recognizer.listen(source)

                print("Got it! Now to recognize it...")
                try:
                    # recognize speech using Google Speech Recognition
                    voice_input = str(
                        self.recognizer.recognize_google(
                            audio, language=self.settings["lang"]
                        )
                    ).lower()

                    # we need some special handling here to correctly print unicode characters to standard output
                    print(f"You said {voice_input}")

                    command = self.parse_command(voice_input)

                    if command:
                        self.execute_command(command)

                except sr.UnknownValueError:
                    print("Oops! Didn't catch that")
                except sr.RequestError as e:
                    print(
                        "Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(
                            e
                        )
                    )
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    karen = Karen()
    karen.run()