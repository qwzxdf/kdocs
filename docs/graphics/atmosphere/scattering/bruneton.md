---
title: Bruneton Precomputed Scattering
tags:
  - 描画
---

# Bruneton Precomputed Scattering

大気の散乱は視線に沿った積分です。昼の空だけなら画素ごとに 10 回ほどサンプルする方法で済みます。ところが夕焼けや地球の影が大気に落ちる様子、宇宙から見た地球の縁まで含めると、積分は多重散乱になり画素ごとには解けません。Bruneton と Neyret（2008）は、「積分の結果を前もって全部テーブルに入れておく」ことで、これを解きました。実行時に必要なのはテーブルを数回読むことだけです。このページでは論文を全文読み事前計算の式、テーブルの座標の割り当て実行時の参照をコメント付きの HLSL で示します。

!!! tip "ポイント"
    - 散乱を高度 r・視線の天頂角 µ・太陽の天頂角 µs・視線と太陽のなす角 ν の 4 変数の関数 S として、テーブルに前もって入れる。
    - 空気遠近法は `S(x, v, s) − T(x, xs) · S(xs, v, s)` の 1 つの式で出る。散乱を上端まで積分したテーブルを 2 点で引くだけでよい。
    - 地表の観測者が遠くの山を見るときµ の差は 0.016 しかない。µ を「地平線までの距離の比」に写し替えると、差が約 6 倍になり 128 分割でも足りる。
    - 論文のテーブルは 32 × 128 × 32 × 8 で、RGBA16F なら 8 MiB。5 次までの散乱を GPU で約 5 秒で計算した。
    - 大気の組成（エアロゾル）は高度だけの関数で、場所では変わらない。動的な天候には向かない。

!!! info "このページを読む前に"
    - [Atmospheric Scattering](index.md)（このセクション全体の地図と、読む順番）
    - [Transmittance](transmittance.md)・[Single Scattering](single-scattering.md)（透過率と単散乱の式）

## 読んだ資料 {#sources}

- Eric Bruneton, Fabrice Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum 27(4)（Eurographics Symposium on Rendering 2008）, pp. 1079–1086。HAL の著者版を本文・参考文献・図の説明まで全部読みました。図そのもの（グラフと写真）は見ていません。
- Eric Bruneton, "Precomputed Atmospheric Scattering: a New Implementation", 2017（参照実装の文書）。紹介のページと `functions.glsl` の文書のうち透過率、単散乱、多重散乱の計算の説明（全体の約 6 割）を読みました。多重散乱のテクスチャ、地面の照度、描画の関数は読んでいません。
- Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models"（2017）と、Hillaire（2020）は読んでいません。

## 全体の考え方 {#overview}

<svg class="fig flow" viewBox="0 0 720 340" role="img" aria-label="大気の断面と 4 つの変数"><defs><marker id="br-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">大気の断面: 地表 Rg と上端 Rt、観測者 x、視線 v、太陽 s</text><circle cx="200" cy="330" r="260" fill="none" stroke="#94a3b8" stroke-dasharray="4 4"/><circle cx="200" cy="330" r="240" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="200" y="230" text-anchor="middle" font-size="12" fill="currentColor">地表</text><text x="390" y="52" text-anchor="start" font-size="10" fill="currentColor">上端 Rt</text><circle cx="200" cy="90" r="5" fill="#e5aa28"/><text x="190" y="82" text-anchor="end" font-size="12" fill="currentColor">x</text><line x1="200" y1="90" x2="200" y2="20" stroke="#94a3b8" stroke-dasharray="3 3"/><text x="204" y="28" text-anchor="start" font-size="10" fill="currentColor">天頂</text><line x1="200" y1="90" x2="390" y2="55" stroke="#e5aa28" stroke-width="2" marker-end="url(#br-a)"/><text x="396" y="54" text-anchor="start" font-size="11" fill="currentColor">v(視線)</text><line x1="200" y1="90" x2="350" y2="-30" stroke="#4c8bf5" stroke-width="2" marker-end="url(#br-a)"/><text x="356" y="-34" text-anchor="start" font-size="11" fill="currentColor">s(太陽)</text><text x="252" y="78" text-anchor="start" font-size="12" fill="currentColor">µ</text><text x="260" y="38" text-anchor="start" font-size="12" fill="currentColor">µs</text><text x="310" y="20" text-anchor="start" font-size="12" fill="currentColor">ν</text><text x="400" y="130" text-anchor="start" font-size="11" fill="currentColor">4 つの変数: r = |x|, µ = v・x/r, µs = s・x/r, ν = v・s</text><text x="400" y="150" text-anchor="start" font-size="11" fill="currentColor">球対称なので、位置は高度 r だけで決まる</text></svg>

論文の核はレンダリング方程式を「事前計算できる形」に直すことです。地表を完全な球で一定の反射率とみなすと散乱光は 4 つの変数だけの関数になります。観測者の位置は高度 r（惑星が球なので、位置は高度だけで足りる）、視線の向きは天頂角の cos、太陽の向きも天頂角の cos、そして視線と太陽の間の角の cos です。

実行時には空の色と空気遠近法をこの 4 次元のテーブルを引いて作ります。サンプルによる数値積分がないので、論文は「定数時間」で評価できると言います。

## 物理モデル {#model}

論文が使うのは空気分子（レイリー）とエアロゾル（Mie）の 2 成分の晴天モデルです。大気は地表の半径 Rg ＝ 6360 km から、上端の半径 Rt ＝ 6420 km までの薄い球殻です。

レイリー散乱の係数は波長の 4 乗に反比例します。論文は(680, 550, 440) nm に対して `βsR = (5.8, 13.5, 33.1) × 10⁻⁶ m⁻¹` を使います。青の係数が赤の約 5.7 倍あるので、空は青く夕日は赤くなります。密度はスケールハイト HR ＝ 8 km で指数に減ります。位相関数は `PR(µ) = 3/(16π) (1 + µ²)` です。

Mie 散乱はエアロゾルによるものです。スケールハイトは HM ≃ 1.2 km と小さく、位相関数は前方に強く偏ります。論文は Cornette-Shanks の近似 `PM(µ) = 3/(8π) · (1 − g²)(1 + µ²) / ((2 + g²)(1 + g² − 2gµ)^(3/2))` を使います。エアロゾルは光を吸収するので、消散係数 `βeM = βsM + βaM` を別に持ちます。大気の屈折による光線の曲がり（2 度以下）は、無視します。

## レンダリング方程式と近似 {#equation}

位置 x に方向 v から届く放射輝度 L は、3 つの項の和です（式 8）。

- L0: 太陽の光が x に届くまでに減ったもの。`T(x, xo) · Lsun`（式 9）。
- R[L]: 地面（xo）で反射した光が、減って届いたもの（式 10）。
- S[L]: x と xo の間で、x の方向に散乱された光（式 11）。`S[L] = ∫ T(x, y) J[L](y, v, s) dy`。

J[L] は点 y で方向 −v に散乱される光の量です（式 7）。T は透過率（式 5）で `exp(−∫ (βeR + βeM) dy)` です。

この式は複雑で地形の影（光の筋）があると、積分の中に遮蔽が入ります。論文は次の近似を導きます。

**単散乱（L1 まで）**は影を除いて、厳密に計算します。影の中の点は積分に寄与しないので、積分は x から影の始まる点 xs までの区間に縮みます。ここで遮蔽のない仮想の球の地面での値 `S̄` を使うと次の式になります（式 13）。

