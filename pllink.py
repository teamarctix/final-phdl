from pyrogram import Client
import yt_dlp

# Function to extract playlist links
def extract_playlist_links(playlist_url):
    with yt_dlp.YoutubeDL({'quiet': False, 'extract_flat': True}) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        return [entry['url'] for entry in playlist_info['entries']]

# Function to save links to a file
def save_links_to_file(links, filename='links.txt'):
    with open(filename, 'w') as file:
        file.write('\n'.join(links))

# Set your Telegram API credentials
api_id = 11405252
api_hash = "b1a1fc3dc52ccc91781f33522255a880"
bot_token = "6596160785:AAEQBzgwKJ4LRg9n14bJMvkaKw4WGIDTonA"


# Extract links and save them to a file
playlist_url = 'https://www.pornhub.com/playlist/263313231'  # Replace with the actual URL
links = extract_playlist_links(playlist_url)
save_links_to_file(links)

# Initialize Pyrogram client
app = Client('my_bot', api_id, api_hash, bot_token=bot_token)

# Send the file to the Telegram channel
with app:
    app.send_document(-1002034630043, 'links.txt', caption='Playlist links')

print(f"Playlist links sent to the Telegram channel.")
