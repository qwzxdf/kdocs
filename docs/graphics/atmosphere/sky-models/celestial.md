---
title: Sun, Moon and Stars
tags:
  - 描画
---

# Sun, Moon and Stars

**空には、太陽・月・星があります**。**太陽はディスク、月はテクスチャ付きの球、星は点の集まりで描きます**。このページでは、**天体の描き方**を説明します。

!!! tip "ポイント"
    - **太陽 ＝ 明るいディスク ＋ 光の拡がり**。
    - **月 ＝ 位相（満ち欠け）を持つ球**。
    - **星 ＝ キューブマップ、または点の集まり**。
    - **昼は、星が見えない（空の明るさに負ける）**。

## 太陽・月・星
**空の主役**は**太陽**です。

### 太陽の円盤

**太陽は視線と太陽の方向の角度が小さい所だけ、非常に明るい円盤**です。**実際の太陽の見た目の大きさは、約 0.53°**（**半径 約 0.265°**）です。

```hlsl
float SunDisk(float3 view_dir, float3 sun_dir) {
  float cos_angle = dot(view_dir, sun_dir);
  float cos_radius = cos(radians(0.265));
  float edge = smoothstep(cos_radius - 0.00002, cos_radius, cos_angle);
  return edge * sun_intensity;
}
```

コードの要点です。角度は内積で比べ、`acos` を避けて `cos` の値で判定します。縁を少し滑らかにしてジャギーを防ぎます（TAA でも滑らかになります）。HDR の強度として、昼の太陽は空の 1 万倍以上明るいので、ブルームで光らせます。周りのにじみ（コロナ）は、`exp(-angle * k)` のように、指数関数的に減る光を足します。太陽を大きくしすぎると不自然なので、誇張しすぎないようにします。

### 夕焼けの色

**太陽が地平線に近づくと、光が大気を長く通る**ので、**青が散り尽くして、赤が残ります**。**太陽の色を高さに応じて変える**だけで、**夕焼けの雰囲気**が**出ます**。

```hlsl
float3 SunColor(float sun_height) {
  float t = saturate(sun_height * 4.0);
  return lerp(float3(1.0, 0.35, 0.1), float3(1.0, 0.95, 0.85), t);
}
```

**正確には大気の透過率（光学的厚さ）から求めます**（[Atmospheric Scattering](../scattering/index.md)）。

### 月と星

月と星の表現です。月は、太陽と同様に円盤で描き、満ち欠けは、太陽の向きとの角度から、球の陰影として表します。星は、HDR の星空のキューブマップを回して貼ります。空が暗いほど見え、昼の明るさで消えます。夜空の明るさとして、月明かりや星明かりを環境光に足します。星に、時間でわずかな明滅（またたき）を付けることもあります。

```hlsl
float3 stars = star_cubemap.Sample(linear_wrap, mul(view_dir, star_rotation)).rgb;
float night_factor = saturate(-sun_dir.y * 5.0);
float3 sky = day_sky + stars * night_factor;
```

## よくあるミス

??? failure "昼なのに、星が透けて見える"
    **空の明るさに応じて、星を弱める**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **太陽・月・星を、それぞれに合う方法で**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky Models](index.md)
- [Day-Night Cycle](day-night.md)
