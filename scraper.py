from bs4 import BeautifulSoup
import requests
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client.db591

pageNum = 0
while pageNum >= 0:

  homePage = requests.get(
      'https://rent.591.com.tw/?kind=0&region=1&firstRow=' + str(pageNum * 30)).text
  pageNum += 1
  homeSoup = BeautifulSoup(homePage, 'lxml')

  allHouseTitle = homeSoup.find('div', id='content').find_all(
      'ul', class_='listInfo clearfix')

  for i in range(len(allHouseTitle)):
    houseUrl = 'http:' + \
        allHouseTitle[i].find('a', target='_blank')['href']

    source = requests.get(
        houseUrl).text

    soup = BeautifulSoup(source, 'lxml')

    detailBox = soup.find('div', class_='detailBox clearfix')

    userInfo = detailBox.find('div', class_='userInfo')

    avatarRight = userInfo.find('div', class_='avatarRight')

    name = avatarRight.i.text.split('i')[0]

    identity = avatarRight.div.text

    identityLength = len(avatarRight.div.text)

    if '屋主' in identity:
      identity = '屋主'
    elif '代理人' in identity:
      identity = '代理人'
    elif '仲介' in identity:
      identity = '仲介'

    phone = userInfo.find('span', class_='dialPhoneNum')['data-value']

    attrContent = detailBox.find('ul', class_='attr').find_all('li')

    houseType = ''
    houseCondition = ''
    houseAtrrCnt = 1

    while houseAtrrCnt < len(attrContent):
      # print(attrContent[houseAtrrCnt].text.split(' :  '))
      if attrContent[houseAtrrCnt].text.split(' :  ')[0] == '現況':
        houseCondition = attrContent[houseAtrrCnt].text.split(' :  ')[
            1]
        houseType = attrContent[houseAtrrCnt -
                                1].text.split(' :  ')[1]
        break
      houseAtrrCnt += 1

    landlordProvide = detailBox.find(
        'ul', class_='clearfix labelList labelList-1').find_all('li')

    sex = '男女生皆可'
    landlordProvideLen = len(landlordProvide)
    sexCnt = 4
    # print(landlordProvide[sexCnt].find_all('div', class_='one').text)
    while sexCnt < landlordProvideLen:
      # print(landlordProvide[sexCnt].find('div', class_='one').text)
      if landlordProvide[sexCnt].find('div', class_='one').text == '性別要求':
        sex = landlordProvide[sexCnt].em.text
        if(sexCnt > 7):
          print(
              'faillllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll', name, sexCnt)
        break
      sexCnt += 1
    if(sexCnt < 4):
      print('faillllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll', name, sexCnt)
    print(sex, houseCondition, houseType, phone, identity, name)
    db.coll.insert_one({'name': name,
                        'identity': identity,
                        'phone': phone,
                        'houseType': houseType,
                        'houseCondition': houseCondition,
                        'sex': sex})

# dblist = client.list_database_names()
# col = db.list_collection_names()
