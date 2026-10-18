---
title: Water Refraction Distortion
tags:
  - 描画
---

# Water Refraction Distortion

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

コードの要点です。`distortion_strength` は 0.02 程度で、大きすぎると不自然になります。深度の再確認として、ずらした先が水面より手前（水の外にある物）なら、ずらしません。手前の物が水の中に引きずられて見える失敗を防ぎます。遠くの水は歪みを減らして、ちらつきを防ぎます。水深で強める処理もあり、深いほど歪みが大きく、浅い所はほとんど歪みません。

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

- [Water Shading](index.md)
- [Screen-Space Refraction](../../translucency/refraction/screen-space.md)
