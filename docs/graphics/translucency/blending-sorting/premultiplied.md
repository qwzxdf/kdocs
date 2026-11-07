---
title: Premultiplied Alpha
tags:
  - 描画
---

# Premultiplied Alpha

半透明の画像を縮小したら輪郭に暗い線が出た。拡大したら白い縁取りがついた。パーティクルの火と煙を 1 つのシステムで描きたいが、加算と通常のブレンドを切り替えるとソート順が崩れる。これらは色とアルファを別々に保存しているストレート アルファに由来する問題で、色にあらかじめアルファを掛けて保存する「乗算済みアルファ」で、まとめて解決できます。このページでは縁の暗さがどれだけ出るかミップで何が起きるか層を重ねる順序が自由になる理由を数字で確かめ、sRGB と 8 ビットの落とし穴、画像の種類とブレンドの組み合わせを整理します。最後に、変換のコード、ミップを正しく作るコード、ブレンド ステート、火と煙のシェーダーをまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通し、ブレンド ステートのコードは `g++ -fsyntax-only`（mingw の `<d3d11.h>`）で構文を確かめただけで、描画した結果は確かめていません。以前のページにあった「ストレート」と「乗算済み」の補間結果が同じ数字になっている例は、説明として誤解を招くので数え直した値に置き換えました。末尾の資料は今回は読んでいません。

!!! tip "ポイント"
    - 乗算済みは色 × α を先に計算して保存します。ブレンドは `src.rgb + dst × (1 − src.a)`（ONE / INV_SRC_ALPHA）です。
    - 赤い不透明テクセルと黒が保存された透明テクセルの中間（t = 0.5）をバイリニアで読むと、ストレートは白い背景で R が 0.75 に落ちます（正解は 1.0）。乗算済みは正解どおりの 1.0 です。
    - 画像の種類とブレンド ステートが合わないと色 0.8、α = 0.5、背景 0.2 の正解 0.500 が、0.300（暗すぎる）か 0.900（明るすぎる）になります。
    - α = 0 の成分は加算、α が大きい成分は通常のブレンドとして働くので、火と煙を 1 つのブレンド ステートで描けます。
    - 乗算は sRGB のエンコードを外した（リニアの）値で行います。sRGB のまま掛けると色 0.5、α = 0.5 で 2.10 倍暗くなります。

