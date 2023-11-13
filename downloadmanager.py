import os
from pytube import YouTube
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler

# Define global variable for download folder
download_folder = "C:\\test\\"

class DownloadManager:
    currently_downloading = set()

    @staticmethod
    async def download_audio(url):
        if url in DownloadManager.currently_downloading:
            return None

        print(f'\nDownloadManager.download_audio(url)\nTrying to download video: {url}')
        video_id = YouTubeDataHandler.fetch_video_id(url)
        yt = YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        if audio_stream:
            extension = audio_stream.mime_type.split('/')[-1]
            filename = f"{video_id}.{extension}"
            file_path = os.path.join(download_folder, filename)

            # Check if the file already exists
            if os.path.exists(file_path):
                print(f'\n Skipping download, the file already exists! {file_path}')
                return file_path  # File already downloaded, return the existing file path

            try:
                DownloadManager.currently_downloading.add(url)
                audio_stream.download(output_path=download_folder, filename=filename)
                print(f'downloaded {url} to: {file_path}')
                return file_path
            except Exception as e:
                print(f"Download failed for {url}: {e}")
                return None
            finally:
                DownloadManager.currently_downloading.remove(url)
                print(f'\nremoved from current download list: {url}\n')

        return None
