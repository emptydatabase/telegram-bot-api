import os
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv

from telegram_bot_api import TelegramClient, SerializableJSON, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()


def is_parent(parent: Any, child: Any) -> bool:
    if isinstance(child, dict):
        if not isinstance(parent, dict):
            return False
        for key, value in child.items():
            if key not in parent:
                return False
            if not is_parent(parent[key], value):
                return False
        return True
    elif isinstance(child, list):
        if not isinstance(parent, list):
            return False
        if len(child) != len(parent):
            return False
        for c, p in zip(child, parent):
            if not is_parent(p, c):
                return False
        return True
    else:
        return parent == child


def common_function_test(
        function: Callable,
        **kwargs
):
    client = TelegramClient(os.environ["TOKEN"])
    response = function(client, **kwargs)

    mock = TelegramClient(mock=True)
    mock_response = function(mock, **kwargs)

    return is_parent(response, mock_response)


def test_send_message():
    assert common_function_test(
        TelegramClient.send_message,
        chat_id=os.environ["CHAT_ID"],
        text="TEST",
        reply_markup=SerializableJSON(InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text="BUTTON",
                callback_data="DATA"
            )]]
        ))
    )
