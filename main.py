import os

import requests


def get_file_path(dir_name="books"):
    os.makedirs(dir_name, exist_ok=True)
    file_path = os.path.abspath(dir_name)
    return file_path


def get_books():
    for id in range(10):
        url = f"https://tululu.org/txt.php?id={32168 + id}"
        response = requests.get(url)
        response.raise_for_status()
        book = f'book{id}.txt'
        path = get_file_path()
        with open(f'{path}/{book}', 'wb')as file:
            file.write(response.content)


get_books()