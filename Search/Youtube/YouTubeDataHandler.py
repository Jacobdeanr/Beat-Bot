from pytube import YouTube
from pytube import Playlist
from pytube import Channel

class YouTubeDataHandler:

#move this into a different class
    @staticmethod
    async def validate_url(url):
        """
        Validates a YouTube URL and returns the standardized watch URL if successful.

        :param url: The URL of the YouTube video.
        :return: The standardized watch URL of the video if valid, None otherwise.
        """
        try:
            video = YouTube(url)
            return video.watch_url  # Returns the standardized watch URL
        except Exception:
            return None
        
#move this into a different class
    @staticmethod
    async def fetch_playlist_urls(playlist_url):
        """
        Fetches individual video URLs from a YouTube playlist URL.

        :param playlist_url: The URL of the YouTube playlist.
        :return: A list of video URLs if successful, None otherwise.
        """
        try:
            results = Playlist(playlist_url)
            if results.length > 0:
                return [url for url in results.video_urls]
            else:
                return None
        except Exception as e:
            return None
        
    @staticmethod
    async def fetch_video_length(url):
        """
        Fetches the length of a YouTube video in seconds.

        :param url: The URL of the YouTube video.
        :return: The length of the video in seconds, or None if an error occurs.
        """
        try:
            video = YouTube(url)
            return video.length
        except Exception as e:
            return None
    
    @staticmethod        
    async def fetch_video_title(url):
        """
        Fetches the title of a YouTube video.

        :param url: The URL of the YouTube video.
        :return: The title of the video, or None if an error occurs.
        """
        try:
            video = YouTube(url)
            return video.title
        except Exception as e:
            return None
    
    @staticmethod    
    async def fetch_video_uploader(url):
        """
        Fetches the channel that uploaded a YouTube video.

        :param url: The URL of the YouTube video.
        :return: The channel of the uploader's video, or None if an error occurs.
        """
        try:
            video = YouTube(url)
            c = Channel(video.channel_url)
            return c.channel_name
        except Exception as e:
            return None
    
    @staticmethod    
    async def fetch_video_id(url):
        """
        Fetches the channel that uploaded a YouTube video.

        :param url: The URL of the YouTube video.
        :return: The id of the video, or None if an error occurs.
        """
        try:
            video = YouTube(url)
            return video.video_id
        except Exception as e:
            return None
        
    @staticmethod
    async def fetch_video_data(url):
        # Use pytube or similar library to fetch video data
        video = YouTube(url)
        return {
            "uploader": video.author,
            "title": video.title,
            "length": video.length,
            "id": video.video_id
        }