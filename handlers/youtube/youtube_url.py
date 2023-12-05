import re
from colorama import Fore

class YouTubeURL:
    def __init__(self):
        pass

    youtube_url_pattern = re.compile(
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )

    def is_youtube_url(self, query) -> bool:
        print(Fore.LIGHTCYAN_EX + '\nYouTubeURL.is_youtube_url()')
        match = self.youtube_url_pattern.match(query)
        print(f'\t{query} = {match}')
        return bool(match)

    def is_playlist_url(self, url) -> bool:
        print(Fore.LIGHTCYAN_EX + '\nYouTubeURLZ.is_playlist_url()')
        print(f'\t {"list=" in url}')
        return "list=" in url