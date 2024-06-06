import telebot
from config import token
import site_parser

def keyboardMain():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    articles_name = site_parser.extractArticlesname()       #извлекаем название статей из базы
    for i in range(10):         #берем названия первых десяти статей
        button= telebot.types.InlineKeyboardButton(text=articles_name[i][0], callback_data=f'article_{i}') 
        keyboard.add(button)
    button_update= telebot.types.InlineKeyboardButton(text='🔄  Обновить список статей  🔄', callback_data='update') 
    keyboard.add(button_update)
    return keyboard

def getArticle(callback, index):
    articles_whole_text = site_parser.extractArticleWholeText()     #звлекаем статьи из базы
    if len(articles_whole_text[index][0]) > 4096:       #печатаем index статью в несколько постов если она огромная
        for x in range(0, len(articles_whole_text[index][0]), 4096):
            bot.send_message(callback.message.chat.id, articles_whole_text[index][0][x:x+4096], reply_markup=returnMain('⬅️  Вернуться в главное меню', 'return_menu'))
    else:
        bot.send_message(callback.message.chat.id, articles_whole_text[index][0], reply_markup=returnMain('⬅️  Вернуться в главное меню', 'return_menu'))

def returnMain(message, callback):      #создаем кнопку Вернуться в главное меню
    markup = telebot.types.InlineKeyboardMarkup()
    button_return = telebot.types.InlineKeyboardButton(message, callback_data=callback)
    markup.add(button_return)
    return markup

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!  📖  Выбери статью  ⬇️', reply_markup=keyboardMain())

@bot.callback_query_handler(func=lambda callback: True)
def callbackMessage(callback):
    if 'article_' in callback.data:
        index = int(callback.data.split('_')[1])
        getArticle(callback, index)

    elif callback.data == 'return_menu':
        bot.send_message(callback.message.chat.id, '▶️  Главное меню  📖  Выбери статью  ⬇️', reply_markup=keyboardMain())

    elif callback.data == 'update':
        bot.send_message(callback.message.chat.id, '⏳  Статьи обнавляются...  ⏳')
        site_parser.main()
        bot.send_message(callback.message.chat.id, '🆕  Главное меню  🔄  Выбери статью  ⬇️', reply_markup=keyboardMain())


if __name__ == '__main__':
    bot.polling(non_stop=True)   