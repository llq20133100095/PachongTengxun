# function: 利用jieba分词后，进行词云分析
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 1.读取文件
save_txt = ""
error_nums = 0
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
fre_words = {}
for i in txt_cut.split(" "):
    if len(i) >= 2 and i not in stopwords:
        new_cut.append(i)
        if i not in fre_words:
            fre_words[i] = 1
        else:
            fre_words[i] += 1

#  # 3.生成词云
# wc = WordCloud(
#     font_path=r'.\simhei.ttf',
#     background_color = 'white',
#     width = 1000,
#     height = 880,).generate(" ".join(new_cut))

# # 4.显示词云图片
# plt.imshow(wc, interpolation="bilinear")
# plt.axis('off')
# plt.savefig("./data/ciyun.png")
# plt.show()

sorted(fre_words.items(), key=lambda item:item[1], reverse=True)
