from spiders.price_based_spider import PriceSpider
from spiders.util import get_old
from os.path import join as pjoin
from bs4 import BeautifulSoup
import os
import pprint

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
old_files = get_old()
print(old_files)
pp = pprint.PrettyPrinter(indent=4)
for html_name in html_names:
    if html_name in old_files:
        continue
    file_path = pjoin(site_dir, html_name)
    n += 1
    if n != n:
        continue
    file_path = pjoin(site_dir, html_name)
    with open (file_path) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    spider = PriceSpider()
    table = spider.webhostingtalk(soup, file_path.split('vps_scrapy_html/')[-1])
    if len(table) == 0:
        empty.append(n)
    else:
        pp.pprint(table)
    print(file_path)
    print(f'File {n}', '='*80)
    old_files.append(html_name)
print(empty)
print(len(empty))
with open('./old_files.txt', 'w') as f:
    for of in old_files:
        print(of, file=f)
