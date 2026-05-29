from PIL import Image, ImageDraw, ImageFont
import io
import os

CARD_W = 840
CARD_H = 596
IMAGE_H = 360
LINE_H  = CARD_H - IMAGE_H   # = 236

_UD_PATHS = [
    "/Library/Fonts/UDDigitalKyokashoN-R.ttf",
    "/Library/Fonts/UDDigitalKyokashoN-B.ttf",
    "/Library/Fonts/UDDGKyokashoN-R.ttf",
    os.path.expanduser("~/Library/Fonts/UDDigitalKyokashoN-R.ttf"),
    "C:/Windows/Fonts/UDDigitalKyokashoN-R.ttf",
]

# フォントファイルのパス（このファイルと同じ場所）
_FONTS_DIR = os.path.dirname(os.path.abspath(__file__))

def _f(filename):
    """フォントファイルのパスを返す（fontsサブフォルダも探す）"""
    # まずルートを探す
    root_path = os.path.join(_FONTS_DIR, filename)
    if os.path.exists(root_path):
        return root_path
    # 次にfontsサブフォルダを探す
    return os.path.join(_FONTS_DIR, "fonts", filename)

FONT_CATALOG = {
    "UD デジタル教科書体": _UD_PATHS,
    "Schoolbell (学校ノート風)": [
        _f("Schoolbell-Regular.ttf"),
    ],
    "Comic Neue (コミック風)": [
        _f("ComicNeue-Bold.ttf"),
        "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
        "C:/Windows/Fonts/comic.ttf",
    ],
    "Patrick Hand (手書き風)": [
        _f("PatrickHand-Regular.ttf"),
    ],
    "Indie Flower (かわいい手書き)": [
        _f("IndieFlower-Regular.ttf"),
    ],
    "Nunito (丸くて読みやすい)": [
        _f("Nunito-Regular.ttf"),
        _f("Nunito-VariableFont_wght.ttf"),
        _f("Nunito-Italic-VariableFont_wght.ttf"),
    ],
    "Open Sans (スッキリ標準)": [
        _f("OpenSans-Regular.ttf"),
        _f("OpenSans-VariableFont_wdth,wght.ttf"),
        _f("OpenSans-Italic-VariableFont_wdth,wght.ttf"),
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ],
    "Chalkboard (黒板風)": [
        "/System/Library/Fonts/ChalkboardSE.ttc",
        "/System/Library/Fonts/Supplemental/Chalkboard.ttc",
    ],
    "Arial (標準)": [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ],
    "Verdana (読みやすい)": [
        "/System/Library/Fonts/Supplemental/Verdana.ttf",
        "C:/Windows/Fonts/verdana.ttf",
    ],
    "Times New Roman (セリフ体)": [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "C:/Windows/Fonts/times.ttf",
    ],
    "ちはやクレヨン (クレヨン風)": [
        os.path.expanduser("~/Library/Fonts/ちはやクレヨンRE-free-.ttf"),
    ],
}


def get_available_fonts():
    result = {}
    for name, paths in FONT_CATALOG.items():
        for path in paths:
            if os.path.exists(path):
                result[name] = path
                break
    return result or {"Default": None}


def _load_font(font_path, size):
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    return ImageFont.load_default(size=max(12, size))


def _draw_dashed_line(draw, x1, y, x2, color, width, dash=14, gap=8):
    x = x1
    while x < x2:
        x_end = min(x + dash, x2)
        draw.line([(x, round(y)), (x_end, round(y))], fill=color, width=width)
        x += dash + gap


def _hline(draw, y, pad_x, color, width, dashed=False):
    """Helper: draw one horizontal line across the card."""
    y = round(y)
    if dashed:
        _draw_dashed_line(draw, pad_x, y, CARD_W - pad_x, color, width)
    else:
        draw.line([(pad_x, y), (CARD_W - pad_x, y)], fill=color, width=width)


