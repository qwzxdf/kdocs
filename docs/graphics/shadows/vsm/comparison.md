---
title: Comparison with PCF
tags:
  - 描画
---

# Comparison with PCF

影をなめらかにしたいとき、最初に思いつくのは PCF です。シャドウ マップを何点も読んで平均を取るだけなので、仕組みが素直で光漏れもありません。ところがぼかしを広げようとすると、読む点の数が半径の 2 乗で増えていきます。そこで「比べる前にシャドウ マップのほうをぼかしておけないか」と考えたのが、VSM・ESM・EVSM・MSM です。

この 4 方式はどれも、深度をそのまま持たずに、ぼかしても意味が壊れない値へ変換して保存します。そのかわり、ぼかした値から影の割合を「推定」することになるので、推定が外れたときに光漏れが出ます。このページでは、PCF と 4 方式を読み込みの回数・メモリ・外れ方の 3 つの軸で並べます。最後に、判定関数を同じ形で並べて、数値を入れて試した結果を載せます。

!!! tip "ポイント"
    - PCF は比較してから平均するので、ぼかしの幅に比例して読み込みが増えます。VSM 系は平均してから式で割合を出すので、画素あたりの読み込みは 1 回です。
    - そのかわり VSM 系は、ぼかしのパスとメモリ（2〜4 倍）を払います。画面が小さくぼかしが狭いなら PCF のほうが安くなる場合があります。
    - 4 方式の違いは推定が外れるときの見え方です。VSM は光漏れ ESM は受け手が遮蔽物の近くにあるときの不安定さ EVSM はその両方を弱めた形、MSM は 4 つのモーメントで外れを小さくした形です。
    - どれが速いかは論文の測定ではメモリの量でほぼ決まっていました。

!!! info "このページを読む前に"
    - [VSM, ESM and MSM](index.md)（このセクションの地図。Chebyshev の不等式と VSM の仕組みはここ）
    - [PCF](../pcf.md)（比較する相手。比較サンプラーでの書き方はここ）

## 比較の軸 {#axes}

最初に 4 方式が何を保存するのかを並べます。ここに載せたビット数は MSM の論文が図の説明に書いた値です。PCF は図 6 の 16 ビット深度、VSM と ESM は図 1 の「1 テクセル 32 ビット」です。EVSM のビット数は読んだ範囲に書かれていなかったので空けています。

| 手法 | 保存する値 | チャンネル | 論文の図での 1 テクセル | 外れ方 |
| --- | --- | --- | --- | --- |
| PCF | 深度 z | 1 | 16 ビット（図 6） | 外れない（広いと重い） |
| VSM | z、z² | 2 | 32 ビット（図 1） | 光漏れ |
| ESM | exp(c·z) | 1 | 32 ビット（図 1） | 縁で不安定 |
| EVSM | exp(±c·z) とその 2 乗 | 4 | 記述なし | 弱い光漏れ |
| MSM | z、z²、z³、z⁴ | 4 | 64 ビット（16 × 4） | 短い距離でノイズ |

