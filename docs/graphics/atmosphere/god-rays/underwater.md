---
title: God Rays in Air and Water
tags:
  - 描画
---

# God Rays in Air and Water

空気中のゴッド レイの作り方（[God Rays](index.md)）は、水中でもほとんどそのまま使えます。違うのは、光の色と減衰、光の向き、波による揺れの 3 点だけです。このページは、空気中との違いを整理して、色と減衰のコードを示します。水中の光の筋の作り方（放射状ブラー・シャドウ マップのレイマーチ・メッシュ）は、水のセクションの[Underwater God Rays](../../water/underwater/god-rays.md)にまとめています。

!!! tip "ポイント"
    - 水中は赤から先に吸収されるので、光の筋は青緑になります。
    - 光は 2 回減衰します。太陽から点まで、点からカメラまでです。どちらも Beer の法則です。
    - 水面で屈折するので、光は真下に近い向きになります（最大でも約 48.6°）。
    - 作り方の詳細は[Underwater God Rays](../../water/underwater/god-rays.md)にあります。

!!! info "このページを読む前に"
    - [God Rays](index.md)（このセクション全体の地図と読む順番）

## 空気中との違い

| 項目 | 空気中 | 水中 |
| --- | --- | --- |
| 光の色 | 太陽の色（白、橙） | 青緑（赤が吸収される） |
| 減衰 | ゆるやか（数 km） | 急（数十 m で、消える） |
| 光の筋の揺れ | ほぼ無し（霧のゆらぎ） | 波による強い揺れ（コースティクス） |
| 光の向き | 太陽の方向 | 水面で、屈折して真下に近づく（最大で、約 48.6°） |
| 見える距離 | 長い | 短い（水の濁りで、数 m〜数十 m） |

## 色と減衰

<strong>水中の光の筋の色</strong>は 水面から、そこまでの深さに応じて赤から順に吸収されます。浅い所は明るい青緑、深くなるほど暗い青です。

```hlsl
// 水中の光の筋: 水面からの深さと、カメラまでの距離の、両方で、減衰させる。
float3 UnderwaterSunColor(float depth_below_surface, float distance_to_camera) {
  float3 sun_at_depth = g_sun_color * exp(-g_absorption * depth_below_surface);       // 水面 → この点（太陽の光）
  float3 to_camera = exp(-g_absorption * distance_to_camera);                          // この点 → カメラ（散乱した光）
  return sun_at_depth * to_camera;
}
```

2 回の減衰（太陽 → 点、点 → カメラ）が両方、効きます。どちらも、Beer の法則です。深く遠い光の筋はほぼ見えません。

## よくあるミス

??? failure "水中の光の筋が空気中と同じ色に見える"
    吸収を入れていません。`exp(-g_absorption * 距離)` を、太陽から点まで、点からカメラまでの両方に掛けます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空気中との違いは、色と減衰・光の向き・波の揺れ

## 参考

- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [God Rays](index.md)
- [Underwater God Rays](../../water/underwater/god-rays.md)
