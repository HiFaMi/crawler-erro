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
        # urlencode방식은 여기서 밖에 안쓰게 되니 info에서만 import
        from urllib.parse import urlencode

        payload = {'titleId': self.webtoon_id, 'no': self.no}
        url = 'http://comic.naver.com/webtoon/detail.nhn?'
        # urlencode를 통해 payload의 값이 key1=value1&key2=value2값으로 나오게 됨
        # url문자열과 urlencode를 통해 합쳐지 값을 더함다.
        # 문자열 + 문자열
        result = url + urlencode(payload)
        return result

    def get_image_url_list(self):
        # 그냥 함수가 실행 된 것을 알려줌
        # print('get_image-url_list_start')
        # 파일 경로
        file_path = 'data/episode_detail-{}-{}.html'.format(self.webtoon_id, self.no)
        # file_path 값을 이용하여 만약 해당 경로에 값이 없을경우 파일을 만들어주고
        # 그 안에 self.info의 값을 가져와 requests.get을 이용하여
        # 해당 url의 text(태그 및 속성)값을 가져와서 적고 저장
        # 해당경로 파일 존재시 읽어오기
        if not os.path.exists(file_path):
            url = requests.get(self.info)
            with open('{}'.format(file_path), 'wt') as f:
                f.write(url.text)
        with open('{}'.format(file_path), 'rt') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'lxml')
        # img_list는 BeautifulSoup을 이용하여 해당 태그 안에 있는 문자를 가져온다 -> 리스트 형식
        img_list = soup.select('div.wt_viewer > img')
        # img_list중 하나하나의 값을 img로 가져온 후 그 안의 'src' 값을 반환
        return [img.get('src') for img in img_list]

    def download_all_images(self):
        # download method를 이용하여 get_image_url_list method에 반환값 즉, src의 값을 url에 넣고 실행
        for url in self.get_image_url_list():
            self.download(url)

    def download(self, url_img):
        # Referer: 이전 페이지 URL(어떤 페이지를 거쳐서 왔는가?)
        # 몇몇 사이트는 Referer 헤더 값을 보고 응답을 거부하기도 함
        # 따라서 Referer 값을 커스텀 해 주어야 한다.
        url_referer = 'http://comic.naver.com/webtoon/list.nhn?titledId={}'.format(self.webtoon_id)
        headers = {
            'Referer': url_referer
        }

        response = requests.get(url_img, headers=headers)

        # '/'을 기준으로 1번만 split을 하는데 오른쪽 부터 'r(right)'split 값중 마지막 값
        file_name = url_img.rsplit('/', 1)[-1]
        dir_path = 'data/{}/{}'.format(self.webtoon_id, self.no)

        # os.mkdir(path) = <path>에 해당하는 디렉터리를 생성합니다.
        # os.makedirs(path) = 인자로 전달된 디렉터리를 재귀적으로 생성
        # 이미 디렉터리가 생성되어 있는 경우나 권한이 없어 생성할 수 없는 경우는 예외를 발생합니다.
        os.makedirs(dir_path, exist_ok=True)

        file_path = '{}/{}'.format(dir_path, file_name)

        # wb는 이진파일 쓰기 전용
        with open(file_path, 'wb') as f:
            f.write(response.content)


