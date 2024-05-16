import requests
from bs4 import BeautifulSoup
import json

def getDataMain(url_main, name_file):
    url = url_main
    req = requests.get(url)
    data = req.text

    with open(name_file, 'w', encoding='utf-8') as file:
        file.write(data)

    with open(name_file, 'r', encoding='utf-8') as file:
        data_file = file.read()
    return data_file

def makeDataArticles(data_file_main):
    soup = BeautifulSoup(data_file_main, 'html.parser')
    articles = soup.find_all('article', class_='post')

    article_urls = []
    for article in articles:
        article_url = 'https://astronews.space' + article.find('div', class_='title').find('a').get('href')
        article_urls.append(article_url)
    return article_urls

def parsingPages(article_urls):
    articles_data_list = []
    for article_url in article_urls:
        req = requests.get(article_url)
        data = req.text
        data_name = article_url.split('/')[-2]
    
        with open(f'data/{data_name}.html', 'w', encoding='utf-8') as file:
            file.write(data)

        with open(f'data/{data_name}.html', 'r', encoding='utf-8') as file:
            data_file = file.read()

        soup = BeautifulSoup(data_file, 'html.parser')

        try:
            article_name = soup.find('article', class_='post').find('div', class_='title').find('h1').text
        except Exception as ex:
            print(ex)

        try:
            article_date = soup.find('article', class_='post').find('div', class_='meta').find('time', class_='published').text
        except Exception as ex:
            print(ex)

        try:
            article_author = soup.find('article', class_='post').find('div', class_='meta').find('a', class_='author').find('span', class_='name').text
        except Exception as ex:
            print(ex)

        try:
            article_whole = soup.find('article', class_='post').find_all('p')   #считать всю статью
            article_whole_text = []
            for i in article_whole:
                temp = i.text                                                   #извлечь текст
                temp2 = ' '.join(temp.split())                                  #убрать лишние пробелы
                article_whole_text.append(temp2)

            #на некоторых страницах в последнем абзаце есть реклама - удаляю её
            unnecessary = 'Любой сайт развивается благодаря тому, что о нем узнает все больше людей. Не проходите мимо, поделитесь новостями космоса:'
            try:
                article_whole_text.remove(unnecessary)
            except ValueError:
                pass

            article_whole_add = soup.find_all('div', class_='box-note')         #на некоторых страницах последние абзацы статьи записаны в class "box-note"
            for i in article_whole_add:
                temp = i.text                                                   #извлечь текст
                temp2 = ' '.join(temp.split())                                  #убрать лишние пробелы
                article_whole_text.append(temp2)

            article_whole_text = [x for x in article_whole_text if x != '']     #убрать пустые элементы из списка
        except Exception as ex:
            print(ex)

        articles_data_list.append(
            {
                'Название статьи': article_name,
                'Дата публикации': article_date,
                'Автор статьи': article_author,
                'Статья целиком': article_whole_text
            }
        )
    return articles_data_list    

def saveJson(name_file, articles_data_list):
    with open(name_file, 'w', encoding='utf-8') as file:
        json.dump(articles_data_list, file, indent=4, ensure_ascii=False)

#вызов функций(сама программа)
print('Start!', 'Please wait...')

data_file_main = getDataMain('https://astronews.space/stars/', 'data_main.html')

article_urls = makeDataArticles(data_file_main)

articles_data_list = parsingPages(article_urls)

saveJson('articles_data.json', articles_data_list)

print ('Finish!')