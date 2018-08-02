import scrapy
import os
from bs4 import BeautifulSoup
from os.path import join as pjoin
import re
import nltk
import urllib.request


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
        urls = urls[4: 7]  # drop ads

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

        self.dispatch(site, soup)

    def dispatch(self, site: str, soup: BeautifulSoup):
        dispatch_dict = {
                'www.webhostingtalk.com': self.webhostingtalk
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

        for sent in sentences:
            tagged = nltk.pos_tag(sent)
            grammar = r'''
            Price:  {<NN><:><\$|\€|\£><CD><NN>}
                    {<IN><RB>?<CD><\$|\€|\£><CD>}
                    {<CD><\$|\€|\£><CD>}
                    {<\$|\€|\£><CD><NNP><NN>}
                    {<\$|\€|\£><CD><NN>}
                    {<\$|\€|\£><CD>}

            Conf:   {(<NNP>+|<NN>)<:><CD>}
                    {<NNP>+<\(>.*<\)>}

                    {<NNP>+<\(><CD><NNP><\)>}
                    {<NNP>+<\(><CD><NNP><NNP><CD><\)>}
                    {<NNP>+<\(><CD><NN><\)>}
                    {<NNP>+<\(><CD><NNS><\)>}

                    {<CD><NNP>+}
                    {<CD><NN|NNS>}
            '''

            '''
            Item:   {<Conf>+.*<Price>}
                    {<Price>.*<Conf>+}
            '''
            cp = nltk.RegexpParser(grammar)
            result = cp.parse(tagged)
            for st in result.subtrees():
                # if st.label() == 'Item':
                if has_item(st):
                    print(st)
