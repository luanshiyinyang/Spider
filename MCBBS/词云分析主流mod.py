import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
def data_analysis():
    with open("get.txt", 'r') as f:
        text = f.read()
    text = jieba.cut(text, cut_all=False)
    text = " ".join(text)
    bg_img = plt.imread("bg.jpg")
    stopwords = set()
    stopwords_list = ["整合包", "mod", "整合","MCBBS", "精彩", "作品", "世界", "生存", "附属", "冒险", "很棒", "光影", "内含音乐"]
    for item in stopwords_list:
        stopwords.add(item)
    wc = WordCloud(width=1800, height=1000, background_color='white', font_path="C:/Windows/Fonts/STFANGSO.ttf", mask=bg_img, stopwords=stopwords, max_font_size=700, random_state=50)
    wc.generate_from_text(text)
    img_colors = ImageColorGenerator(bg_img)
    wc.recolor(color_func=img_colors)
    plt.imshow(wc)
    plt.axis('off')  # 不显示坐标轴
    plt.show()
    wc.to_file("result.jpg")
if __name__ == '__main__':
    data_analysis()