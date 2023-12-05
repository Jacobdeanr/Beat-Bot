from services.youtube_service import YouTubeService

class AudioServiceFactory:
    def __init__(self):
        self.services = {
            "youtube.com": YouTubeService(),
            # "vimeo.com": VimeoService(),
            # "soundcloud.com": SoundCloudService()
        }
        self.default_service = YouTubeService()  # Set a default service

    def get_service(self, url: str):
        for domain, service in self.services.items():
            if domain in url:
                return service
        return None

    def get_default_service(self):
        return self.default_service
