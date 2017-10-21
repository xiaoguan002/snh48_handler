# -*- coding:utf-8 -*-
from qqbot import _bot as bot
from qqhandler import QQHandler
from qqbot.utf8logger import INFO, ERROR, DEBUG

import requests
import json
import time
import sys
import os
from collections import defaultdict
from utils import convert_timestamp_to_timestr

reload(sys)
sys.setdefaultencoding('utf8')

VERSION = "4.1.8"


class Pocket48Handler:
    def __init__(self, liveWatch_ids = "", room_ids = "", group_id =""):
        self.room_ids = room_ids
        self.liveWatch_ids = liveWatch_ids
        self.group_id = group_id

        # DEBUG("监控的直播ID"+"\t".join(list(self.liveWatch_ids)))
        # DEBUG("监控的房间ID"+"\t".join(list(self.room_ids)))

        self.session = requests.session()
        self.token = ""
        self.is_login = False
        self.member_room_msg_ids = defaultdict(list)
        self.member_live_msg_ids = []
        
    def login_header_args(self):
        header = {
            "Host" : "puser.48.cn",
            "app-type" : "fans",
            "Accept" : "*/*",
            "version" : VERSION,
            "os" : "ios",
            "Accept-Language": "zh-Hans-CN;q=1, en-CN;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "imei": "E32F7DC6-5797-40D1-BDC2-A548B6337AED",
            "Content-Length": "54",
            "User-Agent": "Mobile_Pocket",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=utf-8"
        }
        return header;
    
    def roomChat_header_args(self):
        header = self.login_header_args()
        header["token"] = self.token
        header["Content-Length"] = "42"
        header["Host"] = "pjuju.48.cn"
        return header

    def memberLive_header_args(self):
        header = self.login_header_args()
        header["token"] = self.token
        header["Content-Length"] = "106"
        header["Host"] = "plive.48.cn"
        return header

    def login(self, username, password):
        if self.is_login:
            return
        login_url = "https://puser.48.cn/usersystem/api/user/v1/login/phone"
        params = {
            "account" : username,
            "password" : password,
        }
        res = self.session.post(login_url, json = params, headers = self.login_header_args()).json()
        if res["status"] == 200:
            self.token = res["content"]["token"]
            self.is_login = True
            DEBUG("Pocket48 login success, token is %s"%self.token)
        else:
            ERROR("login false")

    def init_msg_queue(self, limit = 20):
        for room_id in self.room_ids:
            res = self.get_roomChat_msg(room_id, limit = limit)
            # self.parse_roomChat_msg(res)
            for r in res["content"]["data"]:
                msg_id = r["msgidClient"]
                self.member_room_msg_ids[room_id].append(msg_id)

        res = self.get_memberLive_msg(limit = limit*2)
        self.parse_watchMemberLive_msg(res)

    def get_roomChat_msg(self, _room_id, limit = 10):
        url = "https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/chat"
        params = {
            "lastTime": 0,
            "limit": limit,
            "roomId": _room_id
        } 
        res = self.session.post(url, json = params, headers = self.roomChat_header_args()).json()

        if res["status"] == 200:
            DEBUG("Get room:%s chat success."%_room_id)
        else:
            DEBUG("fail to get room chat.")
        return res

    def parse_roomChat_msg(self, response, room_id):
        # DEBUG('Room: %s exit msg ids: %s'%(room_id,  \
        #         '\t'.join(self.member_room_msg_ids[room_id])))

        msgs = response["content"]["data"]
        msgs.reverse()

        for msg in msgs:
            message = ''
            extInfo = json.loads(msg["extInfo"])
            msg_id = msg["msgidClient"]

            if msg_id in self.member_room_msg_ids[room_id]:
                continue

            DEBUG("小偶像的房间%s有新消息了！"%room_id)

            if len(self.member_room_msg_ids[room_id]) > 1:
                self.member_room_msg_ids[room_id].insert(0, msg_id)
                self.member_room_msg_ids[room_id].pop(-1)

            msg_object = extInfo["messageObject"]
            idol_name = extInfo["senderName"]
            msg_time = msg["msgTimeStr"]

            if msg['msgType'] == 0:    #文字
                if msg_object == "text":
                    DEBUG("普通消息")
                    message = ('【%s的口袋房间】[%s]\n %s：%s'% (idol_name, msg_time, idol_name, extInfo["text"])) + message
                elif msg_object == "faipaiText":
                    DEBUG("翻牌消息")
                    member_msg = extInfo['messageText']
                    gl_msg = extInfo['faipaiContent']
                    gl_name = extInfo['faipaiName']
                    message = ('【%s的口袋房间】[%s]\n gl(%s) : %s\n %s ：%s' 
                                    % (idol_name, msg_time, gl_name, gl_msg, idol_name, member_msg)) + message
            elif msg["msgType"] == 1:  #图片
                DEBUG("图片消息")
                if msg["bodys"] == "":
                    DEBUG("skip pic")
                    continue
                bodys = json.loads(msg["bodys"])
                if "url" in bodys.keys():
                    url = bodys["url"]
                    message = ('【%s的口袋房间】[%s]\n 小偶像发图片啦！：\n%s'% (idol_name, msg_time, url)) + message
            elif msg["msgType"] == 2:  #语音
                DEBUG("语音消息")
                if msg["bodys"] == "":
                    DEBUG("skip voice")
                    continue
                bodys = json.loads(msg["bodys"])
                if "url" in bodys.keys():
                    url = bodys["url"]
                    message = ('【%s的口袋房间】[%s]\n 小偶像发语音啦！：\n%s'% (idol_name, msg_time, url)) + message 
            elif msg["msgType"] == 3:  #小视频
                DEBUG("小视频消息")
                if msg["bodys"] == "":
                    DEBUG("skip video")
                    continue
                bodys = json.loads(msg["bodys"])
                if "url" in bodys.keys():
                    url = bodys["url"]
                    message = ('【%s的口袋房间】[%s]\n 小偶像发小视频啦！：\n%s'% (idol_name, msg_time, url)) + message
            else:
                DEBUG("unknown msgType")
                continue

            # QQHandler.send_to_groups(group_id, message)
            bot.SendTo(bot.List('group', self.group_id)[0], message)
            time.sleep(2)

    def get_memberLive_msg(self, limit = 50, memberId = 0, groupId = 0):
        url = "https://plive.48.cn/livesystem/api/live/v1/memberLivePage"
        params = {
            "type": 0,
            "limit": limit,
            "giftUpdTime": 1503766100000,
            "memberId": memberId,
            "groupId": groupId,
            "lastTime": 0
        }
        res = self.session.post(url, json = params, headers = self.memberLive_header_args()).json()

        if res["status"] == 200:
            DEBUG("Get member live success.")
        else:
            DEBUG("fail to get member live.")
        return res

    def parse_memberLive_msg(self, response):
        message = ""
        if "liveList" in response["content"].keys():
            DEBUG("获得直播列表")
            live_list = response["content"]["liveList"]
            message = message + "当前共有%s人在直播：\n\n"%(len(live_list))
            for live_info in live_list:
                idol_name = live_info["title"]
                subtitle = live_info["subTitle"]
                streamPath = live_info["streamPath"]
                live_id = live_info["liveId"]
                member_id = live_info["memberId"]
                live_url = 'https://h5.48.cn/2017appshare/memberLiveShare/index.html?id=%s' % live_id
                message += ('%s : %s\n %s\n\n'%(idol_name, subtitle, live_url))

            bot.SendTo(bot.List('group', self.group_id)[0], message)
        else:
            bot.SendTo(bot.List('group', self.group_id)[0], "当前没有小偶像在直播~~")

    def parse_watchMemberLive_msg(self, response, by_hand = False):
        all_live_ids = []
        if "liveList" in response["content"].keys():
            live_list = response["content"]["liveList"]
            for live_info in live_list:
                member_id = str(live_info["memberId"])
                idol_name = live_info["title"]
                subtitle = live_info["subTitle"]
                streamPath = live_info["streamPath"]
                live_id = live_info["liveId"]
                live_url = 'https://h5.48.cn/2017appshare/memberLiveShare/index.html?id=%s' %live_id
                all_live_ids.append(member_id)

                if member_id in self.liveWatch_ids:
                    if member_id not in self.member_live_msg_ids:
                        DEBUG("%s开始直播！"%member_id)
                        message = '你关注的小偶像正在直播！\n\n'
                        message += ('%s : %s\n %s'%(idol_name, subtitle, live_url))
                        bot.SendTo(bot.List('group', self.group_id)[0], message)
                        self.member_live_msg_ids.append(member_id)
                    elif by_hand:
                        message = '你关注的小偶像正在直播！\n\n'
                        message += ('%s : %s\n %s'%(idol_name, subtitle, live_url))
                        bot.SendTo(bot.List('group', self.group_id)[0], message)
                    else:
                        DEBUG("%s在直播列表中！"%member_id)
        if not self.member_live_msg_ids:
            DEBUG("没有关注的小偶像在直播！")

        for member_id in self.member_live_msg_ids:
            if member_id not in all_live_ids:
                self.member_live_msg_ids.remove(member_id)
                DEBUG('%s关掉了直播'%member_id)
        return self.member_live_msg_ids

    def parse_memberReviewLive_msg(self, response, limit = 5):
        message = ""
        if "reviewList" in response["content"].keys():
            DEBUG("获得录播列表")
            live_list = response["content"]["reviewList"]
            live_list = live_list[:limit]
            message += "小偶像的录播：\n\n"
            for live_info in live_list:
                idol_name = live_info["title"]
                subtitle = live_info["subTitle"]
                streamPath = live_info["streamPath"]
                startTime = convert_timestamp_to_timestr(live_info["startTime"])
                live_id = live_info["liveId"]
                member_id = live_info["memberId"]
                message += ('%s : %s [%s]\n %s\n\n'%(idol_name, subtitle, startTime,  streamPath))
            bot.SendTo(bot.List('group', self.group_id)[0], message)

if __name__ == "__main__":
    bot.Login(['-q', '2754757912'])
    handler = Pocket48Handler()
    handler.login()
    # res = handler.get_roomChat_msg(room_id, limit = 1)
    # handler.parse_roomChat_msg(res, room_id)
    res = handler.get_memberLive_msg(limit = 20)
    handler.parse_memberLive_msg(res)










	

