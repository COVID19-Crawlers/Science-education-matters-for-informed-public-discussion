import json

translated_words_path = "translated_words.json"

with open(translated_words_path, 'r', encoding='utf-8') as file:
    translated_words = json.load(file)


JURNAL = 'ynet'
translated = {word_data['English']: word_data['Hebrew'] for ty in translated_words.get(JURNAL, {}).values() for word_data in ty}

translated

translated = {'virus': ['וירוס']}
translated


import os, csv
import pandas as pd

# Path to the folder containing CSV files
directory = '../data2024/' + JURNAL


def read_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        if len(rows) != 10 or len(rows[0]) != 8:
            raise ValueError("Invalid CSV format")
        article = {
            'Info': dict(zip(rows[0], rows[1])),
            'TitleWords': dict(zip(rows[2], rows[3])),
            'SubtitleWords': dict(zip(rows[4], rows[5])),
            'ContentWords': dict(zip(rows[6], rows[7])),
            'CommentsWords': dict(zip(rows[8], rows[9]))
        }
        return article


def count(directory):
    comments_counter = 0
    articles_counter = 0

    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
   
    for file in files:
        article = read_csv(file)
        print(article['Info'])

        if(int(article['Info']['year']) != 2022 or not (2 <= int(article['Info']['month']) <= 8)):
            print('skip ', int(article['Info']['year']), int(article['Info']['month']))
            continue
        
        if article:
            print('count ', articles_counter)

            articles_counter += 1
            comments_counter += int(article['Info']['comments_count'])

    print('articles_counter ', articles_counter)
    print('comments_counter ', comments_counter)


count(directory)

articles_counter=7368
comments_counter=66454


def write_csv(file_path, rows, fieldnames):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def search_article(article, eng_word, words):
    result = {
        'AmountInTitle': 0,
        'AmountInSubtitle': 0,
        'AmountInContent': 0,
        'AmountInComments': 0
    }
        
    for word in words:
        result['AmountInTitle'] += int(article['TitleWords'].get(word, 0))
        result['AmountInSubtitle'] += int(article['SubtitleWords'].get(word, 0))
        result['AmountInContent'] += int(article['ContentWords'].get(word, 0))
        result['AmountInComments'] += int(article['CommentsWords'].get(word, 0))
        
    if any(result.values()):
        return {eng_word: result}
    return {}

def search_journals(files, eng_word, words):
    results = []
    for file in files:
        try:
            article = read_csv(file)
            # print(article['Info'])

            if(int(article['Info']['year']) != 2022 or not (2 <= int(article['Info']['month']) <= 8)):
                # print('skip')
                continue

            result = search_article(article, eng_word, words)

            if result:
                results.append({
                    'source_file': file,
                    'article': article,
                    'results': result
                })
        except:
            pass
    return results


def process_files(directory, translated):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]

    print(directory, 'len ', len(files))
    for eng_word, translations in translated.items():
        results = search_journals(files, eng_word, translations)
        totalAmountInContent = 0
        totalAmountInComments = 0

        print(f'eng_word: {eng_word}, len(results): {len(results)}')
        
        if(results):
            # print(results)
            new_filename = f'{eng_word} in {JURNAL}.csv'
            new_file_path = os.path.join(directory, 'results', new_filename)

            # Prepare data for the new CSV
            fieldnames = list(results[0]['article']['Info'].keys()) + [
                f'{eng_word} בכותרת', f'{eng_word} בכותרת המשנה', f'{eng_word} בתוכן', f'{eng_word} בתגובות', f'{eng_word} ב-1000 כתבות', f'{eng_word} ב-1000 תגובות']
            rows = []
            for result in results:
                row = result['article']['Info']
                row.update({
                    f'{eng_word} בכותרת': result['results'][eng_word]['AmountInTitle'],
                    f'{eng_word} בכותרת המשנה': result['results'][eng_word]['AmountInSubtitle'],
                    f'{eng_word} בתוכן': result['results'][eng_word]['AmountInContent'],
                    f'{eng_word} בתגובות': result['results'][eng_word]['AmountInComments']
                })
                rows.append(row)

                totalAmountInContent += result['results'][eng_word]['AmountInContent']
                totalAmountInComments += result['results'][eng_word]['AmountInComments']

            amountIn1000Articles = (totalAmountInContent / articles_counter) * 1000
            amountIn1000Comments = (totalAmountInComments / comments_counter) * 1000

            amountIn1000 = {
                f'{eng_word} ב-1000 כתבות': str(round(amountIn1000Articles, 5)),
                f'{eng_word} ב-1000 תגובות': str(round(amountIn1000Comments, 5))
            }

            rows.insert(0, amountIn1000)
            
            # Write to new CSV file
            write_csv(new_file_path, rows, fieldnames)
            print(f'Created {new_file_path}')


process_files(directory, translated)



