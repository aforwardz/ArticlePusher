#!/bin/sh
celery -B -A ArticlePusher worker -Q crawl -l info
