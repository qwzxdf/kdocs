# kdocs

ゲーム制作のための C++23 標準ライブラリ ノート。

https://qwzxdf.github.io/kdocs/

## ローカルで見る

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
mkdocs serve
```

http://127.0.0.1:8000/kdocs/ を開く。ファイルを保存すると自動で再読み込みされる。

## 記事を追加する

1. `docs/_template.md` をコピーして、カテゴリのフォルダに置く
2. カテゴリの `index.md` の一覧にリンクを足す（よく使う順）
3. 並び順を指定したいときはフォルダの `.pages` に追記する

新しいカテゴリはフォルダを作って `index.md` と `.pages` を置き、親フォルダの `.pages` に追加する。

## 公開

`main` に push すると GitHub Actions がビルドして GitHub Pages に公開する。

初回だけ、リポジトリの Settings → Pages → Source を **GitHub Actions** にする。
