import pymongo
from bs4 import BeautifulSoup

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client.db591


def insertDB(name, identity, location, phone, houseType, houseCondition, sex):
    print(sex, location, houseCondition, houseType, phone, identity, name)
    db.coll.insert_one({'name': name,
                        'identity': identity,
                        'location': location,
                        'phone': phone,
                        'houseType': houseType,
                        'houseCondition': houseCondition,
                        'sex': sex})
# def name():
#     print('7777')


def name(self):
    return self.find('div', class_='avatarRight').i.text.split('i')[0]


def houseCondition(self):
    houseCondition = ''
    atrrCnt = 0
    while atrrCnt < len(self):
        if self[atrrCnt].text.split(' :  ')[0] == '現況':
            houseCondition = self[atrrCnt].text.split(' :  ')[1]
            break
        atrrCnt += 1
    return houseCondition


def houseType(self):
    houseType = ''
    atrrCnt = 0
    while atrrCnt < len(self):
        if self[atrrCnt].text.split(' :  ')[0] == '型態':
            houseType = self[atrrCnt].text.split(' :  ')[1]
            break
        atrrCnt += 1
    return houseType


def phone(self):
    return self.find('span', class_='dialPhoneNum')['data-value']


def identity(self):
    identity = self.find('div', class_='avatarRight').div.text
    if '屋主' in identity:
        identity = '屋主'
    elif '代理人' in identity:
        identity = '代理人'
    elif '仲介' in identity:
        identity = '仲介'

    return identity


def sex(self):
    sex = '男女生皆可'
    length = len(self)
    sexCnt = 4
    while sexCnt < length:
        if self[sexCnt].find('div', class_='one').text == '性別要求':
            sex = self[sexCnt].em.text
        sexCnt += 1
    return sex
