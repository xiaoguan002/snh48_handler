# -*- coding: utf-8 -*-
from qqbot import _bot as bot
from qqbot.utf8logger import INFO, ERROR, DEBUG
from utils import get_info_by_name

from collections import defaultdict
import requests
import json
import time
import re


class WeiboHandler:
    def __init__(self, group_id = '', weibo_ids = ''):
        self.session = requests.session()
        self.group_id = group_id
        self.weibo_ids = weibo_ids
        self.weibo_msg_queue = defaultdict(list)
        
        self.reqHeaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://passport.weibo.cn/signin/login',
            'Connection': 'close',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        }

        
    def login(self, username, password):
        loginApi = 'https://passport.weibo.cn/sso/login'
        loginPostData = {
            'username': username,
            'password': password,
            'savestate': 1,
            'r': '',
            'ec': '0',
            'pagerefer': '',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'mainpageflag': 1,
            'hff': '',
            'hfp': ''
        }
       
        res = self.session.post(loginApi, data=loginPostData, headers=self.reqHeaders)
        if res.status_code == 200 and json.loads(res.text)['retcode'] == 20000000:
            DEBUG('Weibo login successful! UserId:' + json.loads(res.text)['data']['uid'])

    def init_msg_queue(self, limit = 10):
        for weibo_id in self.weibo_ids:
            res = self.get_member_weibo(weibo_id)
            for i in res.json()['cards']:
                if i['card_type'] == 9:
                    id = i['mblog']['id']
                    self.weibo_msg_queue[weibo_id].append(id)
                time.sleep(0.01)
        DEBUG("Init weibo msg queue success.")
           
    def get_member_weibo(self, wb_uid):
        url = 'https://m.weibo.cn/api/container/getIndex?uid=%s&type=uid&value=%s' % (wb_uid, wb_uid)
        res = self.session.get(url, headers=self.reqHeaders)
        container_id = None
        for i in res.json()['tabsInfo']['tabs']:
            if i['tab_type'] == 'weibo':
                container_id = i['containerid']
        weibo_info = 'https://m.weibo.cn/api/container/getIndex?uid=%s&type=uid&value=%s&containerid=%s' % (
                wb_uid, wb_uid, container_id)
        r = self.session.get(weibo_info, headers=self.reqHeaders)
        # DEBUG("Get weibo_id:%s success."%wb_uid)
        return r

    def parse_member_weibo(self, response, limit = 5):
        cnt = 1
        for i in response.json()['cards']:
            if i['card_type'] == 9:
                if cnt > limit:
                    break
                message = ''
                cnt += 1
                id = i['mblog']['id']
                created_at = i["mblog"]["created_at"]
                name = i["mblog"]["user"]["screen_name"]
                text = re.compile(r'<[^>]+>', re.S).sub('', i["mblog"]["text"])

                message += "【%s】 %s:\n%s\n"%(created_at, name, text)

                if "data-url" in i["mblog"]["text"]:
                    video_url = re.compile(r'data-url="(.*?)"', re.I).search(text).groups()[0]
                    message += "%s\n"%video_url

                if "pics" in i["mblog"].keys():
                    for pic in i["mblog"]["pics"]:
                        message += "%s\n"%(pic["url"])

                bot.SendTo(bot.List('group', self.group_id)[0], message)
                time.sleep(0.05)

    def parse_watchMember_weibo(self, response, weibo_id, limit = 10):
        # DEBUG("Get Weibo:%s success"%weibo_id)
        cnt = 1
        for i in response.json()['cards']:
            if i['card_type'] == 9:
                if cnt > limit:
                    break
                cnt += 1
                message = ''
                id = i['mblog']['id']
                created_at = i["mblog"]["created_at"]
                name = i["mblog"]["user"]["screen_name"]
                text = re.compile(r'<[^>]+>', re.S).sub('', i["mblog"]["text"])

                if id in self.weibo_msg_queue[weibo_id]:
                    continue

                DEBUG("Weibo_id:%s %s有新微博了！"%(weibo_id, name))
                message += "%s 有新微博了！\n"%name
                if len(self.weibo_msg_queue[weibo_id]) > 1:
                    self.weibo_msg_queue[weibo_id].insert(0, id)
                    self.weibo_msg_queue[weibo_id].pop(-1)

                message += "【%s】 %s:\n%s\n"%(created_at, name, text)

                if "data-url" in i["mblog"]["text"]:
                    video_url = re.compile(r'data-url="(.*?)"', re.I).search(text).groups()[0]
                    message += "%s\n"%video_url

                if "pics" in i["mblog"].keys():
                    for pic in i["mblog"]["pics"]:
                        message += "%s\n"%(pic["url"])

                bot.SendTo(bot.List('group', self.group_id)[0], message)
                time.sleep(0.05)


if __name__ == "__main__":
	pass


