from colorama import init, Fore, Style
from downloadmanager import DownloadManager

# Initialize Colorama
init(autoreset=True)

class QueueControl:
    song_queues = {}
    download_threshold = 5 # only download songs within this from the front.

    @staticmethod
    async def add_song(guild_id, url):
        """
        Adds a song to the queue. If the song is not downloaded, it downloads it first.
        :param guild_id: ID of the guild.
        :param url: URL of the YouTube video.
        :return: the index where the song was put.
        """
        print(Fore.GREEN + '\nQueueControl.add_song:')
        if guild_id not in QueueControl.song_queues:
            QueueControl.song_queues[guild_id] = [] 

        QueueControl.song_queues[guild_id].append(url)
        print(Fore.GREEN + f'\tSong Added!') 
        print(Fore.GREEN + f'\tQueue length is now {len(QueueControl.song_queues[guild_id])}')
        await QueueControl.trigger_event('song added', guild_id)
    
    @staticmethod
    async def remove_song(guild_id, song_index=0):
        """
        Removes a song from the queue of the specified guild based on its index in the queue.
        
        By default, it removes the first song in the queue, which is typically the currently playing song.
        If the specified index is out of range, no song is removed.

        :param guild_id: ID of the guild.
        :param song_index: Index of the song in the queue to be removed. Default is 0 (the first song).
        :return: The removed song, if removal was successful; otherwise, None.
        """
        print(Fore.RED + '\nQueueControl.remove_song:')
        if guild_id in QueueControl.song_queues and 0 <= song_index < len(QueueControl.song_queues[guild_id]):
            QueueControl.song_queues[guild_id].pop(song_index)
            print(Fore.RED + f'\tSong removed!')
            await QueueControl.trigger_event('song removed', guild_id) # Announce we removed an item from a queue.
    
    @staticmethod
    async def trigger_event(event_type, guild_id):
        """
        Triggers an event related to the song queue.

        :param event_type: The type of event to trigger. Can be 'song added' or 'song removed'.
        :param guild_id: ID of the guild where the event occurred.
        """
        print(f'{event_type}')
        if event_type in ['song added', 'song removed']:
            await QueueControl.handle_queue_update(guild_id)
    
    # We are doing this so we only download the first few songs that are ready to play, then when we move items up in the queue we download the next.
    @staticmethod
    async def handle_queue_update(guild_id):
        """
        Handles updates to the song queue. Downloads songs if they are within the download threshold and not already downloaded.

        :param guild_id: ID of the guild whose queue is being updated.
        """
        print(Fore.CYAN + f'\nQueueControl.handle_queue_update()')
        if guild_id not in QueueControl.song_queues:
            return

        queue = QueueControl.song_queues[guild_id]
        print(Fore.CYAN + f'\tqueue length = {len(queue)}')
        for i in range(min(QueueControl.download_threshold, len(queue))):
            item = queue[i]
            print(Fore.CYAN + f'\tQueueControl: loop {item} = {[i]}')
            if isinstance(item, str) and item.startswith("http"):  # Check if the item is a URL
                # It's a URL, initiate download
                downloaded_file_path = await DownloadManager.download_audio(item)
                if downloaded_file_path:
                    QueueControl.song_queues[guild_id][i] = downloaded_file_path  # Update the URL with the file path in the queue

    @staticmethod
    def clear(guild_id):
        """
        Clears the song queue for a specified guild.

        :param guild_id: ID of the guild whose queue needs to be cleared.
        """
        # Check if the guild has an existing queue
        if guild_id in QueueControl.song_queues:
            QueueControl.song_queues[guild_id] = []
    
    @staticmethod
    async def retrieve(guild_id):
        """
        Retrieves the current song queue for a specified guild.
    
        :param guild_id: ID of the guild whose song queue is to be retrieved.
        :return: A list of songs in the queue. Returns an empty list if the queue does not exist.
        """
        # Return the guild's queue if it exists, otherwise return an empty list
        return QueueControl.song_queues.get(guild_id, [])