---
title: Underwater Rendering
tags:
  - 描画
---

# Underwater Rendering

<strong>水の中に入ると、景色が青く霞み、光の筋が差し、水面が天井のように見えます</strong>。<strong>水中かどうかを判定し、霧・コースティクス・光の筋・水面の裏側を切り替える</strong>のが基本です。このセクションでは、水中の判定・霧・コースティクス・光の筋・水面の裏側・水面をまたぐ処理・他の要素を 1 つずつ別のページで説明します。

## 水中かどうかを決める
<strong>カメラが水面より下か</strong>を<strong>判定</strong>します。

```hlsl
bool underwater = camera_position.y < WaterHeightAt(camera_position.xz, time);
```

水中の判定のコードの要点です。波の高さを含め、平均水位でなく、そこの水面の高さで判定します。水中なら、水中のフォグと色補正をポストプロセスで切り替えます。水中から見る水面は、裏面を描きます（カリングを切るか、裏面用のシェーダーを使います）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Underwater Fog](fog.md) | 距離で青く霞む |
| [Caustics](caustics.md) | 底に揺れる光の模様 |
| [Underwater God Rays](god-rays.md) | 水中のゴッド レイ |
| [The Underside of the Surface and Crossing It](surface-back.md) | 水面の見え方・切り替え |
| [Other Underwater Elements](other.md) | 粒子・音・色補正 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 水中は、霧・コースティクス・光の筋で作る

## 参考

- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）

## 関連ページ

- [Water](../index.md)
- [Water Shading](../shading/index.md)
- [God Rays](../../atmosphere/god-rays/index.md)
