import telebot
from config import token, channel_id, bot_chat_id
import site_parser
import os
import pickle
import asyncio
import time

bot = telebot.TeleBot(token)

def keyboardMain():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_push = telebot.types.InlineKeyboardButton(text='▶️  Запустить бота для постинга статей  ➡️', callback_data='push') 
    button_stop = telebot.types.InlineKeyboardButton(text='⏹  Остановить бота                                           ➡️', callback_data='stop')
    keyboard.add(button_push, button_stop)
    return keyboard

def getArticle(index, delta_number):
    bot.send_message(channel_id, '⬇️  Внимание, 🍋 новая статья!  ⬇️')
    articles_name = site_parser.extractArticlesName(delta_number)
    bot.send_message(channel_id, f'Название статьи:\n<b>{articles_name[index][0]}</b>', parse_mode='html')
    articles_whole_text = site_parser.extractArticleWholeText(delta_number)     #извлекаем статьи из базы
    size_article = len(articles_whole_text[index][0])
    if size_article > 4096:       #печатаем index статью в несколько постов если она огромная
        stop_symbol = []
        for paragraph in articles_whole_text[index]:        
            for i in range(len(paragraph) - 1):             #ищем индексы завершения абазацев и формируем список
                if paragraph[i] == '\n' and paragraph[i+1] == '\n':
                    stop_symbol.append(i)
            start_paragraph = 0
            summa_one_step = 0
            for k in range(len(stop_symbol)):               #печатаем так, чтобы пост заканчивался абзацем, а не прерывался на полуслове
                summa_one_step = stop_symbol[k] - start_paragraph
                if summa_one_step < 4096:
                    continue
                else:
                    bot.send_message(channel_id, paragraph[start_paragraph:stop_symbol[k-1]])     #печатаем очердной пост
                    start_paragraph = stop_symbol[k] + 2
                    summa_one_step = 0
            #печатаем последний пост:
            if len(paragraph[start_paragraph:]) > 2:        #два последних символа могут быть переносом строки
                bot.send_message(channel_id, paragraph[start_paragraph:])
    else:
        bot.send_message(channel_id, articles_whole_text[index][0])

def getPictures(index, delta_number):
    pictures = site_parser.extractArticlePictures(delta_number)
    picture = pictures[index]
    if picture[0] != None:
        list_binary = pickle.loads(picture[0])
        count_pict = 1
        for i in range(len(list_binary)):
            if not os.path.isdir('media_out'):
                os.mkdir('media_out')
            with open(f'media_out/picture_for_post_{count_pict}.jpg', 'wb') as file:
                file.write(list_binary[i])
            with open(f'media_out/picture_for_post_{count_pict}.jpg', 'rb') as file:
                media_file = file.read()
            bot.send_photo(channel_id, media_file)
            count_pict += 1
            time.sleep(5)                   #пауза между размещением фоток иначе получаю Error code: 429. Description: Too Many Requests: retry after 40

def pushArticles(chat_id):
    bot.send_message(chat_id, 'Запускаю поиск новых статей   🚀')
    old_number = site_parser.getNumberRecordsDB()
    site_parser.main()
    new_number = site_parser.getNumberRecordsDB()
    delta_number = new_number[0] - old_number[0]
    if delta_number > 0:
        bot.send_message(chat_id, 'Есть новые статьи!')
        for index in range(delta_number):
            getArticle(index, delta_number)
            getPictures(index, delta_number)
            time.sleep(50)                  #пауза между размещением статей иначе получаю Error code: 429. Description: Too Many Requests: retry after 40
        bot.send_message(chat_id, 'Все статьи размещены!')
    else:
        bot.send_message(chat_id, 'Новых статей увы пока нету!')

""" @bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!  ⬇️  Выбери действие  ⬇️', reply_markup=keyboardMain())

@bot.message_handler(content_types=['text'])
def testAnswer(message):
    bot.send_message(message.chat.id, 'ℹ️  Я умею только постить статьи на канал:  <b>In search of articles</b>', reply_markup=keyboardMain(), parse_mode='html') 

@bot.callback_query_handler(func=lambda callback: True)
def callbackMessage(callback):
    if callback.data == 'push':
        pushArticles(callback.message.chat.id)
        
    if callback.data == 'stop':
        bot.send_message(callback.message.chat.id, '🛑  Бот остановлен!')
        bot.stop_polling()    """

async def newArticlesEveryMinute():
    while True:
        pushArticles(bot_chat_id) 
        await asyncio.sleep(600)                #поиск новых статей через каждые 10 минут


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(newArticlesEveryMinute())
    except KeyboardInterrupt:                   #пропускаю нажатие клавиш Ctrl+C в консоле
        pass
    bot.polling(non_stop=True) 