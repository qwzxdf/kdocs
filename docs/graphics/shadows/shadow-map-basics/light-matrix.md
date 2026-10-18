---
title: The Light Matrix
tags:
  - 描画
---

# The Light Matrix

**シャドウ マップを作るには、「光から見た世界」を描く**必要があり、そのための**ビュー行列と射影行列（光の行列）**を**作ります**。**光の種類で、射影が変わります**：**太陽（平行光）は正射影、スポットライトは透視投影、点光源はキューブ マップの 6 方向**です。このページでは、**それぞれの行列の作り方・範囲の決め方・点光源の 6 方向**を説明します。

!!! tip "ポイント"
    - **平行光（太陽）**：**正射影**。**光の向きにカメラを置き、見える範囲を箱で囲む**。
    - **スポットライト**：**透視投影**。**視野角 ＝ 円錐の角度の 2 倍**。
    - **点光源**：**90° の透視投影を 6 面**（**キューブ マップ**）。
    - **範囲（箱・近い面・遠い面）を、狭く決める**と**解像度が無駄にならない**。

## ① The Light Matrix {#①-光の行列}
<!-- fig:light-frustum:begin -->

<svg class="fig illust motion" data-fig="light-frustum" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-light-frustum" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">光の行列:平行光は「箱」、スポットは「錐」でシーンを捉える</text>
<rect x="40" y="300" width="700" height="14" fill="#d6c7a1"/>
<rect x="220" y="230" width="34" height="70" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<rect x="360" y="190" width="34" height="110" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<rect x="480" y="240" width="34" height="60" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<rect x="590" y="210" width="34" height="90" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<polygon points="0,0 0,0 0,0 0,0" fill="#2563eb" fill-opacity="0.12" stroke="#2563eb" stroke-width="3"><animate attributeName="points" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.3333;0.5833;0.9167;1.0000" values="0,0 0,0 0,0 0,0;0,0 0,0 0,0 0,0;160,90 620,90 620,305 160,305;160,90 620,90 620,305 160,305;370,90 410,90 640,305 140,305;370,90 410,90 640,305 140,305;370,90 410,90 640,305 140,305"/></polygon>
<circle cx="390" cy="70" r="12" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="410" y="66" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">光</text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">平行光（太陽）:光線は平行 → 正射影（箱）。範囲が一定<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光を近くへ（点光源・スポットライト）…<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;0.5830;0.5833;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">スポットライト:光線は 1 点から広がる → 透視投影（錐）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5830;0.5833;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">この箱 / 錐が、シャドウ マップに映る範囲。範囲を狭くするほど、1 テクセルあたりの解像度が上がる。</text>
</svg>

<!-- fig:light-frustum:end -->

### Directional Light (Sun): Orthographic Projection {#平行光太陽正射影}

平行光は**光が全て平行**なので**正射影**（遠近感なし）で撮ります。**光の向き**を前方向にして、**シーンの範囲（影を落とす物・受ける物）を覆う箱**を決めます。

```cpp
Matrix LightViewProjection(const Vector3& light_dir, const Vector3& center, float radius) {
  Vector3 light_pos = center - light_dir * radius * 2.0f;
  Matrix view = XMMatrixLookAtLH(light_pos, center, Vector3::Up);
  Matrix proj = XMMatrixOrthographicLH(radius * 2.0f, radius * 2.0f, 0.0f, radius * 4.0f);
  return view * proj;
}
```

| 点 | 説明 |
| --- | --- |
| **光の位置** | **シーンの中心から、光の逆向きに十分に離れた所**。平行光では位置は本質的ではないが、**ビュー行列を作るため**に必要 |
| **正射影の大きさ** | 影を受ける範囲を覆う。**大きいほど、1 テクセルが粗い**（エイリアシング） |
| **近・遠クリップ** | 影を落とす物体が範囲内に入るように |
| **上方向 `Up`** | 光の向きと平行だと破綻する（真上からの光）。別の軸を使う |

### Spot Light: Perspective Projection {#スポットライト透視投影}

**スポットライト**は、**一点から円錐状**に光が出るので、**透視投影**で撮ります。**視野角**はスポットの**円錐の角度**に合わせます。

### Point Light: Cube Map {#点光源キューブマップ}

**全方向**に光が出るので<strong>6 方向（キューブマップ）</strong>で撮ります（[Point and Spot Light Shadows](../local-lights/index.md)）。

## Common Mistakes {#よくあるミス}

??? failure "太陽の範囲を、シーン全体にして、影がぼやける"
    **カメラの視錐台を覆う最小の箱**にする（[カスケード](../cascaded.md)）。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **光の種類で射影が違う**（正射影・透視・キューブ）
    - [x] **範囲は狭く、必要な所だけ**

## References {#参考}

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## Related Pages {#関連ページ}

- [Shadow Map Basics](index.md)
- [Rendering Depth](render-depth.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
