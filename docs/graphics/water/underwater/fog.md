---
title: Underwater Fog
tags:
  - 描画
---

# Underwater Fog

**水中では、遠くほど、青緑に霞みます**。**距離に応じた指数フォグ**で**表現**でき、**水の色と深さで、霧の色を変えます**。このページでは、**水中の霧**を説明します。

!!! tip "ポイント"
    - **指数フォグ：距離が遠いほど、水の色に近づく**。
    - **水の吸収係数を使う**（赤が先に消える）。
    - **深いほど、暗くする**。
    - **水面からの光の量を、深さで減らす**。

## 水中の霧
**水中では遠くの物ほど、水の色に近づきます**。**地上のフォグと同じ構造**ですが、**吸収が色ごとに違う**のが**特徴**です。

<div class="formula">T = exp( −σ · d )　（σ：吸収係数（RGB）、d：カメラから物までの距離）</div>

```hlsl
float3 absorption = float3(0.45, 0.07, 0.03);
float3 transmittance = exp(-absorption * distance_to_pixel);
float3 scattered = water_color * (1.0 - transmittance);
float3 final_color = scene_color * transmittance + scattered;
```

| 点 | 説明 |
| --- | --- |
| **赤が先に消える** | **遠くは青緑**になる |
| **`distance_to_pixel`** | **深度から求めた、カメラからの距離**（水面を通る分も含む） |
| **水深で明るさを変える** | **深いほど暗い**（**太陽光が届かない**）。**`exp(−k · depth)`** |
| **空は水の色** | **空の部分は遠距離扱いで水の色になる** |

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="水中の霧">
<text x="20" y="24" class="fig-title">水中の霧：距離とともに、赤 → 緑 → 青の順に消える</text>
<line x1="80" y1="170" x2="720" y2="170" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="170" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="80,52 160,100 240,132 320,150 400,160 560,167 720,169"/>
<polyline fill="none" stroke="#2ea043" stroke-width="3" points="80,52 160,60 240,70 320,82 400,95 560,120 720,140"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="3" points="80,52 160,55 240,58 320,63 400,69 560,80 720,98"/>
<text x="720" y="192" text-anchor="end" style="font-size:12px">距離 d →</text>
<text x="86" y="44" style="font-size:12px">残る光の割合 T</text>
<text x="170" y="118" style="font-size:12px;fill:#e5484d">赤（すぐ消える）</text>
<text x="420" y="110" style="font-size:12px;fill:#2ea043">緑</text>
<text x="420" y="64" style="font-size:12px;fill:#4c8bf5">青（最後まで残る）</text>
</svg>

## 水中は、霧の中

水の中は、光が、**吸収と散乱**で、すぐに、減ります。**遠くの物が、見えず、色が、青緑に、染まる**様子は、**霧**（フォグ）と、同じ式で、表現できます。ただし、**色ごとに、吸収の強さが違う**点が、空気中の霧との、大きな違いです。

## 色ごとの減衰

空気中の霧は、**色に関係なく、同じ割合**で、遠くの物の色を、霧の色へ近づけます。水中では、**赤が、すぐに消え、青が、遠くまで残ります**。

```hlsl
// 水中の霧: 色（RGB）ごとに、透過率が違う。
float3 transmittance = exp(-absorption * distance_in_water);      // absorption は RGB ごとの値（1/m）
float3 color = scene_color * transmittance + water_color * (1.0 - transmittance);
```

| 距離 | 赤の残り | 緑の残り | 青の残り | 見た目 |
| --- | --- | --- | --- | --- |
| 0 m | 100% | 100% | 100% | 元の色 |
| 3 m | 26% | 81% | 91% | 赤が、ほぼ消える |
| 10 m | 1% | 50% | 74% | 青緑 |
| 30 m | 0% | 12% | 41% | 青（暗い） |

吸収係数 `(0.45, 0.07, 0.03)`（1/m）で、計算しました（[Color by Water Depth](../shading/depth-color.md)）。

空気中の霧の式（[Fog Equations](../../atmosphere/aerial-fog/fog-equation.md)）と、**形は同じ**ですが、**係数が、RGB で、違う**のが、特徴です。

## 水中の霧を、全画面で適用する

**カメラが、水の中にある**とき、**画面全体**に、霧をかけます。ポストプロセスで、**画素ごとの、距離**（深度バッファから）を、使います。

