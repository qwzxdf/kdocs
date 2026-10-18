---
title: Approximating the Integral
tags:
  - 描画
---

# Approximating the Integral

<strong>AO の積分は、厳密には計算できない</strong>ので、<strong>近似</strong>します。近似のやり方は、大きく 3 つあり、これが、SSAO・HBAO・Alchemy・GTAO などの方式の違いを生みます。このページでは、3 つの近似・方式を分けるものを説明します。

!!! tip "ポイント"
    - ① サンプルする：半球にサンプルを撒き、遮られた割合（SSAO）。
    - ② 水平線を探す：方向ごとに、地平線の高さを探して積分（HBAO・GTAO）。
    - ③ 解析的に近似：式を直接評価（Alchemy・SAO）。
    - 方式を分けるもの：入力（深度・法線）・サンプルの方法・重み付け・コスト。

!!! info "ここで使われる「積分」を、やさしく言うと"
    AO の積分は、<strong>「全方向の、見えている度合いを、重みつきで足して、平均する」</strong>ことです。方向は無限にあるので、<strong>刻んで</strong>足します。

    - 3 つの近似は、<strong>刻み方の違い</strong>です。方向を、<strong>くじ引きで選ぶ</strong>（①）、<strong>仰角で、断面ごとに、一気に足す</strong>（②）、<strong>点ごとの式を足す</strong>（③）。
    - 重みは、<strong>真上ほど大きい</strong>（コサイン重み）。真上から来る光が、面を、最も強く照らすため。

    <strong>数式を使わない、くわしい説明</strong>は [Integrals and Elevation Angles in Plain Words](integral-intuition.md) です。

## 積分を近似する 3 つのやり方
AO は<strong>積分</strong>なのでそのままでは計算できません。次の 3 通りの近似があります。

| 近似 | 考え方 | 代表的な方式 |
| --- | --- | --- |
| ① モンテカルロ法 | 半球から方向（またはサンプル点）をランダムに N 個選び、遮られているかを数えて割合を出す | Crytek SSAO・半球 SSAO・レイトレ AO |
| ② 地平線（ホライゾン）の積分 | 方向を決めて、その方向で<strong>遮蔽が始まる角度（地平線）</strong>を探し、間の角度を解析的に積分 | HBAO・HBAO+・GTAO |
| ③ 式の近似 | 遮蔽物の表面の点ごとに、影響を表す簡単な式を足し合わせる | Alchemy・SAO |

### ① モンテカルロ法

`AO = (1/π) ∫ V (n·ω) dω` を<strong>コサイン重みの分布</strong>（pdf = cosθ / π）で方向をサンプルすると、`(n·ω)` が<strong>打ち消され</strong>、次のようになります。

<div class="formula">AO ≈ (1 / N) · Σ V(ω_i)　（ω_i はコサイン分布のサンプル）</div>

つまり、<strong>コサイン分布で半球から方向を選び、遮られていない割合を数える</strong>だけです。N が大きいほど正確で、<strong>誤差は 1/√N で減ります</strong>。

<strong>サンプル数 N が少ない</strong>と、結果が<strong>ノイズ</strong>だらけになります。リアルタイムでは N が 8〜16 程度なので、ノイズをぼかしや時間蓄積で消すのが前提です（[フィルタ](../filtering/index.md)）。

### ② 地平線の積分

<strong>サンプルを点でなく、方向の線（スライス）にして、解析的に積分</strong>します。半球を<strong>スライスに分け</strong>、各スライスで<strong>「遮蔽が始まる地平線の角度」</strong>を見つければ、スライス内の積分は、角度の関数として、閉じた式で求まります。サンプル数を減らして精度を保てる、というのが利点です（[HBAO](../hbao.md)・[GTAO](../gtao.md)）。

### ③ 式の近似

遮蔽物の表面の各点 q が、点 p を<strong>どれだけ遮るか</strong>を、<strong>p から q へのベクトル</strong>だけで書く、簡単な式に置き換えます。サンプル点ごとにその式を足すだけで AO が出ます（[Alchemy](../alchemy-ao.md)・[SAO](../sao.md)）。

## 方式を分けるもの

3 つの近似は出発点の違いですが、同じ近似を使う方式の間でも、細部の設計で性格が大きく変わります。方式を比べるときは、次の観点で見ると整理できます。

