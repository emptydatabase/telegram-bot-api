from typing import TypedDict, Literal, TypeGuard


class User(TypedDict, total=False):
    id: int
    is_bot: bool
    first_name: str
    last_name: str
    username: str


class Chat(TypedDict, total=False):
    id: int
    type: Literal["private", "group", "supergroup", "channel"]
    title: str
    username: str
    first_name: str
    last_name: str


class InlineKeyboardButton(TypedDict, total=False):
    text: str
    callback_data: str


class InlineKeyboardMarkup(TypedDict, total=False):
    inline_keyboard: list[list[InlineKeyboardButton]]


ReplyMarkup = InlineKeyboardMarkup


def is_inline_keyboard_markup(reply_markup: ReplyMarkup) -> TypeGuard[InlineKeyboardMarkup]:
    return "inline_keyboard" in reply_markup


class Message(TypedDict, total=False):
    message_id: int
    date: int
    chat: Chat
    text: str
    reply_markup: InlineKeyboardMarkup


CallbackQuery = TypedDict("CallbackQuery", {
    "id": str,
    "from": User,
    "data": str,
}, total=False)


class Update(TypedDict, total=False):
    update_id: int
    message: Message
    edited_message: Message
    callback_query: CallbackQuery