```hlsl
// ポストプロセス: カメラが水中のとき、全画面に、水中の霧をかける。
float depth = LinearizeDepth(g_depth.Sample(g_point_clamp, uv).r);
float3 view_ray = ReconstructViewDirection(uv);
float distance = depth * length(view_ray);                       // 視線方向の距離

float3 scene = g_scene.Sample(g_linear_clamp, uv).rgb;
float3 T = exp(-g_absorption * distance);
float3 color = scene * T + g_water_color * (1.0 - T);
```

| 項目 | 内容 |
| --- | --- |
| 空（深度が、最大の画素） | 空は、水の中からは、見えない（水面の向こう）。**水の色**で、塗る |
| 水面を見上げたとき | 水面の描画（[The Underside of the Surface and Crossing It](surface-back.md)）。水面より向こうの、空の描画は、別に扱う |
| 水中の、遠い物 | 距離が、大きいほど、**水の色**（`water_color`）に、近づく |

### 水の色（`water_color`）と、深さ

水中の、**水の色**は、**深くなるほど、暗く**なります。**太陽の光が、深さとともに、減る**ためです。

```hlsl
// カメラの深さに応じて、水の色を、暗くする（太陽光が、届かなくなる）。
float camera_depth_below_surface = max(water_surface_y - camera_position.y, 0.0);
float3 sun_at_camera = exp(-g_absorption * camera_depth_below_surface);
float3 water_color = g_deep_color * (0.2 + 0.8 * sun_at_camera.b);     // 青の光の、残り具合で、明るさを決める
```

| 深さ | 水の色の、明るさ |
| --- | --- |
| 水面の近く | 明るい青緑 |
| 10 m | 暗い青 |
| 50 m | ほぼ、真っ暗 |
| 200 m | 真っ暗（太陽光は、届かない） |

## 光源の、色も、変わる

水中の物を、ライティングするとき、**光が、水の中を、通ってくる**間に、吸収されます。

| 光源 | 水中での、色 |
| --- | --- |
| 太陽光 | 水面から、物までの、**深さ**に応じて、赤から、消える |
| 環境光（空の光） | 同様。**全体に、暗く、青く**なる |
| 水中の、ライト（懐中電灯、ランプ） | 光源から、物までの、**距離**に応じて、吸収される。近くでは、白く、遠くでは、青緑 |

```hlsl
// 太陽光を、水中の深さ d で減衰させる。
float3 sun_underwater = sun_color * exp(-g_absorption * depth_below_surface);
```

## 水中の、遠景の、扱い

遠くの地形や、物を描くとき、**空気中の大気（空気遠近法）は、水中では、使いません**。水中では、**水の霧**で、置き換えます。

| カメラの位置 | 使う霧 |
| --- | --- |
| 空気中 | 大気の霧（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)） |
| 水中 | 水中の霧（このページ） |
| 水面をまたぐ（半分水中、半分空気中） | 水面の高さで、**霧を、切り替える**（[The Underside of the Surface and Crossing It](surface-back.md)） |

水中では、**視界が、非常に短く**なるので、**遠景（地形のチャンク、遠くの物）の描画**は、**早めに、打ち切って**、**コストを、減らせます**。

## 濁り：吸収と、散乱

澄んだ海では、吸収が、主です。**濁った水**（泥、プランクトン）では、**散乱**が、強く、**光が、水中で、あらゆる方向に、散って、視界が、さらに短く**なり、**霧のような、もや**が見えます。

| 水の種類 | 吸収 | 散乱 | 見た目 |
| --- | --- | --- | --- |
| 澄んだ海 | 小さい（赤だけ強い） | ごく小さい | 青く、遠くまで見える |
| 湖 | 中（緑が、残る） | 中 | 緑がかった、少し、もやっとした |
| 川（濁り） | 大きい | **大きい** | **茶色の、もや**。数メートルしか、見えない |

濁った水では、`water_color` を、**明るく、不透明に近く**して、**吸収係数を、大きく**します。**霧のような見た目**になります。

## よくあるミス

??? failure "水中なのに、遠くまでくっきり見える"
    **距離フォグ**を**かける**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離と深さで、色と明るさが変わる**

## 参考

- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997
- Jerlov, "Marine Optics", Elsevier, 1976
- Gordon, Brown, Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics, Vol. 14, No. 2, 1975
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Underwater Rendering](index.md)
- [Color by Water Depth](../shading/depth-color.md)
- [Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)
