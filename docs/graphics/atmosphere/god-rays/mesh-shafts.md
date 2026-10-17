---
title: Light Shaft Meshes
tags:
  - 描画
---

# Light Shaft Meshes

**窓から差し込む光など、位置が決まっている光の筋は、半透明のメッシュ（光の柱）で作る**と、**最も軽く済みます**。このページでは、**メッシュによる光の柱**を説明します。

!!! tip "ポイント"
    - **加算ブレンドの、細長いメッシュ**を置く。
    - **縁と端を、フェードさせる**。
    - **カメラに近づくと、フェードで消す**。
    - **動かない光に、最適**。

## メッシュで光の柱を作る
<strong>固定された光の柱（窓から差す光、洞窟の天井の穴）</strong>は、**半透明メッシュ**で**作れます**。

| 工夫 | 内容 |
| --- | --- |
| **形** | **光が通る形の錐台や箱のメッシュ** |
| **加算ブレンド** | **背景に足して光らせる** |
| **フレネル風の縁** | **視線と面の角度で縁を薄く**（輪郭を消す） |
| **深度フェード** | **床・壁との交差部を薄く**（ハードな線を消す） |
| **ノイズ・流れ** | **テクスチャを流して、ほこりの揺らぎ** |
| **カメラが近づくと薄く** | **近すぎるとフェードアウト** |

```hlsl
float edge_fade = pow(saturate(abs(dot(normal, view_dir))), 2.0);
float depth_fade = saturate((scene_depth - pixel_depth) / fade_distance);
float near_fade = saturate((pixel_depth - near_fade_start) / near_fade_range);
float dust = dust_texture.Sample(linear_wrap, uv + time * 0.02).r;
float alpha = edge_fade * depth_fade * near_fade * (0.7 + 0.3 * dust) * intensity;
return float4(light_color * alpha, 0);
```

## よくあるミス

??? failure "メッシュの縁が硬く、板に見える"
    **縁をフェード**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **加算メッシュで、手軽に光の柱**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [God Rays](index.md)
- [Blend State](../../translucency/blending-sorting/blend-state.md)
