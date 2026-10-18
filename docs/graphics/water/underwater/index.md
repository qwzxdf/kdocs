---
title: Underwater Rendering
tags:
  - 描画
---

# Underwater Rendering

**水の中に入ると、景色が青く霞み、光の筋が差し、水面が天井のように見えます**。**水中かどうかを判定し、霧・コースティクス・光の筋・水面の裏側を切り替える**のが**基本**です。このセクションでは、**水中の判定・霧・コースティクス・光の筋・水面の裏側・水面をまたぐ処理・他の要素**を、**1 つずつ別のページ**で説明します。

## 水中かどうかを決める
**カメラが水面より下か**を**判定**します。

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
    - [x] **水中は、霧・コースティクス・光の筋で作る**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water](../index.md)
- [Water Shading](../shading/index.md)
- [God Rays](../../atmosphere/god-rays/index.md)
