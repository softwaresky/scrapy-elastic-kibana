import sys
import os
import datetime
from twisted.internet import reactor
from twisted.internet.task import deferLater

this_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if this_dir not in sys.path:
    sys.path.append(this_dir)

from eTechStore.spiders import anhochSpider, setecSpider, netpunSpider, productDetailsSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from eTechStore import general

dict_settings = {

    # "HTTPCACHE_ENABLED": True,
    # "HTTPCACHE_DIR": os.path.join(general.OUTPUT_DIR, "httpcache"),
    "DB_URL": general.DB_URL

}

def sleep(*args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)

def _crawl(result, spider):
    deferred = process.crawl(spider)
    deferred.addCallback(lambda results: print(f'{str(datetime.datetime.now()).split(".")[0]} [{spider.name}] waiting 20 seconds before restart...'))
    deferred.addCallback(sleep, seconds=20)
    deferred.addCallback(_crawl, spider)
    return deferred

if __name__ == '__main__':

    project_settings = get_project_settings()
    project_settings.update(dict_settings)
    process = CrawlerProcess(project_settings)

    _crawl(None, anhochSpider.AnhochSpider)
    _crawl(None, setecSpider.SetecSpider)
    _crawl(None, netpunSpider.NetpunSpider)
    _crawl(None, productDetailsSpider.ProductDetailsSpider)

    # process.crawl(anhochSpider.AnhochSpider)
    # process.crawl(setecSpider.SetecSpider)
    # process.crawl(netpunSpider.NetpunSpider)
    process.start()  # the script will block here until all crawling jobs are finished
