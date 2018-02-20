# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


#class ScrapyDcaPipeline(object):
#    def process_item(self, item, spider):
#    return item

from scrapy.exporters import JsonItemExporter

class JsonPipeline(object):

    file = None

    def open_spider(self, spider):
        self.file = open('/code/item.json', 'w')
        self.exporter = JsonItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
