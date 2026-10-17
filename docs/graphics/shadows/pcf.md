---
title: PCF
tags:
  - 描画
---

# PCF

シャドウ マップの比較は、<strong>「影か、日向か」の 0 か 1</strong>です。これを 1 点だけで行うと、<strong>影の縁がギザギザ（エイリアシング）</strong>になります。**PCF**（Percentage Closer Filtering）は、**周りの複数のテクセルで比較して、「日向の割合」を平均**し、**縁を滑らかにする**方法です。**深度を平均してから比べるのでなく、比べた結果を平均する**ことが、重要な点です（深度は補間できません）。このページでは、**PCF の原理・カーネルの種類・サンプルの配置・コスト**を説明します。

!!! tip "ポイント"
    - PCF ＝ <strong>周りの N 点それぞれで「影か」を比べ、その平均（日向の割合）を取る</strong>。
    - <strong>深度を先に平均してはいけない</strong>（影の境で嘘の深度ができる）。<strong>比較してから平均</strong>。
    - <strong>ハードウェア PCF</strong>：<strong>比較サンプラーのバイリニア</strong>が、2×2 の PCF を 1 回で行う。
    - 広くぼかすなら<strong>複数回サンプル</strong>：<strong>格子（N×N）・ポワソン円盤・回転</strong>。
    - <strong>カーネルが大きいほどソフト</strong>だが、<strong>遮蔽物との距離に関係なく一定</strong>のぼけ（現実の影と違う）。
    - カーネルが大きいと、<strong>バイアスの扱い</strong>が難しい（[受け手平面バイアス](bias/index.md)）。

## なぜ、比べてから平均するのか

シャドウ マップの値は**深度**です。**深度を平均**してから比べると、**境界でどちらにも存在しない深度**ができ、**誤った結果**になります（[SAO のミップ](../ao/sao.md)と同じ理由）。

| 方法 | 結果 |
| --- | --- |
| **深度を平均 → 比べる** | **誤り**（影の縁で嘘の深度） |
| **比べる → 結果を平均** | **正しい**（各点の「影か」の割合） |

つまり、**PCF の「比較」は、フィルタの前**に行います。普通のテクスチャ フィルタ（バイリニア・ミップ）は、**比較より前に値を補間**するので、**そのままでは使えません**。専用の**比較サンプラー**が、この順序を実現します。

## ハードウェア PCF（2×2）

**比較サンプラー**（`SamplerComparisonState`）で、`SampleCmp` を呼ぶと、**ハードウェアが周りの 4 テクセルを比較**し、**バイリニアの重みで補間**します（[Shadow Map Basics](shadow-map-basics/index.md)）。

```hlsl
float shadow = shadow_tex.SampleCmpLevelZero(shadow_sampler, uv, depth);
```

| 項目 | 内容 |
| --- | --- |
| **サンプル数** | **1 回の呼び出し**で、4 テクセルの比較 ＋ 補間 |
| **縁の滑らかさ** | **約 1 テクセル幅**のぼかし（最小限の PCF） |
| **コスト** | 小さい（専用ハードウェア） |

これだけでも**点比較より、はるかに滑らか**です。**より広くぼかす**には、**この呼び出しを複数回**行います。

## 広い PCF：複数サンプル

**中心の周りの複数の位置**で `SampleCmp` を呼び、**平均**します。

### 格子（N×N）

**テクセル単位の格子**で、N×N 個をサンプルします。

```hlsl
float PCFGrid(float2 uv, float depth, float2 texel_size) {
  float sum = 0.0;
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      sum += shadow_tex.SampleCmpLevelZero(shadow_sampler, uv + float2(x, y) * texel_size, depth);
    }
  }
  return sum / 9.0;
}
```

| カーネル | 呼び出し回数 | ぼけの幅 | 特徴 |
| --- | --- | --- | --- |
| <strong>2×2（HW）</strong> | 1 | 約 1 テクセル | 縁がやや滑らか |
| **3×3** | 9 | 約 3 テクセル（各 2×2 を含め、実質 4 テクセル幅） | 標準的 |
| **5×5** | 25 | 約 6 テクセル | ソフト。**重い** |
| **7×7** | 49 | 約 8 テクセル | 非常にソフト。**非常に重い** |

**N² に比例してコスト増**です。**大きいカーネル**は、**サンプルの数が増えすぎる**ので、別の配置を使います。

### 重み付き（ガウス・テント）

