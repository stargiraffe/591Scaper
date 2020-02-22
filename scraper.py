from bs4 import BeautifulSoup
import requests
import pymongo
from requests import Response
import asyncio
import time
import aiohttp
import model
from model import insertDB

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client.db591
urlSet = set()


async def main():
    ticks1 = time.time()
    homePageResponse = requests.get(
        'https://rent.591.com.tw/?kind=0&region=1')
    # coros = [cityData(setCookieWithLocationIndex(
    #     '3', homePageResponse)), cityData(setCookieWithLocationIndex('0', homePageResponse))]
    # await asyncio.gather(*coros)
    await cityData(setCookieWithLocationIndex('3', homePageResponse))
    await cityData(setCookieWithLocationIndex('0', homePageResponse))

    ticks2 = time.time()
    print((ticks2 - ticks1) / 60)


def setCookieWithLocationIndex(locationIndex: chr, homePageResponse: Response):

    coo = homePageResponse.cookies.get_dict()
    coo['urlJumpIp'] = locationIndex
    cookie = requests.cookies.merge_cookies(
        requests.cookies.RequestsCookieJar(), coo)

    location = ''
    if locationIndex == '0':
        location = '台北市'
    elif locationIndex == '3':
        location = '新北市'
    return (cookie, location)


async def cityData(cookieAndlocation: tuple):
    cookie = cookieAndlocation[0]
    location = cookieAndlocation[1]

    homePageResponse = requests.get(
        'https://rent.591.com.tw/?kind=0&region=1', cookies=cookie)
    homePage = homePageResponse.text
    homeSoup = BeautifulSoup(homePage, 'lxml')
    houseTitles = homeSoup.find('div', id='content').find_all(
        'ul', class_='listInfo clearfix')
    await findOnePage(houseTitles, location)
    pageNums = int(homeSoup.find_all('a', class_='pageNum-form')[-1].text)

    pageNum = 1
    tasks = []
    # timeout = aiohttp.ClientTimeout(total=70, connect=3)
    async with aiohttp.ClientSession(cookies=cookie, headers={"Connection": "close"}) as session:
        # for pageNum in range(1, pageNums):
        for pageNum in range(1, 10):
            # tasks = []
            # diff = 3
            # if 30 - pageNum < 3:
            #     diff = pageNums - pageNum
            # for num in range(pageNum, pageNum + diff):
            task = asyncio.ensure_future(findAllPage(
                pageNum, session, location))
            tasks.append(task)
        print('ccccc')
        _ = await asyncio.gather(*tasks, return_exceptions=True)
        print('bbbb')
        # pageNum+=10
        # _ = await asyncio.wait(tasks)
    # loop = asyncio.get_event_loop()
    # tasks = asyncio.ensure_future(
    # loop.run_until_complete(tasks)
    # loop.close()
    # await asyncio.gather(*coros)


async def findAllPage(pageNum, session, location):
    url = ('https://rent.591.com.tw/?kind=0&region=1&firstRow=' + str(pageNum * 30))
    # print(url)
    async with session.get(url) as response:
        homePage = await response.read()
        homeSoup = BeautifulSoup(homePage.decode('utf-8'), 'lxml')
        print(pageNum)
        houseTitles = homeSoup.find('div', id='content').find_all(
            'ul', class_='listInfo clearfix')
        await findOnePage(houseTitles, location)


async def findOnePage(houseTitles, location):
    tasks = []
    # timeout = aiohttp.ClientTimeout(total=100, connect=2)
    async with aiohttp.ClientSession() as session:
        for houseTitle in houseTitles:
            url = 'https:' + houseTitle.find('a', target='_blank')['href']
            urlSet.add(url)
            # task = asyncio.ensure_future(insertUrl(
            # url))

            # tasks.append(task)

        # _ = await asyncio.gather(*tasks, return_exceptions=True)
            await fetch(session, url, location)

# async def findOnePage(houseTitles, location):
#     tasks = []
#     timeout = aiohttp.ClientTimeout(total=100, connect=2)
#     response.get()
#         for houseTitle in houseTitles:
#             url = 'https:' + houseTitle.find('a', target='_blank')['href']
#             urlSet.add(url)
#             task = asyncio.ensure_future(insertUrl(
#                 url))
#             # task = asyncio.ensure_future(fetch(
#             #     session, url, location))
#             tasks.append(task)

#         _ = await asyncio.gather(*tasks, return_exceptions=True)


async def fetch(session, url, location):
    async with session.get(url) as response:
        onePageData(await response.text(), location)


def onePageData(source: str, location: str):
    # print('kkkkk')
    soup = BeautifulSoup(source, 'lxml')
    detailBox = soup.find('div', class_='detailBox clearfix')

    userInfo = detailBox.find('div', class_='userInfo')

    attrContent = detailBox.find('ul', class_='attr').find_all('li')
    landlordProvide = detailBox.find(
        'ul', class_='clearfix labelList labelList-1').find_all('li')

    insertDB(model.name(userInfo), model.identity(userInfo), location, model.phone(userInfo),
             model.houseType(attrContent), model.houseCondition(attrContent), model.sex(landlordProvide))


async def insertUrl(url):
    db.coll.insert_one({'url': url})

    # print(sex, location, houseCondition, houseType, phone, identity, name)
    # print('ccc')


if __name__ == "__main__":
    asyncio.run(main())
    # main()
