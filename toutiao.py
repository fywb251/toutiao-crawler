#!coding=utf-8
##爬取今日头条频道数据
import requests
import json
import random
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  ###禁止提醒SSL警告
import hashlib
import execjs
from selenium import webdriver
from toutiaoitem import toutiaoitem
from toutiaouser import toutiaouser
from proxies import get_proxy_ip
from db import toutiaodb
import re
import html
import redis
import urllib


class toutiao(object):

    def __init__(self,path,url):
        self.path = path  # CSV保存地址
        self.url = url
        self.s = requests.session()
        self.page = 0
        self.user_page = 0
        self.search_item_list = []
        self.search_user_list = []
        self.user_artcile_list = []
        headers = {'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
                   'Connection': 'Keep-Alive',
                   }
        self.s.headers.update(headers)
        self.channel = re.search('ch/(.*?)/',url).group(1)
        self.r = redis.Redis(host='localhost', port=6379, password='Terran123456')

    def closes(self):
        self.s.close()


    def get_channel_data(self, page):  #获取数据
        req = self.s.get(url=self.url, verify=False, proxies=get_proxy_ip())
        #print (self.s.headers)
        #print(req.text)
        headers = {'referer': self.url}
        max_behot_time='0'
        signature='.1.hXgAApDNVcKHe5jmqy.9f4U'
        eas = 'A1E56B6786B47FE'
        ecp = '5B7674A7FF2E9E1'
        self.s.headers.update(headers)
        item_list = []
        browser = webdriver.Chrome()
        browser.implicitly_wait(10)
        browser.get(self.url)
        for i in range(0, page):

            Honey = json.loads(self.get_js())
            # eas = self.getHoney(int(max_behot_time))[0]
            # ecp = self.getHoney(int(max_behot_time))[1]
            eas = Honey['as']
            ecp = Honey['cp']
            signature = Honey['_signature']
            if i > 0:
                signature = browser.execute_script("return window.TAC.sign("+ max_behot_time +")")
            url='https://www.toutiao.com/api/pc/feed/?category={}&utm_source=toutiao&widen=1&max_behot_time={}&max_behot_time_tmp={}&tadrequire=true&as={}&cp={}&_signature={}'.format(self.channel,max_behot_time,max_behot_time,eas,ecp,signature)
            req=self.s.get(url=url, verify=False, proxies=get_proxy_ip())
            time.sleep(random.random() * 2+2)
            # print(req.text)
            # print(url)
            j=json.loads(req.text)
            for k in range(0, 10):
                item = toutiaoitem()
                now=time.time()
                if j['data'][k]['tag'] != 'ad' or j['data'][k]['tag'] != 'ad.platform.site':
                    item.title = j['data'][k]['title']  ##标题
                    item.source = j['data'][k]['source']  ##作者
                    item.source_url = 'https://www.toutiao.com/'+j['data'][k]['source_url']   ##文章链接
                    item.media_url = 'https://www.toutiao.com/'+j['data'][k]['media_url']  #作者主页
                    item.article_genre = j['data'][k]['article_genre']  #文章类型
                    try:
                        item.comments_count = j['data'][k]['comments_count']  ###评论
                    except:
                        item.comments_count = 0

                    item.tag = j['data'][k]['tag']  ###频道名
                    try:
                        item.chinese_tag = j['data'][k]['chinese_tag']   ##频道中文名
                    except:
                        item.chinese_tag = ''
                    try:
                        item.label = j['data'][k]['label']  ## 标签
                    except:
                        item.label = []
                    try:
                        item.abstract = j['data'][k]['abstract']  ###文章摘要
                    except:
                        item.abstract = ''
                    behot = int(j['data'][k]['behot_time'])
                    item.behot_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(behot))  ####发布时间
                    item.collect_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(now))  ##抓取时间
                    item.item_id = j['data'][k]['item_id']
                    try:
                        item.image_list = j['data'][k]['image_list']
                    except:
                        item.image_list = []
                    item.image_url = j['data'][k]['image_url']
                    item.middle_image = j['data'][k]['middle_image']
                item_list.append(item)
            toutiaodb.save(item_list)
            time.sleep(2)
            max_behot_time = str(j['next']['max_behot_time'])

    """
    搜索文章
    """
    def get_search_article(self, keyword, offset=0):
        keyword = urllib.request.quote(keyword)
        req_url = "https://www.toutiao.com/search_content/?offset={}&format=json&keyword={}&autoload=true&count=20&cur_tab=1&from=search_tab".format(offset,keyword)
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Connection': 'keep-alive',
            'authority': 'www.toutiao.com',
            'referer': "https://www.toutiao.com/search/?keyword={}".format(keyword),
            'method': 'GET',
            'path': "/search_content/?offset={}&format=json&keyword={}&autoload=true&count=20&cur_tab=1&from=search_tab".format(offset,keyword),
            'scheme': 'https'
        }
        self.s.headers.update(headers)
        req = self.s.get(req_url, proxies=get_proxy_ip())
        time.sleep(random.random() * 2 + 3)
        data = json.loads(req.text)
        items = data['data']
        if data['has_more'] == 1:
            self.page = self.page + 1
            offset = 20 * self.page
            self.parse_data(items)
            time.sleep(2)
            self.get_search_article(keyword, offset)
        else:
            self.parse_data(items)
            toutiaodb.save(self.search_item_list)

    def parse_data(self, items):
        for item in items:
            try:
                type = item['cell_type']
            except:
                type = 0

            if type == 37:    #微头条
                pass
            elif type == 50:
                pass
            elif type == 66:
                pass
            elif type == 26:   #内容推荐
                pass
            elif type == 20:   #搜索推荐
                pass
            elif type == 38:  #用户
                pass
            else:
                titem = toutiaoitem()
                titem.user_id = item['user_id']
                try:
                    titem.source = item['source']
                except:
                    titem.source = item['name']
                titem.title = item['title']
                titem.source_url = item['article_url']
                titem.media_url = item['media_url']
                titem.item_id = item['item_id']
                titem.abstract = item['abstract']
                titem.comments_count = item['comments_count']
                titem.behot_time = item['behot_time']
                titem.image_url = item['image_url']
                titem.image_list = item['image_list']
                titem.tag = item['tag']
                if 'play_effective_count' in item:
                    titem.article_genre = 'vedio'
                    titem.read_count = item['play_effective_count']
                else:
                    titem.article_genre = 'article'
                self.search_item_list.append(titem)

    """
    获取搜索的用户
    """
    def get_search_user(self, keyword, offset=0):
        keyword = urllib.request.quote(keyword)
        req_url = "https://www.toutiao.com/search_content/?offset={}&format=json&keyword={}&autoload=true&count=20&cur_tab=4&from=media".format(
            offset, keyword)
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Connection': 'keep-alive',
            'authority': 'www.toutiao.com',
            'referer': "https://www.toutiao.com/search/?keyword={}".format(keyword),
            'method': 'GET',
            'path': "/search_content/?offset={}&format=json&keyword={}&autoload=true&count=20&cur_tab=4&from=media".format(
                offset, keyword),
            'scheme': 'https'
        }
        self.s.headers.update(headers)
        req = self.s.get(req_url, proxies=get_proxy_ip())
        data = json.loads(req.text)
        # 随机休眠几秒
        time.sleep(random.random() * 2 + 3)
        items = data['data']
        if data['has_more'] == 1:
            self.page = self.page + 1
            offset = 20 * self.page
            self.parse_user(items)
            time.sleep(2)
            self.get_search_user(keyword, offset)
        else:
            self.parse_data(items)
            toutiaodb.save_user(self.search_user_list)

    def parse_user(self, users):
        for user in users:
            tuser = toutiaouser()
            tuser.user_id = user['user_id']
            tuser.avatar_url = user['avatar_url']
            tuser.name = user['name']
            tuser.gender = user['gender']
            tuser.media_id = user['media_id']
            tuser.create_time = user['create_time']
            tuser.follow_count = user['follow_count']
            tuser.source_url = user['source_url']
            tuser.description = user['description']
            tuser.id = user['id']
            self.search_user_list.append(tuser)


    """
    文章详情
    """
    def get_article_detail(self, item):
        url = 'https://www.toutiao.com/i' + item.item_id
        is_exist = self.r.sismember(u'url', url)
        # 如何redis中已经存在爬过的url则自动跳过
        if not is_exist and item.article_genre == 'article':
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Connection': 'keep-alive',
                'authority': 'www.toutiao.com',
                'referer': 'https://www.toutiao.com/i' + item.item_id + '/',
                'method': 'GET',
                'path': 'a/' + item.item_id + '/',
                'scheme': 'https'
            }
            self.s.headers.update(headers)
            req = self.s.get(url, proxies=get_proxy_ip())
            #随机休眠几秒
            time.sleep(random.random() * 2 + 3)
            resp_data = req.text
            data = resp_data.decode()
            content = re.findall(r"content:(.+)", data)[0]
            content = html.unescape(content)
            content = re.findall("'(.+)'", content)[0]
            item.content = content
            #更新文章内容
            toutiaodb.update(item)
            self.r.sadd(u'url', url)
        return item

    """
    获取用户主页的数据
    """
    def get_user_data(self, user):
        browser = webdriver.Chrome()
        browser.implicitly_wait(10)
        browser.get(user.media_url)
        self.fetch_user_articles(user,browser)

    def fetch_user_articles(self, user, browser):
        honey = json.loads(self.get_js())
        signature = honey['_signature']
        max_behot_time = "0"
        _as = honey['as']
        cp = honey['cp']
        if self.user_page > 0:
            signature = browser.execute_script("return window.TAC.sign(" + user.user_id+max_behot_time + ")")
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Connection': 'keep-alive',
            'authority': 'www.toutiao.com',
            'referer': user.media_url,
            'method': 'GET',
            'path': "/c/user/article/?page_type=1&user_id={}&max_behot_time={}&count=20&as={}&cp={}&_signature={}".format(
                user.user_id, max_behot_time, _as, cp, signature),
            'scheme': 'https'
        }
        self.s.headers.update(headers)
        req_url = "https://www.toutiao.com/c/user/article/?page_type=1&user_id={}&max_behot_time={}&count=20&as={}&cp={}&_signature={}".format(
            user.user_id, max_behot_time, _as, cp, signature)
        req = self.s.get(req_url, proxies=get_proxy_ip())
        # 通过随机数控制请求速度
        time.sleep(random.random() * 2 + 2)
        data = json.loads(req.text)
        max_behot_time = str(data['next'][max_behot_time])
        if data['has_more']:
            self.user_page = self.user_page + 1
            self.parse_user_artcle(data['data'], toutiaoitem.user_id, toutiaoitem.media_url)
            #在休眠2s
            time.sleep(2)
            self.fetch_user_articles(user, browser)
        else:
            self.parse_user_artcle(data['data'], toutiaoitem.user_id, toutiaoitem.media_url)
            toutiaodb.save(self.user_artcile_list)

    def parse_user_artcle(self, items, user_id, url):
        for item in items:
            toutiaoitem = toutiaoitem()
            toutiaoitem.user_id = user_id
            toutiaoitem.source = item['source']
            toutiaoitem.title = item['title']
            toutiaoitem.source_url = 'https:' + item['display_url']
            toutiaoitem.media_url = url
            toutiaoitem.item_id = item['item_id']
            toutiaoitem.abstract = item['abstract']
            toutiaoitem.comments_count = item['comments_count']
            toutiaoitem.behot_time = item['behot_time']
            toutiaoitem.image_url = item['image_url']
            toutiaoitem.image_list = item['image_list']
            toutiaoitem.tag = item['tag']
            toutiaoitem.chinese_tag = item['chinese_tag']
            toutiaoitem.read_count = item['go_detail_count']
            toutiaoitem.article_genre = item['article_genre']
            self.user_artcile_list.append(toutiaoitem)


    def getHoney(self,t):  #####根据JS脚本破解as ,cp
        #t = int(time.time())
        #t=1534389637
        #print(t)
        e =str('%X' % t)
        #print(e)
        m1 = hashlib.md5()
        m1.update(str(t).encode(encoding='utf-8'))
        i = str(m1.hexdigest()).upper()
        #print(i)
        n=i[0:5]
        a=i[-5:]
        s=''
        r=''
        for x in range(0,5):
            s+=n[x]+e[x]
            r+=e[x+3]+a[x]
        eas='A1'+ s+ e[-3:]
        ecp=e[0:3]+r+'E1'
        #print(eas)
        #print(ecp)
        return eas,ecp

    def get_js(self):  ###大牛破解as ,cp,  _signature  参数的代码，然而具体关系不确定，不能连续爬取
        # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
        f = open(r"./toutiao-TAC.sign.js", 'r', encoding='UTF-8')
        line = f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr + line
            line = f.readline()
        ctx = execjs.compile(htmlstr)
        return ctx.call('get_as_cp_signature')

 

if __name__=='__main__':
    path=r'./'  ##保存路径
    url='https://www.toutiao.com/ch/news_tech/'  ##频道URL
    t=toutiao(path,url)
    t.get_channel_data(3)
    # t.get_search_article('商业模式')
    t.closes()