1. <strong>コサイン重みの扱い</strong>。AO の本来の式には、表面の法線と方向のなす角のコサインが掛かります。GTAO はこれを積分の中で正確に扱います。HBAO は立体角の割合として近似的に扱い、Alchemy は式の中に取り込んでいます。ここが違うと、平らな面と隅の暗さの比がずれます。
2. <strong>必要な入力</strong>。深度だけで計算できる方式（Crytek SSAO・SAO の一部）は G-Buffer が不要で導入が楽です。深度と法線を使う方式（半球 SSAO・Alchemy・HBAO・GTAO）は、半球を使えるので平らな面の誤判定を避けられます。
3. <strong>サンプルの配置</strong>。球・半球・螺旋・方向ごとのステップなど。配置によって、取りこぼしやすい形（細い隙間、薄い物）が変わります。
4. <strong>メモリ アクセスの工夫</strong>。深度のミップで遠いサンプルを速くする（SAO）、画面を分けて読む順を整理してキャッシュを効かせる（HBAO+ のデインターリーブ）など。式は同じでも、速さがまるで違ってきます。
5. <strong>後処理</strong>。ぼかし・時間蓄積・アップサンプルをどう組み合わせるか。実際の画質は、AO の式そのものよりも、こちらで決まる部分が大きいです（[AO Filtering](../filtering/index.md)）。

したがって、方式を「名前の新しさ」で選ぶのでなく、<strong>自分のゲームの制約（G-Buffer があるか、解像度、予算、必要な正確さ）に合う近似はどれか</strong>で選ぶのが正解です（[AO Comparison](../comparison.md)）。

## 3 つの近似を、コードで比べる

### ① サンプルを撒く：コサイン分布の半球サンプリング

```hlsl
// コサイン重みの分布で、半球の方向を 1 つ選ぶ（ローカル座標。z が法線）。pdf = cosθ / π。
float3 CosineSampleHemisphere(float2 u) {
  float r = sqrt(u.x);
  float phi = 2.0 * 3.14159265 * u.y;
  return float3(r * cos(phi), r * sin(phi), sqrt(max(0.0, 1.0 - u.x)));
}
```

円盤の上に一様に点を取り、それを半球に持ち上げると、`cosθ` に比例した密度になります。AO の式の `(n·ω)` と、モンテカルロ法の `1/pdf` が打ち消し合い、残るのは可視性 V の平均だけです。

```hlsl
// 可視性を数えて、割合にする。Visible() は、方向ごとの遮蔽判定（レイ、または、深度の比較）。
float ao = 0.0;
for (uint i = 0; i < kSamples; ++i) {
  float3 w = TangentToWorld(CosineSampleHemisphere(Hammersley(i, kSamples)), normal);
  ao += Visible(position, w) ? 1.0 : 0.0;
}
ao /= kSamples;
```

これが、Crytek 系や半球 SSAO の、骨格です。サンプル数が少ないぶん、ノイズになります。

### ② 水平線を探す：スライスごとに解析的に積分する

```hlsl
// 1 本のスライスで、左右の水平線の角度 h1, h2（法線から測る）が分かれば、可視な弧の積分は式で出る（GTAO）。
float IntegrateArcCosWeighted(float h1, float h2, float n) {
  float cos_n = cos(n);
  float sin_n = sin(n);
  return 0.25 * (-cos(2.0 * h1 - n) + cos_n + 2.0 * h1 * sin_n
               + -cos(2.0 * h2 - n) + cos_n + 2.0 * h2 * sin_n);
}
```

水平線の角度を 2 つ探すだけで、そのスライスの可視度が、サンプルを撒かずに、閉じた式で得られます。サンプル点の数は、水平線を探す歩数だけで済みます（[GTAO](../gtao.md)）。

### ③ 式で近似する：遮蔽物の点ごとに寄与を足す

```hlsl
// Alchemy 型: 周りの点 q が p を遮る量を、ベクトル v = q - p だけで書き、足し合わせる。
float3 v = q - p;
float vv = dot(v, v);
float vn = dot(v, n);
occlusion += max(0.0, vn + p_depth * kBeta) / (vv + kEpsilon);
```

法線の向きにある点ほど（`vn` が大きい）、近い点ほど（`vv` が小さい）強く遮る、という形です。方向を探さないので軽く、ただし、物理的な厳密さは、水平線の方式に劣ります。

## よくあるミス

??? failure "方式を、名前だけで選んで、特徴を知らない"
    <strong>近似のやり方・入力・コスト</strong>で<strong>選ぶ</strong>（[方式の比較](../comparison.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 近似は 3 つ：サンプル・水平線・解析
    - [x] 方式の違いは、近似の仕方の違い

## 参考

- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks
- McGuire, Osman, Bukowski, Hennessy, "The Alchemy Screen-Space Ambient Obscurance Algorithm", High-Performance Graphics 2011
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice

## 関連ページ

- [AO Theory](index.md)
- [Hemisphere SSAO](../ssao-hemisphere.md)
- [GTAO](../gtao.md)
