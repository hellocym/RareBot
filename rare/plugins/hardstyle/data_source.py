import datetime
import os.path
import re
import time
import pandas
import pandas as pd
import asyncio
import aiohttp

import nest_asyncio

nest_asyncio.apply()

from bs4 import BeautifulSoup
from urllib.request import urlopen
from threading import Thread


class HardstyleRelease:
    def __init__(self):
        self.release_url = 'https://releasehardstyle.nl/releases/'
        self.root_url = 'https://releasehardstyle.nl'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
        self.init_csv()
        # self.get_releases()

    def refresh(self):
        self.get_releases()

    async def url_get(self, url):
        try:
            session = aiohttp.ClientSession()
            response = await session.get(url, headers=self.headers)
            while response.status == 429:
                print(
                    f"Too many requests, waiting for 1 seconds"
                )
                await asyncio.sleep(1)
                response = await session.get(url, headers=self.headers)
            result = await response.text()
            await session.close()
            return result
        except Exception as e:
            print(e)
            return None

    async def get_releases(self):
        html = await self.url_get(self.release_url)
        if not html:
            print(f"Can't open {self.release_url}")
            return
        soup = BeautifulSoup(html, 'html.parser')
        releases = soup.find_all('a', class_='releasetracker-list-entry-info-more-details')
        urls = [self.root_url + release['href'] for release in releases] # [:1]
        # 异步获取专辑信息
        tasks = [asyncio.ensure_future(self.get_release_info(url)) for url in urls]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        # loop.close()
        # for release in releases[:]:
        #     # print(release['href'])
        #     url = self.root_url + release['href']
        #     thread = Thread(target=self.get_release_info, args=(url,))
        #     thread.start()
        #     # sleep 0.1s
        #     await asyncio.sleep(0.1)
        #     thread_list.append(thread)

        # for t in thread_list:
        #     t.join()

        # csv去重
        csv = pd.read_csv('release.csv')
        df = pd.DataFrame(csv)
        f = df.drop_duplicates()
        f.to_csv('release.csv', index=None)

    async def get_release_info(self, url):
        try:
            html = await self.url_get(url)
            # await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Can't open {url}")
        #print(html)
        soup = BeautifulSoup(html, 'html.parser')
        release_info = soup.find('div', class_='releasetracker_details-info_container-inner')
        # 正则提取信息
        # print(release_info)
        try:
            release_info_text = release_info.text
        except Exception as e:
            print(html)
        keys = ['Title', 'Label', 'Release date', 'Catalog ID']
        values = []
        for key in keys:
            finder = re.compile(f'{key}: (.+?) \n')
            value = finder.findall(str(release_info_text))
            values.append(value[0])
        zipped = zip(keys, values)
        info_dict = dict(zipped)
        #info_dict['Release date'] = self.parse_date(info_dict['Release date'])
        await self.csv_append(info_dict)

    def init_csv(self):
        if os.path.exists('release.csv'):
            return
        with open('release.csv', 'w', encoding='utf-8') as f:
            f.write('Title,Label,Release date,Catalog ID\n')

    async def csv_append(self, info_dict):
        df = pandas.DataFrame(info_dict, index=[0])
        df.to_csv('release.csv', mode='a', header=False, index=False, encoding='utf-8')

    # def parse_date(self, date):
    #     # date = '10 Aug 1919'
    #     return datetime.datetime.strptime(date, '%d %b %Y').strftime('%Y-%m-%d')

    def query_releases(self, Type='date', timestamp=None, period: list=None):
        df = pd.read_csv('release.csv', parse_dates=['Release date'])
        if Type == 'period':
            start = pd.Timestamp(period[0])
            end = pd.Timestamp(period[1])
            # print(start, end)
            mask = (df['Release date'] >= start) & (df['Release date'] <= end)
            return df[mask]
        elif Type == 'timestamp':
            timestamp = pd.Timestamp(timestamp)
            mask = (df['Release date'] == timestamp)
            return df[mask]

    def get_releases_today(self):
        today = datetime.datetime.now().date()
        res = self.query_releases(Type='timestamp', timestamp=today)
        return res

    def get_releases_tomorrow(self):
        tomorrow = datetime.datetime.now().date() + datetime.timedelta(days=1)
        res = self.query_releases(Type='timestamp', timestamp=tomorrow)
        return res

    def get_releases_next_week(self):
        today = datetime.datetime.now().date()
        next_week = today + datetime.timedelta(days=7)
        res = self.query_releases(Type='period', period=[today, next_week])
        return res
