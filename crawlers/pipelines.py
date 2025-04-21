import codecs
from itemadapter import ItemAdapter
from pathlib import Path
from crawlers.exporters import ArticleItemExporter

class MultiCSVItemPipeline:
    '''Export each article to different csv'''

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        folder = f'../../data/{adapter["source"]}'

        Path(folder).mkdir(parents=True, exist_ok=True)

        name = f'{folder}/{adapter["year"]} {adapter["month"]} {adapter["day"]} - {adapter["source"]} - {adapter["id"]}.csv'
        file = open(name, 'w+b')

        exporter = ArticleItemExporter(file, encoding='utf-8-sig')
        exporter.start_exporting()
        exporter.export_item(item)
        exporter.finish_exporting()
        file.close()

        return item