# coding: utf-8
import scrapy


class LinkdinSpider(scrapy.Spider):
    name = 'linkedin'
    allowed_host = 'linkedin.com'
    start_urls = [
        'https://engineering.linkedin.com/'  # linkedin
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
