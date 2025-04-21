import json, csv
from scrapy.http import Request
from sortedcontainers import SortedDict
from scrapy.spiders import XMLFeedSpider

from crawlers.items import ArticleItem

URLS_PATH='urls-kikar.csv'

multi_words_phrases_path = "../multi-words-phrases.txt"
translated_words_path = "../translated_words.json"

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
    name = 'kikar_spider_comments'
    allowed_domains = ['www.kikar.co.il', 'a.kikar.co.il']
    itertag = 'Result'

    urls_counter = 0

    def __init__(self, *args, **kwargs):
        super(KikarSpider, self).__init__(*args, **kwargs)
        self.comments_dict = {}
        self.translated_dict = {}

        with open(translated_words_path, 'r', encoding='utf-8') as file:
            self.translated_words = json.load(file)
        for word_data in self.translated_words.get('כיכר השבת', {}).get('טוקבקים', []):
            self.translated_dict[word_data['English']] = set(word_data['Hebrew'])
            self.comments_dict[word_data['English']] = []

    def start_requests(self):
        for article_url in open(URLS_PATH, 'r'):
            article_url = article_url.strip()
            id = article_url.split('/')[-1].split('.')[0]
            url = f'https://a.kikar.co.il/v2/articles/{id}'

            yield Request(url=url, callback=self.parse_article)

    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 0,
        'HTTPERROR_ALLOWED_CODES': [302],
    }


    def parse_article(self, response):
        data = json.loads(response.text)
        new_id = data['id']  # Assuming the JSON response structure includes an 'id' field
        comments_url = f'https://a.kikar.co.il/v2/articles/{new_id}/comments'
        yield Request(url=comments_url, callback=self.parse_comments)


    def parse_comments(self, response):
        item = ArticleItem()
        self.urls_counter += 1
        item['id'] = str(self.urls_counter)

        kikar_article_id = response.url.split('=')[-1]
        item['url'] = f'https://www.kikar.co.il/{kikar_article_id}.html'
        item['source'] = self.source_name

        comments = self.get_comments(response)

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
    

    def get_comments(self, response):
        comments_data = json.loads(response.text)
        comments = [comment['content'] for comment in comments_data]

        return comments

    def closed(self, reason):
        with open('kikar_comments_output_3.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for english_word, data in self.comments_dict.items():
                writer.writerow([english_word, *data])