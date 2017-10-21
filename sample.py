# -*- coding: utf-8 -*-
from qqbot import qqbotsched
from qqbot.utf8logger import DEBUG, INFO, ERROR
from utils import get_info_by_name, get_info_by_list
# from qqhandler import QQHandler

from pocket48_handler import Pocket48Handler
from wds_handler import WdsHandler
from weibo_handler import WeiboHandler

import time
import json
import random
import re
import ConfigParser


pocket48_handler = None
wds_handler = None
weibo_handler = None


config = ConfigParser.ConfigParser()
config.read('config.ini')
POCKET48_USERNAME = config.get("pocket48","username")
POCKET48_PASSWORD = config.get("pocket48","password")
WB_USERNAME = config.get("weibo","username")
WB_PASSWORD = config.get("weibo","password")
GROUP_ID = config.get("qq_groups","group_id")


ROOM_NAMES = ["冯思佳", "金锣赛", "孙语姗", "夏越"]   
LIVE_NAMES = ["BEJ", "刘力菲", "杜秋霖", "卢静", "卢天惠"] 
WEIBO_NAMES = ["SNH", "GNZ", "BEJ", "韩佳乐", "赵佳蕊"] 

# ROOM_IDS = []
# LIVE_IDS = []
# WEIBO_IDS = []

love_str = ["我最喜欢name!","超绝可爱name！","name天下第一可爱!"]


def check_member_info(content):
    tokens = content.split('-')
    if len(tokens) != 2:
        return None
    idol_name = tokens[0]
    type_name = tokens[1]
    DEBUG('%s %s'%(idol_name, type_name))
    if re.compile(u'^[\u4e00-\u9fa5]{2,4}$').match(idol_name.decode('utf-8')):
        if type_name in ["live", "love", "review", "wds", "weibo"]:
            return type_name
    return None

def onQQMessage(bot, contact, member, content):
    # 当收到 QQ 消息时被调用
    # bot     : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # contact : QContact 对象，消息的发送者
    # member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
    # content : str 对象，消息内容
    DEBUG('member: %s', str(getattr(member, 'uin')))
    global pocket48_handler
    global wds_handler
    global weibo_handler

    at_msg_str = "找本帝何事"

    if contact.ctype == 'group':
        if '@ME' in content:  # 在群中@机器人
            bot.SendTo(contact, member.name + '，' + at_msg_str)
        elif content.startswith('-'):
            info= content[1:]
            if info == "help":
                msg = "支持的操作:\n -version\n -小偶像\n " + \
                    "-live-list\n -live-love-list\n"
                bot.SendTo(contact, msg)

            elif info == "version":
                bot.SendTo(contact, 'QQbot-' + bot.conf.version)

            elif info == "live":
                res = pocket48_handler.get_memberLive_msg(limit = 40)
                pocket48_handler.parse_memberLive_msg(res)

            elif info == "live-love":
                res = pocket48_handler.get_memberLive_msg(limit = 30)
                live_list = pocket48_handler.parse_watchMemberLive_msg(res, by_hand = True)
                if not live_list:
                    bot.SendTo(contact, "没有关注的小偶像在直播呢！")

            elif check_member_info(info):
                idol_name, pattern = info.split('-')
                if not get_info_by_name(key = "name", restrict = "name", value = idol_name):
                    bot.SendTo(contact, "不认识的小偶像呢！")
                    return 

                if pattern == "live":
                    pass
                elif pattern == "love":
                    msg = random.choice(love_str).replace("name", idol_name)
                    bot.SendTo(contact, msg)  

                elif pattern == "review":
                    r = get_info_by_name(key = "live_id",  restrict = "name",   \
                                value = idol_name)
                    member_id, group_id = r[0]
                    DEBUG("Get review memberid:%s, group_id:%s"%(member_id, group_id))
                    res = pocket48_handler.get_memberLive_msg(limit = 10, \
                                memberId = member_id, groupId = group_id)
                    pocket48_handler.parse_memberReviewLive_msg(res)

                elif pattern == "wds":
                    res = wds_handler.get_name_wdsList(idol_name)
                    wds_handler.parse_name_wdsList(res)

                elif pattern == "weibo":
                    r = get_info_by_name(key = "weibo_id",  restrict = "name", \
                                value = idol_name)
                    weibo_id = r[0][0]
                    DEBUG("Get %s weibo_id:%s by hand"%(idol_name, weibo_id))
                    res = weibo_handler.get_member_weibo(wb_uid = weibo_id)
                    weibo_handler.parse_member_weibo(res)
            else:
                bot.SendTo(contact, "不认识的命令呢！")


def onStartupComplete(bot):
    # 启动完成时被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    DEBUG('%s.onStartupComplete', __name__)
    global pocket48_handler
    global wds_handler
    global weibo_handler
    # global ROOM_IDS 
    # global LIVE_IDS
    # global WEIBO_IDS

    ROOM_IDS = get_info_by_list(ROOM_NAMES, key = "room_id")
    LIVE_IDS = get_info_by_list(LIVE_NAMES, key = "member_id")
    WEIBO_IDS = get_info_by_list(WEIBO_NAMES, key = "weibo_id")

    DEBUG("ROOM_IDS:%s"%(' '.join(ROOM_IDS)))
    DEBUG("LIVE_IDS:%s"%(' '.join(LIVE_IDS)))
    DEBUG("WEIBO_IDS:%s"%(' '.join(WEIBO_IDS)))

    bot.SendTo(bot.List('group', GROUP_ID)[0], "官帝的机器人已启动~~")
    message = '目前监控的口袋房间：%s\n目前监控的直播：%s\n目前监控的微博：%s' \
                        %(' '.join(ROOM_NAMES), ' '.join(LIVE_NAMES), ' '.join(WEIBO_NAMES))
    bot.SendTo(bot.List('group', GROUP_ID)[0], message)

    pocket48_handler = Pocket48Handler(room_ids = ROOM_IDS, \
            group_id = GROUP_ID, liveWatch_ids = LIVE_IDS)
    pocket48_handler.login(POCKET48_USERNAME, POCKET48_PASSWORD)
    pocket48_handler.init_msg_queue(limit = 40)

    wds_handler = WdsHandler(group_id = GROUP_ID)

    weibo_handler = WeiboHandler(group_id = GROUP_ID, weibo_ids = WEIBO_IDS)
    weibo_handler.login(WB_USERNAME, WB_PASSWORD)
    weibo_handler.init_msg_queue(limit = 10)

    update_conf(bot)
  

@qqbotsched(hour='10')
def restart_sche(bot):
    DEBUG('RESTART scheduled')
    bot.FreshRestart()

@qqbotsched(minute='*')
def update_conf(bot):
    pass

@qqbotsched(second='10', minute='*')
def get_room_msgs(bot):
    global pocket48_handler
    for room_id in pocket48_handler.room_ids:
        res= pocket48_handler.get_roomChat_msg(room_id, limit = 10)
        pocket48_handler.parse_roomChat_msg(res, room_id)

@qqbotsched(minute='*', second='40')
def get_member_lives(bot):
    global pocket48_handler
    res = pocket48_handler.get_memberLive_msg(limit = 30)
    pocket48_handler.parse_watchMemberLive_msg(res)

@qqbotsched(minute='*/5', second='50')
def get_member_weibo(bot):
    global weibo_handler
    DEBUG("Weibo check begin!")
    for weibo_id in weibo_handler.weibo_ids:
        res = weibo_handler.get_member_weibo(weibo_id)
        weibo_handler.parse_watchMember_weibo(res, weibo_id)
    DEBUG("Weibo check finish!")




