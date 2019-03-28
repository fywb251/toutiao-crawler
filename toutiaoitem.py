#!/usr/bin/python
# -*- coding: utf-8 -*-


class toutiaoitem(object):

    def __init__(self):
        self.title = ""  #标题
        self.source = ""  #作者
        self.media_url = ""  #作者主页
        self.source_url = ""  #详情地址
        self.article_genre = ""  #文章类型
        self.item_id = ""   #文章ID
        self.behot_time = '' #发布时间
        self.abstract = ""  #摘要
        self.tag = ""  #英文标签
        self.label = []  #系统打打标签
        self.comments_count = 0  #评论数
        self.chinese_tag = ""  #中文标签
        self.image_list = []  #图片地址
        self.image_url = ""  #标题图片地址
        self.middle_image = ""  #原图地址
        self.content = ""  #文章内容
        self.content_text = ""  #纯文本
        self.read_count = 0   #阅读数
        self.collect_time = ''  #爬虫收录时间
        self.is_complete = 0  #内容是否爬完
        self.collect_count = 0  #爬取的次数
        self.user_id = ""


