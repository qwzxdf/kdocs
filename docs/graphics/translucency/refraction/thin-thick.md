---
title: Thin and Thick Glass
tags:
  - 描画
---

# Thin and Thick Glass

**窓ガラスのような「薄いガラス」は、屈折でほとんどずれません**が、**ガラスの塊のような「厚いガラス」は、大きくずれます**。**両者で、モデルを使い分ける**と、**無駄なく、自然に見えます**。このページでは、**使い分けの基準**を説明します。

!!! tip "ポイント"
    - **薄いガラス：ほぼ透明 ＋ 反射。屈折はほぼ無視**。
    - **厚いガラス：屈折 ＋ 厚みによる色**。
    - **球体・瓶などは、前面と背面の 2 回の屈折**。
    - **使い分けで、コストを抑える**。

## Thin Glass and Thick Glass {#薄いガラスと厚いガラス}
| 種類 | 例 | 屈折 | 表現 |
| --- | --- | --- | --- |
| <strong>薄いガラス（板）</strong> | **窓・ガラス戸** | **ほぼ無視**（**入口と出口で相殺**） | <strong>透過 ＋ 反射（フレネル）</strong> のみ |
| **厚いガラス・水** | **瓶・水槽・宝石** | **目立つ** | **屈折 ＋ 厚みの色 ＋ 反射** |
| **曇りガラス** | **すりガラス** | **ぼやける** | **背景を、ミップや大きなブラーで読む**（粗さに応じて） |

**窓ガラス**は、**屈折を省いて、単純な半透明**にすれば**十分**です。

### Frosted Glass (Rough Refraction) {#曇りガラス粗い屈折}

**粗い面ほど、背景がぼやけて見える**ので、<strong>背景コピーのミップ（ブラー済み）</strong>を、**粗さに応じて**読みます。

```hlsl
float mip = roughness * kMaxMip;
float3 background = scene_color_mips.SampleLevel(linear_clamp, refract_uv, mip).rgb;
```

**背景のコピーに、ミップ チェーンを作って**おく（[ブルームのダウンサンプル](../../postprocess/bloom/index.md)と同様）。

### Why Refraction of Thin Glass Can Be Ignored {#なぜ薄いガラスの屈折は無視できるのか}

ガラス板に斜めから光が入ると、入口で曲がり、ガラス内を直進して、出口で逆向きに同じだけ曲がります。出た光は、入る前と平行で、ずれるだけです。そのずれは、板の厚みに比例し、薄い板ならわずかです。そのため、窓ガラスの向こうの景色は、ほぼそのまま見えます。厚いガラスや水では、ずれが大きく、曲面なら像が拡大・縮小・反転するので、屈折の表現が必要になります。

## Common Mistakes {#よくあるミス}

??? failure "窓ガラスに、強い屈折を付けて、景色が歪みすぎる"
    **薄いガラスは、屈折を弱める**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **薄い → 屈折ほぼ無し、厚い → 屈折 ＋ 色**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [Refraction](index.md)
- [Thickness and Color](thickness-color.md)
