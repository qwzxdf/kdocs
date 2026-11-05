---
name: sourcetree-shots
description: SourceTree の画面を UI Automation で操作して、docs/git/ 用の実寸 PNG を撮る手順（スクリプト化・失敗しても復帰）。SourceTree の画像を撮る・撮り直すときに使う。
---

# SourceTree の画像を撮る

1. `tools/README_sourcetree.md` を読む（使い方・落とし穴）。
2. 新しいルートで `python tools/st_shoot.py setup C:/sampleN`、続けて `python tools/st_shoot.py run C:/sampleN`（120 秒を超えるのでバックグラウンドで）。
3. 失敗は `!! 失敗:` と最後の「失敗した所」に出る。`with s.step('名前'):` で囲んだ所は、失敗しても `recover()` で閉じて次へ進む。
4. 結果は画像を開かず、ファイルの大きさと `git status` で確認。数枚だけ目で見る。

要点:
- 画面取得ツールは使わない（縮小 JPEG でぼやける）。`ST.shot()` が実寸 PNG を `docs/git/img/` に保存する。
- ボタンは `click_input`（Invoke は効かないことがある）。
- ダイアログ・確認ウィンドウは本体の子（別ウィンドウではない）。開きっぱなしだと右クリック メニューが出ない → `recover()`。
- 右クリック メニューは本体の子孫の `MenuItem`。メニュー バーの項目は top < 75。
- サイドバーの項目（スタッシュなど）は `double_click_input` で展開。
- オプションの「全般」タブは撮らない（本名・メールが写る）。
- 練習用フォルダーは消さず、毎回新しいルートを使う。ユーザーが自分で消す。
