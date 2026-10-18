---
title: Reflection Probes
tags:
  - 描画
---

# Reflection Probes

<strong>反射プローブは、ある地点から周囲を撮影して、キューブマップとして保存しておき、反射に使う手法</strong>です。<strong>画面の外の物も映せ、とても安い</strong>のが利点ですが、撮影した場所と、反射を見る場所がずれる（視差）ので、補正が必要です。このセクションでは、発想・事前フィルタ（粗さ）・視差補正・複数プローブのブレンド・SSR との併用を、1 つずつ別のページで説明します。

## 発想
反射は、「<strong>反射方向 R に何が見えるか</strong>」です。<strong>R 方向の景色</strong>をシーンから、その場で求めるのは大変です（レイトレ・SSR）。空間の 1 点（プローブの位置）から見た景色をあらかじめ写真に撮っておけば、R 方向のピクセルを読むだけで済みます。

プローブの使い方は単純です。プローブの位置から 6 方向（上下左右前後）を描いて、キューブマップに保存します（撮影）。表面の反射方向 R で、そのキューブマップを引きます（`cube.Sample(sampler, R)`）。粗い面では、粗さに応じてぼかしたミップを引きます（次の節）。

## キューブマップの作成
| 手順 | 内容 |
| --- | --- |
| ① 位置を決める | 部屋の中央、広場の中央など。反射が映る面の近く |
| ② 6 面を描く | 90 度の視野角で+X, −X, +Y, −Y, +Z, −Z の 6 方向を、HDR で描く |
| <strong>③ ミップを作る（事前フィルタ）</strong> | 粗さごとに反射のぼけを事前計算 |
| ④ 保存 | ベイク（事前）または実行時に更新 |

保存は<strong>HDR（浮動小数点）</strong>でなければなりません。太陽や光源の明るさが、反射のハイライトに効くためです。8 ビットの LDR で保存すると、ハイライトが白飛びして、金属の鋭い反射が出ません。

保存は<strong>HDR（浮動小数点）</strong>でなければなりません。太陽や光源の明るさが、反射のハイライトに効くためです。8 ビットの LDR で保存すると、ハイライトが白飛びして、金属の鋭い反射が出ません。

<strong>HDR（浮動小数点）</strong>で保存します。<strong>太陽や光源の明るさ</strong>が<strong>反射のハイライト</strong>に効くためです。

### プローブの考え方と限界

プローブの本質は、<strong>「1 点から見た景色を、全方向の写真として固定する」</strong>ことです。これは、その点にいる観察者にとっては正確ですが、プローブの位置から離れた表面にとっては、近似にすぎません。たとえば、部屋の中央に置いたプローブで、壁際の床の反射を引くと、本来は壁際から見える景色であるべきところが、部屋の中央から見える景色になります。この位置のずれ（視差）の補正が、[Parallax Correction](parallax.md) の主題です。

もう 1 つの限界は、<strong>静的</strong>なことです。撮影時に存在した物だけが映り、後から動く物、変化する光は映りません。動的に再撮影すると重いので、プローブは「変化しない背景の反射」を担当し、動く物は SSR で補うのが一般的です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Prefiltering (Split-Sum)](prefilter.md) | 粗さごとに、ぼかしたキューブマップを用意 |
| [Parallax Correction](parallax.md) | 撮影位置と見る位置のずれを直す |
| [Probe Operation](blending.md) | ブレンド・ベイクと更新・スカイボックス |
| [Combining with SSR](combine-ssr.md) | 使い分けと長所短所 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] プローブは、安くて、画面外も映せる
    - [x] 粗さは事前フィルタ、ずれは視差補正

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflections](../index.md)
- [SSR Basics](../ssr-basics/index.md)
- [SSR Fallback and Compositing](../ssr-fallback.md)
