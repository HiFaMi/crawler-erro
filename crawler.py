import os
import requests
from bs4 import BeautifulSoup
import re

html = '''http://comic.naver.com/webtoon/list.nhn?titleId=703845&weekday=wed'''

# os.path.exists()를 이용하여 data/espisode_list.html이 존재하는지 판단
# 존재하지 않을 경우 paylod의 key값과 value값을 이용해 requests.get를 이용
# key 값과 value값이 url에 포함되도록 완성
# url이 완성되었으면 그 url의 text값을 저장
if not os.path.exists('data/espisode_list.html'):
    payload = {'titleId': '703845', 'weekday': 'wed'}
    toon_url = requests.get('http://comic.naver.com/webtoon/list.nhn', params=payload)
    print(toon_url.url)
    with open('data/espisode_list.html', 'wt') as f:
        f.write(toon_url.text)
# else일 경우 즉, data/espisode_list.html 파일이 있을경우 html의 변수에 text를 읽어와 저장
with open('data/espisode_list.html', 'rt') as f:
    html = f.read()


soup = BeautifulSoup(html, 'lxml')
# soup.select를 통해 h2값을 가져오고 title_list에 저장
title_list = soup.select('h2')
title = title_list[1].contents[0].strip()
auth_list = soup.select('span[class="wrt_nm"]')
author = auth_list[0].string.strip()
description = soup.p.string

print(' -제목: {}\n -작가: {}\n -설명: {}'.format(title, author, description))


# image_url
list_src = soup.select("a > img['src']")

# 각 화의 제목
list_of_title = soup.select('td.title > a')

# 별점 리스트
rating_list = soup.select('div.rating_type > strong')

# 등록일
date_list = soup.select('td.num')

# no요소를 빈 리스트 안에 넣은 후 반환
# 값이 두번씩 반환되기에 step을 두번씩 주어서 반환
finall_list = []
no_list = soup.select('td > a[href]')
for i in range(1, len(no_list), 2):
    a = no_list[i].get('href')
    finall_list.append(re.findall(r'no=(.*?)&', a)[0])

episode_list = []

for i in range(len(list_of_title)):
    all_dict = {'url_thumbnail': list_src[i+1].get('src'),
                'title': list_of_title[i].string,
                'rating': rating_list[i].string,
                'created_date': date_list[i].string,
                'no': finall_list[i]
                }

    episode_list.append(all_dict)

class Episode:

    def __init__(self, webtoon_id, no, url_thumbnail, title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date

    @property
    def info(self):
        from urllib import parse

        url = 'http://comic.naver.com/webtoon/list.nhn?'

        return parse.urljoin(url, '&titleld={}'.format(self.webtoon_id), 'no='.format(self.no))



