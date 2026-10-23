# STL ページを作る道具（作業用。サイトには出ない）

STL の「1 項目 1 ページ」を保つための道具です。計画のメモは `plan.md`、使った一括生成の台本は `b01.py` 〜 `b22.py` です。

## 足りないものを探す

| コマンド | 何を調べるか |
| --- | --- |
| `python tools/stl/inventory.py [ヘッダ名]` | 標準ライブラリの名前の一覧（`inventory.py` の `INV`）のうち、`docs/stl` に見出し・ファイル名・title が無いもの |
| `python tools/stl/members.py [ページ名]` | 主なクラスのメンバ関数（`members.py` の `MEMBERS`）のうち、そのクラスのページに `###` 見出しが無いもの |
| `python tools/stl/chk.py` | `docs/stl` の md の相対リンクの切れ（`mkdocs build` は 6 分前後かかるので、先にこれで確かめる） |

一覧に名前を足すときは、`INV` の該当ヘッダの文字列に空白区切りで足します。名前だけを見るので、別のヘッダの同じ名前（`std::get` など）で「ある」と判断されることがあります。その場合は、フォルダを指定して調べます。

## ページを作る

`mk.py` に部品があります。

- `P(...)`: 1 ページを作る。`hub=` を渡すと、まとめページの表に行を足す。
- `Q(...)`: 型どおりの関数 1 つのページを、短く作る近道（C の関数、型特性など）。
- `add_secs(ページ, 節)`: 既存のページに、`###` の節を足す（同じ id があれば足さない）。
- `add_list(...)`: 表のないまとめページに、リンクの表を足す。
- 本文中の `(@/basics/x.md)` は、docs からのパスとして相対パスに直る。

`b19.py` / `b20.py` / `b21.py` は、メンバ関数の節を `GEN`（共通の説明）と `SPEC`（クラスごとの説明）から足す台本です。

## 分ける

`b18.py` が、1 ページにまとまっていたものを分けた台本です。節は `drop_sections` で消し、`record_moves` で `moves.json` に記録します。その後 `python tools/stl/fix_links.py` で、他のページのリンクを新しいページに付け替えます。

## 仕上げ

```bash
python tools/stl/gen_index.py --pages   # 各フォルダの .pages
python tools/stl/gen_index.py           # docs/stl/index.md
python tools/stl/chk.py
mkdocs build --strict
```
