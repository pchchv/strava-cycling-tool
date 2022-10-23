"""
Using the LINE Messaging API
"""

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from environment import LINE_CHANNEL_ACCESS_TOKEN


line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


def send_line_message(msg: str):
    """
    Sending LINEMessage
    """
    try:
        line_bot_api.broadcast(TextSendMessage(msg))
    except LineBotApiError:
        print("The was an error sending LINE message!")
