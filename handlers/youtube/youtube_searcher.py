from colorama import Fore
from youtube_search import YoutubeSearch

class YouTubeSearcher:
    def __init__(self):
        pass
    
    def search_for_one_song(self,query: str) -> str:
        print(Fore.LIGHTCYAN_EX + '\nYouTubeSearcher.search_for_one_song()')
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()

            if len(results) == 0:
                return None

            url = f"https://www.youtube.com{results[0]['url_suffix']}"
            return url
        except Exception as e:
            return None
