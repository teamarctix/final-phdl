import os
import yt_dlp
from pyrogram import Client
from urllib.parse import urlparse, parse_qs

api_id = "11405252"
api_hash = "b1a1fc3dc52ccc91781f33522255a880"
bot_token = "6596160785:AAEQBzgwKJ4LRg9n14bJMvkaKw4WGIDTonA"
channel_id = "-1002034630043"

def initialize_client():
    return Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def resolve_channel_id(app, channel_id):
    return app.get_chat(int(channel_id))

def extract_playlist_id(url):
    parsed_url = urlparse(url)
    if "playlist" in parsed_url.path:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('list', [None])[0]
    return None

def download_content(url, save_path):
    options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'writethumbnail': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        
        if 'entries' in info_dict:  # It's a playlist
            playlist_id = extract_playlist_id(url)
            if playlist_id:
                ydl.download([url])
            else:
                print("No playlist ID found. Downloading the single video.")
                ydl.download([info_dict['url']])
        else:  # It's a single video
            ydl.download([url])

if __name__ == "__main__":
    app = initialize_client()

    folder_path = "Downloads"
    video_url = 'https://www.pornhub.com/playlist/4758401'

    download_content(video_url, folder_path)

    with app:
        upload_videos(app, channel_id, folder_path)