**中心を大きく、外側を小さく**重み付けすると、**縁のぼけが自然**になります。**格子のサンプルにガウスの重み**を掛けて、合計を重みの総和で割ります。**3×3 のハードウェア PCF** で、**バイリニアの重みを工夫**して、**少ない呼び出し回数で広いテント フィルタ**を作る手法もあります（NVIDIA の最適化 PCF など）。

### ポワソン円盤

**格子**は**規則的**なので<strong>縞（バンディング）</strong>が出やすいです。**ポワソン円盤**（Poisson disk）は、**ランダムに近いが点が近づきすぎない**分布で、<strong>少ないサンプル（8〜16）</strong>でも**滑らか**になります。

```hlsl
static const float2 kPoissonDisk[16] = { /* 事前計算した 16 点（半径 1 の円盤内） */ };

float PCFPoisson(float2 uv, float depth, float filter_radius_uv, float2 rotation) {
  float sum = 0.0;
  [unroll] for (int i = 0; i < 16; ++i) {
    float2 offset = kPoissonDisk[i];
    offset = float2(offset.x * rotation.x - offset.y * rotation.y,
                    offset.x * rotation.y + offset.y * rotation.x);
    sum += shadow_tex.SampleCmpLevelZero(shadow_sampler, uv + offset * filter_radius_uv, depth);
  }
  return sum / 16.0;
}
```

| 点 | 説明 |
| --- | --- |
| **16 点を事前計算** | 半径 1 の円盤内のポワソン分布の点（定数配列） |
| **`filter_radius_uv`** | ぼけの半径（uv 単位）。**これが影のソフトさ** |
| **回転** | **画素ごとに回す**（下記）。**縞をノイズに変える** |

### 画素ごとの回転（ノイズ）

**全画素が同じサンプル パターン**だと、**パターンの偏りが縞**になります。**画素ごとにパターンを回転**させる（**ランダムな角度**）と、**縞が細かいノイズ**に変わり、**目立たなくなります**。

| 回転の与え方 | 内容 |
| --- | --- |
| **ノイズ テクスチャ** | 4×4 などのランダム角度のテクスチャ |
| <strong>IGN（Interleaved Gradient Noise）</strong> | **画素の座標から、式で計算**（[AO Filtering](../ao/filtering/index.md)） |
| **時間方向** | **フレームごとに角度を変える**（TAA と併用して、時間方向に平均） |

少ないサンプル（8〜16）に、**画素ごとの回転**と、**TAA**（または時間蓄積）を組み合わせると**実質的に非常に多くのサンプル**を使った**ソフトな影**になります。

<!-- fig:pcf-kernel:begin -->

