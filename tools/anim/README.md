# 台本から動く図（SMIL アニメ）を作る手順

kdocs の「動く図」は、**台本（ストーリーボード）をデータで書き、Python が SMIL の `values` と時間を自動計算して SVG を出す**方式で作る。手で座標列を書かない。見本は `fig_forward_deferred.py`（Forward と Deferred の比較）。

## ファイル

| ファイル | 役割 |
| --- | --- |
| `storyboard.py` | ライブラリ。`Scene`・`Node`・`ReplaceBetween` |
| `fig_forward_deferred.py` | 見本。台本をデータで書いて SVG を生成し、md に差し込む |
| `forward_deferred.svg` / `.report.txt` | 生成物（git 管理外）。`.report.txt` は「誰が何秒に何をするか」の表 |

実行: `python tools/anim/fig_xxx.py docs/path/page.md`（引数の md の `<!-- fig:名前:begin -->` と `<!-- fig:名前:end -->` の間を置き換える）。引数なしなら SVG とレポートだけ出す。

## ライブラリの使い方

```python
scene = Scene("名前", 960, 540, duration=12.0, hold=1.5, still=11.5)
root = scene.root
n = root.add("rect", x=0, y=0, width=10, height=10, fill="#fff", opacity=0)
n.Set(t, "opacity", 1)            # t 秒に値が切り替わる（線形補間の ε で段差）
n.Ramp(t0, t1, "x", 100)          # t0〜t1 で線形に動く
n.Show(t0, t1)                    # 不透明度 1 の区間
n.Steps("fill", [(t, "#色"), ...])  # 離散（calcMode=discrete）。マス・色の切り替えはこれ
scene.TextStack(parent, x, y, [(t0, t1, "文"), ...])   # 区間ごとに文を出し分け
scene.Counter(parent, x, y, [(t, 値), ...])            # 数字の遷移（ライブラリが数えた値を渡す）
scene.Note(t, "誰", "何をする")   # タイミング表に出す
scene.Render() / scene.SnapshotAt(t) / scene.Report()
```

- 全アニメは同じ周期 `duration + hold` の `repeatCount="indefinite"` で、基準時刻がそろう（2 つの図の同期）。
- 台本の数字（計算回数・無駄の割合など）は**手で書かず、ループの中で数えて、`assert` で合計を確かめ、結果ボックスにもその値を出す**。

## 進め方（毎回この順）

1. **ユーザーが日本語で台本を書く**（何秒に、何が、どこへ、何が増える）。曖昧なら表にして確認する。
2. 台本を **Python のデータ**（登場物の座標・色・時刻の表と、ループ）に直す。
3. 生成して **`.report.txt` のタイミング表**を見る。数が合うか、時間が重ならないか。
4. **静止画で見た目を確認**する: `FD_SNAP` のように `scene.SnapshotAt(t)` で複数時刻の HTML を作り、ヘッドレス Edge/Chrome で PNG にして見る（`--headless --screenshot`）。
5. **本物の SMIL を実 Chrome で確認**する: 生成 SVG を HTML に入れ、`svg.pauseAnimations(); svg.setCurrentTime(t)` の後に Chrome ヘッドレス（`--headless=new --virtual-time-budget=3000`）で撮る。Edge の静止画だけで安心しない。
6. md に差し込み → `mkdocs build --strict` → アンカー検査 → push。

## 落とし穴（実際に踏んだもの）

- **`fill` を `none` ⇔ 色で離散アニメしない**（Chrome で色が出ない）。出し入れは**グループの `opacity`** か **`fill-opacity`**、色の切り替えは**色だけ**の離散アニメにする。
- SVG 内の文字は、サイトの CSS（`svg.fig text { fill: currentColor }`）に負ける。**文字色は `style="fill:..."`**（`Scene.Text` が付ける）。ダーク テーマでも読めるよう、図の背景は白い `rect` を敷く。
- SVG 内に `<` `>` `&` を直接書かない（`Escape` を通す。`<text>` に「a < b」と書くと SVG が壊れる）。
- `<svg>` の前後は**空行**（`ReplaceBetween` が入れる）。`data-fig` は図ごとに一意、クラスは `fig illust motion`。
- **アニメ要素は約 5,000 個、SVG は数 MB 以内**。マスごとの要素は「グループで 1 回出す」「色は離散 1 本」で減らす。細かすぎる格子（48×27）は重い。**28×16 程度**が目安。
- マス（ピクセル）を円で切り抜くときは、`clipPath` の半径と「マスの採否」の半径を**同じ**にする（ずれると端に前の物体のマスが漏れる）。
- 出現の前にマスが灰色に見えるときは、`fill` ではなく**親グループの `opacity=0`** を使う。
- 色を混ぜすぎない: ライトの影響は**距離だけ**で塗る（現実のライトの `N·L` は使わない）。**近いほど濃く**、範囲は狭く、最初は**全部白**。わかりやすさを優先してよい。
- 自動配置の探索は、狙った見た目（ライトの近くに球を置く）にならない。**手で座標を固定**する。

## このサイト固有の仕組み

- `docs/javascripts/motion-control.js` が `svg.motion` を**自動再生**し、画面外では止め、図の下に「⏸ 一時停止／▶ 再生」ボタンを出す。OS の「動きを減らす」設定でも自動再生する。`data-still` は使わなくなったが残してよい。
- 古い JS が残らないよう、スクリプトのファイル名を変えて配信する（キャッシュ対策）。
- ブラウザは**アプリ内ブラウザを使わない**（ユーザーの希望）。確認はヘッドレス Edge/Chrome とビルド結果で行う。`mkdocs serve`（`serve.bat`）は**止めない**（編集のたびに自動で再ビルドされる）。

## 量産用の構成（2 つ目以降の図）

| ファイル | 役割 |
| --- | --- |
| `common.py` | `NewScene`（白い背景・矢印・題名）、`Arrow`、`Caption`、`Place`（md への差し込み）、`Save` |
| `figs/*.py` | 図の定義。各関数が `dict(name, page, before | replace_fig, scene, size, times)` を返す。末尾の `FIGS` に並べる |
| `build_all.py` | 全図を生成し、md に差し込み、`out/<name>.png`（指定時刻の見本）を作る。`python tools/anim/build_all.py [図の名前...]` |
| `preview.py` | `SVG` を指定時刻で止めた画像にする（実 Chrome ヘッドレス）。`out/` は git 管理外 |

`Place` は、ページの `before` の見出しの直前に `<!-- fig:名前:begin -->` と `end` で囲んで入れる。2 回目以降は同じ範囲を置き換える。`replace_fig` を使うと、既存の `data-fig` の SVG を丸ごと置き換える。

## 追加の落とし穴（量産で踏んだもの）

- **矢印の `marker-end` は、線の `opacity=0` でも先端が見えることがある**（`stroke-dashoffset` で線を描く演出のとき）。先端は別の `polygon` を、描き終わりに `Show` する。
- **`feGaussianBlur` の `stdDeviation` を SMIL で動かしても Chrome で効かない**。ぼかしの強さが違う静的なフィルタを複数作り、重ねて不透明度でクロスフェードする。
- 自動探索（乱数＋山登り）で配置を決めると、見せたい構図にならない。座標は手で決める。
- 図ごとに**セルフチェック**する: 指定時刻の画像を 4 枚並べて、文字のはみ出し・重なり・数字の食い違い・意図した動きになっているかを見る。見つけた問題は台本側（データ）を直す。
