import telebot
from config import token, channel_id
import site_parser
import os
import pickle

bot = telebot.TeleBot(token)

def keyboardMain():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    articles_name = site_parser.extractArticlesName()       #извлекаем название статей из базы
    for i in range(10):         #берем названия первых десяти статей
        button= telebot.types.InlineKeyboardButton(text=articles_name[i][0], callback_data=f'article_{i}') 
        keyboard.add(button)
    button_update= telebot.types.InlineKeyboardButton(text='🔄  Обновить список статей  🔄', callback_data='update') 
    keyboard.add(button_update)
    return keyboard

def keyboardMini():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_return = telebot.types.InlineKeyboardButton(text='⬅️  Вернуться в главное меню', callback_data='return_menu') 
    button_push = telebot.types.InlineKeyboardButton(text='🛜  Разместить пост на канеле  🚀', callback_data='push_to_channel')
    keyboard.add(button_return, button_push)
    return keyboard

def getArticle(callback, index, chat_id):
    if chat_id == channel_id:
        bot.send_message(chat_id, '⬇️  Внимание, 🍋 новая статья!  ⬇️')
    articles_whole_text = site_parser.extractArticleWholeText()     #извлекаем статьи из базы
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
                    bot.send_message(chat_id, paragraph[start_paragraph:stop_symbol[k-1]])     #печатаем очердной пост
                    start_paragraph = stop_symbol[k] + 2
                    summa_one_step = 0
            #печатаем последний пост:        
            bot.send_message(chat_id, paragraph[start_paragraph:])
    else:
        bot.send_message(chat_id, articles_whole_text[index][0])

def getPictures(callback, index, chat_id):
    pictures = site_parser.extractArticlePictures()
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
            bot.send_photo(chat_id, media_file)
            count_pict += 1
        if chat_id != channel_id:
            bot.send_message(chat_id, '⬆️  Статья успешно загружена!  ⬆️', reply_markup=keyboardMini()) 
        else:
            bot.send_message(chat_id, '⬆️  Статья успешно загружена!  ⬆️')  
    else:
        if chat_id != channel_id:
            bot.send_message(chat_id, '⬆️  Статья успешно загружена!  ⬆️', reply_markup=keyboardMini())
        else:
            bot.send_message(chat_id, '⬆️  Статья успешно загружена!  ⬆️')

""" def returnMain(message, callback):      #создаем кнопку Вернуться в главное меню
    markup = telebot.types.InlineKeyboardMarkup()
    button_return = telebot.types.InlineKeyboardButton(message, callback_data=callback)
    markup.add(button_return)
    return markup """

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!  📖  Выбери статью  ⬇️', reply_markup=keyboardMain())

""" @bot.message_handler(content_types=['text'])
def testAnswer(message):
    answer = 'А вот и Я!'
    bot.send_message(channel_id, answer) """    

@bot.callback_query_handler(func=lambda callback: True)
def callbackMessage(callback):
    if 'article_' in callback.data:
        global index 
        index = int(callback.data.split('_')[1])
        getArticle(callback, index, callback.message.chat.id)
        getPictures(callback, index, callback.message.chat.id)

    elif callback.data == 'return_menu':
        bot.send_message(callback.message.chat.id, '▶️  Главное меню  📖  Выбери статью  ⬇️', reply_markup=keyboardMain())

    elif callback.data == 'push_to_channel':
        bot.send_message(callback.message.chat.id, '⏳  Пост размещается...    ⏳')
        getArticle(callback, index, channel_id)
        getPictures(callback, index, channel_id)
        bot.send_message(callback.message.chat.id, '✅  Пост успешно размещен!')
        bot.send_message(callback.message.chat.id, '▶️  Главное меню  📖  Выбери статью  ⬇️', reply_markup=keyboardMain())    

    elif callback.data == 'update':
        bot.send_message(callback.message.chat.id, '⏳  Статьи обновляются...  ⏳')
        site_parser.main()
        bot.send_message(callback.message.chat.id, '🆕  Главное меню  🔄  Выбери статью  ⬇️', reply_markup=keyboardMain())


if __name__ == '__main__':
    bot.polling(non_stop=True)   