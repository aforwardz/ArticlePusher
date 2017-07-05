# coding: utf-8
import scrapy


class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_host = 'googleblog.com'
    start_urls = [
        'https://opensource.googleblog.com/'  # googleblog
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
