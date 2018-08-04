import scrapy
import os
from bs4 import BeautifulSoup
from os.path import join as pjoin
import re
import nltk
import nltk.tag, nltk.data
from nltk.tokenize import RegexpTokenizer
from nltk import RegexpTagger
import urllib.request
from . import util as u
from . import debug
from random import randint
from time import sleep
import html2text


class PriceSpider(scrapy.Spider):
    name = "price"
    output_dir = '/media/hdd_ext4/vps_scrapy_htmls'
    d = debug.DebugLogger()

    def __init__(self):
        self.state_table = self.clean_state_table()
        self.conf_table = {}

    def log(self, *args, **kwargs):
        self.d.log(*args, **kwargs)

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
        with open("./forum.html", 'w') as f:
            print(r, file=f)
        soup = BeautifulSoup(r, "html.parser")
        prefix = 'http://www.webhostingtalk.com/'
        titles = soup.findAll('a', {'class': 'title'})
        urls = []
        for title in titles:
            print(prefix+title['href'])
            urls.append(prefix+title['href'])
        urls = urls[4:]  # drop ads
        print(urls)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse,
                    # meta={'proxy': 'http://127.0.0.1:8081'},
                    )

    def parse(self, response):
        site, thread = response.url.split("/")[-2:]
        site_dir = pjoin(self.output_dir, site)
        html_file = pjoin(site_dir, thread)

        if not os.path.isdir(site_dir):
            os.makedirs(site_dir)

        soup = BeautifulSoup(response.body,
                'html.parser')
        print(response.url)
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
        plain = html2text.html2text(str(content))
        return self.extract_info(plain)

    def clean_state_table(self):
        return {
                'RAM': 0,
                'Traffic': 0,
                'Disk': 0,
                'Price': 0,
                }


    def to_table(self, st: nltk.tree.Tree):
        self.log(self.d.debug_tree, '== Enter to table')
        tables = []
        def try_add(found, k, v):
            if found:
                self.conf_table[k] = v
                self.state_table[k] = 1

        for sst in st:
            self.log(self.d.debug_dollar, "proc: ", sst)
            if not isinstance(sst, nltk.tree.Tree):
                self.log(self.d.debug_tree, "skipped!")
                self.log(self.d.debug_dollar, "skipped!")
                continue
            found = False
            if sst.label() == 'Conf':
                self.log(self.d.debug_dollar, "trav", sst)
                for prop in u.prop_dict:
                    found_t, k, v = u.get_property(prop, u.prop_dict[prop], sst)
                    try_add(found_t, k, v)
                    found |= found_t
            elif sst.label() == 'Price':
                self.log(self.d.debug_dollar, 'trav', sst)
                found_t, k, v = u.get_price(sst)
                try_add(found_t, k, v)
                found |= found_t

            if sum(self.state_table.values()) == 4:
                self.log(self.d.debug_dollar,
                        "## Table generated:", self.conf_table)
                tables.append(self.conf_table)
                self.conf_table = self.clean_state_table()
                self.state_table = self.clean_state_table()
            elif found:
                self.log(self.d.debug_dollar, self.state_table)

        return tables

    def extract_info(self, post: str):
        # $15 -> $ 15
        post = post.replace('_', ' ')
        post = post.replace('$', ' $ ')
        post = post.replace('\x80', ' \x80 ')
        post = post.replace('£', ' £ ')
        rates = {'$': 1, '€': 1.17, '£': 1.31}

        sent_tokenizer = RegexpTokenizer(r'\||,|\.\s|\n', gaps=True)
        sentences = sent_tokenizer.tokenize(post.lower())
        self.log(self.d.debug_dollar, sentences)

        word_tokenizer = RegexpTokenizer(r'\s+', gaps=True)
        sentences = [word_tokenizer.tokenize(sent)
            for sent in sentences]
        self.log(self.d.debug_dollar, sentences)

        spec_tokenizer = RegexpTokenizer(
                r'\$|\x80|£|eur|\d+\.\d+|\d+|\w+', gaps=False)
        new_sents = []
        for sent in sentences:
            new_sent = []
            for words in sent:
                new_sent += spec_tokenizer.tokenize(words)
            new_sents.append(new_sent)
        sentences = new_sents
        self.log(self.d.debug_dollar, sentences)

        non_terms = ['Conf', 'Price']

        conf_list = []
        default_tagger = nltk.data.load(nltk.tag._POS_TAGGER)
        model = {
                'eur': '$',
                '\x80': '$',
                '£': '$',
                'mb': 'Unit',
                'gb': 'Unit',
                'tb': 'Unit',
                'cores': 'Unit',
                'core': 'Unit',
                'hdd': 'HW',
                'ssd': 'HW',
                'storage': 'HW',
                'disk': 'HW',
                'raid10': 'HW',
                'diskspace': 'HW',
                'space': 'HW',
                'ram': 'HW',
                'memory': 'HW',
                'cpu': 'HW',
                'processor': 'HW',
                'bandwidth': 'HW',
                'traffic': 'HW',
                'bw': 'HW',
                'transfer': 'HW',
                'premium': 'HWM',
                'pure': 'HWM',
                'ddr4': 'HWM',
                'dedicated': 'HWM',
                'data': 'HWM',
                'nvme': 'HWM',
                '|': 'Del',
                'month': 'Time',
                '/month': 'Time',
                'monthly': 'Time',
                'mo': 'Time',
                '/mo': 'Time',
                '/m': 'Time',
                'mo)': 'Time',
                '/mo)': 'Time',
                '/m)': 'Time',
                'year': 'Time',
                'quarterly': 'Time',
                'first': 'First',
                '(first': 'First',
                'price': 'Pri',
                'unmetered': 'CD',
                'unlimited': 'CD',
                'gbps': 'Net',
                'gbit': 'Net',
                'mbps': 'Net',
                }
        tagger = nltk.tag.UnigramTagger(model=model, backoff=default_tagger)
        for sent in sentences:
            if not len(sent):
                continue
            self.log(self.d.debug_tag, sent)
            tagged = tagger.tag(sent)
            self.log(self.d.debug_dollar, tagged)
            grammar = r'''
            Num:    {<CD|LS>}

            Money:
            {<\$><Num>}
            {<Num><\$>}

            Conf: {<Num><Unit><HW><HWM>}
            Conf: {<Num><Unit><HWM><HW>}
            Conf: {<Num><Unit><Time><HW>}
            Conf: {<Num><Unit><HW>}
            Conf: {<HW><Num><Unit>}
            Conf: {<HW><:><Num><Unit>}

            Conf: {<Num><HW><HWM>}
            Conf: {<Num><HWM><HW>}
            Conf: {<Num><HW>}
            Conf: {<HW><Num>}
            Conf: {<HW><:><Num>}
            Conf: {<HW><:><Num>}

            Conf: {<Num><Net><Num>}
            Conf: {<Num><Unit><Num><Net>}


            Price:  {<PRP\$><Pri><:>?<Money>}
            Price:  {<Money><Time>}
            Price:  {<Money><First><Time>}
            Price:  {<Money><IN><Time>}
            Price:  {<Time><Money>}
            Price:  {<Money><IN>?<NN>}
            Price:  {<IN><RB>?<Money>}
            Price:  {<Money><NNP><NN>?}

            Price:  {<Money>}
            '''

            cp = nltk.RegexpParser(grammar)
            result = cp.parse(tagged)
            tables = self.to_table(result)
            conf_list += tables
        return conf_list
