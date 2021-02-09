# -*- coding: utf8 -*-
import json
import pprint
import time
import uuid
from eTechStore import general
from scrapy.utils.project import get_project_settings
import os
from elasticsearch import Elasticsearch
import datetime
import os
import hashlib

class ElasticSearchAPI:

    def __init__(self, index_name=""):
        self.es_hosts = os.environ.get("ELASTICSEARCH_HOSTS", None)
        self.es = Elasticsearch(self.es_hosts, timeout=500)
        # self.index_name = "e-tech-store"
        self.index_name = index_name if index_name else os.environ.get("ELASTIC_SEARCH_INDEX_NAME", "e-tech-store")
        self._connect_to_elasticsearch()

    def _connect_to_elasticsearch(self):

        while self.es and not self.es.ping():
            self.es = Elasticsearch(self.es_hosts)
            print (self.es)
            time.sleep(0.5)

    def insert_data(self, id, dict_data):
        res = self.es.index(index=self.index_name, id=id, body=dict_data)
        return res

    def refresh(self):
        self.es.indices.refresh(index=self.index_name)

    def get_product_by_id(self, id):
        res = self.es.get(index=self.index_name, id=id)
        return res['_source']

    def get_products_by_market(self, market_name=""):
        res = self.es.search(index=self.index_name,
                             body={
                                    "query": {
                                        "match_phrase": {
                                            "market_name": market_name
                                        }
                                    }

                                  },
                             size=10000
                             )
        return res['hits']['hits']
        # return res

    def get_data_test(self, market_name=""):
        dict_query = {
                        "match_phrase": {
                            "market_name": market_name
                        }
                    }
        # res = self.es.search(index=self.index_name, body={ "query": dict_query}, size=10000)
        res = self.es.count(index=self.index_name, body={ "query": dict_query})

        return res["count"]

    def update_product(self, id="", dict_data = {}):
        if id:
            res = self.es.update(index=self.index_name, id=id, body={"doc": dict_data})
            # print (res)

    def is_product_exists_by_url(self, product_url=""):

        res = self.es.count(index=self.index_name,
                            body={
                                "query": {
                                    "match_phrase":{
                                        "url": product_url
                                    }
                                }
                            })

        return res["count"] > 0

    def is_product_exists_by_id(self, product_id):
        return self.es.exists(index=self.index_name, id=product_id)

    def remove_index(self):
        self.es.indices.delete(index=self.index_name, ignore=[400, 404])

    def insert_from_json(self, json_file="", do_remove_index=False):
        print("insert_from_json() ...")
        print(json_file)

        if json_file:

            if do_remove_index:
                self.remove_index()

            lst_data = []
            with open(json_file, 'r', encoding='utf8') as file_:
                for line_ in file_.readlines():
                    dict_product_ = json.loads(line_.strip())
                    # dict_product_["id"] = str(uuid.uuid4())
                    lst_data.append(dict_product_)

            # key = (dict_product_["market_name"], dict_product_["brand"], dict_product_["product_name"])

            lst_data.sort(key=lambda item_: (item_["market_name"], item_["brand"], item_["product_name"]))
            total = len(lst_data)
            for i in range(total):
                dict_data_ = lst_data[i]
                dict_data_.pop("id")

                price = dict_data_["price"]
                if isinstance(price, str):
                    price = price.replace(",", "")
                    if price.isdigit():
                        dict_data_["price"] = float(price)

                dict_data_["description"] = dict_data_["description"].replace("\n\n", "\n").replace("\n", ".")
                self.insert_data(id=i, dict_data=dict_data_)

                general.print_progress_bar(iteration=i, total=total)


def fill_elastic_search():
    elastic_search_api = ElasticSearchAPI()
    json_file = ""
    data_dir = os.path.join(general.OUTPUT_DIR, "data")
    if data_dir and os.path.exists(data_dir):
        lst_item = os.listdir(data_dir)
        if lst_item:
            json_file = os.path.join(data_dir, max(lst_item))
            elastic_search_api.insert_from_json(json_file=json_file, do_remove_index=True)

def elastic_search_examples():

    elastic_search_api = ElasticSearchAPI()

    # total_count = 0
    # total_hit = 0

    # result = elastic_search_api.es.search(index=elastic_search_api.index_name,
    #                          body={},
    #                          size=10000
    #                          )
    #
    # lst_product = result['hits']['hits']

    dict_group_by_market = {}

    # {'anhoch': 3610, 'neptun': 2548, 'setec': 3842}


    for market_ in ["anhoch", "neptun", "setec"]:
        print ("Market: ",market_)
        rbr = 0

        lst_product = elastic_search_api.get_products_by_market(market_)
        if lst_product:
            totals = len(lst_product)
            for dict_data_ in lst_product:
                data = dict_data_["_source"]
                product_name = data["product_name"].replace("Лаптоп", "").replace("Notebook", "").strip()
                # elastic_search_api.update_product(id=dict_data_["_id"], dict_data = {"brand": data["brand"].title()})
                elastic_search_api.update_product(id=dict_data_["_id"], dict_data = {"product_name": product_name})

                rbr += 1

                print (f"{market_}: {rbr} / {totals}")

            # pprint.pprint(lst_product[0])
            # print (product_url, elastic_search_api.is_product_exists_by_url(product_url))
            # print (_id, elastic_search_api.is_product_exists_by_id(_id))
    #     lst_item = result["hits"]["hits"]
    #     total_count += len(lst_item)
    #     total_hit += result["hits"]["total"]["value"]

    # result = elastic_search_api.get_data_test("anhoch")
    # result = elastic_search_api.get_data_test("setech")
    # result = elastic_search_api.get_data_test("neptun")
    # lst_item = result["hits"]["hits"]
    # total = result["hits"]["total"]["value"]
    # print ("total: {0}".format(total))
    # print ("Count: {0}".format(len(lst_item)))

    # print (f"total_count: {total_count}")
    # print (f"total_hit: {total_hit}")


    pass

def elastic_search_update():
    elastic_search_api = ElasticSearchAPI()
    id = 'setech-62080'
    dict_data = {"description": "", "prices": [{'timestamp': '2020-10-26 01:01:01', 'value': 200.0}]}

    elastic_search_api.update_product(id, dict_data)

    pprint.pprint(elastic_search_api.get_product_by_id(id))

def elastic_search_remove_index():
    elastic_search_api = ElasticSearchAPI()
    elastic_search_api.remove_index()

def main():

    # es_api = ElasticSearchAPI()
    # es_api.remove_index()

    # fill_elastic_search()
    elastic_search_examples()
    # elastic_search_remove_index()
    # elastic_search_update()
    pass

if __name__ == '__main__':
    main()