# coding: utf-8
import os
from datetime import datetime
from ArticlePusher import settings
import hashlib
from .utils import BloomInstance
import json


def save_updated_articles(response, file_path):
    hash_md5 = hashlib.md5()
    hash_md5.update(response.url.encode())
    file_name = hash_md5.hexdigest()
    data = dict(
        html=response.text,
        url=response.url,
        base_url=response.meta.get('base_url'),
        release_time = response.meta.get('release_time'),
        # attachment=file_name
    )
    with open(os.path.join(file_path, file_name), 'w') as f:
        json.dump(data,f)
        # f.write(response.text)
    return file_name


def article_update(response, selectors, use_bloom=settings.USE_BLOOM):
    '''
    对传入的对象进行判重，重复的跳过，不重复的保存
    :param response: response 对象
    :param selectors: 判重用的选择器
    :return: 页面文章是否更新
    '''
    if use_bloom:
        bf = BloomInstance
        content = ''
        if selectors:   # 判断是否传入selectors
            # html = etree.HTML(response.text)
            for selector in selectors:
                try:
                    cont = str(response.xpath(selector).extract_first())
                    # cont = str(html.xpath(selector)[0].xpath('string(.)'))
                except:
                    cont = ''
                content += cont
            if len(content) < 5:
                content_hash = hashlib.md5(response.body).hexdigest()
            else:
                content_hash = hashlib.md5(content.encode()).hexdigest()
        else:           # 如果没有传入selectors则直接用整个html做hash
            content_hash = hashlib.md5(response.body).hexdigest()

        if bf.isContains(content_hash, settings.REDIS_DB):  # 判断content_hash是否存在
            return False
        else:           # 如果不存在则添加并保存
            bf.insert(content_hash, settings.REDIS_DB)
            return True

    else:
        return True
