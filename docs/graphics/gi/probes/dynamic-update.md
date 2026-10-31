---
title: Dynamic Updates
tags:
  - 描画
---

# Dynamic Updates

<strong>ベイクしたプローブは光や物が動くと、古くなります</strong>。動的に更新するにはプローブごとにレイを飛ばして、再計算します。1 フレームに更新する数を絞るのがコツです。このページでは動的更新の考え方を説明します。

!!! tip "ポイント"
    - ベイクだけだと昼夜の変化・動く光に追従できない。
    - プローブからレイを飛ばして、再計算（DDGI など）。
    - 1 フレームに更新するプローブ数を絞る。
    - 変化が無い所は更新を省く。

!!! info "このページを読む前に"
    - [Probe GI](index.md)（このセクション全体の地図と、読む順番）

## 動的な更新
<strong>ベイクしたプローブ</strong>は 静的な光に対する固定の値です。

| 方式 | 内容 |
| --- | --- |
| ベイクのみ | 固定。最も安い |
| ライトの強さ・色を実行時に掛ける | ライトごとにプローブを別々にベイクし、実行時に強さ・色で合成（複数ライト分のメモリ） |
| 実行時に再ライティング | プローブごとにレイ・キューブマップで毎フレーム更新（[DDGI](../ddgi.md)・[Ray-Traced GI](../rt-gi/index.md)） |
| 時間帯の切り替え | 複数セット（朝・昼・夕）を補間 |


### 更新を絞る

実行時に全プローブを毎フレーム更新すると重すぎるので、1 フレームに更新する数を絞ります。数フレームに分けて順番に更新したり、カメラに近いプローブを優先したり、前のフレームから変化が小さいプローブの更新を省いたりします。更新にはレイを使うのでレイの数を一定の予算に収め、足りない分を時間蓄積で補います。ライトが動くと間接光がワンテンポ遅れて追従するように見えますが、拡散の間接光は低周波で変化がゆっくりなので、数フレームの遅れは目立ちません。

### 更新するもの

動的に更新するのはプローブの放射照度だけではありません。ジオメトリが動くとき（ドアが開く、壁が壊れる）はプローブの可視性（その方向にどれだけ先まで壁がないか）も更新します。ここを更新しないと壊れた壁の向こうの光が通らず、ライト リークの逆の問題（光が通るべき所で遮られる）が起きます。DDGI は放射照度と距離の両方を毎フレーム更新することで、この問題に対処しています。

### 更新を絞る

実行時に全プローブを毎フレーム更新すると重すぎるので、1 フレームに更新する数を絞ります。数フレームに分けて順番に更新したり、カメラに近いプローブを優先したり、前のフレームから変化が小さいプローブの更新を省いたりします。更新にはレイを使うのでレイの数を一定の予算に収め、足りない分を時間蓄積で補います。ライトが動くと間接光がワンテンポ遅れて追従するように見えますが、拡散の間接光は低周波で変化がゆっくりなので、数フレームの遅れは目立ちません。

### 更新するもの

動的に更新するのはプローブの放射照度だけではありません。ジオメトリが動くとき（ドアが開く、壁が壊れる）はプローブの可視性（その方向にどれだけ先まで壁がないか）も更新します。ここを更新しないと壊れた壁の向こうの光が通らず、ライト リークの逆の問題（光が通るべき所で遮られる）が起きます。DDGI は放射照度と距離の両方を毎フレーム更新することで、この問題に対処しています。

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

## 光が変わったらプローブも、更新する

<strong>ベイクしたプローブ</strong>は 光が固定です。昼夜が変わるライトが動く・点滅する扉が開いて光が差し込む場面ではプローブの値が現実と、ずれます。実行時にプローブを更新します。

## 更新の方法

| 方法 | 内容 | 品質 | コスト |
| --- | --- | --- | --- |
| ベイクを時間帯ごとに複数用意して、補間 | 朝・昼・夕・夜の 4 セットをベイクし時間で補間 | 良い（静的な、形状のみ） | 最小（補間だけ） |
| 環境光だけ動的に更新（空の SH） | 空の光（太陽、空の色）を SH に投影してプローブの、環境光の成分として足す | 中（ライトの反射は、固定） | 小 |
| キューブマップをプローブごとに、描き直す | 各プローブの位置で、全方向をレンダリングし SH に、投影 | 高 | 重い |
| レイトレーシング（DDGI） | 毎フレーム、レイを飛ばして更新 | 高 | 中（GPU RT が、必要） |

## 方法 1：時間帯ごとの、ベイクを補間

