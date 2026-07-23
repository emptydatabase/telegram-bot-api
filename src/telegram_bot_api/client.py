import time
from functools import wraps
from types import FunctionType

from requests import Session

from .serializable import Serializable, SerializableJSON, SerializableInputFile
from .types import Update, Message, Chat, ReplyMarkup, is_inline_keyboard_markup


def snake_to_camel(s: str) -> str:
    head, *tail = s.split("_")
    return "".join((head, *map(str.capitalize, tail)))


def api(method: FunctionType):
    @wraps(method)
    def wrapper(self, **kwargs):
        return self._request(method, kwargs)

    return wrapper


class TelegramClient:
    def __init__(self, token: str | None = None, mock: bool = False):
        if not mock and token is None:
            raise TypeError(f"{self.__class__.__name__}.__init__() missing 1 required positional argument: 'token'")
        if token:
            self._base_url = f"https://api.telegram.org/bot{token}"
            self._session = Session()
        self._mock = mock

    def _request(self, method: FunctionType, kwargs: dict):
        if self._mock:
            return method(self, **kwargs)

        name = snake_to_camel(method.__name__)
        params = {}
        files = {}
        for key, value in kwargs.items():
            if isinstance(value, Serializable):
                value.serialize(key, params, files)
            else:
                params[key] = value

        response = self._session.post(
            url=f"{self._base_url}/{name}",
            json=params,
            files=files
        )
        content = response.json()
        if content["ok"]:
            return content["result"]

        raise NotImplementedError

    @api
    def get_updates(
            self, *,
            offset: int | None = None,
            limit: int | None = None,
            timeout: int | None = None,
            allowed_updates: list[str] | None = None,
    ) -> list[Update]:
        return []

    @api
    def send_message(
            self, *,
            chat_id: int | str,
            text: str,
            reply_markup: SerializableJSON[ReplyMarkup] | None = None
    ) -> Message:
        message = Message(
            date=int(time.time()),
            chat=Chat(),
            text=text,
        )
        if isinstance(chat_id, int):
            message["chat"]["id"] = chat_id
        if reply_markup and is_inline_keyboard_markup(reply_markup.value):
            message["reply_markup"] = reply_markup.value
        return message

    @api
    def set_webhook(
            self, *,
            url: str,
            certificate: SerializableInputFile | str | None = None,
            ip_address: str | None = None,
            max_connections: int | None = None,
            allowed_updates: list[str] | None = None,
            drop_pending_updates: bool | None = None,
            secret_token: str | None = None,
    ) -> bool:
        return True

    @api
    def delete_webhook(
            self, *,
            drop_pending_updates: bool | None = None,
    ) -> bool:
        return True
