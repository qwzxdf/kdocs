---
title: 踏まれる草
tags:
  - 描画
---

# 踏まれる草

**キャラクターが通ると、草が倒れる**と、**インタラクティブ**になります。**キャラクターの位置を、テクスチャに書き込み、草が読む**ことで**実現**します。このページでは、**踏まれる草**を説明します。

!!! tip "ポイント"
    - **キャラクターの位置を、インタラクション マップに描く**。
    - **草は、マップを読んで、倒れる**。
    - **時間とともに、ゆっくり戻る**。
    - **範囲は、カメラの周りに限る**。

## 踏まれる草
**キャラクターが歩くと草が倒れる**表現です。**キャラクターの位置をシェーダーに渡し、近い草を押しのけます**。

```hlsl
float3 away = world_position - character_position;
float influence = saturate(1.0 - length(away.xz) / push_radius);
world_position.xz += normalize(away.xz) * influence * push_strength * height_t;
world_position.y -= influence * push_strength * height_t;
```

**複数の物を扱うなら、物の位置を高さマップ風のテクスチャに描き、それを草が読む**（[波紋のブラシ](../../water/interaction/index.md)と同じ）のが**スケールします**。

## よくあるミス

??? failure "草が、倒れたまま戻らない"
    **マップを、徐々に薄める**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **位置をマップに描き、草が読む**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [植生](index.md)
- [風](wind.md)
