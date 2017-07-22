# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class TtmeijuSpider(scrapy.Spider):
    name = 'ttmeiju_opera'
    allowed_host = 'ttmeiju.com'
    proxy = False
    start_urls = [
        'http://www.ttmeiju.com/latest-0.html'  # ttmeiju
    ]
    compare_xpath = '//table[@class="latesttable"]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        if article_handler.article_update(response, self.compare_xpath):
            opera_titles = response.xpath('//tr//td[@align="left"]/a/@title').extract()
            opera_links = response.xpath('//tr//td[@align="left"]/a/@href').extract()
            assert len(opera_titles) == len(opera_links), '文章标题数与连接数不匹配'
            opera_links = list([response.urljoin(url) for url in opera_links])
            opera_dicts = dict((x, y) for x, y in zip(opera_titles, opera_links))
            ttmeiju = PusherGenerator()
            ttmeiju.save_today_new_articles('opera', self.name, opera_dicts)