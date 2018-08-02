from spiders.price_based_spider import PriceSpider
from os.path import join as pjoin
from bs4 import BeautifulSoup
import os

# import socks
# import socket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
# socket.socket = socks.socksocket
# import nltk
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')

site_dir = '/media/hdd_ext4/vps_scrapy_htmls/www.webhostingtalk.com'

soup = None

html_names = os.listdir(site_dir)
n = 0
for html_name in html_names:
    n += 1
    with open (pjoin(site_dir, html_name)) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    spider = PriceSpider()
    spider.webhostingtalk(soup)
    print(f'File {n}', '='*80)

