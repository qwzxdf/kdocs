---
title: 水の屈折の歪み
tags:
  - 描画
---

# 水の屈折の歪み

**水の中の景色は、水面で曲がって見えます**。**法線に応じて、既に描いた画面をずらして読む**ことで、**安く表現**できます。このページでは、**水の屈折の歪みと、水面より手前の物の扱い**を説明します。

!!! tip "ポイント"
    - **画面のコピーを、法線でずらして読む**。
    - **水面より手前の物は、ずらさない**（深度で判定）。
    - **歪みが強すぎると、不自然**。
    - **水深が浅いほど、歪みを弱める**。

## 屈折の歪み
**水面の法線は波で傾く**ので、**水中の物は歪んで見えます**。**法線の XZ 成分で背景を読む UV をずらします**。

```hlsl
float2 distortion = wave_normal.xz * distortion_strength;
float2 refract_uv = screen_uv + distortion;

float scene_depth_at_uv = LinearizeDepth(depth_texture.Sample(point_clamp, refract_uv).r);
if (scene_depth_at_uv < surface_depth) {
  refract_uv = screen_uv;
}

float3 scene_color = scene_copy.Sample(linear_clamp, refract_uv).rgb;
```

| 点 | 説明 |
| --- | --- |
| **`distortion_strength`** | **0.02 程度**。**大きすぎると不自然** |
| **深度の再確認** | **ずらした先が水面より手前（水の外にある物）なら、ずらさない**。**手前の物が水の中に引きずられて見える**失敗を防ぐ |
| **距離で弱める** | **遠くの水は歪みを減らす**（**ちらつき防止**） |
| **水深で強める** | **深いほど、歪みが大きい**（**浅い所はほとんど歪まない**） |

## よくあるミス

??? failure "岸辺の物が、水面に引き込まれて歪む"
    **深度を比べて、手前の物は除く**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **法線で画面をずらす**
    - [x] **手前の物は除く**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水の質感](index.md)
- [画面空間の屈折](../../translucency/refraction/screen-space.md)
