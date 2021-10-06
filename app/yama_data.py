"""山データを取り出すためのモジュール."""
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse


def get_yama_dataframe(url: str) -> Optional[pd.DataFrame]:
    """Webページから山データを取り出しデータフレームを作成する."""
    # ページをGETで取得する
    file_path = download_file_if_needed(url)

    if file_path is not None:
        with open(file_path, mode='r') as f:
            res = f.read()

        soup = BeautifulSoup(res, 'html.parser')
        # class名がbase_textのdiv要素を探す
        info = soup.find('div', class_='base_txt')

        # Tableの中身を取り出す
        rows = info.find_all('tr')
        if len(rows) > 1:            
            headers = [h.text.strip() for h in rows[0].find_all('th')]
            headers.append('url')
            values = []
            for row in rows[1:]:
                v = []
                link = None
                for r in row.find_all('td'):
                    if link is None: 
                        # 山名<山頂名>, URLの取り出し
                        link = r.find('a')
                        v.append(link.text.strip())
                    else:
                        v.append(r.text.strip())
                v.append(link['href'] if link is not None else '')
                values.append(v)

        df = pd.DataFrame(values, columns=headers)
        return df
    else:
        return None


def download_file_if_needed(url) -> Optional[str]:
    """ローカルにデータファイルがない場合は、データファイルをダウンロードする."""
    # ローカルへの保存先
    dir = f'{os.path.dirname(__file__) }/data'
    if not os.path.isdir(dir):
        os.mkdir(dir)

    path = urlparse(url).path.split('/')
    file_path = None

    if len(path) > 0:
        file_path = f'{dir}/{path[len(path)-1]}'
        if not os.path.exists(file_path):
            data = requests.get(url).content
            with open(file_path, mode='wb') as f:
                f.write(data)
    return file_path
