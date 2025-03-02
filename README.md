
# Genshin Impact Discord RPC

A Discord Rich Presence client for Genshin Impact that displays your in-game information and automatically claims daily rewards.

## Features

- Displays your Genshin Impact nickname and level on Discord
- Automatic daily reward claiming
- Real-time status updates every 5 minutes
- Cross-platform support
- Colored console logging

## Prerequisites

- Python 3.8 or higher
- A Discord account
- HoYoLAB account

## Installation

1. Clone this repository:
```bash
git clone https://github.com/rawnullbyte/GenshinRPC.git
cd GenshinRPC
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## How to Get Required Parameters

### Discord Token

Method 1 (Easy):
1. Install [Discord Tools](https://chromewebstore.google.com/detail/discord-tools/encmchanjcanmoijgilfplklckhidnhh) extension
2. Open Discord in your browser
3. Click on the extension icon
4. Copy your token

Method 2 (Manual):
1. Open Discord in your browser
2. Press F12 to open Developer Tools
3. Go to the "Network" tab
4. Click on "Preserve log"
5. Press Ctrl+R to refresh the page
6. Type "/api" in the filter box
7. Look for a request with "science" or "messages"
8. Find the "authorization" header in the request
9. Copy the token value

### V2 UID and Token (HoYoLAB)
1. Go to [HoYoLAB](https://www.hoyolab.com/)
2. Log in to your account
3. Press F12 to open Developer Tools
4. Go to "Application" tab
5. Click on "Cookies" in the left sidebar
6. Look for these cookies:
   - `ltuid_v2` (This is your V2UID)
   - `ltoken_v2` (This is your V2TOKEN)

### Genshin UID
1. Open Genshin Impact
2. Open the in-game menu
3. Click on your profile icon
4. Your UID will be shown in the bottom right corner

### Game Server
Choose your server from the following options:
- `os_usa` - North America
- `os_euro` - Europe
- `os_asia` - Asia
- `os_cht` - TW/HK/MO

## Configuration

Edit the following variables in the script:

```python
DISCORD_TOKEN = "your_discord_token"
CLAIM_DAILY_REWARDS = True  # Set to False if you don't want to claim daily rewards
GENSHIN_UID = your_genshin_uid
V2UID = your_v2_uid
V2TOKEN = "your_v2_token"
GAME_SERVER = "your_server"  # e.g., "os_euro"
```

## Usage

Run the script:
```bash
python main.py
```

## Notes

- Keep your tokens private and never share them
- The script needs to run continuously to update your Discord status
- Daily rewards are claimed automatically at the same time each day
- If you encounter any errors, check the console output for detailed information

## License

MIT License - feel free to modify and distribute as you like!
