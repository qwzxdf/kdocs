---
title: Dispersion
tags:
  - 描画
---

# Dispersion

**光の波長ごとに屈折率が違うため、ガラスの縁で、色が分かれて見える**ことがあります。**赤・緑・青で、ずらす量を変える**と、**この効果を作れます**。このページでは、**分散の表現**を説明します。

!!! tip "ポイント"
    - **波長ごとに屈折率が違う ＝ 分散**。
    - **R・G・B で、ずらす量を変えて、3 回読む**。
    - **宝石・プリズムなど、強い分散の物体に効果的**。
    - **やりすぎない**（普通のガラスは、ほぼ目立たない）。

## 色収差（分散）
**波長ごとに屈折率が少し違う**ので、**ガラスの縁で、色がずれて見えます**（**プリズムの虹**）。**R・G・B で、屈折の強さを少しずつ変えて、3 回サンプル**します。

```hlsl
float3 background;
background.r = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.00).r;
background.g = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.03).g;
background.b = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.06).b;
```

**わずか（数%）の差**で**十分**です。**宝石・水晶・厚いガラス**で**効果的**です。

## よくあるミス

??? failure "すべてのガラスに強い色収差を付けて、安っぽくなる"
    **宝石など、分散が目立つ物だけに使う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **R・G・B で、ずらす量を変える**
    - [x] **控えめに使う**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Refraction](index.md)
- [色収差（レンズ）](../../postprocess/lens-effects/index.md)
