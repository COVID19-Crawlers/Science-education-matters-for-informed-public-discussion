import json, csv
from scrapy.http import FormRequest
from sortedcontainers import SortedDict
from scrapy.spiders import CrawlSpider

import requests
import re
from crawlers.items import ArticleItem

URLS_PATH='urls-ynet.csv'

multi_words_phrases_path = "../multi-words-phrases.txt"
translated_words_path = "../translated_words.json"

REMOVAL_STRINGS = [",", ":", "(", ")", ".", " \"", "\" ", " ,\"", "\", ",
                   " :\"", "\": ", "' ", " '", "?", "!", "<br />", "<br/>", "\n"]
QUOTATION = ["\"", "'"]

NEW_FORMAT = r'https:\/\/www\.ynet\.co\.il\/(([A-Za-z]+)\/)+article\/[a-zA-Z0-9]{8,10}'
OLD_FORMAT = r'https:\/\/www\.ynet\.co\.il\/articles\/0,7340,L-(?!3369891)([0-9]{7}),00\.html'


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

class YnetSpider(CrawlSpider):
    source_name = 'ynet'
    name = 'ynet_spider_comments'
    allowed_domains = ['www.ynet.co.il']

    urls_counter = 0

    def __init__(self, *args, **kwargs):
        super(YnetSpider, self).__init__(*args, **kwargs)
        self.comments_dict = {}
        self.translated_dict = {}

        with open(translated_words_path, 'r', encoding='utf-8') as file:
            self.translated_words = json.load(file)
        for word_data in self.translated_words.get('Ynet', {}).get('טוקבקים', []):
            self.translated_dict[word_data['English']] = set(word_data['Hebrew'])
            self.comments_dict[word_data['English']] = []


    def start_requests(self):
        for url in open(URLS_PATH, 'r'):
            url = url.strip()

            if re.search(NEW_FORMAT, url):
                yield FormRequest(url, callback=self.parse_new_format_article)

            if re.search(OLD_FORMAT, url):
                yield FormRequest(url, callback=self.parse_old_format_article)

    custom_settings = {
        'REDIRECT_ENABLED': False,
        'CLOSESPIDER_PAGECOUNT': 0,
    }

    def parse_new_format_article(self, response):
        item = ArticleItem()
        self.urls_counter += 1
        item['id'] = str(self.urls_counter)
        item['url'] = response.url
        item['source'] = self.source_name

        comments = self.get_new_format_comments(response.url)

        self.update_comments_dict(comments)

        yield item

    def parse_old_format_article(self, response):
        item = ArticleItem()
        self.urls_counter += 1
        item['id'] = str(self.urls_counter)
        item['url'] = response.url
        item['source'] = self.source_name

        comments = self.get_old_format_comments(response.url)

        self.update_comments_dict(comments)

        yield item

    def update_comments_dict(self, comments):
        for comment in comments:
            clean_comment = self.get_clean_comment(comment)

            for english, translations in self.translated_dict.items():
                if any(t in clean_comment for t in translations): 
                    self.comments_dict[english].append(comment)


    def get_clean_comment(self, content):
        clean_content = str(content)
        if content.isspace() or clean_content == '':
            return ''

        if clean_content[0] in QUOTATION:
            clean_content = clean_content[1:]

        if clean_content[-1] in QUOTATION:
            clean_content = clean_content[0:-1]

        for str1 in REMOVAL_STRINGS:
            clean_content = clean_content.replace(str1, " ")

        return clean_content

    def get_new_format_comments(self, url):
        article_id = url.split('/')[-1]
        comments_json_url = f'https://www.ynet.co.il/iphone/json/api/talkbacks/list/{article_id}/end_to_start/1'
        comments_json = requests.get(url=comments_json_url).json()
        comments = []

        if 'rss' in comments_json and 'channel' in comments_json['rss'] and 'item' in comments_json['rss']['channel']:
            comments = ['. '.join([x['title'], x['text']])
                        for x in comments_json['rss']['channel']['item']]

        return comments

    def get_old_format_comments(self, url):
        article_id = url.split('-')[-1].split(',')[0]
        comments_json_url = f'https://www.ynet.co.il/Ext/Comp/ArticleLayout/Proc/ShowTalkBacksAjax/v2/0,12990,L-{article_id}-desc-68-0-0,00.html'
        comments_json = requests.get(url=comments_json_url).json()
        comments = []

        if 'rows' in comments_json:
            comments = ['. '.join([x['title'], x['text']])
                        for x in comments_json['rows']]

        return comments
    
    def closed(self, reason):
        with open('ynet_comments_output_3.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for english_word, data in self.comments_dict.items():
                writer.writerow([english_word, *data])
