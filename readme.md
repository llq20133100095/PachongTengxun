@[toc]
# 1.《开端》
最近大火的《开端》让不少小伙伴着迷。这部剧主要讲述的是大学生**李诗情**和游戏架构师**肖鹤云**，在45路公交车被炸毁的当天**不断循环**，之后为了保护车上乘客的安全，携手阻止公交车爆炸，并找出爆炸人同时寻找凶手真正的作案动机的故事。

电视剧已经播放到了13集，还有两集才大结局，但是大部分观众已经迫不及待地想要看到电视剧最后两集的结局。

目前网友也在各大平台上对《开端》这部剧的结局进行了讨论。为了能够更加深入网友们近期最关注的到底是什么内容，因此利用了爬虫把《开端》的评论进行爬取，从而进行具体的分析。

# 2.爬取内容

主要爬取了腾讯视频上的评论，参考了文章上的做法：
[Python爬虫| 实战爬取腾讯视频评论](https://mp.weixin.qq.com/s?__biz=MzU2NTczODU3NA==&mid=2247485501&idx=1&sn=0f13b39533cd4ee4c272246a1cb8337c&chksm=fcb6651ccbc1ec0a62255c8e721b1b342deef6b7b7a710896cca1d522035a19ae96e1cf1d5fa&scene=21#wechat_redirect)

## 2.1 分析评论页面
我们可以看到，在《开端》这部剧的评论上，其内容是进行了折叠的：
![在这里插入图片描述](https://img-blog.csdnimg.cn/d885bb97bd0c454c9e310b96c853142a.png?x-oss-process=image)
这里可以知道，评论折叠主要使用了**Ajax异步刷新技术**。这样不能够靠常规的手段分析网页规律，来爬取具体的评论内容。这时候就需要通过抓包技术，分析评论的网页规律。

利用Fiddle抓包工具进行分析：
- 在网页上，点击按钮“**查看更多评论**”
- 通过在Fiddle工具上，找到对应的评论：

![在这里插入图片描述](https://img-blog.csdnimg.cn/1975ca256fa04963986d211f425673b1.png?x-oss-process=image)
- 复制Host中的url，我们就可以找到具体的网页链接地址：
![在这里插入图片描述](https://img-blog.csdnimg.cn/ba2f8958905547c894335806a0df83f7.png)
- 从上面可以看到，三个URL中，具体差异性在：**cursor=** 和 **&_**= 这两个值中，因此具体思路就是要找出这两个值的规律，然后就可以使用python进行内容爬取

- 具体规律查看上面的那篇文章，文章中发现**cursor**的值是从上一个链接继承过来的，因此当前页面的cursor可以用上一个URL来进行确定。而 **&** 这个值的规律是：上一个页面的 &_ - 下一个页面&_ = 1
![在这里插入图片描述](https://img-blog.csdnimg.cn/a423fb3caea74a2aa97165da4016771c.png?x-oss-process=image)
## 2.2 具体爬虫代码
由于过度频繁的请求腾讯视频网页，会返回**连接关闭**错误的提醒，为了避免这种情况，做了以下两种操作：
- 需要在每次爬取时进行睡眠操作，同时当出现错误时，睡眠更长的时间：
![在这里插入图片描述](https://img-blog.csdnimg.cn/4c3a358fe7b44882b35bceae4fcafd85.png?x-oss-process=image)

- 同时也保证在请求完一次后，需要把request连接进行关闭：
![在这里插入图片描述](https://img-blog.csdnimg.cn/817b51647c074878b4268649f23e7ce2.png?x-oss-process=image)

具体代码如下：
```python
import re
import random
import urllib.request
import time

#构建用户代理
uapools=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
         "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
        ]
#从用户代理池随机选取一个用户代理
def ua(uapools):
    thisua=random.choice(uapools)
    #print(thisua)
    headers=("User-Agent",thisua)
    opener=urllib.request.build_opener()
    opener.addheaders=[headers]
    #设置为全局变量
    urllib.request.install_opener(opener)

#获取源码
def get_content(page,lastId):
    # url="https://video.coral.qq.com/varticle/7640716440/comment/v2?callback=_varticle3242201702commentv2&orinum=10&oriorder=o&pageflag=1&cursor="+lastId+"&scorecursor=0&orirepnum=2&reporder=o&reppageflag=1&source=132&_="+str(page)
    url="https://video.coral.qq.com/varticle/7640716440/comment/v2?callback=_varticle7640716440commentv2&orinum=10&oriorder=o&pageflag=1&cursor="+lastId+"&scorecursor=0&orirepnum=2&reporder=o&reppageflag=1&source=132&_="+str(page)
    request=urllib.request.urlopen(url)
    html=request.read().decode("utf-8","ignore")
    request.close()
    return html

#从源码中获取评论的数据
def get_comment(html):
    pat='"content":"(.*?)"'
    rst = re.compile(pat,re.S).findall(html)
    return rst

#从源码中获取下一轮刷新页的ID
def get_lastId(html):
    pat='"last":"(.*?)"'
    lastId = re.compile(pat,re.S).findall(html)[0]
    return lastId

def main(save_file):
    ua(uapools)
    #初始页面
    page=1642842694728
    #初始待刷新页面ID
    lastId="6889565751302807937"
    for i in range(1,500):
        try:
            html = get_content(page,lastId)
            #获取评论数据
            commentlist=get_comment(html)
            print("------第"+str(i)+"轮页面评论------")
            for j in range(1,len(commentlist)):
                # print("第"+str(j)+"条评论：" +str(commentlist[j]))

                save_file.write(str(commentlist[j]) + "\n")
            print("Finish %d epoch" % i)
            #获取下一轮刷新页ID
            lastId=get_lastId(html)
            page += 1
            time.sleep(10)
        except:
            print("Start Sleep")
            time.sleep(30)
            continue

save_file = open("./data/pinglun.txt", "w", encoding='utf-8')
main(save_file)
save_file.close()
```

# 3.数据分析
利用爬虫，本次从腾讯视频网站上爬取了5257条数据。

通过词云分析，发现网友大部分都在关注《开端》这部剧情的几个关键词：**王萌萌、司机、循环、女儿、老张、色狼** 等等。
![在这里插入图片描述](https://img-blog.csdnimg.cn/1489ce62a0814a2eb4214952fbc6f783.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5rSb5YWLLeadjg==,size_15,color_FFFFFF,t_70,g_se,x_16)
从词频分布来看，高频词语**“循环”**、**“王萌萌”**出现得比较多，其次是**“司机”**这个词语：
![在这里插入图片描述](https://img-blog.csdnimg.cn/10d179bbe2f9437aa2c9fce11cef71cf.png)

根据文本分析，总结了以下几个比较有代表性得问题：

- **大结局关键道具？**
- **王萌萌是什么原因导致的下车？**
- **结局走向he还是be？**

## 3.1 最后大结局走向猜测

**（1）大结局关键道具？**

- 修复手机成为破局关键：大部分网友的评论中，与“王萌萌”关键词出现最多的是**手机，修复**等关键词，不难发现王萌萌手机中存在破局的关键性线索：
![在这里插入图片描述](https://img-blog.csdnimg.cn/ddfb98b661f044d1a58baac8087b3597.png)
![在这里插入图片描述](https://img-blog.csdnimg.cn/f89f0660c3614486b97cdc2e21d01c7d.png)

**（2）王萌萌是什么原因导致的下车？**

从“王萌萌”这个关键词语出发，对应的词云如下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/55d2a7987c464a5ca87a7467ffbe81d5.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5rSb5YWLLeadjg==,size_15,color_FFFFFF,t_70,g_se,x_16)

目前网友讨论的具体走向主要分为两种：

- **王萌萌在五年前陷入过循环**
- **王萌萌遭遇色狼**
![在这里插入图片描述](https://img-blog.csdnimg.cn/cf7749e89ea945069a87c845cad0ada0.png?x-oss-process=image)
这两种情况讨论最多，**同时有接近70%的人相信王萌萌处于循环中。**

处于循环中网友的猜测：

> 捋一下剧情 再猜一下结局\n不知道有没有原著也没看过\n按现在剧情来说
> 王萌萌出事的那次45路公交车后续没有爆炸车祸等情况发生，所以车内监控完好，监控内容显示王萌萌并无发生被欺负，吵架，疾病等情况发生，所以让她惊慌绝望非要桥上下车的理由，应该只有进入循环这一个理由了，个人感觉她并没有队友，很不幸当年她那一车人都没有一个道德高尚愿意信任她的人，她的循环应该是不断的经历整车人丧命的车祸（或也是爆炸），期间她也曾尝试过多种办法想救全车人但都无果，最后无奈的她选择救自己，但却不知道进入循环后如果选择自己活不救其他人，反而是终止循环死自己一个的结果。她下车前不是在看某一个人应该是在看所有人，觉得愧疚惋惜。

> 我感觉王萌萌也在45路公交循环，为了提前下车逃离死海。

> 我看到一篇文章说双循环，可能萌萌不只是应为坐过站而要下车吧

> 王萌萌想让李诗情他们解开父母的心结，发动了这个循环，然而能力有限，不得不吸取白的生命力维持循环

被色狼骚扰的猜测：

> 王萌萌本来就是个品学优良的好学生，考上了个好大学，家庭情况优异，这45路公交常有色狼猥亵小姑娘，司机因为快退休了不想惹事，次次都不理（我不知道电视剧怎么改的）怎么说也是司机的问题吧，王萌萌从小生活环境好没经历这种事情，当时已经吓疯了，所以才这样，当然抢方向盘是不对的。她妈妈更不用说了，我是真的很心疼锅姨，她太难了，啥都没了。当然公交上的乘客也很无辜，但是李诗情被捅那集车上的乘客和王萌萌坐的那辆公交上的乘客一样冷漠😶

> 只有我觉得事情的始作俑者是哪个色狼吗？没有他萌萌就不会去抢方向盘，不抢方向盘司机就不会放他下车，这样萌萌就不会死，萌萌不死的话，就不会有这次爆炸，也不会有人陷入循环，这一系列人中，多多少少都有过错，但是如果没有那个色狼，这一切都不会发生，追根溯源色狼才是一切的开始，或许别人都有一定的理由，但是色狼猥亵小姑娘有什么理由，图一时之快？看似他没有多少过错，即便报警也就是个拘留，但是如果没有这种人，会有后面的事吗？#开端#

**（3）结局走向he还是be？**

在对结局是he还是be来看，大部分观众还是保持着乐观的情绪，**有接近60%左右的观众认为结局走向良好**：
![在这里插入图片描述](https://img-blog.csdnimg.cn/4b7bfab1a24b4be28358b6ee6fa972c3.png?x-oss-process=image)
其中he结局：

> 我希望是这样的结局。因为他们每一个循环都在找线索都在排雷，到最后应该是成功排除炸弹，无一人受伤死亡，然后锅姨的女儿死因也查清楚了！

> 开端结局头脑风暴#想一个he的结局。第25次循环，这时候肖鹤云已经很难醒过来了，这是他们最后一次机会。但这次他不会再下车，先打电话给他的游戏合伙人让他修改以暴制暴的想法。再短信报警让老张戴好三级甲三级头。这次，猫之使徒终于觉醒了！！！！和李诗晴、肖鹤云配合拖延时间，在跨江大桥上顺利把炸弹递给张警官，并扔在江里。在警局，三人都没提循环，因为没有证据，老张也相信了真诚的三人，就放他们离开了。锅姨和司机入狱，李肖二人去探视，对偏执疯狂的锅姨说，我知道萌萌，我能理解你的感受，真的能理解……萌萌希望你们好。

当然，就我本人来说，最后还是希望结局是好的。肖鹤云和李诗情起码不会牺牲一个人来结束这个循环，毕竟连两个人的名字都这么有情侣性：
![在这里插入图片描述](https://img-blog.csdnimg.cn/6b00698c3cb34e898428d93e3adbe407.png?x-oss-process=image)

