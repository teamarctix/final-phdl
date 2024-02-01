import yt_dlp
import os
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from pyrogram import Client
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram configuration
TELEGRAM_BOT_TOKEN = '6596160785:AAEQBzgwKJ4LRg9n14bJMvkaKw4WGIDTonA'
TELEGRAM_CHANNEL_ID = -1002034630043 
TELEGRAM_API_ID = 11405252 
TELEGRAM_API_HASH = 'b1a1fc3dc52ccc91781f33522255a880'

# YouTube configuration
PLAYLIST_URL = os.getenv('PLAYLIST_URL', 'https://youtube.com/playlist?list=PL3b0A8gfzTYWlc521bm7R2LibJRwcxidd&si=RYt6WJ9i25btrBFN')
VIDEO_QUALITY = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'

# Download configuration
OUTPUT_PATH = 'downloads'
MAX_CONCURRENT_DOWNLOADS = 3

# Lock for Pyrogram client access
pyrogram_lock = threading.Lock()

def send_to_telegram(video_file):
    try:
        with pyrogram_lock:
            app = Client("my_session", api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_BOT_TOKEN)
            app.start()

            try:
                logger.info(f"Sending video to Telegram channel: {video_file}")
                app.send_video(TELEGRAM_CHANNEL_ID, video=video_file, supports_streaming=True)
                logger.info("Video successfully sent to Telegram channel")

                # Remove the downloaded file after successful upload
                os.remove(video_file)
                logger.info(f"File {video_file} removed")
            except Exception as e:
                logger.error(f"Error sending video to Telegram: {e}")
            finally:
                app.stop()
    except Exception as e:
        logger.error(f"Error: {e}")

def send_link_file_to_telegram():
    try:
        with pyrogram_lock:
            app = Client("my_session", api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_BOT_TOKEN)
            app.start()

            try:
                # Send link.txt file to Telegram as a document
                logger.info("Sending link.txt file to Telegram")
                with open('link.txt', 'rb') as link_file:
                    app.send_document(TELEGRAM_CHANNEL_ID, document=link_file, caption="Links from link.txt")
                logger.info("link.txt file successfully sent to Telegram")

                # Remove the link.txt file after successful upload
                os.remove('link.txt')
                logger.info("link.txt file removed")
            except Exception as e:
                logger.error(f"Error sending link.txt to Telegram: {e}")
            finally:
                app.stop()
    except Exception as e:
        logger.error(f"Error: {e}")




def download_video(url, semaphore=None):
    ydl_opts = {
        'quiet': False,
        'outtmpl': f'{OUTPUT_PATH}/%(title)s.%(ext)s',
        'format': VIDEO_QUALITY,
        'nooverwrites': True,
        'no_warnings': False,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = f"{OUTPUT_PATH}/{info['title']}.{info['ext']}"
            # Append the video link to link.txt
            with open('link.txt', 'a') as link_file:
                link_file.write(f"{url}\n")
    except yt_dlp.DownloadError as e:
        print(f"Error downloading {url}: {e}")
        return
    finally:
        # Release the semaphore when the thread is done
        semaphore.release()

    # Use the event loop to call the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_telegram(video_file))

def parallel_video_downloads():
    # Extract playlist links
    with yt_dlp.YoutubeDL({'quiet': False, 'extract_flat': True}) as ydl:
        playlist_info = ydl.extract_info(PLAYLIST_URL, download=False)
        links = [entry['url'] for entry in playlist_info['entries']]

    # Create a semaphore to limit concurrent downloads
    semaphore = threading.Semaphore(MAX_CONCURRENT_DOWNLOADS)

    # Create a ThreadPoolExecutor with a maximum number of threads for downloads
    with ThreadPoolExecutor(MAX_CONCURRENT_DOWNLOADS) as executor:
        # Submit each video download as a task
        futures = [executor.submit(download_video, link, semaphore) for link in links]

        # Wait for all download tasks to complete
        wait(futures)

    # Send link.txt file to Telegram after all files have been processed
    send_link_file_to_telegram()

if __name__ == "__main__":
    # Perform parallel video downloads based on the specified configurations
    parallel_video_downloads()
