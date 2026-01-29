
import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from database import Database
from filters import COUNTRIES, STEM_FIELDS

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Running Internship Search 🚀", callback_data='start_search')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to the Internship Bot! 🤖\nClick below to find internships:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == 'start_search':
        # Show Country Selection
        keyboard = []
        row = []
        for country in COUNTRIES:
            row.append(InlineKeyboardButton(country, callback_data=f'country_{country}'))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("Global / All", callback_data='country_All')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="🌍 Select a Country:", reply_markup=reply_markup)

    elif data.startswith('country_'):
        selected_country = data.split('_')[1]
        context.user_data['country'] = selected_country
        
        # Show Field Selection
        keyboard = []
        for field in STEM_FIELDS.keys():
            keyboard.append([InlineKeyboardButton(field, callback_data=f'field_{field}')])
        
        keyboard.append([InlineKeyboardButton("All Fields", callback_data='field_All')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"selected Country: {selected_country}\n\n📚 Select a Field:", reply_markup=reply_markup)

    elif data.startswith('field_'):
        selected_field = data.split('_')[1]
        country = context.user_data.get('country', 'All')

        # Check Rate Limit
        allowed, count = db.check_rate_limit(user_id)
        if not allowed:
            await query.edit_message_text(text=f"⚠️ You have reached your daily limit of 100 requests.\nPlease try again tomorrow.")
            return

        await query.edit_message_text(text=f"🔍 Searching for {selected_field} internships in {country}...")

        # Perform Search
        results = db.search_internships(country=country, field=selected_field, limit=5)

        if not results:
            await context.bot.send_message(chat_id=user_id, text="No internships found matching your criteria at the moment. Try again later!")
            return

        for internship in results:
            msg = (
                f"🚀 <b>{internship.title}</b>\n"
                f"🏢 {internship.company}\n"
                f"📍 {internship.location}\n"
                f"📅 {internship.date_posted.strftime('%Y-%m-%d') if internship.date_posted else 'N/A'}\n"
                f"👇 <b>Apply Here:</b>\n{internship.link}"
            )
            try:
                await context.bot.send_message(chat_id=user_id, text=msg, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")

        await context.bot.send_message(chat_id=user_id, text=f"✅ Sent top {len(results)} results.\nDaily Requests: {count}/100")

def main():
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN environment variable is missing.")
        return

    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    logger.info("Bot is polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
