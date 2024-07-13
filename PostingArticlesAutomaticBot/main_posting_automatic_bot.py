import telebot
from config import token, channel_id, bot_chat_id
import site_parser
import site_parser_2
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
    if size_article > 4000:       #печатаем index статью в несколько постов если она огромная
        stop_symbol_dict = {}
        for paragraph in articles_whole_text[index]:        
            for i in range(len(paragraph) - 1):             #ищем индексы завершения абазацев и формируем словарь
                if paragraph[i] == '\n' and paragraph[i+1] == '\n':
                    stop_symbol_dict[i] = 'paragraph'       #помечаем индекс как параграф
            for i in range(len(paragraph) - 2):             #ищем индексы картинок и формируем словарь       
                if paragraph[i] == '$' and paragraph[i+1] == '#' and paragraph[i+2] == '$':
                    stop_symbol_dict[i] = 'picture'         #помечаем индекс как картинку
            stop_symbol_dict = dict(sorted(stop_symbol_dict.items()))       #отсортируем словарь по ключам
            #print(stop_symbol_dict)
            start_paragraph = 0
            summa_one_step = 0
            back_key = 0
            for key in stop_symbol_dict:               #печатаем так, чтобы пост заканчивался абзацем, а не прерывался на полуслове
                if stop_symbol_dict[key] == 'paragraph':    #если это абзац
                    summa_one_step = key - start_paragraph
                    if summa_one_step < 4000:
                        back_key = key
                        continue
                    else:
                        bot.send_message(channel_id, paragraph[start_paragraph:back_key])     #печатаем очередной пост
                        time.sleep(5)
                        start_paragraph = key + 2
                        summa_one_step = 0
                else:  #иначе это картинка
                    if back_key != 0 and start_paragraph < key:                 #если картинка не первый и не предыдущий пост
                        if key - start_paragraph > 4000:
                            bot.send_message(channel_id, paragraph[start_paragraph:back_key])     #печатаем большой пост
                            start_paragraph = back_key + 2
                        bot.send_message(channel_id, paragraph[start_paragraph:key])     #печатаем пост до картинки
                        time.sleep(5)
                    picture_number = int(paragraph[key + 3]) * 10 + int(paragraph[key + 4])     #узнаем номер картинки
                    getOnePicture(picture_number)
                    start_paragraph = key + 7
            #печатаем последний пост:
            if len(paragraph[start_paragraph:]) > 2:        #два последних символа могут быть переносом строки
                bot.send_message(channel_id, paragraph[start_paragraph:])
    else:   #иначе статья помещается в один пост, но в ней могу буть картинки
        stop_symbol_dict = {}
        for paragraph in articles_whole_text[index]:        
            for i in range(len(paragraph) - 2):             #ищем индексы картинок и формируем словарь       
                if paragraph[i] == '$' and paragraph[i+1] == '#' and paragraph[i+2] == '$':
                    stop_symbol_dict[i] = 'picture'         #помечаем индекс как картинку
        if len(stop_symbol_dict) == 0:                      #если нету картинок, то печатем целиком
            bot.send_message(channel_id, articles_whole_text[index][0])
        else:       #иначе есть картинки
            stop_symbol_dict = dict(sorted(stop_symbol_dict.items()))       #отсортируем словарь по ключам
            start_paragraph = 0
            for key in stop_symbol_dict:
                if key != 0 and start_paragraph < key:                 #если картинка не первый и не предыдущий пост
                        bot.send_message(channel_id, paragraph[start_paragraph:key])     #печатаем очередной пост
                        time.sleep(5)
                picture_number = int(paragraph[key + 3]) * 10 + int(paragraph[key + 4])     #узнаем номер картинки
                getOnePicture(picture_number)
                start_paragraph = key + 7
            #печатаем последний пост:    
            if len(paragraph[start_paragraph:]) > 2:        #два последних символа могут быть переносом строки
                bot.send_message(channel_id, paragraph[start_paragraph:])

def getPictures(index, delta_number):
    pictures = site_parser.extractArticlePictures(delta_number)
    picture = pictures[index]
    if picture[0] != None:
        list_binary = pickle.loads(picture[0])
        count_pict = 1
        for i in range(len(list_binary)):           #записываем все картинки статьи в папку
            if not os.path.isdir('media_out'):
                os.mkdir('media_out')
            with open(f'media_out/picture_for_post_{count_pict}.jpg', 'wb') as file:
                file.write(list_binary[i])
            count_pict += 1

def getOnePicture(picture_number):
    with open(f'media_out/picture_for_post_{picture_number}.jpg', 'rb') as file:
        media_file = file.read()
    bot.send_photo(channel_id, media_file)
    time.sleep(5)                   #пауза между размещением фоток иначе получаю Error code: 429. Description: Too Many Requests: retry after 40

def pushArticles(chat_id):
    bot.send_message(chat_id, 'Запускаю поиск новых статей   🚀')
    old_number = site_parser.getNumberRecordsDb()
    site_parser.main()
    site_parser_2.main()
    new_number = site_parser.getNumberRecordsDb()
    delta_number = new_number[0] - old_number[0]
    if delta_number > 0:
        bot.send_message(chat_id, 'Есть новые статьи!')
        for index in range(delta_number):
            getPictures(index, delta_number)
            getArticle(index, delta_number)
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