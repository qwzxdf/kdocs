---
title: TAA Challenges
tags:
  - 描画
---

# TAA Challenges

TAA を入れるとジャギーが消える代わりに別の問題が出ます。走る人の背後に前の絵が尾を引く。画面全体が少しぼやける。遠くの電線が点滅する。パーティクルが二重に見える。カメラがカットした直後に前のシーンが一瞬残る。どれも原因は同じで過去のフレーム（履歴）が、今のフレームの内容と合っていないことです。このページではその原因を数字で確かめます。ゴーストがどれだけ長く残るか履歴を毎フレーム読み直すとどれだけぼけるか近傍クランプと分散クリップの違い、細い線がなぜ点滅するかを数えます。最後に、これらの対策をまとめた合成パスの HLSL を 1 本にします。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。以前のページの動く図はα = 0.05 のとき「40 フレームで見えなくなる」としていましたが、数え直すと 59 フレームなので、図は作り直しました。近傍クランプ、分散クリップなどの手法は発表・論文の内容を今回は読んでおらず考え方を自分で導いて数字で確かめたものです。

!!! tip "ポイント"
    - 履歴の混ぜる割合 α が 0.1 のとき消えた物の色は 29 フレーム（0.48 秒）で 5% 未満になります。α = 0.05 では 59 フレーム（0.98 秒）です。
    - 履歴をバイリニアで読み直すと動く縁の幅（10〜90%）は、1 フレーム 0.25 画素の動きで 3.24 画素、0.5 画素で 3.62 画素に広がります。Catmull-Rom なら 2.06 と 2.21 です。静止していれば 1.60 のままです。
    - 近傍の 3×3 の範囲に履歴を押し込むと輝度 1.0 のゴーストは 1 フレーム目に 0.420（箱のクランプ）か 0.360（分散クリップ）まで下がります。
    - 幅 0.3 画素の線を 8 フレームの Halton 列でサンプルすると、命中は 1〜3 回（平均 2.40）に揺れます。α = 0.1 では出力の揺れが平均の 35% になります。
    - 速度バッファが R8G8 で ±32 画素だと刻みは 0.251 画素で、再投影が最大 0.125 画素ずれます。R16 浮動小数点なら 8 画素付近で 0.0078 画素です。

!!! info "このページを読む前に"
    - [Anti-Aliasing](index.md)（このセクション全体の地図と読む順番）
    - [TAA](taa.md)（ジッター、再投影、合成の基本）

## 問題と原因の一覧 {#overview}

