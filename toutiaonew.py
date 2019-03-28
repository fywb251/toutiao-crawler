#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver

class toutiaonew(object):

    def parse_page(self,url):
        browser = webdriver.Chrome()
        browser.get(url)