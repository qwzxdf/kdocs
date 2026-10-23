---
title: PCF
tags:
  - 描画
---

# PCF

シャドウ マップの比較は、<strong>「影か、日向か」の 0 か 1</strong>です。これを 1 点だけで行うと、影の縁がギザギザ（エイリアシング）になります。PCF（Percentage Closer Filtering）は、周りの複数のテクセルで比較して、「日向の割合」を平均し、縁を滑らかにする方法です。深度を平均してから比べるのでなく、比べた結果を平均することが、重要な点です（深度は補間できません）。このページでは、PCF の原理・カーネルの種類・サンプルの配置・コストを説明します。

!!! tip "ポイント"
    - PCF ＝ <strong>周りの N 点それぞれで「影か」を比べ、その平均（日向の割合）を取る</strong>。
    - <strong>深度を先に平均してはいけない</strong>（影の境で嘘の深度ができる）。比較してから平均。
    - ハードウェア PCF：比較サンプラーのバイリニアが、2×2 の PCF を 1 回で行う。
    - 広くぼかすなら複数回サンプル：格子（N×N）・ポワソン円盤・回転。
    - カーネルが大きいほどソフトだが、遮蔽物との距離に関係なく一定のぼけ（現実の影と違う）。
    - カーネルが大きいと、バイアスの扱いが難しい（[Shadow Bias](bias/index.md)）。

## なぜ、比べてから平均するのか

シャドウ マップの値は<strong>深度</strong>です。深度を平均してから比べると、境界でどちらにも存在しない深度ができ、誤った結果になります（[SAO のミップ](../ao/sao.md)と同じ理由）。

深度を先に平均してから比べるのは誤りです。影の縁で、どちらにも存在しない嘘の深度ができるからです。先に比べて、その結果を平均すれば正しくなります。各点の「影か」の割合が得られます。

つまり、PCF の「比較」は、フィルタの前に行います。普通のテクスチャ フィルタ（バイリニア・ミップ）は、比較より前に値を補間するので、そのままでは使えません。専用の比較サンプラーが、この順序を実現します。

## ハードウェア PCF（2×2）

<strong>比較サンプラー</strong>（`SamplerComparisonState`）で、`SampleCmp` を呼ぶと、ハードウェアが周りの 4 テクセルを比較し、バイリニアの重みで補間します（[Shadow Map Basics](shadow-map-basics/index.md)）。

```hlsl
float shadow = shadow_tex.SampleCmpLevelZero(shadow_sampler, uv, depth);
```

ハードウェアの比較サンプラーの特徴です。1 回の呼び出しで、4 テクセルの比較と補間が行われます。縁は約 1 テクセル幅のぼかしになり、最小限の PCF になります。専用ハードウェアなので、コストは小さいです。

これだけでも点比較より、はるかに滑らかです。より広くぼかすには、この呼び出しを複数回行います。

## 広い PCF：複数サンプル

<strong>中心の周りの複数の位置</strong>で `SampleCmp` を呼び、平均します。

### 格子（N×N）

テクセル単位の格子で、N×N 個をサンプルします。

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
| 2×2（HW） | 1 | 約 1 テクセル | 縁がやや滑らか |
| 3×3 | 9 | 約 3 テクセル（各 2×2 を含め、実質 4 テクセル幅） | 標準的 |
| 5×5 | 25 | 約 6 テクセル | ソフト。重い |
| 7×7 | 49 | 約 8 テクセル | 非常にソフト。非常に重い |

N² に比例してコスト増です。大きいカーネルは、サンプルの数が増えすぎるので、別の配置を使います。

### 重み付き（ガウス・テント）

中心を大きく、外側を小さく重み付けすると、縁のぼけが自然になります。格子のサンプルにガウスの重みを掛けて、合計を重みの総和で割ります。3×3 のハードウェア PCF で、バイリニアの重みを工夫して、少ない呼び出し回数で広いテント フィルタを作る手法もあります（NVIDIA の最適化 PCF など）。

### ポワソン円盤

格子は規則的なので縞（バンディング）が出やすいです。ポワソン円盤（Poisson disk）は、ランダムに近いが点が近づきすぎない分布で、少ないサンプル（8〜16）でも滑らかになります。

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

コードの要点です。16 点を事前計算し、半径 1 の円盤内のポワソン分布の点を定数配列にしておきます。`filter_radius_uv` はぼけの半径（uv 単位）で、これが影のソフトさになります。回転は画素ごとに行います（次に説明します）。縞をノイズに変えるためです。

### 画素ごとの回転（ノイズ）

全画素が同じサンプル パターンだと、パターンの偏りが縞になります。画素ごとにパターンを回転させる（ランダムな角度）と、縞が細かいノイズに変わり、目立たなくなります。

回転の与え方は 3 通りあります。4×4 などのランダムな角度のテクスチャを使う方法。IGN（Interleaved Gradient Noise）を画素の座標から式で計算する方法（[AO Filtering](../ao/filtering/index.md)）。フレームごとに角度を変えて、TAA と併用し、時間方向に平均する方法です。

少ないサンプル（8〜16）に、画素ごとの回転と、TAA（または時間蓄積）を組み合わせると実質的に非常に多くのサンプルを使ったソフトな影になります。

<!-- fig:pcf-kernel:begin -->

