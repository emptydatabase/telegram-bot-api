import json
import os

from dotenv import load_dotenv

from telegram_bot_api import TelegramClient

load_dotenv()

client = TelegramClient(os.environ["TOKEN"])
offset = 0
while True:
    for update in client.get_updates(offset=offset):
        print(json.dumps(update, indent=2))
        offset = max(offset, update["update_id"] + 1)
