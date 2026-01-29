import os
import logging
import time
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Poster:
    def __init__(self, bot_token, channel_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"

    def format_message(self, internship):
        return (
            f"🚀 <b>{internship['title']}</b>\n\n"
            f"🏢 <b>Company:</b> {internship['company']}\n"
            f"📍 <b>Location:</b> {internship['location']}\n"
            f"🎓 <b>Field:</b> {internship['field']}\n"
            f"🕒 <b>Duration:</b> {internship['duration']}\n"
            f"💰 <b>Stipend:</b> {internship['stipend']}\n\n"
            f"🛠 <b>Requirements:</b>\n"
            f"{self._format_requirements(internship['requirements'])}\n\n"
            f"🗓 <b>Deadline:</b> {internship['deadline']}\n\n"
            f"🔗 <a href='{internship['apply_link']}'><b>Apply Here</b></a>\n\n"
            f"#Internship #STEM #{internship['country'].replace(' ', '')} #{internship['field'].replace(' ', '').split('/')[0]}"
        )

    def _format_requirements(self, reqs):
        if not reqs:
            return "• Relevant Skills"
        return "\n".join([f"• {r}" for r in reqs[:3]]) # Limit to 3

    def post_internship(self, internship):
        if not self.bot_token or not self.channel_id:
            logger.error("Missing BOT_TOKEN or CHANNEL_ID")
            return False

        message = self.format_message(internship)
        logo_url = internship.get('logo')

        payload = {
            'chat_id': self.channel_id,
            'caption': message,
            'parse_mode': 'HTML',
            'photo': logo_url
        }

        try:
            # First try sending with photo
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()
            logger.info(f"Posted: {internship['title']}")
            return True
        except Exception as e:
            logger.warning(f"Failed to post with image: {e}. Retrying with text only...")
            # Fallback to text message if image fails (e.g. invalid URL)
            text_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload.pop('photo')
            payload['text'] = message
            try:
                requests.post(text_url, json=payload).raise_for_status()
                logger.info(f"Posted (Text Only): {internship['title']}")
                return True
            except Exception as ex:
                logger.error(f"Failed to post text fallback: {ex}")
                return False