class Webtoon:

    def __init__(self, webtoon_id):

        self.webtoon_id = webtoon_id
        self.title = None
        self.author = None
        self.description = None
        self.episode_list = []

    def rework(self):

        payload = {'titleId': self.webtoon_id}
        if not os.path.exists('data/{}.html'.format(self.webtoon_id,)):
            toon_url = requests.get('http://comic.naver.com/webtoon/list.nhn', params=payload)
            with open('data/{}.html'.format(self.webtoon_id), 'wt') as f:
                f.write(toon_url.text)

        with open('data/{}.html'.format(self.webtoon_id), 'rt') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'lxml')

        # 각각의 태그 안에 있는 내용들을 BeautifulSoup을 통해 파싱
        title_list = soup.select('div.detail > h2')
        self.title = title_list[0].contents[0].strip()

        auth_list = soup.select('span."wrt_nm"')
        self.author = auth_list[0].string.strip()

        self.description = soup.p.string

    def update(self):
        page = 1

        if not os.path.exists('data/{}-{}.html'.format(self.webtoon_id, page)):
            while True:
                first_payload = {'titleId': self.webtoon_id, 'page': page}
                second_payload = {'titleId': self.webtoon_id, 'page': page + 1}
                first_toon_url = requests.get('http://comic.naver.com/webtoon/list.nhn', params=first_payload)
                second_toon_url = requests.get('http://comic.naver.com/webtoon/list.nhn', params=second_payload)
                first_parsing_soup = BeautifulSoup(first_toon_url.text, 'lxml')
                second_parsing_soup = BeautifulSoup(second_toon_url.text, 'lxml')
                first_page_title = first_parsing_soup.select('td.title > a')[0].string
                second_page_title = second_parsing_soup.select('td.title > a')[0].string

                if re.findall(r'(^.*?)화', first_page_title)[0] != re.findall(r'(^.*?)화', second_page_title)[0]:
                    with open('data/{}-{}.html'.format(self.webtoon_id, page), 'wt') as f:
                        f.write(first_toon_url.text)
                    page += 1
                else:
                    with open('data/{}-{}.html'.format(self.webtoon_id, page), 'wt') as f:
                        f.write(first_toon_url.text)
                    break

        while True:
            if os.path.exists('data/{}-{}.html'.format(self.webtoon_id, page)):
                with open('data/{}-{}.html'.format(self.webtoon_id, page), 'rt') as f:
                    html = f.read()
                soup = BeautifulSoup(html, 'lxml')
                # image_url
                list_src = soup.select("a > img['src']")

                # 각 화의 제목
                list_of_title = soup.select('td.title > a')

                # 별점 리스트
                rating_list = soup.select('div.rating_type > strong')

                # 등록일
                date_list = soup.select('td.num')

                # no요소를 빈 리스트 안에 넣은 후 반환
                finall_list = []
                no_list = soup.select('td.title > a[href]')
                for i in range(len(no_list)):
                    a = no_list[i].get('href')
                    # no값만 가져오기 위하여 href값 안에서 정규표현식을 이용하여 파싱
                    finall_list.append(re.findall(r'no=(.*?)&', a)[0])

                # 리스트에 값이 아닌 클래스 생성자를 넣음
                for i in range(len(list_of_title)):
                    inst = Episode(self.webtoon_id, finall_list[i], list_src[i + 1].get('src'), list_of_title[i].string,
                                   rating_list[i].string, date_list[i].string)
                    self.episode_list.append(inst)
                page += 1
            else:
                break

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
        dict_list = []
        # 모든 웹툰 제목과 그에 해당하는 titleId를 파싱하여 딕트 형태로 만듬
        for i in range(len(all_webtoon_list)):
            href = all_webtoon_list[i]['href']
            titleid = re.findall('titleId=(.*?)&.*?', href)
            dict_list.append({'Title': all_webtoon_list[i].string, 'titleId': titleid[0]})

        search_list = []
        # 찾으려는 웹툰의 부분적인 문자를 받아 그 문자가 포함되어 있는 모든 파일을 혹시 모를 중복을 없게 만들고
        # set을 사용한 경우 딕트 값으로 바뀌기 떄문에 list화 시켜준다.
        for i in range(len(dict_list)):
            if webtoon_name in dict_list[i]['Title']:
                search_list.append(dict_list[i]['Title'])
        search_list = list(set(search_list))

        # 해당 결과에 해당하는 리스트를 보여주고 찾으려는 웹튼의 번호를 적게 되면
        # webtoon에게는 선택 된 값이 주어진다.
        while True:
            for index, title in enumerate(search_list):
                print('{}. {}'.format(index + 1, title))

            user_input = input('선택: ')
            webtoon = search_list[int(user_input) - 1]
            break
        # webtoon에 주어진 값을 이용해 위에서 만든 딕트 타입과 비교하여
        # titleId를 반환하고 생성자를 만들어 준다.
        for i in range(len(dict_list)):
            if webtoon == dict_list[i]['Title']:
                return cls((dict_list[i]['titleId']))


class EpisodeImage:
    def __init__(self, episode, url):
        self.episode = episode
        self.url = url
        self.image_url_list = []

    def image_crawler(self, episode_user):

        if not os.path.exists('data/{}.html'.format(episode_user)):
            toon_url = requests.get(self.url)
            with open('data/{}.html'.format(episode_user), 'wt') as f:
                f.write(toon_url.text)

        with open('data/{}.html'.format(episode_user), 'rt') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'lxml')
        # 아래의 태그에 해당하는 태그를 파싱
        list_src = soup.select('div.wt_viewer > img')
        # 생성자를 만들어 준다
        user = EpisodeImage(self.episode, self.url)
        # 생성자의 리스트에 list_src의 태그 안에서 'src' 값만 넘겨준다.
        for i in range(len(list_src)):
            user.image_url_list.append(list_src[i]['src'])

        episode_user.image_list.append(user)


if __name__ == '__main__':
    print('안내) Ctrl+C로 종료합니다.')
    while True:
        user_search_input = input('검색할 웹툰명을 입력해주세요: ')
        toon = Webtoon.search_webtoon(user_search_input)
        toon.rework()
        toon.update()
        while True:
            print('현재 "{}" 웹툰이 선택되어 있습니다.'.format(toon.title))
            user_number_select = input('1. 웹툰 정보 보기\n2. 웹툰 저장하기\n3. 다른 웹툰 검색해서 선택하기\n선택: ')
            if user_number_select == '1':
                print('{}\n  작가명: {}\n  설명: {}\n  총 연재회수: {}'.format(
                    toon.title,
                    toon.author,
                    toon.description,
                    re.findall(r'(^.*?)화', toon.episode_list[0].title)[0]))
            elif user_number_select == '2':
                for number in range(len(toon.episode_list), 0, -1):
                    download = toon.episode_list[number-1]
                    download.download_all_images()
                    print('{}화 저장완료'.format(re.findall(r'(^.*?)화', download.title)[0]))
            else:
                break
