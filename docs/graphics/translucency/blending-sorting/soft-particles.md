---
title: ソフト パーティクル
tags:
  - 描画
---

# ソフト パーティクル

**パーティクルが地面や壁と交差する所で、硬い線が見えて、不自然**になります。**シーンの深度を読んで、近いほどアルファを弱める「ソフト パーティクル」**で、**なめらかに消せます**。このページでは、**ソフト パーティクルの仕組み**を説明します。

!!! tip "ポイント"
    - **パーティクルの深度と、シーンの深度の差を求める**。
    - **差が小さい（交差に近い）ほど、アルファを弱める**。
    - **深度バッファを、テクスチャとして読む**必要がある。
    - **煙・炎・霧のパーティクルで、効果が大きい**。

## 深度の読み取り（ソフト パーティクル）
**パーティクルの板**が、**地面や壁と交差する所で、硬い線**が出ます。**シーンの深度を読んで、近いほど透明にする**と、**なじみます**（**ソフト パーティクル**）。

```hlsl
float scene_depth = LinearDepth(depth_texture.Load(int3(input.position.xy, 0)).r);
float particle_depth = LinearDepth(input.position.z);
float fade = saturate((scene_depth - particle_depth) / fade_distance);
color.a *= fade;
```

| 点 | 説明 |
| --- | --- |
| **`scene_depth`** | **不透明な物の深度**（深度バッファを SRV として読む） |
| **`particle_depth`** | **パーティクル自身の深度** |
| **`fade_distance`** | **この距離で、完全に不透明に** |
| **要件** | **深度バッファを、読み取りと深度テストで、同時に使えない**ので、**深度のコピー**（または読み取り専用 DSV）が要る |

## よくあるミス

??? failure "煙が地面と交差して、硬い線が出る"
    **ソフト パーティクル**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **深度の差でアルファを弱める**
    - [x] **交差の硬い線が消える**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [アルファ ブレンドとソート](index.md)
- [ソート](sorting.md)
