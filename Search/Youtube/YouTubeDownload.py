import os
from pytube import YouTube
from colorama import Fore
import glob
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler

download_folder = "C:\\test\\"
video_max_length = 10800 # maximum length of a video in seconds.

class YouTubeDownload:
    currently_downloading = set()

    @staticmethod
    def find_existing_file(video_id):
        """
        Searches for an existing downloaded file with the given video ID.

        :param video_id: The YouTube video ID to search for
        :return: Path to the existing file if found, None otherwise
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDownload.find_existing_file()')
        pattern = os.path.join(download_folder, f"{video_id}.*")
        files = glob.glob(pattern)
        return files[0] if files else None


    @staticmethod
    async def download_audio(url):
        """
        Downloads the audio from a YouTube URL.

        :param url: The YouTube URL to download audio from.
        :returns: The file path of the downloaded audio file if successful, None otherwise.
        """
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDownload.download_audio()')       
        if url in YouTubeDownload.currently_downloading:
            return None

        video_id = await YouTubeDataHandler.fetch_video_id(url)
        print(f'\tchecking if downloaded already: {url}')
        existing_file = YouTubeDownload.find_existing_file(video_id)
        if existing_file:
            print(f'\tSkipping download, file exists: {existing_file}')
            return existing_file

        if(await YouTubeDataHandler.fetch_video_length(url)>video_max_length):
            return None

        yt = YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        if audio_stream:
            extension = audio_stream.mime_type.split('/')[-1]
            filename = f"{video_id}.{extension}"
            file_path = os.path.join(download_folder, filename)

            try:
                YouTubeDownload.currently_downloading.add(url)
                audio_stream.download(output_path=download_folder, filename=filename)
                print(f'\tdownloaded {url} to: {file_path}')
                return file_path
            except Exception as e:
                print(f"\tDownload failed for {url}: {e}")
                return None
            finally:
                YouTubeDownload.currently_downloading.remove(url)
                print(f'\tremoved from current download list: {url}\n')

        return None
