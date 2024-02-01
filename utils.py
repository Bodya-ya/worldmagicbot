from telebot.types import Message
def open_img(path):
    with open(path, "rb") as file:
        return file.read()

