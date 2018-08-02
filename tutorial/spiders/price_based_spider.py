import scrapy
import os
from bs4 import BeautifulSoup
from os.path import join as pjoin
import re
import nltk


class PriceSpider(scrapy.Spider):
    name = "price"
    output_dir = '/media/hdd_ext4/vps_scrapy_htmls'


    def start_requests(self):
        urls = [
                'http://www.webhostingtalk.com/showthread.php?t=1723436',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        site, thread = response.url.split("/")[-2:]
        site_dir = pjoin(self.output_dir, site)
        html_file = pjoin(site_dir, thread)

        if not os.path.isdir(site_dir):
            os.makedirs(site_dir)

        soup = BeautifulSoup(response.body,
                'html.parser')

        dispatch(site, soup)

    def dispatch(self, site: str, soup: BeautifulSoup):
        dispatch_dict = {
                'webhostingtalk': self.webhostingtalk
                }
        dispatch_dict[site](soup)

    def webhostingtalk(self, soup: BeautifulSoup):
        content = soup.find('blockquote')
        plain = content.text
        plain = " ".join(plain.split())
        self.extract_info(plain)

    def is_like_conf(self, post: str):
        key_words = ['disk', 'ssd', 'ram', 'gb', 'mb', 'ip', 'cpu']
        post = post.lower()

        count = 0
        for key_word in key_words:
            if key_word in post:
                count += 1

        return count > 3

    def is_conf_before_price(self, post: str):
        signs = ['$', '€', '£']
        sign = None
        for s in signs:
            if s in post:
                sign = s
        segments = post.split(sign)
        return sign, self.is_like_conf(segments[0])

    def text_to_table(self, conf: str, cbp: bool):
        conf_length = 120
        tagged = nltk.pos_tag(conf.split())
        grammar = r"NP: {(<NNP>+|<NN>)<:><CD>}"
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(tagged)
        print(result)
        return None

    def extract_info(self, post: str):
        rates = {'$': 1, '€': 1.17, '£': 1.31}
        sign, cbp = self.is_conf_before_price(post)
        print(post)
        segments = post.split(sign)
        if cbp:
            segments = segments[:-1]
        else:
            segments = segments[1:]

        tables = []
        for text in segments:
            tables.append(self.text_to_table(text, cbp))
        print(tables)

