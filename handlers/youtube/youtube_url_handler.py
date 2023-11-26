import re
from colorama import Fore

class YouTubeURLHandler:
    # Compiled regular expression to match YouTube URLs
    youtube_url_pattern = re.compile(
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )

    @staticmethod
    def validate_url(query):
        """
        Validates whether a given query string is a YouTube URL.
        It checks against both full YouTube URLs and shortened youtu.be URLs.

        :param query: The query string which may contain a YouTube URL.
        :return: True if the query is a valid YouTube URL, False otherwise.
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeURLHandler.validate_url()')
        match = YouTubeURLHandler.youtube_url_pattern.match(query)
        print(f'\t{query} = {match}')
        return bool(match)

    @staticmethod
    def is_playlist_url(url):
        """
        Determines if a given YouTube URL is a playlist URL.
        This method checks whether the URL contains playlist parameters,
        which is useful for distinguishing between individual video URLs and playlist URLs.

        :param url: The YouTube URL to check.
        :return: True if the URL is a playlist URL, False otherwise.
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeURLHandler.is_playlist_url()')
        print(f'\t {"list=" in url}')
        return "list=" in url