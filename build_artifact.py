# -*- coding: utf-8 -*-
"""
index.html を読み込んで、単一ファイルの「アーティファクト版」を書き出す。
- manifest.json を data:application/manifest+json;base64,... のリンクに置き換え（アイコンも埋め込み）
- apple-touch-icon を data URI に置き換え
- <!-- SW:START --> 〜 <!-- SW:END --> の Service Worker 登録コードを削除

出力先: C:\\Claude\\ワイン\\sakelog_artifact.html
"""
import base64
import json
import os
import re

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)

INDEX_PATH = os.path.join(APP_DIR, 'index.html')
MANIFEST_PATH = os.path.join(APP_DIR, 'manifest.json')
ICONS_DIR = os.path.join(APP_DIR, 'icons')
OUT_PATH = os.path.join(ROOT_DIR, 'sakelog_artifact.html')


def to_data_uri_png(path):
    with open(path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('ascii')
    return f'data:image/png;base64,{b64}'


def build_manifest_data_uri():
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # icons の src を data URI に置き換え
    for icon in manifest.get('icons', []):
        src = icon['src']
        icon_path = os.path.join(APP_DIR, src)
        icon_path = os.path.normpath(icon_path)
        icon['src'] = to_data_uri_png(icon_path)

    manifest_json = json.dumps(manifest, ensure_ascii=False)
    b64 = base64.b64encode(manifest_json.encode('utf-8')).decode('ascii')
    return f'data:application/manifest+json;base64,{b64}'


def strip_service_worker(html):
    pattern = re.compile(
        r'<!-- SW:START -->.*?<!-- SW:END -->',
        re.DOTALL
    )
    return pattern.sub('', html)


def main():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1) manifest リンクを data URI に置き換え
    manifest_data_uri = build_manifest_data_uri()
    html = html.replace(
        '<link rel="manifest" href="manifest.json">',
        f'<link rel="manifest" href="{manifest_data_uri}">'
    )

    # 2) apple-touch-icon を data URI に置き換え
    apple_icon_path = os.path.join(ICONS_DIR, 'apple-touch-icon.png')
    apple_icon_data_uri = to_data_uri_png(apple_icon_path)
    html = html.replace(
        '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">',
        f'<link rel="apple-touch-icon" href="{apple_icon_data_uri}">'
    )

    # 3) Service Worker 登録コードを削除
    html = strip_service_worker(html)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'書き出し完了: {OUT_PATH}')
    print(f'サイズ: {os.path.getsize(OUT_PATH):,} bytes')
    assert 'data:application/manifest+json' in html, 'manifest data URI が見つからない'
    assert 'serviceWorker' not in html, 'serviceWorker の文字列がまだ残っている'
    print('検証OK: manifest埋め込み済み / serviceWorker削除済み')


if __name__ == '__main__':
    main()