<svg class="fig illust motion" data-fig="pcf-kernel" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-pcf-kernel" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">PCF: 周りの数マスを調べて平均し、影の縁をなめらかにする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">同じシャドウ マップ(1 マス = 3×3 ピクセルの荒い表)を、1 回 / 3×3 回 / 5×5 回 読んで比べる</text>
<rect x="30" y="96" width="286.0" height="182.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">PCF なし(1 回)</text>
<rect x="30.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#fde68a"/></rect>
<rect x="121.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#fde68a"/></rect>
<rect x="147.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#fde68a"/></rect>
<rect x="121.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#fde68a"/></rect>
<rect x="147.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#fde68a"/></rect>
<rect x="121.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#fde68a"/></rect>
<rect x="147.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#475569"/></rect>
<rect x="238.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#475569"/></rect>
<rect x="251.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#475569"/></rect>
<rect x="264.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#475569"/></rect>
<rect x="238.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#475569"/></rect>
<rect x="251.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#475569"/></rect>
<rect x="264.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#475569"/></rect>
<rect x="238.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#475569"/></rect>
<rect x="251.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#475569"/></rect>
<rect x="264.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#475569"/></rect>
<rect x="238.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#475569"/></rect>
<rect x="251.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#475569"/></rect>
<rect x="264.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#475569"/></rect>
<rect x="238.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#475569"/></rect>
<rect x="251.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#475569"/></rect>
<rect x="264.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#475569"/></rect>
<rect x="238.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#475569"/></rect>
<rect x="251.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#475569"/></rect>
<rect x="264.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#475569"/></rect>
<rect x="121.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#475569"/></rect>
<rect x="134.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#475569"/></rect>
<rect x="147.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="160.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="173.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="186.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#475569"/></rect>
<rect x="199.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#475569"/></rect>
<rect x="212.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#475569"/></rect>
<rect x="225.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#fde68a"/></rect>
<rect x="121.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#fde68a"/></rect>
<rect x="147.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#fde68a"/></rect>
<rect x="160.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#fde68a"/></rect>
<rect x="173.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#fde68a"/></rect>
<rect x="186.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#fde68a"/></rect>
<rect x="199.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#fde68a"/></rect>
<rect x="212.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#fde68a"/></rect>
<rect x="225.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="30.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="43.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="56.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="69.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#fde68a"/></rect>
<rect x="82.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#fde68a"/></rect>
<rect x="95.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#fde68a"/></rect>
<rect x="108.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#fde68a"/></rect>
<rect x="121.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#fde68a"/></rect>
<rect x="147.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#fde68a"/></rect>
<rect x="160.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#fde68a"/></rect>
<rect x="173.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#fde68a"/></rect>
<rect x="186.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#fde68a"/></rect>
<rect x="199.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#fde68a"/></rect>
<rect x="212.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#fde68a"/></rect>
<rect x="225.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#fde68a"/></rect>
<rect x="238.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#fde68a"/></rect>
<rect x="251.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#fde68a"/></rect>
<rect x="264.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="277.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="290.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="303.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<g opacity="0.18"><line x1="43.0" y1="96" x2="43.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="56.0" y1="96" x2="56.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="69.0" y1="96" x2="69.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="82.0" y1="96" x2="82.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="95.0" y1="96" x2="95.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="108.0" y1="96" x2="108.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="121.0" y1="96" x2="121.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="134.0" y1="96" x2="134.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="147.0" y1="96" x2="147.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="160.0" y1="96" x2="160.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="173.0" y1="96" x2="173.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="186.0" y1="96" x2="186.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="199.0" y1="96" x2="199.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="212.0" y1="96" x2="212.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="225.0" y1="96" x2="225.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="238.0" y1="96" x2="238.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="251.0" y1="96" x2="251.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="264.0" y1="96" x2="264.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="277.0" y1="96" x2="277.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="290.0" y1="96" x2="290.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="303.0" y1="96" x2="303.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="109.0" x2="316.0" y2="109.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="122.0" x2="316.0" y2="122.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="135.0" x2="316.0" y2="135.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="148.0" x2="316.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="161.0" x2="316.0" y2="161.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="174.0" x2="316.0" y2="174.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="187.0" x2="316.0" y2="187.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="200.0" x2="316.0" y2="200.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="213.0" x2="316.0" y2="213.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="226.0" x2="316.0" y2="226.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="239.0" x2="316.0" y2="239.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="252.0" x2="316.0" y2="252.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="30" y1="265.0" x2="316.0" y2="265.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="30" y="96" width="286.0" height="182.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<rect x="225.0" y="148.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2752;0.2754;1.0000" values="0;0;1;1"/></rect>
<text x="30" y="322" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">読み込み:</text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">14<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.0661;0.0663;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0661;0.0663;0.0752;0.0754;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">42<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0752;0.0754;0.0843;0.0846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">56<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0843;0.0846;0.0935;0.0937;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">70<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0935;0.0937;0.1026;0.1029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">84<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;0.1118;0.1120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">98<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1118;0.1120;0.1209;0.1211;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">112<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1209;0.1211;0.1301;0.1303;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">126<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1303;0.1392;0.1394;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">140<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1392;0.1394;0.1483;0.1486;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">154<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1483;0.1486;0.1575;0.1577;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">168<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1575;0.1577;0.1666;0.1669;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">182<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1666;0.1669;0.1758;0.1760;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">196<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1758;0.1760;0.1849;0.1851;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">210<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1849;0.1851;0.1941;0.1943;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">224<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2032;0.2034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">238<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2032;0.2034;0.2123;0.2126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">252<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2123;0.2126;0.2215;0.2217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">266<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2215;0.2217;0.2306;0.2309;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">280<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2306;0.2309;0.2398;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">294<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2398;0.2400;0.2489;0.2491;1.0000" values="0;0;1;1;0;0"/></text>
<text x="108" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d" opacity="0">308<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2489;0.2491;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/><rect x="36.0" y="340.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<text x="63.0" y="356" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">赤枠の画素:</text>
<text x="63.0" y="376" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">影 1 / 1 マス</text>
<text x="63.0" y="398" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">= 影の濃さ 1.00</text>
</g>
<rect x="335" y="96" width="286.0" height="182.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="335" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">PCF 3×3(9 回)</text>
<rect x="335.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#e9d686"/></rect>
<rect x="387.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#e9d686"/></rect>
<rect x="400.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#e9d686"/></rect>
<rect x="413.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#c0b67f"/></rect>
<rect x="426.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#c0b67f"/></rect>
<rect x="439.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#c0b67f"/></rect>
<rect x="452.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#989578"/></rect>
<rect x="465.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#989578"/></rect>
<rect x="478.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#989578"/></rect>
<rect x="491.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#989578"/></rect>
<rect x="504.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#989578"/></rect>
<rect x="517.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#989578"/></rect>
<rect x="530.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c0b67f"/></rect>
<rect x="543.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c0b67f"/></rect>
<rect x="556.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c0b67f"/></rect>
<rect x="569.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e9d686"/></rect>
<rect x="582.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e9d686"/></rect>
<rect x="595.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e9d686"/></rect>
<rect x="608.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#e9d686"/></rect>
<rect x="387.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#e9d686"/></rect>
<rect x="400.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#e9d686"/></rect>
<rect x="413.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#c0b67f"/></rect>
<rect x="426.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#c0b67f"/></rect>
<rect x="439.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#c0b67f"/></rect>
<rect x="452.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#989578"/></rect>
<rect x="465.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#989578"/></rect>
<rect x="478.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#989578"/></rect>
<rect x="491.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#989578"/></rect>
<rect x="504.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#989578"/></rect>
<rect x="517.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#989578"/></rect>
<rect x="530.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c0b67f"/></rect>
<rect x="543.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c0b67f"/></rect>
<rect x="556.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c0b67f"/></rect>
<rect x="569.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e9d686"/></rect>
<rect x="582.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e9d686"/></rect>
<rect x="595.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e9d686"/></rect>
<rect x="608.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#e9d686"/></rect>
<rect x="387.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#e9d686"/></rect>
<rect x="400.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#e9d686"/></rect>
<rect x="413.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#c0b67f"/></rect>
<rect x="426.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#c0b67f"/></rect>
<rect x="439.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#c0b67f"/></rect>
<rect x="452.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#989578"/></rect>
<rect x="465.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#989578"/></rect>
<rect x="478.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#989578"/></rect>
<rect x="491.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#989578"/></rect>
<rect x="504.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#989578"/></rect>
<rect x="517.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#989578"/></rect>
<rect x="530.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c0b67f"/></rect>
<rect x="543.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c0b67f"/></rect>
<rect x="556.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c0b67f"/></rect>
<rect x="569.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e9d686"/></rect>
<rect x="582.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e9d686"/></rect>
<rect x="595.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e9d686"/></rect>
<rect x="608.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d5c683"/></rect>
<rect x="387.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d5c683"/></rect>
<rect x="400.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d5c683"/></rect>
<rect x="413.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#989578"/></rect>
<rect x="426.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#989578"/></rect>
<rect x="439.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#989578"/></rect>
<rect x="452.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#5b656d"/></rect>
<rect x="465.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#5b656d"/></rect>
<rect x="478.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#5b656d"/></rect>
<rect x="491.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#5b656d"/></rect>
<rect x="504.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#5b656d"/></rect>
<rect x="517.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#5b656d"/></rect>
<rect x="530.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#989578"/></rect>
<rect x="543.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#989578"/></rect>
<rect x="556.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#989578"/></rect>
<rect x="569.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d5c683"/></rect>
<rect x="582.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d5c683"/></rect>
<rect x="595.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d5c683"/></rect>
<rect x="608.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d5c683"/></rect>
<rect x="387.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d5c683"/></rect>
<rect x="400.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d5c683"/></rect>
<rect x="413.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#989578"/></rect>
<rect x="426.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#989578"/></rect>
<rect x="439.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#989578"/></rect>
<rect x="452.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#5b656d"/></rect>
<rect x="465.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#5b656d"/></rect>
<rect x="478.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#5b656d"/></rect>
<rect x="491.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#5b656d"/></rect>
<rect x="504.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#5b656d"/></rect>
<rect x="517.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#5b656d"/></rect>
<rect x="530.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#989578"/></rect>
<rect x="543.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#989578"/></rect>
<rect x="556.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#989578"/></rect>
<rect x="569.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d5c683"/></rect>
<rect x="582.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d5c683"/></rect>
<rect x="595.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d5c683"/></rect>
<rect x="608.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d5c683"/></rect>
<rect x="387.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d5c683"/></rect>
<rect x="400.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d5c683"/></rect>
<rect x="413.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#989578"/></rect>
<rect x="426.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#989578"/></rect>
<rect x="439.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#989578"/></rect>
<rect x="452.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#5b656d"/></rect>
<rect x="465.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#5b656d"/></rect>
<rect x="478.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#5b656d"/></rect>
<rect x="491.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#5b656d"/></rect>
<rect x="504.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#5b656d"/></rect>
<rect x="517.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#5b656d"/></rect>
<rect x="530.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#989578"/></rect>
<rect x="543.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#989578"/></rect>
<rect x="556.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#989578"/></rect>
<rect x="569.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d5c683"/></rect>
<rect x="582.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d5c683"/></rect>
<rect x="595.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d5c683"/></rect>
<rect x="608.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#c0b67f"/></rect>
<rect x="387.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#c0b67f"/></rect>
<rect x="400.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#c0b67f"/></rect>
<rect x="413.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#848574"/></rect>
<rect x="426.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#848574"/></rect>
<rect x="439.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#848574"/></rect>
<rect x="452.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="465.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="478.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="491.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#5b656d"/></rect>
<rect x="504.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#5b656d"/></rect>
<rect x="517.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#5b656d"/></rect>
<rect x="530.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#989578"/></rect>
<rect x="543.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#989578"/></rect>
<rect x="556.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#989578"/></rect>
<rect x="569.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d5c683"/></rect>
<rect x="582.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d5c683"/></rect>
<rect x="595.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d5c683"/></rect>
<rect x="608.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#c0b67f"/></rect>
<rect x="387.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#c0b67f"/></rect>
<rect x="400.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#c0b67f"/></rect>
<rect x="413.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#848574"/></rect>
<rect x="426.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#848574"/></rect>
<rect x="439.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#848574"/></rect>
<rect x="452.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="465.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="478.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="491.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#5b656d"/></rect>
<rect x="504.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#5b656d"/></rect>
<rect x="517.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#5b656d"/></rect>
<rect x="530.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#989578"/></rect>
<rect x="543.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#989578"/></rect>
<rect x="556.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#989578"/></rect>
<rect x="569.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d5c683"/></rect>
<rect x="582.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d5c683"/></rect>
<rect x="595.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d5c683"/></rect>
<rect x="608.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#c0b67f"/></rect>
<rect x="387.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#c0b67f"/></rect>
<rect x="400.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#c0b67f"/></rect>
<rect x="413.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#848574"/></rect>
<rect x="426.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#848574"/></rect>
<rect x="439.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#848574"/></rect>
<rect x="452.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#475569"/></rect>
<rect x="465.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#475569"/></rect>
<rect x="478.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#475569"/></rect>
<rect x="491.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#5b656d"/></rect>
<rect x="504.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#5b656d"/></rect>
<rect x="517.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#5b656d"/></rect>
<rect x="530.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#989578"/></rect>
<rect x="543.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#989578"/></rect>
<rect x="556.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#989578"/></rect>
<rect x="569.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d5c683"/></rect>
<rect x="582.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d5c683"/></rect>
<rect x="595.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d5c683"/></rect>
<rect x="608.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d5c683"/></rect>
<rect x="387.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d5c683"/></rect>
<rect x="400.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d5c683"/></rect>
<rect x="413.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#aca67b"/></rect>
<rect x="426.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#aca67b"/></rect>
<rect x="439.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#aca67b"/></rect>
<rect x="452.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#848574"/></rect>
<rect x="465.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#848574"/></rect>
<rect x="478.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#848574"/></rect>
<rect x="491.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#989578"/></rect>
<rect x="504.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#989578"/></rect>
<rect x="517.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#989578"/></rect>
<rect x="530.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c0b67f"/></rect>
<rect x="543.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c0b67f"/></rect>
<rect x="556.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c0b67f"/></rect>
<rect x="569.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e9d686"/></rect>
<rect x="582.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e9d686"/></rect>
<rect x="595.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e9d686"/></rect>
<rect x="608.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d5c683"/></rect>
<rect x="387.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d5c683"/></rect>
<rect x="400.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d5c683"/></rect>
<rect x="413.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#aca67b"/></rect>
<rect x="426.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#aca67b"/></rect>
<rect x="439.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#aca67b"/></rect>
<rect x="452.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#848574"/></rect>
<rect x="465.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#848574"/></rect>
<rect x="478.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#848574"/></rect>
<rect x="491.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#989578"/></rect>
<rect x="504.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#989578"/></rect>
<rect x="517.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#989578"/></rect>
<rect x="530.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c0b67f"/></rect>
<rect x="543.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c0b67f"/></rect>
<rect x="556.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c0b67f"/></rect>
<rect x="569.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e9d686"/></rect>
<rect x="582.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e9d686"/></rect>
<rect x="595.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e9d686"/></rect>
<rect x="608.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d5c683"/></rect>
<rect x="387.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d5c683"/></rect>
<rect x="400.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d5c683"/></rect>
<rect x="413.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#aca67b"/></rect>
<rect x="426.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#aca67b"/></rect>
<rect x="439.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#aca67b"/></rect>
<rect x="452.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#848574"/></rect>
<rect x="465.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#848574"/></rect>
<rect x="478.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#848574"/></rect>
<rect x="491.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#989578"/></rect>
<rect x="504.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#989578"/></rect>
<rect x="517.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#989578"/></rect>
<rect x="530.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c0b67f"/></rect>
<rect x="543.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c0b67f"/></rect>
<rect x="556.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c0b67f"/></rect>
<rect x="569.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e9d686"/></rect>
<rect x="582.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e9d686"/></rect>
<rect x="595.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e9d686"/></rect>
<rect x="608.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#e9d686"/></rect>
<rect x="387.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#e9d686"/></rect>
<rect x="400.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#e9d686"/></rect>
<rect x="413.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#d5c683"/></rect>
<rect x="426.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#d5c683"/></rect>
<rect x="439.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#d5c683"/></rect>
<rect x="452.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#c0b67f"/></rect>
<rect x="465.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#c0b67f"/></rect>
<rect x="478.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#c0b67f"/></rect>
<rect x="491.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#d5c683"/></rect>
<rect x="504.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#d5c683"/></rect>
<rect x="517.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#d5c683"/></rect>
<rect x="530.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#e9d686"/></rect>
<rect x="543.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#e9d686"/></rect>
<rect x="556.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#e9d686"/></rect>
<rect x="569.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="582.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="595.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="608.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<rect x="335.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#fde68a"/></rect>
<rect x="348.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#fde68a"/></rect>
<rect x="361.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#fde68a"/></rect>
<rect x="374.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#e9d686"/></rect>
<rect x="387.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#e9d686"/></rect>
<rect x="400.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#e9d686"/></rect>
<rect x="413.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#d5c683"/></rect>
<rect x="426.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#d5c683"/></rect>
<rect x="439.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#d5c683"/></rect>
<rect x="452.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#c0b67f"/></rect>
<rect x="465.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#c0b67f"/></rect>
<rect x="478.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#c0b67f"/></rect>
<rect x="491.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#d5c683"/></rect>
<rect x="504.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#d5c683"/></rect>
<rect x="517.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#d5c683"/></rect>
<rect x="530.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#e9d686"/></rect>
<rect x="543.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#e9d686"/></rect>
<rect x="556.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#e9d686"/></rect>
<rect x="569.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#fde68a"/></rect>
<rect x="582.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#fde68a"/></rect>
<rect x="595.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#fde68a"/></rect>
<rect x="608.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#fde68a"/></rect>
<g opacity="0.18"><line x1="348.0" y1="96" x2="348.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="361.0" y1="96" x2="361.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="374.0" y1="96" x2="374.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="387.0" y1="96" x2="387.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="400.0" y1="96" x2="400.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="413.0" y1="96" x2="413.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="426.0" y1="96" x2="426.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="439.0" y1="96" x2="439.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="452.0" y1="96" x2="452.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="465.0" y1="96" x2="465.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="478.0" y1="96" x2="478.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="491.0" y1="96" x2="491.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="504.0" y1="96" x2="504.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="517.0" y1="96" x2="517.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="530.0" y1="96" x2="530.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="543.0" y1="96" x2="543.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="556.0" y1="96" x2="556.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="569.0" y1="96" x2="569.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="582.0" y1="96" x2="582.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="595.0" y1="96" x2="595.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="608.0" y1="96" x2="608.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="109.0" x2="621.0" y2="109.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="122.0" x2="621.0" y2="122.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="135.0" x2="621.0" y2="135.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="148.0" x2="621.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="161.0" x2="621.0" y2="161.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="174.0" x2="621.0" y2="174.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="187.0" x2="621.0" y2="187.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="200.0" x2="621.0" y2="200.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="213.0" x2="621.0" y2="213.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="226.0" x2="621.0" y2="226.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="239.0" x2="621.0" y2="239.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="252.0" x2="621.0" y2="252.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="335" y1="265.0" x2="621.0" y2="265.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="335" y="96" width="286.0" height="182.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<rect x="530.0" y="148.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2752;0.2754;1.0000" values="0;0;1;1"/></rect>
<text x="335" y="322" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">読み込み:</text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">126<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.0661;0.0663;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">252<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0661;0.0663;0.0752;0.0754;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">378<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0752;0.0754;0.0843;0.0846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">504<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0843;0.0846;0.0935;0.0937;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">630<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0935;0.0937;0.1026;0.1029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">756<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;0.1118;0.1120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">882<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1118;0.1120;0.1209;0.1211;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,008<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1209;0.1211;0.1301;0.1303;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,134<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1303;0.1392;0.1394;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,260<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1392;0.1394;0.1483;0.1486;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,386<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1483;0.1486;0.1575;0.1577;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,512<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1575;0.1577;0.1666;0.1669;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,638<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1666;0.1669;0.1758;0.1760;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,764<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1758;0.1760;0.1849;0.1851;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">1,890<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1849;0.1851;0.1941;0.1943;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2,016<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2032;0.2034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2,142<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2032;0.2034;0.2123;0.2126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2,268<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2123;0.2126;0.2215;0.2217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2,394<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2215;0.2217;0.2306;0.2309;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2,520<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2306;0.2309;0.2398;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2,646<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2398;0.2400;0.2489;0.2491;1.0000" values="0;0;1;1;0;0"/></text>
<text x="413" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">2,772<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2489;0.2491;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/><rect x="341.0" y="340.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="356.0" y="340.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="371.0" y="340.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="341.0" y="355.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="356.0" y="355.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="371.0" y="355.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="341.0" y="370.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="356.0" y="370.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="371.0" y="370.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<text x="398.0" y="356" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">赤枠の画素:</text>
<text x="398.0" y="376" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">影 5 / 9 マス</text>
<text x="398.0" y="398" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2563eb">= 影の濃さ 0.56</text>
</g>
<rect x="640" y="96" width="286.0" height="182.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="640" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">PCF 5×5(25 回)</text>
<rect x="640.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#eeda87"/></rect>
<rect x="653.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#eeda87"/></rect>
<rect x="666.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#eeda87"/></rect>
<rect x="679.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d9c983"/></rect>
<rect x="692.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d9c983"/></rect>
<rect x="705.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d9c983"/></rect>
<rect x="718.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#c3b87f"/></rect>
<rect x="731.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#c3b87f"/></rect>
<rect x="744.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#c3b87f"/></rect>
<rect x="757.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="770.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="783.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="796.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="809.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="822.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="835.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c3b87f"/></rect>
<rect x="848.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c3b87f"/></rect>
<rect x="861.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c3b87f"/></rect>
<rect x="874.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d9c983"/></rect>
<rect x="887.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d9c983"/></rect>
<rect x="900.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d9c983"/></rect>
<rect x="913.0" y="96.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#eeda87"/></rect>
<rect x="653.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#eeda87"/></rect>
<rect x="666.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#eeda87"/></rect>
<rect x="679.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d9c983"/></rect>
<rect x="692.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d9c983"/></rect>
<rect x="705.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d9c983"/></rect>
<rect x="718.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#c3b87f"/></rect>
<rect x="731.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#c3b87f"/></rect>
<rect x="744.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#c3b87f"/></rect>
<rect x="757.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="770.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="783.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="796.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="809.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="822.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="835.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c3b87f"/></rect>
<rect x="848.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c3b87f"/></rect>
<rect x="861.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c3b87f"/></rect>
<rect x="874.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d9c983"/></rect>
<rect x="887.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d9c983"/></rect>
<rect x="900.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d9c983"/></rect>
<rect x="913.0" y="109.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#eeda87"/></rect>
<rect x="653.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#eeda87"/></rect>
<rect x="666.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#eeda87"/></rect>
<rect x="679.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d9c983"/></rect>
<rect x="692.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d9c983"/></rect>
<rect x="705.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d9c983"/></rect>
<rect x="718.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#c3b87f"/></rect>
<rect x="731.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#c3b87f"/></rect>
<rect x="744.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#c3b87f"/></rect>
<rect x="757.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="770.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="783.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="796.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="809.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="822.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="835.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c3b87f"/></rect>
<rect x="848.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c3b87f"/></rect>
<rect x="861.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c3b87f"/></rect>
<rect x="874.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d9c983"/></rect>
<rect x="887.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d9c983"/></rect>
<rect x="900.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d9c983"/></rect>
<rect x="913.0" y="122.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#cabd81"/></rect>
<rect x="692.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#cabd81"/></rect>
<rect x="705.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#cabd81"/></rect>
<rect x="718.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#ada67b"/></rect>
<rect x="731.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#ada67b"/></rect>
<rect x="744.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#ada67b"/></rect>
<rect x="757.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#9e9b79"/></rect>
<rect x="770.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#9e9b79"/></rect>
<rect x="783.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#9e9b79"/></rect>
<rect x="796.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#9e9b79"/></rect>
<rect x="809.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#9e9b79"/></rect>
<rect x="822.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#9e9b79"/></rect>
<rect x="835.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="848.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="861.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="874.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d1c382"/></rect>
<rect x="887.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d1c382"/></rect>
<rect x="900.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d1c382"/></rect>
<rect x="913.0" y="135.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#cabd81"/></rect>
<rect x="692.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#cabd81"/></rect>
<rect x="705.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#cabd81"/></rect>
<rect x="718.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#ada67b"/></rect>
<rect x="731.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#ada67b"/></rect>
<rect x="744.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#ada67b"/></rect>
<rect x="757.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#9e9b79"/></rect>
<rect x="770.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#9e9b79"/></rect>
<rect x="783.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#9e9b79"/></rect>
<rect x="796.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#9e9b79"/></rect>
<rect x="809.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#9e9b79"/></rect>
<rect x="822.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#9e9b79"/></rect>
<rect x="835.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="848.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="861.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="874.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d1c382"/></rect>
<rect x="887.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d1c382"/></rect>
<rect x="900.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d1c382"/></rect>
<rect x="913.0" y="148.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#cabd81"/></rect>
<rect x="692.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#cabd81"/></rect>
<rect x="705.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#cabd81"/></rect>
<rect x="718.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#ada67b"/></rect>
<rect x="731.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#ada67b"/></rect>
<rect x="744.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#ada67b"/></rect>
<rect x="757.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#9e9b79"/></rect>
<rect x="770.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#9e9b79"/></rect>
<rect x="783.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#9e9b79"/></rect>
<rect x="796.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#9e9b79"/></rect>
<rect x="809.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#9e9b79"/></rect>
<rect x="822.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#9e9b79"/></rect>
<rect x="835.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="848.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="861.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="874.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d1c382"/></rect>
<rect x="887.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d1c382"/></rect>
<rect x="900.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d1c382"/></rect>
<rect x="913.0" y="161.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#cabd81"/></rect>
<rect x="692.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#cabd81"/></rect>
<rect x="705.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#cabd81"/></rect>
<rect x="718.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#ada67b"/></rect>
<rect x="731.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#ada67b"/></rect>
<rect x="744.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#ada67b"/></rect>
<rect x="757.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#9e9b79"/></rect>
<rect x="770.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#9e9b79"/></rect>
<rect x="783.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#9e9b79"/></rect>
<rect x="796.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#9e9b79"/></rect>
<rect x="809.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#9e9b79"/></rect>
<rect x="822.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#9e9b79"/></rect>
<rect x="835.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="848.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="861.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="874.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d1c382"/></rect>
<rect x="887.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d1c382"/></rect>
<rect x="900.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d1c382"/></rect>
<rect x="913.0" y="174.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#cabd81"/></rect>
<rect x="692.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#cabd81"/></rect>
<rect x="705.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#cabd81"/></rect>
<rect x="718.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#ada67b"/></rect>
<rect x="731.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#ada67b"/></rect>
<rect x="744.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#ada67b"/></rect>
<rect x="757.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#9e9b79"/></rect>
<rect x="770.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#9e9b79"/></rect>
<rect x="783.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#9e9b79"/></rect>
<rect x="796.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#9e9b79"/></rect>
<rect x="809.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#9e9b79"/></rect>
<rect x="822.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#9e9b79"/></rect>
<rect x="835.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="848.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="861.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="874.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d1c382"/></rect>
<rect x="887.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d1c382"/></rect>
<rect x="900.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d1c382"/></rect>
<rect x="913.0" y="187.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#cabd81"/></rect>
<rect x="692.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#cabd81"/></rect>
<rect x="705.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#cabd81"/></rect>
<rect x="718.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#ada67b"/></rect>
<rect x="731.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#ada67b"/></rect>
<rect x="744.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#ada67b"/></rect>
<rect x="757.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#9e9b79"/></rect>
<rect x="770.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#9e9b79"/></rect>
<rect x="783.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#9e9b79"/></rect>
<rect x="796.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#9e9b79"/></rect>
<rect x="809.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#9e9b79"/></rect>
<rect x="822.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#9e9b79"/></rect>
<rect x="835.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="848.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="861.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#b4ac7d"/></rect>
<rect x="874.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d1c382"/></rect>
<rect x="887.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d1c382"/></rect>
<rect x="900.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d1c382"/></rect>
<rect x="913.0" y="200.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d1c382"/></rect>
<rect x="692.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d1c382"/></rect>
<rect x="705.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d1c382"/></rect>
<rect x="718.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#bbb27e"/></rect>
<rect x="731.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#bbb27e"/></rect>
<rect x="744.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#bbb27e"/></rect>
<rect x="757.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#ada67b"/></rect>
<rect x="770.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#ada67b"/></rect>
<rect x="783.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#ada67b"/></rect>
<rect x="796.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#ada67b"/></rect>
<rect x="809.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#ada67b"/></rect>
<rect x="822.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#ada67b"/></rect>
<rect x="835.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c3b87f"/></rect>
<rect x="848.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c3b87f"/></rect>
<rect x="861.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c3b87f"/></rect>
<rect x="874.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d9c983"/></rect>
<rect x="887.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d9c983"/></rect>
<rect x="900.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d9c983"/></rect>
<rect x="913.0" y="213.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d1c382"/></rect>
<rect x="692.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d1c382"/></rect>
<rect x="705.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d1c382"/></rect>
<rect x="718.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#bbb27e"/></rect>
<rect x="731.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#bbb27e"/></rect>
<rect x="744.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#bbb27e"/></rect>
<rect x="757.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#ada67b"/></rect>
<rect x="770.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#ada67b"/></rect>
<rect x="783.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#ada67b"/></rect>
<rect x="796.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#ada67b"/></rect>
<rect x="809.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#ada67b"/></rect>
<rect x="822.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#ada67b"/></rect>
<rect x="835.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c3b87f"/></rect>
<rect x="848.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c3b87f"/></rect>
<rect x="861.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c3b87f"/></rect>
<rect x="874.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d9c983"/></rect>
<rect x="887.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d9c983"/></rect>
<rect x="900.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d9c983"/></rect>
<rect x="913.0" y="226.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#e7d586"/></rect>
<rect x="653.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#e7d586"/></rect>
<rect x="666.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#e7d586"/></rect>
<rect x="679.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#d1c382"/></rect>
<rect x="692.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#d1c382"/></rect>
<rect x="705.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#d1c382"/></rect>
<rect x="718.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#bbb27e"/></rect>
<rect x="731.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#bbb27e"/></rect>
<rect x="744.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#bbb27e"/></rect>
<rect x="757.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#ada67b"/></rect>
<rect x="770.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#ada67b"/></rect>
<rect x="783.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#ada67b"/></rect>
<rect x="796.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#ada67b"/></rect>
<rect x="809.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#ada67b"/></rect>
<rect x="822.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#ada67b"/></rect>
<rect x="835.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#c3b87f"/></rect>
<rect x="848.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#c3b87f"/></rect>
<rect x="861.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#c3b87f"/></rect>
<rect x="874.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#d9c983"/></rect>
<rect x="887.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#d9c983"/></rect>
<rect x="900.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#d9c983"/></rect>
<rect x="913.0" y="239.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#eeda87"/></rect>
<rect x="640.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#eeda87"/></rect>
<rect x="653.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#eeda87"/></rect>
<rect x="666.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#eeda87"/></rect>
<rect x="679.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#e0cf85"/></rect>
<rect x="692.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#e0cf85"/></rect>
<rect x="705.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#e0cf85"/></rect>
<rect x="718.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#d1c382"/></rect>
<rect x="731.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#d1c382"/></rect>
<rect x="744.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#d1c382"/></rect>
<rect x="757.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#cabd81"/></rect>
<rect x="770.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#cabd81"/></rect>
<rect x="783.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#cabd81"/></rect>
<rect x="796.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#cabd81"/></rect>
<rect x="809.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#cabd81"/></rect>
<rect x="822.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#cabd81"/></rect>
<rect x="835.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#d9c983"/></rect>
<rect x="848.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#d9c983"/></rect>
<rect x="861.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#d9c983"/></rect>
<rect x="874.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e7d586"/></rect>
<rect x="887.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e7d586"/></rect>
<rect x="900.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e7d586"/></rect>
<rect x="913.0" y="252.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#f6e089"/></rect>
<rect x="640.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#eeda87"/></rect>
<rect x="653.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0663" values="#e5e7eb;#eeda87"/></rect>
<rect x="666.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0754" values="#e5e7eb;#eeda87"/></rect>
<rect x="679.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0846" values="#e5e7eb;#e0cf85"/></rect>
<rect x="692.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0937" values="#e5e7eb;#e0cf85"/></rect>
<rect x="705.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1029" values="#e5e7eb;#e0cf85"/></rect>
<rect x="718.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#d1c382"/></rect>
<rect x="731.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#d1c382"/></rect>
<rect x="744.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1303" values="#e5e7eb;#d1c382"/></rect>
<rect x="757.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#cabd81"/></rect>
<rect x="770.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1486" values="#e5e7eb;#cabd81"/></rect>
<rect x="783.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#e5e7eb;#cabd81"/></rect>
<rect x="796.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1669" values="#e5e7eb;#cabd81"/></rect>
<rect x="809.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#cabd81"/></rect>
<rect x="822.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#e5e7eb;#cabd81"/></rect>
<rect x="835.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1943" values="#e5e7eb;#d9c983"/></rect>
<rect x="848.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2034" values="#e5e7eb;#d9c983"/></rect>
<rect x="861.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2126" values="#e5e7eb;#d9c983"/></rect>
<rect x="874.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#e7d586"/></rect>
<rect x="887.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2309" values="#e5e7eb;#e7d586"/></rect>
<rect x="900.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e7d586"/></rect>
<rect x="913.0" y="265.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#f6e089"/></rect>
<g opacity="0.18"><line x1="653.0" y1="96" x2="653.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="666.0" y1="96" x2="666.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="679.0" y1="96" x2="679.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="692.0" y1="96" x2="692.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="705.0" y1="96" x2="705.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="718.0" y1="96" x2="718.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="731.0" y1="96" x2="731.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="744.0" y1="96" x2="744.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="757.0" y1="96" x2="757.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="770.0" y1="96" x2="770.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="783.0" y1="96" x2="783.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="796.0" y1="96" x2="796.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="809.0" y1="96" x2="809.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="822.0" y1="96" x2="822.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="835.0" y1="96" x2="835.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="848.0" y1="96" x2="848.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="861.0" y1="96" x2="861.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="874.0" y1="96" x2="874.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="887.0" y1="96" x2="887.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="900.0" y1="96" x2="900.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="913.0" y1="96" x2="913.0" y2="278.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="109.0" x2="926.0" y2="109.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="122.0" x2="926.0" y2="122.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="135.0" x2="926.0" y2="135.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="148.0" x2="926.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="161.0" x2="926.0" y2="161.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="174.0" x2="926.0" y2="174.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="187.0" x2="926.0" y2="187.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="200.0" x2="926.0" y2="200.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="213.0" x2="926.0" y2="213.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="226.0" x2="926.0" y2="226.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="239.0" x2="926.0" y2="239.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="252.0" x2="926.0" y2="252.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="640" y1="265.0" x2="926.0" y2="265.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="640" y="96" width="286.0" height="182.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<rect x="835.0" y="148.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2752;0.2754;1.0000" values="0;0;1;1"/></rect>
<text x="640" y="322" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">読み込み:</text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="1">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">350<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.0661;0.0663;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">700<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0661;0.0663;0.0752;0.0754;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">1,050<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0752;0.0754;0.0843;0.0846;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">1,400<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0843;0.0846;0.0935;0.0937;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">1,750<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0935;0.0937;0.1026;0.1029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">2,100<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;0.1118;0.1120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">2,450<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1118;0.1120;0.1209;0.1211;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">2,800<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1209;0.1211;0.1301;0.1303;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">3,150<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1303;0.1392;0.1394;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">3,500<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1392;0.1394;0.1483;0.1486;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">3,850<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1483;0.1486;0.1575;0.1577;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">4,200<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1575;0.1577;0.1666;0.1669;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">4,550<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1666;0.1669;0.1758;0.1760;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">4,900<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1758;0.1760;0.1849;0.1851;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">5,250<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1849;0.1851;0.1941;0.1943;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">5,600<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2032;0.2034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">5,950<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2032;0.2034;0.2123;0.2126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">6,300<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2123;0.2126;0.2215;0.2217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">6,650<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2215;0.2217;0.2306;0.2309;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">7,000<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2306;0.2309;0.2398;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">7,350<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2398;0.2400;0.2489;0.2491;1.0000" values="0;0;1;1;0;0"/></text>
<text x="718" y="324" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043" opacity="0">7,700<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2489;0.2491;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/><rect x="646.0" y="340.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="661.0" y="340.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="676.0" y="340.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="691.0" y="340.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="706.0" y="340.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="646.0" y="355.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="661.0" y="355.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="676.0" y="355.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="691.0" y="355.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="706.0" y="355.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="646.0" y="370.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="661.0" y="370.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="676.0" y="370.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="691.0" y="370.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="706.0" y="370.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="646.0" y="385.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="661.0" y="385.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="676.0" y="385.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="691.0" y="385.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="706.0" y="385.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="646.0" y="400.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="661.0" y="400.0" width="14.0" height="14.0" fill="#334155" stroke="#94a3b8" stroke-width="1"/>
<rect x="676.0" y="400.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="691.0" y="400.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<rect x="706.0" y="400.0" width="14.0" height="14.0" fill="#fde68a" stroke="#94a3b8" stroke-width="1"/>
<text x="733.0" y="356" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">赤枠の画素:</text>
<text x="733.0" y="376" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">影 10 / 25 マス</text>
<text x="733.0" y="398" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043">= 影の濃さ 0.40</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3438;0.3440;1.0000" values="0;0;1;1"/><rect x="30" y="440" width="900" height="74" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="464" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1e3a8a">影の濃さの段階: 1 回 → 2 種類(0 か 1 だけ)/ 3×3 → 9 種類 / 5×5 → 12 種類</text>
<text x="46" y="489" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">読み込みは 1 : 9 : 25。縁のなめらかさと引き換えに、画面の全画素で テクスチャ読み込みが 9 倍・25 倍に増える</text>
</g>
<text x="30" y="528" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ荒いシャドウ マップを、3 通りの読み方で比べる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="30" y="528" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面を左から右へなぞって、各画素の影の濃さを決める<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.2581;0.2583;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="528" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縁の 1 画素の中身: 読んだ 1 マスずつの 影 / 光 を、平均する<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2581;0.2583;0.3438;0.3440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="528" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">読む範囲が広いほどなめらかだが、読み込みが増える<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3438;0.3440;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:pcf-kernel:end -->

