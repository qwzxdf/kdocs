---
title: Dynamic Updates
tags:
  - 描画
---

# Dynamic Updates

**ベイクしたプローブは、光や物が動くと、古くなります**。**動的に更新するには、プローブごとにレイを飛ばして、再計算します**。**1 フレームに更新する数を絞る**のが**コツ**です。このページでは、**動的更新の考え方**を説明します。

!!! tip "ポイント"
    - **ベイクだけだと、昼夜の変化・動く光に追従できない**。
    - **プローブからレイを飛ばして、再計算**（DDGI など）。
    - **1 フレームに更新するプローブ数を絞る**。
    - **変化が無い所は、更新を省く**。

## 動的な更新
**ベイクしたプローブ**は、**静的な光**に対する**固定**の値です。

| 方式 | 内容 |
| --- | --- |
| **ベイクのみ** | **固定**。**最も安い** |
| **ライトの強さ・色を実行時に掛ける** | **ライトごとにプローブを別々にベイク**し、**実行時に強さ・色で合成**（**複数ライト分のメモリ**） |
| **実行時に再ライティング** | **プローブごとにレイ・キューブマップ**で**毎フレーム更新**（[DDGI](../ddgi.md)・[レイトレ GI](../rt-gi/index.md)） |
| **時間帯の切り替え** | <strong>複数セット（朝・昼・夕）</strong>を、**補間** |


### 更新を絞る

実行時に全プローブを毎フレーム更新すると重すぎるので、**1 フレームに更新する数を絞ります**。数フレームに分けて順番に更新したり、カメラに近いプローブを優先したり、前のフレームから変化が小さいプローブの更新を省いたりします。更新にはレイを使うので、レイの数を一定の予算に収め、足りない分を時間蓄積で補います。ライトが動くと、間接光がワンテンポ遅れて追従するように見えますが、拡散の間接光は低周波で変化がゆっくりなので、数フレームの遅れは目立ちません。

### 更新するもの

動的に更新するのは、プローブの放射照度だけではありません。ジオメトリが動くとき（ドアが開く、壁が壊れる）は、プローブの<strong>可視性（その方向にどれだけ先まで壁がないか）</strong>も更新する必要があります。ここを更新しないと、壊れた壁の向こうの光が通らず、ライト リークの逆の問題（光が通るべき所で遮られる）が起きます。DDGI は、放射照度と距離の両方を毎フレーム更新することで、この問題に対処しています。

### 更新を絞る

実行時に全プローブを毎フレーム更新すると重すぎるので、**1 フレームに更新する数を絞ります**。数フレームに分けて順番に更新したり、カメラに近いプローブを優先したり、前のフレームから変化が小さいプローブの更新を省いたりします。更新にはレイを使うので、レイの数を一定の予算に収め、足りない分を時間蓄積で補います。ライトが動くと、間接光がワンテンポ遅れて追従するように見えますが、拡散の間接光は低周波で変化がゆっくりなので、数フレームの遅れは目立ちません。

### 更新するもの

動的に更新するのは、プローブの放射照度だけではありません。ジオメトリが動くとき（ドアが開く、壁が壊れる）は、プローブの<strong>可視性（その方向にどれだけ先まで壁がないか）</strong>も更新する必要があります。ここを更新しないと、壊れた壁の向こうの光が通らず、ライト リークの逆の問題（光が通るべき所で遮られる）が起きます。DDGI は、放射照度と距離の両方を毎フレーム更新することで、この問題に対処しています。

<!-- fig:probe-roundrobin:begin -->

