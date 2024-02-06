import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

logging.basicConfig(filename='example.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_to_date(date_list):
    month_dict = {'янв.': 1, 'февр.': 2, 'мар.': 3, 'апр.': 4, 'мая': 5, 'июн.': 6,
                  'июл.': 7, 'авг.': 8, 'сент.': 9, 'окт.': 10, 'нояб.': 11, 'дек.': 12}
    month = month_dict.get(date_list[1])
    day = int(date_list[0])
    year = int(date_list[2])
    date_obj = datetime(year, month, day)
    return date_obj

def parse(url):
    i = 1
    final_dict = {'title':[], 'link':[], 'date_published':[], 'date_updated':[]}
    try:
        while True:
            response = requests.get(url + str(i))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                posts = soup.find_all(class_='index_article__15dX1')
                for post in posts:
                    try:
                        final_dict['link'].append('https://www.okx.com' + post.find('a')['href'])
                        final_dict['date_published'].append(convert_to_date(list(post.find_all('span', class_='index_dateRow__3aYpG'))[0].text.split()[1:4]))
                        final_dict['date_updated'].append(convert_to_date(list(post.find_all('span', class_='index_dateRow__3aYpG'))[0].text.split()[5:8]))
                        final_dict['title'].append(post.find('div', class_='index_title__6wUnB').text.strip())
                    except Exception as e:
                        logging.error(f'Error occurred while parsing post: {e}')
                i += 1
            else:
                logging.error(f'Request to the website returned status code: {response.status_code}')
                break
    except Exception as e:
        logging.error(f'An error occurred during parsing: {e}')
    return final_dict

def save(res, path, start_date, end_date):
    try:
        df = pd.DataFrame(res)
        converted_start_date = datetime.strptime(start_date, '%d.%m.%Y')
        converted_end_date = datetime.strptime(end_date, '%d.%m.%Y')
        df = df[(df['date_published'] >= converted_start_date) & (df['date_published'] <= converted_end_date)]
        file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_okx_news'
        df.to_excel(f"{path}/{file_name}.xlsx", index=False)
    except Exception as e:
        logging.error(f'An error occurred while saving the data: {e}')

if __name__ == "__main__":
    #input examples:
    #START_DATE = '06.02.2024'
    #END_DATE = '06.02.2024'
    #FOLDER = "C:/Users/kamil/PycharmProjects/equivalent_script"

    START_DATE = input()
    END_DATE = input()
    FOLDER = input()
    URL = 'https://www.okx.com/ru/help/section/announcements-latest-announcements/page/'
    try:
        RES = parse(URL)
        save(RES, FOLDER, START_DATE, END_DATE)
    except Exception as e:
        logging.critical(f'An unexpected error occurred: {e}')


