import os
import yt_dlp
from pyrogram import Client
import asyncio

api_id = "11405252"
api_hash = "b1a1fc3dc52ccc91781f33522255a880"
bot_token = "6596160785:AAEQBzgwKJ4LRg9n14bJMvkaKw4WGIDTonA"
channel_id = "-1002034630043"

def initialize_client():
    return Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

async def resolve_channel_id(app, channel_id):
    if not app.is_initialized:
        await app.start()  # Start the client if not already started
    return await app.get_chat(int(channel_id))

async def upload_single_video(app, channel_id, folder_path, video):
    resolved_channel = await resolve_channel_id(app, channel_id)
    video_path = os.path.join(folder_path, video)

    # Additional parameters
    caption = video.replace(".mp4", "")
    video_name = os.path.splitext(video)[0]  # Remove the file extension
    thumbnail_extensions = ['.png', '.jpg', '.webp']

    # Attempt to find a suitable thumbnail with different extensions
    for ext in thumbnail_extensions:
        thumb = os.path.join(folder_path, f"{video_name}{ext}")
        if os.path.exists(thumb):
            break

    # Print the thumbnail path for debugging
    print(f"Thumbnail Path: {thumb}")

    # Check if the thumbnail file exists before trying to open it
    if os.path.exists(thumb):
        # Sending video with additional parameters
        await app.send_video(
            resolved_channel.id,
            video_path,
            caption=caption,
            thumb=thumb,
            supports_streaming=True,
            progress=progress
        )

        print(f"Successfully sent the file: {video}")
        os.remove(video_path)
        print(f"Removed the file: {video}")
    else:
        print(f"No suitable thumbnail file found for: {video}")


async def upload_videos(app, channel_id, folder_path):
    if not app.is_initialized:
        await app.start()  # Start the client if not already started

    videos = [video for video in os.listdir(folder_path) if video.endswith(".mp4")]

    if videos:
        for video in videos:
            await upload_single_video(app, channel_id, folder_path, video)
    else:
        print("No video files found in the folder.")

def download_content(url, save_path):
    options = {
        'format': 'bestvideo[height=360]+bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'writethumbnail': True,
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
    video_url = 'https://youtube.com/playlist?list=PL9bw4S5ePsEEqCMJSiYZ-KTtEjzVy0YvK&si=k26FJHJy85Qb9bHZ'

    download_content(video_url, folder_path)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(upload_videos(app, channel_id, folder_path))

    if app.is_initialized:
        loop.run_until_complete(app.stop())  # Stop the client if it was started
