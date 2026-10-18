---
title: Anisotropic Filtering
tags:
  - 描画
---

# Anisotropic Filtering

**地面を斜めから見ると、遠くのテクスチャがぼやけます**。**異方性フィルタリングは、縦と横で別々にフィルタして、ぼけを防ぎます**。このページでは、**異方性フィルタの効果**を説明します。

!!! tip "ポイント"
    - **斜めの面で、ぼけを防ぐ**。
    - **サンプル数（2x〜16x）で、品質とコストが変わる**。
    - **地形では、ほぼ必須**。
    - **設定で ON にするだけ**。

## Anisotropic Filtering {#異方性フィルタリング}
**斜めから見る地面**は、**テクスチャが縦に潰れる**ので、**ぼやけます**。<strong>異方性フィルタリング（16x など）</strong>を**有効**にすると**遠くの地面もくっきり**します。**地形ではほぼ必須**です。

<!-- fig:aniso-footprint:begin -->

<svg class="fig illust motion" data-fig="aniso-footprint" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-aniso-footprint" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">斜めから見ると、1 画素が、地面の細長い楕円を覆う</text>
<rect x="90" y="35" width="600" height="300" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<ellipse cx="390" cy="185" rx="24" ry="24" fill="#e5aa28" opacity="0.8" stroke="#e5484d" stroke-width="3"><animate attributeName="ry" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1481;0.2222;0.3704;0.4444;0.5926;0.6667;1.0000" values="24;24;33.941;33.941;70.171;70.171;138.21;138.21"/></ellipse>
<text x="100" y="55" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">地面を、真上から見た図（赤い楕円 = 1 画素が覆う範囲）</text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">視線の角度 0 度（真上）: 円。1 画素 = 正方形の領域<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;1.0000" values="1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">45 度: 縦に 1.4 倍<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">70 度: 2.9 倍。普通のミップは、長い方に合わせて、ぼやける<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.6516;0.6519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">80 度: 5.8 倍。異方性フィルタリングは、細長い範囲を複数のサンプルで平均する<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6516;0.6519;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:aniso-footprint:end -->

## Common Mistakes {#よくあるミス}

??? failure "遠くの地面が、ぼやけている"
    **異方性フィルタリング（8x〜16x）**を有効にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **斜めの面のぼけを防ぐ**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Terrain Texturing](index.md)
- [テクスチャ フィルタ](../../../3d/mesh-textures.md)
