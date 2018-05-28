# 우리가 웹 브라우저를 통애 보는 HTML문서는 GET요정의 결과
# requests를 사용해 'http://comic.naver.com/webtoon/weekday.nhn'
# 요청결과를 response 변수에 할당해서 status_Code속성을 출력

import requests as rt

response = rt.get('http://comic.naver.com/webtoon/weekday.nhn')
print(response.status_code)

# HTML GET요청을 받아온 Content를 text데이터로 리턴
print(response.text)

f = open('weekday.html', 'wt')
f.write(response.text)
f.close()
