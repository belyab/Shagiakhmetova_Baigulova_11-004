import math
import os
import shutil
from collections import Counter, defaultdict
import pymorphy2
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from bs4 import BeautifulSoup

PACKAGE_PATH = "downloaded_texts"
TOKENS_LIST_PATH = "tokens_list_tf_idf"
LEMMAS_LIST_PATH = "lemmas_list_tf_idf"


def get_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text


def idf_count(files_texts, word):
    count = 0
    for text in files_texts.values():
        if word in text:
            count += 1
    return count


class Calculator:
    tokens_tags = {"NUMB", "ROMN", "PRCL", "PREP", "CONJ", "INTJ", "LATN", "UNKN", "PNCT"}

    def __init__(self, text):
        self.text = text
        self.stop_words = set(stopwords.words("russian"))
        self.tokenizer_result = WordPunctTokenizer().tokenize(text)
        self.morph_analyzer = pymorphy2.MorphAnalyzer()
        self.tokens = set()
        self.lemmas = defaultdict(set)
        self.parse_text()

    def parse_text(self):
        self.tokens.update(self.tokenizer_result)
        bad_tokens = set()
        for token in self.tokens:
            morph = self.morph_analyzer.parse(token)[0]
            tags = str(morph.tag)
            if self.is_bad_token(tags, token):
                bad_tokens.add(token)
        self.tokens -= bad_tokens

        for token in self.tokens:
            morph = self.morph_analyzer.parse(token)[0]
            if morph.score >= 0.5:
                self.lemmas[morph.normal_form].add(token)

    def is_bad_token(self, tags, token):
        return any(tag in self.tokens_tags for tag in tags.split("|")) or token in self.stop_words


def clear_directory(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")


def process_files(FILES_PATH, TOKENS_PATH, LEMMAS_PATH):
    clear_directory(TOKENS_PATH)
    clear_directory(LEMMAS_PATH)

    files_texts = {}
    for root, _, files in os.walk(FILES_PATH):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            text = get_text(file_path)
            files_texts[file] = text

    entire_text = " ".join(files_texts.values())
    entire_text_calculate = Calculator(entire_text)

    for file_name, text in files_texts.items():
        text_calc = Calculator(text)
        words_counter = Counter(text_calc.tokenizer_result)

        os.makedirs(TOKENS_PATH, exist_ok=True)
        for token in text_calc.tokens:
            tf = words_counter[token] / len(text_calc.tokenizer_result)
            idf = math.log(len(files_texts) / sum(1 for text in files_texts.values() if token in text))
            tf_idf = tf * idf
            newFile = f"{os.path.splitext(file_name)[0]}.txt"
            with open(os.path.join(TOKENS_PATH, newFile), "a") as f:
                f.write(f"{token} {idf} {tf_idf}\n")

        os.makedirs(LEMMAS_PATH, exist_ok=True)
        for lemma, tokens in text_calc.lemmas.items():
            tf_n = sum(words_counter[lemma] for lemma in [lemma] + list(tokens))
            count = sum(any(token in text for token in tokens) or lemma in text for text in files_texts.values())
            tf = tf_n / len(text_calc.tokenizer_result)
            idf = math.log(len(files_texts) / count)
            tf_idf = tf * idf
            newFile = f"{os.path.splitext(file_name)[0]}.txt"
            with open(os.path.join(LEMMAS_PATH, newFile), "a") as f:
                f.write(f"{lemma} {idf} {tf_idf}\n")


if __name__ == "__main__":
    process_files(PACKAGE_PATH, TOKENS_LIST_PATH, LEMMAS_LIST_PATH)