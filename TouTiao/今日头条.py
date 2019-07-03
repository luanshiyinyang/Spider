import requests
import json

base_url = "https://www.toutiao.com"
def get_pics(number):

    target_url = "https://www.toutiao.com/search_content/?offset=0&format=json&keyword=%E7%BE%8E%E5%A5%B3&autoload=true&count=20&cur_tab=3&from=gallery"
    target_url = target_url.replace("xxx", str(number))
    return target_url


if __name__ == '__main__':
    url_list = []
    for i in range(0, 1000, 20):
       url_list.append(get_pics(i))
    headers = {'Upgrade-Insecure-Requests': '1',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                      'Referer': 'http://www.xicidaili.com/nn/',
                      'Accept-Encoding': 'gzip, deflate, sdch',
                      'Accept-Language': 'zh-CN,zh;q=0.8',
                      }
    rsp_list = []
    for item in url_list:
        rsp_list.append(requests.get(item, headers=headers, verify=False))
    pic_list = []
    for item in rsp_list:
        j = json.loads(item.text)['data']
        for item in j:
            try:
                for i in item['image_list']:
                    pic_list.append("http:"+i['url'].replace("list", "large"))
            except Exception as e:
                pass
    import os
    number = 0
    os.chdir("zc2")
    for i in pic_list:
        s = requests.get(i, headers=headers).content
        with open(str(number)+".jpg", 'wb') as f:
            f.write(s)
            print(" 第{}张图片下载完成".format(number))
            number += 1

