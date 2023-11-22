from colorama import Fore
from Search.Youtube.YouTubeDownload import YouTubeDownload
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler
from config import DOWNLOAD_THRESHOLD

class QueueControl:
    current_songs = {}  # Dictionary to store current song for each guild
    song_queues = {}
    download_threshold = DOWNLOAD_THRESHOLD # only download songs within this from the front.

    @staticmethod
    async def add_song(guild_id, url):
        """
        Adds a song to the queue. If the song is not downloaded, it downloads it first.
        :param guild_id: ID of the guild.
        :param url: URL of the YouTube video.
        :return: the index where the song was put.
        """
        print(Fore.LIGHTCYAN_EX + '\nQueueControl.add_song:')
        if guild_id not in QueueControl.song_queues:
            QueueControl.song_queues[guild_id] = [] 

        QueueControl.song_queues[guild_id].append(url)
        print(f'\tSong added: {url}') 
        await QueueControl.trigger_event('song added', guild_id, url)
    
    @staticmethod
    async def remove_song(guild_id, song_index=0):
        """
        Removes a song from the queue of the specified guild based on its index in the queue.
    
        By default, it removes the first song in the queue, which is typically the currently playing song.
        If the specified index is out of range, no song is removed.
    
        :param guild_id: ID of the guild.
        :param song_index: Index of the song in the queue to be removed. Default is 0 (the first song).
        :return: The removed song's data, if removal was successful; otherwise, None.
        """
        print(Fore.LIGHTCYAN_EX + '\nQueueControl.remove_song:')
        if guild_id in QueueControl.song_queues and 0 <= song_index < len(QueueControl.song_queues[guild_id]):
            removed_song_data = QueueControl.song_queues[guild_id].pop(song_index)
            print(f'\tSong removed: {removed_song_data}')
            await QueueControl.trigger_event('song removed', guild_id, removed_song_data)  # Announce we removed an item from a queue.
            return removed_song_data
        else:
            print('\tNo song removed (index out of range or queue empty).')
            return None
        
    @staticmethod
    async def trigger_event(event_type, guild_id, song):
        """
        Triggers an event related to the song queue.

        :param event_type: The type of event to trigger. Can be 'song added' or 'song removed'.
        :param guild_id: ID of the guild where the event occurred.
        """
        print(Fore.LIGHTCYAN_EX + '\nQueueControl.trigger_event()')
        print(Fore.GREEN + '\t!!!! Queue Event !!!!')
        print(Fore.YELLOW + f'\t{event_type}: {song}')
        if event_type in ['song added', 'song removed']:
            await QueueControl.handle_queue_update(guild_id)
    
    # We are doing this so we only download the first few songs that are ready to play, then when we move items up in the queue we download the next.
    # This is the only thing tightly coupled to YouTube for now. We'll need to make a machine for dependency injection at some point.

    @staticmethod
    async def handle_queue_update(guild_id):
        """
        Handles updates to the song queue. Downloads songs if they are within the download threshold and not already downloaded.
        Also fetches and stores song data like title, length, etc., for each song in the queue.

        :param guild_id: ID of the guild whose queue is being updated.
        """
        print(Fore.LIGHTCYAN_EX + f'\nQueueControl.handle_queue_update()')
        if guild_id not in QueueControl.song_queues:
            return

        queue = QueueControl.song_queues[guild_id]
        for i in range(min(QueueControl.download_threshold, len(queue))):
            item = queue[i]
            if isinstance(item, str) and item.startswith("http"):
                # Fetch song data
                song_data = await YouTubeDataHandler.fetch_video_data(item)

                # Initiate possible download
                downloaded_file_path = await YouTubeDownload.download_audio(song_data['url'], song_data['id'])
                if downloaded_file_path:
                    print(f'\tdownload_path: {downloaded_file_path} in position {i} for {guild_id}')
                    song_data['download_path'] = downloaded_file_path
                    QueueControl.song_queues[guild_id][i] = song_data

    @staticmethod
    async def clear(guild_id):
        """
        Clears the song queue for a specified guild.

        :param guild_id: ID of the guild whose queue needs to be cleared.
        """
        print(Fore.LIGHTCYAN_EX + '\nQueueControl.clear()')
        if guild_id in QueueControl.song_queues:
            QueueControl.song_queues[guild_id] = []
            await QueueControl.retrieve(guild_id)

    
    @staticmethod
    async def retrieve(guild_id):
        """
        Retrieves the current song queue for a specified guild.

        :param guild_id: ID of the guild whose song queue is to be retrieved.
        :return: A list of songs in the queue. Returns an empty list if the queue does not exist.
        """
        print(Fore.LIGHTCYAN_EX + '\nQueueControl.retrieve()')
        queue = QueueControl.song_queues.get(guild_id, [])
        print('\tQueue is now:')
        for song in queue:
            if isinstance(song, dict):
                for key, value in song.items():
                    print(f'\t\t{key}: {value}')
            else:
                print(f'\t\tSong URL: {song}')
            print('')
        return queue