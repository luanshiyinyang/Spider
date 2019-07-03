import requests
import re
from bs4 import BeautifulSoup
from contextlib import closing


target_url = "http://www.bizhiku.net"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': 'http://www.xicidaili.com/nn/',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
               }


def geturllist():

    rsp = requests.get(url=target_url, headers=headers)
    bs = BeautifulSoup(rsp.text, "lxml")
    a_list = bs.find_all('a', attrs={'target': '_blank', 'href': re.compile(r'^/wallpaper/\d+'), 'class': 'pic'})
    url_list = []
    for item in a_list:
        url_list.append(target_url+item["href"])
    return url_list


def parseurl(list):
    number = 0
    for item in list:
        rst = requests.get(item, headers=headers)
        bs = BeautifulSoup(rst.text, "lxml")
        bigurl = bs.find("img", attrs={"id": "bigimg"})
        img_url = target_url + bigurl['src']
        with closing(requests.get(url=img_url, stream=True, verify=False, headers=headers)) as r:
            with open("{}.jpg".format(number), 'ab+') as f:
                print("正在获得第{}个图片".format(number))
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        number += 1
        import time
        time.sleep(1)


if __name__ == '__main__':
    l = geturllist()
    parseurl(l)