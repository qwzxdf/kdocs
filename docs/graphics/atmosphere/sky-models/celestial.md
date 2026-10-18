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

| 点 | 説明 |
| --- | --- |
| **角度を内積で** | **`acos` を避け、`cos` の値で比べる** |
| **縁を少し滑らかに** | **ジャギーを防ぐ**（**TAA で滑らかになる**） |
| **HDR の強度** | **昼の太陽は空の 1 万倍以上明るい**。**ブルームが光る** |
| <strong>周りのにじみ（コロナ）</strong> | **指数関数的に減る光を足す**：`exp(-angle * k)` |
| **大きすぎる太陽は不自然** | **誇張しすぎない** |

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

| 要素 | 内容 |
| --- | --- |
| **月** | **太陽と同様に円盤**。**月の満ち欠けは、太陽の向きとの角度から、球の陰影で表す** |
| **星** | <strong>星空のキューブマップ（HDR）</strong>を**回して貼る**。**空が暗いほど見える**（**昼の明るさで消える**） |
| **夜空の明るさ** | **月明かり・星明かりを環境光に足す** |
| **またたき** | **星に時間でわずかな明滅** |

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