```text
S[L0](x, v, s) = S̄[L̄0](x, v, s) − T(x, xs) · S̄[L̄0](xs, v, s)
```

x から上端まで積分した値から、xs から先を引くことで x と xs の間だけが残ります。引く側に透過率 T(x, xs) を掛けるのが要点です。

**多重散乱（L2 以降）**は遮蔽の影響を近似します。多重散乱は昼間には単散乱より小さく、地面の寄与は地面が太陽に直接照らされていないときは小さいという理由です。遮蔽なしで計算した多重散乱を x から xs まで積分し（正と負の偏りが出る）、地面の項には地面の接平面による半球の環境遮蔽 `(1 + n·n̄)/2` を掛けます。

最終的に式 16 です。

```text
L ≃ L0 + R[L0] + R̂[L̄*] + S̄[L̄]|x − T(x, xs) · S̄[L̄]|xs
```

最初の 3 項は 2 次元のテーブル T と Ē から速く計算でき残りの 2 項が 4 次元のテーブル S の 2 回の参照です。

## 事前計算のアルゴリズム {#precompute}

テーブルは散乱の次数ごとに 1 つずつ計算して、足し合わせます（Algorithm 4.1）。

1. 透過率 T と 1 次散乱の ΔS、地面の照度 ΔE を計算する。
2. 次数 i ごとに前の次数の光を光源とみなして、散乱される光 ΔJ を計算する。
3. ΔJ を視線に沿って積分して、新しい ΔS にする（`ΔS(x, v, s) ← ∫ T(x, y) ΔJ(y, v, s) dy`）。
4. ΔE と ΔS を結果のテーブル E、S に足す。

論文はこの計算を GPU のフラグメント シェーダーで行い 5 次までの散乱を NVIDIA 8800 GTS で約 5 秒と書きます。そのため、大気の係数を変えてもすぐに作り直せます。2017 年の参照実装はこの反復を「点 q で、あらゆる方向から来る光が散乱される量（二重積分）」と「p から q への積分（一重）」の 2 段に分け、冗長な計算を省いています。

## テーブルと座標の割り当て {#tables}

### テーブルの形 {#table-shape}

論文は T(r, µ) を 64 × 256、地面の照度 E(r, µ) を 16 × 64 のテクスチャに入れます。4 次元の S は `S(ur, uµ, uµs, uν) = [C*, CM,r]` を 32 × 128 × 32 × 8 のテーブルにして、8 枚の 3D テクスチャを 1 つの 32 × 128 × 256 の RGBA テクスチャに詰めます。4 番目の座標（ν）の補間は手で行います。16 bit 浮動小数点で 8 MB で、Schafhitzel らの 128³ のテクスチャ（12 MB）より精度が高く、小さいと書かれています。

<svg class="fig flow" viewBox="0 0 700 218" role="img" aria-label="4D → 3D の詰め方"><defs><marker id="br-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">4D のテーブルを 3D テクスチャに詰める(幅 256 = ν 8 x µs 32、高さ 128 = µ、奥行き 32 = r)</text><rect x="40" y="40" width="68" height="120" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="74" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 0</text><line x1="40" y1="40" x2="40" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="57" y1="40" x2="57" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="74" y1="40" x2="74" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="91" y1="40" x2="91" y2="160" stroke="#94a3b8" stroke-width="0.4"/><rect x="110" y="40" width="68" height="120" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="144" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 1</text><line x1="110" y1="40" x2="110" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="127" y1="40" x2="127" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="144" y1="40" x2="144" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="161" y1="40" x2="161" y2="160" stroke="#94a3b8" stroke-width="0.4"/><rect x="180" y="40" width="68" height="120" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="214" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 2</text><line x1="180" y1="40" x2="180" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="197" y1="40" x2="197" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="214" y1="40" x2="214" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="231" y1="40" x2="231" y2="160" stroke="#94a3b8" stroke-width="0.4"/><rect x="250" y="40" width="68" height="120" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="284" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 3</text><line x1="250" y1="40" x2="250" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="267" y1="40" x2="267" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="284" y1="40" x2="284" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="301" y1="40" x2="301" y2="160" stroke="#94a3b8" stroke-width="0.4"/><rect x="320" y="40" width="68" height="120" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="354" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 4</text><line x1="320" y1="40" x2="320" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="337" y1="40" x2="337" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="354" y1="40" x2="354" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="371" y1="40" x2="371" y2="160" stroke="#94a3b8" stroke-width="0.4"/><rect x="390" y="40" width="68" height="120" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="424" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 5</text><line x1="390" y1="40" x2="390" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="407" y1="40" x2="407" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="424" y1="40" x2="424" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="441" y1="40" x2="441" y2="160" stroke="#94a3b8" stroke-width="0.4"/><rect x="460" y="40" width="68" height="120" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="494" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 6</text><line x1="460" y1="40" x2="460" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="477" y1="40" x2="477" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="494" y1="40" x2="494" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="511" y1="40" x2="511" y2="160" stroke="#94a3b8" stroke-width="0.4"/><rect x="530" y="40" width="68" height="120" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="564" y="104" text-anchor="middle" font-size="11" fill="currentColor">ν = 7</text><line x1="530" y1="40" x2="530" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="547" y1="40" x2="547" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="564" y1="40" x2="564" y2="160" stroke="#94a3b8" stroke-width="0.4"/><line x1="581" y1="40" x2="581" y2="160" stroke="#94a3b8" stroke-width="0.4"/><text x="40" y="182" text-anchor="start" font-size="10" fill="currentColor">各 ν の帯の中に、µs が 32 テクセル並ぶ</text><text x="600" y="100" text-anchor="start" font-size="10" fill="currentColor">← µ が縦 128</text><text x="40" y="206" text-anchor="start" font-size="10" fill="currentColor">奥行き 32 枚(r)。実行時は ν を 2 つの帯で読んで補間する → 3D の読み込み 2 回で 4D を作る</text></svg>

### Mie の 1 次散乱を分けて持つ {#mie-split}

4 次元のテーブルは角度の分解能が低くなります。特に、Mie の前方散乱は鋭いので、問題が出ます。そこで、1 次の Mie 散乱 CM ＝ S̄M[L̄0] をほかの散乱から分けて保存し、位相関数 PM は実行時に掛けます。残り `C* = S̄R[L̄0] + S̄[L̄*]/PR` も別に持ちます。3 色分で 6 個の値が要りますが論文は、赤の成分 CM,r だけを持ちほかを比例則で近似して 4 個にする方法も示します。`CM ≃ C* · (CM,r / C*,r) · (βsR,r / βsM,r) · (βsM / βsR)`。2017 年の実装はこの 2 つの方法を両方備えています。

### µ の写し替え {#mu-mapping}

単純な割り当てはµ を [−1, 1] から [0, 1] へ線形に写します。ところが、これでは空気遠近法の分解能が足りません。地表の観測者が水平を見て 100 km 先に山があるとします。山の位置ではµ ＝ d/√(r² + d²)、観測者の位置では µ ＝ 0 なので、差は 0.016 しかなくテーブルの 1 テクセル程度で、アーティファクトが出ます。

論文の解決策はµ を `uµ`（観測者から先の地形までの距離 do と水平線までの距離 dh、または上端までの距離 dH の比）に写すことです。同じ例で差は 0.11 になります。

C++ で式を計算しました。µ の差は 0.0157（128 分割で約 1 テクセル）、uµ の差は 0.096（約 12 テクセル）です。論文の 0.11 は距離を近似した値で、私の計算はそれより少し小さくなりました。

