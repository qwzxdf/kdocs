---
title: Volumetric Fog
tags:
  - 描画
---

# Volumetric Fog

<strong>ボリューメトリック フォグは、霧の中を光が通る様子を 3D の体積として計算する手法</strong>です。<strong>光の筋や影の中の霧、ライトの周りの光の玉</strong>が表現できます。このセクションでは通常のフォグとの違い・froxel・手順・密度・光の注入・積分と適用・時間蓄積・品質と速度を、1 つずつ別のページで説明します。

## 何が違うか
フォグ系の方式の違いを整理します。距離フォグはピクセルの距離だけで決まり、光は関係しません。高さフォグは高さと距離で決まり、これも光とは関係しません。ボリューメトリック フォグは、空間の各点で光を計算するので、光の筋・影・光る霧を表現できます。

## 手順
<svg class="fig illust" viewBox="0 0 780 160" role="img" aria-label="ボリューメトリック フォグの手順"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">4 つのパス</text>
<g font-size="12">
<rect x="20" y="56" width="165" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/><text x="102" y="86" text-anchor="middle" style="font-weight:700">① 密度</text><text x="102" y="106" text-anchor="middle" style="font-size:11px">各 froxel の霧の濃さ</text>
<rect x="215" y="56" width="165" height="70" rx="8" fill="#e5aa28" fill-opacity="0.22" stroke="#e5aa28" stroke-width="2"/><text x="297" y="86" text-anchor="middle" style="font-weight:700">② 光の注入</text><text x="297" y="106" text-anchor="middle" style="font-size:11px">光 × 影 × 位相関数</text>
<rect x="410" y="56" width="165" height="70" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6" stroke-width="2"/><text x="492" y="86" text-anchor="middle" style="font-weight:700">③ 積分</text><text x="492" y="106" text-anchor="middle" style="font-size:11px">奥へ足して透過率</text>
<rect x="605" y="56" width="155" height="70" rx="8" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043" stroke-width="2"/><text x="682" y="86" text-anchor="middle" style="font-weight:700">④ 適用</text><text x="682" y="106" text-anchor="middle" style="font-size:11px">画面に合成</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="187" y1="91" x2="213" y2="91" marker-end="url(#rfa)"/><line x1="382" y1="91" x2="408" y2="91" marker-end="url(#rfa)"/><line x1="577" y1="91" x2="603" y2="91" marker-end="url(#rfa)"/></g>
</svg>

## 背景：なぜ froxel なのか

視線に沿って光を積分する処理（レイマーチ）は、画素ごとにシャドウ マップを何十回も引くので、重い処理です。ボリューメトリック フォグが実用になったのは、Wronski の SIGGRAPH 2014 の発表 "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering"（『Assassin's Creed IV』）が、この計算を<strong>画面の解像度に依存しない、低解像度の 3D テクスチャ</strong>に移したからです。

考え方は次のとおりです。フォグは細かい構造をほとんど持たない、低周波の現象です。画素ごとに正確に計算しなくても、視錐台を 160×90×64 のような粗いセルに分けて、セルごとに光の量を計算し画素の位置では補間して取り出せば、見た目に十分です。計算量は画素数（約 200 万）から、セル数（約 90 万）へさらに、各セルで 1 回だけ光を計算すれば済むので、画素ごとのレイマーチより桁違いに少なくなります。

さらに、セルごとに計算するのでライトを複数注入するのが簡単です。ライトの数が増えてもセルごとにライトを足し合わせるだけで、画素ごとのマーチを増やす必要がありません。Hillaire の Frostbite での発表（"Physically Based and Unified Volumetric Rendering in Frostbite"、SIGGRAPH 2015）は、この仕組みを物理的に整えました。散乱係数と吸収係数を分けて持ち、フォグ・パーティクル・ローカルなボリュームをすべて同じ froxel に書き込む、統一された設計です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Froxels](froxel.md) | 視錐台のグリッド |
| [Step 1: Density](density.md) | 霧の濃さを決める |
| [Step 2: Light Injection](injection.md) | 各セルにライトを足す |
| [Steps 3 and 4: Integration and Application](integration.md) | 視線に沿って足し、シーンに合成 |
| [Temporal Accumulation](temporal.md) | ノイズを消す |
| [Quality and Performance](quality.md) | 解像度・スライス数の目安 |

## ボリューム フォグとは

<strong>通常の霧</strong>（[Fog Equations](../aerial-fog/fog-equation.md)）は、<strong>距離だけ</strong>で霧の濃さを決めます。ボリューム フォグは空間の各点の、霧の濃さ・光の当たり方をボリューム（3D グリッド）として、計算します。

| | 通常の霧 | ボリューム フォグ |
| --- | --- | --- |
| 濃さ | 距離と高さだけ | 空間の、各点（局所的な霧の塊） |
| 光の筋（ゴッド レイ） | 出ない | 出る（影の中は、暗い） |
| 局所光の散乱（ランプの周りの、光の玉） | 出ない | 出る |
| 動く霧（ノイズで動く） | 難しい | 簡単（密度を、ノイズで変える） |
| コスト | 最小 | 中（毎フレーム、ボリュームを計算） |

<strong>ライトの周りの光の玉</strong>、<strong>窓から差し込む光の筋</strong>、霧の渦などリアルな大気の表現が、1 つの仕組みで得られます。Wronski（2014）の方式が多くの、ゲームの標準です。

## 4 つの段階

ボリューム フォグは <strong>4 つの段階</strong>で、できています。

| 段階 | 内容 | ページ |
| --- | --- | --- |
| ① 密度 | 各セルの霧の濃さを、決める（一様、高さノイズ、局所のボリューム） | [Step 1: Density](density.md) |
| ② ライトの注入 | 各セルに、ライトの光を散乱光として書き込む（影も、考慮） | [Step 2: Light Injection](injection.md) |
| ③ 積分 | 奥行き方向に、散乱光を累積する（カメラから、各距離までの結果） | [Steps 3 and 4: Integration and Application](integration.md) |
| ④ 適用 | 物体の色に、霧の効果をかける | [Steps 3 and 4: Integration and Application](integration.md) |

## froxel：カメラに、合わせたグリッド

<strong>ボリュームはカメラの視錐台</strong>に、<strong>合わせた 3D グリッド</strong>です（froxel = frustum + voxel）。画面の横・縦と奥行きで分割します。

```text
横（画面）160 × 縦（画面）90 × 奥行き 64   =  約 92 万セル

カメラ ●──→ 奥行き（近いところは、細かく、遠いところは、粗く）
```

| 軸 | 分割数の例 | 意味 |
| --- | --- | --- |
| x | 160 | 画面の横（画素の 1/12 程度） |
| y | 90 | 画面の縦 |
| z | 64 | 奥行き（指数的に分割。近くを細かく） |

詳しくは[Froxels](froxel.md) を、参照してください。

## 毎フレームの流れ

```text
① 密度ボリュームを、書く         （計算シェーダー）
② ライトを、注入する              （計算シェーダー。シャドウ マップを引く）
③ 奥行き方向に、積分する          （計算シェーダー）
④ 物体を描くとき、ボリュームを、引いて、霧を、かける   （ピクセル シェーダー）
```

<strong>毎フレームのコスト</strong>は <strong>約 0.5〜1.5 ms</strong>（解像度、ライトの数による）です。時間方向の平均（[Temporal Accumulation](temporal.md)）で、低い解像度でもなめらかになります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] froxel に光を注入して、積分する

## 参考

- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Sky and Atmosphere](../index.md)
- [Aerial Perspective and Fog](../aerial-fog/index.md)
- [God Rays](../god-rays/index.md)