| 問題 | 原因 | 節 |
| --- | --- | --- |
| ゴースト（残像） | 履歴が現在の内容と合わない | [ゴースト](#ghost) |
| 全体のぼけ | 履歴を毎フレーム補間して読む | [ぼけ](#blur) |
| 細い物のちらつき | 1 画素以下の線が、サンプルのずれで出入りする | [細い物](#thin) |
| 半透明・パーティクル | 深度や速度が書かれない | [半透明](#transparent) |
| カット・露出の急変 | 履歴が無効になる | [カット](#reset) |
| 速度の精度 | 再投影の位置がずれる | [精度](#velocity-precision) |

## ゴースト {#ghost}

### 原因 {#ghost-cause}

画素 P に前フレームでは物 A が映っていて、今フレームでは背景 B が映るとします（A が動いて、背景が現れた）。履歴（A の色）をそのまま混ぜると、B の画素に A の色が残ります。これがゴーストです。履歴は毎フレーム `履歴' = (1 − α) × 履歴 + α × 現在` で更新されるので、消えた物の色は毎フレーム `(1 − α)` 倍に減るだけです。

### どれだけ残るか {#ghost-lifetime}

物が消えた画素の現在値を 0、履歴を 1.0 として 5% を下回るまでのフレーム数を数えました。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="ゴーストの寿命"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">α ごとのゴーストの寿命</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,60.0 78.7,155.0 87.3,202.5 96.0,226.2 104.7,238.1 113.3,244.1 122.0,247.0 130.7,248.5 139.3,249.3 148.0,249.6 156.7,249.8 165.3,249.9 174.0,250.0 182.7,250.0 191.3,250.0 200.0,250.0 208.7,250.0 217.3,250.0 226.0,250.0 234.7,250.0 243.3,250.0 252.0,250.0 260.7,250.0 269.3,250.0 278.0,250.0 286.7,250.0 295.3,250.0 304.0,250.0 312.7,250.0 321.3,250.0 330.0,250.0 338.7,250.0 347.3,250.0 356.0,250.0 364.7,250.0 373.3,250.0 382.0,250.0 390.7,250.0 399.3,250.0 408.0,250.0 416.7,250.0 425.3,250.0 434.0,250.0 442.7,250.0 451.3,250.0 460.0,250.0 468.7,250.0 477.3,250.0 486.0,250.0 494.7,250.0 503.3,250.0 512.0,250.0 520.7,250.0 529.3,250.0 538.0,250.0 546.7,250.0 555.3,250.0 564.0,250.0 572.7,250.0 581.3,250.0 590.0,250.0"/><circle cx="113.3" cy="244.1" r="4" fill="#e5484d"/><text x="119.33333333333334" y="218.5" text-anchor="start" style="font-size:11px;font-weight:700">α=0.5: 5 フレーム</text><polyline fill="none" stroke="#e5aa28" stroke-width="2.5" points="70.0,60.0 78.7,98.0 87.3,128.4 96.0,152.7 104.7,172.2 113.3,187.7 122.0,200.2 130.7,210.2 139.3,218.1 148.0,224.5 156.7,229.6 165.3,233.7 174.0,236.9 182.7,239.6 191.3,241.6 200.0,243.3 208.7,244.7 217.3,245.7 226.0,246.6 234.7,247.3 243.3,247.8 252.0,248.2 260.7,248.6 269.3,248.9 278.0,249.1 286.7,249.3 295.3,249.4 304.0,249.5 312.7,249.6 321.3,249.7 330.0,249.8 338.7,249.8 347.3,249.8 356.0,249.9 364.7,249.9 373.3,249.9 382.0,249.9 390.7,250.0 399.3,250.0 408.0,250.0 416.7,250.0 425.3,250.0 434.0,250.0 442.7,250.0 451.3,250.0 460.0,250.0 468.7,250.0 477.3,250.0 486.0,250.0 494.7,250.0 503.3,250.0 512.0,250.0 520.7,250.0 529.3,250.0 538.0,250.0 546.7,250.0 555.3,250.0 564.0,250.0 572.7,250.0 581.3,250.0 590.0,250.0"/><circle cx="191.3" cy="241.6" r="4" fill="#e5aa28"/><text x="197.33333333333331" y="218.5" text-anchor="start" style="font-size:11px;font-weight:700">α=0.2: 14 フレーム</text><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,60.0 78.7,79.0 87.3,96.1 96.0,111.5 104.7,125.3 113.3,137.8 122.0,149.0 130.7,159.1 139.3,168.2 148.0,176.4 156.7,183.8 165.3,190.4 174.0,196.3 182.7,201.7 191.3,206.5 200.0,210.9 208.7,214.8 217.3,218.3 226.0,221.5 234.7,224.3 243.3,226.9 252.0,229.2 260.7,231.3 269.3,233.2 278.0,234.8 286.7,236.4 295.3,237.7 304.0,239.0 312.7,240.1 321.3,241.1 330.0,241.9 338.7,242.8 347.3,243.5 356.0,244.1 364.7,244.7 373.3,245.2 382.0,245.7 390.7,246.1 399.3,246.5 408.0,246.9 416.7,247.2 425.3,247.5 434.0,247.7 442.7,248.0 451.3,248.2 460.0,248.3 468.7,248.5 477.3,248.7 486.0,248.8 494.7,248.9 503.3,249.0 512.0,249.1 520.7,249.2 529.3,249.3 538.0,249.4 546.7,249.4 555.3,249.5 564.0,249.5 572.7,249.6 581.3,249.6 590.0,249.7"/><circle cx="321.3" cy="241.1" r="4" fill="#2e9e5b"/><text x="327.33333333333337" y="204.5" text-anchor="start" style="font-size:11px;font-weight:700">α=0.1: 29 フレーム</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,60.0 78.7,69.5 87.3,78.5 96.0,87.1 104.7,95.2 113.3,103.0 122.0,110.3 130.7,117.3 139.3,124.0 148.0,130.3 156.7,136.2 165.3,141.9 174.0,147.3 182.7,152.5 191.3,157.3 200.0,162.0 208.7,166.4 217.3,170.6 226.0,174.5 234.7,178.3 243.3,181.9 252.0,185.3 260.7,188.5 269.3,191.6 278.0,194.5 286.7,197.3 295.3,199.9 304.0,202.4 312.7,204.8 321.3,207.1 330.0,209.2 338.7,211.3 347.3,213.2 356.0,215.0 364.7,216.8 373.3,218.4 382.0,220.0 390.7,221.5 399.3,222.9 408.0,224.3 416.7,225.6 425.3,226.8 434.0,228.0 442.7,229.1 451.3,230.1 460.0,231.1 468.7,232.1 477.3,232.9 486.0,233.8 494.7,234.6 503.3,235.4 512.0,236.1 520.7,236.8 529.3,237.5 538.0,238.1 546.7,238.7 555.3,239.3 564.0,239.8 572.7,240.3 581.3,240.8 590.0,241.2"/><circle cx="581.3" cy="240.8" r="4" fill="#4c8bf5"/><text x="587.3333333333333" y="190.5" text-anchor="start" style="font-size:11px;font-weight:700">α=0.05: 59 フレーム</text><line x1="70" y1="240.5" x2="590" y2="240.5" stroke="currentColor" stroke-dasharray="5 4"/><text x="590" y="254.5" text-anchor="end" style="font-size:11px;font-weight:400">5%(見えなくなる目安)</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="156.66666666666669" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">10</text><text x="243.33333333333334" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">20</text><text x="330.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30</text><text x="416.6666666666667" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">40</text><text x="503.3333333333333" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">50</text><text x="590.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0.0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">1.0</text><text x="330.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">物が消えてからのフレーム数</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">履歴に残る、消えた物の色の割合</text></svg>

- α = 0.50: 5 フレーム（0.08 秒）、半減期 1.0 フレーム、実効サンプル数 `(2 − α) / α` = 3.0
- α = 0.20: 14 フレーム（0.23 秒）、3.1 フレーム、9.0
- α = 0.10: 29 フレーム（0.48 秒）、6.6 フレーム、19.0
- α = 0.05: 59 フレーム（0.98 秒）、13.5 フレーム、39.0

α が小さいほどノイズは減り（実効サンプル数が増える）、ゴーストは長く残ります。α = 0.1 の 19 サンプル相当を得るために 0.48 秒の残像を許容する、という取引です。ゴーストを抑える手段は履歴を「今の見た目と合う範囲」に押し込むことです。

### 近傍クランプと分散クリップ {#clamp-clip}

履歴の色が現在の画素の近傍（3×3）の色の範囲を大きく外れていたら、その履歴は別の物のものです。そこで、履歴を近傍の範囲に押し込みます。範囲の作り方は 2 つあります。

- 最小・最大: 近傍の最小から最大まで。簡単ですが 1 つだけ外れた明るい画素に引きずられて、範囲が広がります。
- 分散クリップ: 近傍の平均 `μ` と標準偏差 `σ` から、`μ ± γσ` の範囲を作ります。γ は 1.0 から 1.25 程度です。外れ値の影響が小さく範囲が狭くなります。

近傍の輝度が `0.28, 0.30, 0.31, 0.29, 0.35, 0.27, 0.33, 0.30, 0.42` のとき（1 つだけ 0.42 が外れています）、最小は 0.270、最大は 0.420、平均は 0.3167、標準偏差は 0.0432 でした。分散クリップの範囲はγ = 1.0 で [0.2735, 0.3599]、1.25 で [0.2627, 0.3707]、1.5 で [0.2519, 0.3815] です。履歴が 1.0 のゴーストなら最小・最大の箱は 0.420 に分散クリップ（γ = 1.0）は 0.3599 に押し込みます。

押し込んだあとα = 0.1 で現在（真の色 0.3167）と混ぜたときの誤差を、フレームごとに追いました。

- クランプなし: 0.6150、0.5535、0.4981、0.4483、0.4035、0.3632、0.3268、0.2942（8 フレーム目でも 0.29 残る）
- 箱のクランプ: 0.0930、0.0837、0.0753、0.0678、0.0610、0.0549、0.0494、0.0445
- 分散クリップ: 0.0389、0.0350、0.0315、0.0283、0.0255、0.0230、0.0207、0.0186

クランプなしでは 8 フレーム経っても真の色との差が 0.29 あります。箱のクランプなら 1 フレーム目から 0.093 に下がり分散クリップはさらに半分以下の 0.039 です。外れ値の 0.42 が箱を広げている分だけ差が出ます。γ を小さくするほどゴーストは減りますが、正当な履歴まで切ってジャギーが戻ります。γ は 1.0 から 1.25 の間で調整します。

### YCoCg とクリップの向き {#ycocg}

色の範囲は RGB より YCoCg で作ったほうが自然です。輝度（Y）と色度（Co、Cg）が分かれるので箱で切ったときに色相がずれにくくなります。変換は `Y = 0.25 R + 0.5 G + 0.25 B`、`Co = 0.5 R − 0.5 B`、`Cg = −0.25 R + 0.5 G − 0.25 B` で逆変換は `R = Y + Co − Cg`、`G = Y + Cg`、`B = Y − Co − Cg` です。`(0.8, 0.3, 0.1)` を変換すると `(0.3750, 0.3500, −0.0750)` で戻すと元の値に一致しました。

箱の外へはみ出した履歴の戻し方にも 2 通りがあります。成分ごとに切る `clamp` と箱の中心へ向けて境界まで縮める `clip` です。中心 (0.3, 0.3, 0.3)、箱 [0.25, 0.35] × [0.2, 0.4] × [0.25, 0.35]、履歴 (0.9, 0.6, 0.3) で数えました。

<svg class="fig flow" viewBox="0 0 620 320" role="img" aria-label="clamp と clip"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">clamp と clip の違い</text><line x1="70" y1="260" x2="490" y2="260" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="260" x2="70" y2="30" stroke="currentColor" stroke-width="1.5"/><rect x="175.0" y="128.6" width="42.0" height="65.7" fill="rgba(76,139,245,0.25)" stroke="currentColor"/><text x="169.0" y="120.57142857142856" text-anchor="end" style="font-size:11px;font-weight:400">近傍の箱</text><line x1="196.0" y1="161.4" x2="448.0" y2="62.9" stroke="currentColor" stroke-dasharray="4 3"/><circle cx="196.0" cy="161.4" r="5" fill="#888"/><text x="186.0" y="177.42857142857142" text-anchor="start" style="font-size:11px;font-weight:700">中心</text><circle cx="448.0" cy="62.9" r="5" fill="#e5484d"/><text x="456.0" y="54.85714285714283" text-anchor="start" style="font-size:11px;font-weight:700">履歴 (0.90, 0.600)</text><circle cx="217.0" cy="128.6" r="5" fill="#e5aa28"/><text x="227.0" y="118.57142857142856" text-anchor="start" style="font-size:11px;font-weight:700">clamp (0.35, 0.400)</text><circle cx="217.0" cy="153.2" r="5" fill="#2e9e5b"/><text x="227.0" y="171.21428571428572" text-anchor="start" style="font-size:11px;font-weight:700">clip (0.35, 0.325)</text><text x="70.0" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="175.0" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">0.25</text><text x="280.0" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="385.0" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="490.0" y="278" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="264.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="198.28571428571428" text-anchor="end" style="font-size:11px;font-weight:400">0.2</text><text x="62" y="132.57142857142856" text-anchor="end" style="font-size:11px;font-weight:400">0.4</text><text x="62" y="66.85714285714283" text-anchor="end" style="font-size:11px;font-weight:400">0.6</text><text x="280.0" y="298" text-anchor="middle" style="font-size:12px;font-weight:400">R</text><text x="74" y="22" text-anchor="start" style="font-size:12px;font-weight:400">G(B は 0.3 で固定)</text></svg>

- clamp: (0.3500, 0.4000, 0.3000)。R と G を別々に切るので、G が箱の端 0.4 まで残り中心からの向きが変わります。
- clip: (0.3500, 0.3250, 0.3000)。中心から履歴へのベクトルの向きを保つので、色の比が履歴に近くなります。

clamp は履歴の G が R に比べて高い（黄みの）ことを箱の端まで残してしまい、色がずれます。clip は中心から履歴への直線上の最も近い点なので、ずれが小さくなります。

## ぼけ {#blur}

### 履歴を毎フレーム補間して読む {#bilinear-blur}

再投影で履歴を読むとき前フレームの位置は画素の中間になります。バイリニアで読むと隣の 2 画素が混ざります。この混ぜを毎フレーム繰り返すので、縁が少しずつ広がります。縁が画素の面積で被覆率を表す段差（立ち上がり幅 1.60 画素）で、右へ 1 フレーム `v` 画素動くときα = 0.1 で 200 フレーム後の縁の幅（10〜90%）を数えました。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="履歴のぼけ"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">縁の幅</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="174.0" x2="570" y2="174.0" stroke="currentColor" stroke-dasharray="5 4"/><text x="570" y="168.0" text-anchor="end" style="font-size:11px;font-weight:400">静止(動きなし)の幅 1.60</text><rect x="130" y="96.1" width="60" height="153.9" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="160" y="90.1" text-anchor="middle" style="font-size:12px;font-weight:700">3.24</text><rect x="200" y="152.1" width="60" height="97.9" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="230" y="146.14999999999998" text-anchor="middle" style="font-size:12px;font-weight:700">2.06</text><text x="195" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.25 px/フレーム</text><text x="160" y="284" text-anchor="middle" style="font-size:10px;font-weight:400">双線形</text><text x="230" y="284" text-anchor="middle" style="font-size:10px;font-weight:400">Catmull-Rom</text><rect x="350" y="78.0" width="60" height="172.0" fill="rgba(229,72,77,0.45)" stroke="currentColor"/><text x="380" y="72.04999999999998" text-anchor="middle" style="font-size:12px;font-weight:700">3.62</text><rect x="420" y="145.0" width="60" height="105.0" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="450" y="139.025" text-anchor="middle" style="font-size:12px;font-weight:700">2.21</text><text x="415" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5 px/フレーム</text><text x="380" y="284" text-anchor="middle" style="font-size:10px;font-weight:400">双線形</text><text x="450" y="284" text-anchor="middle" style="font-size:10px;font-weight:400">Catmull-Rom</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">2</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">3</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">4</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">縁の立ち上がり幅(10〜90%、画素)</text></svg>

- `v = 0`（静止）: バイリニア 1.60、Catmull-Rom 1.60
- `v = 0.25`: バイリニア 3.24、Catmull-Rom 2.06
- `v = 0.5`: バイリニア 3.62、Catmull-Rom 2.21

静止していれば履歴は動かないので、補間の影響を受けません。動くとバイリニアは縁の幅が 2 倍以上に広がります。Catmull-Rom は広がりが約 1.3〜1.4 倍で収まります。カメラや物体が動いている間は絵がぼやけて見えます。

### 対策 {#blur-fix}

- バイキュービック（Catmull-Rom）で履歴を読みます。4×4 = 16 タップが要りますが、中央の 2 タップを 1 回のバイリニアにまとめると 3×3 = 9 回の取得になり、角の 4 つを省くと 5 回になります。1 次元の「4 タップ = 3 回の取得」は、1000 点で最大差 1.33e-15 で一致しました。2 次元で 9 回は最大差 4.44e-16、角を省いた 5 回は最大差 0.0124（値の範囲 0〜1.5 のテスト画像）です。角の重みの和は最大でも 0.0156 です。
- TAA のあとに軽いシャープ フィルタ（アンシャープ マスクや CAS）を掛けます。失われた高周波を戻しますが強すぎるとちらつきを強調します。
- 現在フレームの混ぜる割合を上げます。ぼけは減りますがちらつきが増えます。

## 細い物のちらつき {#thin}

電線、フェンス、遠くの細い線は幅が 1 画素より細く、サンプルの位置次第で出たり消えたりします。TAA はジッター（Halton(2, 3)）で位置を変えるので、ある程度は平均されますが完全には消えません。幅 `w` の縦線を 8 フレームの Halton(2) の位置で点サンプルしたとき、8 フレームの命中数を線の位置を 1000 通りに変えて数えました。

- `w = 0.15`: 命中は 0〜2 回（平均 1.21、真の値 1.20）
- `w = 0.30`: 1〜3 回（平均 2.40、真の値 2.40）
- `w = 0.50`: 3〜5 回（平均 4.00、真の値 4.00）

平均は真の値に一致しますが線の位置によっては、8 フレームで見える回数が 1 回ずれます。`w = 0.3` で 8 フレームの命中が 2 回か 3 回かで、平均が 0.25 か 0.375 かに分かれます。さらに、履歴の指数移動平均が命中のある 0 / 1 の列を平均すると、出力の分散は `w (1 − w) α / (2 − α)` です。

- α = 0.10、`w = 0.15`: 標準偏差 0.0819（平均の 55%）
- α = 0.10、`w = 0.30`: 0.1051（35%）
- α = 0.05、`w = 0.15`: 0.0572（38%）
- α = 0.05、`w = 0.30`: 0.0734（24%）

α を下げると揺れは減ります。それでも細い線は平均の 2 割から 5 割の揺れが残ります。対策は描画側で細い物を太くする（距離に応じて最小の太さを保つ）、コンサバティブ ラスタライズで確実に画素に当てるジッター列の周期を伸ばす（8 を 16 に）、シャープ化を弱めるのいずれかです。

## 半透明・パーティクル {#transparent}

半透明やパーティクルには深度や速度が書かれないことが多く、TAA の再投影がうまく働きません。履歴を引く位置が背景の速度になり粒が二重に見えます。対応は 3 通りです。

1. TAA のあとに描き AA 済みの画像の上に重ねます。自身は AA されませんが安全で簡単です。
2. 半透明も速度と深度を書き TAA に参加させます。複雑です。
3. ディザリングで半透明を表現し、ノイズ的な透け具合を TAA の平均で滑らかにします。

## カットとリセット {#reset}

カメラの瞬間移動、カット、場面転換では履歴が完全に無効です。履歴を捨てます（現在の割合を 1.0 にします）。露出の急変では履歴と現在で露出をそろえるかリセットします。解像度を変えたときも履歴を作り直します。

## 速度バッファの精度 {#velocity-precision}

履歴を引く位置は速度で決まります。速度の精度が低いと再投影がずれて、履歴が少し違う場所を指しぼけやゴーストになります。R8G8 の UNORM で ±R 画素を表すと刻みは `2R / 255` です。

- ±16 画素: 刻み 0.125 画素、再投影の最大誤差 0.063 画素
- ±32 画素: 0.251 画素、0.125 画素
- ±64 画素: 0.502 画素、0.251 画素

16 ビット浮動小数点の速度は値が大きいほど刻み（ulp）が粗くなります。1 画素で 0.00098 画素、8 画素で 0.00781 画素、32 画素で 0.03125 画素、100 画素で 0.06250 画素です。ふだんの速度は 0 から数画素なので、実用上は誤差になりません。TAA の速度には `R16G16_FLOAT` を使います。

## アップスケールとの統合 {#upscale}

TAA の発展形が低解像度で描き時間的に蓄積しながら高解像度に拡大する方式（TAAU、TSR、FSR 2、DLSS）です。ジッターと履歴により元の画素数より多くの情報を取り出します。詳しい運用は[TAA、アップスケール、VRS のコスト](../taa-upscaling-cost.md)を参照してください。

## コード：合成パス {#code}

ここからコードを数行ずつ見ます。最初は定数とテクスチャです。

```hlsl
cbuffer TaaCB : register(b0) {
  float2 gScreenSize;     // 画面の幅と高さ（画素）
  float2 gInvScreenSize;  // その逆数
  float  gBaseAlpha;      // 現在フレームを混ぜる割合の基本値。例: 0.1
  float  gGamma;          // 分散クリップの γ。例: 1.0〜1.25
  float  gSharpen;        // シャープ化の強さ。0 で無効。例: 0.2
  float  gResetHistory;   // 1 なら履歴を捨てる（カット、解像度変更）
};

Texture2D<float4> gCurrent  : register(t0);   // 今フレームの色（ジッター付き）
Texture2D<float4> gHistory  : register(t1);   // 前フレームの合成結果
Texture2D<float2> gVelocity : register(t2);   // 画素単位の移動量（前の位置 = 今の位置 − 速度）
Texture2D<float>  gDepth    : register(t3);   // 深度（標準 Z: 小さいほど手前）
SamplerState gLinear : register(s0);          // 双線形・クランプ
```

`gBaseAlpha` が基本の混ぜる割合（0.1 程度）、`gGamma` が分散クリップの γ、`gSharpen` がシャープ化の強さです。`gResetHistory` はカットで履歴を捨てるためのスイッチです。速度は画素単位の移動量で前の位置は「今の位置 − 速度」です。

YCoCg の変換です。

```hlsl
// 色を YCoCg に変換する。輝度（Y）と色度（Co, Cg）に分かれるので、箱で切ったときの色ずれが目立ちにくい。
float3 RgbToYCoCg(float3 c) {
  return float3(0.25 * c.r + 0.5 * c.g + 0.25 * c.b, 0.5 * c.r - 0.5 * c.b, -0.25 * c.r + 0.5 * c.g - 0.25 * c.b);
}
float3 YCoCgToRgb(float3 c) {
  return float3(c.x + c.y - c.z, c.x + c.z, c.x - c.y - c.z);   // 逆変換: r = Y + Co − Cg、g = Y + Cg、b = Y − Co − Cg
}
```

逆変換は前の節の式です。

履歴を箱へクリップします。

```hlsl
// 履歴を箱の中心へ向けて境界までクリップする。成分ごとに切る clamp と違い、中心からの向きを保つ。
float3 ClipToAabb(float3 aabb_min, float3 aabb_max, float3 history) {
  float3 center = 0.5 * (aabb_max + aabb_min);                  // 箱の中心
  float3 extent = 0.5 * (aabb_max - aabb_min) + 1e-5;           // 半幅（ゼロ割りを避ける下限を足した）
  float3 v = history - center;                                  // 中心から履歴へのベクトル
  float3 unit = abs(v / extent);                                // 箱の半幅を 1 としたときの大きさ
  float m = max(unit.x, max(unit.y, unit.z));                   // はみ出す倍率（1 以下なら箱の中）
  return m > 1.0 ? center + v / m : history;                    // はみ出すなら、同じ向きのまま境界まで縮める
}
```

`v / m` で中心から履歴への向きを保ったまま境界まで縮めます。`+ 1e-5` は足した処理で半幅が 0 の次元（近傍の色がまったく同じ）でのゼロ割りを避けます。

履歴を Catmull-Rom で読みます。

```hlsl
// Catmull-Rom で履歴を読む。中央の 2 タップを 1 回の双線形にまとめ、角の 4 タップを省いた 5 回の取得版。
// 1 次元の「4 タップ = 3 回の取得」は一致することを確かめた。角を省いた誤差は 0.0124 程度（値の範囲 0〜1.5 のテスト画像）。
float3 SampleHistoryCatmullRom(float2 uv) {
  float2 pos = uv * gScreenSize;                                // 画素座標（中心が .5）
  float2 center = floor(pos - 0.5) + 0.5;                       // 中央の画素の中心
  float2 f = pos - center;                                      // 0〜1 の小数部
  float2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f));                 // 4 タップの重み
  float2 w1 = 1.0 + f * f * (-2.5 + 1.5 * f);
  float2 w2 = f * (0.5 + f * (2.0 - 1.5 * f));
  float2 w3 = f * f * (-0.5 + 0.5 * f);
  float2 w12 = w1 + w2;                                         // 中央 2 タップをまとめた重み
  float2 offset12 = w2 / w12;                                   // まとめた取得位置のずらし量
  float2 uv0 = (center - 1.0) * gInvScreenSize;                 // 手前の画素の uv
  float2 uv3 = (center + 2.0) * gInvScreenSize;                 // 奥の画素の uv
  float2 uv12 = (center + offset12) * gInvScreenSize;           // 中央 2 画素の間（重みに応じた位置）
  float3 result = gHistory.SampleLevel(gLinear, float2(uv12.x, uv0.y), 0).rgb * (w12.x * w0.y) +   // 上
                  gHistory.SampleLevel(gLinear, float2(uv0.x, uv12.y), 0).rgb * (w0.x * w12.y) +   // 左
                  gHistory.SampleLevel(gLinear, float2(uv12.x, uv12.y), 0).rgb * (w12.x * w12.y) + // 中央
                  gHistory.SampleLevel(gLinear, float2(uv3.x, uv12.y), 0).rgb * (w3.x * w12.y) +   // 右
                  gHistory.SampleLevel(gLinear, float2(uv12.x, uv3.y), 0).rgb * (w12.x * w3.y);    // 下
  float wsum = (w12.x * w0.y) + (w0.x * w12.y) + (w12.x * w12.y) + (w3.x * w12.y) + (w12.x * w3.y);  // 使った重みの合計
  return result / wsum;                                         // 角の重みを除いて、残りで正規化
}
```

`w0` から `w3` は 4 タップの重みで、`w12 = w1 + w2` と `offset12 = w2 / w12` で中央の 2 タップを 1 回のバイリニアにまとめます。5 回の取得で上下左右と中央を読み角の 4 つを省きます。使った重みの合計で割って全体を正規化します。省いた角の重みは小さい（和が最大 0.0156）ので、結果の差は小さいです。

ここから本体です。

```hlsl
float4 TaaResolvePS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  int2 px = int2(pos.xy);
  float3 current = gCurrent.Load(int3(px, 0)).rgb;                      // 今の色
  if (gResetHistory > 0.5) return float4(current, 1.0);                 // カットなど: 履歴を使わない
```

最初に今の色を読みます。カットなどで履歴を捨てるときはここで今の色だけを返して終わりです。

3×3 の近傍を調べます。

```hlsl
  // 3×3 の近傍の色の平均と標準偏差、一番手前の画素の位置（速度を借りる）。
  float3 m1 = 0, m2 = 0;                                                // 1 次と 2 次のモーメント（YCoCg）
  float closest_depth = 1.0;
  int2 closest = px;
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      int2 q = clamp(px + int2(x, y), int2(0, 0), int2(gScreenSize) - 1);   // 画面の端は端の値で代用（足した）
      float3 c = RgbToYCoCg(gCurrent.Load(int3(q, 0)).rgb);
      m1 += c; m2 += c * c;
      float d = gDepth.Load(int3(q, 0));
      if (d < closest_depth) { closest_depth = d; closest = q; }        // 標準 Z なので、小さい方が手前
    }
  }
  float3 mean = m1 / 9.0;
  float3 sigma = sqrt(max(m2 / 9.0 - mean * mean, 0.0));                // 分散が負になる丸め誤差を 0 に
  float3 box_min = mean - gGamma * sigma;
  float3 box_max = mean + gGamma * sigma;
```

近傍の 9 画素の色を YCoCg にして、1 次と 2 次のモーメントを足します。分散は `E[x²] − E[x]²` で丸め誤差で負になるのを `max(…, 0)` で防ぎます。同じループで一番手前の（深度が最も小さい）画素の位置を覚えます。画面の端は端の値で代用しています（足した処理です）。平均と標準偏差から箱の範囲を作ります。

速度と履歴です。

```hlsl
  // 縁の画素は、手前の物体の速度で履歴を引く（背景の速度で引くと、縁が尾を引く）。
  float2 velocity = gVelocity.Load(int3(closest, 0));                   // 画素単位
  float2 prev_uv = uv - velocity * gInvScreenSize;                      // 前フレームでの位置

  float3 history = SampleHistoryCatmullRom(prev_uv);                    // 履歴をバイキュービックで読む
  if (any(prev_uv < 0.0) || any(prev_uv > 1.0)) history = current;     // 前フレームで画面の外だった: 履歴が無い
  float3 history_clipped = YCoCgToRgb(ClipToAabb(box_min, box_max, RgbToYCoCg(history)));  // 現在の近傍の範囲へ押し込む
```

縁の画素は背景ではなく手前の物体の速度で履歴を引きます。背景の速度で引くと物体の縁が尾を引きます。前フレームの位置が画面の外なら履歴はないので現在の色を使います。履歴を読んだら近傍の箱へクリップします。

混ぜ方とシャープ化です。

```hlsl
  // 混ぜる割合。速く動く画素は履歴の信用が下がるので、現在の割合を上げる（上限 0.5）。
  float speed = length(velocity);                                       // 画素/フレーム
  float alpha = lerp(gBaseAlpha, 0.5, saturate(speed / 8.0));           // 8 画素/フレームで 0.5
  float3 resolved = lerp(history_clipped, current, alpha);

  // シャープ化: 現在の近傍の平均との差を足す。履歴の読み出しで失われた高周波を戻す（強すぎるとちらつきを強調する）。
  float3 blurred = YCoCgToRgb(mean);
  resolved = max(resolved + (resolved - blurred) * gSharpen, 0.0);      // 負の色にならないように 0 で切る（足した）
  return float4(resolved, 1.0);
}
```

速く動く画素は履歴の信用が下がるので、現在の割合を最大 0.5 まで上げます。速度が 8 画素/フレームで 0.5 です。シャープ化は現在の近傍の平均との差を足します。負の色にならないよう 0 で切ります（足した処理です）。

## よくあるミス {#mistakes}

??? failure "動く物体の後ろに長く残像が尾を引く"
    原因は履歴のクランプが弱い（または無い）ことです。α = 0.1 で消えた物の色は 29 フレーム残ります。近傍の分散クリップを入れ速度の大きい画素で現在の割合を上げます。

??? failure "TAA を入れたら、全体がぼやけた"
    原因は履歴をバイリニアで読み直していることです。動く縁の幅は 1.60 画素から 3.24 画素（0.25 画素/フレーム）に広がります。Catmull-Rom で読み軽くシャープ化します。

??? failure "細い電線が点滅する"
    原因は幅が 1 画素より細く、サンプルの位置次第で見えたり消えたりすることです。幅 0.3 画素で 8 フレームの命中が 1〜3 回に揺れます。描画側で太くするかコンサバティブ ラスタライズを使います。

??? failure "パーティクルが二重に見える"
    原因は速度と深度のない半透明を TAA の再投影に通していることです。TAA のあとに描きます。

??? failure "カット直後に前のシーンが一瞬残る"
    原因は履歴を捨てていないことです。カットのフレームは現在の割合を 1.0 にします。

??? failure "物体の縁が尾を引く"
    原因は縁の画素が背景の速度で履歴を引いていることです。3×3 で一番手前の画素の速度を使います。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] TAA の失敗は、履歴が現在と合わないことから起きる
    - [x] ゴーストは α で寿命が決まる（α = 0.1 で 29 フレーム）。近傍の分散クリップと速度による割合の調整で抑える
    - [x] 履歴の補間ぼけは Catmull-Rom で減らす（縁の幅 3.24 → 2.06）。シャープ化を併用する
    - [x] 細い線は 8 フレームで 1〜3 回の命中に揺れる。描画側で太くする
    - [x] 半透明・パーティクルは TAA のあと。カットと露出の急変で履歴をリセット

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
#include <vector>

// ---------------------------------------------------------------- 1. 履歴の指数移動平均
// history' = (1 - a) * history + a * current。物体が消えた画素(current = 0)に、履歴 1.0 が残る量を数える。
int FramesBelow(double alpha, double threshold) {
  double h = 1.0;
  int n = 0;
  while (h >= threshold) { h *= (1.0 - alpha); ++n; }   // 毎フレーム (1 - a) 倍
  return n;
}

// ---------------------------------------------------------------- 2. YCoCg と 3×3 のクリップ
struct V3 { double x, y, z; };
V3 ToYCoCg(V3 c) { return {0.25 * c.x + 0.5 * c.y + 0.25 * c.z, 0.5 * c.x - 0.5 * c.z, -0.25 * c.x + 0.5 * c.y - 0.25 * c.z}; }
V3 FromYCoCg(V3 c) { return {c.x + c.y - c.z, c.x + c.z, c.x - c.y - c.z}; }

// 履歴を AABB の中心へ向けて、境界までクリップする。clamp(各成分を独立に切る)とは違い、中心からの向きを保つ。
V3 ClipToAabb(V3 mn, V3 mx, V3 history) {
  const V3 c = {(mx.x + mn.x) / 2, (mx.y + mn.y) / 2, (mx.z + mn.z) / 2};          // 中心
  const V3 e = {(mx.x - mn.x) / 2 + 1e-5, (mx.y - mn.y) / 2 + 1e-5, (mx.z - mn.z) / 2 + 1e-5};  // 半幅
  const V3 v = {history.x - c.x, history.y - c.y, history.z - c.z};
  const double m = std::max({std::abs(v.x / e.x), std::abs(v.y / e.y), std::abs(v.z / e.z)});  // 外へどれだけはみ出すか
  if (m <= 1.0) return history;                                                  // 中なら、そのまま
  return {c.x + v.x / m, c.y + v.y / m, c.z + v.z / m};                           // 中心へ向かって境界まで縮める
}
V3 ClampToAabb(V3 mn, V3 mx, V3 h) {
  return {std::clamp(h.x, mn.x, mx.x), std::clamp(h.y, mn.y, mx.y), std::clamp(h.z, mn.z, mx.z)};
}

// ---------------------------------------------------------------- 3. バイリニアとバイキュービックの履歴ぼけ(1 次元)
// 位置 x(ピクセル中心が整数)の値を、線形補間で読む。
double SampleLinear(const std::vector<double>& a, double x) {
  const int n = static_cast<int>(a.size());
  const int i = static_cast<int>(std::floor(x));
  const double f = x - i;
  auto at = [&](int k) { return a[std::clamp(k, 0, n - 1)]; };                   // 端は端の値で延長
  return at(i) * (1.0 - f) + at(i + 1) * f;
}
// Catmull-Rom(a = -0.5)の 4 タップ。f は 0〜1 の小数部。
void CatmullRomWeights(double f, double w[4]) {
  w[0] = f * (-0.5 + f * (1.0 - 0.5 * f));
  w[1] = 1.0 + f * f * (-2.5 + 1.5 * f);
  w[2] = f * (0.5 + f * (2.0 - 1.5 * f));
  w[3] = f * f * (-0.5 + 0.5 * f);
}
double SampleCubic(const std::vector<double>& a, double x) {
  const int n = static_cast<int>(a.size());
  const int i = static_cast<int>(std::floor(x));
  double w[4];
  CatmullRomWeights(x - i, w);
  double s = 0.0;
  for (int k = 0; k < 4; ++k) s += w[k] * a[std::clamp(i - 1 + k, 0, n - 1)];
  return s;
}
// 10〜90% の立ち上がり幅(ピクセル)。
double EdgeWidth(const std::vector<double>& a) {
  double x10 = -1, x90 = -1;
  for (size_t i = 0; i + 1 < a.size(); ++i) {
    if (x10 < 0 && a[i] < 0.1 && a[i + 1] >= 0.1) x10 = i + (0.1 - a[i]) / (a[i + 1] - a[i]);
    if (x90 < 0 && a[i] < 0.9 && a[i + 1] >= 0.9) x90 = i + (0.9 - a[i]) / (a[i + 1] - a[i]);
  }
  return x90 - x10;
}

double Halton(int index, int base) {
  double r = 0.0, f = 1.0 / base;
  for (int i = index; i > 0; i /= base) { r += f * (i % base); f /= base; }
  return r;
}

int main() {
  // 1. ゴーストの寿命。
  std::printf("-- ghost lifetime (history 1.0 -> disappears below 5%%)\n");
  for (double a : {0.5, 0.2, 0.1, 0.05}) {
    std::printf("alpha %.2f: %2d frames to fall below 5%% (%.2f s at 60 fps), half-life %.1f frames, effective samples (2-a)/a = %.1f\n", a,
                FramesBelow(a, 0.05), FramesBelow(a, 0.05) / 60.0, std::log(0.5) / std::log(1.0 - a), (2.0 - a) / a);
  }

  // 2. 近傍の 3×3 と、クランプ/クリップ。近傍の色(Y の値)から 平均と標準偏差。履歴は明るいゴースト。
  std::printf("-- neighborhood clamp vs variance clip (Y channel)\n");
  const double nb[9] = {0.28, 0.30, 0.31, 0.29, 0.35, 0.27, 0.33, 0.30, 0.42};      // 近傍の輝度
  double mn = 1e9, mx = -1e9, mean = 0.0, sq = 0.0;
  for (double v : nb) { mn = std::min(mn, v); mx = std::max(mx, v); mean += v; sq += v * v; }
  mean /= 9.0;
  const double sigma = std::sqrt(sq / 9.0 - mean * mean);
  std::printf("min %.3f, max %.3f, mean %.4f, sigma %.4f\n", mn, mx, mean, sigma);
  for (double gamma : {1.0, 1.25, 1.5}) {
    std::printf("gamma %.2f: range [%.4f, %.4f]\n", gamma, mean - gamma * sigma, mean + gamma * sigma);
  }
  std::printf("history 1.0 -> box clamp %.3f; variance clip (gamma 1.0) %.4f\n", std::min(1.0, mx), std::min(1.0, mean + sigma));
  // 毎フレーム、履歴をクランプしてから alpha = 0.1 で混ぜたときの、ゴーストの残り(正解は current = mean)。
  {
    double h_box = 1.0, h_var = 1.0, h_none = 1.0;
    std::printf("frame: no clamp / box clamp / variance clip (gamma 1.0), error vs the true color %.3f:\n", mean);
    for (int f = 1; f <= 8; ++f) {
      h_none = 0.9 * h_none + 0.1 * mean;
      h_box = 0.9 * std::min(h_box, mx) + 0.1 * mean;
      h_var = 0.9 * std::min(h_var, mean + sigma) + 0.1 * mean;
      std::printf("  %d: %.4f / %.4f / %.4f\n", f, h_none - mean, h_box - mean, h_var - mean);
    }
  }
  // 色の向き: 中心 (0.3, 0.3, 0.3)、箱の半幅 (0.05, 0.1, 0.05)、履歴 (0.9, 0.6, 0.3)。clamp は成分ごとに切るので向きが変わる。
  {
    const V3 mn3 = {0.25, 0.2, 0.25}, mx3 = {0.35, 0.4, 0.35}, h = {0.9, 0.6, 0.3};
    const V3 a = ClampToAabb(mn3, mx3, h), b = ClipToAabb(mn3, mx3, h);
    std::printf("clamp -> (%.4f, %.4f, %.4f), clip -> (%.4f, %.4f, %.4f), center (0.3000, 0.3000, 0.3000)\n", a.x, a.y, a.z, b.x, b.y, b.z);
  }
  // YCoCg の往復。
  {
    const V3 c = {0.8, 0.3, 0.1};
    const V3 y = ToYCoCg(c), back = FromYCoCg(y);
    std::printf("YCoCg of (0.8, 0.3, 0.1) = (%.4f, %.4f, %.4f), back = (%.4f, %.4f, %.4f)\n", y.x, y.y, y.z, back.x, back.y, back.z);
  }

  // 3. 履歴のぼけ。縁(段差)が右へ v ピクセル/フレームで動く。毎フレーム、履歴を 位置 i - v で読み、alpha = 0.1 で現在と混ぜる。
  std::printf("-- edge blur from resampling the history (alpha 0.1, 200 frames)\n");
  const int n = 256;
  for (double v : {0.0, 0.25, 0.5}) {
    for (int mode = 0; mode < 2; ++mode) {
      std::vector<double> hist(n, 0.0), next(n, 0.0);
      for (int f = 0; f < 200; ++f) {
        const double e = 128.0 + v * f;                                    // 縁の位置
        for (int i = 0; i < n; ++i) {
          const double cur = std::clamp(i + 0.5 - e, 0.0, 1.0);            // 画素の面積による被覆率(エッジの AA 済みの値)
          const double reproj = mode == 0 ? SampleLinear(hist, i - v) : SampleCubic(hist, i - v);
          next[i] = f == 0 ? cur : 0.9 * reproj + 0.1 * cur;
        }
        hist = next;
      }
      // 現在の縁の位置を引いて、幅だけを見る。
      std::printf("v = %.2f px/frame, %s: edge width (10-90%%) = %.2f px\n", v, mode == 0 ? "bilinear " : "catmull  ", EdgeWidth(hist));
    }
  }

  // 4. 細い線のちらつき。幅 w の縦線を、Halton(2) の 8 点で点サンプリングする。線の位置(画素内のオフセット)を変えて、8 フレームの命中数を数える。
  std::printf("-- thin line, 8-frame Halton(2) cycle\n");
  for (double w : {0.15, 0.3, 0.5}) {
    int lo = 99, hi = 0;
    double mean_hits = 0.0;
    const int steps = 1000;
    for (int s = 0; s < steps; ++s) {
      const double o = static_cast<double>(s) / steps;                      // 線の左端のオフセット
      int hits = 0;
      for (int i = 1; i <= 8; ++i) {
        const double x = Halton(i, 2);                                     // その画素内のサンプル位置
        const double d = std::fmod(x - o + 1.0, 1.0);                       // 線の左端からの距離(0〜1、画素の端で回り込む)
        if (d < w) ++hits;
      }
      lo = std::min(lo, hits); hi = std::max(hi, hits); mean_hits += hits;
    }
    std::printf("w = %.2f: hits per 8 frames between %d and %d (mean %.2f, true %.2f)\n", w, lo, hi, mean_hits / steps, 8 * w);
  }
  //     EMA の出力の揺れ。入力が確率 w で 1 になる 0/1 の列のとき、出力の分散 = w (1 - w) * a / (2 - a)。
  for (double a : {0.1, 0.05}) {
    for (double w : {0.15, 0.3}) {
      const double var = w * (1.0 - w) * a / (2.0 - a);
      std::printf("alpha %.2f, w = %.2f: output sigma %.4f (relative to mean %.0f%%)\n", a, w, std::sqrt(var), std::sqrt(var) / w * 100.0);
    }
  }

  // 5. 速度バッファの精度。R8G8 UNORM で ±R ピクセルを表すときの刻みと、再投影の最大誤差。R16 浮動小数点は ulp = 2^(e - 10)。
  std::printf("-- velocity precision\n");
  for (double r : {16.0, 32.0, 64.0}) {
    const double step = 2.0 * r / 255.0;
    std::printf("R8G8 +-%2.0f px: step %.3f px, max reprojection error %.3f px\n", r, step, step / 2.0);
  }
  for (double v : {1.0, 4.0, 8.0, 32.0, 100.0}) {
    const double ulp = std::ldexp(1.0, static_cast<int>(std::floor(std::log2(v))) - 10);
    std::printf("R16F velocity %6.1f px: ulp %.5f px\n", v, ulp);
  }

  // 6. Catmull-Rom の 4 タップ(1 次元)と、中央 2 タップを 1 回の線形補間にまとめた 3 回の取得が一致する。
  std::printf("-- catmull-rom: 4 taps vs 3 fetches (center two merged into one bilinear)\n");
  {
    std::vector<double> a(16);
    for (size_t i = 0; i < a.size(); ++i) a[i] = std::sin(0.9 * i) + 0.3 * std::cos(2.1 * i);
    double worst = 0.0;
    for (int t = 0; t < 1000; ++t) {
      const double x = 4.0 + 6.0 * t / 1000.0;
      const int i = static_cast<int>(std::floor(x));
      double w[4];
      CatmullRomWeights(x - i, w);
      const double direct = SampleCubic(a, x);
      // 中央の 2 タップ(i, i+1)を、重み w1 + w2 と 位置 i + w2 / (w1 + w2) の線形補間 1 回にまとめる。
      const double w12 = w[1] + w[2], pos = i + w[2] / w12;
      const double merged = w[0] * a[i - 1] + w[3] * a[i + 2] + w12 * SampleLinear(a, pos);
      worst = std::max(worst, std::abs(direct - merged));
    }
    std::printf("worst difference over 1000 positions: %.2e\n", worst);
  }
  // 2 次元で 9 回の取得(3×3)から 角の 4 回を省いて 5 回にしたときの誤差。角の重みは w0*w0 などで小さい。
  {
    const int W = 16;
    std::vector<double> img(W * W);
    for (int y = 0; y < W; ++y) for (int x = 0; x < W; ++x) img[y * W + x] = std::sin(0.7 * x) * std::cos(0.9 * y) + 0.5;
    auto at = [&](int x, int y) { return img[std::clamp(y, 0, W - 1) * W + std::clamp(x, 0, W - 1)]; };
    auto lin2 = [&](double x, double y) {
      const int xi = static_cast<int>(std::floor(x)), yi = static_cast<int>(std::floor(y));
      const double fx = x - xi, fy = y - yi;
      return (at(xi, yi) * (1 - fx) + at(xi + 1, yi) * fx) * (1 - fy) + (at(xi, yi + 1) * (1 - fx) + at(xi + 1, yi + 1) * fx) * fy;
    };
    double worst9 = 0.0, worst5 = 0.0, wsum_corner = 0.0;
    for (int t = 0; t < 400; ++t) {
      const double x = 5.0 + (t % 20) / 20.0 * 5.0, y = 5.0 + (t / 20) / 20.0 * 5.0;
      const int xi = static_cast<int>(std::floor(x)), yi = static_cast<int>(std::floor(y));
      double wx[4], wy[4];
      CatmullRomWeights(x - xi, wx); CatmullRomWeights(y - yi, wy);
      double direct = 0.0;
      for (int j = 0; j < 4; ++j) for (int i = 0; i < 4; ++i) direct += wx[i] * wy[j] * at(xi - 1 + i, yi - 1 + j);   // 16 タップ
      const double wx12 = wx[1] + wx[2], wy12 = wy[1] + wy[2];
      const double px = xi + wx[2] / wx12, py = yi + wy[2] / wy12;
      // 9 回: 中央 1(2D 線形)+ 上下左右の 4 + 角の 4。5 回: 角の 4 を省く。
      const double center = wx12 * wy12 * lin2(px, py);
      const double up = wx12 * wy[0] * lin2(px, yi - 1), down = wx12 * wy[3] * lin2(px, yi + 2);
      const double left = wx[0] * wy12 * lin2(xi - 1, py), right = wx[3] * wy12 * lin2(xi + 2, py);
      const double corners = wx[0] * wy[0] * at(xi - 1, yi - 1) + wx[3] * wy[0] * at(xi + 2, yi - 1) + wx[0] * wy[3] * at(xi - 1, yi + 2) +
                             wx[3] * wy[3] * at(xi + 2, yi + 2);
      const double nine = center + up + down + left + right + corners;
      const double wc = wx[0] * wy[0] + wx[3] * wy[0] + wx[0] * wy[3] + wx[3] * wy[3];
      const double five = (center + up + down + left + right) / (1.0 - wc);      // 角の重みを除いて、残りで正規化
      worst9 = std::max(worst9, std::abs(direct - nine));
      worst5 = std::max(worst5, std::abs(direct - five));
      wsum_corner = std::max(wsum_corner, std::abs(wc));
    }
    std::printf("2D: 9 fetches worst error %.2e; 5 fetches (corners dropped) worst error %.4f (value range 0..1.5); largest |corner weight sum| %.4f\n", worst9, worst5, wsum_corner);
  }
}
```

```text title="実行結果"
-- ghost lifetime (history 1.0 -> disappears below 5%)
alpha 0.50:  5 frames to fall below 5% (0.08 s at 60 fps), half-life 1.0 frames, effective samples (2-a)/a = 3.0
alpha 0.20: 14 frames to fall below 5% (0.23 s at 60 fps), half-life 3.1 frames, effective samples (2-a)/a = 9.0
alpha 0.10: 29 frames to fall below 5% (0.48 s at 60 fps), half-life 6.6 frames, effective samples (2-a)/a = 19.0
alpha 0.05: 59 frames to fall below 5% (0.98 s at 60 fps), half-life 13.5 frames, effective samples (2-a)/a = 39.0
-- neighborhood clamp vs variance clip (Y channel)
min 0.270, max 0.420, mean 0.3167, sigma 0.0432
gamma 1.00: range [0.2735, 0.3599]
gamma 1.25: range [0.2627, 0.3707]
gamma 1.50: range [0.2519, 0.3815]
history 1.0 -> box clamp 0.420; variance clip (gamma 1.0) 0.3599
frame: no clamp / box clamp / variance clip (gamma 1.0), error vs the true color 0.317:
  1: 0.6150 / 0.0930 / 0.0389
  2: 0.5535 / 0.0837 / 0.0350
  3: 0.4981 / 0.0753 / 0.0315
  4: 0.4483 / 0.0678 / 0.0283
  5: 0.4035 / 0.0610 / 0.0255
  6: 0.3632 / 0.0549 / 0.0230
  7: 0.3268 / 0.0494 / 0.0207
  8: 0.2942 / 0.0445 / 0.0186
clamp -> (0.3500, 0.4000, 0.3000), clip -> (0.3500, 0.3250, 0.3000), center (0.3000, 0.3000, 0.3000)
YCoCg of (0.8, 0.3, 0.1) = (0.3750, 0.3500, -0.0750), back = (0.8000, 0.3000, 0.1000)
-- edge blur from resampling the history (alpha 0.1, 200 frames)
v = 0.00 px/frame, bilinear : edge width (10-90%) = 1.60 px
v = 0.00 px/frame, catmull  : edge width (10-90%) = 1.60 px
v = 0.25 px/frame, bilinear : edge width (10-90%) = 3.24 px
v = 0.25 px/frame, catmull  : edge width (10-90%) = 2.06 px
v = 0.50 px/frame, bilinear : edge width (10-90%) = 3.62 px
v = 0.50 px/frame, catmull  : edge width (10-90%) = 2.21 px
-- thin line, 8-frame Halton(2) cycle
w = 0.15: hits per 8 frames between 0 and 2 (mean 1.21, true 1.20)
w = 0.30: hits per 8 frames between 1 and 3 (mean 2.40, true 2.40)
w = 0.50: hits per 8 frames between 3 and 5 (mean 4.00, true 4.00)
alpha 0.10, w = 0.15: output sigma 0.0819 (relative to mean 55%)
alpha 0.10, w = 0.30: output sigma 0.1051 (relative to mean 35%)
alpha 0.05, w = 0.15: output sigma 0.0572 (relative to mean 38%)
alpha 0.05, w = 0.30: output sigma 0.0734 (relative to mean 24%)
-- velocity precision
R8G8 +-16 px: step 0.125 px, max reprojection error 0.063 px
R8G8 +-32 px: step 0.251 px, max reprojection error 0.125 px
R8G8 +-64 px: step 0.502 px, max reprojection error 0.251 px
R16F velocity    1.0 px: ulp 0.00098 px
R16F velocity    4.0 px: ulp 0.00391 px
R16F velocity    8.0 px: ulp 0.00781 px
R16F velocity   32.0 px: ulp 0.03125 px
R16F velocity  100.0 px: ulp 0.06250 px
-- catmull-rom: 4 taps vs 3 fetches (center two merged into one bilinear)
worst difference over 1000 positions: 1.33e-15
2D: 9 fetches worst error 4.44e-16; 5 fetches (corners dropped) worst error 0.0124 (value range 0..1.5); largest |corner weight sum| 0.0156
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。近傍クランプ、分散クリップ、Catmull-Rom の取得回数の削減は、一般的な手法を自分で導き数字で確かめたもので、各資料の記述との一致は確かめていません。

- Brian Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Marco Salvi, "An Excursion in Temporal Supersampling", GDC 2016
- Lasse Jon Fuglsang Pedersen, "Temporal Reprojection Anti-Aliasing in INSIDE", GDC 2016

## 関連ページ {#related}

- [Anti-Aliasing](index.md)
- [TAA](taa.md)
- [Comparison and Choosing](comparison.md)
- [TAA、アップスケール、VRS のコスト](../taa-upscaling-cost.md)
