import os
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Retrieve API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ensure keys are available
if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise EnvironmentError("Missing OPENAI_API_KEY or TELEGRAM_BOT_TOKEN environment variables.")

# Set OpenAI API key
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

# OpenAI interaction function
async def ask_openai(prompt: str) -> str:
    try:
        response = await aclient.chat.completions.create(model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.7)

        ret = ""
        async for chunk in response:
             ret = ret + str(chunk.choices[0].delta.content or "")
        return ret

    except Exception as e:
        return f"Error communicating with OpenAI: {e}"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! How many I provide excellent service today?"
    )

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    chat_id = update.effective_chat.id

    # Send user message to OpenAI
    response = await ask_openai(user_message)

    # Send the response back to Telegram
    await context.bot.send_message(chat_id=chat_id, text=response)

# Main function to run the bot
def main() -> None:
    # Create application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
