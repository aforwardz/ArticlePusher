# coding: utf-8
import scrapy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_host = 'instagram.com'
    start_urls = [
        'https://engineering.instagram.com/'  # instagram
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
