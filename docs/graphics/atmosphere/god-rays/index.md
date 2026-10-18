---
title: God Rays
tags:
  - 描画
---

# God Rays

<strong>ゴッド レイ（光の筋）は霧や埃の中を、光が通る時に見える筋状の光</strong>です。<strong>手法には画面空間のぼかし・シャドウ マップのレイマーチ・ボリューム・メッシュなど、いくつかあります</strong>。このセクションでは見える理由・画面空間の放射ぼかし・シャドウ マップでレイマーチ・ボリューム・メッシュで作る・水中・見た目の調整を、1 つずつ別のページで説明します。

## 光の筋が見える理由
<strong>光は空気中を通っても何もなければ見えません</strong>。<strong>粒（ほこり・水蒸気）があると光が散らされて、視線の方向に光が飛んできます</strong>。途中に影を作る物があると影の部分では光が通らないので、光る部分と暗い部分が筋になります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="光の筋の原理">
<text x="20" y="24" class="fig-title">遮る物があるから、光の部分と暗い部分の「筋」ができる</text>
<circle cx="120" cy="50" r="16" fill="#e5aa28"/><text x="100" y="86" style="font-size:12px">太陽</text>
<g stroke="#e5aa28" stroke-width="2"><line x1="120" y1="66" x2="210" y2="170"/><line x1="130" y1="64" x2="300" y2="170"/><line x1="140" y1="62" x2="400" y2="170"/><line x1="150" y1="60" x2="500" y2="170"/><line x1="160" y1="58" x2="600" y2="170"/></g>
<rect x="190" y="106" width="40" height="40" fill="#555"/><rect x="330" y="96" width="40" height="40" fill="#555"/>
<text x="196" y="130" style="font-size:11px;fill:#fff">遮る物</text>
<g fill="#e5aa28" fill-opacity="0.22"><polygon points="230,146 330,170 280,170 235,155"/><polygon points="370,136 470,170 410,170 370,142"/></g>
<line x1="40" y1="170" x2="740" y2="170" stroke="currentColor" stroke-opacity="0.5" stroke-width="2"/>
<circle cx="680" cy="150" r="6" fill="#e5484d"/><text x="640" y="190" style="font-size:12px">カメラ</text>
<text x="360" y="220" style="font-size:12px">暗い帯：遮られた所（光が通らない）　明るい帯：光が通る所</text>
</svg>

## 方式の選び方

光の筋の方式は品質と軽さそして使える条件で選びます。

最も手軽なのは <strong>画面空間の放射ぼかし</strong>です。ポストプロセスで太陽の位置から放射状にぼかすだけで、遮蔽物の形が筋になります。軽く既存のパイプラインに簡単に足せますが、太陽が画面内にあるときにしか使えず、空気の濃さや影の奥行きは表せません。

次が <strong>シャドウ マップを使ったレイマーチ</strong>です。視線に沿って歩き各点が日向かをシャドウ マップで判定するので、太陽が画面外でも正確に動作します。ステップ数を増やすと重いので、ジッターと時間蓄積で補います。

すでに<strong>ボリューメトリック フォグ</strong>を使っているなら、それに光の筋は含まれます。froxel に太陽光と影を注入するときに、影の遮蔽が自然に筋として現れるので、追加コストがほぼかかりません。

固定された場所の光（窓から差す光など）なら、<strong>メッシュの光の柱</strong>が最も軽くて、アーティストが形を完全に制御できます。

実際のゲームではこれらを組み合わせます。たとえば、広い屋外はボリューメトリック フォグ、窓の光はメッシュ、太陽に向かうときの強い光のにじみは放射ぼかし、というように場面ごとに最も効率のよい方式を使い分けます。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Screen-Space Radial Blur](radial-blur.md) | 最も手軽な方式 |
| [Shadow Map Raymarching](shadowmap-march.md) | 正確な筋 |
| [Volume-Based God Rays](volume.md) | froxel による方式 |
| [Light Shaft Meshes](mesh-shafts.md) | 最も軽い方式 |
| [Underwater God Rays](underwater.md) | 水中での表現 |
| [Tuning the Look](tuning.md) | 強さ・色・ノイズ |

