import os
import yt_dlp
from pyrogram import Client

api_id = "11405252"
api_hash = "b1a1fc3dc52ccc91781f33522255a880"
bot_token = "6596160785:AAEQBzgwKJ4LRg9n14bJMvkaKw4WGIDTonA"
channel_id = "-1002034630043"

def initialize_client():
    return Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def resolve_channel_id(app, channel_id):
    return app.get_chat(int(channel_id))

def upload_single_video(app, channel_id, folder_path, video):
    resolved_channel = resolve_channel_id(app, channel_id)
    video_path = os.path.join(folder_path, video)
    app.send_video(resolved_channel.id, video_path)
    print(f"Successfully sent the file: {video}")
    os.remove(video_path)
    print(f"Removed the file: {video}")

def upload_videos(app, channel_id, folder_path):
    videos = [video for video in os.listdir(folder_path) if video.endswith(".mp4")]

    if videos:
        for video in videos:
            upload_single_video(app, channel_id, folder_path, video)
    else:
        print("No video files found in the folder.")

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
            ydl.download([url])
        else:  # It's a single video
            ydl.download([url])

if __name__ == "__main__":
    app = initialize_client()

    folder_path = "Downloads"
    video_url = 'https://youtube.com/playlist?list=PLMC9KNkIncKvYin_USF1qoJQnIyMAfRxl&si=7pXYNvVN1HjVyVRL'

    download_content(video_url, folder_path)

    with app:
        upload_videos(app, channel_id, folder_path)
        
