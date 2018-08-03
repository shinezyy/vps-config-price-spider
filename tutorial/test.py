from spiders.price_based_spider import PriceSpider
from os.path import join as pjoin
from bs4 import BeautifulSoup
import os

# import socks
# import socket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
# socket.socket = socks.socksocket
# import nltk
# nltk.download()
# 










site_dir = '/media/hdd_ext4/vps_scrapy_htmls/www.webhostingtalk.com'

soup = None

html_names = os.listdir(site_dir)
n = 0
empty = []
old_empty = [3, 6, 8, 10, 11, 12, 13, 17, 19, 20,
        21, 24, 26, 27, 29, 30, 32, 34, 37, 39]
for html_name in html_names:
    n += 1
    if n not in old_empty:
        continue
    file_path = pjoin(site_dir, html_name)
    with open (file_path) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    spider = PriceSpider()
    table = spider.webhostingtalk(soup, file_path.split('vps_scrapy_html/')[-1])
    if len(table) == 0:
        empty.append(n)
    print(file_path)
    print(f'File {n}', '='*80)
    break
print(empty)

