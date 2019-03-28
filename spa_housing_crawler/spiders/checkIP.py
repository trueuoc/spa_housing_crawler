# -*- coding: utf-8 -*-
import scrapy
import sys, os

# -*- Checks your public IP when rotating proxies  -*-
# For running it -->   scrapy crawl checkIP

class checkIP(scrapy.Spider):
    name = 'checkIP'
    start_urls = ['http://checkip.dyndns.org/']

    sys.path.append(os.getcwd() + '/spa_housing_crawler')

    print(os.getcwd())

    def parse(self, response):
        pub_ip = response.xpath('//body/text()').re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')[0]
        print("My public IP is: " + pub_ip)
        yield response.follow('http://checkip.dyndns.org/', callback=self.parse)