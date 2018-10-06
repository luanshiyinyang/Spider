# import requests
# import re
# from bs4 import BeautifulSoup
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


def parse_html(html):
    '''
    :param html: 传入的response的字符串
    :return: 返回id的列表和评论内容的列表
    '''
    soup = BeautifulSoup(html, "html.parser")
    html = soup.body
    soup = BeautifulSoup(str(html), "html.parser")
    html = soup.find("div", attrs={"id": "wrapper"})
    a_list = [item.text for item in html.find_all("a", class_=re.compile(r'^'), href=re.compile(r'^https://www.douban.com/people'))]
    span_list = [item.text for item in html.find_all("span", class_="short")]
    return a_list, span_list


def local_store():
    '''
    经过观察得知每一页的url结构，组成url地址不断访问，将id和评论存入本地txt文件
    :return:None
    '''
    for i in range(0, 2000, 20):
        # 访问的url地址
        url = "https://movie.douban.com/subject/24852545/comments?start=" + str(i) + "&limit=20&sort=new_score&status=P"
        # 访问的头
        headers = {'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'http://www.xicidaili.com/nn/',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    }
        rsp = requests.get(url=url, headers=headers)
        if rsp.status_code == 200:
            html = rsp.text
        else:
            html = None
        if html is not None:
            id_list, content_list = parse_html(html)
        with open("text.txt", 'a', encoding="utf-8") as f:
            # 一个id必然对应一个评论，所以一个循环控制即可
            for i in range(len(id_list)):
                text = id_list[i] + " " + content_list[i]+"\n"
                f.write(text)


def data_analysis():
    '''
    进行得到txt文件内的数据分析
    由于数据限制，这里只进行词云分析
    :return: None
    '''
    with open("text.txt", 'r', encoding="utf-8") as f:
        text = f.read()
    comment = jieba.cut(text, cut_all=False)
    # 获得文件内容
    comment = " ".join(comment)
    # 解析背景图
    bg_img = plt.imread("bg.jpg")
    # 拦截词
    stopwords = set()
    stopwords.add("爱情公寓")
    stopwords.add("爱情")
    stopwords.add("公寓")
    stopwords.add("电影")
    # 创建wc对象
    wc = WordCloud(width=1800, height=1000, background_color='white', font_path="C:/Windows/Fonts/STFANGSO.ttf", mask=bg_img, stopwords=stopwords, max_font_size=400, random_state=50)
    wc.generate_from_text(comment)
    plt.imshow(wc)
    plt.axis('off')  # 不显示坐标轴
    plt.show()
    wc.to_file("result.jpg")







if __name__ == '__main__':
    # local_store()
    data_analysis()