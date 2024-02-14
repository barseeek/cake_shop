from django.core.management.base import BaseCommand
from django.conf import settings
from environs import Env
import telebot
from telebot import custom_filters
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
    first_level = State()
    second_level = State()
    third_level = State()


@bot.message_handler(state=BotStates.select_type)
def choose_cake(message):
    bot.send_message(message.chat.id, "Нажмите 'Выбрать торт'")
    bot.set_state(message.from_user.id, 'waiting_for_choice')


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
    bot.set_state(message.from_user.id, BotStates.select_type)


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
