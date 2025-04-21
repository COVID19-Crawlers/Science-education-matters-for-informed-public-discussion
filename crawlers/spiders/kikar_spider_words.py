import json
from scrapy.http import Request
from sortedcontainers import SortedDict
from scrapy.spiders import XMLFeedSpider
from datetime import datetime
from w3lib.html import remove_tags

from crawlers.pipelines import MultiCSVItemPipeline
from crawlers.items import ArticleItem


URLS_PATH='urls-test.csv'
URLS_PATH='kikar_urls_2024.csv'

multi_words_phrases_path = "../phrases.txt"

REMOVAL_STRINGS = [",", ":", "(", ")", ".", " \"", "\" ", " ,\"", "\", ",
                   " :\"", "\": ", "' ", " '", "?", "!", "<br />", "<br/>", "\n"]
QUOTATION = ["\"", "'"]


def get_multi_words_phrases():
    phrases = []

    with open(multi_words_phrases_path, 'rb') as f:
        for line in f.readlines():
            phrase = line[:-1].decode()

            for str1 in REMOVAL_STRINGS:
                phrase = phrase.replace(str1, " ")

            if not phrase.isspace() and phrase != '':
                phrases.append(phrase)

    return phrases


phrases = get_multi_words_phrases()


class KikarSpider(XMLFeedSpider):
    source_name = 'kikar'
    name = 'kikar_spider_words'
    allowed_domains = ['www.kikar.co.il', 'a.kikar.co.il']
    itertag = 'Result'

    urls_counter = 0

    def start_requests(self):
        for article_url in open(URLS_PATH, 'r'):
            article_url = article_url.strip()
            id = article_url.split('/')[-1].split('.')[0]
            url = f'https://a.kikar.co.il/v2/articles/{id}'

            yield Request(url=url, callback=self.parse_article, meta={'ur': article_url})

    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 0,
        'ITEM_PIPELINES': {
            MultiCSVItemPipeline: 300,
        }
    }


    def parse_article(self, response):
        data = json.loads(response.text)
        new_id = data['id']
        author = data['author']['name']
        title = data['title']
        subtitle = data['subTitle']

        # Convert Unix timestamp (in milliseconds) to datetime
        timestamp_ms = data['time']  # 'time' field in milliseconds
        date_time = datetime.fromtimestamp(timestamp_ms / 1000.0)
        year, month, day = date_time.year, date_time.month, date_time.day
        
        # Extract and clean HTML content parts
        content_parts = [remove_tags(part['html']) for part in data['content']['content'] if part['type'] == 'html']
        content = ' '.join(content_parts)
        
        comments_url = f'https://a.kikar.co.il/v2/articles/{new_id}/comments'
        
        # Pass data to the next method via the meta dictionary
        yield Request(url=comments_url, callback=self.parse_comments, meta={
            'article_id': new_id,
            'author': author,
            'title': title,
            'subtitle': subtitle,
            'year': year,
            'month': month,
            'day': day,
            'content': content,
            'ur': response.meta['ur']
        })

    def parse_comments(self, response):
        item = ArticleItem()
        self.urls_counter += 1
        item['id'] = str(self.urls_counter)

        item['url'] = response.meta['ur']
        item['source'] = self.source_name
        item['author'] = response.meta['author']
        item['year'] = str(response.meta['year'])
        item['month'] = str(response.meta['month'])
        item['day'] = str(response.meta['day'])

        title = response.meta['title']
        subtitle = response.meta['subtitle']
        content = response.meta['content']
        
        comments = self.get_comments(response)
        joined_comments = ' '.join(comments).strip()

        item['comments_count'] = len(comments)

        self._set_dicts(item, title, subtitle, content, joined_comments)

        yield item

    def _set_dicts(self, item, title, subtitle, content, comments):
        titles_dict = self.count_words_to_dict(title)
        subtitle_dict = self.count_words_to_dict(subtitle)
        content_dict = self.count_words_to_dict(content)
        comments_dict = self.count_words_to_dict(comments)

        item['title_words_count'] = len(titles_dict)
        item['title_words_dict'] = titles_dict

        item['subtitle_words_count'] = len(subtitle_dict)
        item['subtitle_words_dict'] = subtitle_dict

        item['content_words_count'] = len(content_dict)
        item['content_words_dict'] = content_dict

        item['comments_words_count'] = len(comments_dict)
        item['comments_words_dict'] = comments_dict

        pass

    def get_clean_words(self, content):
        clean_content = str(content)
        if content.isspace() or clean_content == '':
            return []

        if clean_content[0] in QUOTATION:
            clean_content = clean_content[1:]

        if clean_content[-1] in QUOTATION:
            clean_content = clean_content[0:-1]

        for str1 in REMOVAL_STRINGS:
            clean_content = clean_content.replace(str1, " ")

        return list(filter(lambda w: w not in ["-"], clean_content.split()))

    def merge_counter_dicts(self, counter_dict1, counter_dict2):
        counter_dict = counter_dict1.copy()
        for word in counter_dict2:
            if word not in counter_dict:
                counter_dict[word] = 0
            counter_dict[word] += 1

        return counter_dict

    def count_words_to_dict(self, text):
        if not isinstance(text, str):
            raise TypeError(
                f'text must be of type `str`, but got `{type(text)}`')

        counter_dict = SortedDict()
        words = self.get_clean_words(text)

        for word in words:
            if word not in counter_dict:
                counter_dict[word] = 0
            counter_dict[word] += 1

        for phrase in phrases:
            count_phrase = text.count(phrase)

            if count_phrase > 0:
                counter_dict[phrase] = count_phrase

        return counter_dict

    def get_comments(self, response):
        comments_data = json.loads(response.text)
        comments = [comment['content'] for comment in comments_data]

        return comments
