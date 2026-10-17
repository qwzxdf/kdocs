---
title: froxel
tags:
  - 描画
---

# froxel

**froxel は、カメラの視錐台（frustum）を分けた、3D のボクセルです**。**画面に近い所は細かく、遠い所は粗くなる**ので、**見た目に効率が良い**です。このページでは、**froxel の構造**を説明します。

!!! tip "ポイント"
    - **froxel ＝ frustum ＋ voxel**。
    - **画面の縦横に分割し、奥行きを対数的に分割**。
    - **3D テクスチャ（例：160×90×64）**で持つ。
    - **近くが細かい**ので、**効率的**。

## froxel
**froxel**（frustum voxel）は、**カメラの視錐台を画面の格子（X, Y）と奥行き（Z）で分割した 3D 格子**です。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="froxel">
<text x="20" y="24" class="fig-title">froxel：視錐台を、画面に沿った 3D の格子に切る</text>
<polygon points="80,140 400,60 400,220" fill="#4c8bf5" fill-opacity="0.1" stroke="#4c8bf5" stroke-width="2"/>
<g stroke="currentColor" stroke-opacity="0.4">
<line x1="130" y1="127" x2="130" y2="153"/><line x1="190" y1="112" x2="190" y2="168"/><line x1="260" y1="95" x2="260" y2="185"/><line x1="340" y1="75" x2="340" y2="205"/><line x1="400" y1="60" x2="400" y2="220"/>
</g>
<circle cx="80" cy="140" r="6" fill="#e5484d"/><text x="60" y="164" style="font-size:12px">カメラ</text>
<text x="130" y="120" style="font-size:11px">近い：薄い</text><text x="320" y="62" style="font-size:11px">遠い：厚い</text>
<g transform="translate(470,50)">
<text x="0" y="0" style="font-size:12px;font-weight:700">画面方向の格子（幅×高さ）</text>
<g stroke="currentColor" stroke-opacity="0.4" fill="none"><rect x="0" y="14" width="240" height="135"/>
<line x1="60" y1="14" x2="60" y2="149"/><line x1="120" y1="14" x2="120" y2="149"/><line x1="180" y1="14" x2="180" y2="149"/>
<line x1="0" y1="48" x2="240" y2="48"/><line x1="0" y1="82" x2="240" y2="82"/><line x1="0" y1="116" x2="240" y2="116"/></g>
<rect x="120" y="48" width="60" height="34" fill="#e5aa28" fill-opacity="0.5"/>
<text x="0" y="176" style="font-size:12px">1 マス ＝ 画面の 8×8 ピクセルほど</text>
<text x="0" y="198" style="font-size:12px">奥行き方向に 64 枚ほどのスライス</text>
</g>
</svg>

| 項目 | 内容 |
| --- | --- |
| **解像度** | **160×90×64 程度**（画面の 1/8 の解像度）。**ピクセルを 1 つずつでなく、まとめて計算** |
| **形式** | **3D テクスチャ**（`RGBA16F`：散乱光 RGB ＋ 密度） |
| **奥行きの割り当て** | **近くを細かく**（指数的）。**`z = near * pow(far/near, slice/N)`** |
| **カメラに追従** | **視錐台と一緒に動く**。**画面の解像度に依存しない** |

```hlsl
float SliceToDepth(float slice, float near_z, float far_z, float slice_count) {
  return near_z * pow(far_z / near_z, slice / slice_count);
}

float DepthToSlice(float depth, float near_z, float far_z, float slice_count) {
  return log(depth / near_z) / log(far_z / near_z) * slice_count;
}
```

## よくあるミス

??? failure "奥行きの分割が粗く、層状の縞が見える"
    **スライス数を増やす**・**ジッタ**を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **視錐台を分けた、3D のグリッド**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [ボリューメトリック フォグ](index.md)
- [密度](density.md)
