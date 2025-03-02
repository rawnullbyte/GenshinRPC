import asyncio
import genshin
import websockets
import json
import base64
import zlib
import logging
import os
import colorama
import requests
import pytz
from colorama import Fore, Back, Style
from PIL import Image
from io import BytesIO
import term_image
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Initialize colorama for cross-platform color support
colorama.init(autoreset=True)

DISCORD_TOKEN = "" # Discord account token
CLAIM_DAILY_REWARDS = True  # Set to False if you don't want to claim daily rewards
GENSHIN_UID = 12345
V2UID = 12345
V2TOKEN = "v2_......."
GAME_SERVER = "os_euro"
# Other servers:
# os_usa - North America
# os_asia - Asia
# os_cht - TW/HK/MO
# os_euro - Europe

# Configure logging with colors
def setup_logger():
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    return logger

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_name = getattr(record, 'task', 'Unknown')
        
        if record.levelno == logging.INFO:
            color = Fore.CYAN + Style.BRIGHT
            time_color = Fore.GREEN
            message_color = Fore.WHITE + Style.BRIGHT
        elif record.levelno == logging.WARNING:
            color = Fore.YELLOW + Style.BRIGHT
            time_color = Fore.YELLOW
            message_color = Fore.YELLOW + Style.BRIGHT
        elif record.levelno == logging.ERROR:
            color = Fore.RED + Style.BRIGHT
            time_color = Fore.RED
            message_color = Fore.RED + Style.BRIGHT
        else:
            color = Fore.WHITE + Style.BRIGHT
            time_color = Fore.WHITE
            message_color = Fore.WHITE
        
        return f"{color}[{task_name}] {time_color}{current_time}: {message_color}{record.getMessage()}{Style.RESET_ALL}"

class DiscordSelfBot:
    def __init__(self, token):
        self.token = token
        self.ws = None
        self.logger = setup_logger()

    async def connect(self):
        extra = {'task': 'DiscordRPC'}
        self.logger.info(f"{Fore.CYAN}Connecting to Discord WebSocket...{Style.RESET_ALL}", extra=extra)
        self.ws = await websockets.connect('wss://gateway.discord.gg/?v=9&encoding=json', max_size=None)
        self.logger.info(f"{Fore.GREEN}WebSocket connection established.{Style.RESET_ALL}", extra=extra)
        await self.identify()

    async def identify(self):
        extra = {'task': 'DiscordRPC'}
        self.logger.info(f"{Fore.CYAN}Sending identification payload to Discord...{Style.RESET_ALL}", extra=extra)
        identify_payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 16381,
                "properties": {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": ""
                },
                "intents": 0
            }
        }
        await self.ws.send(json.dumps(identify_payload))
        self.logger.info(f"{Fore.GREEN}Identification payload sent.{Style.RESET_ALL}", extra=extra)
        await self.receive_hello()

    async def receive_hello(self):
        while True:
            message = await self.ws.recv()
            data = json.loads(message)
            if data.get('op') == 10:  # Hello event
                heartbeat_interval = data['d']['heartbeat_interval']
                asyncio.create_task(self.send_heartbeat(heartbeat_interval))
                break

    async def send_heartbeat(self, interval):
        extra = {'task': 'DiscordHeartbeat'}
        while True:
            await asyncio.sleep(interval / 1000)
            heartbeat_payload = {"op": 1, "d": None}
            await self.ws.send(json.dumps(heartbeat_payload))
            self.logger.info(f"{Fore.CYAN}Heartbeat sent{Style.RESET_ALL}", extra=extra)

    async def update_activity(self, details, state):
        extra = {'task': 'DiscordRPC'}
        self.logger.info(f"{Fore.CYAN}Updating Discord activity...{Style.RESET_ALL}", extra=extra)
        activity_payload = {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [{
                    "type": 0,
                    "name": "Genshin Impact",
                    "application_id": "1261185993000747150",
                    "details": details[:128],
                    "state": state[:128],
                    "assets": {
                        "large_image": "1269863139680194681",
                        "large_text": "Genshin Impact"
                    }
                }],
                "status": "online",
                "afk": False
            }
        }
        await self.ws.send(json.dumps(activity_payload))
        self.logger.info(f"{Fore.GREEN}Activity updated with details: {Fore.YELLOW}{details}{Fore.GREEN}, state: {Fore.YELLOW}{state}{Style.RESET_ALL}", extra=extra)

