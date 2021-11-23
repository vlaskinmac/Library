import argparse
import logging
import os
import urllib
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import HTTPError
from urllib.parse import urljoin, urlparse


def get_file_path(dir_name="books"):
    os.makedirs(dir_name, exist_ok=True)
    file_path = os.path.abspath(dir_name)
    return file_path


def check_for_redirect(response):
    if response.history:
        raise HTTPError(f'{response.history} - {HTTPError.__name__}')


def download_txt(soup, number, response_download, folder='books'):
    filepath = get_file_path(dir_name=sanitize_filepath(folder))
    text_tag = soup.find(id='content').find('h1').get_text(strip=True)
    file_name = sanitize_filename(f"{number}.{text_tag.split('::')[0].strip()}")
    file_path = os.path.join(filepath, f'{file_name}.txt')
    with open(file_path, 'w') as file:
        file.write(response_download.text)


def get_tail_url(url):
    parse_path_url = urlparse(url)
    path_clean = urllib.parse.unquote(parse_path_url.path)
    url_file_name = os.path.split(path_clean)
    url_tail = os.path.splitext(url_file_name[-1])[-1]
    url_name = os.path.splitext(url_file_name[-1])[0]
    return url_name, url_tail


def download_image(soup, filepath):
    host = 'https://tululu.org/'
    image_link = soup.find(class_='bookimage').find('img')['src']
    url_image = urljoin(host, image_link)
    url_name, url_tail = get_tail_url(url=url_image)
    response_download = requests.get(url_image)
    response_download.raise_for_status()
    file_path = os.path.join(filepath, f'{url_name}{url_tail}')
    with open(file_path, 'wb') as file:
        file.write(response_download.content)


def parse_book_page(soup):
    host = 'https://tululu.org/'
    title_tag = soup.find(id='content').find('h1').get_text(strip=True)
    genre_book = [i.text for i in soup.find('span', class_='d_book').find_all('a')]
    comments = soup.find_all(class_="texts")
    image_link = soup.find(class_='bookimage').find('img')['src']
    url_image = urljoin(host, image_link)
    title, author = title_tag.split('::')
    content_book = {
        'title': title,
        'author': author,
        'genre_book': genre_book,
        'image_link': url_image,
    }
    comments_book = []
    for comment_tag in comments:
        comments_book.append(comment_tag.find('span', class_="black").get_text(strip=True))
    content_book['comments'] = comments_book
    pprint(content_book)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="The code collects book data from an online library."
    )
    parser.add_argument(
        "-s", "--start_id", type=int, help="Set the initial id for book use arguments: '-s or --start_id'"
    )
    parser.add_argument(
        "-e", "--end_id", type=int, help="Set the end id for book use arguments: '-e or --end_id'"
    )
    args = parser.parse_args()
    return args.start_id, args.end_id


def main():
    logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(funcName)s() - [line %(lineno)d] - %(message)s",
    )
    start, end = get_arguments()
    start=1
    end=10

    for number in range(start, end + 1):
        payload = {"id": number}
        url_download = f"https://tululu.org/txt.php"
        response_download = requests.get(url_download, params=payload)
        response_download.raise_for_status()
        url_title = f'https://tululu.org/b{number}/'
        response_title = requests.get(url_title)
        response_title.raise_for_status()
        filepath = get_file_path(dir_name='image')
        try:
            check_for_redirect(response_download)
        except:
            logging.warning("[<Response [302]>] - HTTPError")
            continue
        soup = BeautifulSoup(response_title.text, 'lxml')
        download_txt(soup, number, response_download, folder='books')
        download_image(soup, filepath)
        parse_book_page(soup)


if __name__ == "__main__":
    main()
