import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ========== НАСТРОЙКИ (ЭТО НАДО ИЗМЕНИТЬ!) ==========
# 1. Вставь сюда токен, который дал тебе BotFather
BOT_TOKEN = "ТВОЙ_ТОКЕН_СЮДА"

# 2. URL сайта Матрешки
SITE_URL = "https://matrp.ru/"

# 3. Классы для парсинга (ЭТО ГЛАВНОЕ, ЧТО НАДО УТОЧНИТЬ!)
#    Как найти нужный класс: F12 (инспектор) -> навести на число онлайна -> скопировать class="..."
CSS_ONLINE_MAIN = ".server__online"  # Замени!
CSS_ONLINE_MT = ".server__online"   # Замени!
# ====================================================

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

def get_online_from_page(url, css_selector):
    """Универсальная функция для парсинга онлайна с любой страницы"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        online_element = soup.select_one(css_selector)
        
        if online_element:
            online_text = online_element.get_text(strip=True)
            # Ищем число в тексте
            numbers = re.findall(r'\d+', online_text)
            if numbers:
                return numbers[0]
        return "Не удалось определить"
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        return f"Ошибка: {str(e)}"

def get_main_online():
    """Онлайн на главном сервере"""
    return get_online_from_page(SITE_URL, CSS_ONLINE_MAIN)

def get_mt_online():
    """Онлайн на МТ сервере"""
    # Если МТ на том же сайте, но в другом блоке
    # Если отдельный URL, замени на него
    mt_url = SITE_URL  # Или "https://matrp.ru/mt" если есть
    return get_online_from_page(mt_url, CSS_ONLINE_MT)

def create_keyboard():
    """Создает клавиатуру как на твоем скриншоте"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        KeyboardButton("🏠 Дома в госке"),
        KeyboardButton("💰 Бизнесы в госке"),
        KeyboardButton("🚗 Гаражи в госке"),
        KeyboardButton("👤 Имущество игрока"),
        KeyboardButton("📊 Прочее"),
        KeyboardButton("🌐 Онлайн МТ"),
        KeyboardButton("ℹ️ ЖБ Форум")
    ]
    
    # Распределяем кнопки по рядам
    keyboard.add(buttons[0], buttons[1])
    keyboard.add(buttons[2], buttons[3])
    keyboard.add(buttons[4], buttons[5])
    keyboard.add(buttons[6])
    
    return keyboard

# ========== ОБРАБОТЧИКИ КОМАНД ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 *Привет! Я бот Матрешка РП*\n\n"
        "Я умею показывать:\n"
        "• Онлайн на серверах\n"
        "• Информацию о недвижимости\n"
        "• Данные с форума\n\n"
        "Используй кнопки меню 👇"
    )
    bot.send_message(message.chat.id, welcome_text, 
                     parse_mode='Markdown', 
                     reply_markup=create_keyboard())

@bot.message_handler(commands=['online'])
def cmd_online(message):
    bot.send_message(message.chat.id, "📡 Получаю данные о онлайне...")
    
    main_online = get_main_online()
    
    response_text = (
        "🎮 *Текущий онлайн на серверах:*\n"
        f"├ Главный сервер: *{main_online}* чел.\n"
    )
    
    bot.send_message(message.chat.id, response_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    
    if text == "🌐 Онлайн МТ":
        bot.send_message(message.chat.id, "📡 Получаю данные с МТ...")
        mt_online = get_mt_online()
        bot.send_message(message.chat.id, f"🌐 *Онлайн на МТ:* {mt_online} чел.", 
                        parse_mode='Markdown')
    
    elif text == "ℹ️ ЖБ Форум":
        bot.send_message(message.chat.id, 
                        "📰 *Форум Матрешки РП:*\nhttps://forum.matrp.ru/\n\n"
                        "Там ты найдешь:\n"
                        "• Новости проекта\n"
                        "• Вакансии в организации\n"
                        "• Жалобы и апелляции\n"
                        "• Общение с игроками",
                        parse_mode='Markdown',
                        disable_web_page_preview=True)
    
    elif text in ["🏠 Дома в госке", "💰 Бизнесы в госке", "🚗 Гаражи в госке", "👤 Имущество игрока"]:
        bot.send_message(message.chat.id, 
                        f"⚠️ Раздел '{text}' требует настройки парсинга.\n\n"
                        "Нужно добавить URL страницы поиска и CSS-селекторы.\n"
                        "Это можно сделать по аналогии с функцией get_main_online()",
                        parse_mode='Markdown')
    
    elif text == "📊 Прочее":
        bot.send_message(message.chat.id, 
                        "📊 *Дополнительная информация:*\n\n"
                        "Команды:\n"
                        "/online - Онлайн на серверах\n"
                        "/help - Эта справка\n\n"
                        "Больше функций в разработке!",
                        parse_mode='Markdown')
    
    elif text == "/help":
        help_text = (
            "🤖 *Команды бота:*\n\n"
            "/start - Главное меню\n"
            "/online - Онлайн на серверах\n\n"
            "Или просто жми на кнопки!"
        )
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
    
    else:
        # Неизвестная команда
        bot.send_message(message.chat.id, 
                        "Используй кнопки меню или команду /help",
                        reply_markup=create_keyboard())

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("Бот Матрешка РП запущен!")
    print(f"Токен: {BOT_TOKEN[:10]}...")
    print("Настройка CSS-селекторов: проверь CSS_ONLINE_MAIN и CSS_ONLINE_MT")
    bot.infinity_polling()
