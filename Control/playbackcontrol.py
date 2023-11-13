class PlaybackControl:
    def __init__(self, client):
        self.client = client

    async def pause(self, voice_client):
        """
        Pauses the currently playing audio in the voice channel.

        :param voice_client: The voice client whose audio is to be paused.
        """
        if voice_client.is_playing():
            print("Pausing")
            voice_client.pause()

    async def resume(self, voice_client):
        """
        Resumes audio playback if it was paused in the voice channel.

        :param voice_client: The voice client whose audio is to be resumed.
        """
        if voice_client.is_paused():
            print("Resuming")
            voice_client.resume()
        else:
            print("Player is not paused")