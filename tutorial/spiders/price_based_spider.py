import scrapy
import os
from bs4 import BeautifulSoup
from os.path import join as pjoin
import re
import nltk
import urllib.request
from . import util as u


class PriceSpider(scrapy.Spider):
    name = "price"
    output_dir = '/media/hdd_ext4/vps_scrapy_htmls'

    def start_requests(self):
        def gen_req(url):
            req = urllib.request.Request(
                url,
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh;'
                    ' Intel Mac OS X 10_9_3)'
                    ' AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/35.0.1916.47 Safari/537.36'
                }
            )
            return req

        forum = 'http://www.webhostingtalk.com/forumdisplay.php?f=104'
        req = gen_req(forum)
        r = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(r, "html.parser")
        prefix = 'http://www.webhostingtalk.com/'
        titles = soup.findAll('a', {'class': 'title'})
        urls = []
        for title in titles:
            print(prefix+title['href'])
            urls.append(prefix+title['href'])
        urls = urls[7: 12]  # drop ads

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
        with open(html_file, 'w') as f:
            print(soup.prettify(), file=f)
        return

        self.dispatch(site, soup, response.url)

    def dispatch(self, site: str, soup: BeautifulSoup, link):
        dispatch_dict = {
                'www.webhostingtalk.com': self.webhostingtalk
                }
        dispatch_dict[site](soup, link)

    def webhostingtalk(self, soup: BeautifulSoup, link:str):
        content = soup.find('blockquote')
        plain = content.text
        plain = " ".join(plain.split())
        return self.extract_info(plain)

    def clean_state_table(self):
        return {
                'RAM': 0,
                'Traffic': 0,
                'Disk': 0,
                'Price': 0,
                }


    def to_table(self, st: nltk.tree.Tree):
        tables = []
        table = {}
        state_table = self.clean_state_table()
        def try_add(found, k, v):
            if found:
                table[k] = v
                state_table[k] = 1

        for sst in st:
            if not isinstance(sst, nltk.tree.Tree):
                continue
            # print(sst)
            found = False
            if sst.label() == 'Conf':
                for prop in u.prop_dict:
                    found, k, v = u.get_property(prop, u.prop_dict[prop], sst)
                    # print(found, k, v)
                    try_add(found, k, v)
            elif sst.label() == 'Price':
                found, k, v = u.get_price(sst)
                try_add(found, k, v)

            if sum(state_table.values()) == 4:
                # print(table)
                tables.append(table)
                table = self.clean_state_table()
                state_table = self.clean_state_table()

        return tables

    def extract_info(self, post: str):
        rates = {'$': 1, '€': 1.17, '£': 1.31}
        sentences = nltk.sent_tokenize(post)
        sentences = [nltk.tokenize.regexp_tokenize(sent,
            pattern='\d+\.\d+|\d+|\w+|\$|\S+')
            for sent in sentences]
        non_terms = ['Conf', 'Price']

        def has_item(st):
            has_price = False
            has_conf = False
            for sst in st:
                if not isinstance(sst, nltk.tree.Tree):
                    continue
                if sst.label() == 'Conf':
                    has_conf = True
                if sst.label() == 'Price':
                    has_price = True
            return has_conf and has_price

        conf_list = []
        for sent in sentences:
            tagged = nltk.pos_tag(sent)
            grammar = r'''
            Money:
            {<\$|\€|\£><CD>}
            {<CD><\$|\€|\£>}

            Price:  {<Money><JJ>}
            Price:  {<NN|NNP><\:><Money><NN>}
            Price:  {<Money><IN>?<NN>}
            Price:  {<IN><RB>?<Money>}
            Price:  {<Money><NNP><NN>?}

            Conf: {(<NNP>+|<NN>)<:><CD>}
            Conf: {<NNP>+<\(>.*<\)>}
            Conf: {<NNP>+<\(><CD><NNP><\)>}
            Conf: {<NNP>+<\(><CD><NNP><NNP><CD><\)>}
            Conf: {<NNP>+<\(><CD><NN><\)>}
            Conf: {<NNP>+<\(><CD><NNS><\)>}
            Conf: {<CD><NNP>+}
            Conf: {<CD><NN|NNS>}
            '''

            cp = nltk.RegexpParser(grammar)
            result = cp.parse(tagged)
            for st in result.subtrees():
                if has_item(st):
                    # print(st)
                    tables = self.to_table(st)
                    conf_list += tables
        return conf_list
