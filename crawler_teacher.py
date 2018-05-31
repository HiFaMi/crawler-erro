import os
import requests
from bs4 import BeautifulSoup
from urllib import parse

html = '''http://comic.naver.com/webtoon/list.nhn?titleId=703845&weekday=wed'''

if not os.path.exists('data/espisode_list.html'):
    payload = {'titleId': '703845', 'weekday': 'wed'}
    toon_url = requests.get('http://comic.naver.com/webtoon/list.nhn', params=payload)
    print(toon_url.url)
    with open('data/espisode_list.html', 'wt') as f:
        f.write(toon_url.text)

with open('data/espisode_list.html', 'rt') as f:
    html = f.read()


soup = BeautifulSoup(html, 'lxml')
title_list = soup.select_one('div.detail > h2')
title = title_list.contents[0].strip()
author = title_list.contents[1].get_text(strip=True)
description = soup.select_one("div.detail > p").get_text(strip=True)

print(' -제목: {}\n -작가: {}\n -설명: {}'.format(title, author, description))

table = soup.select_one('table.viewList')
tr_list = table.select('tr')
result = []
for index, tr in enumerate(tr_list[1:]):
    if tr.get('class'):
        continue

    url_thumbnail = tr.select_one('td:nth-of-type(1) img').get('src')
    url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')
    query_string = parse.urlsplit(url_detail).query
    query_dict = parse.parse_qs(query_string)
    num = query_dict['no'][0]

    title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)

    rating = tr.select_one('td:nth-of-type(3) strong').get_text(strip=True)

    created_data = tr.select_one('td:nth-of-type(4)').get_text(strip=True)

    result.append({'url_thumbnail': url_thumbnail,
                   'title': title,
                   'rating': rating,
                   'created_data': created_data,
                   'no': num})

print(result)