---
title: God Rays
tags:
  - 描画
---

# God Rays

**ゴッド レイ（光の筋）は、霧や埃の中を、光が通る時に見える、筋状の光**です。**手法には、画面空間のぼかし・シャドウ マップのレイマーチ・ボリューム・メッシュなど、いくつかあります**。このセクションでは、**見える理由・画面空間の放射ぼかし・シャドウ マップでレイマーチ・ボリューム・メッシュで作る・水中・見た目の調整**を、**1 つずつ別のページ**で説明します。

## 光の筋が見える理由
**光は空気中を通っても何もなければ見えません**。**粒（ほこり・水蒸気）があると光が散らされて、視線の方向に光が飛んできます**。**途中に影を作る物があると、影の部分では光が通らないので、光る部分と暗い部分が筋になります**。

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

光の筋の方式は、品質と軽さ、そして使える条件で選びます。

最も手軽なのは、<strong>画面空間の放射ぼかし</strong>です。ポストプロセスで、太陽の位置から放射状にぼかすだけで、遮蔽物の形が筋になります。軽く、既存のパイプラインに簡単に足せますが、太陽が画面内にあるときにしか使えず、空気の濃さや影の奥行きは表せません。

次が、<strong>シャドウ マップを使ったレイマーチ</strong>です。視線に沿って歩き、各点が日向かをシャドウ マップで判定するので、太陽が画面外でも正確に動作します。ステップ数を増やすと重いので、ジッターと時間蓄積で補います。

すでに<strong>ボリューメトリック フォグ</strong>を使っているなら、それに光の筋は含まれます。froxel に太陽光と影を注入するときに、影の遮蔽が自然に筋として現れるので、追加コストがほぼかかりません。

固定された場所の光（窓から差す光など）なら、<strong>メッシュの光の柱</strong>が最も軽くて、アーティストが形を完全に制御できます。

実際のゲームでは、これらを組み合わせます。たとえば、広い屋外はボリューメトリック フォグ、窓の光はメッシュ、太陽に向かうときの強い光のにじみは放射ぼかし、というように、場面ごとに最も効率のよい方式を使い分けます。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Screen-Space Radial Blur](radial-blur.md) | 最も手軽な方式 |
| [Shadow Map Raymarching](shadowmap-march.md) | 正確な筋 |
| [Volume-Based God Rays](volume.md) | froxel による方式 |
| [Light Shaft Meshes](mesh-shafts.md) | 最も軽い方式 |
| [Underwater God Rays](underwater.md) | 水中での表現 |
| [Tuning the Look](tuning.md) | 強さ・色・ノイズ |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **散乱を、霧の中で可視化したもの**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky and Atmosphere](../index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
- [Underwater Rendering](../../water/underwater/index.md)
