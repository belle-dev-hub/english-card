import streamlit as st
import io
import zipfile
from gtts import gTTS
from card_generator import create_word_card, get_available_fonts

st.set_page_config(
    page_title="英単語カード作成",
    page_icon="🔤",
    layout="wide",
)

st.title("🔤 英単語カード作成")
st.markdown("イラスト画像と英単語を組み合わせた **4線付き学習カード** を作成します")

# ── Sidebar settings ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ カード設定")

    available_fonts = get_available_fonts()
    font_names = list(available_fonts.keys())
    default_font = next(
        (f for f in font_names if "UD" in f),
        next((f for f in font_names if "Comic" in f), font_names[0]),
    )
    selected_font = st.selectbox("フォント", font_names, index=font_names.index(default_font))

    if "UD" in selected_font and available_fonts.get(selected_font) is None:
        st.warning("UD デジタル教科書体がインストールされていません。\nモリサワ公式サイトからインストールしてください。")

    # 背景色
    bg_color = st.color_picker("背景色", "#ffffff")

    st.caption("💡 Schoolbell や Comic Neue がおすすめです")
    st.divider()
    st.markdown("""
**使い方**
1. 「カードを追加」でカード枠を作成
2. ① イラスト画像をアップロード
3. ② 英単語を入力して **Enter**
4. 「このカードを生成」を押す
5. プレビューを確認してダウンロード
""")

# ── Session state ──────────────────────────────────────────────────────────────
if "cards" not in st.session_state:
    st.session_state.cards = [{"id": 0, "text": "", "image_bytes": None, "card_bytes": None}]
if "next_id" not in st.session_state:
    st.session_state.next_id = 1

# ── Top controls ───────────────────────────────────────────────────────────────
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])

with btn_col1:
    if st.button("➕ カードを追加", use_container_width=True):
        nid = st.session_state.next_id
        st.session_state.cards.append({"id": nid, "text": "", "image_bytes": None, "card_bytes": None})
        st.session_state.next_id += 1
        st.rerun()

with btn_col2:
    if st.button("🔄 全て生成", type="primary", use_container_width=True):
        font_path = available_fonts.get(selected_font)
        for card in st.session_state.cards:
            card["card_bytes"] = create_word_card(
                text=card["text"],
                image_bytes=card["image_bytes"],
                font_path=font_path,
                bg_color=bg_color,
            )
        st.rerun()

with btn_col3:
    ready = [c for c in st.session_state.cards if c.get("card_bytes")]
    if ready:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, c in enumerate(ready):
                safe_name = c["text"].replace("/", "_").replace("\\", "_") or f"card_{i+1}"
                zf.writestr(f"{i+1:02d}_{safe_name}.png", c["card_bytes"])
        zip_buf.seek(0)
        st.download_button(
            f"📦 一括ダウンロード ({len(ready)}枚)",
            data=zip_buf.getvalue(),
            file_name="word_cards.zip",
            mime="application/zip",
            use_container_width=True,
        )

st.divider()

# ── Card list ──────────────────────────────────────────────────────────────────
to_delete = None

for idx, card in enumerate(st.session_state.cards):
    cid = card["id"]

    with st.container(border=True):
        h_col, del_col = st.columns([11, 1])
        with h_col:
            label = card["text"] or "(未入力)"
            st.markdown(f"### カード {idx + 1} &nbsp; `{label}`")
        with del_col:
            if st.button("🗑️", key=f"del_{cid}", help="このカードを削除"):
                to_delete = cid

        left, right = st.columns([1, 1], gap="large")

        with left:
            st.markdown("**① イラスト画像**")
            uploaded = st.file_uploader(
                "イラスト画像",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key=f"up_{cid}",
                label_visibility="collapsed",
            )
            if uploaded is not None:
                new_bytes = uploaded.read()
                if new_bytes != card["image_bytes"]:
                    card["image_bytes"] = new_bytes
                    card["card_bytes"] = None

            if card["image_bytes"]:
                st.image(card["image_bytes"], use_container_width=True)

            st.markdown("**② 英単語 / フレーズ**")
            new_text = st.text_input(
                "英単語",
                value=card["text"],
                key=f"txt_{cid}",
                placeholder="例: play kick baseball",
                label_visibility="collapsed",
            )
            if new_text != card["text"]:
                card["text"] = new_text
                card["card_bytes"] = None

            # 読み上げボタン
            if card["text"].strip():
                if st.button("🔊 読み上げ", key=f"tts_{cid}", use_container_width=True):
                    tts = gTTS(text=card["text"], lang="en", slow=False)
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    audio_fp.seek(0)
                    st.audio(audio_fp, format="audio/mp3", autoplay=True)

            if st.button("🎨 このカードを生成", key=f"gen_{cid}", use_container_width=True):
                font_path = available_fonts.get(selected_font)
                card["card_bytes"] = create_word_card(
                    text=card["text"],
                    image_bytes=card["image_bytes"],
                    font_path=font_path,
                    bg_color=bg_color,
                )
                st.rerun()

        with right:
            st.markdown("**プレビュー**")
            if card.get("card_bytes"):
                st.image(card["card_bytes"], use_container_width=True)
                dl_name = f"{card['text'] or f'card_{idx+1}'}.png"
                st.download_button(
                    "📥 このカードをダウンロード",
                    data=card["card_bytes"],
                    file_name=dl_name,
                    mime="image/png",
                    key=f"dl_{cid}",
                    use_container_width=True,
                )
            else:
                st.info("「このカードを生成」を押してプレビューを表示します", icon="👈")

if to_delete is not None:
    st.session_state.cards = [c for c in st.session_state.cards if c["id"] != to_delete]
    st.rerun()
