import requests
from bs4 import BeautifulSoup
import os

def download_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Ошибка при загрузке страницы {url}. Статус код: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None

def save_html(content, filename):
    with open(filename, 'wb') as f:
        f.write(content)

def crawler(url, output_dir, max_pages=100):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    index_file = open(os.path.join(output_dir, 'index.txt'), 'w', encoding='utf-8')

    pages_downloaded = 0
    visited_links = set()
    next_pages = [url]
    while pages_downloaded < max_pages and next_pages:
        current_url = next_pages.pop(0)
        if current_url in visited_links:
            continue

        html_content = download_page(current_url)
        if html_content:
            filename = f"page_{pages_downloaded+1}.html"
            save_html(html_content, os.path.join(output_dir, filename))
            index_file.write(f"{filename}: {current_url}\n")
            print(f"Страница {current_url} успешно загружена и сохранена как {filename}")
            pages_downloaded += 1

            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                next_link = link['href']

                if next_link.startswith('/') and not next_link.startswith('//'):
                    next_link = 'https://tur-kazan.ru' + next_link
                    next_pages.append(next_link)

            visited_links.add(current_url)
        else:
            continue

    index_file.close()

if __name__ == "__main__":

    start_url = 'https://tur-kazan.ru/info/dostoprimechatelnosti'
    output_directory = 'downloaded_texts'
    crawler(start_url, output_directory, max_pages=100)