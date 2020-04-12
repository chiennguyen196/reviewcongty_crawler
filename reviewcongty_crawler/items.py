# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewcongtyCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Company(scrapy.Item):
    image_logo = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    slug = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    company_type = scrapy.Field()
    size = scrapy.Field()
    address = scrapy.Field()

class Review(scrapy.Item):
    name = scrapy.Field()
    position = scrapy.Field()
    rating = scrapy.Field()
    created = scrapy.Field(serializer=str)
    content = scrapy.Field()
    num_likes = scrapy.Field()
    num_dislikes = scrapy.Field()
    num_delete_requests = scrapy.Field()
    replies = scrapy.Field()
