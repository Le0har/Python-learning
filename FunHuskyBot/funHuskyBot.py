import telebot
import random
import requests
import json
from bs4 import BeautifulSoup

def parserAnecdotes():
    url = 'http://www.anekdot.ru/last/good/'
    try:
        req = requests.get(url)
    except Exception as ex:
        print(ex)
    soup = BeautifulSoup(req.text, 'html.parser')
    data = soup.find_all('div', class_='text')
    anecdotes = []
    for anecdot in data:
        anecdotes.append(anecdot.text)
    return anecdotes

def getAnecdote(callback):
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton('Еще анекдот?', callback_data='another_anecdote')
    markup.add(button)
    anecdotes = parserAnecdotes()
    anecdote = random.choice(anecdotes)
    bot.send_message(callback.message.chat.id, anecdote, reply_markup=markup)

def parserPhotoes():
    url = 'https://wallpaperscraft.ru/catalog/nature'
    try:
        req = requests.get(url)
    except Exception as ex:
        print(ex)
    soup = BeautifulSoup(req.text, 'html.parser')
    data = soup.find_all('span', class_='wallpapers__canvas')
    photoes = []
    for photo in data:
        photo_url = photo.find('img', class_='wallpapers__image').get('src')
        photo_url = photo_url[:-11] + '800x600.jpg'     #увеличиваю разрешение фото
        photoes.append(photo_url) 
    return photoes    

def getPhoto(callback):
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton('Еще фото?', callback_data='another_nature_photo')
    markup.add(button)
    photoes = parserPhotoes()
    photo = random.choice(photoes)
    bot.send_photo(callback.message.chat.id, photo, reply_markup=markup)

def parserDayInHistory():
    url = 'https://knowhistory.ru'
    try:
        req = requests.get(url)
    except Exception as ex:
        print(ex)
    soup = BeautifulSoup(req.text, 'html.parser')
    today = soup.find('div', class_='view view-today view-id-today view-display-id-block view-dom-id-27dfbba6877a11c9c74138333e107536')
    today_url = url + today.find('div', class_='h3').find('a').get('href')
    try:
        req = requests.get(today_url)
    except Exception as ex:
        print(ex)
    soup = BeautifulSoup(req.text, 'html.parser')
    data = soup.find_all('div', class_='field-content')
    articles = []
    for article in data:
        articles.append(article.text)
    articles = [articles[i] for i in range(2, len(articles), 3)]    #записываю только каждый третий элемент
    return articles

def getDayInHistory(callback):
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton('Еще событие?', callback_data='another_day_in_history')
    markup.add(button)
    days_in_history = parserDayInHistory()
    day_in_history = random.choice(days_in_history)
    bot.send_message(callback.message.chat.id, day_in_history, reply_markup=markup)

def getAstroprogonosis(zodiac_sign):
    url = 'https://goroskop365.ru/' + zodiac_sign
    try:
        req = requests.get(url)
    except Exception as ex:
        print(ex)
    soup = BeautifulSoup(req.text, 'html.parser')
    data = soup.find('div', class_='content_wrapper horoborder').find('p').text
    return data

