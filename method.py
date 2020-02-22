from bs4 import BeautifulSoup
import pymongo
import asyncio
import aiohttp
import requests
import model
import env


async def findAllPage(cookie, city):
    pageNums = maxPageNum(cookie)
    pageBunchs = pageNums // env.bunchCnt
    pageRemain = pageNums % env.bunchCnt
    for pageBunch in range(pageBunchs):
        currPage = pageBunch * env.bunchCnt
        await findBunchPage(currPage, env.bunchCnt, cookie, city)
        if pageBunch == pageBunchs:
            await findBunchPage(currPage, pageRemain, cookie, city)


async def findBunchPage(pageNums, bunchCnt, cookie, city):
    tasks = []
    async with aiohttp.ClientSession(cookies=cookie, headers={"Connection": "close"}) as session:
        for pageNum in range(pageNums, pageNums + bunchCnt):
            task = asyncio.ensure_future(bunchFetch(
                pageNum, session, city))
            tasks.append(task)
        _ = await asyncio.gather(*tasks, return_exceptions=True)


async def bunchFetch(pageNum, session, city):
    url = ('https://rent.591.com.tw/?kind=0&region=1&firstRow=' + str(pageNum * 30))
    async with session.get(url) as response:
        homePage = await response.read()
        homeSoup = BeautifulSoup(homePage.decode('utf-8'), 'lxml')
        houseTitles = homeSoup.find('div', id='content').find_all(
            'ul', class_='listInfo clearfix')
        await findOnePage(houseTitles, city)


async def findOnePage(houseTitles, city):
    tasks = []
    # timeout = aiohttp.ClientTimeout(total=100, connect=2)
    async with aiohttp.ClientSession() as session:
        for houseTitle in houseTitles:
            url = 'https:' + houseTitle.find('a', target='_blank')['href']
            # urlSet.add(url)
            await fetch(session, url, city)


async def fetch(session, url, city):
    async with session.get(url) as response:
        onePageData(await response.text(), city)


def onePageData(source: str, city: str):
    soup = BeautifulSoup(source, 'lxml')
    detailBox = soup.find('div', class_='detailBox clearfix')
    userInfo = detailBox.find('div', class_='userInfo')
    attrContent = detailBox.find('ul', class_='attr').find_all('li')
    landlordProvide = detailBox.find(
        'ul', class_='clearfix labelList labelList-1').find_all('li')
    model.insertDB(model.name(userInfo), model.identity(userInfo), city, model.phone(userInfo),
                   model.houseType(attrContent), model.houseCondition(attrContent), model.sex(landlordProvide))


def finalCookie(cityIndex, homePageResponse):
    coo = homePageResponse.cookies.get_dict()
    coo['urlJumpIp'] = cityIndex
    cookie = requests.cookies.merge_cookies(
        requests.cookies.RequestsCookieJar(), coo)
    return cookie


def city(cityIndex):
    city = ''
    if cityIndex == '0':
        city = '台北市'
    elif cityIndex == '3':
        city = '新北市'
    return city


def maxPageNum(cookie):
    homePageResponse = requests.get(
        'https://rent.591.com.tw/?kind=0&region=1', cookies=cookie)
    homePage = homePageResponse.text
    homeSoup = BeautifulSoup(homePage, 'lxml')
    houseTitles = homeSoup.find('div', id='content').find_all(
        'ul', class_='listInfo clearfix')
    return int(homeSoup.find_all('a', class_='pageNum-form')[-1].text)
