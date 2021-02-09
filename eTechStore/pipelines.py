# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import datetime
import time
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from eTechStore.elastic_search_lib import ElasticSearchAPI
from eTechStore.db_api import SqlAlchemy
import pprint

from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse

def is_floats_equal(f1, f2, threshold=0.0001):
    return abs(f1 - f2) <= threshold

class ElasticSearchPipeline(object):

    def __init__(self):
        self.elastic_search_api = ElasticSearchAPI()
        self.db_api = SqlAlchemy()

    def open_spider(self, spider):
        # self.elastic_search_api = ElasticSearchAPI()
        # self.db_api = SqlAlchemy()
        pass

    def process_item(self, item, spider):

        dict_item = ItemAdapter(item).asdict()
        if dict_item:
            # dict_item["timestamp"] = f"{datetime.datetime.now()}".split(".")[0]
            dict_item["@timestamp"] = datetime.datetime.now()
            dict_item["timestamp_int"] = time.time()
            dict_price_ = {"value": dict_item["price"], "@timestamp": dict_item["@timestamp"]}

            product_id = dict_item["id"]
            # url = dict_item["url"]

            self.db_api.transfer_url(dict_item["url"])

            if self.elastic_search_api.is_product_exists_by_id(product_id):
                dict_product_ = self.elastic_search_api.get_product_by_id(product_id)
                if dict_product_:
                    lst_price_history = dict_product_["price_history"]
                    if lst_price_history:
                        if is_floats_equal(dict_item["price"], lst_price_history[-1]["value"]):
                            # raise DropItem("Duplicate item found: {0}".format(dict_item["id"]))
                            pass
                        else:
                            lst_price_history.append(dict_price_)

                            self.elastic_search_api.update_product(product_id, dict_data={"price_history": lst_price_history,
                                                                                          "price": dict_item["price"],
                                                                                          "@timestamp": dict_item["@timestamp"]
                                                                                          })
            else:
                dict_product = dict_item.copy()
                dict_product["price_history"] = [dict_price_]
                res = self.elastic_search_api.insert_data(id=product_id, dict_data=dict_product)

            # self.elastic_search_api.refresh()

        return item

    def close_spider(self, spider):
        # self.elastic_search_api.es.close()
        pass

class UrlManagerPipeline(object):

    def __init__(self):
        self.db_api = SqlAlchemy()
        pass

    def open_spider(self, spider):
        # self.db_api = SqlAlchemy()
        pass

    def process_item(self, item, spider):
        self.db_api.insert_new_urls(dict(item))
        return item

    def close_spider(self, spider):
        pass

class MyImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        return os.path.basename(urlparse(request.url).path)