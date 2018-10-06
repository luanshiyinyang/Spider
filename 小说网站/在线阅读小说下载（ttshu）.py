#coding:utf-8
from urllib import request
from bs4 import BeautifulSoup
import re
# 处理写入文字内容的js代码中的占位符号
def solve_text(content):
    content = content.replace("document.write('", "")
    content = content.replace("' ;", "")
    content = content.replace(")", " ")
    content = content.replace("</br>", "\n")
    content = content.replace("<br /><br />", "\n")
    content = content.replace("&nbsp;", " ")
    return content


if __name__ == '__main__':
    with open('圣墟.txt', 'a', encoding='utf-8') as f:
        index_url = 'http://www.ttshu.com/html/content/18424482.html'
        start_url = "http://www.ttshu.com"
        # 使用代理服务器访问
        proxy = {'http': '39.137.77.66:8080'}
        proxy_handler = request.ProxyHandler(proxy)
        opener = request.build_opener(proxy_handler)
        request.install_opener(opener)
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
        }
        # 用户代理伪装
        req = request.Request(url=index_url, headers=head)
        rsp = request.urlopen(req)
        # 解码获得的结果
        html = rsp.read().decode('gb2312', 'ignore')
        # 创建bs对象
        soup = BeautifulSoup(html, 'html.parser')
        chapters = soup.find_all("a")
        start_download_flag = False
        number = 0
        # 开始寻找是章节的链接
        for item in chapters:
            # 找到了，从章节的标签开始，访问每个章节的链接
            if start_download_flag is True:

                # 拼接章节链接并访问
                download_url = start_url + item['href']
                download_req = request.Request(url=download_url, headers=head)
                download_rsp = request.urlopen(download_req)
                download_html = download_rsp.read().decode('gb2312', 'ignore')
                download_soup = BeautifulSoup(download_html, 'html.parser')
                # 找到章节名称的标签，并获取文本内容（也就是处理掉标签符号）
                name = download_soup.find('h1').string + "\n"
                f.write(name)
                content_url = start_url+download_soup.find('script', src=re.compile("content2"))['src']
                content_req = request.Request(url=content_url, headers=head)
                content_rsp = request.urlopen(content_url)
                content_html = content_rsp.read().decode("gb2312", 'ignore')
                content = solve_text(content_html)
                f.write(content+"\n")
                number += 1
                print("下载了"+str(number)+"章")
            # 找到章节的a标签
            if item.text == u'向站长举报错误章节':
                start_download_flag = True



