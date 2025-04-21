from scrapy.exporters import CsvItemExporter

class ArticleItemExporter(CsvItemExporter):
    def export_item(self, item):
        self.fields_to_export = ['id', 'url', 'source', 'author', 'year', 'month', 'day', 'comments_count']
        row = list(self._build_row(self.fields_to_export))
        self.csv_writer.writerow(row)

        fields = self._get_serialized_fields(item, default_value='', include_empty=True)
        row = list(self._build_row([x for _, x in fields]))
        self.csv_writer.writerow(row)

        row = list(self._build_row(['title_words_count', *item['title_words_dict'].keys()]))
        self.csv_writer.writerow(row)

        row = list(self._build_row([item['title_words_count'], *item['title_words_dict'].values()]))
        self.csv_writer.writerow(row)

        row = list(self._build_row(['subtitle_words_count', *item['subtitle_words_dict'].keys()]))
        self.csv_writer.writerow(row)

        row = list(self._build_row([item['subtitle_words_count'], *item['subtitle_words_dict'].values()]))
        self.csv_writer.writerow(row)

        row = list(self._build_row(['content_words_count', *item['content_words_dict'].keys()]))
        self.csv_writer.writerow(row)

        row = list(self._build_row([item['content_words_count'], *item['content_words_dict'].values()]))
        self.csv_writer.writerow(row)

        row = list(self._build_row(['comments_words_count', *item['comments_words_dict'].keys()]))
        self.csv_writer.writerow(row)

        row = list(self._build_row([item['comments_words_count'], *item['comments_words_dict'].values()]))
        self.csv_writer.writerow(row)

        pass

        