<svg class="fig flow" viewBox="0 0 640 164" role="img" aria-label="µ の写し替えの効果"><defs><marker id="br-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">100 km 先の山と観測者: 128 分割のテクセル数の差</text><text x="182" y="60" text-anchor="end" font-size="11" fill="currentColor">µ(線形)</text><rect x="190" y="40" width="24.5" height="28" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="220.52857142857144" y="59" text-anchor="start" font-size="11" fill="currentColor">1.01 テクセル</text><text x="182" y="104" text-anchor="end" font-size="11" fill="currentColor">u_µ(論文の割り当て)</text><rect x="190" y="84" width="298.7" height="28" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="494.7142857142857" y="103" text-anchor="start" font-size="11" fill="currentColor">12.3 テクセル</text><text x="190" y="150" text-anchor="start" font-size="10" fill="currentColor">差が 1 テクセル程度だと補間で潰れてアーティファクトが出る。12 テクセル離れれば解像できる</text></svg>

もう 1 つの問題は S が地平線で不連続なことです。視線の長さが地平線で急に変わるためで、連続な割り当てだと不連続をまたいで補間されて、アーティファクトが出ます。そこで、uµ 自体を地平線で不連続にします。論文の最終的な割り当ては次のとおりです。

```text
u_r  = ρ / H
u_µ  = 1/2 + (rµ + √Δ) / (2ρ)            （rµ < 0 かつ Δ > 0：地面に当たる向き）
       1/2 − (rµ − √(Δ + H²)) / (2ρ + 2H)  （それ以外：空へ抜ける向き）
u_µs = (1 − e^(−3µs − 0.6)) / (1 − e^(−3.6))
u_ν  = (1 + ν) / 2
（ρ = √(r² − Rg²)、H = √(Rt² − Rg²)、Δ = r²µ² − ρ²）
```

r と µs には地表付近と太陽の天頂角が 90 度付近で精度が上がるように、非線形の関数が使われています。2017 年の参照実装はこの割り当てを一般化し、地球固有の定数を取り除きました。µ は端まで使う形に直しµs は設定できる 1 つのパラメーター（`mu_s_min`）だけを使います。

## 光の筋（シャドウ ボリューム）{#shafts}

地形の影が大気に落ちると光の筋が出ます。多くの手法は視線に沿って数値積分し、シャドウ マップで日向かを調べます。論文は最大で 100 サンプル要ると見積もっています。

提案はシャドウ ボリュームを使う方法です。積分 S を事前計算してあるので、日向の区間 [xi, xi+1] の散乱は `T(x, xi) S|xi − T(x, xi+1) S|xi+1` で出ます。xi は地形のシャドウ ボリュームの境界です。ところが、シャドウ ボリュームの面には日向と日陰の境界でないもの（偽の境界）も多く、見分けるのは GPU に向きません。

そこで、影の区間の合計の長さ l だけを計算して、1 つの区間にまとめ視線の地面側の端に置きます。偽の境界で l が過大になるのは、シャドウ ボリュームの最も近い面と最も遠い面の間の距離で打ち切ります。地面を見るときは `l̃ = clamp(Δz − Δn · zground, 0, zground − zmin)`、空を見るときは `l̃ = clamp(Δz, 0, zmax)` です（式 17, 18）。ほとんどの場合に正しい結果で、そうでないときは近似になります。

2017 年の参照実装は式 17、18 を実装していますがシャドウ ボリュームのアルゴリズムは実装していません。

## 2017 年の参照実装 {#impl2017}

2008 年の実装にはコメントがなく、テストがなく地球向けの定数が埋め込まれていました。2017 年の実装は単位の次元を静的に検査し、単体テストを持ち太陽のスペクトルを設定できオゾン層に対応します。

透過率テクスチャは(r, µ) を上端までの距離 d を使って写します。`x_µ = (d − dmin) / (dmax − dmin)`、`x_r = ρ / H`。テクスチャの端での外挿を避けるため、値 x を `0.5/n + x (1 − 1/n)` に写して端のテクセルの中心に境界の値を置きます。

光学的長さは 500 区間の台形則で積分し、単散乱は 50 区間の台形則で積分します。太陽の透過率は太陽が円盤なので、水平線にかかっている間の見えている面積の割合を smoothstep で近似して掛けます。

多重散乱は次数 n ごとに前の次数のテクスチャを使って計算します。冗長な計算を避けるため「点 q から −ω 方向に散乱する光（二重積分）」と「p での光（単積分）」の 2 段に分けます。地面を経由する経路は平均の反射率を使って、事前計算に含めます。

## 実装してみる {#code}

論文の式と参照実装の文書に沿って、HLSL で書き直しました。`fxc`（cs_5_0、ps_5_0）でコンパイルして確かめました。実行して絵は確かめていません。多重散乱の反復は含めず単散乱までです。単位は km で「足した処理」「一例」と書いた所は、資料にない処理です。

### 幾何と密度 {#code-geometry}

```hlsl
// Bruneton & Neyret (2008) の事前計算散乱を、HLSL で書き直したもの。
// 中身: ① 球の幾何 ② 密度と光学的厚み ③ 透過率テクスチャ ④ 単散乱の事前計算 ⑤ 4D → 3D の座標 ⑥ 実行時の参照
// 単位は km。係数は 1/km。論文（2008）の式と、2017 年の参照実装の文書（バージョン 2017）に沿って書き直した。
// 多重散乱の反復（Algorithm 4.1 の i ≥ 1）は、このファイルには入れていない。

// ================= ① パラメーターと球の幾何 =================

cbuffer AtmosphereCB : register(b0) {
  float g_bottom_radius;        // 地表の半径 Rg [km]。論文: 6360
  float g_top_radius;           // 大気の上端の半径 Rt [km]。論文: 6420
  float g_mu_s_min;             // 太陽の天頂角の cos の下限。cos(102°) ≒ -0.208（一例。夜側をどこまで持つか）
  float g_mie_g;                // Mie の位相関数の g。論文の図 6 は 0.76
  float3 g_beta_rayleigh;       // レイリー散乱係数 [1/km]。論文: (5.8, 13.5, 33.1) × 1e-3（680, 550, 440 nm）
  float g_height_rayleigh;      // レイリーのスケールハイト HR [km]。論文: 8
  float3 g_beta_mie_scatter;    // Mie 散乱係数 [1/km]。論文の図 7: 2.2 × 1e-2
  float g_height_mie;           // Mie のスケールハイト HM [km]。論文: 1.2
  float3 g_beta_mie_extinct;    // Mie 消散係数 [1/km]。散乱 / 0.9（散乱の割合 0.9）
  float g_sun_angular_radius;   // 太陽の見かけの半径 [rad]。約 0.00468
  float3 g_solar_irradiance;    // 大気の上端での太陽放射照度（RGB）
  float g_pad;
};

// テクスチャの大きさ。単散乱の 3D は、論文と同じ 32 x 128 x 256（= 8 x 32 のνと μs を横に並べる）。
static const int kTransW = 256, kTransH = 64;               // 透過率: 256 x 64
static const int kNuSize = 8, kMuSSize = 32, kMuSize = 128, kRSize = 32;   // ν, μs, μ, r の分割数

float ClampCosine(float mu) { return clamp(mu, -1.0, 1.0); }          // acos や sqrt の NaN を避ける
float SafeSqrt(float a) { return sqrt(max(a, 0.0)); }                  // 浮動小数点の誤差で負にならないように

// 点 (半径 r、視線の天頂角の cos = mu) から、大気の上端までの距離。
// 視線上の点 d の位置の二乗は d² + 2 r μ d + r²。それが Rt² になる d を解く。
float DistanceToTop(float r, float mu) {
  float discriminant = r * r * (mu * mu - 1.0) + g_top_radius * g_top_radius;
  return max(-r * mu + SafeSqrt(discriminant), 0.0);
}

// 同じく地表まで（地面にぶつかる向きのときだけ意味がある）。手前の交点を取るので、符号が逆。
float DistanceToBottom(float r, float mu) {
  float discriminant = r * r * (mu * mu - 1.0) + g_bottom_radius * g_bottom_radius;
  return max(-r * mu - SafeSqrt(discriminant), 0.0);
}

// 視線が地面に当たるか。μ < 0 で、判別式が 0 以上。
bool RayIntersectsGround(float r, float mu) {
  return mu < 0.0 && r * r * (mu * mu - 1.0) + g_bottom_radius * g_bottom_radius >= 0.0;
}

// ================= ② 密度と光学的厚み =================

// 高度 h [km] での、地表を 1 とした密度。指数で減る。
float RayleighDensity(float h) { return exp(-h / g_height_rayleigh); }
float MieDensity(float h) { return exp(-h / g_height_mie); }

// 点 (r, μ) から上端までの、密度の線積分（長さの次元 [km]）。台形則で 500 区間（参照実装と同じ数）。
// 結果が (レイリー, Mie) の 2 成分。これに散乱係数を掛けて exp すれば透過率。
float2 OpticalLengthToTop(float r, float mu) {
  const int kSamples = 500;
  float dx = DistanceToTop(r, mu) / kSamples;                      // 1 区間の長さ
  float2 result = 0;
  for (int i = 0; i <= kSamples; ++i) {
    float d = i * dx;                                              // 点 p から d だけ進んだ位置
    float r_i = sqrt(d * d + 2.0 * r * mu * d + r * r);            // そこの惑星中心からの距離
    float h = r_i - g_bottom_radius;                               // 高度
    float weight = (i == 0 || i == kSamples) ? 0.5 : 1.0;          // 台形則の重み（両端は半分）
    result += float2(RayleighDensity(h), MieDensity(h)) * weight * dx;
  }
  return result;
}
```

