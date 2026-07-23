# telegram-bot-api

A Python wrapper for the [Telegram Bot API](https://core.telegram.org/bots/api).

## Requirements

- Python 3.12+
- `requests`

## Installation

```sh
pip install https://github.com/emptydatabase/telegram-bot-api
```

## Usage

```python
from telegram_bot_api import TelegramClient, SerializableJSON, InlineKeyboardMarkup, InlineKeyboardButton

client = TelegramClient(token="YOUR_BOT_TOKEN")

# Send a message
client.send_message(
    chat_id=123456789,
    text="Choose an option",
    reply_markup=SerializableJSON(InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Click me", callback_data="data")]]
    ))
)

# Poll for updates
while True:
   offset = 0
   for update in client.get_updates(offset=offset):
        do_something(update)
        offset = max(offset, update["update_id"] + 1)
```

All API methods are keyword-only.

## Mock mode

For testing or offline development, instantiate the client without a token:

```python
client = TelegramClient(mock=True)
```

Mock methods return canned data from the method body without making network requests.

## Testing

Tests are integration tests that hit the real Telegram API.

1. Create `tests/.env` with your bot credentials:

```
TOKEN=your_bot_token
CHAT_ID=your_chat_id
```

2. Install test dependencies:

```sh
pip install pytest python-dotenv
```

3. Run:

```sh
pytest tests/
```

## License

```
    telegram-bot-api - A telegram bot client
    Copyright (C) 2026  emptydatabase

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
