# -*- coding: utf-8 -*-
import scrapy
import urllib.parse


class GetRecentlyUpdatedCompaniesSpider(scrapy.Spider):
    name = 'get-recently-updated-companies'
    allowed_domains = ['reviewcongty.com']
    start_urls = ['https://reviewcongty.com/']

    def parse(self, response):
        review_list = response.xpath('//section[@class="summary-reviews column z-1"]/div[@class="review"]')
        for review in review_list:
            company_url = review.xpath('./h3//a/@href').get()
            yield {
                'id': company_url.split('/')[-1],
                'url': urllib.parse.urljoin('https://reviewcongty.com/', company_url)
            }
