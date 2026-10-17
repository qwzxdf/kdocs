---
title: 水深による色
tags:
  - 描画
---

# 水深による色

**水は、深いほど色が濃くなり、赤から先に吸収されます**。**Beer の法則（指数で減衰）**で、**この色の変化を表せます**。このページでは、**水深の求め方と、色の付け方**を説明します。

!!! tip "ポイント"
    - **透過率 ＝ exp(−吸収 × 水深)**。
    - **水深 ＝ シーンの深度 − 水面の深度**。
    - **赤の吸収が強い**ので、**深いと青緑**になる。
    - **浅い所は透けて、底の色が見える**。

## 水深による色（Beer の法則）
**光が水の中を距離 d だけ進むと、強さは指数関数的に減ります**（**Beer–Lambert の法則**）。**吸収の強さは色（波長）ごとに違い**、**水は赤を強く吸収し、青をあまり吸収しません**。**そのため、深くなるほど青緑に変わります**。

<div class="formula">透過率 T = exp( −σ · d )　（σ：色ごとの吸収係数、d：水中を通った距離）</div>

| 記号 | 意味 |
| --- | --- |
| <strong>σ（RGB）</strong> | **吸収係数**。**水は赤が大きく、青が小さい**（例：(0.45, 0.07, 0.03) /m） |
| **d** | **光が水中を通った距離** |
| **T** | **残る光の割合**。**色ごとに違う** |

```hlsl
float3 absorption = float3(0.45, 0.07, 0.03);
float3 transmittance = exp(-absorption * water_depth);
float3 refracted_color = scene_color * transmittance + deep_color * (1.0 - transmittance);
```

| 点 | 説明 |
| --- | --- |
| **`scene_color * transmittance`** | **底の色が水を通って減った分** |
| **`deep_color * (1 − T)`** | **減った分を水自身の色で置き換える<strong>（</strong>散乱で光る水の色**） |
| **浅い所** | **T ≈ 1**。**底がはっきり見える** |
| **深い所** | **T ≈ 0**。**水自身の色（深い青）だけ** |

### 水深の求め方

**水深**は**不透明な物の深度（水の後ろにある底）と、水面の深度の差**です（[屈折](../../translucency/refraction/index.md)）。

```hlsl
float scene_depth = LinearizeDepth(depth_texture.Sample(point_clamp, screen_uv).r);
float surface_depth = LinearizeDepth(input.position.z);
float water_depth = max(scene_depth - surface_depth, 0.0);
```

| 注意 | 内容 |
| --- | --- |
| **視線方向の距離** | **深度の差は視線に沿った距離ではなく、カメラの前方（Z）方向の差**。**斜めから見るほど、実際の水中の距離は長い**ので、**`/ dot(V, 前方)`** のような補正をすることもある |
| **ワールド座標で求める** | **底のワールド位置を再構築し、水面との距離を直接測る**ほうが**正確** |
| **垂直の水深** | **泡や岸辺の判定には、垂直方向の深さ**（ワールドの Y の差）を使う |

## よくあるミス

??? failure "深い所も浅い所も、同じ水色"
    **水深から、透過率を計算**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **深いほど、指数で濃くなる**
    - [x] **赤から先に消える**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水の質感](index.md)
- [厚みと色](../../translucency/refraction/thickness-color.md)
- [色のパラメータ](parameters.md)