視線 `(r, µ)` から上端までの距離は `d² + 2rµd + r² = Rt²` を d について解いた式です。地面に当たる向きは手前の交点を取るので、符号が逆になります。光学的長さは台形則で 500 区間です。

### 透過率テクスチャ {#code-transmittance}

```hlsl
// ================= ③ 透過率テクスチャ =================

// [0, 1] の値 x を、テクセル中心だけを使う座標 [0.5/n, 1 - 0.5/n] に写す。
// こうしないと、端で外挿された値を読んでしまう（参照実装の GetTextureCoordFromUnitRange）。
float UnitToTexCoord(float x, int size) { return 0.5 / size + x * (1.0 - 1.0 / size); }
float TexCoordToUnit(float u, int size) { return (u - 0.5 / size) / (1.0 - 1.0 / size); }

// (r, μ) → 透過率テクスチャの (u, v)。μ は「上端までの距離 d」で写す（水平線付近が密になる）。
float2 TransmittanceUvFromRMu(float r, float mu) {
  float H = sqrt(g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius);   // 地表の水平視線の上端までの距離
  float rho = SafeSqrt(r * r - g_bottom_radius * g_bottom_radius);                    // 水平線までの距離
  float d = DistanceToTop(r, mu);
  float d_min = g_top_radius - r;                                  // 真上を見たときの距離（最小）
  float d_max = rho + H;                                           // 水平線を見たときの距離（最大）
  float x_mu = (d - d_min) / (d_max - d_min);
  float x_r = rho / H;                                             // 高さは「水平線までの距離」で写す
  return float2(UnitToTexCoord(x_mu, kTransW), UnitToTexCoord(x_r, kTransH));
}

// 逆写像: テクスチャの画素 (u, v) → (r, μ)。事前計算のとき、画素ごとに呼ぶ。
void RMuFromTransmittanceUv(float2 uv, out float r, out float mu) {
  float x_mu = TexCoordToUnit(uv.x, kTransW);
  float x_r = TexCoordToUnit(uv.y, kTransH);
  float H = sqrt(g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius);
  float rho = H * x_r;
  r = sqrt(rho * rho + g_bottom_radius * g_bottom_radius);
  float d_min = g_top_radius - r;
  float d_max = rho + H;
  float d = d_min + x_mu * (d_max - d_min);
  // d² + 2 r μ d + r² = Rt² を μ について解き、H² = Rt² - Rg², ρ² = r² - Rg² を使うと次の形になる。
  mu = (d == 0.0) ? 1.0 : ClampCosine((H * H - rho * rho - d * d) / (2.0 * r * d));
}

RWTexture2D<float4> g_transmittance_out : register(u0);
Texture2D<float4> g_transmittance : register(t0);
SamplerState g_linear_clamp : register(s0);

// 透過率テクスチャを作る。画素ごとに 500 区間の積分をする重い処理だが、一度だけ。
[numthreads(8, 8, 1)]
void PrecomputeTransmittanceCS(uint3 id : SV_DispatchThreadID) {
  if (id.x >= (uint)kTransW || id.y >= (uint)kTransH) return;
  float r, mu;
  RMuFromTransmittanceUv((id.xy + 0.5) / float2(kTransW, kTransH), r, mu);   // 画素の中心
  float2 len = OpticalLengthToTop(r, mu);                          // (レイリー, Mie) の光学的長さ
  float3 optical_depth = g_beta_rayleigh * len.x + g_beta_mie_extinct * len.y;
  g_transmittance_out[id.xy] = float4(exp(-optical_depth), 1.0);   // ベール・ランベルト則
}

// 点 (r, μ) から大気の上端までの透過率（1 回の読み込み）。
float3 TransmittanceToTop(float r, float mu) {
  return g_transmittance.SampleLevel(g_linear_clamp, TransmittanceUvFromRMu(r, mu), 0).rgb;
}

// 点 p から d だけ離れた点 q までの透過率。T(p,q) = T(p,上端) / T(q,上端)（地面に当たる向きは逆の向きで）。
float3 Transmittance(float r, float mu, float d, bool ray_hits_ground) {
  float r_d = clamp(sqrt(d * d + 2.0 * r * mu * d + r * r), g_bottom_radius, g_top_radius);   // q の半径
  float mu_d = ClampCosine((r * mu + d) / r_d);                    // q での視線の天頂角の cos
  float3 result;
  if (ray_hits_ground) {
    result = TransmittanceToTop(r_d, -mu_d) / TransmittanceToTop(r, -mu);   // 地面に当たる向きは、逆向きで比べる
  } else {
    result = TransmittanceToTop(r, mu) / TransmittanceToTop(r_d, mu_d);
  }
  return min(result, 1.0);                                         // 誤差で 1 を超えるのを防ぐ
}

// 点から太陽までの透過率。太陽は円盤なので、地平線にかかっている間は、見えている面積の割合を掛ける。
// 割合は smoothstep で近似できる（参照実装の説明）。
float3 TransmittanceToSun(float r, float mu_s) {
  float sin_theta_h = g_bottom_radius / r;                         // 水平線の天頂角の sin
  float cos_theta_h = -sqrt(max(1.0 - sin_theta_h * sin_theta_h, 0.0));   // 水平線の cos（負）
  return TransmittanceToTop(r, mu_s) *
         smoothstep(-sin_theta_h * g_sun_angular_radius, sin_theta_h * g_sun_angular_radius, mu_s - cos_theta_h);
}
```

