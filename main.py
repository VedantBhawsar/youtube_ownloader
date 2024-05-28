from pytube import Playlist, YouTube
import pytube
import os
from tqdm import tqdm
import re
import curses
import logging
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import sys


logging.basicConfig(filename='event.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', "", filename)

def download_video(yt, resolution, folder_path, filename, count):
    """Download a single video."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    try:
        stream = yt.streams.filter(res=resolution, file_extension="mp4").first()
        if not stream:
            logging.warning(f"Desired quality {resolution} not available for {yt.title}, downloading the highest quality available.")
            stream = yt.streams.get_highest_resolution()
        
        file_path = os.path.join(folder_path, f"{count} {filename}.mp4")
        if not os.path.exists(file_path):
            global tqdm_instance
            tqdm_instance = tqdm(
                total=stream.filesize,
                desc=f"Downloading: {filename}",
                unit="B",
                unit_scale=True,
            )
            yt.register_on_progress_callback(show_progress_bar)
            stream.download(output_path=folder_path, filename=f"{count} {filename}.mp4")
            tqdm_instance.close()
        else:
            print(f'Already Downloaded: {filename}')
            logging.info(f'Already Downloaded: {filename}')

    except Exception  as e:
        logging.error(f"Failed to download {filename}: {e}")

def show_progress_bar(stream, chunk, file_handle, bytes_remaining=None):
    """Display the download progress bar."""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining if bytes_remaining is not None else total_size
    progress = bytes_downloaded / total_size
    tqdm_instance.update(len(chunk))
    tqdm_instance.set_postfix({"progress": f"{progress:.2%}"})

def download_playlist(playlist_url, resolution="720p"):
    """Download videos from a playlist."""
    playlist = Playlist(playlist_url)
    playlist_title = sanitize_filename(playlist.title)
    user_download_path = os.path.expanduser('~/Downloads')
    folder_path = os.path.join(user_download_path, playlist_title)

    logging.info(f"Downloading playlist: {playlist.title}")
    count = 1
    for video_url in playlist.video_urls:
        yt = YouTube(video_url)
        video_title = sanitize_filename(yt.title)

        try:
            logging.info(f"Downloading {yt.title} at {resolution}")
            download_video(yt, resolution, folder_path, video_title, count)
        except Exception as e:
            logging.error(f"Failed to download {yt.title}: {e}")
        count += 1
    print("Download completed")

def select_resolution():
    """Select resolution using prompt_toolkit."""
    resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
    completer = WordCompleter(resolutions)

    selected_resolution = prompt('Enter resolution: ', completer=completer)
    while selected_resolution not in resolutions:
        print("Invalid resolution. Please choose from the available options.")
        selected_resolution = prompt('Select resolution: ', completer=completer)

    return selected_resolution

if __name__ == "__main__":
    try:
        playlist_url = input("Enter the playlist URL: ")
        resolution = input("Enter the resolution (eg: 480p, 1080p): ")

        download_playlist(playlist_url, resolution)
    except KeyboardInterrupt:
        logging.info("Download interrupted by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