def display_reward_image(reward):
    try:
        response = requests.get(reward.icon)
        img = Image.open(BytesIO(response.content))
        term_image.image(img)
    except Exception as e:
        print(f"{Fore.RED}Could not display image: {e}{Style.RESET_ALL}")

async def claim_daily_reward(client, logger):
    extra = {'task': 'DailyClaim'}
    try:
        logger.info(f"{Fore.CYAN}Attempting to claim daily rewards...{Style.RESET_ALL}", extra=extra)
        reward = await client.claim_daily_reward()
        logger.info(f"{Fore.GREEN}Successfully claimed daily reward: {Fore.YELLOW}{reward}{Style.RESET_ALL}", extra=extra)
        display_reward_image(reward)
    except genshin.AlreadyClaimed:
        logger.info(f"{Fore.YELLOW}Daily rewards already claimed today.{Style.RESET_ALL}", extra=extra)
    except Exception as e:
        logger.error(f"{Fore.RED}Error claiming daily rewards: {e}{Style.RESET_ALL}", extra=extra)

async def update_player_data(client, discord_bot, logger):
    extra = {'task': 'DiscordRPC'}
    try:
        logger.info(f"{Fore.CYAN}Fetching updated Genshin user data...{Style.RESET_ALL}", extra=extra)
        data = await client.get_genshin_user(GENSHIN_UID)
        
        details = f"{data.info.nickname}"
        state = f"Lv.{data.info.level} | Europe"

        await discord_bot.update_activity(details, state)
    except Exception as e:
        logger.error(f"{Fore.RED}Error updating player data: {e}{Style.RESET_ALL}", extra=extra)

async def scheduled_update_player_data(client, discord_bot, logger):
    await update_player_data(client, discord_bot, logger)

async def scheduled_claim_daily_reward(client, logger):
    await claim_daily_reward(client, logger)

async def main():
    logger = setup_logger()
    extra = {'task': 'DiscordRPC'}
    logger.info(f"{Fore.CYAN}Starting Genshin Impact Discord RPC script...{Style.RESET_ALL}", extra=extra)
    
    logger.info(f"{Fore.CYAN}Using Discord token: {Fore.YELLOW}{DISCORD_TOKEN}{Style.RESET_ALL}", extra=extra)

    cookies = {
        "ltuid_v2": V2UID,
        "ltoken_v2": V2TOKEN,
        "server": GAME_SERVER
    }
    logger.info(f"{Fore.CYAN}Initializing Genshin client...{Style.RESET_ALL}", extra=extra)
    client = genshin.Client(cookies)
    client.default_game = genshin.Game.GENSHIN

    discord_bot = DiscordSelfBot(DISCORD_TOKEN)
    await discord_bot.connect()

    if CLAIM_DAILY_REWARDS:
        await claim_daily_reward(client, logger)

    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    if CLAIM_DAILY_REWARDS:
        scheduler.add_job(
            scheduled_claim_daily_reward,
            'interval',
            hours=24,
            args=[client, logger],
            name='Daily Reward Claim'
        )
    
    scheduler.add_job(
        scheduled_update_player_data,
        'interval',
        minutes=5,
        args=[client, discord_bot, logger],
        name='Player Data Update'
    )

    logger.info(f"{Fore.CYAN}Fetching initial Genshin user data...{Style.RESET_ALL}", extra=extra)
    data = await client.get_genshin_user(727488232)
    
    details = f"{data.info.nickname}"
    state = f"Lv.{data.info.level} | Europe"

    await discord_bot.update_activity(details, state)

    scheduler.start()

    logger.info(f"{Fore.GREEN}Keeping connection alive...{Style.RESET_ALL}", extra=extra)
    while True:
        logger.info(f"{Fore.CYAN}Sleeping for 30 seconds...{Style.RESET_ALL}", extra=extra)
        await asyncio.sleep(30)

asyncio.run(main())