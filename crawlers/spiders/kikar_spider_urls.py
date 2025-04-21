from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import dateutil.parser
from datetime import datetime

from crawlers.items import UrlItem

start_date = datetime.strptime("10/2021", "%m/%Y")
end_date = datetime.strptime("08/2022", "%m/%Y")

class KikarSpider(CrawlSpider):
    source_name = 'kikar'
    name = 'kikar_spider_urls'
    allowed_domains = ['www.kikar.co.il']
    start_urls = ['https://www.kikar.co.il/499/427707']

    urls_counter = 0

    rules = (
        Rule(LinkExtractor(
            allow=r'https:\/\/www\.kikar\.co\.il$'), follow=True),
        Rule(LinkExtractor(
            allow=r'https:\/\/www\.kikar\.co\.il\/([A-Za-z0-9-%]+)$'), follow=True),
        Rule(LinkExtractor(
            allow=r'https:\/\/www\.kikar\.co\.il\/(authors|magazines)\/[a-zA-Z0-9]{6,10}$'), follow=True),
        Rule(LinkExtractor(
            allow=r'https:\/\/www\.kikar\.co\.il\/(([A-Za-z0-9-]+)\/)+[a-zA-Z0-9]{6,10}$'), callback='parse_article', follow=True),
        Rule(LinkExtractor(
            allow=r'https:\/\/www\.kikar\.co\.il\/.*$'), follow=True),
    )

    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 0,
    }

    def parse_article(self, response):
        item = UrlItem()
        item['url'] = response.url

        try:
            date_str = response.xpath('//meta[@name="article:published_time"]/@content').get().strip()
            date = dateutil.parser.isoparse(date_str).replace(tzinfo=None)
            
            if start_date <= date <= end_date:
                yield item
        except Exception as exc:
            print(exc)
            pass