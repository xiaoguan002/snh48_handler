# -*- coding: utf-8 -*-
import time
from snh48db_handler.mysql_handler import MysqlHandler

TEAM_LIST = ["SII", "NII", "HII", "X", "XII", "B", "E", "J", \
                "G", "NIII", "Z", "SIII", "HIII", "新成员"]
GROUP_LIST = ["SNH", "BEJ", "GNZ", "SHY"]


def convert_timestamp_to_timestr(timestamp):
    """
    将13位时间戳转换为字符串
    :param timestamp:
    :return:
    """
    timeArray = time.localtime(timestamp / 1000)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return time_str


def convert_timestr_to_timestamp(time_str):
    """
    将时间字符串转换为时间戳
    :param self:
    :param time_str:
    :return:
    """
    timestamp = time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
    return int(timestamp)


def get_info_by_name(key = "member_id", restrict = "name", value = "", status = '99'):
    """ 
    name_type = name | gname| tname  
    info_name = * | member_id | group_id | live_id | weibo_id 
    """
    mysql_handler = MysqlHandler()
    status_str = "STATUS = '99'" if status == '99' else "STATUS = '44'"
    res = ''
    if key not in ["*", "member_id", "room_id", "group_id", "live_id", "name", "weibo_id", "sid"]:
        return res
    if restrict not in ["name", "tname", "gname", "sid", "member_id", "weibo_id"]:
        return res
    
    if key != "live_id":
        sql = "SELECT %s FROM SNH48 WHERE %s = '%s' AND %s"%(key, restrict, value, status_str)
        res = mysql_handler.select(sql)
    else:
        sql = "SELECT member_id, group_id FROM SNH48 WHERE %s = '%s' AND %s"%(restrict, value, status_str)
        res = mysql_handler.select(sql)

    mysql_handler.close()
    res = filter(lambda x : x[0] != '-', res)
    return res


def get_info_by_list(name_list, key = "room_id"):
    res = []
    for item in name_list:
        if item in TEAM_LIST:
            r = get_info_by_name(key = key, restrict = "tname", value = item)
            res.extend(r)
        elif item in GROUP_LIST:
            r = get_info_by_name(key = key, restrict = "gname", value = item)
            res.extend(r)
        else:
            r = get_info_by_name(key = key, restrict = "name", value = item)
            res.extend(r)
  
    if key != "live_id":
        res = map(lambda x : x[0], res)
    return res