透過率は 2 つの変数 (r, µ) だけの関数で、滑らかなので小さな 2D テクスチャに入れます。点 p から q への透過率は `T(p, q) = T(p, 上端) / T(q, 上端)` の比で、2 回の読み込みで求まります。太陽までの透過率は円盤の見えている割合を smoothstep で掛けます。

### 単散乱の事前計算 {#code-single}

```hlsl
// ================= ④ 単散乱の事前計算 =================

// 位相関数。ν は視線と太陽の向きのなす角の cos。
float RayleighPhase(float nu) { return 3.0 / (16.0 * 3.14159265) * (1.0 + nu * nu); }
// 論文の式 (4)、Cornette-Shanks。
float MiePhase(float g, float nu) {
  float k = 3.0 / (8.0 * 3.14159265) * (1.0 - g * g) / (2.0 + g * g);
  return k * (1.0 + nu * nu) / pow(max(1.0 + g * g - 2.0 * g * nu, 1e-4), 1.5);
}

// 点 p (r, μ, μs, ν) から視線に沿って d 進んだ点 q で、散乱して p に届く光（位相関数と係数は後で掛ける）。
void SingleScatteringIntegrand(float r, float mu, float mu_s, float nu, float d, bool ray_hits_ground,
                               out float3 rayleigh, out float3 mie) {
  float r_d = clamp(sqrt(d * d + 2.0 * r * mu * d + r * r), g_bottom_radius, g_top_radius);   // q の半径
  float mu_s_d = ClampCosine((r * mu_s + d * nu) / r_d);           // q での太陽の天頂角の cos
  // 太陽 → q の透過率 × q → p の透過率。
  float3 transmittance = Transmittance(r, mu, d, ray_hits_ground) * TransmittanceToSun(r_d, mu_s_d);
  float h = r_d - g_bottom_radius;                                 // q の高度
  rayleigh = transmittance * RayleighDensity(h);
  mie = transmittance * MieDensity(h);
}

// p から視線方向の最も近い大気の境界（上端か地面）までを積分。台形則で 50 区間。
void SingleScattering(float r, float mu, float mu_s, float nu, bool ray_hits_ground,
                      out float3 rayleigh, out float3 mie) {
  const int kSamples = 50;
  float length_to_boundary = ray_hits_ground ? DistanceToBottom(r, mu) : DistanceToTop(r, mu);
  float dx = length_to_boundary / kSamples;
  float3 sum_r = 0, sum_m = 0;
  for (int i = 0; i <= kSamples; ++i) {
    float3 ri, mi;
    SingleScatteringIntegrand(r, mu, mu_s, nu, i * dx, ray_hits_ground, ri, mi);
    float weight = (i == 0 || i == kSamples) ? 0.5 : 1.0;
    sum_r += ri * weight;
    sum_m += mi * weight;
  }
  // 太陽の放射照度と散乱係数を掛ける。位相関数は、角度の精度のため、実行時に掛ける。
  rayleigh = sum_r * dx * g_solar_irradiance * g_beta_rayleigh;
  mie = sum_m * dx * g_solar_irradiance * g_beta_mie_scatter;
}
```

積分は p から視線に沿って進み各点 q で、太陽 → q の透過率と q → p の透過率を掛けます。レイリーと Mie は密度だけが違うので、同じ透過率を共有します。太陽の放射照度と散乱係数は掛けますが、位相関数は掛けません。角度の精度を保つため実行時に掛けます。

### 4 次元 → 3 次元の座標 {#code-mapping}

```hlsl
// ================= ⑤ 4 次元 → 3 次元の座標 =================

// 順写像: (r, μ, μs, ν) → (u_ν, u_μs, u_μ, u_r)。論文の式と、2017 年版の改良（端まで使う μ）に沿う。
float4 ScatteringUvwzFromRMuMuSNu(float r, float mu, float mu_s, float nu, bool ray_hits_ground) {
  float H = sqrt(g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius);
  float rho = SafeSqrt(r * r - g_bottom_radius * g_bottom_radius);
  float u_r = UnitToTexCoord(rho / H, kRSize);                     // r: 水平線までの距離で写す

  float r_mu = r * mu;
  float discriminant = r_mu * r_mu - r * r + g_bottom_radius * g_bottom_radius;
  float u_mu;
  if (ray_hits_ground) {
    // 地面に当たる側 [0, 0.5)。地面までの距離 d を、最小（真下）と最大（水平線）の間で写す。
    float d = -r_mu - SafeSqrt(discriminant);
    float d_min = r - g_bottom_radius;
    float d_max = rho;
    u_mu = 0.5 - 0.5 * UnitToTexCoord(d_max == d_min ? 0.0 : (d - d_min) / (d_max - d_min), kMuSize / 2);
  } else {
    // 空へ抜ける側 [0.5, 1]。上端までの距離を写す。水平線で u_μ が不連続になる（補間をまたがせない）。
    float d = -r_mu + SafeSqrt(discriminant + H * H);
    float d_min = g_top_radius - r;
    float d_max = rho + H;
    u_mu = 0.5 + 0.5 * UnitToTexCoord((d - d_min) / (d_max - d_min), kMuSize / 2);
  }

  // μs: 地表から太陽方向の上端までの距離で写し、水平線付近を密にする 1 つの非線形関数を使う。
  float d = DistanceToTop(g_bottom_radius, mu_s);
  float d_min = g_top_radius - g_bottom_radius;
  float d_max = H;
  float a = (d - d_min) / (d_max - d_min);
  float D = DistanceToTop(g_bottom_radius, g_mu_s_min);
  float A = (D - d_min) / (d_max - d_min);
  float u_mu_s = UnitToTexCoord(max(1.0 - a / A, 0.0) / (1.0 + a), kMuSSize);

  float u_nu = (nu + 1.0) / 2.0;                                   // ν は線形
  return float4(u_nu, u_mu_s, u_mu, u_r);
}

// 逆写像: 3D テクスチャの画素 (x, y, z) → (r, μ, μs, ν)。x に ν と μs を詰めている。
void RMuMuSNuFromFragCoord(float3 frag, out float r, out float mu, out float mu_s, out float nu,
                           out bool ray_hits_ground) {
  float frag_nu = floor(frag.x / kMuSSize);                         // x の上位: ν の番号
  float frag_mu_s = fmod(frag.x, (float)kMuSSize);                  // x の下位: μs の番号
  float4 uvwz = float4(frag_nu / (kNuSize - 1), frag_mu_s / kMuSSize, frag.y / kMuSize, frag.z / kRSize);

  float H = sqrt(g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius);
  float rho = H * TexCoordToUnit(uvwz.w, kRSize);
  r = sqrt(rho * rho + g_bottom_radius * g_bottom_radius);

  if (uvwz.z < 0.5) {
    float d_min = r - g_bottom_radius;
    float d_max = rho;
    float d = d_min + (d_max - d_min) * TexCoordToUnit(1.0 - 2.0 * uvwz.z, kMuSize / 2);
    mu = (d == 0.0) ? -1.0 : ClampCosine(-(rho * rho + d * d) / (2.0 * r * d));
    ray_hits_ground = true;
  } else {
    float d_min = g_top_radius - r;
    float d_max = rho + H;
    float d = d_min + (d_max - d_min) * TexCoordToUnit(2.0 * uvwz.z - 1.0, kMuSize / 2);
    mu = (d == 0.0) ? 1.0 : ClampCosine((H * H - rho * rho - d * d) / (2.0 * r * d));
    ray_hits_ground = false;
  }

  float x_mu_s = TexCoordToUnit(uvwz.y, kMuSSize);
  float d_min = g_top_radius - g_bottom_radius;
  float d_max = H;
  float D = DistanceToTop(g_bottom_radius, g_mu_s_min);
  float A = (D - d_min) / (d_max - d_min);
  float a = (A - x_mu_s * A) / (1.0 + x_mu_s * A);
  float d = d_min + min(a, A) * (d_max - d_min);
  mu_s = (d == 0.0) ? 1.0 : ClampCosine((H * H - d * d) / (2.0 * g_bottom_radius * d));
  nu = ClampCosine(uvwz.x * 2.0 - 1.0);
  // ν は μ と μs から独立ではない。取りうる範囲に切る（2 本の単位ベクトルのなす角の範囲）。
  float s = sqrt((1.0 - mu * mu) * (1.0 - mu_s * mu_s));
  nu = clamp(nu, mu * mu_s - s, mu * mu_s + s);
}

RWTexture3D<float4> g_rayleigh_out : register(u1);   // 単散乱のレイリー成分
RWTexture3D<float4> g_mie_out : register(u2);        // 単散乱の Mie 成分

// 単散乱の 3D テクスチャを作る。1 スレッド = 1 テクセル。サイズは (kNuSize * kMuSSize, kMuSize, kRSize)。
[numthreads(8, 8, 1)]
void PrecomputeSingleScatteringCS(uint3 id : SV_DispatchThreadID) {
  if (id.x >= (uint)(kNuSize * kMuSSize) || id.y >= (uint)kMuSize || id.z >= (uint)kRSize) return;
  float r, mu, mu_s, nu;
  bool ray_hits_ground;
  RMuMuSNuFromFragCoord(float3(id) + 0.5, r, mu, mu_s, nu, ray_hits_ground);   // 画素の中心
  float3 rayleigh, mie;
  SingleScattering(r, mu, mu_s, nu, ray_hits_ground, rayleigh, mie);
  g_rayleigh_out[id] = float4(rayleigh, 1.0);
  g_mie_out[id] = float4(mie, 1.0);
}
```

