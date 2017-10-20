# -*- coding:utf-8 -*-
from mysql_handler import MysqlHandler

import requests
import re
import os
import sys
import json
import time
import ConfigParser

reload(sys)
sys.setdefaultencoding('utf8')

config = ConfigParser.ConfigParser()
path = os.path.join(os.path.abspath(os.getcwd()), "config.ini")
config.read(path)

mysql_handler = MysqlHandler()
username = config.get("pocket48","username")
password = config.get("pocket48","password")
VERSION = "4.1.8"


def get_member_info(team_id):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded; charset= utf-8',
        'Connection':"keep-alive",
        'Referer': 'http://www.snh48.com/member_ny.html',
        "Host" : "h5.snh48.com"
    }

    url = 'http://h5.snh48.com/resource/jsonp/members.php?gid=%s&callback=get_members_success'%(team_id)
    res = requests.get(url, headers = headers)
    res = res.text.split('(',1)[1][:-2]
    rows = json.loads(res, encoding='utf-8')["rows"]
    for row in rows:
        name = row["sname"]
        pinyin = row["pinyin"]
        
        room_id = "-"
        member_id = "-"
        group_id = "-"

        sid = row["sid"]
        gid = row["gid"]
        gname = row["gname"]
        abbr = row["abbr"]
        tid = row["tid"]
        tname = row["tname"]
        pid = row["pid"]
        pname = row["pname"]
        nickname = row["nickname"]
        join_day = row["join_day"]
        height = row["height"]
        birth_day = row["birth_day"]
        star_sign_12 = row["star_sign_12"]
        star_sign_48 = row["star_sign_48"]
        birth_place = row["birth_place"]
        speciality = row["speciality"]
        hobby = row["hobby"]
        # experience = row["experience"]
        catch_phrase = row["catch_phrase"]

        if sid == "40017":     #zhaojiarui
            catch_phrase = ""

        weibo_id = row["weibo_uid"]
        weibo_verifier = row["weibo_verifier"]
        blood_type = row["blood_type"]
        status = row["status"]

        print name

        sql = "INSERT INTO SNH48 \
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %(  \
                name,\
                pinyin,\
                room_id,\
                member_id,\
                group_id,\
                sid,\
                gid,\
                gname,\
                abbr,\
                tid,\
                tname,\
                pid,\
                pname,\
                nickname,\
                join_day,\
                height,\
                birth_day,\
                star_sign_12,\
                star_sign_48,\
                birth_place,\
                speciality,\
                hobby,\
                catch_phrase,\
                weibo_id,\
                weibo_verifier,\
                blood_type,\
                status)
        mysql_handler.execute(sql)

class CrawlerPocker48:
    def __init__(self):
        self.session = requests.session()
        self.token = ""
        self.username = username
        self.password = password
        
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

    def login(self):
        login_url = "https://puser.48.cn/usersystem/api/user/v1/login/phone"
        params = {
            "account" : self.username,
            "password" : self.password,
        }
        res = self.session.post(login_url, json = params, headers = self.login_header_args()).json()
        if res["status"] == 200:
            self.token = res["content"]["token"]
            print "login success, token is %s"%self.token
        else:
            print "login false"

    def get_room_info(self, page):
        headers = self.login_header_args()
        headers["Host"] = "pjuju.48.cn"
        headers["token"] = self.token
        headers["Content-Length"] = "68"
        params = {
                "groupId": "0",
                "topMemberIds": ["327587"],
                "needRootRoom": "true",
                "page": "%s"%page
        }
        
        url = "https://pjuju.48.cn/imsystem/api/im/v1/member/room/hot"
        res = self.session.post(url, json = params, headers = headers)
        return res

    def parse_room_info(self, response):
        res = json.loads(response.text, encoding = "utf-8")
        if res["status"] != 200:
            print res["status"]
            return 
        for row in res["content"]["data"]:
            name = row["memberName"].encode("utf8")
            room_id = row["roomId"]
            member_id = row["memberId"]
            group_id = row["groupId"]
            sid = row["voteMemberId"]

            print name, type(name)
            print member_id, room_id, group_id, sid

            sql = "UPDATE SNH48 SET room_id = '%s', member_id = '%s', group_id = '%s' \
                    WHERE name = '%s'" % (room_id, member_id, group_id, name)
            mysql_handler.execute(sql)


if __name__ == '__main__':
    # team_id_list = ["10", "20", "30", "40"]
    # for team_id in team_id_list:
    #     get_member_info(team_id)
    
    # handler = CrawlerPocker48()
    # handler.login()
    # for id in range(1,30):
    #     res = handler.get_room_info(page = id)
    #     handler.parse_room_info(res)
    #     time.sleep(0.05)


    mysql_handler.close()



