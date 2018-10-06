import time
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
import re

# 获得一组可能可用的代理ip地址
def getproxy():
    # 目标地址
    target_url = "http://www.goubanjia.com/"
    # 使用谷歌浏览器
    driver = webdriver.Chrome(r'C:\Users\16957\AppData\Local\Google\Chrome\Application\chromedriver.exe')
    # 等待js加载
    time.sleep(1)
    # 访问地址
    driver.get(target_url)
    # 得到html文件
    target_html = driver.page_source
    # 建立bs对象
    bs = BeautifulSoup(target_html, 'html.parser')
    # 找到了20个存放地址的td标签
    rst_etree = bs.find_all(attrs={'class': 'ip'})
    index = 0
    addr_list = []
    # 遍历每一个td
    while index < len(rst_etree):
        rst_etree[index] = str(rst_etree[index])
        # 用l存放所有网页分析干扰项的p标签
        list_p = re.compile(r'<p.*?>[^<]*?</p>').findall(rst_etree[index])
        # 将所有p标签替换为空字符
        for item in list_p:
            rst_etree[index] = rst_etree[index].replace(item, "")
        # 通过etree里的xpath中的string方法获得ip地址
        dom = etree.HTML(rst_etree[index])
        ip_addr = ''
        ip_addr += dom.xpath("string(.)")
        addr_list.append(ip_addr)
        index += 1
    # 得到最新的代理ip列表
    return addr_list


def check_ip(ip_list=[]):
    # 使用request验证ip可用性
    import requests
    for item in ip_list:
        proxies = {
            "http": item,
            "https": item
        }
        # 如果连接成功，且返回来内容认为ip可用，返回该ip退出循环
        try:
            rsp = requests.get("http://www.baidu.com", proxies=proxies)
            if rsp.text is not None:
                return item
                break
        except Exception:
            pass
    # 如果20个遍历完没找到可用的ip，返回none
    return None


# 得到一个可用的ip地址
# 这个函数在其他地方导入该模块并且执行该函数就会返回一个可用的ip地址
def get_one_proxy_ip():
    ip_list = getproxy()
    if check_ip(ip_list) is not None:
        return check_ip(ip_list)
    else:
        return None


if __name__ == '__main__':
    print(get_one_proxy_ip())