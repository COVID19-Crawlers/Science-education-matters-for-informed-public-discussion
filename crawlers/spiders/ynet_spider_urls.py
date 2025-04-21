from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import dateutil.parser
from datetime import datetime

from crawlers.items import UrlItem

start_date = datetime.strptime("10/2021", "%m/%Y")
end_date = datetime.strptime("08/2022", "%m/%Y")

class YnetSpider(CrawlSpider):
    source_name = 'ynet'
    name = 'ynet_spider_urls'
    allowed_domains = ['www.ynet.co.il']
    start_urls = ['https://www.ynet.co.il/home/0,7340,L-8,00.html']
    urls_counter = 0

    rules = (
        Rule(LinkExtractor(allow=r'https:\/\/www\.ynet\.co\.il\/home\/0,7340,L-8,00.html'), follow=True),
        Rule(LinkExtractor(allow=r'https:\/\/www\.ynet\.co\.il\/([A-Za-z-]+)$'), follow=True),
        Rule(LinkExtractor(allow=r'https:\/\/www\.ynet\.co\.il\/(([A-Za-z-]+)\/)+[0-9]{1,10}$'), follow=True),
        Rule(LinkExtractor(allow=r'https:\/\/www\.ynet\.co\.il\/(([A-Za-z-]+)\/)+([A-Za-z-]+)$'), follow=True),
        Rule(LinkExtractor(allow=r'https:\/\/www\.ynet\.co\.il\/(([A-Za-z-]+)\/)+article\/[a-zA-Z0-9]{8,10}$'), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'https:\/\/www\.ynet\.co\.il\/.*$'), follow=True),
    )

    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 0,
    }

    def parse_article(self, response):
        item = UrlItem()
        item['url'] = response.url

        if not response.xpath('/html/body/nav/div/div/div').get():
            date_str = response.xpath('//meta[@property="article:published_time"]/@content').get().strip()
            date = dateutil.parser.isoparse(date_str).replace(tzinfo=None)
            
            if start_date <= date <= end_date:
                yield item

