import logging
import os
import urllib

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


def download_txt(folder='books'):
    for id in range(1, 11):
        url_download = f"https://tululu.org/txt.php?id={id}"
        response_download = requests.get(url_download)
        response_download.raise_for_status()
        url_title = f'https://tululu.org/b{id}/'
        response_title = requests.get(url_title)
        response_title.raise_for_status()
        try:
            if check_for_redirect(response_title):
                continue
            else:
                soup = BeautifulSoup(response_title.text, 'lxml')
                filepath = get_file_path(dir_name=sanitize_filepath(folder))
                text_tag = soup.find(id='content').find('h1').get_text(strip=True)
                file_name = sanitize_filename(f"{id}.{text_tag.split('::')[0].strip()}")
                comments = soup.find_all(class_="texts")
                print(text_tag.split('::')[0].strip())
                for comment_tag in comments:
                    comment = comment_tag.find('span', class_="black").get_text(strip=True)
                    print(comment)
                print()
                file_path = os.path.join(filepath, f'{file_name}.txt')
        except HTTPError as exc:
            logging.warning(exc)
        try:
            if check_for_redirect(response_download):
                continue
            else:
                with open(f'{file_path}', 'wb') as file:
                    file.write(response_download.content)
        except HTTPError as exc:
            logging.warning(exc)


def get_tail_url(url):
    parse_path_url = urlparse(url)
    path_clean = urllib.parse.unquote(parse_path_url.path)
    url_file_name = os.path.split(path_clean)
    url_tail = os.path.splitext(url_file_name[-1])[-1]
    url_name = os.path.splitext(url_file_name[-1])[0]
    return url_name, url_tail


def download_image():
    host = 'https://tululu.org/'
    for id in range(1, 11):
        url_title = f'https://tululu.org/b{id}/'
        response = requests.get(url_title)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        filepath = get_file_path(dir_name='image')
        try:
            if check_for_redirect(response):
                continue
            else:
                image_link = soup.find(class_='bookimage').find('img')['src']
                url_image = urljoin(host, image_link)
                url_name, url_tail = get_tail_url(url=url_image)
                response_download = requests.get(url_image)
                response.raise_for_status()
                file_path = os.path.join(filepath, f'{url_name}{url_tail}')

                with open(f'{file_path}', 'wb') as file:
                    file.write(response_download.content)
        except HTTPError as exc:
            logging.warning(exc)


def main():
    logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(funcName)s() - [line %(lineno)d] - %(message)s",
    )
    download_txt()
    download_image()


if __name__ == "__main__":
    main()
