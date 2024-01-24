import telebot
import json
import random


def load_user_data(user_id):
    try:
        with open('user_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            user_data = data.get(str(user_id))
            if user_data is None:
                # Если данные пустые или отсутствуют, возвращаем пустой объект
                user_data = {}
            return user_data
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл отсутствует или содержит некорректные данные, возвращаем пустой объект
        return {}


# Функция сохранения данных пользователя
def save_user_data(user_id, user_data):
    try:
        with open('user_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[str(user_id)] = user_data

    try:
        with open('user_data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)
            return True  # Возвращаем True при успешном сохранении
    except IOError as e:
        print(f"Ошибка при сохранении данных пользователя: {str(e)}")
        return False  # Возвращаем False в случае ошибки


# Логика для обработки выбора правого пути
def handle_right_path(chat_id, bot, user_item):
    user_data = load_user_data(chat_id)
    bot.send_message(chat_id, "Перед вами темный тоннель, но от страха быть утонувшим вы решаетесь побежать по нему.")
    bot.send_message(chat_id,
                     f"Вы бежите, но ничего не видите. Тут вы вспоминаете, что у вас в кармане лежит {user_item}.")
    if user_item == 'Фонарик':
        bot.send_message(chat_id, "Вы включили фонарик и, оказалось, что это старое советское убежище.\n"
                                  "Вы добегаете до конца, открываете железную дверь и выбираетесь из канализации!\nЧтобы начать игру заново введите /start")
    else:
        bot.send_message(chat_id,
                         f"К сожалению, {user_item} не излучает света. Испугавшись темноты вы решаете остановиться.\n"
                         "И вдруг, откуда не возьмись, появилась летучая мышь, которая смертельно вас укусила. Вы не выжили.\nЧтобы начать игру заново введите /start")


# Логика для обработки выбора прямого пути
def handle_straight_path(chat_id, bot, user_item):
    user_data = load_user_data(chat_id)
    user_item = user_data.get("inventory", "")
    bot.send_message(chat_id, "Вы нашли огромную крысу, которая что-то ела. Это была пицца.")
    if user_item == 'Багет':
        bot.send_message(chat_id, "Вы достаёте багет из кармана и отдаете половину.\n"
                                  "Крыса была благодарна.\n"
                                  "Вскоре пришли странные, на ваш взгляд черепахи. Испугавшись, вы закричали, но потом вспомнили,\n"
                                  "что это те самые ниндзя-черепашки, а крыса - Сплинтер, их учитель.\n"
                                  "Они предложили помочь вам выбраться...")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('Согласиться', callback_data='agree'),
            telebot.types.InlineKeyboardButton('Отказаться', callback_data='refuse')
        )
        # Отправляем сообщение с клавиатурой
        bot.send_message(chat_id, "Сделайте свой выбор:", reply_markup=keyboard)
    else:
        bot.send_message(chat_id,
                         "Вы попытались тихо пройти, но крыса замечает вас и нападает. Вы погибли :(\nЧтобы начать игру заново введите /start")


# Логика для обработки выбора левого пути
def handle_left_path(chat_id, bot, user_item):
    user_data = load_user_data(chat_id)
    bot.send_message(chat_id, "Перед вами 2 шлюза. Какой выбрать?")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('1', callback_data='gate1'),
        telebot.types.InlineKeyboardButton('2', callback_data='gate2')
    )
    bot.send_message(chat_id, text="Выберите номер шлюза:", reply_markup=keyboard)


# Логика для обработки выбора шлюза
def handle_gate_selection_1(bot, chat_id):
    bot.send_message(chat_id, "Оказалось, это выход из канализации!\nЧтобы начать игру заново введите /start")


def handle_gate_selection_2(bot, chat_id, gate_number):
    user_data = load_user_data(chat_id)
    user_item = user_data.get("inventory", "")
    bot.send_message(chat_id, f"Перед вами небольшой сундук. Но для него нужен ключ.\nВы вспоминаете, что у вас в кармане {user_item}.")
    if user_item == 'Лом':
        bot.send_message(chat_id, "Вы достаете лом и ломаете замок.\n"
                                  "Внутри вы находите миллион долларов и уходите в люк под сундуком.\nЧтобы начать игру заново введите /start")
    else:
        bot.send_message(chat_id, f"Вы достаете {user_item} из кармана, "
                                  "но им не взломать сундук. Вы возвращаетесь назад и вас уносит огромная волна.\nЧтобы начать игру заново введите /start")


# Согласиться на помощь
def handle_agree(chat_id, bot):
    bot.send_message(chat_id, "Вы соглашаетесь. Мои поздравления! Вы выбрались из канализации!\nЧтобы начать игру заново введите /start ")


def load_game_data():
    with open('game_data.json', 'r') as file:
        game_data = json.load(file)
    return game_data


# Отказаться от помощи
def handle_refuse(chat_id, bot):
    bot.send_message(chat_id, "Вы решаете отказаться. И теперь вам предстоит сразиться с ниндзя-черпашками.")

    game_data = load_game_data()
    player_health = game_data['player_health']
    enemy_health = game_data['enemy_health']
    enemy_damage = game_data['enemy_damage']
    player_damage_baguette = game_data['player_damage_baguette']

    while player_health > 0 and enemy_health > 0:
        # Шанс игрока атаковать первым
        player_attacks_first = random.choice([True, False])

        if player_attacks_first:
            # Атака игрока
            damage = player_damage_baguette
            enemy_health -= damage
            bot.send_message(chat_id, f"Вы атакуете черепашек и наносите {damage} урона.")

            if enemy_health <= 0:
                break

        # Атака врага
        player_health -= enemy_damage
        bot.send_message(chat_id,
                         f"Черепашки атакуют вас и наносят {enemy_damage} урона. Ваше здоровье: {player_health}")

        if player_health <= 0:
            break

    if player_health > 0:
        bot.send_message(chat_id, "Поздравляю! Вы одержали победу над ниндзя-черепашками.\nСплинтер, восхищаясь вами показывает выход из канализации.\nЧтобы начать игру заново введите /start")
    else:
        bot.send_message(chat_id, "К сожалению, в этот раз победа досталась ниндзя-черепашкам. Вы проиграли :(\nЧтобы начать игру заново введите /start")