<strong>時間帯ごとにプローブをベイク</strong>して、時刻に応じて補間します。計算は事前で実行時は 2 つのセットの、補間だけです。

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
// 2 つのベイク セットの SH を読んで、補間する。
float3 sh_a[9], sh_b[9], sh[9];
LoadSH(g_probe_set_a, uvw, sh_a);
LoadSH(g_probe_set_b, uvw, sh_b);
for (int i = 0; i < 9; ++i) sh[i] = lerp(sh_a[i], sh_b[i], g_time_blend);
```

SH 係数は線形なので 2 セットの係数を補間するだけで中間の時刻の光がそのまま得られます。簡単で安いですがベイクしたときの、形状（建物、壁）に固定です。扉が開く物が壊れる場面は反映できません。

## 方法 2：空の光を動的に足す

<strong>屋外の光</strong>の大部分は 空（太陽、空の色）です。空の光を SH に投影してプローブの、環境光に足します。プローブ自身はベイク（建物の遮蔽は、焼き込み）、空の光の強さだけを動的に変えます。

```text
プローブの SH = ベイクした、「空に対する、可視性」の SH × 動的な、空の光の SH
```

ベイクのときに 「そのプローブから空がどれだけ見えるか」（空の可視性、方向ごと）を SH に保存します。実行時、空の色（時間帯で変わる）の SH と、掛け合わせ（SH の積）、プローブの環境光を更新します。

SH の積（2 つの SH を掛けた結果の SH）は計算がやや複雑（3 つの SH の結合係数が必要）ですが L1〜L2 なら、軽いです。

簡易版は 可視性を「上を向いた法線の、重み」の 1 つのスカラーにして、空の SH の L0（平均色）に掛ける方法です。

```hlsl
// 簡易版: ベイクした「空の可視性」（0〜1）× 動的な、空の環境光の色。
float3 sky_ambient = IrradianceFromSH9(g_sky_sh, normal);                    // 空の放射照度（毎フレーム更新）
float3 indirect_sky = albedo / 3.14159265 * sky_ambient * probe_sky_visibility;   // 可視性（ベイク）を掛ける
float3 indirect_baked = albedo / 3.14159265 * IrradianceFromSH9(probe_sh, normal);// 他の、光（ランプ、反射）は、ベイクのまま
float3 indirect = indirect_sky + indirect_baked;
```

空の光（昼夜で大きく変わる）と、その他の光（ランプ、反射、静的）を分けて空だけを動的にします。昼夜の変化がほぼこれでまかなえます（ほとんどの屋外の、ゲーム）。

## 方法 3：プローブごとに、描き直す

<strong>各プローブの位置</strong>に カメラを置いて、全方向（キューブマップ）をレンダリングし、SH に投影します。動的なライト、動く物の遮蔽も含めて正確です。

```text
プローブ 1 つの更新:
  ① キューブマップ（32×32 × 6 面）を、レンダリング（簡易なシーン）
  ② キューブマップを、SH（L2）に、投影（[Spherical Harmonics (SH)]）
  ③ 結果を、3D テクスチャに、書き込む
```

1 つのプローブの更新がシーンを 6 回、描くので重いです。1 フレームに数個だけ更新し、全プローブを数十フレームで一巡させます。

| 工夫 | 内容 |
| --- | --- |
| ラウンド ロビン | 1 フレームに N 個（4〜16 個）だけ更新。全体は数秒で一巡（[Probe Round-Robin の図]） |
| カメラの近くを優先 | カメラに近い、プローブを頻繁に遠いプローブは、まれに |
| 変化したプローブだけ | ライトが動いた周りの、プローブだけ更新 |
| 低解像度（キューブマップ 16×16） | 環境光は、なめらかなので小さい解像度で、十分 |

## 方法 4：DDGI

<strong>レイトレーシング</strong>で プローブごとに、数百本のレイを毎フレーム、飛ばし前のフレームの結果と混ぜて、更新します（[DDGI](../ddgi.md)）。動的なライト、動く物、扉の開閉がすべて反映されます。GPU のレイトレーシングが必要です。

## 更新の頻度と遅れ

| 方法 | 光の変化への追従 |
| --- | --- |
| 時間帯の補間 | 即座（補間だけ） |
| 空の SH を更新 | 即座（毎フレーム、SH を計算） |
| ラウンド ロビンで再計算 | 遅れる（数秒で、一巡）。光が急に変わる（フラッシュ、扉が開く）と反映が遅い |
| DDGI | 数フレームでほぼ、追従（履歴との混ぜ具合による） |

<strong>光が遅れて反映される</strong>のが、目立つ場合（扉を開けた瞬間）は、急な変化のときに周りのプローブを優先して更新する特別な扱いを入れます。

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
