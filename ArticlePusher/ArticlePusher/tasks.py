# coding: utf-8
from celery import shared_task
from ArticlePusher import launch_crawler
from ArticlePusher.wx_pusher.pusher import pusher
import logging

task_logger = logging.getLogger('task_logger')


@shared_task(queue='crawl')
def crawl_tech_sites():
    launch_crawler.launch_tech_crawler()


@shared_task(queue='push')
def push_new_articles():
    pass
