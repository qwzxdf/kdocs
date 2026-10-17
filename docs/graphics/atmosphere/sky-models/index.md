---
title: Sky Models
tags:
  - 描画
---

# Sky Models

**空は、背景として、画面の大きな面積を占め、シーンの雰囲気を決めます**。**単純なグラデーションから、物理に基づく計算まで、方法がいくつかあります**。このセクションでは、**空の描き方・グラデーション・解析的なモデル・太陽と月と星・空をライティングに使う・昼夜のサイクル**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **空 ＝ 背景。画面の大部分を占める**。
    - **簡単な方法はグラデーション、物理的な方法は大気散乱**。
    - **空の色は、ライティング（環境光）にも使う**。
    - **昼夜のサイクルで、空・光・影が連動する**。

## 空の描き方
**空はワールドの一番遠くにある背景**です。**描き方は 2 通り**あります。

空の描き方は 2 通りあります。スカイボックスは、キューブマップ（6 枚の絵）を貼った箱を、カメラ中心に描きます。全画面で計算する方式は、画面の各ピクセルから視線の向きを求め、その向きの色を計算します。

**スカイボックスは絵が固定**ですが、**全画面計算は時刻や天気に応じて色を変えられます**。

### 視線の向きを求める

**ピクセルごとの視線の向きは、逆射影行列で作ります**。

```hlsl
float3 ViewDirection(float2 uv) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  float4 clip = float4(ndc, 1.0, 1.0);
  float4 world = mul(clip, inverse_view_projection);
  return normalize(world.xyz / world.w - camera_position);
}
```

コードの要点です。クリップ空間の Z = 1 は最も遠い面です（リバース Z なら 0）。`mul(行ベクトル, 行列)` は、行ベクトル規約（`v * M`）に従います。カメラ位置を引いて、ワールド位置から方向を求めます。

### 深度テストで最奥だけに描く

**空は他の物を描いた後で深度が最奥のピクセルだけ**を**塗ります**（**描画量が減る**）。

空は、他の物を描いた後に、深度が最奥のピクセルだけを塗ると、描画量が減ります。方法は 2 つあります。フル スクリーン三角形を Z = 1（最奥）で描き、深度テストの比較を `LESS_EQUAL` にする方法。不透明物の後で半透明の前に描くことで、早期 Z により、物があるピクセルを省略する方法です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Gradient Sky](gradient.md) | 最も簡単な空 |
| [Analytic Sky Models](analytic.md) | Preetham・Hosek-Wilkie |
| [Sun, Moon and Stars](celestial.md) | 天体の描き方 |
| [Using the Sky for Lighting](sky-lighting.md) | 環境光・IBL |
| [Day-Night Cycle](day-night.md) | 時間による変化 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **空は、背景であり、ライティングの源**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気](../index.md)
- [Atmospheric Scattering](../scattering/index.md)
- [Clouds](../clouds/index.md)
