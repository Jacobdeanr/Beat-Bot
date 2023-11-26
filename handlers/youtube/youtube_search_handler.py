from youtube_search import YoutubeSearch

class YouTubeSearchHandler:
    @staticmethod
    async def search_for_one_song(query: str) -> str:
        """
        Searches YouTube for the given query and returns the URL of the top result.

        :param query: The search query string.
        :return: The URL of the top search result, or None if no results are found.
        """
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()

            if len(results) == 0:
                return None

            url = f"https://www.youtube.com{results[0]['url_suffix']}"
            return url
        except Exception as e:
            return None
