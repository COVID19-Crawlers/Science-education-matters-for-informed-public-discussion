import csv

jurnal = 'kikar'

def create_individual_csv_files(input_csv):
    with open(input_csv, mode='r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        for row in reader:
            filename = f'COVID19-Crawlers/terms_appearance_comments/{jurnal}/{(row[0].replace('?', ''))}_{jurnal}.csv'
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as outfile:
                writer = csv.writer(outfile)
                writer.writerow([row[0]]) 
                
                for sample in row[1:]:
                    writer.writerow([sample]) 

if __name__ == "__main__":
    input_csv = f'{jurnal}_comments_output.csv' 
    create_individual_csv_files(input_csv)
