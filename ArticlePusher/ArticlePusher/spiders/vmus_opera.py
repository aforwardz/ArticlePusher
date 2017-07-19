# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class VmusSpider(scrapy.Spider):
    name = 'vmus_opera'
    allowed_host = 'vmus.co'
    start_urls = [
        'https://vmus.co/'  # vmus
    ]
    headers = {
        ':authority': 'vmus.co',
        ':method': 'GET',
        ':path': '/',
        ':scheme': 'https',
        'referer': 'https://vmus.co/',
        'upgrade-insecure-requests': '1'
    }
    cookies = {
        'Hm_lpvt_32cba912b39cf52427cbd63049b1bbe6': '1500455728',
        'Hm_lvt_32cba912b39cf52427cbd63049b1bbe6': '1500454514,1500455000,1500455008',
        '__atuvc': '4%7C29',
        '__atuvs': '596f1e7239c9aa94003',
        '__cfduid': 'd0012cd0697289e531c53856f9f5451df1500454502',
        '_ga': 'GA1.2.1991679120.1500454514',
        '_gid': 'GA1.2.2079849184.1500454514',
        'cf_clearance': '371beb2918e057fc63f0853a287958025c5fa814'
    }
    compare_xpath = '//div[@id="wrap"]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                cookies=self.cookies,

                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
        return
        if article_handler.article_update(response, self.compare_xpath):
            opera_titles = response.xpath('//article[@class="post"]//h2/a/span/text()').extract()
            opera_links = response.xpath('//article[@class="post"]//h2/a/@href').extract()
            assert len(opera_titles) == len(opera_links), '文章标题数与连接数不匹配'
            opera_dicts = dict((x, y) for x, y in zip(opera_titles, opera_links))
            vmus = PusherGenerator()
            vmus.save_today_new_articles(self.name, opera_dicts)
