from bs4 import BeautifulSoup
import time
import site_parser
from selenium import webdriver
from selenium.webdriver.common.by import By

def makeDataArticles(data_file_main):
    soup = BeautifulSoup(data_file_main, 'html.parser')
    articles = soup.find_all('a', class_='jsx-3299022473 link')

    article_urls = []
    for article in articles:
        article_url = 'https://www.ferra.ru' + article.get('href')
        article_urls.append(article_url)
    return article_urls

def getArticleElements(soup):
    article_name = soup.find('h1', class_='jsx-2848471422 Cqvs5c42').text
    print(article_name)
    article_date = soup.find('div', class_='qzByRHub P5lPq1qA').text[13:]
    article_author = soup.find('a', class_='jsx-3100841914 link jsx-475206913 VTDVsGBI').text
    return article_name, article_date, article_author

def getArticleWholeText(soup):
    try: 
        article_whole = soup.find('div', class_='jsx-3295165523 text P7usgGGL jsx-3479134751 text').find_all('p')   #считать всю статью
    except:
        print('Вот тут надо парсить текст по-другому')
    article_whole_text = []
    count = 1

    article_whole_text.append(f'$#${count:02}\n\n')             #добавляем номер картинки
  
    for i in article_whole:
        temp = i.text                                                   #извлечь текст
        temp2 = ' '.join(temp.split())                                  #убрать лишние пробелы
        article_whole_text.append(temp2)
    
        article_whole_text.append('\n\n')                               #добавить две пустые строки после абзаца

    article_whole_text = [x for x in article_whole_text if x != '']     #убрать пустые элементы из списка
    return article_whole_text

def findPictures(article_url):                                    #поиск картинок на сайте
    picture_urls = [] 

    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])      #подавление журанала ошибок (иначе вылетает ошбика Bluetooth драйвера)
    options.add_argument('--headless')                                          #для запуска браузера в фоновом режиме
    
    with webdriver.Chrome(options=options) as browser:
        browser = webdriver.Chrome(options=options)
        try:
            browser.get(article_url)
            time.sleep(5)
        except Exception as ex:
            print(ex)  
        pictures = browser.find_elements(By.CLASS_NAME, 'sX8xPdQU')
          
        for picture in pictures[0:1]:                                       #берем только первую картинку
            picture_url = picture.get_attribute('src')
            picture_urls.append(picture_url)
            print('picture_urls', picture_urls)
    return picture_urls

def parsingPages(article_urls):
    articles_data_list = []
    articles_pictures_list = []
    for article_url in article_urls:
        data_file = site_parser.getDataArticle(article_url)
        soup = BeautifulSoup(data_file, 'html.parser')

        try:
            article_name, article_date, article_author = getArticleElements(soup)
            article_whole_text = getArticleWholeText(soup) 
            picture_urls = findPictures(article_url)                    #вот нужен url страницы для selenium
            list_binary = site_parser.getArticleImages(picture_urls)
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

def main():
    for pages in range(1, 2):      #первая страница сайта
        data_file_main = site_parser.getDataMain(f'https://www.ferra.ru/label/kosmos?page={pages}/', f'data_main_{pages}')
        article_urls = makeDataArticles(data_file_main)
        articles_data_list, articles_pictures_list = parsingPages(article_urls)
        site_parser.saveJson('articles_data.json', articles_data_list)
        site_parser.saveDb(articles_data_list, articles_pictures_list)

