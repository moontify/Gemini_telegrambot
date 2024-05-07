import time

import telebot
import json
from datetime import datetime
from openai import OpenAI

GOOGLE_API_KEY = 'апишка гемини'
OPENAI_BASE_URL = 'https://my-openai-gemini-beta-two.vercel.app/v1'

client = OpenAI(api_key=GOOGLE_API_KEY, base_url=OPENAI_BASE_URL)

bot = telebot.TeleBot('Токен бота')
additional_prompt = "Промт сюды"

def save_conversation(user_id, messages):
    filename = f"user_{user_id}.json"
    new_data = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }

    try:
        with open(filename, "r+") as f:
            data = json.load(f)
            data.append(new_data)
            f.seek(0)
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        with open(filename, "w") as f:
            json.dump([new_data], f, indent=4)

def get_chat_history(user_id):
    filename = f"user_{user_id}.json"
    try:
        with open(filename, "r") as f:
            conversation_history = json.load(f)

        chat_text = "\nВесь чат:\n"
        for entry in conversation_history:
            for message in entry["messages"]:
                chat_text += f"{message['role']}: {message['content']}\n"
        return chat_text

    except FileNotFoundError:
        return "История переписки не найдена."


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text

    user_id = message.from_user.id

    chat_history = get_chat_history(user_id)

    combined_message = "\n\nИстория чата" + chat_history + "\n\nКак ты должен себя вести" + additional_prompt + "\n\nСообщение человека: " + user_message

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": combined_message},
        ],
        model="gpt-3.5-turbo",
    )

    messages = [
        {"role": "user", "content": user_message},
        {"role": "bot", "content": chat_completion.choices[0].message.content},
    ]
    save_conversation(user_id, messages)

    response_text = chat_completion.choices[0].message.content
    time.sleep(2)
    bot.reply_to(message, response_text)


bot.polling()