<svg class="fig illust motion" data-fig="pcf-kernel" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-pcf-kernel" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">PCF:カーネルが広いほど、影の縁がやわらかくなる</text>
<text x="60" y="70" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">カーネル 1（比較 1 回）</text>
<text x="684" y="128" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b"/>
<rect x="60" y="78" width="27" height="18" fill="#334155"/>
<rect x="88" y="78" width="27" height="18" fill="#334155"/>
<rect x="116" y="78" width="27" height="18" fill="#334155"/>
<rect x="144" y="78" width="27" height="18" fill="#334155"/>
<rect x="172" y="78" width="27" height="18" fill="#334155"/>
<rect x="200" y="78" width="27" height="18" fill="#334155"/>
<rect x="228" y="78" width="27" height="18" fill="#334155"/>
<rect x="256" y="78" width="27" height="18" fill="#334155"/>
<rect x="284" y="78" width="27" height="18" fill="#334155"/>
<rect x="312" y="78" width="27" height="18" fill="#334155"/>
<rect x="340" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="368" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="396" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="424" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="452" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="480" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="508" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="536" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="564" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="592" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="620" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="648" y="78" width="27" height="18" fill="#fde68a"/>
<rect x="60" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741" values="#f1f5f9;#334059"/></rect>
<rect x="88" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#f1f5f9;#334059"/></rect>
<rect x="116" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1407" values="#f1f5f9;#334059"/></rect>
<rect x="144" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1741" values="#f1f5f9;#334059"/></rect>
<rect x="172" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2074" values="#f1f5f9;#334059"/></rect>
<rect x="200" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2407" values="#f1f5f9;#334059"/></rect>
<rect x="228" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2741" values="#f1f5f9;#334059"/></rect>
<rect x="256" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3074" values="#f1f5f9;#334059"/></rect>
<rect x="284" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3407" values="#f1f5f9;#334059"/></rect>
<rect x="312" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3741" values="#f1f5f9;#334059"/></rect>
<rect x="340" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="368" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="396" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="424" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="452" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="480" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="508" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="536" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="564" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="592" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="620" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="648" y="100" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="60" y="76" width="27" height="64" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1074;0.1407;0.1741;0.2074;0.2407;0.2741;0.3074;0.3407;0.3741;0.4074;0.4407;0.4741;0.5074;0.5407;0.5741;0.6074;0.6407;0.6741;0.7074;0.7407;0.7741" values="60;60;88;116;144;172;200;228;256;284;312;340;368;396;424;452;480;508;536;564;592;620;648"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8071;0.8074;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="60" y="160" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">カーネル 3</text>
<text x="684" y="218" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b"/>
<rect x="60" y="168" width="27" height="18" fill="#334155"/>
<rect x="88" y="168" width="27" height="18" fill="#334155"/>
<rect x="116" y="168" width="27" height="18" fill="#334155"/>
<rect x="144" y="168" width="27" height="18" fill="#334155"/>
<rect x="172" y="168" width="27" height="18" fill="#334155"/>
<rect x="200" y="168" width="27" height="18" fill="#334155"/>
<rect x="228" y="168" width="27" height="18" fill="#334155"/>
<rect x="256" y="168" width="27" height="18" fill="#334155"/>
<rect x="284" y="168" width="27" height="18" fill="#334155"/>
<rect x="312" y="168" width="27" height="18" fill="#334155"/>
<rect x="340" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="368" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="396" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="424" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="452" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="480" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="508" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="536" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="564" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="592" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="620" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="648" y="168" width="27" height="18" fill="#fde68a"/>
<rect x="60" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741" values="#f1f5f9;#334059"/></rect>
<rect x="88" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#f1f5f9;#334059"/></rect>
<rect x="116" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1407" values="#f1f5f9;#334059"/></rect>
<rect x="144" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1741" values="#f1f5f9;#334059"/></rect>
<rect x="172" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2074" values="#f1f5f9;#334059"/></rect>
<rect x="200" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2407" values="#f1f5f9;#334059"/></rect>
<rect x="228" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2741" values="#f1f5f9;#334059"/></rect>
<rect x="256" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3074" values="#f1f5f9;#334059"/></rect>
<rect x="284" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3407" values="#f1f5f9;#334059"/></rect>
<rect x="312" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3741" values="#f1f5f9;#757b80"/></rect>
<rect x="340" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4074" values="#f1f5f9;#b8b7a6"/></rect>
<rect x="368" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="396" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="424" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="452" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="480" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="508" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="536" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="564" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="592" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="620" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="648" y="190" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="60" y="166" width="83" height="64" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1074;0.1407;0.1741;0.2074;0.2407;0.2741;0.3074;0.3407;0.3741;0.4074;0.4407;0.4741;0.5074;0.5407;0.5741;0.6074;0.6407;0.6741;0.7074;0.7407;0.7741" values="60;32;60;88;116;144;172;200;228;256;284;312;340;368;396;424;452;480;508;536;564;592;620"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8071;0.8074;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="60" y="250" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">カーネル 5</text>
<text x="684" y="308" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b"/>
<rect x="60" y="258" width="27" height="18" fill="#334155"/>
<rect x="88" y="258" width="27" height="18" fill="#334155"/>
<rect x="116" y="258" width="27" height="18" fill="#334155"/>
<rect x="144" y="258" width="27" height="18" fill="#334155"/>
<rect x="172" y="258" width="27" height="18" fill="#334155"/>
<rect x="200" y="258" width="27" height="18" fill="#334155"/>
<rect x="228" y="258" width="27" height="18" fill="#334155"/>
<rect x="256" y="258" width="27" height="18" fill="#334155"/>
<rect x="284" y="258" width="27" height="18" fill="#334155"/>
<rect x="312" y="258" width="27" height="18" fill="#334155"/>
<rect x="340" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="368" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="396" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="424" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="452" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="480" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="508" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="536" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="564" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="592" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="620" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="648" y="258" width="27" height="18" fill="#fde68a"/>
<rect x="60" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741" values="#f1f5f9;#334059"/></rect>
<rect x="88" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#f1f5f9;#334059"/></rect>
<rect x="116" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1407" values="#f1f5f9;#334059"/></rect>
<rect x="144" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1741" values="#f1f5f9;#334059"/></rect>
<rect x="172" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2074" values="#f1f5f9;#334059"/></rect>
<rect x="200" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2407" values="#f1f5f9;#334059"/></rect>
<rect x="228" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2741" values="#f1f5f9;#334059"/></rect>
<rect x="256" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3074" values="#f1f5f9;#334059"/></rect>
<rect x="284" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3407" values="#f1f5f9;#5b6370"/></rect>
<rect x="312" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3741" values="#f1f5f9;#838787"/></rect>
<rect x="340" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4074" values="#f1f5f9;#aaab9e"/></rect>
<rect x="368" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4407" values="#f1f5f9;#d2cfb5"/></rect>
<rect x="396" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="424" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="452" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="480" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="508" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="536" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="564" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="592" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="620" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="648" y="280" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="60" y="256" width="139" height="64" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1074;0.1407;0.1741;0.2074;0.2407;0.2741;0.3074;0.3407;0.3741;0.4074;0.4407;0.4741;0.5074;0.5407;0.5741;0.6074;0.6407;0.6741;0.7074;0.7407;0.7741" values="60;4;32;60;88;116;144;172;200;228;256;284;312;340;368;396;424;452;480;508;536;564;592"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8071;0.8074;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="60" y="340" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">カーネル 9</text>
<text x="684" y="398" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b"/>
<rect x="60" y="348" width="27" height="18" fill="#334155"/>
<rect x="88" y="348" width="27" height="18" fill="#334155"/>
<rect x="116" y="348" width="27" height="18" fill="#334155"/>
<rect x="144" y="348" width="27" height="18" fill="#334155"/>
<rect x="172" y="348" width="27" height="18" fill="#334155"/>
<rect x="200" y="348" width="27" height="18" fill="#334155"/>
<rect x="228" y="348" width="27" height="18" fill="#334155"/>
<rect x="256" y="348" width="27" height="18" fill="#334155"/>
<rect x="284" y="348" width="27" height="18" fill="#334155"/>
<rect x="312" y="348" width="27" height="18" fill="#334155"/>
<rect x="340" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="368" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="396" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="424" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="452" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="480" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="508" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="536" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="564" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="592" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="620" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="648" y="348" width="27" height="18" fill="#fde68a"/>
<rect x="60" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741" values="#f1f5f9;#334059"/></rect>
<rect x="88" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#f1f5f9;#334059"/></rect>
<rect x="116" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1407" values="#f1f5f9;#334059"/></rect>
<rect x="144" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1741" values="#f1f5f9;#334059"/></rect>
<rect x="172" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2074" values="#f1f5f9;#334059"/></rect>
<rect x="200" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2407" values="#f1f5f9;#334059"/></rect>
<rect x="228" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2741" values="#f1f5f9;#495466"/></rect>
<rect x="256" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3074" values="#f1f5f9;#5f6773"/></rect>
<rect x="284" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3407" values="#f1f5f9;#757b80"/></rect>
<rect x="312" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3741" values="#f1f5f9;#8b8f8c"/></rect>
<rect x="340" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4074" values="#f1f5f9;#a2a399"/></rect>
<rect x="368" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4407" values="#f1f5f9;#b8b7a6"/></rect>
<rect x="396" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4741" values="#f1f5f9;#cecbb2"/></rect>
<rect x="424" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#e4debf"/></rect>
<rect x="452" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="480" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="508" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="536" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="564" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="592" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7074" values="#f1f5f9;#faf2cc"/></rect>
<rect x="620" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7407" values="#f1f5f9;#faf2cc"/></rect>
<rect x="648" y="370" width="27" height="36" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7741" values="#f1f5f9;#faf2cc"/></rect>
<rect x="60" y="346" width="251" height="64" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1074;0.1407;0.1741;0.2074;0.2407;0.2741;0.3074;0.3407;0.3741;0.4074;0.4407;0.4741;0.5074;0.5407;0.5741;0.6074;0.6407;0.6741;0.7074;0.7407;0.7741" values="60;-52;-24;4;32;60;88;116;144;172;200;228;256;284;312;340;368;396;424;452;480;508;536"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8071;0.8074;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="60" y="425" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">上の帯:影の判定（暗 = 影、黄 = 光）。下の帯:PCF の結果<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="60" y="425" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">橙の枠の中の判定を平均して、真ん中の画素の明るさにする<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8071;0.8074;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="425" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">カーネルを広げると、縁が広くなだらか。ただし、サンプルが増えてコストも上がる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8071;0.8074;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:pcf-kernel:end -->

