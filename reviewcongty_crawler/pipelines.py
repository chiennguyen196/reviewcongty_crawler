# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from items import Company, Review

class ReviewcongtyCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.company_urls_seen = set()
        self.reviews_id_seen = set()

    def process_item(self, item, spider):
        if isinstance(item, Company):
            url = item['url']
            if url in self.company_urls_seen:
                raise DropItem("Duplicate item for company {}".format(item["name"]))
            else:
                self.company_urls_seen.add(url)
                return item
        elif isinstance(item, Review):
            id = item['review_id']
            if id in self.reviews_id_seen:
                raise DropItem("Duplicate item for review {}".format(id))
            else:
                self.reviews_id_seen.add(id)
                return item
        else:
            return item
