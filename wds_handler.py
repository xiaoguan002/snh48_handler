# -*- coding: utf-8 -*-
from qqbot import _bot as bot
from qqbot.utf8logger import INFO, ERROR, DEBUG

import requests
import json
import time
from utils import convert_timestr_to_timestamp

class WdsHandler:
    def __init__(self, group_id):
        self.session = requests.session()
        self.group_id = group_id

    def wds_search_headers(self):
    	headers = {
            "Host": "wds.modian.com",
            "Connection": "keep-alive",
            "Content-Length": "68",
            "Accept": "application/json",
            "Origin": "https://wds.modian.com",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://wds.modian.com/search_wds?category=1",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en,zh-CN;q=0.8,zh;q=0.6,en-US;q=0.4,ja;q=0.2,zh-TW;q=0.2"
        }
        return headers

    def get_name_wdsList(self, idol_name):
        url = "https://wds.modian.com/ajax_search"
        
        params = {
            "category" : "1",
            "keyword":idol_name,
            "page":"1",
            "page_rows":"10",
            "ajaxtype":"1"
        }
        res = self.session.post(url, data = params, headers = self.wds_search_headers()).json()
        return res

    def parse_name_wdsList(self, response):
    	if response["status"] == "-1":
            DEBUG("fail to get wds list")
            bot.SendTo(bot.List('group', self.group_id)[0], "查不到小偶像的集资链接~~")
            return 

    	current_timestamps = int(time.time())
    	wds_cnt = 0
    	message = ''

    	for des in response["des"]:
    		id = des["id"]
    		name = des["name"]
    		goal = des["goal"]
    		all_amount = des["all_amount"]
    		end_timestamps = convert_timestr_to_timestamp(des["end_time"])
    		url = "https://wds.modian.com/show_weidashang_pro/%s"%id

    		if current_timestamps < end_timestamps:
    			wds_cnt += 1
    			message += ("%s: \n目标：%s，已集：%s \n链接：%s\n\n")%(name, goal, all_amount, url)

    	message = "你查询的小偶像有%s个进行中的集资：\n\n"%(wds_cnt) + message
    	bot.SendTo(bot.List('group', self.group_id)[0], message)


if __name__ == "__main__":
	pass

    		

















        