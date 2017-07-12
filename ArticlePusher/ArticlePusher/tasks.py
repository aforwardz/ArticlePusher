# coding: utf-8
import time
from ArticlePusher.celery import app
from ArticlePusher import launch_crawler
from ArticlePusher.util import utils
from celery.signals import task_success
import logging

task_logger = logging.getLogger('task_logger')


@app.task(queue='crawl', routing_key='crawl.tech')
def crawl_tech_sites():
    complete = launch_crawler.launch_tech_crawler()
    time.sleep(1)
    if complete:
        task_logger.info('crawl task complete')
        utils.set_update_flag()


# @task_success.connect(sender='ArticlePusher.tasks.crawl_tech_sites')
# def set_middleware_update_flag(sender=None, **kwargs):
#     print('set update flag')
#     utils.set_update_flag()


@app.task(queue='push', routing_key='push.articles')
def push_new_articles():
    pass
