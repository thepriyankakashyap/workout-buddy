from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from pymongo import MongoClient
from datetime import datetime
import calendar

# MongoDB read function
def read_from_mongo():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["your_database_name"]
    collection = db["your_collection_name"]

    # Get today's date
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Find document with today's date
    document = collection.find_one({"date": today_date})

    if document:
        return f"Date: {document['date']}, Day: {document['day_name']}"
    else:
        return "No data found for today."

# Command handler for 'today'
def today(update: Update, context: CallbackContext):
    response = read_from_mongo()
    update.message.reply_text(response)

def main():
    # Your Telegram bot token
    TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handler for 'today'
    dispatcher.add_handler(CommandHandler("today", today))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
