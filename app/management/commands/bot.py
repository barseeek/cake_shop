from django.core.management.base import BaseCommand
from django.conf import settings
from environs import Env
import telebot
from telebot import custom_filters, callback_data
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton
import datetime

from app.models import EXTRA_PRICES, Cake, Client, Order

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
    get_date = State()
    get_time = State()
    create_order = State()


@bot.message_handler(state=BotStates.create_order, func=lambda message: True)
def create_order(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["comment"] = message.text
    
    # Updating or creating client
    new_client, created = Client.objects.update_or_create(
        username=data['username'],
        defaults={
            'username': data['username'],
            'address': data['address'],
        }
    )
    if created:
        print(f'Создан новый пользователь {new_client.username}')
        
    # Creating custom cake in db
    if data.get('type') == 'custom':
        new_custom_cake = Cake.objects.create(
            levels_number=data.get('level'),
            shape=data.get('form'),
            topping=data.get('topping'),
            berries=data.get('berries'),
            decor=data.get('decor'),
        )
        new_custom_cake.save()
        Cake.objects.filter(id=new_custom_cake.id).get_price()
    
    # Creating order in db
    new_order = Order.objects.create(
            client=new_client,
            comment=data.get('comment'),
            date=data.get('date'),
            time=data.get('time'),
            inscription=data.get('inscription'),
    )
    if data.get('fast_delivery'):
        new_order.fast_delivery = True
        new_order.save()
    if data.get('type') == 'base':
        order_base_cake = Cake.objects.get(id=data.get('base_cake_id'))
        new_order.cake = order_base_cake
        new_order.save()
    else:
        new_order.cake = new_custom_cake
        new_order.save()
    total_price = new_order.cake.price
    if new_order.inscription:
        total_price += EXTRA_PRICES['inscription']
    if new_order.fast_delivery:
        total_price *= EXTRA_PRICES['express_coefficient']
    new_order.total_price = total_price
    new_order.save()
    
    msg = f"Ваш заказ №{new_order.id} создан\n"
    msg += "Состав заказа: "
    if data.get("type") == "base":
        msg += f"Торт {order_base_cake.title}"
        if new_order.inscription:
            msg += f"с надписью '{new_order.inscription}' \n"
        msg += f"Цена в рублях: {new_order.total_price} \n "
    elif data.get("type") == "custom":
        msg += (f"Кастомный торт {new_custom_cake.pk}, вы выбрали: \n"
                f"Уровни: {new_custom_cake.get_levels_number_display()}\n"
                f"Форма: {new_custom_cake.get_shape_display()}\n"
                f"Топпинг: {new_custom_cake.get_topping_display()}\n"
                f"Декор: {new_custom_cake.get_decor_display()}\n")
        if new_order.inscription:
            msg += f"Надпись: {new_order.inscription} \n"
        # TODO Добавить вывод цены
        msg += f"Цена в рублях: {new_order.total_price} \n "
    msg += (f"\nДата доставки {new_order.date}, время {new_order.time}\n"
            f"Комментарий курьеру: {new_order.comment} ")

    bot.send_message(message.chat.id, msg)
    bot.send_message(message.chat.id, "Хотите заказать новый торт? Для нового заказа через бота введите /start")
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.callback_query_handler(state=BotStates.get_time, func=lambda call: True)
def get_time(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["time"] = call.data
    bot.send_message(chat_id, "Введите комментарий для курьера")
    bot.set_state(chat_id, BotStates.create_order)


@bot.callback_query_handler(state=BotStates.get_date, func=lambda call: call.data == "YES" or call.data == "fast_delivery")
def get_date(call):
    message = call.message
    chat_id = message.chat.id
    delivery_date = datetime.datetime.now() + datetime.timedelta(days=2)
    current_datetime = datetime.datetime.now()
    bot.edit_message_reply_markup(chat_id, message.message_id)
    if call.data == "fast_delivery":
        with bot.retrieve_data(call.from_user.id, chat_id) as data:
            data["fast_delivery"] = True
        if current_datetime.time().hour >= 17:
            delivery_date = current_datetime + datetime.timedelta(days=1)
        else:
            delivery_date = current_datetime
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["date"] = delivery_date.date()
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    if delivery_date.date() == current_datetime.date():
        inline_keyboard.add(InlineKeyboardButton("До 22", callback_data="until_22"))
    else:
        inline_keyboard.add(InlineKeyboardButton("9-13", callback_data="9-13"),
                            InlineKeyboardButton("13-17", callback_data="13-17"),
                            InlineKeyboardButton("17-21", callback_data="17-21"))
    bot.send_message(chat_id, "Выберите временной интервал", reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.get_time)


@bot.callback_query_handler(state=BotStates.get_date, func=lambda call: call.data == "call_manager")
def call_manager(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    bot.send_message(chat_id, "Менеджер Ирина: +79211233446")
    bot.set_state(chat_id, BotStates.after_order)


@bot.callback_query_handler(state=BotStates.get_date, func=lambda call: call.data == "NO")
def get_another_date(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(InlineKeyboardButton("Срочная доставка", callback_data="fast_delivery"),
                        InlineKeyboardButton("Позвонить менеджеру", callback_data="call_manager"))
    bot.send_message(chat_id, "Мы можем предложить доставку сегодня, если заказ сделан не позднее 17 часов,"
                              " это прибавит 20% к стоимости заказа, либо можно позвонить менеджеру", reply_markup=inline_keyboard)


@bot.message_handler(state=BotStates.get_address, func=lambda message: True)
def get_address(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["address"] = message.text
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_yes = InlineKeyboardButton("Да", callback_data="YES")
    button_no = InlineKeyboardButton("Нет", callback_data="NO")
    inline_keyboard.add(button_yes, button_no)
    delivery_date = datetime.datetime.now() + datetime.timedelta(days=2)
    bot.send_message(message.chat.id, f"Отлично! Ближайшая дата доставки {delivery_date.date()}, устроит?",
                     reply_markup=inline_keyboard)
    bot.set_state(message.from_user.id, BotStates.get_date, message.chat.id)


@bot.message_handler(state=BotStates.get_inscription, func=lambda message: True)
def get_inscription(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["inscription"] = message.text
    bot.send_message(message.chat.id, "Понял вас. Теперь введите адрес")
    bot.set_state(message.from_user.id, BotStates.get_address, message.chat.id)


@bot.callback_query_handler(state=BotStates.get_inscription, func=lambda call: True)
def custom_cake_inscription(call):
    message = call.message
    chat_id = message.chat.id
    bot.edit_message_reply_markup(chat_id, message.message_id)
    if call.data == "YES":
        bot.send_message(chat_id, "Введите надпись на торт")
    elif call.data == "NO":
        bot.send_message(chat_id, "Хорошо. Введите адрес доставки")
        bot.set_state(chat_id, BotStates.get_address)
    else:
        print(call.data)


@bot.callback_query_handler(state=BotStates.select_inscription, func=lambda call: True)
def custom_cake_inscription(call):
    message = call.message
    chat_id = message.chat.id
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        if data.get('type') == 'base':
            data["base_cake_id"] = call.data
        else:
            data["decor"] = call.data
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
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["berries"] = call.data
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
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["topping"] = call.data
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("Без ягод", callback_data="no_berries"),
                        InlineKeyboardButton("Ежевика", callback_data="blackberry"),
                        InlineKeyboardButton("Малина", callback_data="raspberry"),
                        InlineKeyboardButton("Голубика", callback_data="blueberry"),
                        InlineKeyboardButton("Клубника", callback_data="strawberry"))
    bot.send_message(chat_id, "Выберите ягоды",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_decor)


@bot.callback_query_handler(state=BotStates.select_topping, func=lambda call: True)
def custom_cake_topping(call):
    message = call.message
    chat_id = message.chat.id
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["form"] = call.data
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("Без топпинга", callback_data="no_topping"),
                        InlineKeyboardButton("Белый соус", callback_data="white_sauce"),
                        InlineKeyboardButton("Карамельный сироп", callback_data="caramel_syrup"),
                        InlineKeyboardButton("Кленовый сироп", callback_data="maple_syrup"),
                        InlineKeyboardButton("Клубничный сироп", callback_data="strawberry_syrup"),
                        InlineKeyboardButton("Черничный сироп", callback_data="blueberry_syrup"),
                        InlineKeyboardButton("Молочный шоколад", callback_data="milk_chocolate"),
                        )
    bot.send_message(chat_id, "Выберите топпинги",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_berries)


@bot.callback_query_handler(state=BotStates.select_form, func=lambda call: True)
def custom_cake_form(call):
    message = call.message
    chat_id = message.chat.id
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["level"] = call.data
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
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["username"] = call.from_user.username
        data["type"] = call.data
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
    with bot.retrieve_data(call.from_user.id, chat_id) as data:
        data["username"] = call.from_user.username
        data["type"] = call.data
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup()
    base_cakes = Cake.objects.filter(is_base=True)
    for cake in base_cakes:
        button_cake = InlineKeyboardButton(
            f"{cake.title} - {cake.price}р.",
            callback_data=f"{cake.id}",
        )
        inline_keyboard.add(button_cake)
    bot.send_message(chat_id, "Выберите торт из предложенных",
                     reply_markup=inline_keyboard)
    bot.set_state(chat_id, BotStates.select_inscription)


@bot.callback_query_handler(state=BotStates.approve_pd, func=lambda call: call.data == 'YES')
def approved(call):
    message = call.message
    chat_id = message.chat.id
    bot.send_document(message.chat.id, open('agreement.pdf', 'rb'))
    bot.edit_message_reply_markup(chat_id, message.message_id)
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    button_base = InlineKeyboardButton("Выбрать готовый торт", callback_data="base")
    button_custom = InlineKeyboardButton("Создать новый торт", callback_data="custom")
    inline_keyboard.add(button_base, button_custom)
    bot.send_message(chat_id, "Какой торт вы хотите: выбрать из готовых или создать свой?",
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

    client = Client.objects.filter(username=message.from_user.username).exists()
    bot.send_message(message.chat.id, "Добро пожаловать в наш магазин!")
    if not client:
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        button_yes = InlineKeyboardButton("Да", callback_data="YES")
        button_no = InlineKeyboardButton("Нет", callback_data="NO")
        inline_keyboard.add(button_yes, button_no)
        bot.send_message(message.chat.id,
                     "Для заказа торта необходимо принять согласие на обработку персональных данных, вы согласны? ",
                     reply_markup=inline_keyboard)
        bot.set_state(message.from_user.id, BotStates.approve_pd, message.chat.id)
    else:
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        button_base = InlineKeyboardButton("Выбрать готовый торт", callback_data="base")
        button_custom = InlineKeyboardButton("Создать новый торт", callback_data="custom")
        inline_keyboard.add(button_base, button_custom)
        bot.send_message(message.chat.id, "Какой торт вы хотите: выбрать из готовых или создать свой?",
                         reply_markup=inline_keyboard)
        bot.set_state(message.chat.id, BotStates.select_type)


# Название класса обязательно - "Command"
class Command(BaseCommand):
    help = 'Just a command for launching a Telegram bot.'

    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2)  # Сохранение обработчиков
        bot.load_next_step_handlers()  # Загрузка обработчиков
        bot.add_custom_filter(custom_filters.StateFilter(bot))
        bot.infinity_polling()