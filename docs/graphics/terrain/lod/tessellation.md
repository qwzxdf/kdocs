---
title: Hardware Tessellation
tags:
  - 描画
---

# Hardware Tessellation

**GPU のテッセレーションで、パッチを、距離に応じて細かく分割**できます。**メッシュの管理が楽で、細かさを連続的に変えられます**。このページでは、**テッセレーションによる地形の LOD**を説明します。

!!! tip "ポイント"
    - **ハル・ドメイン シェーダーで、パッチを分割**。
    - **距離に応じて、分割数を決める**。
    - **隣のパッチと、境界の分割数を揃える**。
    - **対応していない環境もある**。

## ハードウェア テッセレーション
**DX11 のテッセレーション**は、**ハル シェーダー・ドメイン シェーダー**で**パッチ（四角形）を、GPU 内で細分**します。**地形ではパッチ（例：64×64 m）を渡し、距離に応じた細分数を決めます**。

| ステージ | 役割 |
| --- | --- |
| **ハル シェーダー** | **パッチの 4 辺と内側の、細分係数**を決める（**距離から**） |
| **固定機能のテッセレータ** | **係数に従い、パッチを細分** |
| **ドメイン シェーダー** | **細分された点の位置を計算し、高さマップを読んで持ち上げる** |

```hlsl
HullConstants ComputeConstants(InputPatch<ControlPoint, 4> patch) {
  HullConstants output;
  float3 center = (patch[0].position + patch[1].position + patch[2].position + patch[3].position) * 0.25;
  float distance_to_camera = distance(center, camera_position);
  float factor = clamp(max_tessellation * (1.0 - distance_to_camera / far_distance), 1.0, max_tessellation);
  output.edge[0] = output.edge[1] = output.edge[2] = output.edge[3] = factor;
  output.inside[0] = output.inside[1] = factor;
  return output;
}
```

| 点 | 説明 |
| --- | --- |
| **辺の係数を隣と揃える** | **隣り合うパッチが共有する辺で同じ係数**を使う（**クラックを防ぐ**）。**辺の中心の距離から計算**する |
| **係数は 1〜64** | **係数を上げすぎると小さな三角形が増えて遅い** |
| **カリング** | **ハル シェーダーで画面外のパッチは係数 0 にして捨てる** |
| **利点** | **メッシュの管理が不要**。**連続的に細かさが変わる** |
| **欠点** | **三角形が小さすぎると非効率**。**GPU によっては、テッセレーションが遅い** |

**近年はコンピュート シェーダーで四分木を選び、メッシュ シェーダーで描く**構成も**増えています**。

## よくあるミス

??? failure "パッチの境目に、隙間が見える"
    **境界の分割数を、隣と揃える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **GPU で、距離に応じて分割**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain LOD](index.md)
- [CDLOD](cdlod.md)