順写像（`ScatteringUvwzFromRMuMuSNu`）と逆写像（`RMuMuSNuFromFragCoord`）が対になっています。事前計算は逆写像で「この画素は (r, µ, µs, ν) のどれか」を求め、実行時は順写像で「この (r, µ, µs, ν) はどの画素か」を求めます。3D テクスチャの x にν と µs を詰めます（x = ν の番号 × 32 + µs の番号）。ν はµ と µs が決まると、とれる範囲が決まります。そのため、逆写像の最後でその範囲に切ります。

### 実行時の参照 {#code-runtime}

```hlsl
// ================= ⑥ 実行時の参照 =================

Texture3D<float4> g_rayleigh_tex : register(t1);
Texture3D<float4> g_mie_tex : register(t2);

// 4 次元の補間を、3D テクスチャの 2 回の読み込みで作る（ν 方向は自前で lerp）。
float3 ReadScattering(Texture3D<float4> tex, float r, float mu, float mu_s, float nu, bool ray_hits_ground) {
  float4 uvwz = ScatteringUvwzFromRMuMuSNu(r, mu, mu_s, nu, ray_hits_ground);
  float tex_x = uvwz.x * (kNuSize - 1);                            // ν の連続位置
  float floor_x = floor(tex_x);
  float t = tex_x - floor_x;                                       // 隣の ν との補間係数
  float3 uvw0 = float3((floor_x + uvwz.y) / kNuSize, uvwz.z, uvwz.w);
  float3 uvw1 = float3((floor_x + 1.0 + uvwz.y) / kNuSize, uvwz.z, uvwz.w);
  return tex.SampleLevel(g_linear_clamp, uvw0, 0).rgb * (1.0 - t) +
         tex.SampleLevel(g_linear_clamp, uvw1, 0).rgb * t;
}

// 空の色。camera は惑星中心を原点とした位置 [km]、view は視線、sun は太陽へ向かう単位ベクトル。
// 位相関数は、ここで掛ける。論文の言う「Mie の 1 次散乱だけを分けて保存する」理由はここにある。
float3 SkyRadiance(float3 camera, float3 view, float3 sun) {
  float r = length(camera);
  float mu = dot(camera, view) / r;                                // 視線の天頂角の cos
  float mu_s = dot(camera, sun) / r;                               // 太陽の天頂角の cos
  float nu = dot(view, sun);                                       // 視線と太陽のなす角の cos
  bool hits_ground = RayIntersectsGround(r, mu);
  float3 rayleigh = ReadScattering(g_rayleigh_tex, r, mu, mu_s, nu, hits_ground);
  float3 mie = ReadScattering(g_mie_tex, r, mu, mu_s, nu, hits_ground);
  return rayleigh * RayleighPhase(nu) + mie * MiePhase(g_mie_g, nu);
}

// 空気遠近法: カメラから点 p (距離 distance) までの間に散乱された光。論文の恒等式（式 13 の考え方）:
//   S(x, v, s) - T(x, p) · S(p, v, s)    （S は上端まで積分した散乱）
// 点 p から先の散乱を引くことで、x と p の間だけが残る。
float3 AerialPerspective(float3 camera, float3 view, float3 sun, float distance_km, out float3 transmittance) {
  float r = length(camera);
  float mu = dot(camera, view) / r;
  float mu_s = dot(camera, sun) / r;
  float nu = dot(view, sun);
  bool hits_ground = RayIntersectsGround(r, mu);

  // p の位置での (r, μ, μs)。
  float r_p = clamp(sqrt(distance_km * distance_km + 2.0 * r * mu * distance_km + r * r), g_bottom_radius, g_top_radius);
  float mu_p = ClampCosine((r * mu + distance_km) / r_p);
  float mu_s_p = ClampCosine((r * mu_s + distance_km * nu) / r_p);

  transmittance = Transmittance(r, mu, distance_km, hits_ground);  // x から p まで
  float3 s_x = ReadScattering(g_rayleigh_tex, r, mu, mu_s, nu, hits_ground) * RayleighPhase(nu) +
               ReadScattering(g_mie_tex, r, mu, mu_s, nu, hits_ground) * MiePhase(g_mie_g, nu);
  float3 s_p = ReadScattering(g_rayleigh_tex, r_p, mu_p, mu_s_p, nu, hits_ground) * RayleighPhase(nu) +
               ReadScattering(g_mie_tex, r_p, mu_p, mu_s_p, nu, hits_ground) * MiePhase(g_mie_g, nu);
  return max(s_x - transmittance * s_p, 0.0);                      // 誤差で負にならないように
}

// 画素シェーダー: 空 + 地表の物体に空気遠近法をかける。scene_color は物体の色、distance_km はその距離。
float4 ApplyAtmospherePS(float4 pos : SV_Position, float3 camera : TEXCOORD0, float3 view : TEXCOORD1,
                         float3 sun : TEXCOORD2, float3 scene_color : TEXCOORD3, float distance_km : TEXCOORD4)
    : SV_Target {
  float3 t;
  float3 in_scatter = AerialPerspective(camera, normalize(view), sun, distance_km, t);
  return float4(in_scatter + t * scene_color, 1.0);              // 物体の色 × 透過率 + 空気遠近法
}
```

