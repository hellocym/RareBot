import datetime
import os.path
import re
import time
import pandas
import pandas as pd

from bs4 import BeautifulSoup
from urllib.request import urlopen
from threading import Thread


class HardstyleRelease:
    def __init__(self):
        self.release_url = 'https://releasehardstyle.nl/releases/'
        self.root_url = 'https://releasehardstyle.nl'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
        self.init_csv()
        self.get_releases()

    def get_releases(self):
        html = urlopen(self.release_url)
        soup = BeautifulSoup(html.read(), 'html.parser')
        releases = soup.find_all('a', class_='releasetracker-list-entry-info-more-details')
        # 多线程获取专辑信息
        thread_list = []
        for release in releases[:]:
            # print(release['href'])
            url = self.root_url + release['href']
            thread = Thread(target=self.get_release_info, args=(url,))
            thread.start()
            time.sleep(0.1)
            thread_list.append(thread)

        for t in thread_list:
            t.join()

        # csv去重
        csv = pd.read_csv('release.csv')
        df = pd.DataFrame(csv)
        f = df.drop_duplicates()
        f.to_csv('release.csv', index=None)

    def get_release_info(self, url):
        try:
            html = urlopen(url)
        except Exception as e:
            print(f"Can't open {url}")
        soup = BeautifulSoup(html.read(), 'html.parser')
        release_info = soup.find('div', class_='releasetracker_details-info_container-inner')
        # 正则提取信息
        release_info_text = release_info.text
        keys = ['Title', 'Label', 'Release date', 'Catalog ID']
        values = []
        for key in keys:
            finder = re.compile(f'{key}: (.+?) \n')
            value = finder.findall(str(release_info_text))
            values.append(value[0])
        zipped = zip(keys, values)
        info_dict = dict(zipped)
        #info_dict['Release date'] = self.parse_date(info_dict['Release date'])
        self.csv_append(info_dict)

    def init_csv(self):
        if os.path.exists('release.csv'):
            return
        with open('release.csv', 'w', encoding='utf-8') as f:
            f.write('Title,Label,Release date,Catalog ID\n')
    def csv_append(self, info_dict):
        df = pandas.DataFrame(info_dict, index=[0])
        df.to_csv('release.csv', mode='a', header=False, index=False, encoding='utf-8')

    # def parse_date(self, date):
    #     # date = '10 Aug 1919'
    #     return datetime.datetime.strptime(date, '%d %b %Y').strftime('%Y-%m-%d')

    def query_releases(self, Type='date', timestamp=None, period=None):
        if Type == 'period':
            pass
        elif Type == 'timestamp':
            df = pd.read_csv('release.csv', parse_dates=['Release date'])
            timestamp = pd.Timestamp(timestamp)
            mask = (df['Release date'] == timestamp)
            print(df[mask])

    def get_releases_today(self):
        today = datetime.datetime.now().date()
        self.query_releases(Type='timestamp', timestamp=today)


if __name__ == '__main__':
    r = HardstyleRelease()
    r.get_releases_today()