「外れ方」の列は、MSM の論文の関連研究と結果の節を、私が短くまとめたものです。くわしくは [それぞれの外れ方](#failures) で書きます。

## PCF が払うもの {#pcf-cost}

PCF はシャドウ マップの周りの k×k 点について、受け手の深度と比べた結果（0 か 1）を平均します。比べる相手が受け手の深度なので、比較は画素ごとにしかできません。シャドウ マップを先にぼかしておく、ということができないのです。深度を先にぼかしてしまうと遮蔽物の縁で「手前と奥の中間の深度」ができて、そこで比較が成り立たなくなります。

GPU Gems 3 の第 8 章は、PCF の弱点を 2 つ挙げています。1 つは最悪の場合にフィルタ範囲のすべてのテクセルを読んで比べる必要があることです。もう 1 つはバイアスでフィルタの範囲のなかの深度の差を全部覆う量が要るため、決めにくいと書いています。VSM 系では分散に下限を置くことで、バイアスの問題が多くの場合に消えます。

ハードウェアの比較サンプラーを使うと 1 回の読み込みで周りの 2×2 テクセルを比べて双線形に混ぜた値が返ります。MSM の論文は実装では PCF のサンプル数をこの機能で 4 分の 1 にしている、と測定の節に注記しています。このページの見積もりではそのような割引を入れていません。

## フィルタ可能にするという考え方 {#filterable}

VSM 系が「ぼかせる」理由を論文は次のように説明しています。PCF のフィルタはカーネルのなかから確率的に深度を 1 つ選ぶことと見なせます。そのときの深度の分布を Z とすると、PCF が求めているのは「選んだ深度が受け手の深度 z_f より小さい確率」、つまり Z の累積分布関数 F_Z(z_f) です。

ここでシャドウ マップに深度 z の代わりに b(z) という値を書いておきます。同じカーネルでぼかすと得られるのは b(z) の期待値です。期待値は線形の演算（平均、ミップ、ガウス ぼかし異方性フィルタ、MSAA）で保てます。この期待値から F_Z(z_f) の下限を式で計算するのが、VSM 系の共通の骨格です。b(z) を何にするかで方式が分かれます。論文では次のとおりです。

- VSM は b(z) = (z、z²) です。Chebyshev の不等式で下限を出します。
- ESM は b(z) = exp(c·z) です（c は 1 より十分大きい定数）。Markov の不等式で下限を出します。
- EVSM は VSM を exp(c·z) と exp(−c·z) の 2 通りに適用して、暗いほうを使います。
- MSM は b(z) = (z、z²、z³、z⁴) です。4 つのモーメントを満たす分布のなかで、最も鋭い下限を計算します。

下限を使うので、推定は影を「濃く見積もりすぎない」方向に外れます。論文の評価の節も、この種の手法の誤差は光漏れの形でしか出ないと書いています。

<svg class="fig flow" viewBox="0 0 660 250" role="img" aria-label="PCF と VSM 系の処理の順番"><defs><marker id="m1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">比べる順番の違い</text><text x="360" y="44" text-anchor="middle" style="font-size:13px;font-weight:700">画素ごとに比べてから平均する（PCF）</text><rect x="16" y="56" width="130" height="44" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="81.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">深度を 1 点読む</text><rect x="176" y="56" width="130" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="241.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">受け手と比べる</text><rect x="336" y="56" width="130" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="401.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">k×k 回くり返す</text><rect x="496" y="56" width="130" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="561.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">0/1 を平均</text><line x1="146" y1="78" x2="174" y2="78" stroke="currentColor" stroke-width="2" marker-end="url(#m1)"/><line x1="306" y1="78" x2="334" y2="78" stroke="currentColor" stroke-width="2" marker-end="url(#m1)"/><line x1="466" y1="78" x2="494" y2="78" stroke="currentColor" stroke-width="2" marker-end="url(#m1)"/><text x="360" y="140" text-anchor="middle" style="font-size:13px;font-weight:700">先にシャドウ マップをぼかしてから 1 回読む（VSM 系）</text><rect x="16" y="152" width="130" height="44" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="81.0" y="174.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">値を変換して書く</text><rect x="176" y="152" width="130" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="241.0" y="174.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ぼかし（2 パス）</text><rect x="336" y="152" width="130" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="401.0" y="174.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">画素で 1 回読む</text><rect x="496" y="152" width="130" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="561.0" y="174.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">式で影の割合</text><line x1="146" y1="174" x2="174" y2="174" stroke="currentColor" stroke-width="2" marker-end="url(#m1)"/><line x1="306" y1="174" x2="334" y2="174" stroke="currentColor" stroke-width="2" marker-end="url(#m1)"/><line x1="466" y1="174" x2="494" y2="174" stroke="currentColor" stroke-width="2" marker-end="url(#m1)"/><text x="360" y="232" text-anchor="middle" style="font-size:12px;font-weight:400">比較を後ろに回せるように、比べても結果が変わらない値に変換しておく</text></svg>

## 読み込み回数の見積もり {#cost-model}

「VSM 系は 1 回読むだけ」という説明だけでは、いつ得なのかが分かりません。画面の画素数を P、シャドウ マップのテクセル数を T、ぼかしの幅を k とします。ぼかしは縦横の 2 パスに分けるので、1 テクセルあたり 2k 回読みます。読み込みの回数を数えると次のようになります。

- PCF は P × k² 回です。
- VSM 系は P × 1 回とぼかしの T × 2k 回の合計です。

画素あたりに直すと PCF が k²、VSM 系が 1 + 2k·(T / P) です。1920×1080 の画面（P ≈ 207 万）に 2048×2048 のシャドウ マップ（T ≈ 419 万、T / P ≈ 2.02）なら k = 3 で PCF が 9、VSM 系が約 13.1 です。k = 5 で 25 と約 21.2、k = 9 で 81 と約 37.4、k = 15 で 225 と約 61.7 になります。釣り合うのは k² = 1 + 2k·(T / P) を解いて、k ≈ 4.3 のあたりです。

<svg class="fig flow" viewBox="0 0 680 306" role="img" aria-label="1 画素あたりの読み込み回数"><defs><marker id="m2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">フィルタの幅と読み込み回数</text><rect x="90" y="241.9" width="42" height="8.1" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><rect x="136" y="238.21" width="42" height="11.79" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="111" y="235.9" text-anchor="middle" style="font-size:12px;font-weight:400">9</text><text x="157" y="232.21" text-anchor="middle" style="font-size:12px;font-weight:400">13.1</text><text x="134" y="268" text-anchor="middle" style="font-size:13px;font-weight:700">3×3</text><rect x="225" y="227.5" width="42" height="22.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><rect x="271" y="230.92000000000002" width="42" height="19.08" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="246" y="221.5" text-anchor="middle" style="font-size:12px;font-weight:400">25</text><text x="292" y="224.92000000000002" text-anchor="middle" style="font-size:12px;font-weight:400">21.2</text><text x="269" y="268" text-anchor="middle" style="font-size:13px;font-weight:700">5×5</text><rect x="360" y="177.1" width="42" height="72.9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><rect x="406" y="216.34" width="42" height="33.66" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="381" y="171.1" text-anchor="middle" style="font-size:12px;font-weight:400">81</text><text x="427" y="210.34" text-anchor="middle" style="font-size:12px;font-weight:400">37.4</text><text x="404" y="268" text-anchor="middle" style="font-size:13px;font-weight:700">9×9</text><rect x="495" y="47.5" width="42" height="202.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><rect x="541" y="194.47" width="42" height="55.53" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="516" y="41.5" text-anchor="middle" style="font-size:12px;font-weight:400">225</text><text x="562" y="188.47" text-anchor="middle" style="font-size:12px;font-weight:400">61.7</text><text x="539" y="268" text-anchor="middle" style="font-size:13px;font-weight:700">15×15</text><line x1="70" y1="250" x2="650" y2="250" stroke="currentColor" stroke-width="1.5"/><rect x="90" y="38" width="14" height="14" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="110" y="50" text-anchor="start" style="font-size:12px;font-weight:400">PCF（k² 回）</text><rect x="90" y="58" width="14" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="110" y="70" text-anchor="start" style="font-size:12px;font-weight:400">ぼかし済みを 1 回 + ぼかしの分</text><text x="360" y="290" text-anchor="middle" style="font-size:12px;font-weight:400">1920×1080 の画面、2048×2048 のシャドウ マップ。読み込み回数だけの見積もり</text></svg>

この見積もりは、回数だけを数えた粗いものです。3 つの点で実際とずれます。

- 比較サンプラーの 2×2 の割引が PCF にかかるので、PCF は表より最大で 4 分の 1 近くまで軽くなります。
- VSM は 1 テクセルが 8 バイト（`R32G32_FLOAT`）で、深度の 4 バイトより重いので、読み込み 1 回の重さが違います。
- ぼかしのパスはシャドウ マップを毎フレーム描き直すライトでは毎回かかります。ライトが動かずマップを再利用できる場面では、ぼかしの分が 0 に近づきます。

逆に、VSM 系にはミップマップと異方性フィルタが使えます。遠くの影の縮小フィルタを PCF のように多数のサンプルで補う必要がありません。

## 論文のフレーム時間 {#paper-timings}

MSM の論文には同じシーンで方式を替えたときのフレーム時間が載っています。次の値は図 1 と図 6 のキャプションの数字から、「影なしで描いたときの時間」を引いたものです。引き算は私がしました。

図 1 では影なしが 0.64 ms で、PCF が 1.73 ms、VSM と ESM が 1.15 ms、MSM が 1.46 ms です。引くと影のコストは PCF が約 1.09 ms、VSM と ESM が約 0.51 ms、MSM が約 0.82 ms になります。図 6 では影なしが 0.44 ms で、PCF（16 ビット）が 1.13 ms、VSM（16 ビット）が 0.89 ms、ESM（c = 80、32 ビット）が 0.9 ms です。Hamburger 4MSM（16 ビット）が 1.13 ms、Hausdorff 4MSM（32 ビット）が 1.46 ms、三角関数版の TMSM（16 ビット）が 1.87 ms でした。引くと PCF と Hamburger 4MSM が約 0.69 ms、VSM と ESM が約 0.45〜0.46 ms になります。

図 1 と図 6 は別のシーンで、設定も違います。両者の数字を並べて方式の優劣を決めることはできません。論文が図 7 の測定について書いているのは、次の点です。測定は GeForce GTX 780 と Direct3D 11 で、平行光源が 1 つシャドウ マップがシーン全体を一様に覆う条件でした。フィルタ可能なシャドウ マップのフレーム時間は、テクセルあたりのメモリでほぼ決まります。32 ビット量子化の VSM と 16 ビット量子化の 4MSM は、4MSM のアルゴリズムのほうが複雑なのに、ほとんど同じ時間でした。16 ビットの VSM は ESM と同じ時間です。Hamburger 4MSM は出力解像度が大きいときフィルタ カーネルが大きいとき、シャドウ マップが小さいときに PCF より速くなりました。

この結果から読み取れるのは「判定の計算が複雑でもメモリの量が同じなら時間は変わらない」ということです。判定のコスト（連立方程式を解くなど）は、読み込みのコストに隠れます。図 1 と図 6 の測定の環境（GPU や解像度）は、読んだ範囲では確かめられていません。

## それぞれの外れ方 {#failures}

### PCF {#fail-pcf}

PCF の問題は光漏れではなく、バイアスとコストです。フィルタの範囲が広がるほど傾いた面の自己影を防ぐバイアスも大きくしなければならず、そのぶん接触部で影が浮きます。

### VSM {#fail-vsm}

VSM の光漏れは、カーネルのなかに分散の大きな深度の分布があるときに出ます。論文の関連研究の節はカーネルのなかの分散が大きいと完全に影のはずの領域で VSM が光漏れを出すと書いています。

次の例で数えてみます。カーネルの半分が深度 0.2 の層 A、残り半分が深度 0.5 の層 B で、受け手が深度 0.8 にあるとします。受け手は両方の層の後ろなので、PCF の答えは 0（完全な影）です。VSM は平均が 0.35、分散が 0.0225 になります。Chebyshev の式は分散 ÷（分散 + (受け手 − 平均)²）です。受け手 − 平均は 0.45 で、2 乗は 0.2025 です。0.0225 ÷ 0.225 で 0.10 になり 10% の光が漏れます。

<svg class="fig flow" viewBox="0 0 680 256" role="img" aria-label="2 層の奥の受け手で VSM が光漏れする例"><defs><marker id="m3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">VSM の光漏れ（深度の軸）</text><line x1="60" y1="120" x2="620" y2="120" stroke="currentColor" stroke-width="2"/><line x1="60" y1="116" x2="60" y2="124" stroke="currentColor"/><text x="60" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><line x1="172.0" y1="116" x2="172.0" y2="124" stroke="currentColor"/><text x="172.0" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">0.2</text><line x1="284.0" y1="116" x2="284.0" y2="124" stroke="currentColor"/><text x="284.0" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">0.4</text><line x1="396.0" y1="116" x2="396.0" y2="124" stroke="currentColor"/><text x="396.0" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">0.6</text><line x1="508.0" y1="116" x2="508.0" y2="124" stroke="currentColor"/><text x="508.0" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">0.8</text><line x1="620.0" y1="116" x2="620.0" y2="124" stroke="currentColor"/><text x="620.0" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">1.0</text><text x="60" y="160" text-anchor="start" style="font-size:11px;font-weight:400">近い</text><text x="620" y="160" text-anchor="end" style="font-size:11px;font-weight:400">遠い</text><rect x="146.0" y="64" width="52" height="38" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="172.0" y="83" text-anchor="middle" style="font-size:12px;font-weight:400">層 A 50%</text><rect x="314.0" y="64" width="52" height="38" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="340.0" y="83" text-anchor="middle" style="font-size:12px;font-weight:400">層 B 50%</text><line x1="256.0" y1="50" x2="256.0" y2="120" stroke="#4c8bf5" stroke-width="2" stroke-dasharray="5 4"/><text x="256.0" y="44" text-anchor="middle" style="font-size:12px;font-weight:700">平均 0.35</text><rect x="480.0" y="76" width="56" height="26" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="508.0" y="93" text-anchor="middle" style="font-size:12px;font-weight:400">受け手 0.8</text><text x="360" y="190" text-anchor="middle" style="font-size:13px;font-weight:400">分散 = 0.0225、(0.8 − 0.35)² = 0.2025</text><text x="360" y="214" text-anchor="middle" style="font-size:13px;font-weight:700">VSM: 0.0225 ÷ (0.0225 + 0.2025) = 0.10 → 10% が光漏れ</text><text x="360" y="238" text-anchor="middle" style="font-size:13px;font-weight:400">PCF: 2 層とも手前なので 0（完全な影）</text></svg>

層が 2 つあるだけでこうなります。人の体や柱の重なる場面のように遮蔽物が重なるシーンで目立つのは、この仕組みのためです。対策は [Light Bleeding](light-bleeding.md) に書きました。

### ESM {#fail-esm}

論文は ESM が部分的な影の一番奥の受け手と完全な影の領域では高い品質を出す一方、受け手の境界では不安定になると書いています。指数を使うので遮蔽物と受け手の深度の差が小さいと `exp(−c·差)` が 1 に近いまま残って、影が薄くなります。もう 1 つの注意は桁あふれです。32 ビット浮動小数点で `exp(c·z)` が表せるのは c·z が約 88 までなので、z が 1 に近い所では c を 80 付近までにとどめます。

### EVSM {#fail-evsm}

EVSM は VSM と ESM の長所をあわせる方式として、論文で紹介されています。VSM を 4 通りの変換で適用して暗いほうを使うため、VSM の光漏れも ESM の不安定さもどちらも弱くなります。そのかわりチャンネルが 4 つになり指数が大きくなるぶん精度にも気を使います。

### MSM {#fail-msm}

MSM の外れ方は論文が結果の節で書いています。非常に短い距離で落ちる影はわずかな量子化ノイズと光漏れを出すことがあります。16 ビット量子化で必要なバイアス α を強くすると、光漏れがわずかに強まります。三角関数版の TMSM は Hausdorff 4MSM と同じ程度の光漏れで、頑健さに問題があり時間も遅いと書かれています。

## 数値で試す {#experiment}

外れ方を数字で見るためにカーネルのなかの深度の分布を決めて、5 方式の判定を計算してみました。表の値は「光が当たる割合」で、0 が完全な影、1 が完全な明るさです。PCF は正解として扱います。Python で後のコードと同じ式（ガードの分岐を除く）を書いて計算したもので、論文や資料の数字ではありません。EVSM の c は 40、ESM の c は 80、最小分散は VSM が 0.0001、EVSM がワープ後の値に比例する形（0.0001 × (c·t)²）、MSM のバイアスは 3×10⁻⁵ です。これらは私が選んだ一例で変えれば値は変わります。

| 場面（深度は 0〜1） | PCF | VSM | ESM | EVSM | MSM |
| --- | --- | --- | --- | --- | --- |
| A：層 0.2 と 0.5、受け手 0.8 | 0 | 0.100 | 0 | 0.138 | 0 |
| D：層 0.2・0.5・0.7、受け手 0.9 | 0 | 0.183 | 0 | 0.138 | 0.024 |
| G：遮蔽物 0.5 のすぐ後ろ 0.51 | 0 | 0.500 | 0.449 | 0.398 | 0.070 |
| F：傾いた面 0.4〜0.6、受け手 0.5 | 0.5 | 1.000 | 1.000 | 0.805 | 0.744 |
| B：縁（0.3 と 1.0）、受け手 1.0 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| C：同じ縁、受け手 0.3 | 1 | 1 | 1 | 1 | 1 |
| E：遮蔽物 1 つ 0.4、受け手 0.9 | 0 | 0 | 0 | 0 | 0 |

A と D は重なった層の奥の受け手です。VSM が漏れる量はそれぞれ 0.100 と 0.183 で、遮蔽物の層が増えるほど増えました。ESM は 0 を返し MSM は D で 0.024 とわずかに漏れます。EVSM は A と D で 0.138 を返しました。ここでは最小分散の下限が効いているためで、下限の係数を小さくすれば値は下がります。

G は遮蔽物のすぐ後ろの受け手です。正解は 0 ですが 4 方式がすべて漏れます。VSM の 0.5 は分散が 0 なので最小分散の下限だけで決まった値です（(0.51 − 0.5)² = 0.0001 がちょうど下限と同じなので 0.5 になります）。ESM の 0.449 は `exp(−c·0.01) = exp(−0.8) ≈ 0.449` と一致します。この近い距離で影が薄くなる性質が、ESM の「接触部の薄れ」です。MSM は 0.070 と最も小さく漏れました。

F はカーネルのなかの深度が連続して広がる場合です。受け手は範囲の真ん中にあり正解は 0.5 です。VSM と ESM は 1.0 を返します。VSM は受け手が平均以下のとき Chebyshev の条件によって無条件に 1 を返す設計なので、ちょうど平均にある受け手は完全に明るくなります。MSM の 0.744 と EVSM の 0.805 も正解の 0.5 より明るい側に外れています。どの方式も下限の値を明るい側に返す性質を示しています。

B・C・E は、どの方式も PCF と一致しました。遮蔽物が 1 つだけの単純な縁では、方式による差が出ません。差が出るのは層が重なる場面と受け手が遮蔽物に近い場面です。

## 判定関数を同じ形で並べる {#code}

ここからは、同じ入力（ぼかし済みの値と受け手の深度）で「光が当たる割合」を返す関数を並べます。HLSL（SM5）で書きました。このコードはコンパイルしていません。ガードの分岐を除いた式の動きは前節の表を計算した Python の版で確かめています。

### 共通の入力 {#code-common}

```hlsl
// 受け手の深度 zf は、ライトから見た 0〜1（近いほど小さい）。
// 戻り値は「光が当たる割合」。1 が明るい、0 が完全な影。
// 4 方式で戻り値の向きをそろえてあるので、同じ呼び出しに差し替えて比べられる。

static const float kMinVariance = 1e-4;   // VSM の分散の下限（一例）。0 だと割り算が壊れる

// Chebyshev の不等式。m は (E[w]、E[w²])、t は受け手側の値。
// VSM と EVSM が共有する。
float Chebyshev(float2 m, float t, float min_variance) {
  if (t <= m.x) return 1.0;                 // 平均以下なら遮られていない（式の前提 t > 平均 を満たさない）
  float variance = max(m.y - m.x * m.x, min_variance);  // 丸め誤差で負になるのを防ぐ
  float d = t - m.x;
  return variance / (variance + d * d);     // 片側 Chebyshev：光が当たる割合の上限
}
```

`Chebyshev` は VSM と EVSM の両方から呼びます。`t <= m.x` で 1 を返すのは不等式が `t` が平均より大きいときにだけ成り立つからです。この分岐を忘れて式をそのまま計算すると、受け手が遮蔽物の手前にあるのに値が 1 を下回って、影が出ます。

分散を `max` で下から押さえるのは、GPU Gems 3 の第 8 章が書いている方法です。`E[w²] − E[w]²` は浮動小数点の丸めで 0 付近でわずかに負になり割り算が壊れます。下限の値はシーンの深度の範囲に合わせて決めます。ここの 1e-4 は一例です。

### PCF（正解の側） {#code-pcf}

```hlsl
Texture2D<float> gDepth;               // 通常のシャドウ マップ（深度 1 チャンネル）
SamplerComparisonState gCompare;       // 比較関数 LESS_EQUAL、フィルタは比較つき双線形

// k は奇数（3、5、…）。texel は 1 テクセルの UV の大きさ。
// 戻り値は 0〜1。ぼかしの幅を広げると、呼び出しが k * k 回に増える。
float LitPcf(float2 uv, float zf, float bias, float2 texel, int k) {
  float sum = 0.0;
  int half_k = k / 2;
  for (int y = -half_k; y <= half_k; ++y) {
    for (int x = -half_k; x <= half_k; ++x) {
      // SampleCmpLevelZero は「zf <= 保存された深度」なら 1。2×2 の双線形がハードウェアでかかる。
      sum += gDepth.SampleCmpLevelZero(gCompare, uv + float2(x, y) * texel, zf - bias);
    }
  }
  return sum / (k * k);                  // 比べた結果の平均
}
```

`zf - bias` と引くのは面の傾きで自己影が出るのを防ぐためです。k が大きいほどフィルタ範囲の深度の差が大きくなり必要なバイアスも増えます。ここが前に書いた PCF の弱点です。

### VSM {#code-vsm}

```hlsl
Texture2D<float2> gVsm;                // ぼかし済み。(E[z]、E[z²])
SamplerState gLinear;                  // 双線形（ミップ、異方性も使える）

float LitVsm(float2 uv, float zf) {
  float2 m = gVsm.SampleLevel(gLinear, uv, 0);   // 1 回の読み込みで、ぼかし済みの値が得られる
  return Chebyshev(m, zf, kMinVariance);
}

// シャドウ パスの出力。深度 z とその 2 乗を書く。
// 論文（GPU Gems 3）は、傾いた面で分散が足りなくなる問題を、ddx/ddy の項で補っている。
float2 WriteVsm(float z) {
  float dx = ddx(z), dy = ddy(z);
  return float2(z, z * z + 0.25 * (dx * dx + dy * dy));  // 2 次モーメントに偏微分の項を足す
}
```

`WriteVsm` の `0.25 * (dx² + dy²)` は GPU Gems 3 の第 8 章の `ComputeMoments`（リスト 8-2）にある ddx/ddy の項を、私が式の形に書き直したものです。章の要約で確かめた範囲では係数の 0.25 までは確認できていません。使う前に原文のリストで係数を照らしてください。

### ESM {#code-esm}

```hlsl
Texture2D<float> gEsm;                 // ぼかし済み。E[exp(c * z)]
static const float kEsmC = 80.0;       // 論文の図 6 で使われた値。z が 0〜1 なら exp(80) は 32 ビットで表せる

float LitEsm(float2 uv, float zf) {
  float e = gEsm.SampleLevel(gLinear, uv, 0);
  // E[exp(c z_遮蔽)] * exp(-c * zf) = E[exp(-c * (zf - z_遮蔽))]。差が正に大きいほど 0 に近づく
  return saturate(e * exp(-kEsmC * zf));
}

float WriteEsm(float z) { return exp(kEsmC * z); }
```

`saturate` で 1 に切るのは、カーネルのなかに受け手より奥の深度が混ざると、平均が `exp(c·zf)` を超えて、結果が 1 を超えるためです。

### EVSM {#code-evsm}

```hlsl
Texture2D<float4> gEvsm;               // ぼかし済み。(E[wp]、E[wp²]、E[wn]、E[wn²])
static const float2 kEvsmC = float2(40.0, 40.0);   // 正側・負側の指数（一例）。exp(2c) が桁あふれしない値

float LitEvsm(float2 uv, float zf) {
  float4 m = gEvsm.SampleLevel(gLinear, uv, 0);
  // 受け手側も同じ変換をかける。wp = exp(c z)、wn = -exp(-c z)（どちらも z について増加）
  float2 t = float2(exp(kEvsmC.x * zf), -exp(-kEvsmC.y * zf));
  // 最小分散は、変換後の値の傾き（c * t）の 2 乗に比例させる。足した（資料にない一例）
  float2 floor_var = kMinVariance * (kEvsmC * t) * (kEvsmC * t);
  float lit_p = Chebyshev(m.xy, t.x, floor_var.x);
  float lit_n = Chebyshev(m.zw, t.y, floor_var.y);
  return min(lit_p, lit_n);              // 暗いほうを使う（論文の説明）
}

float4 WriteEvsm(float z) {
  float wp = exp(kEvsmC.x * z), wn = -exp(-kEvsmC.y * z);
  return float4(wp, wp * wp, wn, wn * wn);
}
```

負側の変換を `−exp(−c·z)` にするのは、変換後の値が `z` について増加するようにして、`Chebyshev` が正側と同じ向きで使えるようにするためです。符号を付けずに `exp(−c·z)` を使うと遠いほど小さくなって、不等式の向きが逆になります。

最小分散を変換後の値の大きさに合わせるのは、私が足した処理です。変換後の値は `exp(c·z)` なので桁が深度によって大きく変わります。固定の `1e-4` では遠い所では小さすぎて割り算が壊れ近い所では大きすぎて影が薄まります。

### MSM（Hamburger 4MSM） {#code-msm}

```hlsl
Texture2D<float4> gMsm;                // ぼかし済み。(E[z]、E[z²]、E[z³]、E[z⁴])
static const float kMsmAlpha = 3e-5;   // 論文のアルゴリズム 3 の例。16 ビット量子化では強くする

// 論文のアルゴリズム 3。戻り値は「光が当たる割合」。
float LitMsm(float2 uv, float zf) {
  float4 b = gMsm.SampleLevel(gLinear, uv, 0);
  b = (1.0 - kMsmAlpha) * b + kMsmAlpha * 0.5;   // 手順 1。バイアスで行列を正則に保つ

  // 手順 2。3×3 の連立方程式 B c = (1, zf, zf²) を LDLT 分解で解く。
  // B = [1 b1 b2; b1 b2 b3; b2 b3 b4]。D と L は下三角分解の対角と下三角。
  float d2 = b.y - b.x * b.x;                        // 第 2 対角
  float l32 = (b.z - b.x * b.y) / d2;
  float d3 = b.w - b.y * b.y - l32 * l32 * d2;       // 第 3 対角
  float y2 = zf - b.x;
  float y3 = zf * zf - b.y - l32 * y2;
  float c3 = y3 / d3;
  float c2 = y2 / d2 - l32 * c3;
  float c1 = 1.0 - b.x * c2 - b.y * c3;

  // 手順 3。c3 z² + c2 z + c1 = 0 を解いて、遮蔽物の深度 z2 <= z3 を得る。
  // c3 が 0 に近いと解が発散する。足した：論文が触れる「c3 が 0 に近づく」問題への保険
  c3 = abs(c3) < 1e-9 ? 1e-9 : c3;
  float disc = max(c2 * c2 - 4.0 * c3 * c1, 0.0);    // 足した：丸めで負になるのを防ぐ
  float r = sqrt(disc);
  float za = (-c2 - r) / (2.0 * c3), zb = (-c2 + r) / (2.0 * c3);
  float z2 = min(za, zb), z3 = max(za, zb);

  // 手順 4〜6。zf が z2、z3 のどこにあるかで場合分け。G は「影の割合」の下限。
  float g;
  if (zf <= z2) {
    g = 0.0;                                          // 受け手が最も手前の遮蔽物より前
  } else if (zf <= z3) {
    g = (zf * z3 - b.x * (zf + z3) + b.y) / ((z3 - z2) * max(zf - z2, 1e-9));
  } else {
    g = 1.0 - (z2 * z3 - b.x * (z2 + z3) + b.y) / (max(zf - z2, 1e-9) * (zf - z3));
  }
  return 1.0 - saturate(g);                           // 論文は G を [0,1] に切ると外れ値を抑えられると書く
}

float4 WriteMsm(float z) {
  float z2 = z * z;
  return float4(z, z2, z2 * z, z2 * z2);
}
```

手順の番号は MSM の論文のアルゴリズム 3 に対応しています。論文はこのアルゴリズムの数値的な安定のためにバイアスの付け方と LDLT 分解を採用した理由を書いています。単精度で安定させるにはバイアス α を 2×10⁻⁶ にするとありますが、アルゴリズム 3 の入力欄には 3×10⁻⁵ という例も書かれています。この数字の違いの理由は論文では確かめられていません。

最後の `[0,1]` への切り詰めは論文が書く「ごくまれに個々の画素で影の強さが [0,1] の外に出るアーティファクト」への対策です。論文は G を切ることで目立たなくなり Hausdorff 4MSM を使えば完全に消えると書いています。`za` と `zb` の小さいほうを z2 にしているのは、アルゴリズムが z2 ≤ z3 を前提にしているからです。

### 差し替える {#code-switch}

```hlsl
// 呼び出し側。マクロで方式を切り替えて、同じシーンで見比べる。
float Lit(float2 uv, float zf) {
#if SHADOW_METHOD == 0
  return LitPcf(uv, zf, 0.002, gTexel, 5);
#elif SHADOW_METHOD == 1
  return LitVsm(uv, zf);
#elif SHADOW_METHOD == 2
  return LitEsm(uv, zf);
#elif SHADOW_METHOD == 3
  return LitEvsm(uv, zf);
#else
  return LitMsm(uv, zf);
#endif
}
```

`gTexel` は 1 テクセルの UV 幅です。バイアスの `0.002` は PCF の一例で、シーンの深度の範囲に合わせて調整します。ほかの方式はバイアスをほとんど必要としません。

## 使い分け {#choose}

<svg class="fig flow" viewBox="0 0 700 356" role="img" aria-label="どの方式を選ぶかの流れ"><defs><marker id="m4" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">選び方の流れ</text><rect x="240" y="40" width="200" height="40" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="340.0" y="60.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ぼかしは大きいか</text><rect x="30" y="130" width="180" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="120.0" y="150.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">PCF（3×3〜5×5）</text><line x1="240" y1="70" x2="120" y2="128" stroke="currentColor" stroke-width="2" marker-end="url(#m4)"/><text x="150" y="100" text-anchor="middle" style="font-size:12px;font-weight:400">いいえ</text><rect x="470" y="130" width="180" height="40" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="560.0" y="150.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">メモリは厳しいか</text><line x1="440" y1="70" x2="560" y2="128" stroke="currentColor" stroke-width="2" marker-end="url(#m4)"/><text x="540" y="100" text-anchor="middle" style="font-size:12px;font-weight:400">はい</text><rect x="340" y="220" width="150" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="415.0" y="240.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ESM / VSM</text><line x1="540" y1="170" x2="440" y2="218" stroke="currentColor" stroke-width="2" marker-end="url(#m4)"/><text x="520" y="200" text-anchor="middle" style="font-size:12px;font-weight:400">はい</text><rect x="520" y="220" width="150" height="40" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="595.0" y="240.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">光漏れは許せるか</text><line x1="580" y1="170" x2="595" y2="218" stroke="currentColor" stroke-width="2" marker-end="url(#m4)"/><text x="612" y="200" text-anchor="middle" style="font-size:12px;font-weight:400">いいえ</text><rect x="420" y="300" width="120" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="480.0" y="320.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">VSM</text><line x1="560" y1="260" x2="500" y2="298" stroke="currentColor" stroke-width="2" marker-end="url(#m4)"/><text x="510" y="284" text-anchor="middle" style="font-size:12px;font-weight:400">はい</text><rect x="560" y="300" width="120" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="620.0" y="320.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">EVSM / MSM</text><line x1="610" y1="260" x2="620" y2="298" stroke="currentColor" stroke-width="2" marker-end="url(#m4)"/><text x="630" y="284" text-anchor="middle" style="font-size:12px;font-weight:400">いいえ</text></svg>

論文が結論で述べているのは MSM が「メモリ 64 ビット / テクセルで可能な最良のシャドウ マッピング」だという点です。PCF を超えるかどうかは条件次第で、大きな出力解像度・大きなカーネル・小さなシャドウ マップで有利になるという書き方です。

このページの残りの節は論文の主張ではなく、私の見方です。実際のゲームで何が主流かを示す統計は、読んだ範囲にありません。

- 太陽光と数個のライトで足りるなら、PCF の 3×3 から 5×5 で始めます。光漏れがなく、手順が素直だからです。
- ぼかしを広げたい場面（やわらかい影、遠景のカスケード）では VSM 系の読み込みの安さが効いてきます。ただし光漏れの対策が要ります。
- 光漏れが許せない構造（重なる物が多い柱や髪など）なら EVSM か MSM、それでも不安なら PCF に戻ります。
- メモリが厳しいなら、ESM か VSM の 16 ビットで 1 値 32 ビット程度に収めます。
- 近年は PCF にブルー ノイズを混ぜて少ないサンプルで時間方向に平均する（TAA）方向や、ハードウェア レイトレーシング（[Ray-Traced Shadows](../ray-traced.md)）が使われます。光漏れの対策が複雑なぶん VSM 系の使いどころは狭まったと私は見ています。

## よくあるミス {#mistakes}

??? failure "光漏れの調整に時間がかかる"
    VSM を選んだあとに重なった遮蔽物で光漏れが出てから EVSM や MSM に替えると、保存形式とぼかしのパスが全部変わります。原因は遮蔽物が重なる場面を最初に試さなかったことです。最初に層が 2 つ以上重なるテスト シーンで確かめます。

??? failure "遮蔽物のすぐ後ろの影が薄い"
    ESM や EVSM で、接触部の影が薄れます。前節の G の例で ESM は 0.449 を返しました。原因は深度の差が小さいと指数が 1 に近いままだからです。c を大きくすれば濃くなりますが、桁あふれに近づくので 32 ビット浮動小数点で `exp` が表せる範囲（c·z が約 88 まで）に収まるかを確かめます。

??? failure "フィルタの結果が 16 ビットで荒れる"
    VSM や ESM を 16 ビットの浮動小数点で保存すると、2 乗やべき乗の値の精度が足りません。分散が 0 付近で潰れます。VSM は 32 ビットの浮動小数点にするか MSM の論文が示す専用の量子化（4 つのモーメントを 16 ビット × 4 に収める）を使います。

??? failure "平均と受け手がちょうど等しい所だけ明るい"
    `Chebyshev` の `t <= m.x` で 1 を返す分岐のためです。前節の F のようにカーネルの真ん中に受け手があると、VSM は 1.0 を返しました。光漏れの一種で分散が大きい傾いた面で目立ちます。分散の下限や光漏れの削減（[Light Bleeding](light-bleeding.md)）で抑えます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] PCF は比較してから平均する。VSM 系は平均してから式で割合を出す
    - [x] 読み込みは PCF が k²、VSM 系は 1 回とぼかしの分。釣り合いはこのページの例で k ≈ 4.3
    - [x] VSM 系の外れ方は、下限が明るい側に外れること。VSM は光漏れ ESM は接触部の薄れ
    - [x] 速さは判定の複雑さよりメモリ量で決まる（MSM の論文の測定）

## 参考 {#references}

読んだ範囲を版ごとに書きます。

- Christoph Peters, Reinhard Klein, "Moment Shadow Mapping", Proceedings of the ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games (I3D 2015), 2015. DOI: 10.1145/2699276.2699277。著者版の 8 ページを全文読みました（補足資料と動画は読んでいません）。関連研究・評価・アルゴリズム 3・結果と結論の節を使いました。
- Andrew Lauritzen, "Summed-Area Variance Shadow Maps", GPU Gems 3, 第 8 章, Addison-Wesley, 2007。https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-8-summed-area-variance-shadow-maps 。章の本文は取得した要約で確かめました。リストの細かい係数は原文で照らしていません。
- William Donnelly, Andrew Lauritzen, "Variance Shadow Maps", I3D 2006。読んでいません。MSM の論文と GPU Gems 3 の記述の範囲で触れました。
- William T. Reeves, David H. Salesin, Robert L. Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987。読んでいません。
- Thomas Annen, Tom Mertens, Hans-Peter Seidel, Eugene Fiume, Frédo Durand, "Exponential Shadow Maps", Graphics Interface 2008。読んでいません。ESM の記述は MSM の論文の関連研究の節によります。
- Andrew Lauritzen, Michael McCool, "Layered Variance Shadow Maps", Graphics Interface 2008。読んでいません。

## 関連ページ {#related}

- [VSM, ESM and MSM](index.md)
- [Light Bleeding](light-bleeding.md)
- [PCF](../pcf.md)
- [PCSS](../pcss.md)
