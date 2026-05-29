# 🔤 英単語カード作成アプリ

イラスト画像と英単語を組み合わせた4線付き学習カードを作成できるアプリです。画像をアップロードして英単語を入力するだけで、教育用の英語罫線（4線）にぴったり合ったカードを自動生成。個別ダウンロードや一括ZIP出力にも対応。Comic SansやChalkboardなど9種類のフォントから選べます。小学校・中学校の英語授業や自主学習に最適です。

![カードサンプル](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 📋 機能

- 🖼️ イラスト画像のアップロード（PNG / JPG / GIF / WebP）
- ✏️ 英単語・フレーズの入力
- 📏 4線（英語罫線）付きカードの自動生成
- 🎨 フォント選択（9種類）
- 📥 カードの個別ダウンロード（PNG）
- 📦 全カードの一括ダウンロード（ZIP）

---

## 🖥️ 使い方

### 1. カードを追加する
「➕ カードを追加」ボタンでカード枠を作成します。

### 2. 画像と文字を入力する
① イラスト画像をアップロード  
② 英単語またはフレーズを入力して **Enter**

### 3. カードを生成する
「🎨 このカードを生成」を押すとプレビューが表示されます。

### 4. ダウンロードする
- 個別：「📥 このカードをダウンロード」
- まとめて：「📦 一括ダウンロード」

---

## 🎨 選べるフォント

| フォント | 特徴 |
|---------|------|
| UD デジタル教科書体 | 教育向け・視認性最高（要インストール） |
| Comic Sans MS | 子ども向け・親しみやすい |
| Chalkboard | 黒板風 |
| Bradley Hand | 手書き風 |
| Noteworthy | ノート風 |
| Arial | 標準的・スッキリ |
| Verdana | 読みやすい |
| Times New Roman | セリフ体・クラシック |
| Trebuchet MS | モダンなサンセリフ |

---

## 🚀 ローカルで動かす

### 必要なもの
- Python 3.8 以上

### インストール

```bash
git clone https://github.com/あなたのユーザー名/english-card.git
cd english-card
pip install -r requirements.txt
```

### 起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が開きます。

---

## 📁 ファイル構成

```
english-card/
├── app.py              # メインアプリ（Streamlit）
├── card_generator.py   # カード生成ロジック（PIL）
├── requirements.txt    # 必要なライブラリ
└── README.md           # この説明ファイル
