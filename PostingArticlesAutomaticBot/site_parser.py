import os
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from datetime import datetime
import pickle

def makeHtmlFile(name_file, data):
    if not os.path.isdir('data'):
        os.mkdir('data')
    with open(f'data/{name_file}.html', 'w', encoding='utf-8') as file:
        file.write(data)

    with open(f'data/{name_file}.html', 'r', encoding='utf-8') as file:
        data_file = file.read()
    return data_file

def getDataMain(url_main, name_file):
    try:
        req = requests.get(url_main)
    except Exception as ex:
        print(ex)

    data = req.text
    data_file = makeHtmlFile(name_file, data)
    return data_file

def makeDataArticles(data_file_main):
    soup = BeautifulSoup(data_file_main, 'html.parser')
    articles = soup.find_all('div', class_='tm-article-snippet tm-article-snippet')

    article_urls = []
    for article in articles:
        article_url = 'https://habr.com' + article.find('h2', class_='tm-title tm-title_h2').find('a').get('href')
        article_urls.append(article_url)
    return article_urls

def getDataArticle(article_url):
    try:
        req = requests.get(article_url)
    except Exception as ex:
        print(ex)  

    data = req.text
    name_file = article_url.split('/')[-2]
    data_file = makeHtmlFile(name_file, data)
    return data_file

def getArticleElements(soup):
    article_name = soup.find('h1', class_='tm-title tm-title_h1').find('span').text
    article_date = soup.find('span', class_='tm-article-datetime-published').find('time').get('title')
    article_author = soup.find('span', class_='tm-user-info tm-article-snippet__author').find('a', class_='tm-user-info__username').text
    return article_name, article_date, article_author

def getArticleWholeText(soup):
    try: 
        article_whole = soup.find('div', class_='article-formatted-body article-formatted-body article-formatted-body_version-2').find_all('p')   #считать всю статью
    except:
        article_whole = soup.find('div', class_='article-formatted-body article-formatted-body article-formatted-body_version-1') #считать статью только для кривой страницы
    article_whole_text = []
    count = 1

    previous_element = article_whole[0].previous_sibling                #есть ли первая картинка перед текстом статьи
    if previous_element != None: 
        if previous_element.find('img') != None:                        #нашли картинку
            article_whole_text.append(f'$#${count:02}\n\n')             #добавляем номер картинки
            count += 1

    for i in article_whole:
        temp = i.text                                                   #извлечь текст
        temp2 = ' '.join(temp.split())                                  #убрать лишние пробелы
        article_whole_text.append(temp2)
               
        next_element = i.next_sibling                                   #ищем картинку после абзаца текста
        if next_element != None:
            if next_element.find('img') != None:                        #нашли картинку
                article_whole_text.append(f'$#${count:02}')             #добавляем номер картинки
                count += 1
                next_element = next_element.next_sibling                #проверяем нет ли еще картинок до следующего абзаца
                while True:
                    if next_element == None:
                        break
                    if next_element.name == 'p' or next_element.name == '/div':     #дошли до следующего абзаца или конца текста на странице
                        break
                    else:
                        if next_element.find('img') != None:            #нашли еще картинку
                            article_whole_text.append(f'\n\n$#${count:02}')         #добавляем номер картинки и пустые строчки
                            count += 1
                        next_element = next_element.next_sibling

        article_whole_text.append('\n\n')                               #добавить две пустые строки после абзаца

    #print('Кол-во картинок: ', count)
    article_whole_text = [x for x in article_whole_text if x != '']     #убрать пустые элементы из списка
    return article_whole_text

def findPictures(soup):                                                 #поиск картинок на сайте
    picture_urls = [] 
    pictures = soup.find_all('figure', class_='full-width')
    if len(pictures) == 0:                                              #если картинок нету на сайте
        return picture_urls
    
    for picture in pictures:
        picture_url = picture.find('img').get('src')
        picture_urls.append(picture_url)
    return picture_urls

def getArticleImages(picture_urls):
    if len(picture_urls) == 0:                                          #если картинок нету на сайте
        list_binary = []
        return list_binary
    picture_list = []
    for picture_url in picture_urls:                                    #скачивание картинок в папку media
        name_file = picture_url.split('/')[-1] 
        req = requests.get(picture_url)
        data = req.content
        if not os.path.isdir('media'):
            os.mkdir('media')
        with open(f'media/{name_file}', 'wb') as file:
            file.write(data)
        with open(f'media/{name_file}', 'rb') as file:
            media_file = file.read()
        picture_list.append(media_file)
    list_binary = pickle.dumps(picture_list)                            #упаковка в один бинарник
    return list_binary

