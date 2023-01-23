import re
import time

from bs4 import BeautifulSoup
from urllib.request import urlopen
from threading import Thread


class HardstyleRelease:
    def __init__(self):
        self.release_url = 'https://releasehardstyle.nl/releases/'
        self.root_url = 'https://releasehardstyle.nl'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

    def __str__(self):
        releases = self.get_releases()
        for i, release in enumerate(releases):
            print(f'{i} : {release}')
        return ''

    def get_releases(self):
        html = urlopen(self.release_url)
        soup = BeautifulSoup(html.read(), 'html.parser')
        releases = soup.find_all('a', class_='releasetracker-list-entry-info-more-details')
        # 多线程获取专辑信息
        thread_list = []
        for release in releases[0:1]:
            # print(release['href'])
            url = self.root_url + release['href']
            thread = Thread(target=self.get_release_info, args=(url,))
            thread.start()
            time.sleep(0.1)
            thread_list.append(thread)

        for t in thread_list:
            t.join()
        #return releases

    def get_release_info(self, url):
        html = urlopen(url)
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
        print(info_dict)


if __name__ == '__main__':
    r = HardstyleRelease()
    r.get_releases()
