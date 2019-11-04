# -*- coding: utf-8 -*-
import logging
import pymongo
logger=logging.getLogger(__name__)
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class OilPipeline(object):
    def process_item(self, item, spider):
        if item['url'] and item['text'] and item['time']:
            return item
        else:
            logging.warning("有空值！")

class MongoPipeline(object):
    def __init__(self,mongo_url,mongo_db):
        self.mongo_url=mongo_url
        self.mongo_db=mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self,spider):
        self.client=pymongo.MongoClient(self.mongo_url)
        self.db=self.client[self.mongo_db]

    def process_item(self,item,spider):
        name=item.__class__.__name__
        try:
            check_url=item['url']
            if not self.db[name].find_one({'url':check_url}):
                self.db[name].insert(dict(item))
            else:
                logging.warning("this url already exist")
        except:
            pass #'NoneType' object is not subscriptable
        return item

    def close_spider(self,spider):
        self.client.close()