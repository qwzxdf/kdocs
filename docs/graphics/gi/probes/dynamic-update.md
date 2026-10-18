---
title: Dynamic Updates
tags:
  - 描画
---

# Dynamic Updates

<strong>ベイクしたプローブは、光や物が動くと、古くなります</strong>。<strong>動的に更新するには、プローブごとにレイを飛ばして、再計算します</strong>。1 フレームに更新する数を絞るのがコツです。このページでは、動的更新の考え方を説明します。

!!! tip "ポイント"
    - ベイクだけだと、昼夜の変化・動く光に追従できない。
    - プローブからレイを飛ばして、再計算（DDGI など）。
    - 1 フレームに更新するプローブ数を絞る。
    - 変化が無い所は、更新を省く。

## 動的な更新
<strong>ベイクしたプローブ</strong>は、<strong>静的な光</strong>に対する固定の値です。

| 方式 | 内容 |
| --- | --- |
| ベイクのみ | 固定。最も安い |
| ライトの強さ・色を実行時に掛ける | ライトごとにプローブを別々にベイクし、実行時に強さ・色で合成（複数ライト分のメモリ） |
| 実行時に再ライティング | プローブごとにレイ・キューブマップで毎フレーム更新（[DDGI](../ddgi.md)・[Ray-Traced GI](../rt-gi/index.md)） |
| 時間帯の切り替え | <strong>複数セット（朝・昼・夕）</strong>を、補間 |


### 更新を絞る

実行時に全プローブを毎フレーム更新すると重すぎるので、<strong>1 フレームに更新する数を絞ります</strong>。数フレームに分けて順番に更新したり、カメラに近いプローブを優先したり、前のフレームから変化が小さいプローブの更新を省いたりします。更新にはレイを使うので、レイの数を一定の予算に収め、足りない分を時間蓄積で補います。ライトが動くと、間接光がワンテンポ遅れて追従するように見えますが、拡散の間接光は低周波で変化がゆっくりなので、数フレームの遅れは目立ちません。

### 更新するもの

動的に更新するのは、プローブの放射照度だけではありません。ジオメトリが動くとき（ドアが開く、壁が壊れる）は、プローブの<strong>可視性（その方向にどれだけ先まで壁がないか）</strong>も更新する必要があります。ここを更新しないと、壊れた壁の向こうの光が通らず、ライト リークの逆の問題（光が通るべき所で遮られる）が起きます。DDGI は、放射照度と距離の両方を毎フレーム更新することで、この問題に対処しています。

### 更新を絞る

実行時に全プローブを毎フレーム更新すると重すぎるので、<strong>1 フレームに更新する数を絞ります</strong>。数フレームに分けて順番に更新したり、カメラに近いプローブを優先したり、前のフレームから変化が小さいプローブの更新を省いたりします。更新にはレイを使うので、レイの数を一定の予算に収め、足りない分を時間蓄積で補います。ライトが動くと、間接光がワンテンポ遅れて追従するように見えますが、拡散の間接光は低周波で変化がゆっくりなので、数フレームの遅れは目立ちません。

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

## 光が、変わったら、プローブも、更新する

<strong>ベイクした、プローブ</strong>は、<strong>光が、固定</strong>です。昼夜が、変わる、ライトが、動く・点滅する、扉が、開いて、光が、差し込む場面では、プローブの値が、現実と、ずれます。実行時に、プローブを、更新する必要が、あります。

## 更新の、方法

| 方法 | 内容 | 品質 | コスト |
| --- | --- | --- | --- |
| ベイクを、時間帯ごとに、複数用意して、補間 | 朝・昼・夕・夜の、4 セットを、ベイクし、時間で、補間 | 良い（静的な、形状のみ） | 最小（補間だけ） |
| 環境光だけ、動的に、更新（空の SH） | 空の光（太陽、空の色）を、SH に、投影して、プローブの、環境光の、成分として、足す | 中（ライトの、反射は、固定） | 小 |
| キューブマップを、プローブごとに、描き直す | 各プローブの位置で、全方向を、レンダリングし、SH に、投影 | 高 | 重い |
| レイトレーシング（DDGI） | 毎フレーム、レイを、飛ばして、更新 | 高 | 中（GPU RT が、必要） |

## 方法 1：時間帯ごとの、ベイクを、補間

<strong>時間帯ごとに、プローブを、ベイク</strong>して、<strong>時刻に応じて、補間</strong>します。計算は、事前で、実行時は、2 つのセットの、補間だけです。

```cpp
// 時刻から、2 つの、ベイク セットと、補間係数を決める。
struct TimeOfDaySets { int set_a, set_b; float t; };
TimeOfDaySets Select(float hour) {
  // 例: 6 時, 12 時, 18 時, 24 時の、4 セット。
  const float kHours[4] = {6, 12, 18, 24};
  for (int i = 0; i < 4; ++i) {
    const float next = kHours[(i + 1) % 4] + ((i + 1) == 4 ? 24 : 0);
    if (hour < kHours[i + 1 > 3 ? 3 : i + 1]) return {i, (i + 1) % 4, (hour - kHours[i]) / (kHours[i + 1] - kHours[i])};
  }
  return {3, 0, 0.0f};
}
```

```hlsl
// 2 つのベイク セットの SH を、読んで、補間する。
float3 sh_a[9], sh_b[9], sh[9];
LoadSH(g_probe_set_a, uvw, sh_a);
LoadSH(g_probe_set_b, uvw, sh_b);
for (int i = 0; i < 9; ++i) sh[i] = lerp(sh_a[i], sh_b[i], g_time_blend);
```

