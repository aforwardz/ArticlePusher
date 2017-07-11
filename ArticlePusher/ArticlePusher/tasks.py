# coding: utf-8
from celery import shared_task
from ArticlePusher import launch_crawler
import logging

task_logger = logging.getLogger('task_logger')


@shared_task(queue='crawl')
def crawl_tech_sites():
    launch_crawler.launch_tech_crawler()
