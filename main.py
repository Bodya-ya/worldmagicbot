import telebot
from telebot.types import Message, ReplyKeyboardMarkup
from dotenv import load_dotenv
from os import getenv
import json
from steps import STEPS, msg, choices, img
from utils import open_img
load_dotenv()
token = getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)

def load_data() -> dict:
    """Функция загрузки данных из json"""
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}


def save_data(data: dict):
    """Функция сохранения данных в json"""
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)



user_data = load_data()

@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    msg = (f"Привет, {message.from_user.username}! \n"
           "Предистория к игре:\n"
           "Ваш персонаж - Эдвин, молодой друид, который отправляется в Мрачный лес для выполнения важной миссии.\n"
    "Он является последним из древнего ордена друидов, и его цель - найти мистическую реликвию, известную как “Сердце леса”.\n"
    "Эдвин - мудрый и опытный маг, однако он не обладает грубой силой воина. Его оружие - это его знания и навыки, которые позволяют ему управлять природой и создавать магические щиты.\n"
    "В своем путешествии он встречает множество злых существ, и все они пытаются помешать ему достичь своей цели.\n")

    user_id = message.from_user.id
    if str(user_id) not in user_data:
        user_data[str(user_id)] = "локация0"
        save_data(user_data)

    if user_data[str(user_id)] != "локация0":
        msg += "Летим дальше на приключения,или заново начнём?"
        keyboard.add("Начать заново", "Продолжить")
    else:
        msg += "Скорее начинай уже!"
        keyboard.add("Начать приключения!")

    bot.send_photo(
        chat_id=user_id,
        photo=open_img("media/let's go.jpg"),
        caption=msg,
        reply_markup=keyboard,
    )

def filter_start_choice(message: Message):
    keywords = ['Начать заново', 'Продолжить', 'Начать приключения!']
    return message.text in keywords

def send_next_quest_step(user_id):
    current_step = user_data[str(user_id)]
    msg, choices, img = STEPS[current_step]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*choices)

    bot.send_photo(
        chat_id=user_id,
        photo=open_img(img),
        caption=msg,
        reply_markup=keyboard,
    )

@bot.message_handler(func=filter_start_choice)
def handler_start_choices(message: Message):
    user_id = message.from_user.id
    current_choice = message.text

    if current_choice == 'Начать заново':
        user_data[str(user_id)] = "локация0"
        save_data(user_data)

    send_next_quest_step(user_id)


@bot.message_handler(content_types=["text"])
def handler_users_answers(message: Message):
    user_id = message.from_user.id
    current_step = user_data[str(user_id)]
    available_choices = STEPS[current_step][1]
    current_choice = message.text

    if current_choice not in available_choices:
        bot.send_message(
            chat_id=user_id,
            text='выбери что-то из предложенного...',
        )
        return
    if current_choice in ['Победа', 'Далее']:
        send_end_message(message)
    else:
        user_data[str(user_id)] = current_choice
        save_data(user_data)
        send_next_quest_step(user_id)

def repeatgame(message: Message):
    user_id = message.from_user.id
    msg = 'хочешь сыграть по новой?'
    current_choices = message.text
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Начать заново")
    user_data[str(user_id)] = 'локация0'
    save_data(user_data)

    bot.send_message(
        chat_id=user_id,
        text=msg,
        reply_markup=keyboard,
    )
def send_end_message(message: Message):
    user_id = message.from_user.id
    current_choices = message.text

    if current_choices == "Победа":
        msg = 'ты выйграл! ты молодец!'
        img = 'media/photoforwin.jpg'
    else:
        msg = 'вас скушали ... 😥'
        img = 'media/photoforlose.jpg'
    user_data[str(user_id)] = 'локация0'
    save_data(user_data)

    bot.send_photo(
        chat_id=user_id,
        photo=open_img(img),
        caption=msg,
    )
    repeatgame(message)



if __name__ == '__main__':
    bot.polling( )
