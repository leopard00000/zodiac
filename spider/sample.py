import urllib.parse

import requests
import bs4
import jieba.posseg as pseg
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

wikipedia = 'https://zh.wikipedia.org/wiki/Wikipedia:首页'
baidu = 'https://www.baidu.com/'
baike = 'https://baike.baidu.com/'
messi = 'https://baike.baidu.com/item/%E9%87%8C%E5%A5%A5%C2%B7%E6%A2%85%E8%A5%BF/4443471'

constellations = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']


class NameLink:
    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.constellations = ''


class Crawler:

    def __init__(self):
        self.result_link_list = list()
        self.name_link_list = list()
        self.history_link = list()

    def crawl(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        # resp = requests.get(wikipedia)
        self.name_link_list.append(NameLink('梅西', messi))

        while len(self.result_link_list) < 10:

            cur_name = self.name_link_list.pop()
            resp = requests.get(cur_name.url, headers=headers)
            resp.encoding = 'utf-8'
            html = resp.text
            soup = bs4.BeautifulSoup(html, 'html.parser')
            # self.handle_target_info(cur_name, soup)

            # crawl others
            for link in soup.find_all('a'):
                if not cur_name.constellations:
                    if link.string in constellations:
                        cur_name.constellations = link.string
                        logger.info(f'抓取到星座 {cur_name.name}:{cur_name.constellations}')
                        self.result_link_list.append(cur_name)
                        continue

                if self.is_interested_link(link):
                    url = urllib.parse.urljoin(baike, link.get('href'))
                    name_link = NameLink(link.text, url)
                    self.name_link_list.append(name_link)

            self.history_link.append(cur_name)
            logger.debug(f'已处理页面 {cur_name.name}:{cur_name.url}')

        with open('./result.txt', 'w+') as f:
            data = dict()
            for c in constellations:
                data.update({c: 0})
            for ret in self.result_link_list:
                for c in constellations:
                    if ret.constellations == c:
                        data[c] += 1
                f.write(f'{ret.name}:{ret.constellations}\n')

            summary = ''
            for c in constellations:
                summary += c + ':' + str(data[c] / len(self.result_link_list))
            f.write(f'{summary}\n')

    def is_interested_link(self, link):
        return self.is_name(link.string) and link.get('href').startswith('/item') and link.string not in [n.name for n
                                                                                                          in
                                                                                                          self.result_link_list] and link.string not in [
                   n.name for n in self.history_link]

    @staticmethod
    def is_name(text):
        if not text:
            return False
        word_list = pseg.lcut(text)
        for eve_word, cixing in word_list:
            if cixing == 'nr':
                return True
        return False

    def handle_target_info(self, curname, soup):
        curname.constellations = self.get_constellations(soup)

    @staticmethod
    def get_constellations(soup):
        for item in soup.find_all('dd', class_='basicInfo-item value'):
            # print(item.string)
            if item.string in constellations:
                return item.string

            if item.childern:
                for cd in item.childern:
                    # print(cd.string)
                    if cd.string in constellations:
                        return cd.string
        return ''


def test_is_name():
    print(Crawler.is_name('梅西'))


if __name__ == '__main__':
    Crawler().crawl()
    # test_is_name()
