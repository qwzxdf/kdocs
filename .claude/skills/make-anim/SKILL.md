---
name: make-anim
description: kdocs の動く図(SMIL アニメ)を、台本から Python で生成して md に差し込み、確認して push するまでの手順。アニメ・動く図・比較アニメを作るときに使う。
---

`tools/anim/README.md` を読んで、そのとおりに進める。

1. ユーザーに日本語の台本(何秒に、何が、どこへ、何が増えるか)を書いてもらう。曖昧なら表で確認する。
2. `tools/anim/storyboard.py` を使い、`tools/anim/fig_forward_deferred.py` を見本に新しい `fig_<名前>.py` を作る。数字はループで数えて assert する。
3. 生成して `.report.txt` のタイミング表を確認する。
4. `SnapshotAt` の静止画(ヘッドレス Edge)と、実 Chrome での SMIL 描画(`setCurrentTime`)で見た目を確認する。
5. md の `<!-- fig:名前:begin -->`〜`end` に差し込み、`mkdocs build --strict`、`check_anchors.py` を通して push する。

落とし穴: `fill` の `none` 離散アニメは Chrome で効かない。SVG の文字色は style で指定する。アプリ内ブラウザは使わない。`mkdocs serve` は止めない。
