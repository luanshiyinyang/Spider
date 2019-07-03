from wxpy import Bot
import requests
import time
from threading import Timer


def get_sentence():
    """
    获取每日一句
    """
    header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
    }
    url = "http://open.iciba.com/dsapi/"
    r = requests.get(url, headers=header)
    rsp = r.json()
    content = rsp['content']
    note = rsp['note']
    print(content, note)
    return content, note


def get_weather(city_no):
    """
    获取天气数据
    """
    url = 'http://t.weather.sojson.com/api/weather/city/'
    url = url + str(city_no)
    header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
    }
    r = requests.get(url, headers=header)
    rsp = r.json()
    # 解析得到的json数据以如下格式组合字符串
    '''
    # 今日天气预报
    # 年月日 + 星期 + 所在地城市
    # 天气类型 + 风向 + 风力
    # 温度范围（最低温度~最高温度）
    # 日出 + 日落
    # 污染指数：PM2.5/PM10/AQI
    # 当前温度 + 空气湿度
    # Notice信息
    '''
    today_info = rsp['data']['forecast'][0]
    date_list = today_info['ymd'].split('-')
    date = date_list[0] + '年' + date_list[1] + '月' + date_list[2] + '日' + '   ' + today_info['week'] + '   ' + rsp['cityInfo']['city'] + '\n'
    weather = '天气:' + today_info['type'] + '   ' + '风向:' + today_info['fx'] +  '   ' + '风力:' + today_info['fl'] + '\n'
    temp_range = '温度范围:' + today_info['low'] + today_info['high'] + '\n'
    sun = '日出:' + today_info['sunrise'] + '   ' + '日落' + today_info['sunset'] + '\n'
    level = '污染指数:' + 'PM2.5:' + str(rsp['data']['pm25']) + '   ' + 'PM10:' + str(rsp['data']['pm10']) + '   ' + 'AQI:'+ str(today_info['aqi']) + '\n'  # 注意整个数据只有这三项是浮点数
    temp_now = '当前温度:' + rsp['data']['wendu'] + '   ' + '湿度' + rsp['data']['shidu'] + '\n'
    notice = '注意:' + today_info['notice']
    
    result = date + weather + temp_range + sun + level + temp_now + notice
    return result
 
def auto_send():
    try:
        weather_info = get_weather(101190201)  # 无锡 
        sentence_info = get_sentence()
        # 发送给指定群组代码如下
        my_friend = bot.groups().search('一家人')[0]  # 昵称，官方文档解释会找到所有这个昵称的好友组合成列表，这可能是因为wxpy基于web微信，微信没有提供更深的接口
        # 发送给指定好友代码如下
        # my_friend = bot.friends().search('好友昵称')
        my_friend.send("早上好Y(^o^)Y，这里是今日份的天气信息请查收!")
        my_friend.send(weather_info)      
        my_friend.send("天天有个好心情哦!!!")
        my_friend.send(sentence_info[0])
        my_friend.send(sentence_info[1])
        # 每隔86400秒（1天），发送1次
        t = Timer(86400, auto_send)
        t.start()
 
    except:
        # 部署者的昵称，微信自己是作为自己的微信好友的
        my_friend = bot.friends().search('周先森爱吃素')[0]
        my_friend.send("今日份的信息发送失败了！")
 
 
if __name__ == "__main__":
    # 程序等待，直到到达时间第一次运行
    while True:
        if time.localtime().tm_hour >= 8:
            break
    
    # 扫码登录，Windows系统
    bot = Bot()
 
    # 扫码登录，Linux系统
    # bot = Bot(console_qr=2, cache_path="botoo.pkl")
 
    # 调用函数进行消息发送
    auto_send()