## カーネルの大きさと見た目

<strong>PCF のぼけの幅は、カーネルの大きさで決まり、</strong>遮蔽物との距離とは無関係です。

PCF のぼけの幅は、カーネルの大きさで決まります。小さいと縁がくっきりして、エイリアシングを少し隠せます。大きいと縁が全体にぼんやりします。いずれも一定なので、接地部も遠い影も同じぼけになり、これが PCF の限界です（接触硬化は[PCSS](pcss.md)の領域です）。

現実の影は遮蔽物に近い所は鋭く、離れるほどぼける（接触硬化）ので一定のぼけは不自然です。距離に応じてぼけを変えるには、[PCSS](pcss.md)を使います。

## コスト

| 項目 | 内容 |
| --- | --- |
| サンプル数 | カーネル（N×N・点数）に比例 |
| メモリ帯域 | シャドウ マップを画素ごとに複数回読む。キャッシュに乗るかが重要（近いサンプルほど有利） |
| カスケード | カスケードごとにカーネルのテクセル数が決まる（解像度が違うのでぼけの見た目の幅がカスケードで変わる。補正が要る） |
| ブランチの活用 | 完全に日向・完全に影の領域は、少ないサンプルで済ませる（早期終了） |

### 早期終了（影の縁だけ重くする）