## カーネルの大きさと見た目

<strong>PCF のぼけの幅は、カーネルの大きさで決まり、</strong>遮蔽物との距離とは無関係**です。

| 設定 | 見た目 |
| --- | --- |
| **小さい** | 縁がくっきり（エイリアシングを少し隠す） |
| **大きい** | 縁が全体に**ぼんやり** |
| **一定** | **接地部も遠い影も同じぼけ** |

**現実の影**は**遮蔽物に近い所は鋭く、離れるほどぼける**（接触硬化）ので**一定のぼけは不自然**です。**距離に応じてぼけを変える**には、<strong>[PCSS](pcss.md)</strong>を使います。

## コスト

| 項目 | 内容 |
| --- | --- |
| **サンプル数** | カーネル（N×N・点数）に比例 |
| **メモリ帯域** | シャドウ マップを**画素ごとに複数回読む**。**キャッシュに乗るか**が重要（近いサンプルほど有利） |
| **カスケード** | **カスケードごとにカーネルのテクセル数**が決まる（解像度が違うので**ぼけの見た目の幅がカスケードで変わる**。補正が要る） |
| **ブランチの活用** | **完全に日向・完全に影**の領域は、**少ないサンプルで済ませる**（早期終了） |

### 早期終了（影の縁だけ重くする）

