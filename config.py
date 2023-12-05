import os

# Path to the directory of the running script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Set download folder to 'downloads' subdirectory within the base directory
DOWNLOAD_FOLDER = os.path.join(base_dir, 'downloads')

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

VIDEO_MAX_LENGTH = 10800  # Maximum length of a video in seconds
DOWNLOAD_THRESHOLD = 5    # Only download songs within this from the front