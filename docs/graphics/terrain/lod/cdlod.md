---
title: CDLOD (Quadtree)
tags:
  - 描画
---

# CDLOD (Quadtree)

**CDLOD は、地形を四分木に分け、カメラからの距離で、細かさを選ぶ手法**です。**距離に応じた連続的な LOD**で、**ポップが目立たない**のが**特徴**です。このページでは、**CDLOD の仕組み**を説明します。

!!! tip "ポイント"
    - **四分木で、地形を再帰的に分割**。
    - **カメラから近い区画ほど、細かく分割**。
    - **各区画は、同じ格子メッシュを再利用**。
    - **距離で LOD の範囲を決める**。

## 四分木（CDLOD）
**CDLOD**（Continuous Distance-Dependent LOD）は、**地形を四分木で管理**します。**根（地形全体）から始め、カメラに近いノードを、4 つの子に分割**していきます。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="四分木 LOD">
<text x="20" y="24" class="fig-title">四分木：カメラに近いほど、細かく分割する</text>
<rect x="60" y="50" width="320" height="180" fill="none" stroke="currentColor" stroke-opacity="0.6"/>
<g stroke="currentColor" stroke-opacity="0.6" fill="none">
<line x1="220" y1="50" x2="220" y2="230"/><line x1="60" y1="140" x2="380" y2="140"/>
<line x1="140" y1="140" x2="140" y2="230"/><line x1="60" y1="185" x2="220" y2="185"/>
<line x1="100" y1="185" x2="100" y2="230"/><line x1="140" y1="185" x2="140" y2="230"/><line x1="60" y1="207" x2="140" y2="207"/>
</g>
<circle cx="80" cy="218" r="7" fill="#e5484d"/>
<text x="92" y="214" style="font-size:12px;fill:#e5484d">カメラ</text>
<text x="400" y="80" style="font-size:13px">・カメラに近いノード → 4 分割</text>
<text x="400" y="106" style="font-size:13px">・遠いノード → そのまま 1 枚</text>
<text x="400" y="132" style="font-size:13px">・各ノードは同じ頂点数の格子</text>
<text x="400" y="158" style="font-size:13px">・大きいノード ＝ 粗い（広い範囲を同じ頂点数で覆う）</text>
</svg>

**ノードの分割の判定**は、**カメラまでの距離がノードの大きさに比べて近いか**で決めます。

```cpp
void SelectNodes(const QuadNode& node, const Camera& camera, int level,
                 std::vector<SelectedNode>& out) {
  float range = lod_ranges[level];
  if (!node.bounds.IntersectsSphere(camera.position, range)) {
    return;
  }
  if (!camera.frustum.Intersects(node.bounds)) {
    return;
  }
  if (level == 0 || !node.bounds.IntersectsSphere(camera.position, lod_ranges[level - 1])) {
    out.push_back({node, level});
    return;
  }
  for (const QuadNode& child : node.children) {
    SelectNodes(child, camera, level - 1, out);
  }
}
```

| 点 | 説明 |
| --- | --- |
| **`lod_ranges[level]`** | **レベルごとの距離**。**倍々**にする（例：50・100・200・400 m …） |
| **同じ格子メッシュ** | <strong>どのノードも同じ頂点数の格子（例：33×33）</strong>を**拡大縮小して描く**（**インスタンシング**） |
| **視錐台カリング** | **画面外のノードは捨てる** |
| **AABB の高さ** | **ノードごとの最小・最大の高さ**で**境界を作る** |


原典は、Strugar の "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（Journal of Graphics, GPU, and Game Tools、2010）です。

原典は、Strugar の "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（Journal of Graphics, GPU, and Game Tools、2010）です。

<!-- fig:terrain-quadtree:begin -->