**少ないサンプルで全部同じ結果**（全部日向・全部影）なら、**縁ではない**ので**そこで終了**します。**縁の画素だけ、残りのサンプル**を読みます。

```hlsl
float shadow = FirstFewSamples();
if (shadow > 0.0 && shadow < 1.0) {
  shadow = AllSamples();
}
```

**画面の大半は縁ではない**ので**大幅に速く**なります。ただし、**ブランチの発散**（隣の画素と道が分かれる）に注意します。

## PCF とバイアス

**カーネルが大きい**と**周りのサンプル**の位置が、**中心から離れる**ので**面の傾き**により、**サンプルごとに面の深度が違い**ます。**中心の深度のまま比べる**と、**傾いた面でサンプルが自己遮蔽**します。

| 対策 | 内容 |
| --- | --- |
| **受け手平面バイアス** | **サンプルごとに面の傾きで深度を補正**（[Shadow Bias](bias/index.md)） |
| **法線オフセット** | 位置を法線方向にずらす |
| **バイアスを大きく** | 簡単だがピーター パンニング |

**広い PCF には、受け手平面バイアスがほぼ必須**です。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **簡単**（比較サンプラー ＋ ループ） | **ぼけが一定**（接触硬化がない） |
| **ハードウェア支援で速い** | **サンプル数 × シャドウ マップ読み込み**で、重くなる |
| **ブランチで縁だけ重く**できる | **広いカーネルでバイアスが難しい** |
| **シャドウ マップの形式を選ばない**（深度のみ） | **サンプルが少ないと縞・ノイズ** |

## よくあるミス

??? failure "深度を、フィルタ（バイリニア）してから比べて、境界で破綻する"
    **比較サンプラー**で**比べてから**補間します。

??? failure "全画素で、同じサンプル パターンを使って、縞が見える"
    **画素ごとに回転**（ノイズ）させます。

??? failure "広いカーネルで、受け手平面バイアスなしで、傾いた面にアクネ"
    **受け手平面バイアス**を入れます。

??? failure "カスケードごとに、テクセル数が同じでぼけの幅がカスケードで変わる"
    **カスケードのワールド サイズ**で、**カーネルをスケール**します。

??? failure "全画素で、最大のカーネルを使って、重い"
    **早期終了**で縁だけを重くします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PCF ＝ <strong>周りの複数点で「影か」を比べ、その平均（日向の割合）を取る</strong>
    - [x] <strong>比べてから平均</strong>（深度の平均は誤り）。<strong>比較サンプラー</strong>が 2×2 の PCF を行う
    - [x] 広くするには<strong>格子・ポワソン円盤</strong>。<strong>画素ごとに回転</strong>してノイズに変える
    - [x] <strong>ぼけは一定</strong>（接触硬化なし）→ PCSS
    - [x] <strong>広いカーネルは、受け手平面バイアスが必要</strong>。<strong>早期終了</strong>で軽く

## 参考

- Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps"（SIGGRAPH 1987、PCF の原典）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"

## 関連ページ

- [Shadows](index.md)
- [Shadow Map Basics](shadow-map-basics/index.md)
- [Shadow Bias](bias/index.md)
- [PCSS](pcss.md)
- [AO のフィルタ（IGN・ノイズ）](../ao/filtering/index.md)
