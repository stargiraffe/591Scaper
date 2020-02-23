import unittest
import method
import requests
from bs4 import BeautifulSoup


class Test_test1(unittest.TestCase):
    url = 'https://rent.591.com.tw/?kind=0&region=1'
    diffUrl = 'https://rent.591.com.tw/?kind=0&region=5&firstRow=300'
    resp = requests.get(url)
    diffResp = requests.get(diffUrl)
    cookie = method.finalCookie('3', resp)
    diffCookie = method.finalCookie('3', diffResp)

    def test_city(self):
        expected = '新北市'
        result = method.city('3')
        self.assertEqual(expected, result)

    def test_totalPageNum(self):
        testResp = requests.get(self.diffUrl, cookies=self.diffCookie)
        expected = int(BeautifulSoup(testResp.text, 'lxml').find_all(
            'a', class_='pageNum-form')[-1].text)
        result = method.totalPageNum(self.cookie)
        self.assertEqual(expected, result)

    def test_finalCookie(self):
        expected = '3'
        result = self.cookie.get_dict()['urlJumpIp']
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