<svg class="fig illust motion" data-fig="terrain-quadtree" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-terrain-quadtree" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">四分木 LOD: カメラに近い所だけ細かく分け、遠くは大きなまま描く</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">16×16 の地形。分けた回数 = レベル。カメラとの距離がノードの大きさの 1.5 倍より近ければ、4 つに分ける</text>
<rect x="30" y="96" width="436.0" height="436.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">上から見た地形(色 = レベル)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="1;1;0;0"/><rect x="40.0" y="100.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="100.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="66.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="66.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="118.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="118.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="412.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="438.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="66.0" y="412.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="66.0" y="438.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="464.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="490.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="66.0" y="464.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="66.0" y="490.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="412.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="438.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="118.0" y="412.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="118.0" y="438.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="464.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="490.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="118.0" y="464.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="118.0" y="490.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="412.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="438.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="412.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="438.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="464.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="490.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="464.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="490.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="100.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="204.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="100.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="204.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="308.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="412.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;0.5776;0.5778;1.0000" values="0;0;1;1;0;0"/><rect x="40.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="92.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="170.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="222.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="256.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="282.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="274.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="308.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="334.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="360.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="386.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="412.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="464.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5776;0.5778;1.0000" values="0;0;1;1"/><rect x="40.0" y="100.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="204.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="196.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="308.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="40.0" y="412.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="308.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="144.0" y="412.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="100.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="152.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="100.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="126.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="100.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="126.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="152.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="178.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="152.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="178.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="204.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="326.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="100.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="126.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="378.0" y="100.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="378.0" y="126.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="152.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="178.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="378.0" y="152.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="378.0" y="178.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="100.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="126.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="430.0" y="100.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="430.0" y="126.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="152.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="178.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="430.0" y="152.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="430.0" y="178.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="378.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="378.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="430.0" y="204.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="430.0" y="230.0" width="24.5" height="24.5" fill="#fca5a5" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="256.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="300.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="248.0" y="412.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="308.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="404.0" y="360.0" width="50.5" height="50.5" fill="#fdba74" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
<rect x="352.0" y="412.0" width="102.5" height="102.5" fill="#fde047" fill-opacity="0.55" stroke="#334155" stroke-width="1.2"/>
</g>
<circle cx="105.0" cy="438.0" r="9" fill="#1f2937" stroke="#ffffff" stroke-width="2.5"><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.3022;0.5244;0.5689;1.0000" values="105;105;248;248;391;391"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.3022;0.5244;0.5689;1.0000" values="438;438;308;308;165;165"/></circle>
<text x="117.0" y="428.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">カメラ</text>
<rect x="500" y="96" width="430" height="220" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="500" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">選ばれたノード</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="1;1;0;0"/><rect x="520" y="122" width="18" height="18" fill="#7dd3fc" opacity="0.8"/>
<text x="548" y="136" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 0(1 辺 16): 0 個</text>
<rect x="520" y="148" width="18" height="18" fill="#86efac" opacity="0.8"/>
<text x="548" y="162" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 1(1 辺 8): 0 個</text>
<rect x="520" y="174" width="18" height="18" fill="#fde047" opacity="0.8"/>
<text x="548" y="188" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 2(1 辺 4): 8 個</text>
<rect x="520" y="200" width="18" height="18" fill="#fdba74" opacity="0.8"/>
<text x="548" y="214" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 3(1 辺 2): 23 個</text>
<rect x="520" y="226" width="18" height="18" fill="#fca5a5" opacity="0.8"/>
<text x="548" y="240" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 4(1 辺 1): 36 個</text>
<text x="520" y="290" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">ノード 67 個 → 三角形 8,576 個</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;0.5776;0.5778;1.0000" values="0;0;1;1;0;0"/><rect x="520" y="122" width="18" height="18" fill="#7dd3fc" opacity="0.8"/>
<text x="548" y="136" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 0(1 辺 16): 0 個</text>
<rect x="520" y="148" width="18" height="18" fill="#86efac" opacity="0.8"/>
<text x="548" y="162" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 1(1 辺 8): 0 個</text>
<rect x="520" y="174" width="18" height="18" fill="#fde047" opacity="0.8"/>
<text x="548" y="188" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 2(1 辺 4): 0 個</text>
<rect x="520" y="200" width="18" height="18" fill="#fdba74" opacity="0.8"/>
<text x="548" y="214" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 3(1 辺 2): 48 個</text>
<rect x="520" y="226" width="18" height="18" fill="#fca5a5" opacity="0.8"/>
<text x="548" y="240" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 4(1 辺 1): 64 個</text>
<text x="520" y="290" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">ノード 112 個 → 三角形 14,336 個</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5776;0.5778;1.0000" values="0;0;1;1"/><rect x="520" y="122" width="18" height="18" fill="#7dd3fc" opacity="0.8"/>
<text x="548" y="136" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 0(1 辺 16): 0 個</text>
<rect x="520" y="148" width="18" height="18" fill="#86efac" opacity="0.8"/>
<text x="548" y="162" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 1(1 辺 8): 0 個</text>
<rect x="520" y="174" width="18" height="18" fill="#fde047" opacity="0.8"/>
<text x="548" y="188" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 2(1 辺 4): 8 個</text>
<rect x="520" y="200" width="18" height="18" fill="#fdba74" opacity="0.8"/>
<text x="548" y="214" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 3(1 辺 2): 23 個</text>
<rect x="520" y="226" width="18" height="18" fill="#fca5a5" opacity="0.8"/>
<text x="548" y="240" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">レベル 4(1 辺 1): 36 個</text>
<text x="520" y="290" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">ノード 67 個 → 三角形 8,576 個</text>
</g>
<text x="500" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">ノード数:</text>
<text x="600" y="350" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0576;0.0578;1.0000" values="1;1;0;0"/></text>
<text x="600" y="350" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">67<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0576;0.0578;0.3243;0.3244;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="350" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">112<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;0.5909;0.5911;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="350" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">67<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5909;0.5911;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8220;0.8222;1.0000" values="0;0;1;1"/><rect x="500" y="376" width="430" height="100" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="516" y="400" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">全部を最も細かく描くと、ノード 256 個(三角形 32,768 個)</text>
<text x="516" y="423" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">四分木: 67 / 112 / 67 個(それぞれ 26% / 44% / 26%)</text>
<text x="516" y="446" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">どのノードも、同じ 8×8 の格子を使い回す(1 ノード = 三角形 128 個)</text>
</g>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">地形を 1 枚の大きなノードから始める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;1.0000" values="1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが左下: そこだけ細かく分かれる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;0.3109;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが中央: 中央が細かく、まわりは大きなまま<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;0.5776;0.5778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが右上: 細かい所が追いかけてくる。描く数は、ほぼ一定<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5776;0.5778;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:terrain-quadtree:end -->

## よくあるミス

??? failure "LOD の範囲が狭すぎて、粗い所が目立つ"
    **LOD の範囲を広げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離に応じて、四分木を分割**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain LOD](index.md)
- [Geomorphing](morphing.md)
- [Cracks and Seams](cracks.md)