def parsingPages(article_urls):
    articles_data_list = []
    articles_pictures_list = []
    for article_url in article_urls:
        data_file = getDataArticle(article_url)
        soup = BeautifulSoup(data_file, 'html.parser')

        try:
            article_name, article_date, article_author = getArticleElements(soup)
            article_whole_text = getArticleWholeText(soup) 
            picture_urls = findPictures(soup)
            list_binary = getArticleImages(picture_urls)
        except Exception as ex:
            print(ex)

        articles_data_list.append(
            {
                'Сслыка на статью': article_url,
                'Название статьи': article_name,
                'Дата публикации': article_date,
                'Автор статьи': article_author,
                'Статья целиком': article_whole_text
            }
        )
        articles_pictures_list.append(list_binary)
    return articles_data_list, articles_pictures_list     

def saveJson(name_file, articles_data_list):
    with open(name_file, 'a', encoding='utf-8') as file:
        json.dump(articles_data_list, file, indent=4, ensure_ascii=False)

def saveDb(articles_data_list, articles_pictures_list):
    with sqlite3.connect('articles.db') as con:
        cur = con.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS articles (
                    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_url TEXT,
                    addition_date_in_db TEXT,
                    article_date TEXT,
                    article_name TEXT UNIQUE,
                    article_author TEXT,
                    article_whole_text TEXT,
                    pictures BLOB
                    )''') 

        for i in range(20):      #20 статей на странице
            try:
                stroka = ''.join(articles_data_list[i]['Статья целиком'])   #преобразование списка в строку
                cur.execute('INSERT INTO articles (article_url, article_date, article_name, article_author, article_whole_text) VALUES(?, ?, ?, ?, ?)', 
                            (articles_data_list[i]['Сслыка на статью'], articles_data_list[i]['Дата публикации'], articles_data_list[i]['Название статьи'], 
                             articles_data_list[i]['Автор статьи'], stroka))

                time_now = datetime.now()
                addition_date_in_db = f'{time_now.year}-{time_now.month}-{time_now.day}, {time_now.hour}:{time_now.minute}'
                cur.execute('UPDATE articles SET addition_date_in_db = ? WHERE article_name = ?', (addition_date_in_db, articles_data_list[i]['Название статьи']) )

                if len(articles_pictures_list[i]) != 0:                     #только если в статье есть картинки
                    cur.execute('UPDATE articles SET pictures = ? WHERE article_name = ?', (articles_pictures_list[i], articles_data_list[i]['Название статьи']) )
            except Exception:   #пропускаю если была попытка записать в БД такую же статью
                pass

def main():
    for pages in range(1, 2):      #первая страница сайта
        data_file_main = getDataMain(f'https://habr.com/ru/hubs/python/articles/page{pages}/', f'data_main_{pages}')
        article_urls = makeDataArticles(data_file_main)
        articles_data_list, articles_pictures_list = parsingPages(article_urls)
        saveJson('articles_data.json', articles_data_list)
        saveDb(articles_data_list, articles_pictures_list)

def extractArticlesName(delta_number):
    with sqlite3.connect('articles.db') as con:
        cur = con.cursor()
        cur.execute('SELECT article_name FROM articles ORDER BY article_id DESC LIMIT ?', (delta_number,))  #новые записи из БД отсортированных по id
        articles_name = cur.fetchall()
    return articles_name        

def extractArticleWholeText(delta_number):
    with sqlite3.connect('articles.db') as con:
        cur = con.cursor()
        cur.execute('SELECT article_whole_text FROM articles ORDER BY article_id DESC LIMIT ?', (delta_number,))  #новые записи из БД отсортированных по id
        article_whole_text = cur.fetchall()
    return article_whole_text

def extractArticlePictures(delta_number):
    with sqlite3.connect('articles.db') as con:
        cur = con.cursor()
        cur.execute('SELECT pictures FROM articles ORDER BY article_id DESC LIMIT ?', (delta_number,))  #новые записи из БД отсортированных по id
        article_pictures = cur.fetchall()
    return article_pictures

def getNumberRecordsDb():
    if os.path.exists('articles.db') == False:
        return (0, )
    with sqlite3.connect('articles.db') as con:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM articles')  #количество записей в БД
        number_records = cur.fetchone()
    return number_records