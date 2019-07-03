import requests
from bs4 import BeautifulSoup
import re
import time
try:
    headers = {'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Android:Mozilla/5.0 (Linux; U; Android 2.2) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 ',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://www.xicidaili.com/nn/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
                }
    index_url = "http://m.55dushu.com"
    url = "某小说目录页"
    # 共有110页内容
    for i in range(1, 111):
        start_url = url + str(i) + "/"
        rsp = requests.get(url=start_url, headers=headers)
        rsp.encoding = 'gbk'
        html = rsp.text
        bs_html = BeautifulSoup(html, 'lxml')
        # 正则表达式熟练之后比较快
        chapters_list = bs_html.find_all('a', href=re.compile(r'^/61/61841/\d+'))
        time.sleep(0.1)
        for item in chapters_list:
            content_url = index_url + item['href']
            rsp = requests.get(url=content_url, headers=headers)
            rsp.encoding = 'gbk'
            content_html = rsp.text
            bs_content = BeautifulSoup(content_html, 'lxml')
            content_title = bs_content.find('div', attrs={"id": "nr_title"}).text
            content_text = bs_content.find('div', attrs={"id": "nr1"}).text
            content_text.replace("    ", "\n")
            with open("get.txt", 'a', encoding='utf-8') as f:
                f.write(content_title+"\n")
                f.write(content_text+"\n\n")
            time.sleep(0.1)
except Exception as e:
    print(e)

