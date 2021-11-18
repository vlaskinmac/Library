import logging
import os

import requests
from requests import HTTPError


def get_file_path(dir_name="books"):
    os.makedirs(dir_name, exist_ok=True)
    file_path = os.path.abspath(dir_name)
    return file_path


def check_for_redirect(response):
    if response.history:
        raise HTTPError(f'{response.history} - {HTTPError.__name__}')


def get_books(path):
    number = 0
    for id in range(1, 11):
        url = f"https://tululu.org/txt.php?id={id}"
        response = requests.get(url)
        response.raise_for_status()
        try:
            if check_for_redirect(response):
                continue
            else:
                number += 1
                book = f'book{number}.txt'
                with open(f'{path}/{book}', 'wb') as file:
                    file.write(response.content)
        except HTTPError as exc:
            logging.warning(exc)


def main():
    logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )

    path = get_file_path()
    get_books(path)


if __name__ == "__main__":
    main()

