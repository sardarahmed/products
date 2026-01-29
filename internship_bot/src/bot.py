
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
            if "chat not found" in e.response.text:
                logger.error("Double-check: 1. Did you add the bot to the channel? 2. Is the bot an Admin? 3. Is the CHANNEL_ID correct?")
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
        source = internship.get('source', 'Web')
        date = internship.get('date', 'Recently')
        country = internship.get('country', 'Global')
        field = internship.get('field', 'Tech')
        
        # Premium / Clean Formatting
        return (
            f"⚡ <b>New Opportunity!</b>\n\n"
            f"💼 <b>{title}</b>\n"
            f"🏢 <i>{company}</i>\n"
            f"📍 {location} ({country})\n"
            f"\n"
            f"💰 <b>Stipend:</b> {stipend}\n"
            f"📅 <b>Posted:</b> {date}\n"
            f"🏷️ <b>Field:</b> {field}\n"
            f"\n"
            f"🔗 <a href='{internship.get('link')}'><b>Apply Now</b></a>\n"
            f"\n"
            f"#{field.replace(' ', '')} #Internship #{country.replace(' ', '')}"
        )
