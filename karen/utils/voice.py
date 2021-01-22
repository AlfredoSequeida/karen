import vlc

from gtts import gTTS
from googletrans import Translator
from utils import setup


class Voice:
    """
    voice instance to handle responses and media using vlc bindings
    """

    def __init__(self, config_file_path: str):
        """
        config_file_path: main (global) config file
        """

        self.config_file_path = config_file_path
        self.vlc_instance = vlc.Instance("--no-video")
        self.player = self.vlc_instance.media_player_new()

    def say(self, voice_output: str, lang: str = "en", translate: bool = True):
        """
        say a response

        voice_output: the response
        lang: 639-1 language code for response (default: en)
        translate: option to translate response using google translate
        (default: true)
        """

        settings = (setup.load_config(self.config_file_path))["settings"]

        if translate:
            translator = Translator()
            voice_output = translator.translate(
                voice_output, dest=settings["lang"]
            ).text

        tts = gTTS(voice_output, lang=settings["lang"])
        tts.save("response.mp3")

        media = self.vlc_instance.media_new("response.mp3")

        self.player.set_media(media)
        self.player.play()

    def play_media(self, media_path: str):
        """
        play media

        media_path: the path of media to pay/stream
        """

        media = self.vlc_instance.media_new(media_path)
        media.get_mrl()
        self.player.set_media(media)
        self.player.play()

    def pause(self):
        """
        pause media
        """

        self.player.pause()

    def stop(self):
        """
        stop media
        """

        self.player.stop()
