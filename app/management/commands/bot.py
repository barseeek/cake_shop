from django.core.management.base import BaseCommand
from django.conf import settings
from environs import Env
import telebot
from telebot import custom_filters, callback_data
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton

env = Env()
env.read_env()

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token=env.str("TELEGRAM_BOT_TOKEN"), state_storage=state_storage)


class BotStates(StatesGroup):
    approve_pd = State()
    select_type = State()
    base_cake = State()
    custom_cake = State()
    select_form = State()
    select_topping = State()
    select_berries = State()
    select_decor = State()
    select_inscription = State()
    get_inscription = State()
    get_address = State()


@bot.message_handler(state=BotStates.get_address, func= lambda message: True)
def get_inscription(message):
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_yes = InlineKeyboardButton("Да", callback_data="YES")
    button_no = InlineKeyboardButton("Нет", callback_data="NO")
    inline_keyboard.add(button_yes, button_no)
    bot.send_message(message.chat.id, "Отлично! Ближайшая дата доставки послезавтра, устроит?")
    bot.set_state(message.from_user.id, BotStates.get_address, message.chat.id)

@bot.message_handler(state=BotStates.get_inscription, func= lambda message: True)
def get_inscription(message):
    bot.send_message(message.chat.id, "Понял вас. Теперь введите адрес")
    bot.set_state(message.from_user.id, BotStates.get_address, message.chat.id)

@bot.callback_query_handler(state=BotStates.get_inscription, func=lambda call: True)
def custom_cake_inscription(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    if call.data == "YES":
        bot.send_message(chat_id,"Введите надпись на торт")
    elif call.data == "NO":
        bot.send_message(chat_id,"Хорошо. Введите адрес доставки")
        bot.set_state(chat_id, BotStates.get_address)
    else:
        print(call.data)


@bot.callback_query_handler(state=BotStates.select_inscription, func=lambda call: True)
def custom_cake_inscription(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_yes = InlineKeyboardButton("Да", callback_data="YES")
    button_no = InlineKeyboardButton("Нет", callback_data="NO")
    inline_keyboard.add(button_yes, button_no)
    bot.send_message(chat_id, "Отлично, мы почти закончили! Хотите добавить надпись на торт?",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.get_inscription)


@bot.callback_query_handler(state=BotStates.select_decor, func=lambda call: True)
def custom_cake_decor(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup(row_width=3)
    inline_keyboard.add(InlineKeyboardButton("Без декора", callback_data="no_decor"),
                        InlineKeyboardButton("Фисташки", callback_data="pistachio"),
                        InlineKeyboardButton("Безе", callback_data="meringue"),
                        InlineKeyboardButton("Фундук", callback_data="hazelnut"),
                        InlineKeyboardButton("Пекан", callback_data="pecan"),
                        InlineKeyboardButton("Маршмеллоу", callback_data="marshmallow"),
                        InlineKeyboardButton("Марципан", callback_data="marzipan"))
    bot.send_message(chat_id, "Выберите декор",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_inscription)


@bot.callback_query_handler(state=BotStates.select_berries, func=lambda call: True)
def custom_cake_berries(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("Без ягод", callback_data="no_berries"),
                        InlineKeyboardButton("Ежевика", callback_data="blackberry"),
                        InlineKeyboardButton("Малина", callback_data="raspberry"),
                        InlineKeyboardButton("Голубика", callback_data="blueberry"),
                        InlineKeyboardButton("Клубника", callback_data="strawberry"))
    bot.send_message(chat_id, "Выберите форму",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_decor)


@bot.callback_query_handler(state=BotStates.select_topping, func=lambda call: True)
def custom_cake_topping(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("Без топпинга", callback_data="no_topping"),
                        InlineKeyboardButton("Белый соус", callback_data="white_sauce"),
                        InlineKeyboardButton("Сироп", callback_data="syrup")
                        )
    bot.send_message(chat_id, "Выберите топпинги",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_berries)


@bot.callback_query_handler(state=BotStates.select_form, func=lambda call: True)
def custom_cake_form(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("Круг", callback_data="circle"),
                        InlineKeyboardButton("Прямоугольник", callback_data="rectangle"),
                        InlineKeyboardButton("Квадрат", callback_data="square"))
    bot.send_message(chat_id, "Выберите форму",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_topping)


@bot.callback_query_handler(state=BotStates.select_type, func=lambda call: call.data == 'custom')
def custom_cake_level(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("1", callback_data="1"),
                        InlineKeyboardButton("2", callback_data="2"),
                        InlineKeyboardButton("3", callback_data="3"))
    bot.send_message(chat_id, "Давайте начнем! Выберите количество уровней",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_form)


@bot.callback_query_handler(state=BotStates.select_type, func=lambda call: call.data == 'base')
def base_cake(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    for cake in range(1, 4):
        button_cake = InlineKeyboardButton(f"Торт{cake}", callback_data=f"{cake}")
        inline_keyboard.add(button_cake)
    bot.send_message(chat_id, "Выберите торт из предложенных",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_inscription)


@bot.callback_query_handler(state=BotStates.approve_pd, func=lambda call: call.data == 'YES')
def approved(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_base = InlineKeyboardButton("Выбрать готовый торт", callback_data="base")
    button_custom = InlineKeyboardButton("Создать новый торт", callback_data="custom")
    inline_keyboard.add(button_base, button_custom)
    bot.send_message(chat_id, "Спасибо за доверие! Какой торт вы хотите: выбрать из готовых или создать свой?",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_type)


@bot.callback_query_handler(state=BotStates.approve_pd, func=lambda call: call.data == 'NO')
def not_approved(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    bot.send_message(chat_id, "К сожалению, вы не можете заказать торт. Для нового заказа через бота введите /start")


@bot.message_handler(commands=['start'])
def start(message):
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_yes = InlineKeyboardButton("Да", callback_data="YES")
    button_no = InlineKeyboardButton("Нет", callback_data="NO")
    inline_keyboard.add(button_yes, button_no)
    bot.reply_to(message,
                 "Добро пожаловать в наш магазин! Для заказа торта необходимо принять согласие на обработку персональных данных",
                 reply_markup=inline_keyboard)
    bot.send_document(message.chat.id, open('agreement.pdf', 'rb'))
    bot.set_state(message.from_user.id, BotStates.approve_pd, message.chat.id)


# Название класса обязательно - "Command"
class Command(BaseCommand):
    help = 'Just a command for launching a Telegram bot.'

    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2)  # Сохранение обработчиков
        bot.load_next_step_handlers()  # Загрузка обработчиков
        bot.add_custom_filter(custom_filters.StateFilter(bot))
        bot.infinity_polling()
