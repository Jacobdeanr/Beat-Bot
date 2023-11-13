class ConnectionControl:
    def __init__(self, client):
        self.client = client

    async def connect(self, voice_channel):
        """
        Connects the bot to a specified voice channel.

        :param voice_channel: The voice channel to connect to.
        :return: The voice client if successful, None otherwise.
        """
        if voice_channel:
            await voice_channel.connect()
            return
        else:
            print(f"I can't find {voice_channel}")
            return
        
    async def disconnect(self, voice_client):
        """
        Disconnects the bot from its current voice channel.

        :param voice_client: The voice client to be disconnected.
        """
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
        else:
            return