# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class DabappsSpider(scrapy.Spider):
    name = 'dabapps_tech'
    allowed_host = 'dabapps.com'
    start_urls = [
        'https://www.dabapps.com/blog/'  # dabapps
    ]
    compare_xpath = '//div[@class="container"]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        if article_handler.article_update(response, self.compare_xpath):
            article_titles = response.xpath('//div[@class="col-sm-9"]//h2/a/text()').extract()
            article_links = response.xpath('//div[@class="col-sm-9"]//h2/a/@href').extract()
            assert len(article_titles) == len(article_links), '文章标题数与连接数不匹配'
            article_links = list([response.urljoin(url) for url in article_links])
            article_dicts = dict((x, y) for x, y in zip(article_titles, article_links))
            amazon = PusherGenerator()
            amazon.save_today_new_articles(self.name, article_dicts)
