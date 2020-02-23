from bs4 import BeautifulSoup
import pymongo
import asyncio
import aiohttp
import requests
import model
import env

"""
There were request limit.
so we need to divide task into smaller tasks
task = all pages
smaller tasks = some bunch of pages
can adjust env.buncCnt to meet request limit
"""


async def findAll(cookie, city):
    cnt = env.bunchCnt
    pageNums = totalPageNum(cookie)
    pageBunchs = pageNums // cnt  # how many tasks in this task
    remainPages = pageNums % cnt

    for pageBunch in range(pageBunchs):
        currPage = pageBunch * cnt
        await findBunch(currPage, cnt, cookie, city)
        if pageBunch == pageBunchs:
            await findBunch(currPage, remainPages, cookie, city)

"""
Find url on bunch pages
"""


async def findBunch(currPage, bunchCnt, cookie, city):
    tasks = []
    async with aiohttp.ClientSession(cookies=cookie, headers={"Connection": "close"}) as session:
        for pageNum in range(currPage, currPage + bunchCnt):
            task = asyncio.ensure_future(bunchFetch(
                pageNum, session, city))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)

"""
Parse url on bunch pages and access the data
"""


async def bunchFetch(pageNum, session, city):
    """
    591 hide the real variable to change page,
    add (firstRow + str(pageNum*30)) in url will access the true page
    """

    url = ('https://rent.591.com.tw/?kind=0&region=1&firstRow=' + str(pageNum * 30))
    async with session.get(url) as response:
        page = await response.read()
        urlList = BeautifulSoup(page.decode(
            'utf-8'), 'lxml').find('div', id='content').find_all('ul', class_='listInfo clearfix')
        await findOne(urlList, city)

"""
Find url on each page
"""


async def findOne(urlList, city):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for urlItem in urlList:
            url = 'https:' + urlItem.find('a', target='_blank')['href']
            # model.insertUrl(url)
            await fetch(session, url, city)

"""
Parse url and access the data
"""


async def fetch(session, url, city):
    async with session.get(url) as response:
        houseData(await response.text(), url, city)

"""
Parse data and insert db
"""


def houseData(source, url, city):
    detailBox = BeautifulSoup(source, 'lxml').find(
        'div', class_='detailBox clearfix')
    userInfo = detailBox.find('div', class_='userInfo')
    attrContent = detailBox.find('ul', class_='attr').find_all('li')
    landlordProvide = detailBox.find(
        'ul', class_='clearfix labelList labelList-1').find_all('li')
    model.insertDB(model.name(userInfo), model.identity(userInfo), city, url, model.phone(userInfo),
                   model.attr(attrContent, '型態'), model.attr(attrContent, '現況'), model.sex(landlordProvide))


"""
Need specific cookie to access specific city pages
"""


def finalCookie(cityIndex, resp):
    cookie = resp.cookies.get_dict()
    cookie['urlJumpIp'] = cityIndex
    finalCookie = requests.cookies.merge_cookies(
        requests.cookies.RequestsCookieJar(), cookie)
    return finalCookie


"""
city index:
combine with cookie to access specific city pages
Taipei = 0
New Taipei = 3,
Keelung = 5, etc...
"""


def city(cityIndex):
    city = '台北市'
    if cityIndex == '3':
        city = '新北市'
    return city


"""
Total page number of each city
"""


def totalPageNum(cookie):
    resp = requests.get(
        'https://rent.591.com.tw/?kind=0&region=1', cookies=cookie)
    return int(BeautifulSoup(resp.text, 'lxml').find_all('a', class_='pageNum-form')[-1].text)
