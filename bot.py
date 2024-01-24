import telebot
from telebot import types
from game_data import (
    handle_left_path, handle_straight_path, handle_right_path, handle_gate_selection_1,
    handle_refuse, handle_agree, load_user_data, save_user_data, handle_gate_selection_2,
)


bot = telebot.TeleBot('6735669928:AAHza7PNzqT7QyEHIz6j-5ZKRYYUIi7FApg')


@bot.message_handler(commands=['start'])
def handle_start(message):
    # Получение ника пользователя
    user = message.from_user
    username = user.username
    chat_id = message.chat.id
    # Если бот не может прочитать ник
    if not username:
        welcome_message = f"Приветствую, Незнакомец(ка)!\n" \
                          "Вам предстоит пройти текстовый квест.\n" \
                          "Вам будут предложены варианты действий, " \
                          "а в зависимости от выбора, сюжет будет развиваться по-разному."

        # Создание кнопки "Начать игру"
        start_button = types.KeyboardButton("Начать игру")

        # Создание клавиатуры с кнопкой
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(start_button)

        # Отправка приветственного сообщения с кнопкой
        bot.reply_to(message, welcome_message, reply_markup=keyboard)

        return

    # Сохранение ника пользователя
    save_user_data(message.from_user.id, username)

    # Приветственное сообщение
    welcome_message = f"Приветствую, {username}!\n" \
                      "Вам предстоит пройти текстовый квест.\n" \
                      "Вам будут предложены варианты действий, " \
                      "а в зависимости от выбора, сюжет будет развиваться по-разному."

    # Создание кнопки "Начать игру"
    start_button = types.KeyboardButton("Начать игру")

    # Создание клавиатуры с кнопкой
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(start_button)

    # Отправка приветственного сообщения с кнопкой
    bot.reply_to(message, welcome_message, reply_markup=keyboard)


# Обработчик команды "/help"
@bot.message_handler(commands=['help'])
def handle_help(message):
    # Отправляем информацию о доступных командах
    commands = [
        "/start - Начать",
        "/help - Помощь",
    ]
    bot.reply_to(message, "\n".join(commands))


# Обработка нажатия кнопки "Начать игру"
@bot.message_handler(func=lambda message: message.text == "Начать игру")
def handle_game_start(message):
    # Убираем кнопку "Начать игру"
    bot.send_chat_action(message.chat.id, 'typing')
    hide_keyboard = types.ReplyKeyboardRemove()
    user_data = load_user_data(message.chat.id)
    if not user_data:
        user_data = {"inventory": ""}  # Создаем пустую строку для инвентаря нового пользователя
        save_user_data(message.chat.id, user_data)  # Сохраняем данные нового пользователя

    bot.send_message(message.chat.id,
                     "Вы шли по улице и упали в открытый канализационный люк. На трубах рядом с вами спит бродяга, а возле его сумки лежит багет, фонарик и лом. По трубе, где вы находитесь прибывает вода, остается несколько минут до полного заполнения водой! Время тикает, решайте, какой предмет будете брать?",
                     reply_markup=hide_keyboard)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Багет', callback_data='baguette'),
        telebot.types.InlineKeyboardButton('Фонарик', callback_data='flashlight'),
        telebot.types.InlineKeyboardButton('Лом', callback_data='crowbar')
    )
    bot.send_message(message.chat.id, text="Выберите один из предметов:", reply_markup=keyboard)


def handle_picked_item(chat_id, item_name):
    user_data = load_user_data(chat_id)
    user_data = {"inventory": item_name}
    save_user_data(chat_id, user_data)  # Сохраняем обновленные данные пользователя


@bot.callback_query_handler(func=lambda call: call.data in ['baguette', 'flashlight', 'crowbar'])
def handle_direction(call):
    user_item = ""
    if call.data == 'baguette':
        user_item = "Багет"
    elif call.data == 'flashlight':
        user_item = "Фонарик"
    elif call.data == 'crowbar':
        user_item = "Лом"

    handle_picked_item(call.message.chat.id, user_item)  # Сохраняем выбранный предмет в инвентарь

    bot.send_message(call.message.chat.id,
                     f"Отлично, теперь у вас есть {user_item}!\nНо нужно выбираться. Куда пойдете дальше?")

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Налево', callback_data='left'),
        telebot.types.InlineKeyboardButton('Прямо', callback_data='straight'),
        telebot.types.InlineKeyboardButton('Направо', callback_data='right')
    )
    bot.send_message(call.message.chat.id, text="Выберите направление:", reply_markup=keyboard)

    chat_id = call.message.chat.id
    user_data = load_user_data(chat_id)


@bot.callback_query_handler(func=lambda call: call.data in ['left', 'straight', 'right'])
def handle_direction_callback(call):
    chat_id = call.message.chat.id  # Добавляем логирование для chat_id
    user_data = load_user_data(chat_id)  # Загружаем данные пользователя
    user_item = user_data.get("inventory", "")  # Получаем предмет пользователя

    if call.data == 'left':
        handle_left_path(chat_id, bot, user_item)
    elif call.data == 'straight':
        handle_straight_path(call.message.chat.id, bot, user_item)
    elif call.data == 'right':
        handle_right_path(chat_id, bot, user_item)


@bot.callback_query_handler(func=lambda call: call.data in ['gate1', 'gate2'])
def handle_gate_selection(call):
    gate_number = int(call.data[-1])  # Извлекаем номер шлюза из данных обратного вызова
    chat_id = call.message.chat.id

    if gate_number == 1:
        handle_gate_selection_1(bot, call.message.chat.id)  # Вызов другой функции для обработки шлюза 1
    elif gate_number == 2:
        handle_gate_selection_2(bot, call.message.chat.id, call.data)  # Вызов другой функции для обработки шлюза 2


@bot.callback_query_handler(func=lambda call: call.data == 'straight_path')
def handle_straight_path_callback(call):
    user_data = load_user_data(call.message.chat.id)
    user_item = user_data.get("inventory", "")
    handle_straight_path(call.message.chat.id, bot, user_item)


@bot.callback_query_handler(func=lambda call: call.data == 'agree')
def handle_agree_callback(call):
    handle_agree(call.message.chat.id, bot)


@bot.callback_query_handler(func=lambda call: call.data == 'refuse')
def handle_refuse_callback(call):
    handle_refuse(call.message.chat.id, bot)


bot.polling(none_stop=True)
