import argparse
import logging
import os
import urllib
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise HTTPError(f'{response.history} - {HTTPError.__name__}')


def download_txt(content_book, book_id, response_download, folder='books'):
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(f"{book_id}.{content_book['title_book'].strip()}.txt")
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as file:
        file.write(response_download.text)


def get_tail_url(url):
    parse_path_url = urlparse(url)
    path_clean = urllib.parse.unquote(parse_path_url.path)
    _, url_file_name = os.path.split(path_clean)
    url_name, url_tail = os.path.splitext(url_file_name)
    return url_name, url_tail


def download_image(content_book, book_id, folder):
    os.makedirs(folder, exist_ok=True)
    url_name, url_tail = get_tail_url(url=content_book['image_link'])
    response_download_image = requests.get(content_book['image_link'])
    try:
        response_download_image.raise_for_status()
    except HTTPError as exc:
        logging.warning(exc)
    filename = sanitize_filename(f"{book_id}.{content_book['title_book'].strip()}{url_tail}")
    file_path = os.path.join(folder, filename)
    with open(file_path, 'wb') as image:
        image.write(response_download_image.content)


def parse_book_page(soup):
    host = 'https://tululu.org/'
    title_book_tag = soup.find(id='content').find('h1').get_text(strip=True)
    genre_book = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]
    comments = soup.find_all(class_="texts")
    image_link = soup.find(class_='bookimage').find('img')['src']
    url_image = urljoin(host, image_link)
    title_book, author = title_book_tag.split('::')
    comments_book = [comment_tag.find('span', class_="black").get_text(strip=True) for comment_tag in comments]
    content_book = {
        'title_book': title_book.strip(),
        'author': author,
        'genre_book': genre_book,
        'image_link': url_image,
        'comments': comments_book,
    }
    pprint(content_book)
    return content_book


def get_arguments():
    parser = argparse.ArgumentParser(
        description='The code collects book data from an online library.'
    )
    parser.add_argument(
        '-s', '--start_id', type=int, help="Set the initial id for book use arguments: '-s or --start_id'"
    )
    parser.add_argument(
        '-e', '--end_id', type=int, help="Set the end id for book use arguments: '-e or --end_id'"
    )
    args = parser.parse_args()
    return args.start_id, args.end_id


def main():
    logging.basicConfig(
        level=logging.WARNING,
        filename='logs.log',
        filemode='w',
        format='%(asctime)s - [%(levelname)s] - %(funcName)s() - [line %(lineno)d] - %(message)s',
    )

    start, end = get_arguments()
    for book_id in range(start, end + 1):
        payload = {'id': book_id}
        url_download = f'https://tululu.org/txt.php'
        response_download = requests.get(url_download, params=payload)
        try:
            response_download.raise_for_status()
        except HTTPError as exc:
            logging.warning(exc)
        url_title_book = f'https://tululu.org/b{book_id}/'
        response_title_book = requests.get(url_title_book)
        try:
            response_title_book.raise_for_status()
        except HTTPError as exc:
            logging.warning(exc)
        try:
            check_for_redirect(response_download)
        except HTTPError as exc:
            logging.warning(exc)
            continue
        try:
            check_for_redirect(response_title_book)
        except HTTPError as exc:
            logging.warning(exc)
            continue
        soup = BeautifulSoup(response_title_book.text, "lxml")
        content_book = parse_book_page(soup)
        download_txt(content_book, book_id, response_download, folder="books")
        download_image(content_book, book_id, folder="image")


if __name__ == "__main__":
    main()
