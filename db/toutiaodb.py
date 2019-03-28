#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import json
from bs4 import BeautifulSoup
import re

conn = MongoClient('localhost', 27017)
db = conn.crawl
toutiao = db.toutiao
toutiao_user = db.toutiao_user


def fetch_all_users():
    users = toutiao_user.find()
    return users


#根据Id查询用户
def fetch_user(user_id):
    user = toutiao_user.find_one({"user_id": user_id})
    return user


#批量插入作者
def save_user(users):
    if len(users) == 0:
        return
    user_list = []
    for user in users:
        user_list.append(user.__dict__)
    toutiao_user.insert(user_list)


#批量保存文章
def save(items):
    # 从个人首页的链接中提取user_id
    if len(items) == 0:
        return
    item_list = []
    item_id_list = []
    #先补充user_id，遍历出要插入的文章id
    for item in items:
        if not item.user_id:
            user_id = re.findall(r".*?(\d+)\/", item.media_url)[0]
            item.user_id = user_id
        # item_list.append(item.__dict__)
        item_id_list.append(item.item_id)
    #判断是否存在已经存在的记录并去重复
    if len(item_id_list) > 0:
        item_temp = items[:]
        result = toutiao.find({"item_id": {'$in': item_id_list}})
        if result and len(result) > 0:
            for res in result:
                for item in item_temp:
                    if res['item_id'] == item['item_id']:
                        items.remove(item)
    for item in items:
        item_list.append(item.__dict__)
    toutiao.insert(item_list)


def fetch_empty_content():
    return toutiao.find({"content": ""})

#内容下载完成更新
def update(item):
    if len(item.content) > 0:
        soup = BeautifulSoup(item.content)
        item.content_text = soup.text
    toutiao.update({"item_id": item.item_id}, {"$set": {"is_complete": 1, "collect_count":item.collect_count+1, "content": item.content, "content_text": item.content_text}})


#更新阅读数
def update_read_count(item):
    toutiao.update({"item_id": item.item_id}, {"$set": {"read_count": item.read_count}})


#更新爬取次数
def update_collect_count(item):
    toutiao.update({"item_id": item.item_id}, {"$set": {"collect_count": item.collect_count+1}})