<strong>少ないサンプルで全部同じ結果</strong>（全部日向・全部影）なら、縁ではないのでそこで終了します。縁の画素だけ、残りのサンプルを読みます。

```hlsl
float shadow = FirstFewSamples();
if (shadow > 0.0 && shadow < 1.0) {
  shadow = AllSamples();
}
```

画面の大半は縁ではないので大幅に速くなります。ただし、ブランチの発散（隣の画素と道が分かれる）に注意します。

## PCF とバイアス

<strong>カーネルが大きい</strong>と周りのサンプルの位置が、中心から離れるので面の傾きにより、サンプルごとに面の深度が違います。中心の深度のまま比べると、傾いた面でサンプルが自己遮蔽します。

広いカーネルでのバイアスは、3 通りで対処します。サンプルごとに面の傾きで深度を補正する受け手平面バイアス（[Shadow Bias](bias/index.md)）。位置を法線方向にずらす法線オフセット。簡単ですがピーター パンニングが出る、バイアスを大きくする方法です。

広い PCF には、受け手平面バイアスがほぼ必須です。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| 簡単（比較サンプラー ＋ ループ） | ぼけが一定（接触硬化がない） |
| ハードウェア支援で速い | サンプル数 × シャドウ マップ読み込みで、重くなる |
| ブランチで縁だけ重くできる | 広いカーネルでバイアスが難しい |
| シャドウ マップの形式を選ばない（深度のみ） | サンプルが少ないと縞・ノイズ |