<strong>SH 係数は、線形</strong>なので、<strong>2 セットの、係数を、補間</strong>するだけで、中間の時刻の光が、そのまま得られます。簡単で、安いですが、ベイクしたときの、形状（建物、壁）に、固定です。扉が、開く、物が、壊れる場面は、反映できません。

## 方法 2：空の光を、動的に、足す

<strong>屋外の、光</strong>の、大部分は、<strong>空</strong>（太陽、空の色）です。空の光を、SH に、投影して、プローブの、環境光に、足します。プローブ自身は、ベイク（建物の、遮蔽は、焼き込み）、空の光の、強さだけを、動的に、変えます。

```text
プローブの SH = ベイクした、「空に対する、可視性」の SH × 動的な、空の光の SH
```

<strong>ベイク</strong>の、ときに、<strong>「そのプローブから、空が、どれだけ見えるか」</strong>（空の、可視性、方向ごと）を、SH に、保存します。実行時、空の色（時間帯で、変わる）の SH と、掛け合わせ（SH の積）、プローブの、環境光を、更新します。

<strong>SH の、積</strong>（2 つの SH を、<strong>掛けた</strong>結果の SH）は、計算が、やや複雑（3 つの、SH の、結合係数が、必要）ですが、L1〜L2 なら、軽いです。

<strong>簡易版</strong>は、<strong>可視性を、「上を、向いた、法線の、重み」の、1 つの、スカラー</strong>にして、空の SH の、L0（平均色）に、掛ける方法です。

```hlsl
// 簡易版: ベイクした「空の可視性」（0〜1）× 動的な、空の環境光の色。
float3 sky_ambient = IrradianceFromSH9(g_sky_sh, normal);                    // 空の放射照度（毎フレーム更新）
float3 indirect_sky = albedo / 3.14159265 * sky_ambient * probe_sky_visibility;   // 可視性（ベイク）を、掛ける
float3 indirect_baked = albedo / 3.14159265 * IrradianceFromSH9(probe_sh, normal);// 他の、光（ランプ、反射）は、ベイクのまま
float3 indirect = indirect_sky + indirect_baked;
```

<strong>空の光</strong>（昼夜で、大きく変わる）と、<strong>その他の光</strong>（ランプ、反射、静的）を、分けて、空だけを、動的にします。昼夜の、変化が、ほぼ、これで、まかなえます（ほとんどの、屋外の、ゲーム）。

## 方法 3：プローブごとに、描き直す

<strong>各プローブの位置</strong>に、<strong>カメラを、置いて</strong>、全方向（キューブマップ）を、レンダリングし、SH に、投影します。動的な、ライト、動く物の、遮蔽も、含めて、正確です。

```text
プローブ 1 つの更新:
  ① キューブマップ（32×32 × 6 面）を、レンダリング（簡易なシーン）
  ② キューブマップを、SH（L2）に、投影（[Spherical Harmonics (SH)]）
  ③ 結果を、3D テクスチャに、書き込む
```

<strong>1 つのプローブの、更新</strong>が、<strong>シーンを、6 回、描く</strong>ので、重いです。1 フレームに、数個だけ更新し、全プローブを、数十フレームで、一巡させます。

| 工夫 | 内容 |
| --- | --- |
| ラウンド ロビン | 1 フレームに、N 個（4〜16 個）だけ更新。全体は、数秒で、一巡（[Probe Round-Robin の図]） |
| カメラの近くを、優先 | カメラに、近い、プローブを、頻繁に、遠いプローブは、まれに |
| 変化した、プローブだけ | ライトが、動いた、周りの、プローブだけ、更新 |
| 低解像度（キューブマップ 16×16） | 環境光は、なめらかなので、小さい解像度で、十分 |

## 方法 4：DDGI

<strong>レイトレーシング</strong>で、<strong>プローブごとに、数百本の、レイ</strong>を、毎フレーム、飛ばし、前のフレームの、結果と、混ぜて、更新します（[DDGI](../ddgi.md)）。動的な、ライト、動く物、扉の、開閉が、すべて、反映されます。GPU の、レイトレーシングが、必要です。

## 更新の、頻度と、遅れ

| 方法 | 光の変化への、追従 |
| --- | --- |
| 時間帯の、補間 | 即座（補間だけ） |
| 空の SH を、更新 | 即座（毎フレーム、SH を、計算） |
| ラウンド ロビンで、再計算 | 遅れる（数秒で、一巡）。光が、急に変わる（フラッシュ、扉が、開く）と、反映が、遅い |
| DDGI | 数フレームで、ほぼ、追従（履歴との、混ぜ具合による） |

<strong>光が、遅れて、反映される</strong>のが、<strong>目立つ</strong>場合（扉を、開けた、瞬間）は、急な変化のときに、周りの、プローブを、優先して、更新する、特別な、扱いを、入れます。

## よくあるミス

??? failure "光を動かしても、間接光がまったく変わらない"
    <strong>動的更新（またはリアルタイム GI）</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レイで再計算して、動的に更新
    - [x] 更新数を絞って、コストを抑える

## 参考

- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019
- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001
- Iwanicki, "Lighting Technology of The Last of Us", SIGGRAPH 2013, Advances in Real-Time Rendering in Games（アンビエント ダイスなど）
- Sloan, Kautz, Snyder, "Precomputed Radiance Transfer for Real-Time Rendering in Dynamic, Low-Frequency Lighting Environments", ACM Transactions on Graphics (SIGGRAPH 2002)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、ライトマップ、プローブの章）

## 関連ページ

- [Probe GI](index.md)
- [DDGI](../ddgi.md)
- [Probe Placement](placement.md)
