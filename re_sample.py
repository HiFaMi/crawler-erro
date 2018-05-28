import re

with open('weekday.html', 'rt') as f:
    html = f.read()

#print(html)

p = re.compile(r'<a.*?>(.*?)</a>')
p = re.compile(r'''<a                      # <a로 시작하며
                   .*?class="title".*?>    # class="title"문장이 들어있고
                                           #>가 등장하기 전까지의 임의의 문자 최소 반복, >까지
                   (.*?)                   # 임의의 문자 반복
                   </a>                    # </a>가 나오기 전까지''', re.VERBOSE)

m = re.findall(p, html)

print(m)