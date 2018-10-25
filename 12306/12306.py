import requests
import re
'''
这个模块是要获得全国所有的车次详细信息，并且存入数据库
然而12306是没有提供这个功能的，只能查询出发地到目的地的车票
但是进行抓包发现交互了一个js文件，文件内是接下来45天车票信息
由此得到思路：
    不妨得到一个大致的车次信息的只包含出发地-目的地的集合
    然后利用查询的接口去按具体的日期查询车票情况
    由于查询的接口无法使用中文，所以利用12306一个地点代码集去建立一个"中文地点：大写字母代号"的字典
'''
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }


def get_train_set():
    '''
    获得以后45天(可买票时间)内有车的两地,减少query请求的数据量，不给服务器带来太大负担
    js数据量小，不需要落地

    :return:一个大致的车次集合
    '''
    url = "https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0"
    requests.adapters.DEFAULT_RETRIES = 5
    requests.packages.urllib3.disable_warnings()
    try:
        response = requests.get(url, stream=True, verify=False, headers=headers)
        status = response.status_code
    except Exception as e:
        status = None
    if status == 200:
        rst = response.content.decode('utf-8')
        import datetime
        year = datetime.datetime.now().year
        sss = rst.replace("},{", "}\n{").replace(str(year) + "-", "\n").replace("[", "\n").split("\n")
        m_list = list()
        for s in sss:
            pattern = re.compile(r'\((\w+-\w+)\)')
            match = pattern.search(s)
            if match:
                m_list.append(match.group(1))
        train_set = set(m_list)
    return train_set


def get_code_dict():
    '''
    建立一个中文地点名和code相关的字典，作为query的查找字典
    利用的api是https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=2.0
    :return:一个可供查找的字典
    '''
    with open("dict.txt", 'r', encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(r'[\u4e00-\u9fa5]+|[A-Z]+')
    groups = pattern.findall(content)
    groups.remove("海")
    groups.remove("口东")
    groups.remove("KEQ")
    groups.remove("南")
    groups.remove("昌")
    groups.remove("NOG")
    groups.remove("三")
    groups.remove("亚")
    groups.remove("JUQ")
    groups.remove("包头")
    groups.remove("东")
    groups.remove("FDC")
    groups.remove("BTC")
    groups.remove("BTQ")
    code_dict = dict()
    i = 0
    while i < len(groups):
        code_dict[groups[i]] = groups[i+1]
        i += 2
    code_dict["包头"] = "BTC"
    return code_dict


def get_query_list(date):
    '''
    核心代码，可以说这个模块就是为它服务的
    之前得到一个集合可以大致确认哪里到哪里有车，但是不能确认哪一天有没有车，这个api就可以确认是不是有车，返回详细的数据

    :param date: 需要查询的日期格式为-2018-1-1
    :return: 返回一个结果列表，由于传入的set不重复，这里也不会重复，用列表即可
    '''
    url_start = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=datedatedate&leftTicketDTO.from_station=fromwhere&leftTicketDTO.to_station=towhere&purpose_codes=ADULT'
    # datedatedate替换为日期，格式为yyyy-mm-dd
    # fromwhere替换为出发地，使用code
    # towhere替换为目的地，使用code
    reference = get_code_dict()
    requests.adapters.DEFAULT_RETRIES = 5
    requests.packages.urllib3.disable_warnings()
    for item in get_train_set():
        temp = item.split("-")
        fromwhere = reference.get(temp[0])
        towhere = reference.get(temp[1])
        if fromwhere is None or towhere is None:
            continue
        url = url_start
        url = url.replace("datedatedate", date).replace("fromwhere", fromwhere).replace("towhere", towhere)
        import time
        time.sleep(1)
        try:
            response = requests.get(url, stream=True, verify=False, headers=headers)
            status = response.status_code
        except Exception as e:
            status = None
        if status == 200:
            try:
                rst = response.json()
                need = rst['data']['result']
                print("有数据")
                for item in need:
                    rst_dict = dict()
                    rst_dict["from_city"] = temp[0]
                    rst_dict["to_city"] = temp[1]
                    rst_dict["trains"] = item.split("|")[3]
                    rst_dict["begin_time"] = item.split("|")[8]
                    rst_dict["end_time"] = item.split("|")[9]
                    with open(date+".txt", 'a', encoding='utf-8') as f:
                        f.write(rst_dict["from_city"] + " " + rst_dict["to_city"] + " " + rst_dict["begin_time"]+ " " + rst_dict["end_time"] + " " + rst_dict["trains"] + " ""\n")
            except Exception as e:
                pass
    return None


if __name__ == '__main__':
    import datetime
    today = datetime.datetime.now().date()
    get_query_list(str(today))