空の色は `SkyRadiance` で 4 回の 3D 読み込み（2 テクスチャ × ν の補間 2 回）と位相関数の乗算だけです。空気遠近法は `AerialPerspective` で式 13 の恒等式 `S(x) − T(x, p) · S(p)` を使います。p は物体の位置です。

## 数字を出す C++ {#cpp}

透過率の計算、µ の写し替えの効果、テーブルの大きさと計算量を C++ で確かめます。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。

```cpp
// Bruneton & Neyret (2008) の数字を確かめる。
//  1. 太陽の天頂角ごとの、地表から大気の上端までの透過率（夕焼けが赤くなる理由）
//  2. 視線の天頂角 µ を u_µ に写し替えると、空気遠近法の分解能がどれだけ上がるか（論文の 0.016 → 0.11）
//  3. テーブルの大きさと、事前計算・実行時の計算量
#include <cmath>
#include <cstdio>
#include <initializer_list>

namespace {
constexpr double kPi = 3.14159265358979323846;
constexpr double kRg = 6360.0, kRt = 6420.0;              // 地表と上端の半径 [km]（論文 2.1 節）
constexpr double kHr = 8.0, kHm = 1.2;                    // スケールハイト [km]
constexpr double kBetaR[3] = {5.8e-3, 13.5e-3, 33.1e-3};  // レイリー散乱係数 [1/km]（680, 550, 440 nm）
constexpr double kBetaMs = 2.2e-2;                        // Mie 散乱係数 [1/km]（論文の図 7: 2.2e-5 /m）
constexpr double kBetaMe = kBetaMs / 0.9;                 // Mie 消散係数（散乱の割合 0.9）


// 点 (r, mu) から上端までの距離 [km]。
double DistanceToTop(double r, double mu) {
  const double disc = r * r * (mu * mu - 1.0) + kRt * kRt;
  return -r * mu + std::sqrt(disc > 0 ? disc : 0);
}

// 台形則で、密度の線積分 [km]（density は高度 h の関数）。
template <typename F>
double OpticalLength(double r, double mu, F density, int samples) {
  const double dx = DistanceToTop(r, mu) / samples;
  double sum = 0;
  for (int i = 0; i <= samples; ++i) {
    const double d = i * dx;
    const double ri = std::sqrt(d * d + 2 * r * mu * d + r * r);
    const double w = (i == 0 || i == samples) ? 0.5 : 1.0;
    sum += density(ri - kRg) * w * dx;
  }
  return sum;
}

// 論文の式で、µ を u_µ に写す（空へ抜ける側と、地面に当たる側）。r, µ は km と無次元。
double UMu(double r, double mu) {
  const double rho = std::sqrt(r * r - kRg * kRg);
  const double H = std::sqrt(kRt * kRt - kRg * kRg);
  const double delta = r * r * mu * mu - rho * rho;
  if (r * mu < 0.0 && delta > 0.0) return 0.5 + (r * mu + std::sqrt(delta)) / (2.0 * rho);
  return 0.5 - (r * mu - std::sqrt(delta + H * H)) / (2.0 * rho + 2.0 * H);
}
}  // namespace

int main() {
  std::printf("== 地表から上端までの透過率（レイリー + Mie）==\n");
  std::printf("太陽の天頂角   赤(680)   緑(550)   青(440)\n");
  for (double deg : {0.0, 60.0, 80.0, 85.0, 88.0, 90.0}) {
    const double mu = std::cos(deg * kPi / 180.0);
    const double lr = OpticalLength(kRg, mu, [](double h) { return std::exp(-h / kHr); }, 4000);
    const double lm = OpticalLength(kRg, mu, [](double h) { return std::exp(-h / kHm); }, 4000);
    std::printf("%6.0f 度     %.3f     %.3f     %.3f\n", deg, std::exp(-(kBetaR[0] * lr + kBetaMe * lm)),
                std::exp(-(kBetaR[1] * lr + kBetaMe * lm)), std::exp(-(kBetaR[2] * lr + kBetaMe * lm)));
  }

  std::printf("\n== µ の写し替え（地表の観測者が水平を見る。100 km 先に山）==\n");
  const double r0 = kRg + 0.01;                               // 観測者の半径（地表の 10 m 上）
  const double d = 100.0;                                     // 山までの距離 [km]
  const double r1 = std::sqrt(r0 * r0 + d * d);               // 山の半径（水平に進んだ点）
  const double mu0 = 0.0;
  const double mu1 = d / r1;                                  // 山の位置での視線の cos
  std::printf("µ:  観測者 %.4f、山 %.4f、差 %.4f\n", mu0, mu1, mu1 - mu0);
  std::printf("u_µ: 観測者 %.4f、山 %.4f、差 %.4f\n", UMu(r0, mu0), UMu(r1, mu1), std::fabs(UMu(r1, mu1) - UMu(r0, mu0)));
  std::printf("128 分割のとき、µ の差は %.2f テクセル、u_µ の差は %.1f テクセル\n", (mu1 - mu0) * 128 / 2.0,
              std::fabs(UMu(r1, mu1) - UMu(r0, mu0)) * 128);

  std::printf("\n== テーブルの大きさ ==\n");
  const double rgba16 = 8.0;                                  // RGBA16F = 8 バイト
  std::printf("論文の S: 32 x 128 x 32 x 8 = %d 要素、RGBA16F で %.1f MiB\n", 32 * 128 * 32 * 8,
              32.0 * 128 * 32 * 8 * rgba16 / (1024 * 1024));
  std::printf("このページの HLSL: 単散乱を 2 枚（レイリー, Mie）= 256 x 128 x 32 を 2 枚で %.1f MiB\n",
              2.0 * 256 * 128 * 32 * rgba16 / (1024 * 1024));
  std::printf("透過率 256 x 64: %.2f MiB、論文の T 64 x 256: 同じ要素数\n", 256.0 * 64 * rgba16 / (1024 * 1024));
  std::printf("Schafhitzel らの 128^3: %.1f MiB（RGBA16F）\n", 128.0 * 128 * 128 * rgba16 / (1024 * 1024));

  std::printf("\n== 計算量 ==\n");
  std::printf("透過率の事前計算: %d 画素 x 501 サンプル = %.1f M 回の exp\n", 256 * 64, 256.0 * 64 * 501 / 1e6);
  std::printf("単散乱の事前計算: %d テクセル x 51 サンプル = %.1f M 回の積分点（各 2 回の透過率の参照）\n", 256 * 128 * 32,
              256.0 * 128 * 32 * 51 / 1e6);
  std::printf("実行時（空 1 画素）: 散乱 2 テクスチャ x 3D 2 回 = 4 回の読み込み + 透過率\n");
  return 0;
}
```

```text title="実行結果"
== 地表から上端までの透過率（レイリー + Mie）==
太陽の天頂角   赤(680)   緑(550)   青(440)
     0 度     0.927     0.872     0.745
    60 度     0.860     0.761     0.557
    80 度     0.654     0.464     0.195
    85 度     0.450     0.241     0.049
    88 度     0.199     0.063     0.003
    90 度     0.013     0.002     0.000
```

```text title="実行結果（続き）"
== µ の写し替え（地表の観測者が水平を見る。100 km 先に山）==
µ:  観測者 0.0000、山 0.0157、差 0.0157
u_µ: 観測者 0.9936、山 0.8972、差 0.0964
128 分割のとき、µ の差は 1.01 テクセル、u_µ の差は 12.3 テクセル
```

