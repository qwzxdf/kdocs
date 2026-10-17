---
title: トライプラナー
tags:
  - 描画
---

# トライプラナー

**急斜面では、上から貼ったテクスチャが、縦に引き伸ばされます**。**X・Y・Z の 3 方向から貼って、法線に応じて混ぜる**ことで、**伸びを防げます**。このページでは、**トライプラナー マッピング**を説明します。

!!! tip "ポイント"
    - **3 方向（XY・YZ・ZX）から、テクスチャを貼る**。
    - **法線の向きで、3 つを混ぜる**。
    - **テクスチャの読み込みが、3 倍になる**。
    - **崖・岩に使う**。

## トライプラナー
**XZ 平面に投影する UV は、急斜面や崖でテクスチャが縦に引き伸ばされます**。**X・Y・Z の 3 方向から投影した 3 枚を、法線の向きで混ぜる**のが**トライプラナー マッピング**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="トライプラナー">
<text x="20" y="24" class="fig-title">トライプラナー：面の向きに応じて、3 方向の投影を混ぜる</text>
<polyline fill="#a0763c" fill-opacity="0.3" stroke="currentColor" stroke-opacity="0.7" stroke-width="2" points="60,190 220,190 300,70 440,70 520,190 720,190"/>
<g stroke="#4c8bf5" stroke-width="2"><line x1="120" y1="40" x2="120" y2="190"/><line x1="160" y1="40" x2="160" y2="190"/><line x1="200" y1="40" x2="200" y2="190"/></g>
<text x="60" y="34" style="font-size:12px;fill:#4c8bf5">上から投影：平らな所は良い</text>
<g stroke="#e5484d" stroke-width="2"><line x1="260" y1="110" x2="320" y2="110" /><line x1="262" y1="140" x2="320" y2="140"/></g>
<text x="330" y="150" style="font-size:12px;fill:#e5484d">崖は上から投影すると引き伸ばされる</text>
<g stroke="#2ea043" stroke-width="2"><line x1="420" y1="95" x2="470" y2="95" stroke-dasharray="3 3"/><line x1="440" y1="130" x2="490" y2="130" stroke-dasharray="3 3"/></g>
<text x="450" y="64" style="font-size:12px;fill:#2ea043">横から投影すれば良い</text>
</svg>

```hlsl
float3 TriplanarWeights(float3 normal, float sharpness) {
  float3 w = pow(abs(normal), sharpness);
  return w / (w.x + w.y + w.z);
}

float3 Triplanar(Texture2D tex, float3 world_position, float3 normal, float scale) {
  float3 w = TriplanarWeights(normal, 4.0);
  float3 x = tex.Sample(linear_wrap, world_position.zy * scale).rgb;
  float3 y = tex.Sample(linear_wrap, world_position.xz * scale).rgb;
  float3 z = tex.Sample(linear_wrap, world_position.xy * scale).rgb;
  return x * w.x + y * w.y + z * w.z;
}
```

| 点 | 説明 |
| --- | --- |
| **サンプル数が 3 倍** | **3 方向から 1 回ずつ読む**ので**重い**。**急斜面（岩）の層だけに使う** |
| **`sharpness`** | **大きいほど、方向の切り替えが鋭い** |
| **法線マップも要注意** | **接線空間でなくワールド空間の法線に直す**（**投影ごとに軸を入れ替えて、法線を戻す**） |
| **傾きで使い分け** | **平らな所は 1 方向（安い）、急な所だけ 3 方向** |

## よくあるミス

??? failure "崖のテクスチャが、縦に伸びている"
    **トライプラナー**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **3 方向から貼って、法線で混ぜる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形のテクスチャ](index.md)
- [繰り返しを隠す](tiling.md)