## よくあるミス

??? failure "深度を、フィルタ（バイリニア）してから比べて、境界で破綻する"
    <strong>比較サンプラー</strong>で比べてから補間します。

??? failure "全画素で、同じサンプル パターンを使って、縞が見える"
    画素ごとに回転（ノイズ）させます。

??? failure "広いカーネルで、受け手平面バイアスなしで、傾いた面にアクネ"
    受け手平面バイアスを入れます。

??? failure "カスケードごとに、テクセル数が同じでぼけの幅がカスケードで変わる"
    カスケードのワールド サイズで、カーネルをスケールします。

??? failure "全画素で、最大のカーネルを使って、重い"
    早期終了で縁だけを重くします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PCF ＝ <strong>周りの複数点で「影か」を比べ、その平均（日向の割合）を取る</strong>
    - [x] 比べてから平均（深度の平均は誤り）。比較サンプラーが 2×2 の PCF を行う
    - [x] 広くするには格子・ポワソン円盤。画素ごとに回転してノイズに変える
    - [x] ぼけは一定（接触硬化なし）→ PCSS
    - [x] 広いカーネルは、受け手平面バイアスが必要。早期終了で軽く

## 参考

- Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987
- Fernando, "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketches
- Microsoft Learn, "D3D11_SAMPLER_DESC"（比較フィルター）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Shadows](index.md)
- [Shadow Map Basics](shadow-map-basics/index.md)
- [Shadow Bias](bias/index.md)
- [PCSS](pcss.md)
- [AO Filtering](../ao/filtering/index.md)
