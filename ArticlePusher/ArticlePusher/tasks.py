# coding: utf-8
from ArticlePusher.celery import app
from ArticlePusher import launch_crawler
import logging

task_logger = logging.getLogger('task_logger')


@app.task(queue='crawl', routing_key='crawl.tech')
def crawl_tech_sites():
    launch_crawler.launch_tech_crawler()


@app.task(queue='push', routing_key='push.articles')
def push_new_articles():
    pass
