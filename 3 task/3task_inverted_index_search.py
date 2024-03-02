import os
import json
from bs4 import BeautifulSoup

html_directory = 'downloaded_texts'

existing_tokens_file_path = "tokens_list.txt"
existing_lemmas_file_path = "lemmatized_tokens_list.txt"

inverted_index = {}

with open(existing_tokens_file_path, "r", encoding="utf-8") as tokens_file:
    existing_tokens = set(line.strip() for line in tokens_file)

existing_lemmas = {}
with open(existing_lemmas_file_path, "r", encoding="utf-8") as lemmas_file:
    for line in lemmas_file:
        parts = line.strip().split(' ')
        lemma = parts[0]
        tokens = set(parts[1:])
        existing_lemmas[lemma] = tokens

for filename in os.listdir(html_directory):
    if filename.endswith('.html'):
        file_number = filename.split('_')[-1].split('.')[0]

        with open(os.path.join(html_directory, filename), 'r', encoding='utf-8') as html_file:
            soup = BeautifulSoup(html_file, 'html.parser')
            text = soup.get_text()

        tokens = [token.lower() for token in text.split() if token.lower() in existing_tokens]

        for token in set(tokens):
            if token not in inverted_index:
                inverted_index[token] = {
                    "count": 0,
                    "inverted_array": [],
                    "word": token
                }
            inverted_index[token]["count"] += 1
            inverted_index[token]["inverted_array"].append(int(file_number))

output_file_path = 'inverted_index.txt'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for term_data in inverted_index.values():
        json.dump(term_data, output_file, ensure_ascii=False)
        output_file.write('\n')
