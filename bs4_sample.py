# 1방법
with open('weekday.html', 'rt') as f:
    html = f.read()

# 2방법
# f = open('weekday.html', 'rt')
# html = f.read()
# f.close()
#
# 3방법
# html = open('weekday.html', 'rt').read()

print(html)
