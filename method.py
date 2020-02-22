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

    # timeout = aiohttp.ClientTimeout(total=70, connect=3)
    async with aiohttp.ClientSession(cookies=cookie, headers={"Connection": "close"}) as session:
        for pageNum in range(1, pageNums, 10):
            tasks = []
            diff = 10
            if pageNums - pageNum < 10:
                diff = pageNums - pageNum
            for num in range(pageNum, pageNum + diff):
                task = asyncio.ensure_future(findAllPage(
                    num, session, location))
                tasks.append(task)
            _ = await asyncio.gather(*tasks, return_exceptions=True)
            # pageNum+=10
        # _ = await asyncio.wait(tasks)
    print('aaaa')
    # loop = asyncio.get_event_loop()
    # tasks = asyncio.ensure_future(
    # loop.run_until_complete(tasks)
    # loop.close()
    # await asyncio.gather(*coros)


async def findAllPage(pageNum, session, location):
    url = ('https://rent.591.com.tw/?kind=0&region=1&firstRow=' + str(pageNum * 30))
    async with session.get(url) as response:
        homePage = await response.read()
        homeSoup = BeautifulSoup(homePage.decode('utf-8'), 'lxml')
        print(pageNum)
        houseTitles = homeSoup.find('div', id='content').find_all(
            'ul', class_='listInfo clearfix')
        await findOnePage(houseTitles, location)


async def findOnePage(houseTitles, location):
    tasks = []
    timeout = aiohttp.ClientTimeout(total=100, connect=2)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for houseTitle in houseTitles:
            url = 'https:' + houseTitle.find('a', target='_blank')['href']
            task = asyncio.ensure_future(fetch(
                session, url, location))
            tasks.append(task)

        _ = await asyncio.gather(*tasks, return_exceptions=True)


async def fetch(session, url, location):
    async with session.get(url) as response:
        await onePageData(await response.text(), location)


async def onePageData(source: str, location: str):
    # print('kkkkk')
    soup = BeautifulSoup(source, 'lxml')
    detailBox = soup.find('div', class_='detailBox clearfix')

    userInfo = detailBox.find('div', class_='userInfo')
    attrContent = detailBox.find('ul', class_='attr').find_all('li')
    landlordProvide = detailBox.find(
        'ul', class_='clearfix labelList labelList-1').find_all('li')

    await insertDB(userInfo.name(), userInfo.identity(), location, userInfo.phone(), attrContent.houseType(), attrContent.houseCondition(), landlordProvide.sex())
