
import requests
import logging
import os

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, channel_id: str):
        self.token = token
        self.channel_id = channel_id
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message: str, link: str = None):
        if not self.token or not self.channel_id:
            logger.warning("Bot token or Channel ID missing. Skipping message send.")
            return

        payload = {
            'chat_id': self.channel_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        if link:
            payload['reply_markup'] = {
                'inline_keyboard': [[
                    {'text': '🚀 Apply Now', 'url': link}
                ]]
            }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            logger.info("Message sent successfully.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to send message: {e.response.text}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def format_internship(self, internship: dict) -> str:
        """
        Formats an internship dictionary into a Telegram HTML message.
        """
        title = internship.get('title', 'N/A')
        company = internship.get('company', 'N/A')
        location = internship.get('location', 'N/A')
        stipend = internship.get('stipend', 'N/A')
        # Link is handled by the inline keyboard now
        
        return (
            f"⚡ <b>New Opportunity in Tech!</b>\n\n"
            f"💼 <b>Role:</b> {title}\n"
            f"🏢 <b>Company:</b> {company}\n"
            f"📍 <b>Location:</b> {location}\n"
            f"💰 <b>Stipend:</b> {stipend}\n"
            f"⏳ <b>Duration:</b> Check details\n\n"
            f"<i>#ComputerScience #Internship #Hiring</i>"
        )
