---
title: モーフィング
tags:
  - 描画
---

# モーフィング

**LOD が切り替わる時、頂点が突然動くと、ポップが見えます**。**切り替えの手前で、頂点を少しずつ、粗い LOD の位置へ動かす（モーフィング）**ことで、**なめらかに**なります。このページでは、**モーフィングの仕組み**を説明します。

!!! tip "ポイント"
    - **LOD の境界の手前で、モーフ係数を 0 → 1 に動かす**。
    - **頂点を、粗い LOD の位置へ補間する**。
    - **頂点シェーダーで計算**できる。
    - **切り替え時には、粗い LOD と一致しているので、ポップしない**。

## モーフィング
<strong>LOD が切り替わる瞬間に、地形の形が急に変わると「ポップ」</strong>が見えます。**モーフィング**は、**切り替わる手前から、細かい側の頂点を粗い側の位置へ滑らかに寄せる**手法です。

**粗い LOD では、頂点が 1 つおきに間引かれる**ので、**間引かれる側の頂点を両隣の頂点の中点へ寄せます**。

<div class="formula">位置 = lerp( 自分の高さ,　両隣の平均の高さ,　morph )　（morph：0 → 1）</div>

```hlsl
float MorphFactor(float distance_to_camera, float range_start, float range_end) {
  float t = (distance_to_camera - range_start) / (range_end - range_start);
  return saturate((t - 0.7) / 0.3);
}

float2 MorphXZ(float2 grid_position, float morph) {
  float2 fraction = frac(grid_position * (kGridSize * 0.5)) * 2.0 / kGridSize;
  return grid_position - fraction * morph;
}

float2 xz = MorphXZ(input.grid_position, morph) * node_size + node_origin;
float height = SampleHeight(xz);
```

| 点 | 説明 |
| --- | --- |
| **`morph` の範囲** | **LOD の距離範囲の最後の 30 %** で**0 → 1**。**範囲の前半はそのまま** |
| **奇数番の頂点を寄せる** | **粗い LOD に存在しない頂点が、偶数番の頂点の位置に重なる** |
| **効果** | **切り替え時に形が同じ**になり、**ポップが消える** |
| **高さも補間** | **XZ を寄せたうえで高さを読み直す** |

## よくあるミス

??? failure "LOD の切り替わりで、地形がポップする"
    **モーフィング**を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **切り替えの手前で、粗い位置へ寄せる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形の LOD](index.md)
- [CDLOD](cdlod.md)
