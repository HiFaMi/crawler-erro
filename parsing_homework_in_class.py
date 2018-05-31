import os
import requests
from bs4 import BeautifulSoup
import re


class Episode:

    def __init__(self, webtoon_id, no, url_thumbnail, title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date
        self.image_list = []

    @property
    def info(self):
        from urllib.parse import urlencode

        payload = {'titleId': self.webtoon_id, 'no': self.no}
        url = 'http://comic.naver.com/webtoon/detail.nhn?'

        result = url + urlencode(payload)
        return result


class Webtoon:

    def __init__(self, webtoon_id):

        self.webtoon_id = webtoon_id
        self._title = None
        self._author = None
        self._description = None
        self._episode_list = []
        self._html = ''
        # 초기화 할때 rework method를 이용하여 각 속성값을 저장


    def _get_info(self, attr_name):
        if not getattr(self, attr_name):
            self.rework()
        return getattr(self, attr_name)

    @property
    def title(self):
        if self._title is None:
            self.rework()
        return self._title

    @property
    def author(self):
        if self._author is None:
            self.rework()
        return self._author

    @property
    def description(self):
        if self._description is None:
            self.rework()
        return self._description

    @property
    def html(self):

        if self._html == '':
            payload = {'titleId': self.webtoon_id}
            if not os.path.exists('data/{}.html'.format(self.webtoon_id)):
                toon_url = requests.get('http://comic.naver.com/webtoon/list.nhn', params=payload)
                with open('data/{}.html'.format(self.webtoon_id), 'wt') as f:
                    f.write(toon_url.text)

            with open('data/{}.html'.format(self.webtoon_id), 'rt') as f:
                html = f.read()
            self._html = html
        return self._html

    def rework(self):

        soup = BeautifulSoup(self.html, 'lxml')
        title_list = soup.select('div.detail > h2')
        auth_list = soup.select('span."wrt_nm"')

        self._title = title_list[0].contents[0].strip()
        self._author = auth_list[0].string.strip()
        self._description = soup.p.string

    def update(self):

        self.episode_list = []
        soup = BeautifulSoup(self.html, 'lxml')
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
        no_list = soup.select('td.title > a[href]')
        for i in range(0, len(no_list)):
            a = no_list[i].get('href')
            finall_list.append(re.findall(r'no=(.*?)&', a)[0])

        for i in range(len(list_of_title)):
            inst = Episode(self.webtoon_id, finall_list[i], list_src[i + 1].get('src'), list_of_title[i].string,
                           rating_list[i].string, date_list[i].string)
            self._episode_list.append(inst)

    @property
    def episode_list(self):
        if not self._episode_list:
            self.update()
        return self._episode_list

    @classmethod
    def search_webtoon(cls, webtoon_name):

        if not os.path.exists('data/all_webtoon.html'):
            all_webtoon_url = requests.get('http://comic.naver.com/webtoon/weekday.nhn')
            with open('data/all_webtoon.html', 'wt') as f:
                f.write(all_webtoon_url.text)

        with open('data/all_webtoon.html', 'rt') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'lxml')

        all_webtoon_list = soup.select('div.col_inner > ul > li > a')
        all_dict_webtoon_list = []

        for i in range(len(all_webtoon_list)):
            href = all_webtoon_list[i]['href']
            titleid = re.findall('titleId=(.*?)&.*?', href)
            all_dict_webtoon_list.append({'Title': all_webtoon_list[i].string, 'titleId': titleid[0]})

        search_list = []
        for i in range(len(all_dict_webtoon_list)):
            if webtoon_name in all_dict_webtoon_list[i]['Title']:
                search_list.append(all_dict_webtoon_list[i]['Title'])
        search_list = list(set(search_list))

        while True:
            for index, title in enumerate(search_list):
                print('{}. {}'.format(index + 1, title))

            user_input = input('선택: ')
            webtoon = search_list[int(user_input) - 1]
            break

        for i in range(len(all_dict_webtoon_list)):
            if webtoon == all_dict_webtoon_list[i]['Title']:
                # user는 classmethod에서의 생성자 호출 변수
                return cls((all_dict_webtoon_list[i]['titleId']))


class EpisodeImage:

    def __init__(self, name_of_episode, episode_url):

        self.episode = name_of_episode
        self.url = episode_url
        self.image_url_list = []

    def image_crawler(self, episode_user):

        if not os.path.exists('data/{}.html'.format(episode_user)):
            toon_url = requests.get(self.url)
            with open('data/{}.html'.format(episode_user), 'wt') as f:
                f.write(toon_url.text)

        with open('data/{}.html'.format(episode_user), 'rt') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'lxml')
        list_src = soup.select('div.wt_viewer > img')

        user = EpisodeImage(self.episode, self.url)

        for i in range(len(list_src)):
            user.image_url_list.append(list_src[i]['src'])

        episode_user.image_list.append(user)


if __name__ == '__main__':
    webtoon1 = Webtoon(703845)
    print(webtoon1.title)
    print(webtoon1.author)
    print(webtoon1.description)

    for episode in webtoon1.episode_list:
        print(episode)

