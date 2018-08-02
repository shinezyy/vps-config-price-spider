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

    def extract_info(self, post: str):
        rates = {'$': 1, '€': 1.17, '£': 1.31}
        sentences = nltk.sent_tokenize(post)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        for sent in sentences:
            tagged = nltk.pos_tag(sent)
            grammar = r'''
            Conf:   {(<NNP>+|<NN>)<:><CD>}
            Price: {<IN><RB>?<CD><\$|\€|\£>}
            '''
            cp = nltk.RegexpParser(grammar)
            result = cp.parse(tagged)
            print(result)
