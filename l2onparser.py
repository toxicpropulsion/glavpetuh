import re
import string
import urllib.request
import urllib.parse
import requests

from urllib.parse import quote_from_bytes as qfb
from selenium import webdriver
from pprint import pprint
from bs4 import BeautifulSoup

url = 'http://l2on.net'
OUTPUT = \
"""
*{}*
_{}_
[{}]({})
Раса: {}
Класс: {}
Макс. HP: `{}`
Макс. MP: `{}`
Клан: {}
Альянс: {}
Замечен: {}
Обновлен: {}
Торговля: {}
"""

# *bold text*
# _italic text_
# [text](http://www.example.com/)
# `inline fixed-width code`
# ```text
# pre-formatted fixed-width code block
# ```


def is_valid(nickname):
    for char in nickname:
        if char in string.punctuation + string.whitespace:
            return 0

    pattern = re.compile('[а-яА-ЯёЁ]')
    match = re.search(pattern, nickname)

    if match:
        return 1


def clean_strings(dct):
    cleaned = {}
    for k, v in dct.items():
        cleaned[k] = re.sub('\\n', '', v)
    return cleaned


def parse(nickname):
    valid = is_valid(nickname)

    if valid == 0:
        return 'Невалидное имя'
    elif valid == 1:
        name = nickname.encode('windows-1251')
    else:
        name = nickname

    values = {'setworld': 1092,
              'c': 'userdata',
              'a': 'search',
              'type': 'char',
              'name': name}

    req = requests.get(url, params=values)  # ConnectionError
    soup = BeautifulSoup(req.text, 'html.parser')
    table = soup.find_all('a', 'black', href=re.compile('id'))
    players = table[::2]

    player_url = None

    for i in players:
        if i.text.lower() == nickname.lower():
            m = re.search('id=[0-9]+', str(i))
            start = m.span()[0]
            end = m.span()[1]
            player_id = str(i)[start:end]
            player_url = 'http://l2on.net/?c=userdata&a=char&' + player_id
            break

    if not player_url:
        return 'Ничего не найдено'
    # else:
    #     return player_url

    # start
    # driver = webdriver.Firefox()
    driver = webdriver.PhantomJS(executable_path="D:\Downloads\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    driver.get(player_url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    char_head = soup.find_all('table', 'char-head')[0]
    player_header = char_head.find_all('h1')[0]
    player_name =  player_header.contents[0] # name
    player_comments = player_header.find_all('a')[0]
    player_comments_link = player_comments.attrs['href'] # comments url
    player_comments_string = player_comments.string # comment's url text
    player_values = soup.find_all('table', 'values')[0]
    player_values_dict = {}

    for tag in player_values.tbody:
        try:
            player_values_dict[tag.th.string] = tag.td.text
            # print(tag.th.string, '---', tag.td.text)
        except AttributeError:
            pass

    pvd = clean_strings(player_values_dict) # dict of cleaned values

    output = OUTPUT.format(player_name, pvd['Уровень'],
                           player_comments_string, 
                           player_comments_link,
                           pvd['Раса'],
                           pvd['Класс'],
                           pvd['Макс. HP'],
                           pvd['Макс. MP'],
                           pvd['Клан'],
                           pvd['Альянс'],
                           pvd['Замечен'],
                           pvd['Обновлён'],
                           pvd['Торговля'],)

    return output

if __name__ =='__main__':
    pass