# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ETechStoreItem(scrapy.Item):

    id = scrapy.Field()
    brand = scrapy.Field()
    product_name = scrapy.Field()
    categories_path = scrapy.Field()
    price = scrapy.Field()
    discount_price = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    market_name = scrapy.Field()

class UrlItem(scrapy.Item):

    url = scrapy.Field()

