#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import Request

def get_ip_list(obj):
    ip_text = obj.findAll('tr', {'class': 'odd'})
    ip_list = []
    for i in range(len(ip_text)):
        ip_tag = ip_text[i].findAll('td')
        ip_port = ip_tag[1].get_text() + ':' + ip_tag[2].get_text()
        ip_list.append(ip_port)
    # print("共收集到了{}个代理IP".format(len(ip_list)))
    # print(ip_list)
    return ip_list


def get_random_ip(bsObj):
    ip_list = get_ip_list(bsObj)
    import random
    random_ip = 'http://' + random.choice(ip_list)
    proxy_ip = {'http:': random_ip}
    return proxy_ip

def get_proxy_ip():
    url = 'http://www.xicidaili.com/'
    headers = {
        'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    request = Request(url, headers=headers)
    response = urlopen(request)
    bsObj = BeautifulSoup(response, 'lxml')
    random_ip = get_random_ip(bsObj)
    return random_ip

if __name__ == '__main__':

    print(get_proxy_ip())     # 打印出获取到的随机代理IP
