# -*- coding:utf-8 -*-
import MySQLdb
import logging
import ConfigParser
import os

config = ConfigParser.ConfigParser()
path = os.path.join(os.path.abspath(os.getcwd()), "config.ini")
config.read(path)

mysql_config = {
    'user': config.get("mysql", "username"),
    'passwd': config.get("mysql", "password"),
    'host': '127.0.0.1',
    'port': 3306,
    'db': 'SNH48_db',
    'charset': 'utf8',
    'use_unicode': True
}

class MysqlHandler:
    def __init__(self):
        try:
            self.connection = MySQLdb.connect(**mysql_config)
        except Exception as e:
            logging.exception(e)

    def execute(self, sql):
        """
        针对insert, delete, update操作
        :param sql:
        :return:
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            logging.exception(e)
            self.connection.rollback()

    def select(self, sql):
        """
        读操作
        :param sql:
        :return:
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            logging.exception(e)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

if __name__ == "__main__":
    pass
