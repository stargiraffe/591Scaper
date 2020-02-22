from bs4 import BeautifulSoup
import requests
import pymongo
from requests import Response
import asyncio
import time
import aiohttp
import model
from model import insertDB
import method
import env


async def main():
    ticks1 = time.time()
    homePageResponse = requests.get(
        'https://rent.591.com.tw/?kind=0&region=1')
    for cityIndex in env.cityIndexBox:
        cookie = method.finalCookie(cityIndex, homePageResponse)
        await method.findAllPage(cookie, method.city(cityIndex))
    ticks2 = time.time()
    print((ticks2 - ticks1) / 60)


if __name__ == "__main__":
    asyncio.run(main())
