---
title: Height at Arbitrary Positions
tags:
  - 描画
---

# Height at Arbitrary Positions

**キャラクターを地面に立たせるには、任意の位置の地面の高さが必要**です。**格子の 4 点から補間**して**求めます**。このページでは、**高さの取得方法**を説明します。

!!! tip "ポイント"
    - **位置を格子の座標に変換**し、**周囲の 4 点を取り出す**。
    - **双線形補間で、高さを求める**。
    - **CPU 側にも、高さマップを持つ**。
    - **格子の三角形の分割と、補間を合わせる**。

## 任意の位置の高さを取る
**キャラクターを地面に立たせる・草を置く・当たり判定**には、**CPU で任意の (x, z) の高さ**が**必要**です。**高さマップの 4 点を、双線形補間**します。

```cpp
float SampleHeight(const HeightMap& map, float world_x, float world_z) {
  float u = (world_x - map.origin_x) / map.cell_size;
  float v = (world_z - map.origin_z) / map.cell_size;
  int x0 = static_cast<int>(std::floor(u));
  int z0 = static_cast<int>(std::floor(v));
  float fx = u - x0;
  float fz = v - z0;

  float h00 = map.At(x0, z0);
  float h10 = map.At(x0 + 1, z0);
  float h01 = map.At(x0, z0 + 1);
  float h11 = map.At(x0 + 1, z0 + 1);

  float h0 = h00 + (h10 - h00) * fx;
  float h1 = h01 + (h11 - h01) * fx;
  return h0 + (h1 - h0) * fz;
}
```

| 点 | 説明 |
| --- | --- |
| **双線形補間** | **4 点を補間**して**滑らかな高さ** |
| **メッシュの三角形と一致させる** | **見た目のメッシュは三角形 2 枚**なので、**厳密には三角形に沿って補間する**と**ずれない**（**足が浮く・めり込む**を防ぐ） |
| **GPU と同じデータ** | **CPU 側にも同じ高さマップを保持** |
| **範囲外** | **`At` は端にクランプ** |

**対角線方向の三角形に沿った補間**は、**マス内の位置 (fx, fz) が `fx + fz < 1` かどうか**で**三角形を選び**、**その三角形上の平面の式**で**高さを出します**。

<!-- fig:bilinear-height:begin -->

<svg class="fig illust motion" data-fig="bilinear-height" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bilinear-height" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">好きな位置の高さ: 周りの 4 点を、距離で混ぜる(バイリニア補間)</text>
<rect x="270" y="90" width="220" height="220" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<circle cx="270" cy="310" r="5" fill="#64748b"/>
<text x="258" y="332" text-anchor="end" style="font-size:13px;font-weight:700;fill:#64748b">h=2</text>
<circle cx="490" cy="310" r="5" fill="#64748b"/>
<text x="502" y="332" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">h=6</text>
<circle cx="270" cy="90" r="5" fill="#64748b"/>
<text x="258" y="80" text-anchor="end" style="font-size:13px;font-weight:700;fill:#64748b">h=4</text>
<circle cx="490" cy="90" r="5" fill="#64748b"/>
<text x="502" y="80" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">h=8</text>
<circle cx="314.0" cy="266.0" r="9" fill="#e5484d"><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1931;0.2759;0.4000;0.4828;0.6069;0.6897;1.0000" values="314;314;380;380;446;446;325;325"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1931;0.2759;0.4000;0.4828;0.6069;0.6897;1.0000" values="266;266;200;200;244;244;145;145"/></circle>
<text x="390" y="350" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">u = 0.20, v = 0.20 → h = 3.20<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;1.0000" values="1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">u = 0.50, v = 0.50 → h = 5.00<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;0.4825;0.4828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">u = 0.80, v = 0.30 → h = 5.80<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;0.6894;0.6897;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">u = 0.25, v = 0.75 → h = 4.50<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6894;0.6897;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#64748b">h = h00(1−u)(1−v) + h10·u(1−v) + h01(1−u)v + h11·u·v</text>
</svg>

<!-- fig:bilinear-height:end -->

## よくあるミス

??? failure "キャラクターが、地面にめり込む・浮く"
    **描画と同じ補間方法**で**高さを求める**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **4 点を補間して、高さを求める**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [Chunking](chunks.md)
