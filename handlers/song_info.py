import datetime

class SongInfo:
    def __init__(
        self, 
        uploader: str = "", 
        title: str = "", 
        length: int = -1, 
        id: str = "",
        publish_date: datetime = datetime.datetime.min, 
        channel_id: str = "", 
        channel_name: str = "",
        url: str = "", 
        full_path: str = "",
        audio_stream: str = ""
    ): 
        self.uploader = uploader
        self.title = title
        self.length = length
        self.id = id
        self.publish_date = publish_date
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.url = url
        self.full_path = full_path
        self.audio_stream = audio_stream
        
    def __str__(self):
        return (
            f"SongInfo(\n"
            f"  uploader='{self.uploader}',\n"
            f"  title='{self.title}',\n"
            f"  length={self.length},\n"
            f"  id='{self.id}',\n"
            f"  publish_date='{self.publish_date}',\n"
            f"  channel_id='{self.channel_id}',\n"
            f"  channel_name='{self.channel_name}',\n"
            f"  url='{self.url}',\n"
            f"  full_path='{self.full_path}'\n"
            ")"
        )

    #Example of how to call this:
    # song = SongInfo(uploader="John Doe", title="Old Title", length=300)
    # song.update_song_info(title="New Title", length=350)
    def update_song_info(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

