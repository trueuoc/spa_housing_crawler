# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class House(scrapy.Item):

    # Location Features
    loc_street = scrapy.Field()
    loc_city = scrapy.Field()
    loc_zone = scrapy.Field()

    # Price
    price = scrapy.Field()

    # House Properties
    lift = scrapy.Field()
    bath_num = scrapy.Field()