<svg class="fig illust motion" data-fig="probe-roundrobin" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-probe-roundrobin" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">プローブの更新を絞る: 1 フレームに 4 個だけ、順番に更新</text>
<circle cx="181.0" cy="111.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="181.0" cy="111.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1357;0.1360;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="181.0" cy="111.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1357;0.1360;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="243.0" cy="111.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="243.0" cy="111.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1357;0.1360;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="243.0" cy="111.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1357;0.1360;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="305.0" cy="111.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="305.0" cy="111.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1357;0.1360;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="305.0" cy="111.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1357;0.1360;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="367.0" cy="111.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="367.0" cy="111.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1357;0.1360;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="367.0" cy="111.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1357;0.1360;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="429.0" cy="111.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="429.0" cy="111.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2477;0.2480;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="429.0" cy="111.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;0.2477;0.2480;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="491.0" cy="111.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="491.0" cy="111.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2477;0.2480;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="491.0" cy="111.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;0.2477;0.2480;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="181.0" cy="173.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="181.0" cy="173.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2477;0.2480;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="181.0" cy="173.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;0.2477;0.2480;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="243.0" cy="173.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="243.0" cy="173.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2477;0.2480;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="243.0" cy="173.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;0.2477;0.2480;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="305.0" cy="173.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="305.0" cy="173.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3597;0.3600;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="305.0" cy="173.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.3597;0.3600;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="367.0" cy="173.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="367.0" cy="173.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3597;0.3600;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="367.0" cy="173.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.3597;0.3600;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="429.0" cy="173.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="429.0" cy="173.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3597;0.3600;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="429.0" cy="173.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.3597;0.3600;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="491.0" cy="173.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="491.0" cy="173.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3597;0.3600;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="491.0" cy="173.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.3597;0.3600;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="181.0" cy="235.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="181.0" cy="235.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4717;0.4720;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="181.0" cy="235.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;0.4717;0.4720;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="243.0" cy="235.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="243.0" cy="235.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4717;0.4720;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="243.0" cy="235.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;0.4717;0.4720;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="305.0" cy="235.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="305.0" cy="235.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4717;0.4720;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="305.0" cy="235.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;0.4717;0.4720;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="367.0" cy="235.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="367.0" cy="235.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4717;0.4720;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="367.0" cy="235.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;0.4717;0.4720;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="429.0" cy="235.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="429.0" cy="235.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5837;0.5840;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="429.0" cy="235.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5837;0.5840;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="491.0" cy="235.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="491.0" cy="235.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5837;0.5840;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="491.0" cy="235.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5837;0.5840;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="181.0" cy="297.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="181.0" cy="297.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5837;0.5840;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="181.0" cy="297.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5837;0.5840;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="243.0" cy="297.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="243.0" cy="297.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5837;0.5840;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="243.0" cy="297.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5837;0.5840;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="305.0" cy="297.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="305.0" cy="297.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6957;0.6960;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="305.0" cy="297.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;0.6957;0.6960;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="367.0" cy="297.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="367.0" cy="297.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6957;0.6960;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="367.0" cy="297.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;0.6957;0.6960;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="429.0" cy="297.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="429.0" cy="297.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6957;0.6960;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="429.0" cy="297.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;0.6957;0.6960;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="491.0" cy="297.0" r="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<circle cx="491.0" cy="297.0" r="20" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6957;0.6960;1.0000" values="0;0;0.45;0.45"/></circle>
<circle cx="491.0" cy="297.0" r="24" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;0.6957;0.6960;1.0000" values="0;0;1;1;0;0"/></circle>
<text x="150" y="68" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">6×4 = 24 個のプローブ(橙: このフレームで更新、青: 更新済み)</text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 1: プローブ 1〜4 を更新<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1917;0.1920;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 2: プローブ 5〜8 を更新<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;0.3037;0.3040;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 3: プローブ 9〜12 を更新<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.4157;0.4160;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 4: プローブ 13〜16 を更新<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;0.5277;0.5280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 5: プローブ 17〜20 を更新<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.6397;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 6: プローブ 21〜24 を更新<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;0.7517;0.7520;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:probe-roundrobin:end -->

## よくあるミス

??? failure "光を動かしても、間接光がまったく変わらない"
    **動的更新（またはリアルタイム GI）**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **レイで再計算して、動的に更新**
    - [x] **更新数を絞って、コストを抑える**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Probe GI](index.md)
- [DDGI](../ddgi.md)
- [置き方](placement.md)