def create_word_card(text, image_bytes=None, font_path=None):
    """PNG bytes for a word card. 4-line positions are derived from font metrics."""

    card = Image.new("RGB", (CARD_W, CARD_H), "white")
    draw = ImageDraw.Draw(card)

    # 外枠
    draw.rectangle([0, 0, CARD_W - 1, CARD_H - 1], outline="#bbbbbb", width=2)

    # ── イラスト領域 ────────────────────────────────────────────────────
    img_pad = 24
    if image_bytes:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            max_w = CARD_W - img_pad * 2
            max_h = IMAGE_H - img_pad * 2
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            bg = Image.new("RGB", img.size, "white")
            bg.paste(img, mask=img.split()[3])
            x = (CARD_W - img.width) // 2
            y = img_pad + (max_h - img.height) // 2
            card.paste(bg, (x, y))
        except Exception:
            pass

    # 区切り線
    draw.line([(0, IMAGE_H), (CARD_W, IMAGE_H)], fill="#dddddd", width=2)

    # 罫線エリア背景
    writing_bg = Image.new("RGB", (CARD_W, LINE_H), "#fafaf8")
    card.paste(writing_bg, (0, IMAGE_H))
    draw.line([(0, IMAGE_H), (CARD_W, IMAGE_H)], fill="#dddddd", width=2)

    # ── フォント & サイズ決定 ────────────────────────────────────────────
    if not (text and text.strip()):
        # テキストなし: デフォルト比率で罫線だけ描く
        _draw_default_lines(draw)
        buf = io.BytesIO()
        card.save(buf, format="PNG", dpi=(150, 150))
        buf.seek(0)
        return buf.getvalue()

    LINE_MARGIN = 8  # 上下の最小余白 (px)
    available_h  = LINE_H - LINE_MARGIN * 2  # 罫線エリアの実効高さ

    def _measure_refs(fnt):
        """参照文字の実ピクセル高さを返す (anchor='ls' = ベースライン基準)
        actual_ascent : アセンダー文字群の最大上端ピクセル（ベースライン上方）
        actual_descent: ディセンダー文字群の最大下端ピクセル（ベースライン下方）
        x_height      : 'x' の上端までのピクセル数
        """
        # 全アセンダー文字の最大値を取る（'f','h','l' が 'b' より高いフォントがある）
        asc_chars  = "bdfhklt"
        desc_chars = "gjpqy"
        actual_ascent  = max(
            -draw.textbbox((0, 0), ch, font=fnt, anchor="ls")[1]
            for ch in asc_chars
        )
        actual_descent = max(
            draw.textbbox((0, 0), ch, font=fnt, anchor="ls")[3]
            for ch in desc_chars
        )
        x_height = -draw.textbbox((0, 0), "x", font=fnt, anchor="ls")[1]
        return actual_ascent, actual_descent, x_height

    # ① 初期フォントサイズ（available_h を出発点に）
    font_size = max(24, available_h)
    font = _load_font(font_path, font_size)

    # 参照文字の実高さで available_h ぴったりに合わせる
    ref_asc, ref_desc, _ = _measure_refs(font)
    total_ref = ref_asc + ref_desc
    if total_ref > 0:
        font_size = int(font_size * available_h / total_ref)
        font = _load_font(font_path, font_size)

    # ② 幅が超える場合は縮小
    max_text_w = CARD_W - 80
    text_w = draw.textlength(text, font=font)
    if text_w > max_text_w:
        font_size = int(font_size * max_text_w / text_w)
        font = _load_font(font_path, font_size)

    # ③ 最終メトリクス（実ピクセル）
    actual_ascent, actual_descent, x_height = _measure_refs(font)

    # ── ベースライン Y 座標を決定 ─────────────────────────────────────────
    # 上線を LINE_MARGIN に固定 → baseline_y を逆算
    top_line_y    = IMAGE_H + LINE_MARGIN
    baseline_y    = top_line_y + actual_ascent
    bottom_line_y = baseline_y + actual_descent

    # 下がはみ出す場合は再縮小
    if bottom_line_y > CARD_H - LINE_MARGIN:
        scale = (CARD_H - LINE_MARGIN - top_line_y) / (actual_ascent + actual_descent)
        font_size = int(font_size * scale)
        font = _load_font(font_path, font_size)
        actual_ascent, actual_descent, x_height = _measure_refs(font)
        top_line_y    = IMAGE_H + LINE_MARGIN
        baseline_y    = top_line_y + actual_ascent
        bottom_line_y = baseline_y + actual_descent

    xheight_line_y = baseline_y - x_height  # 破線: x-height（小文字の上端）

    PAD_X = 40

    # ── 4本の罫線を描画 ─────────────────────────────────────────────────
    _hline(draw, top_line_y,     PAD_X, "#999999", 1, dashed=False)  # 上線
    _hline(draw, xheight_line_y, PAD_X, "#aaaaaa", 1, dashed=True)   # 破線
    _hline(draw, baseline_y,     PAD_X, "#4a90d9", 2, dashed=False)  # 青ベースライン
    _hline(draw, bottom_line_y,  PAD_X, "#999999", 1, dashed=False)  # 下線

    # ── テキストを青ベースラインに揃えて中央描画 ─────────────────────────
    draw.text(
        (CARD_W // 2, round(baseline_y)),
        text,
        fill="#1a1a1a",
        font=font,
        anchor="ms",   # m=水平中央, s=ベースライン基準
    )

    buf = io.BytesIO()
    card.save(buf, format="PNG", dpi=(150, 150))
    buf.seek(0)
    return buf.getvalue()


def _draw_default_lines(draw):
    """テキストなしの場合のデフォルト4線（比率ベース）"""
    area_top = IMAGE_H
    total_h  = LINE_H
    PAD_X    = 40
    _hline(draw, area_top + total_h * 0.12, PAD_X, "#999999", 1)
    _hline(draw, area_top + total_h * 0.50, PAD_X, "#aaaaaa", 1, dashed=True)
    _hline(draw, area_top + total_h * 0.75, PAD_X, "#4a90d9", 2)
    _hline(draw, area_top + total_h * 0.92, PAD_X, "#999999", 1)
