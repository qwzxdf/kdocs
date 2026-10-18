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

テッセレーションのステージの役割です。ハル シェーダーは、パッチの 4 辺と内側の細分係数を決めます（距離から）。固定機能のテッセレータは、係数に従ってパッチを細分します。ドメイン シェーダーは、細分された点の位置を計算し、高さマップを読んで持ち上げます。

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

コードの要点です。辺の係数を隣と揃え、隣り合うパッチが共有する辺で同じ係数を使います（クラックを防ぎます）。辺の中心の距離から計算します。係数は 1〜64 で、上げすぎると小さな三角形が増えて遅くなります。ハル シェーダーで画面外のパッチの係数を 0 にして捨てます。利点は、メッシュの管理が不要で、連続的に細かさが変わることです。欠点は、三角形が小さすぎると非効率なことと、GPU によってはテッセレーションが遅いことです。

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
