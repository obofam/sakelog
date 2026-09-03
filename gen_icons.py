# -*- coding: utf-8 -*-
"""
酒ログ用のアイコンを生成する。
角丸正方形の深いワイン色背景に、白いワイングラス（円のボウル＋ステム＋ベース）を描く。
出力: icons/icon-192.png, icons/icon-512.png, icons/apple-touch-icon.png(180px)
"""
import os
from PIL import Image, ImageDraw

BG = (123, 45, 59, 255)  # #7B2D3B
FG = (244, 237, 233, 255)  # ほぼ白（--text に寄せた白）

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
os.makedirs(OUT_DIR, exist_ok=True)


def draw_glass(size):
    """size x size の角丸正方形アイコンを1枚作る"""
    scale = 4  # アンチエイリアス用に大きく描いてから縮小
    S = size * scale
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 角丸正方形の背景
    radius = int(S * 0.22)
    draw.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=BG)

    # ワイングラスを中央に描く（円のボウル + ステム + ベース）
    cx = S / 2
    bowl_r = S * 0.22
    bowl_cy = S * 0.36
    # ボウル（円）
    draw.ellipse(
        [cx - bowl_r, bowl_cy - bowl_r, cx + bowl_r, bowl_cy + bowl_r],
        fill=FG
    )
    # ステム（茎）
    stem_w = S * 0.045
    stem_top = bowl_cy + bowl_r * 0.55
    stem_bottom = S * 0.76
    draw.rectangle(
        [cx - stem_w / 2, stem_top, cx + stem_w / 2, stem_bottom],
        fill=FG
    )
    # ベース（台座）
    base_w = S * 0.30
    base_h = S * 0.045
    draw.rounded_rectangle(
        [cx - base_w / 2, stem_bottom, cx + base_w / 2, stem_bottom + base_h],
        radius=base_h / 2,
        fill=FG
    )

    img = img.resize((size, size), Image.LANCZOS)
    return img


def main():
    sizes = {
        'icon-192.png': 192,
        'icon-512.png': 512,
        'apple-touch-icon.png': 180,
    }
    for name, size in sizes.items():
        img = draw_glass(size)
        path = os.path.join(OUT_DIR, name)
        img.save(path, 'PNG')
        print(f'{name}: {size}x{size} -> {path}')


if __name__ == '__main__':
    main()
