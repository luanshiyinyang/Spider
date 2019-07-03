# 微信定时发送
- 简介
	- 本项目使用wxpy第三方包实现定时给微信好友或者微信群发送每日一句和天气预报。
- 环境配置
	- Python3环境
	- 第三方包
		- wxpy
			- 进行网页版微信登录及消息发送等功能。
			- **该第三方包基于Web版微信，目前不能与PC端微信同时登陆（微信网页版与PC版是一个接口），如果常用PC端微信建议使用小号登陆此程序。**
		- requests
			- 爬虫工具包，每天爬取指定最新信息。
- 设计思路
	- 爬取并解析
		- 爬取爱词霸提供的开放[API接口](http://open.iciba.com/dsapi/)信息。
			- 对该API提供的Json数据格式化如下，该接口需要得到的核心信息就是英文句子和中文翻译。
			- ![](/asset/day.png)
			- 使用requests对得到的response调用json方法即可解析json字符串为字典，代码如下。
				- ```python
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
					```
		- 爬取天气网站的开放[API接口](http://t.weather.sojson.com/api/weather/city/101190201)信息。
			- 对该API提供的Json数据格式化如下，该接口的核心信息是当天的天气信息，过去的几天和后来几天可以忽略（按照需求）。
			- ![](/asset/weather.png)
			- 使用requests对得到的response调用json方法即可解析json字符串为字典，并索引需要的信息进行相关的处理组合需要字符串即可，代码如下。
				- ```python
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
					```
		- 说明
			- 上述两个爬虫脚本没有进行异常处理，而API接口经常调整，最好需要进行相应的异常日志输出。
	- 定时发送
		- 逻辑
			- 程序运行进入无限循环，等待当前时间到达指定的一个发送时间如8时，退出循环，调用自动发送函数。
			- 发送成功则计时器开始等待，达到一天时间再次发送，回调当前函数。
			- 发送失败则给预定的报告好友发送失败消息。（一般发送给自己，在微信好友中自己是作为好友在好友列表的。）
		- 代码
			- ```python
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
				```
	- 具体部署
		- 由于该脚本必须保证一直运行，所以适合部署在云端服务器（能访问国内网络），因此每次都要扫码登录就不合适了，一般使用登录缓存。（具体在代码给出，博主也在腾讯云部署测试过，没有问题）
		- 该脚本建议后台进程部署，一旦运行便会自动阻塞，无法使用一般方式终止。
- 运行结果
	- 注意这里是发送给指定昵称搜索到的第一个，多个好友同一个昵称需要进行筛选。
	- ![](/asset/rst_cmd.png)
	- ![](/asset/result.jpg)
- 补充说明
	- 完整的代码已经上传到我的Github，欢迎Star或者Fork。
	- API地址来源其他博客。
	- 如有错误，欢迎指正。