```text title="実行結果（続き）"
== テーブルの大きさ ==
論文の S: 32 x 128 x 32 x 8 = 1048576 要素、RGBA16F で 8.0 MiB
このページの HLSL: 単散乱を 2 枚（レイリー, Mie）= 256 x 128 x 32 を 2 枚で 16.0 MiB
透過率 256 x 64: 0.12 MiB、論文の T 64 x 256: 同じ要素数
Schafhitzel らの 128^3: 16.0 MiB（RGBA16F）
```

```text title="実行結果（続き）"
== 計算量 ==
透過率の事前計算: 16384 画素 x 501 サンプル = 8.2 M 回の exp
単散乱の事前計算: 1048576 テクセル x 51 サンプル = 53.5 M 回の積分点（各 2 回の透過率の参照）
実行時（空 1 画素）: 散乱 2 テクスチャ x 3D 2 回 = 4 回の読み込み + 透過率
```

夕焼けが赤くなる理由が数字に出ています。太陽の天頂角が 0 度（真上）では青の透過率が 0.745 ですが、88 度では青が 0.003、赤が 0.199 です。青の光が大気を長く通るあいだにほとんど散乱され尽くして、赤が残ります。

<svg class="fig flow" viewBox="0 0 620 226" role="img" aria-label="太陽の天頂角と透過率"><defs><marker id="br-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">地表から上端までの透過率と、太陽の天頂角(レイリー + Mie)</text><line x1="60" y1="186" x2="540" y2="186" stroke="#94a3b8"/><line x1="60" y1="36" x2="60" y2="186" stroke="#94a3b8"/><line x1="60" y1="148.5" x2="540" y2="148.5" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="152.5" text-anchor="end" font-size="10" fill="currentColor">0.25</text><line x1="60" y1="111.0" x2="540" y2="111.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="115.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><line x1="60" y1="73.5" x2="540" y2="73.5" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="77.5" text-anchor="end" font-size="10" fill="currentColor">0.75</text><line x1="60" y1="36.0" x2="540" y2="36.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="40.0" text-anchor="end" font-size="10" fill="currentColor">1</text><polyline points="60.0,46.9 380.0,57.0 486.7,87.9 513.3,118.5 529.3,156.2 540.0,184.1" fill="none" stroke="#e05a4f" stroke-width="2.5"/><text x="66.0" y="40.94999999999999" text-anchor="start" font-size="10" fill="currentColor">赤 680nm</text><polyline points="60.0,55.2 380.0,71.8 486.7,116.4 513.3,149.8 529.3,176.6 540.0,185.7" fill="none" stroke="#4caf7a" stroke-width="2.5"/><text x="66.0" y="63.19999999999999" text-anchor="start" font-size="10" fill="currentColor">緑 550nm</text><polyline points="60.0,74.2 380.0,102.4 486.7,156.8 513.3,178.7 529.3,185.6 540.0,186.0" fill="none" stroke="#4c8bf5" stroke-width="2.5"/><text x="66.0" y="96.25" text-anchor="start" font-size="10" fill="currentColor">青 440nm</text><text x="60.0" y="202" text-anchor="middle" font-size="10" fill="currentColor">0°</text><text x="380.0" y="202" text-anchor="middle" font-size="10" fill="currentColor">60°</text><text x="486.66666666666663" y="202" text-anchor="middle" font-size="10" fill="currentColor">80°</text><text x="513.3333333333333" y="202" text-anchor="middle" font-size="10" fill="currentColor">85°</text><text x="529.3333333333333" y="202" text-anchor="middle" font-size="10" fill="currentColor">88°</text><text x="540.0" y="202" text-anchor="middle" font-size="10" fill="currentColor">90°</text></svg>

## 論文の結果とコスト {#results}

論文は NVIDIA 8800 GTS で、1024 × 768 の図 8 の右の場面で、光の筋なしで 125 fps と報告しています。内訳は地形（陰影なし）が 5 ms、式 17、18 の最初の 3 項が 0.4 ms、残りの項が 2.6 ms（非線形な割り当ての評価に 1 ms を含む）です。サンプルは 10 回未満です。光の筋ありでは 25 fps で、最初の 2 つのパス（地形の深度とシャドウ ボリューム）で約 32 ms かかります。比較として O'Neil の方法を自分で再実装し、サンプル 10 回で 50 fps だったと書かれています（光の筋なし、単散乱で同じ品質）。

精度は CIE の晴天モデル（実測に合わせたもの）と比べて、よく合うと書かれています。ただし、水平線付近で過大になります。Preetham のモデルも同じ問題を持つと指摘していて、現在の CG の物理モデルに由来するだろうと書かれています。

## 限界 {#limits}

論文自身が挙げる限界はエアロゾルの性質が高度だけの関数で、実際の大気のように天候で大きく変わることを表せないことです。事前計算は速い（数秒）ので性質を変えることはできますが、均一なままです。今後の課題として雲が地面の照度と空気遠近法に及ぼす影響が挙げられています。

2008 年の方式は動的な霞や場所で変わる密度に向きません。雲との合成も空間的に均一な大気を前提にするので、難しくなります。Hillaire（2020）の方式との比較は、そのページ（[Hillaire 2020](hillaire.md)）を参照してください。このページでは読んでいないので、数字を書きません。

## よくあるミス

??? failure "大気のパラメーターを変えても、空が変わらない"
    テーブルは事前計算なので、係数を変えたら作り直す。透過率、単散乱、（多重散乱）の順に作り直す。

??? failure "地平線のあたりが、線のように明るくなる"
    µ の割り当てが地平線で連続になっている。地面に当たる向きと空へ抜ける向きで、uµ を不連続にする（u_µ ＜ 0.5 と ≥ 0.5 で分ける）。

??? failure "遠くの山の空気遠近法が、階段状になる"
    µ を線形に写している。µ ではなく上端までの距離を使った uµ に写し替える。

??? failure "テーブルの端で、色が変になる"
    端のテクセルの中心に境界の値を置いていない。`0.5/n + x (1 − 1/n)` の割り当てを使い端で外挿された値を読まないようにする。

??? failure "ν の補間で、継ぎ目が出る"
    3D テクスチャの x に ν と µs を詰めているので、ν の補間は自分で 2 回読んで行う。µs の番号をまたがないように `floor` で分ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 散乱を (r, µ, µs, ν) の 4 次元テーブルに前もって入れ、実行時は引くだけ。
    - [x] 空気遠近法は `S(x) − T(x, p) · S(p)`。上端まで積分した値を 2 回引く。
    - [x] µ は水平線までの距離の比に写し替える。地平線で不連続にする。
    - [x] Mie の 1 次散乱は分けて保存し、位相関数を実行時に掛ける。
    - [x] 大気の組成は固定。動的な天候には向かない。

## 参考

- Eric Bruneton, Fabrice Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum 27(4) (Proc. Eurographics Symposium on Rendering 2008), pp. 1079–1086, 2008. DOI: 10.1111/j.1467-8659.2008.01245.x（全文を読んだ。図は見ていない）
- Eric Bruneton, "Precomputed Atmospheric Scattering: a New Implementation", 2017. <https://ebruneton.github.io/precomputed_atmospheric_scattering/>（紹介と `functions.glsl` の文書の前半を読んだ。後半は読んでいない）
- Eric Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE TVCG 23(12), 2017（読んでいない）
- Sébastien Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (EGSR 2020)（読んでいない）
- Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993（読んでいない。論文の参考文献 [NSTN93]）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Hillaire 2020](hillaire.md)
- [Transmittance](transmittance.md)
- [Single Scattering](single-scattering.md)
- [Multiple Scattering](multiple-scattering.md)
