import pymongo
import env
from bs4 import BeautifulSoup

client = pymongo.MongoClient(env.mongoPath)
db = client[env.mongoName]


def insertUrl(url):
    db.coll.insert_one({'url': url})


def insertDB(name, identity, city, url, phone, houseType, houseCondition, sex):
    print(name, identity, city, url, phone, houseType, houseCondition, sex)
    db.coll.insert_one({'name': name,
                        'identity': identity,
                        'city': city,
                        'url': url,
                        'phone': phone,
                        'houseType': houseType,
                        'houseCondition': houseCondition,
                        'sex': sex})


def name(content):
    return content.find('div', class_='avatarRight').i.text.split('i')[0]


def attr(content, id):
    attr = ''
    cnt = 0
    while cnt < len(content):
        if content[cnt].text.split(' :  ')[0] == id:
            attr = content[cnt].text.split(' :  ')[1]
            break
        cnt += 1
    return attr


def phone(content):
    return content.find('span', class_='dialPhoneNum')['data-value']


def identity(content):
    identity = content.find('div', class_='avatarRight').div.text
    if '屋主' in identity:
        identity = '屋主'
    elif '代理人' in identity:
        identity = '代理人'
    elif '仲介' in identity:
        identity = '仲介'
    return identity


def sex(content):
    sex = '男女生皆可'
    length = len(content)
    cnt = 0
    while cnt < length:
        if content[cnt].find('div', class_='one').text == '性別要求':
            sex = content[cnt].em.text
            break
        cnt += 1
    return sex
