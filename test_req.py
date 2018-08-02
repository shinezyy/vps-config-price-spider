from bs4 import BeautifulSoup


with open('./forum.html') as f:
    x = f.read()
soup = BeautifulSoup(x, 'html.parser')
prefix = 'http://www.webhostingtalk.com/'
titles = soup.findAll('a', {'class': 'title'})
urls = []
for title in titles:
    print(title)
    print(prefix+title['href'])
    urls.append(prefix+title['href'])


