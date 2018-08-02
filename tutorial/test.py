from spiders.price_based_spider import PriceSpider
from os.path import join as pjoin
from bs4 import BeautifulSoup

# import socks
# import socket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
# socket.socket = socks.socksocket
# import nltk
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')

site_dir = '/media/hdd_ext4/vps_scrapy_htmls/www.webhostingtalk.com'

soup = None
with open (pjoin(site_dir, 'showthread.php?t=1723436')) as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

spider = PriceSpider()
spider.webhostingtalk(soup)

