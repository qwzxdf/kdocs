---
title: Refraction Boundary Problems
tags:
  - 描画
---

# Refraction Boundary Problems

**画面をずらして読むと、屈折する物体より「手前にある物」まで、ずれて読んでしまう**ことがあります。**境界でにじむ**ので、**深度を見て、手前の物は除く**などの工夫が必要です。このページでは、**境界の問題と対策**を説明します。

!!! tip "ポイント"
    - **屈折する物体より手前の物が、屈折の中に混ざる**。
    - **対策：ずらした先の深度が、手前なら、ずらさない**。
    - **境界のにじみは、深度比較で防げる**。
    - **完全には直らない**ので、**見た目で許容**する。

## The Refraction Boundary Problem {#屈折の境界の問題}
**画面空間の屈折には、典型的な破綻**があります。

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **前景の物が、屈折で背景に混ざる** | **ガラスより手前にある不透明物の画素**を、**屈折で読んでしまう** | **読んだ位置の深度が、ガラスより手前なら、屈折せず元の位置を読む** |
| **画面外を読む** | **歪んだ UV が、画面の外に出る** | **クランプ・端でフェード・歪みを弱める** |
| **後ろの半透明が写らない** | **コピーは、不透明のみ** | **半透明のソート順で、コピーを取り直す**（コスト大）・**割り切る** |
| **ガラスの後ろのガラス** | **屈折物どうしが重なる** | **1 層のみ対応**と割り切る・**レイトレ** |

### Avoiding Foreground Leakage {#前景の混入を避ける}

```hlsl
float refracted_depth = LinearDepth(depth_texture.Sample(point_clamp, refract_uv).r);
float glass_depth = LinearDepth(input.position.z);
if (refracted_depth < glass_depth) {
  refract_uv = screen_uv;
}
float3 background = scene_color_copy.Sample(linear_clamp, refract_uv).rgb;
```

**屈折先の深度が、ガラスより手前**（＝**ガラスの前の物**を読んでしまう）なら、**屈折をやめて**、**元の位置**を**読みます**。

## Common Mistakes {#よくあるミス}

??? failure "ガラスの手前の物が、ガラスの中に映り込んで歪む"
    **ずらした先の深度を比較**して、**手前なら無効**にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **深度を比べて、手前の物は除く**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [Refraction](index.md)
- [Screen-Space Refraction](screen-space.md)
