import logging
import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import HTTPError


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
                text_tag = soup.find(id='content').find('h1').get_text(strip=True)
                filepath = get_file_path(dir_name=sanitize_filepath(folder))
                file_name = sanitize_filename(f"{id}.{text_tag.split('::')[0].strip()}")
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


def main():
    logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(funcName)s() - [line %(lineno)d] - %(message)s",
    )
    download_txt()


if __name__ == "__main__":
    main()
