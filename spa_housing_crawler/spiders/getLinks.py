# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import os
import pandas as pd
from datetime import datetime as dt
from spa_housing_crawler.items import Link

sys.path.append(os.getcwd()+'/spa_housing_crawler')

# Global declarations
default_url = 'http://idealista.com'
saved = []
seen = []
zones = []
selling_flag = True  # True: Selling ; False: Renting

class GetLinks(scrapy.Spider):
    name = 'getLinks'
    allowed_domains = ['idealista.com']

    def __init__(self, start):
        self.start_urls = [start]

        all_zones = pd.read_csv('./additional_csv/zones.csv')
        zones.extend(all_zones['zone'])

        try:
            # -*- Load links dataframe -*-
            exclude = [i for i, line in enumerate(open('./additional_csv/links.csv')) if line.startswith('link')]
            if len(exclude) is 1:
                all_links = pd.read_csv('./additional_csv/links.csv')
            else:
                all_links = pd.read_csv('./additional_csv/links.csv', skiprows=exclude[1:])

            saved.extend(all_links['link'])

        except Exception as e:
            print(e)

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse(self, response):

        # -*- When extracting denied links, if it is a subzone link, go to 'parse_subzones'
        if self.start_urls[0] not in zones:
            yield response.follow(self.start_urls[0], callback=self.parse_subzones)

        else:
            # -*- Get province name -*-
            try:
                province = (response.xpath("//div[@class='full-width-background']/div/ul/li[2]/a/@href")
                            .extract()[0].split('/')[2].replace('-',' ').split(' provincia')[0].lower().strip())
            except:
                province = (response.xpath("//span[@class='breadcrumb-title icon-arrow-dropdown-after']/text()")
                            .extract()[0].split(" provincia")[0].lower().strip())

            try:
                house_num = get_number(response.xpath("//a[@id='showAllLink']/text()").extract()[0])

                # -*- Extract link directly if are less than 2000 houses -*-
                if house_num < 2000:

                    # Check if the link is registered already
                    this_link = default_url + response.xpath("//a[@id='showAllLink']/@href").extract()[0]
                    if this_link not in saved:
                        link = Link()
                        link['link'] = this_link
                        link['num_link'] = house_num
                        link['province'] = province
                        link['obtention_date'] = dt.now().date()
                        yield link
                        saved.extend(this_link)

                # -*- Get unseen from map -*-
                else:
                    zone_paths = response.xpath("//map[@id='map-mapping']/area/@href").extract()
                    for i in range(len(zone_paths)):
                        zone_paths[i] = default_url + zone_paths[i]

                    # discard all the adjacent provinces links that are not part of the zone we are dealing with
                    for path in zones:
                        if path in zone_paths: zone_paths.remove(path)

                    # discard all the zones that are previously saved
                    for path in saved:
                        if path in zone_paths: zone_paths.remove(path)

                    # discard all the zones that are previously seen
                    for path in saved:
                        if path in zone_paths: zone_paths.remove(path)
                    seen.extend(zone_paths)


                    for zone in zone_paths:
                        yield response.follow(zone, callback=self.parse_subzones)

            # -*- Already in the houses list -*-
            except Exception as e:

                # Check if the link is registered already
                this_link = (default_url + response.xpath("//div[@class='fixed-toolbar-controls']/a/@href")
                                .extract()[0])
                if this_link not in saved:
                    link = Link()
                    link['link'] = this_link
                    link['num_link'] = get_number(response.xpath("//div[@id='h1-container']/h1/text()").extract()[0])
                    link['province'] = province
                    link['obtention_date'] = dt.now().date()
                    yield link
                    saved.extend(this_link)

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse_subzones(self, response):

        # -*- Get province name -*-
        try:
            province = (response.xpath("//div[@class='full-width-background']/div/ul/li[2]/a/@href")
                .extract()[0].split('/')[2].replace('-',' ').split(' provincia')[0].lower().strip())
        except:
            province = (response.xpath("//div[@class='breadcrumb-geo wrapper clearfix']/ul/li[2]/a/@href")
                        .extract()[0].split('/')[2].replace('-',' ').split(' provincia')[0].lower().strip())

        try:
            house_num = get_number(response.xpath("//a[@id='showAllLink']/text()").extract()[0])

            # -*- Extract path directly if are less than 2000 houses -*-
            if house_num < 2000:

                # Check if the link is registered already
                this_link = default_url + response.xpath("//a[@id='showAllLink']/@href").extract()[0]
                if this_link not in saved:
                    link = Link()
                    link['link'] = this_link
                    link['num_link'] = house_num
                    link['province'] = province
                    link['obtention_date'] = dt.now().date()
                    yield link
                    saved.extend(this_link)


            # -*- Get unseen from map -*-
            else:
                subzone_paths = response.xpath("//map[@id='map-mapping']/area/@href").extract()
                for i in range(len(subzone_paths)):
                    subzone_paths[i] = default_url + subzone_paths[i]

                # discard all the adjacent provinces links that are not part of the zone we are dealing with
                for path in zones:
                    if path in subzone_paths: subzone_paths.remove(path)

                # discard all the zones that are previously saved
                for path in saved:
                    if path in subzone_paths: subzone_paths.remove(path)

                # discard all the zones that are previously seen
                for path in saved:
                    if path in subzone_paths: subzone_paths.remove(path)
                seen.extend(subzone_paths)

                for subzone in subzone_paths:
                    yield response.follow(subzone, callback=self.parse_subzones)

        # -*- Already in the houses list -*-
        except Exception as e:

            # Check if the link is registered already
            this_link = default_url + response.xpath("//div[@class='fixed-toolbar-controls']/a/@href").extract()[0]
            if this_link not in seen:
                link = Link()
                link['link'] = this_link
                link['num_link'] = get_number(response.xpath("//div[@id='h1-container']/h1/text()").extract()[0])
                link['province'] = province
                link['obtention_date'] = dt.now().date()
                yield link
                seen.extend(this_link)

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

def get_number(property):
    nums = re.findall(r'\d+', property)
    if len(nums) == 2:
        return int(nums[0]+nums[1])           # '40.000' ->   '40' + '000'  -> '40000'  ->  40000
    else:
        return int(nums[0])