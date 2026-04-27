import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

# Flask for Render Free Tier
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cześć! Jestem Twoim agentem AI. Codziennie o 12:00 zapytam Cię co dziś zrobiłeś, a potem przygotuję dla Ciebie posty na social media.")

from gemini import generate_content
from supabase_client import save_generation

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = str(update.effective_user.id)
    
    status_msg = await update.message.reply_text("🤖 Myślę... Gemini generuje Twoje treści...")
    
    try:
        # Generowanie treści przez AI
        ai_response = generate_content(user_input)
        
        # Rozdzielanie treści (prosty podział, można dopracować)
        # Zakładamy że Gemini zwróci sekcje oddzielone np. "---"
        
        linkedin_preview = f"📝 **Podgląd LinkedIn:**\n\n{ai_response.split('🎬')[0]}"
        video_script = f"🎬 **Scenariusz 60s:**\n\n🎬{ai_response.split('🎬')[1] if '🎬' in ai_response else 'Błąd generowania scenariusza'}"
        
        # Zabezpieczenie przed zbyt długą wiadomością (limit Telegrama to 4096)
        linkedin_preview = linkedin_preview[:4000]
        video_script = video_script[:4000]
        
        # Zapis do bazy Supabase
        save_generation(user_id, "linkedin", linkedin_preview)
        save_generation(user_id, "script", video_script)
        
        keyboard = [
            [InlineKeyboardButton("Zatwierdź LinkedIn ✅", callback_data='approve_linkedin')],
            [InlineKeyboardButton("Zatwierdź Scenariusz ✅", callback_data='approve_script')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await status_msg.delete()
        await update.message.reply_text(linkedin_preview, parse_mode='Markdown')
        await update.message.reply_text(video_script, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Wystąpił błąd: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"{query.data} zatwierdzone! 🚀")

async def trigger_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This would eventually iterate over all users in Supabase
    await update.message.reply_text("Cześć! Co dziś zrobiłeś? Napisz mi w kilku zdaniach, a ja przygotuję dla Ciebie treści. 🚀")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    trigger_handler = CommandHandler('trigger', trigger_question)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    callback_handler = CallbackQueryHandler(button_callback)
    
    application.add_handler(start_handler)
    application.add_handler(trigger_handler)
    application.add_handler(msg_handler)
    application.add_handler(callback_handler)
    
    print("Bot is running...")
    keep_alive()
    application.run_polling()
