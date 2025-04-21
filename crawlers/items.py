# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ArticleItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    author = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    day = scrapy.Field()
    comments_count = scrapy.Field()

    title_words_count = scrapy.Field()
    title_words_dict = scrapy.Field()

    subtitle_words_count = scrapy.Field()
    subtitle_words_dict = scrapy.Field()

    content_words_count = scrapy.Field()
    content_words_dict = scrapy.Field()

    comments_words_count = scrapy.Field()
    comments_words_dict = scrapy.Field()
    pass
class UrlItem(scrapy.Item):
    url = scrapy.Field()
    pass
