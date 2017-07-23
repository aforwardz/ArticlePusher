# coding: utf-8
import redis
from ArticlePusher import settings
import requests
import os
import hashlib
import re
import json
from datetime import date, timedelta
import logging

util_logger = logging.getLogger('util_notice')


class SimpleHash:
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(value.__len__()):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(BloomFilter, cls).__new__(cls)
            return cls._instance
        return cls._instance

    def __init__(self):
        self.bit_size = 1 << 25
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.r = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=settings.UTILDB)
        self.hashFunc = []
        for i in range(self.seeds.__len__()):
            self.hashFunc.append(SimpleHash(self.bit_size, self.seeds[i]))

    def isContains(self, str_input, name):
        if not str_input:
            return False
        if str_input.__len__() == 0:
            return False
        ret = True
        for f in self.hashFunc:
            loc = f.hash(str_input)
            ret = ret & self.r.getbit(name, loc)
        return ret

    def insert(self, str_input, name):
        for f in self.hashFunc:
            loc = f.hash(str_input)
            self.r.setbit(name, loc, 1)


BloomInstance = BloomFilter()


class PusherGenerator(object):
    def __init__(self):
        self.client = redis.Redis(settings.REDIS_HOST, db=settings.STUFFDB)

    def generate_updated_key(self, sub_class, name):
        return ''.join([sub_class, '_', str(date.today()), '_', name])

    def generate_old_key(self, sub_class, name):
        return ''.join([sub_class, '_', str(date.today() - timedelta(days=1)), '_', name])

    def save_today_new_articles(self, sub_class, name, new_dict):
        """
        :param name: site name
        :param new_dict: article dict of today
        :return: article dict eliminated articles of yesterday
        """
        new_key = self.generate_updated_key(sub_class, name)
        old_key = self.generate_old_key(sub_class, name)
        if self.client.exists(old_key):
            old_dict = eval(self.client.get(old_key).decode('utf-8'))
            for key in old_dict.keys():
                try:
                    new_dict.pop(key)
                except:
                    util_logger.info('(๑•̀ᄇ•́)و ✧ | {team} has updated article ${key}% today!'.format(
                        team=name, key=key
                    ))
                    continue
            self.client.set(new_key, new_dict, ex=timedelta(days=10))
        else:
            self.client.set(new_key, new_dict, ex=timedelta(days=10))


def set_update_flag(flag_name):
    client = redis.Redis(settings.REDIS_HOST, db=settings.UTILDB)
    client.set(flag_name, settings.YES, xx=True)


def retreat_update_flag(flag_name):
    client = redis.Redis(settings.REDIS_HOST, db=settings.UTILDB)
    client.set(flag_name, settings.NO, xx=True)
