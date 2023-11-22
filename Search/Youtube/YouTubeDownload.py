import os
from pytube import YouTube
from colorama import Fore

from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler
from util.FileSearch import FileSearch
from config import DOWNLOAD_FOLDER, VIDEO_MAX_LENGTH

# Need to make a config or env variable for this.
download_folder = DOWNLOAD_FOLDER
video_max_length = VIDEO_MAX_LENGTH  # maximum length of a video in seconds.

class YouTubeDownload:
    currently_downloading = set()

    @staticmethod
    async def is_downloading(url):
        """
        Checks if the given URL is currently being downloaded.

        :param url: The URL to check.
        :return: True if the URL is currently being downloaded, False otherwise.
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDownload.is_downloading()')
        return url in YouTubeDownload.currently_downloading

    @staticmethod
    async def find_file(video_id):
        """
        Searches for an existing downloaded file based on the video ID.

        :param video_id: The ID of the video to search for.
        :return: The path of the existing file if found, None otherwise.
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDownload.find_file()')
        return FileSearch.find_existing_file(download_folder, video_id)

    @staticmethod
    async def is_video_too_long(url):
        """
        Checks if the video at the given URL exceeds the maximum allowed length.

        :param url: The URL of the video to check.
        :return: True if the video length is greater than the maximum allowed length, False otherwise.
        """
        print(Fore.LIGHTCYAN_EX + f'\nYouTubeDownload.is_video_too_long() < {video_max_length} ?')
        return await YouTubeDataHandler.fetch_video_length(url) > video_max_length

    @staticmethod
    async def download_file(url, video_id):
        """
        Downloads the audio from the YouTube video specified by the URL.

        :param url: The URL of the YouTube video to download.
        :param video_id: The video ID of the YouTube video.
        :return: The file path of the downloaded audio file if successful, None otherwise.
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDownload.download_file()')
        yt = YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        if audio_stream:
            try:
                extension = audio_stream.mime_type.split('/')[-1]
                filename = f"{video_id}.{extension}"
                file_path = os.path.join(download_folder, filename)
                YouTubeDownload.currently_downloading.add(url)
                print(f'\tDownloading {url}')
                audio_stream.download(output_path=download_folder, filename=filename)
                return file_path
            except Exception as e:
                print(f"\tDownload failed for {url}: {e}")
                return None
            finally:
                YouTubeDownload.currently_downloading.remove(url)
        return None

    @staticmethod
    async def download_audio(url, video_id):
        """
        Manages the process of downloading audio from a YouTube URL.

        This includes checking if the video is currently downloading, if it's already downloaded, 
        and if its length exceeds the maximum limit before initiating the download.

        :param url: The YouTube URL to download audio from.
        :param video_id: The video ID of the YouTube video.
        :return: The file path of the downloaded audio file if successful, None otherwise.
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDownload.download_audio()')
        if await YouTubeDownload.is_downloading(url):
            print('\t Already Downloading.')    
            return None

        print(f'\t{video_id}')
        existing_file = await YouTubeDownload.find_file(video_id)
        if existing_file:
            print(f'\tSkipping download, file exists: {existing_file}')
            return existing_file

        if await YouTubeDownload.is_video_too_long(url):
            print('\tVideo too long')
            return None

        return await YouTubeDownload.download_file(url, video_id)