## ゴッド レイとは

<strong>雲の切れ間</strong>、<strong>木々の間</strong>、窓から差し込む光の筋です（光芒、クレパスキュラー レイとも）。空気中の細かい粒子（霧、ほこり水蒸気）が光の通り道を、散乱して見えるようにする現象です。光が遮られた場所（影）は暗く光が通った、場所だけが明るい筋になります。

```text
        太陽
         ╲  ╲  ╲
          ╲  ╲  ╲          ← 光の筋（空気の粒子が、散乱して、光って見える）
    ██████╲  ╲██╲████       ← 遮蔽物（木、建物）の隙間を、光が、通る
          ╲   ╲
       ───────────── 地面
```

<strong>光の筋が見える条件</strong>は <strong>3 つ</strong>です。

| 条件 | 内容 |
| --- | --- |
| 光源が強い | 太陽、強いライト |
| 空気中に粒子（霧、ほこり） | 散乱する媒質が必要。澄んだ空気では筋が見えない |
| 遮蔽物があり光が部分的に遮られる | 光と影の、コントラストが筋を作る |

## 実装方法の一覧

| 方法 | 内容 | 品質 | コスト | ページ |
| --- | --- | --- | --- | --- |
| 放射状ブラー（画面空間） | 太陽の、画面上の位置から放射状に明るい部分を、引き伸ばす | 低〜中 | 小 | [Screen-Space Radial Blur](radial-blur.md) |
| シャドウ マップ レイマーチ | 視線に沿って各点が、光を受けているか（シャドウ マップ）を、積分 | 高 | 中〜大 | [Shadow Map Raymarching](shadowmap-march.md) |
| ボリューム ライティング（froxel） | 空間を、3D グリッドに分割し光の散乱を、格納 | 高（霧と統合） | 中 | [Volume-Based God Rays](volume.md)、[Volumetric Fog](../volumetric-fog/index.md) |
| 光の筋のメッシュ | 半透明の板を、置く | 低〜中（アーティスト制御） | 小 | [Light Shaft Meshes](mesh-shafts.md) |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| まず、出したい軽く | 放射状ブラー（[Screen-Space Radial Blur](radial-blur.md)） |
| 影の正確さが欲しい（木漏れ日） | シャドウ マップ レイマーチ |
| 霧の全体をリアルにしたい | ボリューム フォグ（froxel。光の筋も同時に出る） |
| 特定の場所（窓、洞窟の入口）に演出として | 光の筋の、メッシュ |

近年のゲームでは <strong>ボリューム フォグ</strong>（[Volumetric Fog](../volumetric-fog/index.md)）に、<strong>統合</strong>されることが多く霧と、光の筋が同じ計算で出ます。

## 調整のポイント

| 項目 | 内容 |
| --- | --- |
| 強さ | 強すぎると画面が白く、もやもやする。控えめに |
| 色 | 太陽の色（暖色）。朝夕は橙。青い空の光は筋にならない |
| 方向性 | 太陽の方を見たときに、強く（前方散乱）。太陽に背を向けると弱い（[Tuning the Look](tuning.md)） |
| ちらつき | レイマーチの、ステップ数が少ないと縞が出る。ノイズ + TAA でならす（[Cloud Temporal Reprojection](../clouds/temporal.md)） |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 散乱を霧の中で可視化したもの

## 参考

- Mitchell, "Volumetric Light Scattering as a Post-Process", GPU Gems 3, Chapter 13, 2007（放射状ブラーによる、光の筋）
- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Sky and Atmosphere](../index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
- [Underwater Rendering](../../water/underwater/index.md)
