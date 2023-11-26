from colorama import Fore
from downloaders.download_decision_maker import DownloadDecisionMaker
from downloaders.audio_download_manager import AudioDownloadManager

class YouTubeDownload:
    def __init__(self, decision_maker: DownloadDecisionMaker, download_manager: AudioDownloadManager):
        self.decision_maker = decision_maker
        self.download_manager = download_manager

    async def download_audio(self, url: str, id: str, duration: int) -> str:
        print(Fore.LIGHTCYAN_EX + 'YouTubeDownload.download_audio()')

        decision = await self.decision_maker.should_download(url=url, stem=id, duration=duration)
        if decision is True:
            return await self.download_manager.download_audio(url=url, stem=id)

        elif isinstance(decision, str):
            return decision
        return None