bot = telebot.TeleBot('7483961010:AAFmAfNi1a89tvSGlR85hYMhdr6um9nvCC4')

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    button1 = telebot.types.InlineKeyboardButton('Анекдоты', callback_data='anecdotes') 
    button2 = telebot.types.InlineKeyboardButton('Фото природы', callback_data='nature_photoes')
    markup.add(button1, button2)
    button3 = telebot.types.InlineKeyboardButton('День в истории', callback_data='day_in_history') 
    button4 = telebot.types.InlineKeyboardButton('Астропрогноз', callback_data='astroprogonosis')
    markup.add(button3, button4)
    button5 = telebot.types.InlineKeyboardButton('Новости спорта', url='https://sportmail.ru') 
    button6 = telebot.types.InlineKeyboardButton('Погода', callback_data='weather')
    markup.add(button5, button6)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!  Выбери и нажми кнопку.', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callbackMessage(callback):
    if callback.data == 'anecdotes':
        getAnecdote(callback)
    elif callback.data == 'another_anecdote':
        getAnecdote(callback)
 
    elif callback.data == 'nature_photoes':
        getPhoto(callback)
    elif callback.data == 'another_nature_photo':
        getPhoto(callback)

    elif callback.data == 'day_in_history':
        getDayInHistory(callback)
    elif callback.data == 'another_day_in_history':
        getDayInHistory(callback)

    elif callback.data == 'astroprogonosis':
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        button1 = telebot.types.InlineKeyboardButton('Овен', callback_data='aries') 
        button2 = telebot.types.InlineKeyboardButton('Телец', callback_data='taurus')
        markup.add(button1, button2)
        button3 = telebot.types.InlineKeyboardButton('Близнецы', callback_data='gemini') 
        button4 = telebot.types.InlineKeyboardButton('Рак', callback_data='cancer')
        markup.add(button3, button4)
        button5 = telebot.types.InlineKeyboardButton('Лев', callback_data='leo') 
        button6 = telebot.types.InlineKeyboardButton('Дева', callback_data='virgo')
        markup.add(button5, button6)
        button7 = telebot.types.InlineKeyboardButton('Весы', callback_data='libra') 
        button8 = telebot.types.InlineKeyboardButton('Скорпион', callback_data='scorpio')
        markup.add(button7, button8)
        button9 = telebot.types.InlineKeyboardButton('Стрелец', callback_data='sagittarius') 
        button10 = telebot.types.InlineKeyboardButton('Козерог', callback_data='capricorn')
        markup.add(button9, button10)
        button11 = telebot.types.InlineKeyboardButton('Водолей', callback_data='aquarius') 
        button12 = telebot.types.InlineKeyboardButton('Рыбы', callback_data='pisces')
        markup.add(button11, button12)
        bot.send_message(callback.message.chat.id, 'Выбери знак зодиака:', reply_markup=markup)
    elif callback.data == 'aries':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('aries'))
    elif callback.data == 'taurus':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('taurus'))
    elif callback.data == 'gemini':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('gemini'))
    elif callback.data == 'cancer':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('cancer'))
    elif callback.data == 'leo':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('leo'))
    elif callback.data == 'virgo':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('virgo'))
    elif callback.data == 'libra':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('libra'))
    elif callback.data == 'scorpio':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('scorpio'))
    elif callback.data == 'sagittarius':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('sagittarius'))
    elif callback.data == 'capricorn':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('capricorn'))
    elif callback.data == 'aquarius':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('aquarius'))
    elif callback.data == 'pisces':
        bot.send_message(callback.message.chat.id, getAstroprogonosis('pisces'))

    elif callback.data == 'weather':
        bot.send_message(callback.message.chat.id, 'Напиши название города:')
        bot.register_next_step_handler(callback.message, sendTextWeather)
    elif callback.data == 'another_city':
        bot.send_message(callback.message.chat.id, 'Напиши название города:')
        bot.register_next_step_handler(callback.message, sendTextWeather)    

@bot.message_handler(content_types=['text'])
def sendText(message):
    msg = message.text.lower()
    hello = ['привет', 'привет бот', 'привет, бот', 'привет bot', 'привет, bot','привет fun husky bot', 'привет, fun husky bot']
    if msg in hello:
        bot.send_message(message.chat.id, 'Привет-привет!')
    else:
        bot.send_message(message.chat.id, 'Гав-гав!')

def sendTextWeather(message):
    API_weather = '3d9de74844d28377e81415151cbe6a66'
    msg = message.text.lower()
    try:
        req = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={msg}&appid={API_weather}&units=metric')
    except Exception as ex:
        print(ex)
    if req.status_code == 200:
        data = json.loads(req.text)
        temper = data['main']['temp']
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton('Другой город?', callback_data='another_city')
        markup.add(button)
        bot.send_message(message.chat.id, f'Сейчас температура: {round(temper, 1)} °С', reply_markup=markup)
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton('Другой город?', callback_data='another_city')
        markup.add(button)
        bot.send_message(message.chat.id, 'Город указан неверно!!!', reply_markup=markup)

bot.polling(non_stop=True)    