!!! info "このページを読む前に"
    - [Alpha Blending and Sorting](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 乗算済みアルファとは {#what}

### 2 つの保存の仕方 {#two-forms}

画像の色とアルファの持ち方は 2 通りあります。ストレート（非乗算）は色とアルファをそのまま別々に保存します。乗算済みは色にアルファを掛けた値とアルファを保存します。赤でアルファ 0.5 の画素はストレートでは `(1.0, 0.0, 0.0, 0.5)`、乗算済みでは `(0.5, 0.0, 0.0, 0.5)` です。ブレンド式はそれぞれ次のようになります。

```text
ストレート : 結果 = C × α + D × (1 − α)         (SRC_ALPHA / INV_SRC_ALPHA)
乗算済み   : 結果 = C' + D × (1 − α)            (ONE / INV_SRC_ALPHA)    C' = C × α
```

乗算済みではブレンドの段階でソースにアルファを掛ける計算がなくなります。掛け算が 1 回減る以上に画像を保存するときに掛けておくことで補間、縮小、層の合成という「平均を取る」操作が、すべて正しくなる点が重要です。乗算済みの形は Smith の技術メモ（1995）で整理されていて、Porter と Duff の論文（1984）のアルファ合成の考え方に基づきます。どちらも今回は読んでいないので、ここでは式を自分で確かめます。

### カバレッジの考え方 {#coverage}

アルファは「その画素のうち物体が覆っている割合」と見なせます。覆われていない部分は背景が見えるので、結果は `覆った部分の色 + 背景 × 覆われていない割合` です。乗算済みの色 `C × α` は「覆った部分の寄与」そのものです。ストレートの色 `C` は「覆った部分の色（覆った部分で平均した色）」で、割合を掛けて初めて寄与になります。2 つの画素を混ぜるとき寄与を足し合わせるのが正しい平均です。ストレートの色を混ぜると割合を考えない平均になってしまいます。

## 縁のにじみ {#fringe}

### バイリニア補間で何が起きるか {#bilinear}

画像を縮小・拡大するとき GPU は隣り合う 2 つのテクセルを混ぜます。赤い不透明のテクセル A `(1, 0, 0, α = 1)` と完全に透明なテクセル B の間を読むとします。B は見えないはずですが画像には色の値が保存されていて、多くは黒です（書き出しツールが 0 で埋める）。

<!-- fig:premult-fringe:begin -->
<svg class="fig illust motion" data-fig="premult-fringe" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-premult-fringe" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">縁の黒い線:ストレート アルファは、補間で「透明部分の色」が混ざる</text>
<rect x="60" y="100" width="300" height="70" fill="#e5484d" stroke="#94a3b8" stroke-width="1.5"/>
<text x="210" y="90" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">テクセル A:赤・不透明（α = 1）</text>
<rect x="360" y="100" width="300" height="70" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="360" y="100" width="300" height="70" fill="#f1f5f9"/>
<text x="510" y="140" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">（透明。中の RGB は黒）</text>
<text x="510" y="90" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">テクセル B:透明（α = 0）、色は黒</text>
<text x="60" y="214" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ストレート（補間 → その後でブレンド）</text>
<rect x="60" y="230" width="25" height="40" fill="#e14a4f"/>
<rect x="85" y="230" width="25" height="40" fill="#d94f54"/>
<rect x="110" y="230" width="25" height="40" fill="#d25458"/>
<rect x="135" y="230" width="25" height="40" fill="#cc5a5d"/>
<rect x="160" y="230" width="25" height="40" fill="#c75f63"/>
<rect x="185" y="230" width="25" height="40" fill="#c36568"/>
<rect x="210" y="230" width="25" height="40" fill="#bf6b6e"/>
<rect x="235" y="230" width="25" height="40" fill="#bc7274"/>
<rect x="260" y="230" width="25" height="40" fill="#ba787a"/>
<rect x="285" y="230" width="25" height="40" fill="#b97f81"/>
<rect x="310" y="230" width="25" height="40" fill="#b88688"/>
<rect x="335" y="230" width="25" height="40" fill="#b88e8f"/>
<rect x="360" y="230" width="25" height="40" fill="#b99596"/>
<rect x="385" y="230" width="25" height="40" fill="#bb9d9e"/>
<rect x="410" y="230" width="25" height="40" fill="#bea5a6"/>
<rect x="435" y="230" width="25" height="40" fill="#c1aeae"/>
<rect x="460" y="230" width="25" height="40" fill="#c6b6b7"/>
<rect x="485" y="230" width="25" height="40" fill="#cbbfc0"/>
<rect x="510" y="230" width="25" height="40" fill="#d1c8c9"/>
<rect x="535" y="230" width="25" height="40" fill="#d7d2d2"/>
<rect x="560" y="230" width="25" height="40" fill="#dfdbdb"/>
<rect x="585" y="230" width="25" height="40" fill="#e7e5e5"/>
<rect x="610" y="230" width="25" height="40" fill="#f0efef"/>
<rect x="635" y="230" width="25" height="40" fill="#fafafa"/>
<rect x="60" y="230" width="600" height="40" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="314" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">乗算済み（先に α を掛けて保存 → 補間）</text>
<rect x="60" y="330" width="25" height="40" fill="#e64c51"/>
<rect x="85" y="330" width="25" height="40" fill="#e75358"/>
<rect x="110" y="330" width="25" height="40" fill="#e85b60"/>
<rect x="135" y="330" width="25" height="40" fill="#e96367"/>
<rect x="160" y="330" width="25" height="40" fill="#ea6a6e"/>
<rect x="185" y="330" width="25" height="40" fill="#eb7276"/>
<rect x="210" y="330" width="25" height="40" fill="#ec7a7d"/>
<rect x="235" y="330" width="25" height="40" fill="#ed8185"/>
<rect x="260" y="330" width="25" height="40" fill="#ee898c"/>
<rect x="285" y="330" width="25" height="40" fill="#ef9093"/>
<rect x="310" y="330" width="25" height="40" fill="#f0989b"/>
<rect x="335" y="330" width="25" height="40" fill="#f1a0a2"/>
<rect x="360" y="330" width="25" height="40" fill="#f3a7aa"/>
<rect x="385" y="330" width="25" height="40" fill="#f4afb1"/>
<rect x="410" y="330" width="25" height="40" fill="#f5b7b9"/>
<rect x="435" y="330" width="25" height="40" fill="#f6bec0"/>
<rect x="460" y="330" width="25" height="40" fill="#f7c6c7"/>
<rect x="485" y="330" width="25" height="40" fill="#f8cdcf"/>
<rect x="510" y="330" width="25" height="40" fill="#f9d5d6"/>
<rect x="535" y="330" width="25" height="40" fill="#faddde"/>
<rect x="560" y="330" width="25" height="40" fill="#fbe4e5"/>
<rect x="585" y="330" width="25" height="40" fill="#fcecec"/>
<rect x="610" y="330" width="25" height="40" fill="#fdf4f4"/>
<rect x="635" y="330" width="25" height="40" fill="#fefbfb"/>
<rect x="60" y="330" width="600" height="40" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60" y="222" width="25" height="156" fill="none" stroke="#e5aa28" stroke-width="3"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1037;0.1333;0.1630;0.1926;0.2222;0.2519;0.2815;0.3111;0.3407;0.3704;0.4000;0.4296;0.4593;0.4889;0.5185;0.5481;0.5778;0.6074;0.6370;0.6667;0.6963;0.7259;0.7556" values="60;60;85;110;135;160;185;210;235;260;285;310;335;360;385;410;435;460;485;510;535;560;585;610;635"/></rect>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A と B の境界をバイリニア補間で読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ストレートは、中間で「黒」が混ざって暗い縁（フリンジ）。乗算済みは、混ざらない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8145;0.8148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">→ 乗算済みアルファなら、縁が自然に薄くなるだけ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8145;0.8148;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>
<!-- fig:premult-fringe:end -->

A と B を `t : 1 − t` で混ぜます。ストレートでは色とアルファを別々に混ぜるので、色は `(1 − t, 0, 0)`、アルファは `1 − t` です。白い背景に重ねると R は `(1 − t)(1 − t) + t = 1 − t + t²` になります。正解は A を白に重ねた結果（R = 1）と B を白に重ねた結果（R = 1）の混合なので、常に 1.0 です。乗算済みでは B の色は `0 × 0 = 0` なので、混ぜると色 `(1 − t, 0, 0)`、アルファ `1 − t` で同じ背景では `(1 − t) + 1 × t = 1` になり正解と一致します。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="縁の暗さ"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">補間による縁の暗さ</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,98.0 75.0,98.0 80.0,98.0 85.0,98.0 90.0,98.0 95.0,98.0 100.0,98.0 105.0,98.0 110.0,98.0 115.0,98.0 120.0,98.0 125.0,98.0 130.0,98.0 135.0,98.0 140.0,98.0 145.0,98.0 150.0,98.0 155.0,98.0 160.0,98.0 165.0,98.0 170.0,98.0 175.0,98.0 180.0,98.0 185.0,98.0 190.0,98.0 195.0,98.0 200.0,98.0 205.0,98.0 210.0,98.0 215.0,98.0 220.0,98.0 225.0,98.0 230.0,98.0 235.0,98.0 240.0,98.0 245.0,98.0 250.0,98.0 255.0,98.0 260.0,98.0 265.0,98.0 270.0,98.0 275.0,98.0 280.0,98.0 285.0,98.0 290.0,98.0 295.0,98.0 300.0,98.0 305.0,98.0 310.0,98.0 315.0,98.0 320.0,98.0 325.0,98.0 330.0,98.0 335.0,98.0 340.0,98.0 345.0,98.0 350.0,98.0 355.0,98.0 360.0,98.0 365.0,98.0 370.0,98.0 375.0,98.0 380.0,98.0 385.0,98.0 390.0,98.0 395.0,98.0 400.0,98.0 405.0,98.0 410.0,98.0 415.0,98.0 420.0,98.0 425.0,98.0 430.0,98.0 435.0,98.0 440.0,98.0 445.0,98.0 450.0,98.0 455.0,98.0 460.0,98.0 465.0,98.0 470.0,98.0 475.0,98.0 480.0,98.0 485.0,98.0 490.0,98.0 495.0,98.0 500.0,98.0 505.0,98.0 510.0,98.0 515.0,98.0 520.0,98.0 525.0,98.0 530.0,98.0 535.0,98.0 540.0,98.0 545.0,98.0 550.0,98.0 555.0,98.0 560.0,98.0 565.0,98.0 570.0,98.0"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,98.0 75.0,101.8 80.0,105.4 85.0,109.1 90.0,112.6 95.0,116.1 100.0,119.4 105.0,122.7 110.0,126.0 115.0,129.1 120.0,132.2 125.0,135.2 130.0,138.1 135.0,141.0 140.0,143.8 145.0,146.5 150.0,149.1 155.0,151.6 160.0,154.1 165.0,156.5 170.0,158.8 175.0,161.0 180.0,163.2 185.0,165.3 190.0,167.3 195.0,169.2 200.0,171.1 205.0,172.9 210.0,174.6 215.0,176.2 220.0,177.8 225.0,179.3 230.0,180.7 235.0,182.0 240.0,183.3 245.0,184.4 250.0,185.6 255.0,186.6 260.0,187.5 265.0,188.4 270.0,189.2 275.0,189.9 280.0,190.6 285.0,191.1 290.0,191.6 295.0,192.0 300.0,192.4 305.0,192.7 310.0,192.8 315.0,193.0 320.0,193.0 325.0,193.0 330.0,192.8 335.0,192.7 340.0,192.4 345.0,192.1 350.0,191.6 355.0,191.1 360.0,190.6 365.0,189.9 370.0,189.2 375.0,188.4 380.0,187.5 385.0,186.6 390.0,185.6 395.0,184.4 400.0,183.3 405.0,182.0 410.0,180.7 415.0,179.3 420.0,177.8 425.0,176.2 430.0,174.6 435.0,172.9 440.0,171.1 445.0,169.2 450.0,167.3 455.0,165.3 460.0,163.2 465.0,161.0 470.0,158.8 475.0,156.5 480.0,154.1 485.0,151.6 490.0,149.1 495.0,146.5 500.0,143.8 505.0,141.0 510.0,138.1 515.0,135.2 520.0,132.2 525.0,129.1 530.0,126.0 535.0,122.7 540.0,119.4 545.0,116.0 550.0,112.6 555.0,109.1 560.0,105.4 565.0,101.8 570.0,98.0"/><text x="320.0" y="217.0" text-anchor="middle" style="font-size:12px;font-weight:700">ストレート: 1 − t + t²(t = 0.5 で 0.75)</text><text x="320.0" y="90.0" text-anchor="middle" style="font-size:12px;font-weight:700">乗算済み = 正解: 常に 1.0</text><circle cx="320.0" cy="193.0" r="4" fill="#e5484d"/><text x="70" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.25</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="570" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0.6</text><text x="62" y="177.99999999999997" text-anchor="end" style="font-size:11px;font-weight:400">0.8</text><text x="62" y="102.0" text-anchor="end" style="font-size:11px;font-weight:400">1.0</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">赤い不透明テクセルから、黒が保存された透明テクセルへの位置 t</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">白い背景に重ねた R(赤)チャンネル</text></svg>

- t = 0: 正解 1.0000、ストレート 1.0000、乗算済み 1.0000
- t = 0.25: 1.0000、0.8125、1.0000
- t = 0.5: 1.0000、0.7500、1.0000
- t = 0.75: 1.0000、0.8125、1.0000
- t = 1: 1.0000、1.0000、1.0000

ストレートは中間（t = 0.5）で R が 0.75 まで落ちます。白い背景では赤が暗くなる（暗いピンクの縁取り）としてまず見えます。透明なテクセルの保存色が黒でなく、白や緑なら現れる縁の色も変わります。保存色が黒、白、緑の 3 通りと白、黒の背景 2 通りで RGB の 3 チャンネルを全部数えたところストレートの最悪の誤差はどの組み合わせでも 0.25（t = 0.5）で、乗算済みはどれも 0.0000 でした。縁の色は透明なテクセルの保存色（見えないはずの値）に左右され制作ツールや書き出しの設定で変わるため、画像が変わるたびに縁の見た目が変わります。乗算済みなら保存色が何でも結果は同じです。

### 縁の色を広げる方法 {#bleed}

ストレートのまま縁の問題を避ける方法もあります。透明なテクセルの色を隣の不透明なテクセルの色で埋めておく（縁の色を広げる、ブリード）と補間しても色がずれません。この方法はテクスチャを作るツールで行いますが、ミップを作ると毎回、広げる範囲が足りなくなる場合があり手間もかかります。乗算済みならツールの設定に依存せず数式として正しい結果が得られます。

## ミップと層の合成 {#mip}

### ミップの平均 {#mip-average}

ミップを作るときは 2×2 の画素を平均します。左上が赤い不透明、残りの 3 つが透明の 2×2 を考えます。乗算済みでは色を単純に平均して `(0.25, 0, 0, α = 0.25)` で、白い背景に重ねると `0.25 + 0.75 = 1.0` で正解です。ストレートで単純平均すると透明な 3 つの保存色が混ざります。数えた結果は次のとおりです。

- 保存色が黒: 平均の色は `(0.250, 0.000, 0.000)`、アルファ 0.25
- 白: `(1.000, 0.750, 0.750)`
- マゼンタ: `(1.000, 0.000, 0.750)`

どれも白と黒の背景で重ねると、最悪の誤差が 0.1875 になりました。乗算済みはすべて 0 です。ストレートで正しく平均するには色を α で重みづけして足し、アルファの和で割る必要があります。乗算済みなら 4 成分を同じ重みで平均するだけで済みます。

```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Rgba8 { uint8_t r, g, b, a; };               // 画像 1 画素。r, g, b は sRGB でエンコードされた 8 ビット、a はリニアな 8 ビット

// sRGB(0〜1)からリニアへ、リニアから sRGB へ。
float SrgbToLinear(float c) { return c <= 0.04045f ? c / 12.92f : std::pow((c + 0.055f) / 1.055f, 2.4f); }
float LinearToSrgb(float c) { return c <= 0.0031308f ? c * 12.92f : 1.055f * std::pow(c, 1.0f / 2.4f) - 0.055f; }

struct LinearPremult { float r, g, b, a; };          // リニア空間で色にアルファを掛けた画素(float で持つ)

// ストレートの sRGB 画像を、リニア空間の乗算済みにする。
// 順序が肝心: sRGB をデコード → アルファを掛ける → (ミップを作る) → 必要なら sRGB へエンコード。
// sRGB の値のまま掛けると、0.5 × 0.5 でリニアでは 0.0509 になり、正しい 0.1070 の約半分に暗くなる。
LinearPremult Premultiply(Rgba8 p) {
  const float a = p.a / 255.0f;                                  // アルファは、もともとリニア
  return {SrgbToLinear(p.r / 255.0f) * a, SrgbToLinear(p.g / 255.0f) * a, SrgbToLinear(p.b / 255.0f) * a, a};
}

// 2×2 の平均でミップを 1 段下げる。乗算済みなら、4 成分を同じ重みで平均するだけで正しい。
// (ストレートなら、色を a で重みづけして平均し、最後に a の合計で割る必要がある。)
std::vector<LinearPremult> Downsample(const std::vector<LinearPremult>& src, int w, int h) {
  std::vector<LinearPremult> dst(static_cast<size_t>(w / 2) * (h / 2));
  for (int y = 0; y < h / 2; ++y) {
    for (int x = 0; x < w / 2; ++x) {
      LinearPremult sum = {0, 0, 0, 0};
      for (int dy = 0; dy < 2; ++dy) {
        for (int dx = 0; dx < 2; ++dx) {
          const LinearPremult& s = src[static_cast<size_t>(2 * y + dy) * w + (2 * x + dx)];
          sum.r += s.r; sum.g += s.g; sum.b += s.b; sum.a += s.a;   // 単純に足す
        }
      }
      dst[static_cast<size_t>(y) * (w / 2) + x] = {sum.r / 4, sum.g / 4, sum.b / 4, sum.a / 4};   // 4 で割る
    }
  }
  return dst;
}

// 乗算済みのリニアを、sRGB の 8 ビットとして格納する(ここでは乗算済みの色を sRGB へエンコード)。
// GPU は sRGB テクスチャをデコードしてから補間するので、リニアの乗算済みが得られる。
Rgba8 EncodePremult(LinearPremult p) {
  auto q = [](float v) { return static_cast<uint8_t>(std::lround(std::clamp(v, 0.0f, 1.0f) * 255.0f)); };
  return {q(LinearToSrgb(p.r)), q(LinearToSrgb(p.g)), q(LinearToSrgb(p.b)), q(p.a)};
}

int main() {
  // 2×2 の画像: 左上が不透明の赤、残りは透明で、保存された色は黒。
  std::vector<Rgba8> img = {{255, 0, 0, 255}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};
  std::vector<LinearPremult> pm;
  for (const Rgba8& p : img) pm.push_back(Premultiply(p));
  const std::vector<LinearPremult> mip = Downsample(pm, 2, 2);
  const LinearPremult m = mip[0];
  std::printf("mip 1x1 premult linear = (%.4f, %.4f, %.4f, a = %.4f)\n", m.r, m.g, m.b, m.a);
  std::printf("blend onto white: R = %.4f (want 0.25 + 0.75 = 1.0000), G = %.4f (want 0.75)\n", m.r + 1.0f * (1.0f - m.a),
              m.g + 1.0f * (1.0f - m.a));
  const Rgba8 e = EncodePremult(m);
  std::printf("encoded sRGB8 = (%d, %d, %d, %d)\n", e.r, e.g, e.b, e.a);

  // 色を sRGB のまま掛けた場合との差。色 128 (sRGB 0.502)、アルファ 128 (0.502)。
  const Rgba8 gray = {128, 128, 128, 128};
  const LinearPremult right = Premultiply(gray);
  const float wrong = SrgbToLinear(128.0f / 255.0f * (128.0f / 255.0f));          // sRGB のまま掛けてからデコード(誤り)
  std::printf("gray 128, alpha 128: right linear premult = %.4f, wrong (multiplied in sRGB) = %.4f, ratio %.2f\n", right.r, wrong,
              right.r / wrong);
}
```

`Downsample` は 4 画素を足して 4 で割るだけです。乗算済みだからできる単純な処理で、ミップの全段にこの式を使います。

### 層を重ねる順序 {#associativity}

乗算済みの合成式（`over`）は結合法則を満たします。2 つの層を先にまとめてから背景に重ねても、順に背景に重ねても同じ結果になります。層 1（色 0.6、α 0.4）、層 2（色 0.2、α 0.7）、背景 0.9 で数えると `(L1 over L2) over bg` と `L1 over (L2 over bg)` はどちらも 0.486000 で一致し、まとめた層のアルファは 0.820 でした。結合法則が成り立つので遠い層を先にまとめておく（キャッシュしたり別のレンダー ターゲットに描いたりする）ことが、結果を変えずにできます。パーティクルの一部を別のターゲットに低解像度で描いて、あとで合成する方法（[Low Resolution Effects](../../pipeline/low-res-effects.md)）は、この性質を使っています。

アルファは層を重ねるごとに蓄積します。α = 0.5 の層を n 枚重ねたときの出力のアルファは、n = 1 から 5 で 0.5000、0.7500、0.8750、0.9375、0.9688 で閉じた式 `1 − 0.5ⁿ` と一致しました。そのため、ブレンド ステートのアルファ側も色と同じ ONE / INV_SRC_ALPHA にそろえます。

## 加算と通常を 1 つの式で {#additive}

乗算済みの式 `結果 = C' + D × (1 − α)` でα = 0 にすると `C' + D` で、加算ブレンドそのものです。α = 1 なら `C'` で不透明な上書きです。α が途中なら通常の半透明です。1 つのブレンド ステートで、加算も通常も表せます。火が燃え尽きて煙に変わるパーティクルをアルファだけを動かして連続的に変えられます。次の例は背景 0.3 の上にアルファを 1.0 から 0.0 まで下げたときの結果です（煙の寄与 0.5 × 0.6 と、火の寄与の合計が `c_premult` です）。

- α = 1.0: 結果 0.300
- α = 0.6: 0.580
- α = 0.3: 0.790
- α = 0.0: 1.000

α を下げるほど背景（0.3）の寄与が増えながら、色の寄与も増えて明るくなります。α を 0 にすると純粋な加算になります。ソート順は変えずに描くパスも 1 つで済みます。

## 画像の種類とブレンドの組み合わせ {#combinations}

画像の種類（ストレートか乗算済みか）とブレンド ステート（SRC_ALPHA か ONE か）が合わないと、結果がずれます。色 0.8、α = 0.5、背景 0.2 で数えました。正解は `0.8 × 0.5 + 0.2 × 0.5 = 0.500` です。

<svg class="fig flow" viewBox="0 0 660 310" role="img" aria-label="画像とブレンドの組み合わせ"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">画像の種類とブレンドの組み合わせ</text><line x1="70" y1="250" x2="590" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><rect x="100" y="155.0" width="70" height="95.0" fill="#2e9e5b" opacity="0.45" stroke="currentColor"/><text x="135" y="149.0" text-anchor="middle" style="font-size:12px;font-weight:700">0.500</text><text x="135" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">ストレート</text><text x="135" y="284" text-anchor="middle" style="font-size:11px;font-weight:400">+ SRC_ALPHA</text><rect x="225" y="155.0" width="70" height="95.0" fill="#2e9e5b" opacity="0.45" stroke="currentColor"/><text x="260" y="149.0" text-anchor="middle" style="font-size:12px;font-weight:700">0.500</text><text x="260" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">乗算済み</text><text x="260" y="284" text-anchor="middle" style="font-size:11px;font-weight:400">+ ONE</text><rect x="350" y="193.0" width="70" height="57.0" fill="#e5484d" opacity="0.45" stroke="currentColor"/><text x="385" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700">0.300</text><text x="385" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">乗算済み</text><text x="385" y="284" text-anchor="middle" style="font-size:11px;font-weight:400">+ SRC_ALPHA</text><rect x="475" y="79.0" width="70" height="171.0" fill="#e5484d" opacity="0.45" stroke="currentColor"/><text x="510" y="73.0" text-anchor="middle" style="font-size:12px;font-weight:700">0.900</text><text x="510" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">ストレート</text><text x="510" y="284" text-anchor="middle" style="font-size:11px;font-weight:400">+ ONE</text><line x1="70" y1="155.0" x2="590" y2="155.0" stroke="currentColor" stroke-dasharray="5 4"/><text x="590" y="149.0" text-anchor="end" style="font-size:11px;font-weight:400">正解 0.5</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0.0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">1.0</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">結果(色 0.8、α = 0.5、背景 0.2)</text></svg>

- ストレートの画像 + SRC_ALPHA: 0.500（正解）
- 乗算済みの画像 + ONE: 0.500（正解）
- 乗算済みの画像 + SRC_ALPHA: 0.300（暗すぎる。アルファが二重に掛かる）
- ストレートの画像 + ONE: 0.900（明るすぎる。アルファが掛からない）

以前のページには「ストレートの画像を乗算済みのブレンドで描くと縁に黒い線が出る」と書いてありましたが、数字を見るとそうなりません。ストレートの画像を ONE で描くとアルファが掛からず縁の半透明な画素の色がそのまま足されるので、明るい縁（白い縁取り）が出ます。暗い縁が出るのは逆（乗算済みの画像を SRC_ALPHA で描いた）の場合です。縁が明るいか暗いかでどちらの組み合わせの誤りか見分けられます。

UI ライブラリではフォントやアイコンを乗算済みにするものが多いです。画像がどちらの形式かをライブラリごとに確認します。

## 精度の落とし穴 {#pitfalls}

### 8 ビットで乗算済みにすると、色の段階が減る {#precision}

乗算済みの色は `C × α` なのでα が小さいと色の値は小さい範囲に押し込まれます。8 ビット（0 から 255）で保存すると、元の色を表せる段階は `floor(255 × α) + 1` 個です。

<svg class="fig flow" viewBox="0 0 660 290" role="img" aria-label="8ビットの精度"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">乗算済みの精度</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><rect x="90" y="60.0" width="50" height="190.0" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="115" y="54.0" text-anchor="middle" style="font-size:12px;font-weight:700">256</text><text x="115" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">α=1</text><rect x="168" y="155.0" width="50" height="95.0" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="193" y="149.0" text-anchor="middle" style="font-size:12px;font-weight:700">128</text><text x="193" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">α=0.5</text><rect x="246" y="202.5" width="50" height="47.5" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="271" y="196.5" text-anchor="middle" style="font-size:12px;font-weight:700">64</text><text x="271" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">α=0.25</text><rect x="324" y="230.7" width="50" height="19.3" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="349" y="224.703125" text-anchor="middle" style="font-size:12px;font-weight:700">26</text><text x="349" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">α=0.1</text><rect x="402" y="240.4" width="50" height="9.6" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="427" y="234.3515625" text-anchor="middle" style="font-size:12px;font-weight:700">13</text><text x="427" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">α=0.05</text><rect x="480" y="245.5" width="50" height="4.5" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="505" y="239.546875" text-anchor="middle" style="font-size:12px;font-weight:700">6</text><text x="505" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">α=0.02</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">128</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">256</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">元の色を表せる段階数(8 ビットで乗算済みにしたとき)</text></svg>

- α = 1.00: 256 段階
- 0.50: 128 段階
- 0.25: 64 段階
- 0.10: 26 段階
- 0.05: 13 段階
- 0.02: 6 段階

半透明が薄い領域（煙の縁、グラデーションの端）では元の色をわずかな段階でしか表せません。色の変化が必要なら 16 ビット浮動小数点（`R16G16B16A16_FLOAT`）のテクスチャを使うかアルファが薄い領域では色が見えにくいことを許容します。8 ビットのストレートなら色は全域で 256 段階あります。

### sRGB の画像をエンコードされた値のまま乗算しない {#srgb}

色の画像が sRGB でエンコードされているとき GPU の sRGB テクスチャは、読むときにリニアへデコードしてから補間します。乗算済みはリニア空間で乗算してから sRGB に戻した値を保存する必要があります。sRGB のまま掛けると結果が暗くなります。色 0.5（sRGB）、α = 0.5 で数えました。

- sRGB のまま掛ける（誤り）: エンコード値 0.2500 は、デコードしたリニア値で 0.0509
- リニアで掛ける（正解）: リニア 0.1070（エンコード値 0.3608）

誤りは正解より 2.10 倍暗くなります。画像の処理ツールが sRGB のまま乗算する設定になっていないか確認します。次のコードは sRGB をデコードして、リニアで α を掛けミップを作り再エンコードする流れです。

```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Rgba8 { uint8_t r, g, b, a; };               // 画像 1 画素。r, g, b は sRGB でエンコードされた 8 ビット、a はリニアな 8 ビット

// sRGB(0〜1)からリニアへ、リニアから sRGB へ。
float SrgbToLinear(float c) { return c <= 0.04045f ? c / 12.92f : std::pow((c + 0.055f) / 1.055f, 2.4f); }
float LinearToSrgb(float c) { return c <= 0.0031308f ? c * 12.92f : 1.055f * std::pow(c, 1.0f / 2.4f) - 0.055f; }

struct LinearPremult { float r, g, b, a; };          // リニア空間で色にアルファを掛けた画素(float で持つ)

// ストレートの sRGB 画像を、リニア空間の乗算済みにする。
// 順序が肝心: sRGB をデコード → アルファを掛ける → (ミップを作る) → 必要なら sRGB へエンコード。
// sRGB の値のまま掛けると、0.5 × 0.5 でリニアでは 0.0509 になり、正しい 0.1070 の約半分に暗くなる。
LinearPremult Premultiply(Rgba8 p) {
  const float a = p.a / 255.0f;                                  // アルファは、もともとリニア
  return {SrgbToLinear(p.r / 255.0f) * a, SrgbToLinear(p.g / 255.0f) * a, SrgbToLinear(p.b / 255.0f) * a, a};
}

// 2×2 の平均でミップを 1 段下げる。乗算済みなら、4 成分を同じ重みで平均するだけで正しい。
// (ストレートなら、色を a で重みづけして平均し、最後に a の合計で割る必要がある。)
std::vector<LinearPremult> Downsample(const std::vector<LinearPremult>& src, int w, int h) {
  std::vector<LinearPremult> dst(static_cast<size_t>(w / 2) * (h / 2));
  for (int y = 0; y < h / 2; ++y) {
    for (int x = 0; x < w / 2; ++x) {
      LinearPremult sum = {0, 0, 0, 0};
      for (int dy = 0; dy < 2; ++dy) {
        for (int dx = 0; dx < 2; ++dx) {
          const LinearPremult& s = src[static_cast<size_t>(2 * y + dy) * w + (2 * x + dx)];
          sum.r += s.r; sum.g += s.g; sum.b += s.b; sum.a += s.a;   // 単純に足す
        }
      }
      dst[static_cast<size_t>(y) * (w / 2) + x] = {sum.r / 4, sum.g / 4, sum.b / 4, sum.a / 4};   // 4 で割る
    }
  }
  return dst;
}

// 乗算済みのリニアを、sRGB の 8 ビットとして格納する(ここでは乗算済みの色を sRGB へエンコード)。
// GPU は sRGB テクスチャをデコードしてから補間するので、リニアの乗算済みが得られる。
Rgba8 EncodePremult(LinearPremult p) {
  auto q = [](float v) { return static_cast<uint8_t>(std::lround(std::clamp(v, 0.0f, 1.0f) * 255.0f)); };
  return {q(LinearToSrgb(p.r)), q(LinearToSrgb(p.g)), q(LinearToSrgb(p.b)), q(p.a)};
}

int main() {
  // 2×2 の画像: 左上が不透明の赤、残りは透明で、保存された色は黒。
  std::vector<Rgba8> img = {{255, 0, 0, 255}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};
  std::vector<LinearPremult> pm;
  for (const Rgba8& p : img) pm.push_back(Premultiply(p));
  const std::vector<LinearPremult> mip = Downsample(pm, 2, 2);
  const LinearPremult m = mip[0];
  std::printf("mip 1x1 premult linear = (%.4f, %.4f, %.4f, a = %.4f)\n", m.r, m.g, m.b, m.a);
  std::printf("blend onto white: R = %.4f (want 0.25 + 0.75 = 1.0000), G = %.4f (want 0.75)\n", m.r + 1.0f * (1.0f - m.a),
              m.g + 1.0f * (1.0f - m.a));
  const Rgba8 e = EncodePremult(m);
  std::printf("encoded sRGB8 = (%d, %d, %d, %d)\n", e.r, e.g, e.b, e.a);

  // 色を sRGB のまま掛けた場合との差。色 128 (sRGB 0.502)、アルファ 128 (0.502)。
  const Rgba8 gray = {128, 128, 128, 128};
  const LinearPremult right = Premultiply(gray);
  const float wrong = SrgbToLinear(128.0f / 255.0f * (128.0f / 255.0f));          // sRGB のまま掛けてからデコード(誤り)
  std::printf("gray 128, alpha 128: right linear premult = %.4f, wrong (multiplied in sRGB) = %.4f, ratio %.2f\n", right.r, wrong,
              right.r / wrong);
}
```

`Premultiply` は色をデコードしてから α を掛けます。α は最初からリニアな割合なので、デコードしません。

```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Rgba8 { uint8_t r, g, b, a; };               // 画像 1 画素。r, g, b は sRGB でエンコードされた 8 ビット、a はリニアな 8 ビット

// sRGB(0〜1)からリニアへ、リニアから sRGB へ。
float SrgbToLinear(float c) { return c <= 0.04045f ? c / 12.92f : std::pow((c + 0.055f) / 1.055f, 2.4f); }
float LinearToSrgb(float c) { return c <= 0.0031308f ? c * 12.92f : 1.055f * std::pow(c, 1.0f / 2.4f) - 0.055f; }

struct LinearPremult { float r, g, b, a; };          // リニア空間で色にアルファを掛けた画素(float で持つ)

// ストレートの sRGB 画像を、リニア空間の乗算済みにする。
// 順序が肝心: sRGB をデコード → アルファを掛ける → (ミップを作る) → 必要なら sRGB へエンコード。
// sRGB の値のまま掛けると、0.5 × 0.5 でリニアでは 0.0509 になり、正しい 0.1070 の約半分に暗くなる。
LinearPremult Premultiply(Rgba8 p) {
  const float a = p.a / 255.0f;                                  // アルファは、もともとリニア
  return {SrgbToLinear(p.r / 255.0f) * a, SrgbToLinear(p.g / 255.0f) * a, SrgbToLinear(p.b / 255.0f) * a, a};
}

// 2×2 の平均でミップを 1 段下げる。乗算済みなら、4 成分を同じ重みで平均するだけで正しい。
// (ストレートなら、色を a で重みづけして平均し、最後に a の合計で割る必要がある。)
std::vector<LinearPremult> Downsample(const std::vector<LinearPremult>& src, int w, int h) {
  std::vector<LinearPremult> dst(static_cast<size_t>(w / 2) * (h / 2));
  for (int y = 0; y < h / 2; ++y) {
    for (int x = 0; x < w / 2; ++x) {
      LinearPremult sum = {0, 0, 0, 0};
      for (int dy = 0; dy < 2; ++dy) {
        for (int dx = 0; dx < 2; ++dx) {
          const LinearPremult& s = src[static_cast<size_t>(2 * y + dy) * w + (2 * x + dx)];
          sum.r += s.r; sum.g += s.g; sum.b += s.b; sum.a += s.a;   // 単純に足す
        }
      }
      dst[static_cast<size_t>(y) * (w / 2) + x] = {sum.r / 4, sum.g / 4, sum.b / 4, sum.a / 4};   // 4 で割る
    }
  }
  return dst;
}

// 乗算済みのリニアを、sRGB の 8 ビットとして格納する(ここでは乗算済みの色を sRGB へエンコード)。
// GPU は sRGB テクスチャをデコードしてから補間するので、リニアの乗算済みが得られる。
Rgba8 EncodePremult(LinearPremult p) {
  auto q = [](float v) { return static_cast<uint8_t>(std::lround(std::clamp(v, 0.0f, 1.0f) * 255.0f)); };
  return {q(LinearToSrgb(p.r)), q(LinearToSrgb(p.g)), q(LinearToSrgb(p.b)), q(p.a)};
}

int main() {
  // 2×2 の画像: 左上が不透明の赤、残りは透明で、保存された色は黒。
  std::vector<Rgba8> img = {{255, 0, 0, 255}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};
  std::vector<LinearPremult> pm;
  for (const Rgba8& p : img) pm.push_back(Premultiply(p));
  const std::vector<LinearPremult> mip = Downsample(pm, 2, 2);
  const LinearPremult m = mip[0];
  std::printf("mip 1x1 premult linear = (%.4f, %.4f, %.4f, a = %.4f)\n", m.r, m.g, m.b, m.a);
  std::printf("blend onto white: R = %.4f (want 0.25 + 0.75 = 1.0000), G = %.4f (want 0.75)\n", m.r + 1.0f * (1.0f - m.a),
              m.g + 1.0f * (1.0f - m.a));
  const Rgba8 e = EncodePremult(m);
  std::printf("encoded sRGB8 = (%d, %d, %d, %d)\n", e.r, e.g, e.b, e.a);

  // 色を sRGB のまま掛けた場合との差。色 128 (sRGB 0.502)、アルファ 128 (0.502)。
  const Rgba8 gray = {128, 128, 128, 128};
  const LinearPremult right = Premultiply(gray);
  const float wrong = SrgbToLinear(128.0f / 255.0f * (128.0f / 255.0f));          // sRGB のまま掛けてからデコード(誤り)
  std::printf("gray 128, alpha 128: right linear premult = %.4f, wrong (multiplied in sRGB) = %.4f, ratio %.2f\n", right.r, wrong,
              right.r / wrong);
}
```

`EncodePremult` はミップを作ったあとのリニアの乗算済みを sRGB の 8 ビットに戻します。2×2 の例（左上が赤の不透明、残りは黒の透明）ではミップの結果が `(0.2500, 0, 0, 0.2500)` で、白い背景に重ねると R = 1.0000、G = 0.7500 で正解と一致しました。エンコードすると赤は 137、アルファは 64 です。

### ミップは乗算してから作る {#mip-order}

ストレートでミップを作ってから、シェーダーで `rgb *= a` しても縁の問題は消えません。ミップの中ですでに保存色が混ざっているからです。画像ファイルを作る段階かロード時にミップを作る前に乗算済みにします。

## ブレンド ステート {#blend-state}

乗算済みのブレンドとストレートのブレンドを作る関数です。構文は確かめましたが実行はしていません。

```cpp
#include <d3d11.h>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

// 乗算済みアルファのブレンド ステート。結果 = src.rgb + dst.rgb * (1 - src.a)。
// ソースにはアルファを掛けない(掛け済みなので ONE)。
ComPtr<ID3D11BlendState> CreatePremultipliedBlend(ID3D11Device* device) {
  D3D11_BLEND_DESC desc = {};                                   // 全部 0 で初期化
  D3D11_RENDER_TARGET_BLEND_DESC& rt = desc.RenderTarget[0];
  rt.BlendEnable = TRUE;
  rt.SrcBlend = D3D11_BLEND_ONE;                                // ソースの色: そのまま
  rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;                     // 背景: (1 - src.a) 倍
  rt.BlendOp = D3D11_BLEND_OP_ADD;
  rt.SrcBlendAlpha = D3D11_BLEND_ONE;                           // アルファも同じ式。出力のアルファが 1 - (1-a1)(1-a2)... と蓄積する
  rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
  rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
  ComPtr<ID3D11BlendState> state;
  if (FAILED(device->CreateBlendState(&desc, &state))) return nullptr;
  return state;
}

// ストレート アルファのブレンド ステート。結果 = src.rgb * src.a + dst.rgb * (1 - src.a)。
ComPtr<ID3D11BlendState> CreateStraightBlend(ID3D11Device* device) {
  D3D11_BLEND_DESC desc = {};
  D3D11_RENDER_TARGET_BLEND_DESC& rt = desc.RenderTarget[0];
  rt.BlendEnable = TRUE;
  rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;                          // ソースの色にアルファを掛ける
  rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOp = D3D11_BLEND_OP_ADD;
  rt.SrcBlendAlpha = D3D11_BLEND_ONE;                           // アルファの蓄積は乗算済みと同じにそろえる
  rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
  rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
  ComPtr<ID3D11BlendState> state;
  if (FAILED(device->CreateBlendState(&desc, &state))) return nullptr;
  return state;
}
```

`SrcBlend = ONE` でソースの色をそのまま足し、`DestBlend = INV_SRC_ALPHA` で背景を `1 − α` 倍にします。アルファ側（`SrcBlendAlpha`、`DestBlendAlpha`）も同じ ONE / INV_SRC_ALPHA で、前の節のアルファの蓄積になります。

```cpp
#include <d3d11.h>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

// 乗算済みアルファのブレンド ステート。結果 = src.rgb + dst.rgb * (1 - src.a)。
// ソースにはアルファを掛けない(掛け済みなので ONE)。
ComPtr<ID3D11BlendState> CreatePremultipliedBlend(ID3D11Device* device) {
  D3D11_BLEND_DESC desc = {};                                   // 全部 0 で初期化
  D3D11_RENDER_TARGET_BLEND_DESC& rt = desc.RenderTarget[0];
  rt.BlendEnable = TRUE;
  rt.SrcBlend = D3D11_BLEND_ONE;                                // ソースの色: そのまま
  rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;                     // 背景: (1 - src.a) 倍
  rt.BlendOp = D3D11_BLEND_OP_ADD;
  rt.SrcBlendAlpha = D3D11_BLEND_ONE;                           // アルファも同じ式。出力のアルファが 1 - (1-a1)(1-a2)... と蓄積する
  rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
  rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
  ComPtr<ID3D11BlendState> state;
  if (FAILED(device->CreateBlendState(&desc, &state))) return nullptr;
  return state;
}

// ストレート アルファのブレンド ステート。結果 = src.rgb * src.a + dst.rgb * (1 - src.a)。
ComPtr<ID3D11BlendState> CreateStraightBlend(ID3D11Device* device) {
  D3D11_BLEND_DESC desc = {};
  D3D11_RENDER_TARGET_BLEND_DESC& rt = desc.RenderTarget[0];
  rt.BlendEnable = TRUE;
  rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;                          // ソースの色にアルファを掛ける
  rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOp = D3D11_BLEND_OP_ADD;
  rt.SrcBlendAlpha = D3D11_BLEND_ONE;                           // アルファの蓄積は乗算済みと同じにそろえる
  rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
  rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
  ComPtr<ID3D11BlendState> state;
  if (FAILED(device->CreateBlendState(&desc, &state))) return nullptr;
  return state;
}
```

ストレートでは `SrcBlend = SRC_ALPHA` に変えるだけです。アルファの蓄積は乗算済みと同じ式にそろえています。

## シェーダー {#shader}

ここからシェーダーを数行ずつ見ます。最初はテクスチャと定数です。

```hlsl
Texture2D    gTex  : register(t0);        // 乗算済みで保存した RGBA（sRGB テクスチャなら、リニアの乗算済みを sRGB にエンコードしたもの）
SamplerState gSamp : register(s0);

cbuffer ParticleCB : register(b0) {
  float3 gFireColor;      // 火の色（リニア、HDR）。例: (4.0, 1.6, 0.4)
  float  gSmokeAlpha;     // 煙の最大アルファ。例: 0.6
  float3 gSmokeColor;     // 煙の色（リニア）。例: (0.25, 0.25, 0.25)
  float  gPad;            // 詰め物
};
```

`gTex` は乗算済みで保存した RGBA です。パーティクルの色はリニアで HDR の値（火は 1 を超える）を渡します。

変換の関数です。

```hlsl
// ストレート → 乗算済み。ブレンドの前に必ず 1 回だけ掛ける。2 回掛けると二重に暗くなる。
float4 Premultiply(float4 c) {
  return float4(c.rgb * c.a, c.a);        // 色にアルファを掛ける。アルファはそのまま
}

// 乗算済み → ストレート。ガンマ補正や色調整など、色そのものを触りたいときに使う。
float4 Unpremultiply(float4 c) {
  return float4(c.rgb / max(c.a, 1e-4), c.a);   // α が 0 のとき割れないよう下限を足した（足した処理）
}
```

`Premultiply` はブレンドの前に 1 回だけ掛けます。2 回掛けると二重に暗くなります。`Unpremultiply` は色そのものを触りたいとき（色調整、ガンマ）に乗算済みを一度ストレートに戻すためのものです。`max(c.a, 1e-4)` は足した処理でα が 0 の画素のゼロ除算を避けます。

火から煙に移るパーティクルです。

```hlsl
// 火から煙へ。1 つのパーティクルで、加算（火）から通常のアルファ（煙）へ連続して移る。
// 返すのは乗算済み: α が 0 の成分は加算、α が大きい成分は通常のブレンドとして働く。
float4 FireSmokePS(float4 pos : SV_Position, float2 uv : TEXCOORD0, float life : TEXCOORD1) : SV_Target {
  float shape = gTex.Sample(gSamp, uv).a;                           // 形（粒の輪郭）。乗算済みテクスチャのアルファ
  float fire_amount = saturate(1.0 - life * 2.0);                   // 寿命の前半だけ火。life = 0 で 1、0.5 で 0
  float smoke_alpha = gSmokeAlpha * saturate(life * 2.0) * (1.0 - saturate(life * 2.0 - 1.0));  // 煙は中盤に最大、終盤で消える
  float3 smoke = gSmokeColor * smoke_alpha;                         // 煙の色にアルファを掛け済み（乗算済み）
  float3 fire = gFireColor * fire_amount;                           // 火は、アルファに掛けない。背景に足すだけ（加算）
  float alpha = smoke_alpha * shape;                                // 出力のアルファ。火は寄与しない
  return float4((smoke + fire) * shape, alpha);                     // 形（shape）は色とアルファの両方に掛ける
}
```

`fire_amount` は寿命の前半だけ 1 から 0 に落ちる火の量です。`smoke_alpha` は中盤で最大、終盤で 0 に戻る煙の濃さです。煙の色にはアルファを掛けておきます（乗算済み）。火はアルファに寄与させず色だけを足します。この組み合わせでα = 0 の部分は加算、α の大きい部分は通常のブレンドになります。出力のアルファは煙の分だけです。`shape` は粒の形で色とアルファの両方に掛けます。

UI の例です。

```hlsl
// UI。乗算済みのテクスチャを、頂点色（ストレートのティント）で染める。
// 色は rgb だけでなく、アルファも一緒に掛ける。そうしないと、ティントを暗くしたときにアルファだけが残る。
float4 UiPS(float4 pos : SV_Position, float2 uv : TEXCOORD0, float4 tint : COLOR0) : SV_Target {
  float4 c = gTex.Sample(gSamp, uv);                  // 乗算済み
  float4 t = Premultiply(tint);                       // ティントも乗算済みにしてから掛ける
  return c * t;                                       // 乗算済み同士の積は、乗算済みのまま
}
```

乗算済みのテクスチャに頂点の色（ティント）を掛けるときティントも先に乗算済みにします。そうしないとティントのアルファを下げたときに色が暗くならずアルファだけが下がる、ちぐはぐな結果になります。乗算済み同士の積は乗算済みのままです。

## よくあるミス {#mistakes}

??? failure "半透明テクスチャの縁に黒い線が出る"
    原因はストレートの画像を補間していて、透明なテクセルの黒が混ざっていることです。t = 0.5 で R が 0.75 まで落ちます。乗算済みにするか縁の色を広げます。

??? failure "UI の絵の縁が明るく光る"
    原因はストレートの画像を ONE / INV_SRC_ALPHA で描いていることです。アルファが掛からず色がそのまま足されます（0.900）。画像かブレンド ステートのどちらかをそろえます。

??? failure "UI の絵が全体に暗い縁が黒い"
    原因は乗算済みの画像を SRC_ALPHA で描いていることです。アルファが二重に掛かります（0.300）。

??? failure "ミップの縁が、遠くで色づいて見える"
    原因はストレートでミップを作ったことで、透明なテクセルの保存色が混ざっていることです。乗算してからミップを作ります（`rgb *= a` をシェーダーでやっても遅い）。

??? failure "sRGB の画像を乗算したら、縁が暗くなった"
    原因は sRGB のエンコードされた値のままアルファを掛けていることです。リニアで掛けてから sRGB に戻します。色 0.5、α = 0.5 で 2.10 倍暗くなります。

??? failure "薄い煙の縁で、色が段になって見える"
    原因は 8 ビットの乗算済みで、α が小さい領域の色の段階が少ないことです。α = 0.1 で 26 段階です。浮動小数点のテクスチャにするか煙の色の変化をアルファが小さい所で使わないようにします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 乗算済みは色 × α を保存する。ブレンドは `src.rgb + dst × (1 − src.a)`（ONE / INV_SRC_ALPHA）
    - [x] 補間とミップが、乗算済みなら正しい。ストレートは t = 0.5 で縁が暗くなる（R が 0.75）
    - [x] 画像の種類とブレンドは必ず合わせる。合わないと 0.300 か 0.900（正解 0.500）
    - [x] α = 0 で加算、α が大きいと通常のブレンド。1 つのステートで火も煙も描ける
    - [x] sRGB はリニアで掛けて戻す。8 ビットでは α が小さいと段階が減る

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <vector>

struct Rgba { double r, g, b, a; };

// sRGB(0〜1)からリニアへ、リニアから sRGB へ。IEC 61966-2-1 の式。
double SrgbToLinear(double c) { return c <= 0.04045 ? c / 12.92 : std::pow((c + 0.055) / 1.055, 2.4); }
double LinearToSrgb(double c) { return c <= 0.0031308 ? c * 12.92 : 1.055 * std::pow(c, 1.0 / 2.4) - 0.055; }

// ストレート アルファのブレンド: src.rgb * src.a + dst * (1 - src.a)。ブレンド ステートは SRC_ALPHA / INV_SRC_ALPHA。
double BlendStraight(double c, double a, double dst) { return c * a + dst * (1.0 - a); }
// 乗算済みのブレンド: src.rgb + dst * (1 - src.a)。ブレンド ステートは ONE / INV_SRC_ALPHA。
double BlendPremult(double c_premult, double a, double dst) { return c_premult + dst * (1.0 - a); }

Rgba Lerp(Rgba x, Rgba y, double t) {
  return {x.r + (y.r - x.r) * t, x.g + (y.g - x.g) * t, x.b + (y.b - x.b) * t, x.a + (y.a - x.a) * t};
}

int main() {
  // 1. 縁のにじみ。テクセル A = 赤(1,0,0)・不透明。テクセル B = 完全に透明で、保存されている色(junk)は黒・白・緑のどれか。
  //    2 つのテクセルの間をバイリニア補間(重み t)して、背景(白または黒)にブレンドする。
  //    正解は「各テクセルを別々に背景へ重ねてから、面積の重み t で混ぜる」(カバレッジの考え方)。RGB の 3 チャンネルすべてで誤差を見る。
  std::printf("-- fringe: A = opaque red, B = transparent with junk color; worst channel error over the background\n");
  struct Junk { const char* name; double r, g, b; };
  for (const Junk& j : {Junk{"black", 0, 0, 0}, Junk{"white", 1, 1, 1}, Junk{"green", 0, 1, 0}}) {
    for (double bg : {1.0, 0.0}) {                                               // 背景: 白 / 黒
      double worst_straight = 0.0, worst_premult = 0.0, at_t = 0.0;
      for (int i = 0; i <= 100; ++i) {
        const double t = i / 100.0;                                              // A から B への位置
        const double a_c[3] = {1, 0, 0}, b_c[3] = {j.r, j.g, j.b};
        for (int ch = 0; ch < 3; ++ch) {
          const double truth = (1.0 - t) * BlendStraight(a_c[ch], 1.0, bg) + t * BlendStraight(b_c[ch], 0.0, bg);   // 各テクセルを重ねてから混ぜる
          const double sc = a_c[ch] + (b_c[ch] - a_c[ch]) * t, sa = 1.0 - t;       // ストレートの補間(色とアルファを別々に)
          const double pc = a_c[ch] * (1.0 - t), pa = 1.0 - t;                     // 乗算済みの補間(B は色 0)
          const double es = std::abs(BlendStraight(sc, sa, bg) - truth);
          const double ep = std::abs(BlendPremult(pc, pa, bg) - truth);
          if (es > worst_straight) { worst_straight = es; at_t = t; }
          worst_premult = std::max(worst_premult, ep);
        }
      }
      std::printf("junk %-5s over %s: straight worst error %.4f (at t = %.2f), premult worst error %.4f\n", j.name, bg > 0.5 ? "white" : "black",
                  worst_straight, at_t, worst_premult);
    }
  }
  // 代表例: junk 黒、白背景、R チャンネル。
  std::printf("-- fringe detail: junk black, white background, R channel\n");
  for (double t : {0.0, 0.25, 0.5, 0.75, 1.0}) {
    const double truth = 1.0;                                                    // 赤も白も R = 1
    const double straight = BlendStraight(1.0 - t, 1.0 - t, 1.0);                // 色 (1-t)、α (1-t)
    const double premult = BlendPremult(1.0 - t, 1.0 - t, 1.0);
    std::printf("t = %.2f: truth %.4f, straight %.4f, premult %.4f\n", t, truth, straight, premult);
  }

  // 2. 層を重ねる順序。乗算済みなら (L1 over L2) over bg == L1 over (L2 over bg)。結合法則。
  std::printf("-- associativity of over (premultiplied)\n");
  {
    const double c1 = 0.6 * 0.4, a1 = 0.4;     // 層 1: 色 0.6、α 0.4 を掛け済み
    const double c2 = 0.2 * 0.7, a2 = 0.7;     // 層 2: 色 0.2、α 0.7 を掛け済み
    const double bg = 0.9;
    // L1 over L2: 色 = c1 + c2 (1 - a1)、α = a1 + a2 (1 - a1)
    const double c12 = c1 + c2 * (1.0 - a1), a12 = a1 + a2 * (1.0 - a1);
    const double left = BlendPremult(c12, a12, bg);                              // (L1 over L2) over bg
    const double right = BlendPremult(c1, a1, BlendPremult(c2, a2, bg));        // L1 over (L2 over bg)
    std::printf("(L1 over L2) over bg = %.6f, L1 over (L2 over bg) = %.6f, alpha of L1 over L2 = %.3f\n", left, right, a12);
  }

  // 3. ミップ(2x2 の平均)。左上だけ赤の不透明、残り 3 つは透明で、保存色(junk)が黒・白・マゼンタ。
  //    ストレートの単純平均は junk の色が混ざる。乗算済みなら junk は 0 なので混ざらない。白背景と黒背景で最大の誤差を見る。
  std::printf("-- mip average of 2x2 (1 opaque red + 3 transparent texels)\n");
  for (const Junk& j : {Junk{"black", 0, 0, 0}, Junk{"white", 1, 1, 1}, Junk{"magenta", 1, 0, 1}}) {
    const double s_c[3] = {(1.0 + 3.0 * j.r) / 4.0, (0.0 + 3.0 * j.g) / 4.0, (0.0 + 3.0 * j.b) / 4.0};  // ストレートの平均(色)
    const double s_a = 0.25;                                                     // α の平均
    const double p_c[3] = {0.25, 0.0, 0.0};                                      // 乗算済みの平均(色 × α の平均)
    for (double bg : {1.0, 0.0}) {
      double es = 0.0, ep = 0.0;
      const double want[3] = {0.25 * 1.0 + 0.75 * bg, 0.75 * bg, 0.75 * bg};       // 正解: 赤 25% + 背景 75%
      for (int ch = 0; ch < 3; ++ch) {
        es = std::max(es, std::abs(BlendStraight(s_c[ch], s_a, bg) - want[ch]));
        ep = std::max(ep, std::abs(BlendPremult(p_c[ch], s_a, bg) - want[ch]));
      }
      std::printf("junk %-7s over %s: straight mip color (%.3f, %.3f, %.3f) -> worst error %.4f; premult worst error %.4f\n", j.name,
                  bg > 0.5 ? "white" : "black", s_c[0], s_c[1], s_c[2], es, ep);
    }
  }

  // 4. 加算ブレンドとの両立。premult.a = 0 なら 結果 = C' + D。
  std::printf("-- additive via alpha = 0\n");
  for (double a : {1.0, 0.6, 0.3, 0.0}) {
    const double c_premult = 0.5 * 0.6 + 0.4 * (1.0 - a);   // 煙の色(0.5)×α 0.6 と、火の色の分(0.4 を α の減る分だけ)
    std::printf("alpha %.1f: out = %.3f over dst 0.3\n", a, BlendPremult(c_premult, a, 0.3));
  }

  // 5. 8 ビットの乗算済みの精度。α が小さいと、元の色を何段階で表せるか。
  std::printf("-- 8-bit levels of the original color after premultiplication\n");
  for (double a : {1.0, 0.5, 0.25, 0.1, 0.05, 0.02}) {
    std::printf("alpha %.2f: %3d levels of straight color (max k = floor(255 * a))\n", a, static_cast<int>(std::floor(255.0 * a)) + 1);
  }

  // 6. sRGB のテクスチャを、エンコードされた値のまま乗算してはいけない。色 0.5 (sRGB)、α = 0.5。
  std::printf("-- premultiplying in the wrong color space (color 0.5 sRGB, alpha 0.5)\n");
  {
    const double c = 0.5, a = 0.5;
    const double wrong_enc = c * a;                                    // sRGB のまま掛ける(誤り)
    const double wrong_lin = SrgbToLinear(wrong_enc);                  // GPU がデコードして読む値
    const double right_lin = SrgbToLinear(c) * a;                      // リニアで掛ける(正しい)
    std::printf("wrong: encoded %.4f -> linear %.4f; right: linear %.4f (encoded %.4f); wrong is %.2fx darker\n", wrong_enc, wrong_lin,
                right_lin, LinearToSrgb(right_lin), right_lin / wrong_lin);
  }

  // 7. 画像の種類とブレンドの組み合わせ。色 0.8、α 0.5、背景 0.2。正解は 0.8*0.5 + 0.2*0.5 = 0.5。
  std::printf("-- image type x blend state (C = 0.8, a = 0.5, dst = 0.2)\n");
  {
    const double c = 0.8, a = 0.5, d = 0.2;
    std::printf("straight image + SRC_ALPHA blend:   %.3f (correct)\n", BlendStraight(c, a, d));
    std::printf("premult image  + ONE blend:         %.3f (correct)\n", BlendPremult(c * a, a, d));
    std::printf("premult image  + SRC_ALPHA blend:   %.3f (too dark: alpha applied twice)\n", BlendStraight(c * a, a, d));
    std::printf("straight image + ONE blend:         %.3f (too bright: alpha not applied)\n", BlendPremult(c, a, d));
  }

  // 8. 出力のアルファの蓄積。α = 0.5 の層を n 枚重ねたときのアルファ(カバレッジ) = 1 - (1 - a)^n。
  std::printf("-- accumulated alpha of n layers of alpha 0.5\n");
  for (int n = 1; n <= 5; ++n) {
    double acc = 0.0;
    for (int i = 0; i < n; ++i) acc = acc + 0.5 * (1.0 - acc);          // DestBlendAlpha = INV_SRC_ALPHA, SrcBlendAlpha = ONE
    std::printf("n = %d: %.4f (closed form %.4f)\n", n, acc, 1.0 - std::pow(0.5, n));
  }
}
```

```text title="実行結果"
-- fringe: A = opaque red, B = transparent with junk color; worst channel error over the background
junk black over white: straight worst error 0.2500 (at t = 0.50), premult worst error 0.0000
junk black over black: straight worst error 0.2500 (at t = 0.50), premult worst error 0.0000
junk white over white: straight worst error 0.2500 (at t = 0.50), premult worst error 0.0000
junk white over black: straight worst error 0.2500 (at t = 0.50), premult worst error 0.0000
junk green over white: straight worst error 0.2500 (at t = 0.50), premult worst error 0.0000
junk green over black: straight worst error 0.2500 (at t = 0.50), premult worst error 0.0000
-- fringe detail: junk black, white background, R channel
t = 0.00: truth 1.0000, straight 1.0000, premult 1.0000
t = 0.25: truth 1.0000, straight 0.8125, premult 1.0000
t = 0.50: truth 1.0000, straight 0.7500, premult 1.0000
t = 0.75: truth 1.0000, straight 0.8125, premult 1.0000
t = 1.00: truth 1.0000, straight 1.0000, premult 1.0000
-- associativity of over (premultiplied)
(L1 over L2) over bg = 0.486000, L1 over (L2 over bg) = 0.486000, alpha of L1 over L2 = 0.820
-- mip average of 2x2 (1 opaque red + 3 transparent texels)
junk black   over white: straight mip color (0.250, 0.000, 0.000) -> worst error 0.1875; premult worst error 0.0000
junk black   over black: straight mip color (0.250, 0.000, 0.000) -> worst error 0.1875; premult worst error 0.0000
junk white   over white: straight mip color (1.000, 0.750, 0.750) -> worst error 0.1875; premult worst error 0.0000
junk white   over black: straight mip color (1.000, 0.750, 0.750) -> worst error 0.1875; premult worst error 0.0000
junk magenta over white: straight mip color (1.000, 0.000, 0.750) -> worst error 0.1875; premult worst error 0.0000
junk magenta over black: straight mip color (1.000, 0.000, 0.750) -> worst error 0.1875; premult worst error 0.0000
-- additive via alpha = 0
alpha 1.0: out = 0.300 over dst 0.3
alpha 0.6: out = 0.580 over dst 0.3
alpha 0.3: out = 0.790 over dst 0.3
alpha 0.0: out = 1.000 over dst 0.3
-- 8-bit levels of the original color after premultiplication
alpha 1.00: 256 levels of straight color (max k = floor(255 * a))
alpha 0.50: 128 levels of straight color (max k = floor(255 * a))
alpha 0.25:  64 levels of straight color (max k = floor(255 * a))
alpha 0.10:  26 levels of straight color (max k = floor(255 * a))
alpha 0.05:  13 levels of straight color (max k = floor(255 * a))
alpha 0.02:   6 levels of straight color (max k = floor(255 * a))
-- premultiplying in the wrong color space (color 0.5 sRGB, alpha 0.5)
wrong: encoded 0.2500 -> linear 0.0509; right: linear 0.1070 (encoded 0.3608); wrong is 2.10x darker
-- image type x blend state (C = 0.8, a = 0.5, dst = 0.2)
straight image + SRC_ALPHA blend:   0.500 (correct)
premult image  + ONE blend:         0.500 (correct)
premult image  + SRC_ALPHA blend:   0.300 (too dark: alpha applied twice)
straight image + ONE blend:         0.900 (too bright: alpha not applied)
-- accumulated alpha of n layers of alpha 0.5
n = 1: 0.5000 (closed form 0.5000)
n = 2: 0.7500 (closed form 0.7500)
n = 3: 0.8750 (closed form 0.8750)
n = 4: 0.9375 (closed form 0.9375)
n = 5: 0.9688 (closed form 0.9688)
```

画像の変換とミップ（全体）の実行結果です。

```text title="実行結果"
mip 1x1 premult linear = (0.2500, 0.0000, 0.0000, a = 0.2500)
blend onto white: R = 1.0000 (want 0.25 + 0.75 = 1.0000), G = 0.7500 (want 0.75)
encoded sRGB8 = (137, 0, 0, 64)
gray 128, alpha 128: right linear premult = 0.1084, wrong (multiplied in sRGB) = 0.0517, ratio 2.10
```

## 参考資料 {#references}

このページの数字と式は C++ で数え直したものです。以下の資料は**今回は読んでいません**。式はブレンド式から自分で導き数字で確かめました。

- Alvy Ray Smith, "Image Compositing Fundamentals", Microsoft Technical Memo 4, 1995（乗算済みアルファ）
- Thomas Porter, Tom Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（`SrcBlend`、`DestBlend`、`BlendOp`）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、合成の章）

## 関連ページ {#related}

- [Alpha Blending and Sorting](index.md)
- [Blend State](blend-state.md)
- [Soft Particles](soft-particles.md)
- [Sorting](sorting.md)
