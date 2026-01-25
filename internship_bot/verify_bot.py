
import os
import logging
from src.bot import TelegramBot

logging.basicConfig(level=logging.INFO)

def test():
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHANNEL_ID")
    
    print(f"Testing with Token: {token[:5]}... and Chat ID: {chat_id}")
    
    bot = TelegramBot(token, chat_id)
    bot.send_message("<b>🤖 Internship Bot Test</b>\n\nIf you see this, the bot configuration is correct!")

if __name__ == "__main__":
    test()
