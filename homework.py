import re


def get_text1(tag_string):

    result = re.findall(r'<.*?>(.*?)<.*?>', tag_string)
    print(result)


def get_text2(tag_string):

    p = re.compile(r'<.*?>(.*?)<.*?>')
    result = re.findall(p, tag_string)
    text_list=[]
    for i in result:
        if i != '':
            text_list.append(i)
    print(text_list)


def get_text3(tag_string):

    p = re.compile(r'<.*?>(.*?)<.*?>')
    result = re.findall(p, tag_string)

    print(result[-1])


def get_tag_attr(tag_string, attr):
    if attr in tag_string:
        p = re.compile(r'<.*?{}="(.*?)".*?>'.format(attr))
        result = re.findall(p, tag_string)

    for i in range(len(result)):
        print(result[i])