# function: 利用jieba分词后，词语共现矩阵
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from snownlp import SnowNLP

# 1.读取文件
save_txt = ""
error_nums = 0
wenzhang = []
with open("./data/pinglun copy.txt", "rb") as f:
    while True:
        line = f.readline()
        if line:
            try:
                line = line.decode("utf-8")
            except:
                error_nums += 1
                print(error_nums)
                continue
            save_txt += line.strip()
            wenzhang.append(line)
        else:
            break

# stopwords
stopwords = []
with open("./data/stopwords.txt", "r", encoding="utf-8") as f:
    while True:
        line = f.readline()
        if line:
            line = line.strip()
            stopwords.append(line)
        else:
            break

# 2. 去掉单个字 \ stopwords
txt_cut = jieba.cut(save_txt)
txt_cut = " ".join(txt_cut)
new_cut = []
for i in txt_cut.split(" "):
    if len(i) >= 2 and i not in stopwords:
        new_cut.append(i)

# 3.
fre_words = []
for i in wenzhang:
    if "王萌萌" in i or "结局" in i or "萌" in i:
        w_i = jieba.cut(i)
        for word in "|".join(w_i).split("|"):
            if word in new_cut:
                if word not in fre_words:
                    fre_words.append(word)
                else:
                    fre_words.append(word)

# sorted(fre_words.items(), key=lambda item:item[1], reverse=True)

# # 4. positive and negative
# positive_nums = 0
# negative_nums = 0
# for i in wenzhang:
#     s1 = SnowNLP(i)
#     if s1.sentiments >= 0.9 and "结局" in i:
#         positive_nums += 1
#     elif s1.sentiments < 0.5:
#         negative_nums += 1
#         print(i, s1.sentiments)
#         if negative_nums == 50:
#             break

# print(positive_nums, negative_nums)

 # 3.生成词云
wc = WordCloud(
    font_path=r'.\simhei.ttf',
    background_color = 'white',
    width = 1000,
    height = 880,).generate(" ".join(new_cut))

# 4.显示词云图片
plt.imshow(wc, interpolation="bilinear")
plt.axis('off')
plt.savefig("./data/ciyun.png")
plt.show()