# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


#class ScrapyDcaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
#    pass

class PhysicianItem(Item):

    timestamp = Field()  #scrape time
    source = Field()     #eg CA medical board
    name = Field()
    prev_name = Field()
    license = Field()
    license_type = Field()
    issue_date = Field()
    exp_date = Field()
    status1 = Field()
    status2 = Field()
    school = Field()
    graduation = Field()
    address = Field()

    # THE FOLLOWING INFORMATION IS SELF-REPORTED BY THE LICENSEE AND HAS NOT BEEN VERIFIED BY THE BOARD
    practice_location = Field()
    services = Field()
    certifications = Field()
    ethnicity = Field()
    language = Field()
    gender = Field()
    scraped_at = Field()
