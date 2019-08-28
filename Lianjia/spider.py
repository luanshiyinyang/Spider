# -*-coding:utf-8-*-
"""
Author: Zhou Chen
Date: 2019/8/27
Desc: 爬取链家网上海租房信息
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import re
import time

root_url = "http://sh.lianjia.com"
base_url = "http://sh.lianjia.com/zufang"
headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Referer': 'https://sh.lianjia.com/zufang/',
                    'Host': 'sh.lianjia.com',
                }


def parse_content(content_url):
    """

    :param content_url: 每一个租房的详情页链接
    :return:
    """
    time.sleep(0.5)
    rsp = requests.get(content_url, headers=headers)
    sub_bs = BeautifulSoup(rsp.text, features='lxml')
    # 交通数据
    traffic = ""
    traffic_div = sub_bs.find("div", attrs={'class': 'content__article__info4'})
    if traffic_div:
        traffic_info = traffic_div.ul.find_all("li")
        for li in traffic_info:
            subway_info = li.text.replace("\n", "").strip().split("-")[-1].strip()
            pattern = re.compile(r"[\u4e00-\u9fa5]+")
            re_rst = pattern.search(subway_info)
            traffic += "-".join([re_rst.group(0), subway_info[re_rst.span()[1]:-1]]) + ';'

    # 上架时间
    launch_time = sub_bs.find("div", attrs={'class': 'content__subtitle'}).text.replace("\n", "").strip()
    data_pattern = re.compile(r"[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])")
    launch_time = data_pattern.search(launch_time).group(0)
    # 楼层
    floor = sub_bs.find("div", attrs={'class', 'content__article__info'}).ul.find_all("li")[7].text
    floor = '-'.join([floor.split('/')[0][-3], floor.split('/')[1][:-1]])
    # 电梯
    elevator = 1 if sub_bs.find("div", attrs={'class', 'content__article__info'}).ul.find_all("li")[8].text.strip()[-1] == "有" else 0
    # 房源描述
    introduction = sub_bs.find("div", attrs={'class': 'content__article__info3'})
    if introduction:
        introduction = introduction.find("p", attrs={'data-el': 'houseComment'})
        if introduction:
            introduction = introduction['data-desc'].replace("<br />", "").strip()
        else:
            introduction = ""
    else:
        introduction = ""
    # 大图链接
    image_link = sub_bs.find("div", attrs={'class': 'content__article__slide__item'}).img['src']

    return traffic, launch_time, floor, elevator, introduction, image_link


def get_urls(url):
    rst = {
        'title': [],  # 标题
        'address': [],  # 地址
        'region': [],  # 区域
        'renting': [],  # 租金
        'area': [],  # 面积
        'toward': [],  # 朝向
        'room': [],  # 房间数
        'traffic': [],  # 地铁交通情况
        'launchtime': [],  # 房源上架时间
        'floor': [],  # 楼层
        'elevator': [],  # 有无电梯
        'introduction': [],  # 房源介绍
        'imagelink': [],  # 大图链接
    }

    for i in tqdm(range(1, 101)):
        page_url = url + '/pg' + str(i)
        rsp = requests.get(page_url, headers=headers)
        bs = BeautifulSoup(rsp.text, features='lxml')
        divs = bs.find_all("div", attrs={'class': 'content__list--item--main'})

        for div in divs:
            # 遍历每个出租房信息项，主要获得详情页url
            # 获得title
            rst['title'].append(div.a.get_text(strip=True))
            # 获得详情url并解析
            content_url = root_url + div.find("p", attrs={'class': 'content__list--item--title twoline'}).a['href']
            traffic, launch_time, floor, elevator, introduction, image_link = parse_content(content_url)
            rst['traffic'].append(traffic)
            rst['launchtime'].append(launch_time)
            rst['floor'].append(floor)
            rst['elevator'].append(elevator)
            rst['introduction'].append(introduction)
            rst['imagelink'].append(image_link)
            # 获得地址
            description = div.find("p", attrs={'class': 'content__list--item--des'}).text.replace("\n", "").strip()
            address = description.split('/')[0].strip()
            region = address.split('-')[0]
            rst['address'].append(address)
            rst['region'].append(region)
            # 获得租金
            renting = div.find("span", attrs={'class': 'content__list--item-price'}).em.text
            rst['renting'].append(renting)
            # 获得面积
            area = description.split('/')[1].strip()[:-1]
            rst['area'].append(area)
            # 获得朝向
            toward = "-".join(description.split('/')[2].strip().split(" "))
            rst['toward'].append(toward)
            # 房间数
            room = description.split('/')[3].strip()
            if "未知" in room:
                room = ""
            else:
                pattern = re.compile(r'\d+')
                re_rst = pattern.findall(room)
                room = '-'.join(re_rst)
            rst['room'].append(room)
    return rst


if __name__ == '__main__':
    parse_rst = get_urls(base_url)
    df_result = pd.DataFrame(parse_rst)
    df_result.to_csv('zufang.csv', encoding='utf-8', index=False)