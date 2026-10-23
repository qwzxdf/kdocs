---
title: Underwater Fog
tags:
  - 描画
---

# Underwater Fog

<strong>水中では遠くほど青緑に霞みます</strong>。距離に応じた指数フォグで表現でき、水の色と深さで霧の色を変えます。このページでは水中の霧を説明します。

!!! tip "ポイント"
    - 指数フォグ：距離が遠いほど、水の色に近づく。
    - 水の吸収係数を使う（赤が先に消える）。
    - 深いほど暗くする。
    - 水面からの光の量を、深さで減らす。

!!! info "このページを読む前に"
    - [Underwater Rendering](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 水中の霧
<strong>水中では遠くの物ほど水の色に近づきます</strong>。地上のフォグと同じ構造ですが、吸収が色ごとに違うのが特徴です。

<div class="formula">T = exp( −σ · d )　（σ：吸収係数（RGB）、d：カメラから物までの距離）</div>

```hlsl
float3 absorption = float3(0.45, 0.07, 0.03);
float3 transmittance = exp(-absorption * distance_to_pixel);
float3 scattered = water_color * (1.0 - transmittance);
float3 final_color = scene_color * transmittance + scattered;
```

| 点 | 説明 |
| --- | --- |
| 赤が先に消える | 遠くは青緑になる |
| `distance_to_pixel` | 深度から求めたカメラからの距離（水面を通る分も含む） |
| 水深で明るさを変える | 深いほど暗い（太陽光が届かない）。`exp(−k · depth)` |
| 空は水の色 | 空の部分は遠距離扱いで水の色になる |

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

## 水中は霧の中

水の中は光が <strong>吸収と散乱</strong>ですぐに、減ります。遠くの物が見えず色が青緑に、染まる様子は霧（フォグ）と、同じ式で表現できます。ただし、色ごとに吸収の強さが違う点が、空気中の霧との大きな違いです。

## 色ごとの減衰

空気中の霧は <strong>色に関係なく同じ割合</strong>で、遠くの物の色を霧の色へ近づけます。水中では 赤がすぐに消え青が、遠くまで残ります。

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

吸収係数 `(0.45, 0.07, 0.03)`（1/m）で計算しました（[Color by Water Depth](../shading/depth-color.md)）。

空気中の霧の式（[Fog Equations](../../atmosphere/aerial-fog/fog-equation.md)）と、形は同じですが 係数が RGB で、違うのが特徴です。

## 水中の霧を全画面で適用する

<strong>カメラが水の中にある</strong>とき、画面全体に霧をかけます。ポストプロセスで画素ごとの距離（深度バッファから）を、使います。

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
| 空（深度が最大の画素） | 空は、水の中からは見えない（水面の向こう）。水の色で塗る |
| 水面を見上げたとき | 水面の描画（[The Underside of the Surface and Crossing It](surface-back.md)）。水面より向こうの空の描画は別に扱う |
| 水中の遠い物 | 距離が、大きいほど水の色（`water_color`）に近づく |

### 水の色（`water_color`）と深さ

水中の 水の色は 深くなるほど、暗くなります。太陽の光が深さとともに減るためです。

```hlsl
// カメラの深さに応じて、水の色を、暗くする（太陽光が、届かなくなる）。
float camera_depth_below_surface = max(water_surface_y - camera_position.y, 0.0);
float3 sun_at_camera = exp(-g_absorption * camera_depth_below_surface);
float3 water_color = g_deep_color * (0.2 + 0.8 * sun_at_camera.b);     // 青の光の、残り具合で、明るさを決める
```

| 深さ | 水の色の明るさ |
| --- | --- |
| 水面の近く | 明るい青緑 |
| 10 m | 暗い青 |
| 50 m | ほぼ真っ暗 |
| 200 m | 真っ暗（太陽光は、届かない） |

## 光源の色も変わる

水中の物をライティングするとき <strong>光が、水の中を通ってくる</strong>間に吸収されます。

| 光源 | 水中での色 |
| --- | --- |
| 太陽光 | 水面から物までの、深さに応じて赤から消える |
| 環境光（空の光） | 同様。全体に暗く青くなる |
| 水中のライト（懐中電灯、ランプ） | 光源から物までの、距離に応じて吸収される。近くでは白く遠くでは青緑 |

```hlsl
// 太陽光を、水中の深さ d で減衰させる。
float3 sun_underwater = sun_color * exp(-g_absorption * depth_below_surface);
```

## 水中の遠景の扱い

遠くの地形や物を描くとき <strong>空気中の大気（空気遠近法）は、水中では使いません</strong>。水中では 水の霧で置き換えます。

| カメラの位置 | 使う霧 |
| --- | --- |
| 空気中 | 大気の霧（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)） |
| 水中 | 水中の霧（このページ） |
| 水面をまたぐ（半分水中、半分空気中） | 水面の高さで霧を、切り替える（[The Underside of the Surface and Crossing It](surface-back.md)） |

水中では 視界が短くなるので、遠景（地形のチャンク、遠くの物）の描画は早めに打ち切って、コストを減らせます。

## 濁り：吸収と散乱

澄んだ海では吸収が主です。<strong>濁った水</strong>（泥、プランクトン）では 散乱が強く光が水中で、あらゆる方向に散って視界がさらに短くなり、霧のようなもやが見えます。

| 水の種類 | 吸収 | 散乱 | 見た目 |
| --- | --- | --- | --- |
| 澄んだ海 | 小さい（赤だけ強い） | ごく小さい | 青く、遠くまで見える |
| 湖 | 中（緑が残る） | 中 | 緑がかった少し、もやっとした |
| 川（濁り） | 大きい | 大きい | 茶色のもや。数メートルしか見えない |

濁った水では `water_color` を 明るく不透明に近くして、吸収係数を大きくします。霧のような見た目になります。

## よくあるミス

??? failure "水中なのに、遠くまでくっきり見える"
    <strong>距離フォグ</strong>をかける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 距離と深さで、色と明るさが変わる

## 参考

- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997
- Jerlov, "Marine Optics", Elsevier, 1976
- Gordon, Brown, Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics, Vol. 14, No. 2, 1975
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Underwater Rendering](index.md)
- [Color by Water Depth](../shading/depth-color.md)
- [Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)
