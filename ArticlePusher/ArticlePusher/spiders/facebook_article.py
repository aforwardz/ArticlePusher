# coding: utf-8
import scrapy


class FacebookSpider(scrapy.Spider):
    name = 'facebook'
    allowed_host = 'facebook.com'
    start_urls = [
        'https://code.facebook.com/'  # facebook
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
