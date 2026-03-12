"""
ジム訴求用デモ動画生成スクリプト (Instagram/TikTok 9:16)
- プレースホルダー画像で5シーン構成
- テキストオーバーレイ + トランジション付き
- 実際の素材画像に差し替えて再利用可能
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx,
)
import os

# === 設定 ===
WIDTH, HEIGHT = 1080, 1920  # 9:16 縦型
FPS = 30
SCENE_DURATION = 3  # 各シーン秒数
OUTPUT_DIR = "/home/user/tools/output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "gym_promo_demo.mp4")

# フォント
FONT_JP = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
FONT_EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# カラーパレット
COLORS = {
    "dark": (20, 20, 25),
    "accent": (255, 87, 34),   # オレンジ
    "white": (255, 255, 255),
    "gray": (60, 60, 65),
}

# シーン定義
SCENES = [
    {
        "bg_color": COLORS["dark"],
        "accent_color": COLORS["accent"],
        "main_text": "変わる、ここから。",
        "sub_text": "YOUR FITNESS JOURNEY",
        "layout": "center",
    },
    {
        "bg_color": (15, 25, 40),
        "accent_color": (0, 180, 255),
        "main_text": "最新マシン完備",
        "sub_text": "FULL EQUIPMENT",
        "layout": "top",
    },
    {
        "bg_color": (25, 15, 15),
        "accent_color": (255, 50, 50),
        "main_text": "プロトレーナー在籍",
        "sub_text": "PERSONAL TRAINING",
        "layout": "bottom",
    },
    {
        "bg_color": (10, 30, 20),
        "accent_color": (0, 230, 120),
        "main_text": "24時間営業",
        "sub_text": "OPEN 24/7",
        "layout": "center",
    },
    {
        "bg_color": COLORS["dark"],
        "accent_color": COLORS["accent"],
        "main_text": "無料体験受付中",
        "sub_text": "FREE TRIAL NOW",
        "layout": "center",
    },
]


def create_scene_image(scene, index):
    """シーンのプレースホルダー画像を生成"""
    img = Image.new("RGB", (WIDTH, HEIGHT), scene["bg_color"])
    draw = ImageDraw.Draw(img)
    accent = scene["accent_color"]

    # 装飾パターン: 斜めストライプ
    for i in range(-HEIGHT, WIDTH + HEIGHT, 80):
        draw.line(
            [(i, 0), (i + HEIGHT, HEIGHT)],
            fill=(*accent, 30) if img.mode == "RGBA" else tuple(c // 8 for c in accent),
            width=2,
        )

    # アクセントバー（上部）
    draw.rectangle([(0, 0), (WIDTH, 8)], fill=accent)

    # メインビジュアルエリア（素材画像の代わり）
    if scene["layout"] == "top":
        visual_y = 200
    elif scene["layout"] == "bottom":
        visual_y = 700
    else:
        visual_y = 400

    # ダミービジュアル: グラデーション風の矩形
    for j in range(400):
        alpha = max(0, 255 - j)
        r = min(255, accent[0] + j // 4)
        g = min(255, accent[1] + j // 4)
        b = min(255, accent[2] + j // 4)
        bg = scene["bg_color"]
        ratio = j / 400
        color = tuple(int(c * (1 - ratio) + bg_c * ratio) for c, bg_c in zip(accent, bg))
        draw.rectangle(
            [(100, visual_y + j), (WIDTH - 100, visual_y + j + 1)],
            fill=color,
        )

    # 中央にダンベルアイコン風の図形
    cx, cy = WIDTH // 2, visual_y + 200
    draw.ellipse([(cx - 60, cy - 60), (cx + 60, cy + 60)], outline=accent, width=4)
    draw.rectangle([(cx - 80, cy - 15), (cx + 80, cy + 15)], fill=accent)
    draw.ellipse([(cx - 100, cy - 40), (cx - 60, cy + 40)], fill=accent)
    draw.ellipse([(cx + 60, cy - 40), (cx + 100, cy + 40)], fill=accent)

    # プレースホルダーテキスト
    try:
        small_font = ImageFont.truetype(FONT_EN, 24)
    except:
        small_font = ImageFont.load_default()
    placeholder_text = f"SCENE {index + 1} - REPLACE WITH YOUR IMAGE"
    bbox = draw.textbbox((0, 0), placeholder_text, font=small_font)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - tw) // 2, visual_y + 350),
        placeholder_text,
        fill=(*accent, 128) if img.mode == "RGBA" else tuple(c // 2 for c in accent),
        font=small_font,
    )

    # アクセントバー（下部）
    draw.rectangle([(0, HEIGHT - 8), (WIDTH, HEIGHT)], fill=accent)

    return np.array(img)


def build_text_clip(text, font_path, font_size, color, position, duration, fade_in=0.5):
    """テキストクリップを作成"""
    clip = TextClip(
        text=text,
        font=font_path,
        font_size=font_size,
        color=f"rgb({color[0]},{color[1]},{color[2]})",
        text_align="center",
        method="label",
    )
    clip = clip.with_duration(duration)
    clip = clip.with_position(position)
    clip = clip.with_effects([vfx.CrossFadeIn(fade_in)])
    return clip


def create_scene_clip(scene, index):
    """1シーン分のクリップを作成"""
    bg_array = create_scene_image(scene, index)
    bg_clip = ImageClip(bg_array).with_duration(SCENE_DURATION)

    accent = scene["accent_color"]
    layers = [bg_clip]

    # メインテキスト（日本語）
    if scene["layout"] == "bottom":
        main_y = 1300
    elif scene["layout"] == "top":
        main_y = 900
    else:
        main_y = 1100

    main_text = build_text_clip(
        scene["main_text"],
        FONT_JP,
        font_size=80,
        color=COLORS["white"],
        position=("center", main_y),
        duration=SCENE_DURATION,
        fade_in=0.4,
    )
    layers.append(main_text)

    # サブテキスト（英語）
    sub_text = build_text_clip(
        scene["sub_text"],
        FONT_EN,
        font_size=36,
        color=accent,
        position=("center", main_y + 100),
        duration=SCENE_DURATION,
        fade_in=0.6,
    )
    layers.append(sub_text)

    # CTA（最終シーン）
    if index == len(SCENES) - 1:
        cta = build_text_clip(
            "▶ 今すぐ申し込む",
            FONT_JP,
            font_size=48,
            color=COLORS["white"],
            position=("center", main_y + 200),
            duration=SCENE_DURATION,
            fade_in=1.0,
        )
        layers.append(cta)

    composite = CompositeVideoClip(layers, size=(WIDTH, HEIGHT))
    composite = composite.with_effects([
        vfx.CrossFadeIn(0.3),
        vfx.CrossFadeOut(0.3),
    ])
    return composite


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("シーンを生成中...")
    clips = []
    for i, scene in enumerate(SCENES):
        print(f"  シーン {i+1}/{len(SCENES)}: {scene['main_text']}")
        clip = create_scene_clip(scene, i)
        clips.append(clip)

    print("動画を結合中...")
    final = concatenate_videoclips(clips, method="compose")

    print(f"書き出し中... → {OUTPUT_FILE}")
    final.write_videofile(
        OUTPUT_FILE,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        bitrate="5000k",
        logger="bar",
    )

    duration = len(SCENES) * SCENE_DURATION
    print(f"\n完成! {duration}秒の動画が生成されました")
    print(f"出力: {OUTPUT_FILE}")
    print(f"サイズ: {WIDTH}x{HEIGHT} (9:16)")
    print("\n※ 実際の素材画像に差し替える場合は、SCENES内の設定を変更してください")


if __name__ == "__main__":
    main()
