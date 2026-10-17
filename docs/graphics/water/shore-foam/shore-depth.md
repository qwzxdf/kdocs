---
title: 岸辺の泡：深度差
tags:
  - 描画
---

# 岸辺の泡：深度差

**岸辺は、水面とシーンの深度の差が小さい所**です。**この差から、泡のマスクを作る**と、**岸や物の境界に、自然に泡が出ます**。このページでは、**深度差を使った泡**を説明します。

!!! tip "ポイント"
    - **深度差 ＝ シーンの深度 − 水面の深度**。
    - **差が小さいほど、泡が濃い**。
    - **波で、泡の幅を揺らす**と、自然。
    - **ソフト パーティクルと同じ発想**。

## 岸辺の泡：深度差
**水面と底の深度の差が小さい所は、水が浅い所**＝**岸辺や水中の物の周り**です。**浅いほど泡が強くなるマスク**を作ります。

```hlsl
float scene_depth = LinearizeDepth(depth_texture.Sample(point_clamp, screen_uv).r);
float surface_depth = LinearizeDepth(input.position.z);
float water_depth = max(scene_depth - surface_depth, 0.0);

float shore_mask = 1.0 - saturate(water_depth / foam_distance);
shore_mask = pow(shore_mask, foam_sharpness);
```

| 点 | 説明 |
| --- | --- |
| **`foam_distance`** | **泡が出る水深の範囲**（例：0.5 m）。**これより深いと 0** |
| **`pow(..., sharpness)`** | **端の鋭さ**。**大きいと岸のすぐそばだけ** |
| **水中の物にも出る** | **岩・杭・船の周りにも泡の輪**ができる（**深度差で自動的に**） |

### 波打ち際の動き

**岸辺の泡は波が寄せては引くように動く**と**自然**です。**水深に時間で揺れる値を足す**と**波打ち際が動きます**。

```hlsl
float wave = sin(time * 1.5 + input.world_position.x * 0.3) * 0.5 + 0.5;
float animated_depth = water_depth + wave * 0.3;
float shore_mask = 1.0 - saturate(animated_depth / foam_distance);
```

**波が寄せる位相と引く位相で泡の線が前後します**。**位置（`world_position.x`）で位相をずらす**と**波が一斉に動かず、ばらけます**。

## よくあるミス

??? failure "泡が、岸の形に沿った一定の線になる"
    **ノイズや波で、境界を揺らす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **深度差が小さい所に、泡**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [岸辺の泡](index.md)
- [ソフト パーティクル](../../translucency/blending-sorting/soft-particles.md)
