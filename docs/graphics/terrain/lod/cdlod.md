---
title: CDLOD (Quadtree)
tags:
  - 描画
---

# CDLOD (Quadtree)

<strong>CDLOD は、地形を四分木に分け、カメラからの距離で、細かさを選ぶ手法</strong>です。<strong>距離に応じた連続的な LOD</strong>で、ポップが目立たないのが特徴です。このページでは、CDLOD の仕組みを説明します。

!!! tip "ポイント"
    - 四分木で、地形を再帰的に分割。
    - カメラから近い区画ほど、細かく分割。
    - 各区画は、同じ格子メッシュを再利用。
    - 距離で LOD の範囲を決める。

## 四分木（CDLOD）
<strong>CDLOD</strong>（Continuous Distance-Dependent LOD）は、<strong>地形を四分木で管理</strong>します。根（地形全体）から始め、カメラに近いノードを、4 つの子に分割していきます。

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

<strong>ノードの分割の判定</strong>は、<strong>カメラまでの距離がノードの大きさに比べて近いか</strong>で決めます。

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
| `lod_ranges[level]` | レベルごとの距離。倍々にする（例：50・100・200・400 m …） |
| 同じ格子メッシュ | <strong>どのノードも同じ頂点数の格子（例：33×33）</strong>を拡大縮小して描く（インスタンシング） |
| 視錐台カリング | 画面外のノードは捨てる |
| AABB の高さ | ノードごとの最小・最大の高さで境界を作る |


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

## 論文が解こうとした問題

地形の LOD には、CDLOD より前から、いくつかの有名な方式がありました。論文は、それぞれの欠点を並べて、「GPU に仕事を任せる時代に合う、単純な方式」を提案しています。

| 方式 | 考え方 | 困るところ |
| --- | --- | --- |
| ROAM（1997） | 三角形を 1 枚ずつ、分割・統合する | CPU の仕事が重い。三角形ごとの管理は、GPU に向かない |
| Geomipmapping | 地形を正方形のブロックに分け、ブロックごとに間引く | 切り替えで、ポップが出る。隣と LOD が違うと、継ぎ目の専用インデックスが要る |
| チャンク LOD（Ulrich 2002） | 事前に作った、LOD つきのメッシュのかたまりを切り替える | メッシュをディスクに持つ。切り替えで、ポップが出る |
| クリップマップ（2004） | カメラの周りに、同じ頂点数の格子を重ねる | カメラ周りの層の更新が要る。遠くの視錐台カリングがしにくい |
| CDLOD（2009） | 四分木で範囲を選び、頂点を距離に応じて、連続的に動かす | — |

CDLOD の要点は、次の 5 つです。

1. 四分木のノードを選ぶ基準は、「カメラまでの距離の範囲」。レベルごとに範囲を決めて、その範囲に入るノードを、そのレベルで描く
2. すべてのノードは、同じ格子メッシュを、使い回す。ノードごとに違うのは、位置・大きさ・レベルだけ（インスタンシング向き）
3. 高さは、頂点シェーダーで、テクスチャから読む。ノードごとの頂点データは、持たない
4. 頂点を、距離に応じて、連続的に動かす（モーフィング）。LOD の境目で、粗いレベルの形に、完全に一致させる
5. だから、継ぎ目の専用インデックスも、スカートも要らない

「選ぶのは、CPU の四分木。形を決めるのは、頂点シェーダー」という分担です。CPU は、数百個のノードを選ぶだけで、三角形は 1 枚も触りません。

## LOD の範囲を決める

レベル 0 が最も細かく、レベルが上がるほど粗くなります。カメラからの距離を、レベルごとに区切ります。

| レベル | 範囲（カメラからの距離）の例 | ノードの 1 辺 |
| --- | --- | --- |
| 0 | 0〜50 m | 64 m |
| 1 | 50〜100 m | 128 m |
| 2 | 100〜200 m | 256 m |
| 3 | 200〜400 m | 512 m |
| 4 | 400〜800 m | 1,024 m |

範囲を、<strong>前のレベルの 2 倍</strong>にすると、ノードの大きさ（1 辺が 2 倍）と、範囲の増え方が合います。そうすると、画面に映るノードの、見た目の大きさが、どのレベルでもほぼ同じになります。つまり、ノードごとの三角形数が、画面上で、ほぼ一定の密度になります。

距離は、<strong>カメラからノードの AABB（軸に沿った箱）までの 3 次元の距離</strong>で測ります。ノードの中心ではなく、箱の最も近い点を使います。高さの情報（最小・最大）が、箱に入っているので、山の上にいるときも、正しく測れます。

<strong>範囲の下限</strong>にも、条件があります。隣り合うノードのレベルが、<strong>2 以上離れてはいけません</strong>。1 つ違いなら、モーフィングで、境界を一致させられるからです。範囲を、ノードの大きさに比べて小さくしすぎると、この条件が破れます。論文のサンプルでは、範囲を、ノードの対角線の長さより十分に大きく取り、各レベルの範囲を、前の範囲の 2 倍前後にしています。

## ノードを選ぶアルゴリズム

根（地形全体）から再帰して、ノードを選びます。各ノードでは、次の 3 つを調べます。

1. ノードの AABB が、そのレベルの範囲の球と、交わらなければ、このノードは描かない（遠すぎる）
2. 視錐台と、交わらなければ、捨てる（画面の外）
3. ひとつ細かいレベルの範囲と、交わらなければ、このレベルで描く。交わるなら、4 つの子に分けて、子を調べる

```cpp
struct SelectedNode {
  const QuadNode* node;
  int level;
};

// level は、現在のノードのレベル（根が最大、葉が 0）。
void SelectNodes(const QuadNode& node, int level, const Camera& camera,
                 std::vector<SelectedNode>& out) {
  // ① このレベルの範囲の外なら、描かない（親が、粗いレベルで描いている）
  if (!node.bounds.IntersectsSphere(camera.position, lod_ranges[level])) {
    return;
  }
  // ② 画面の外なら捨てる
  if (!camera.frustum.Intersects(node.bounds)) {
    return;
  }
  // ③ 最も細かいレベル、または、ひとつ細かい範囲に入っていないなら、このノードで描く
  if (level == 0 ||
      !node.bounds.IntersectsSphere(camera.position, lod_ranges[level - 1])) {
    out.push_back({&node, level});
    return;
  }
  // ④ 範囲の内側にも入っている部分は、子に任せる。
  //    ノードの一部だけが近いとき、4 つの子はそれぞれ、別のレベルになる。
  for (const QuadNode& child : node.children) {
    SelectNodes(child, level - 1, camera, out);
  }
}
```

④ で、子に任せるとき、<strong>親のノードが描く範囲のうち、細かい子が受け持たない部分は、粗いまま親が受け持つ</strong>必要があります。実装では、子のうち「描かれなかった子」の領域に、親と同じ大きさの、粗いノードを追加する形にします（論文は、このとき 4 つの子の領域を、それぞれ、子のレベルで描く形で説明しています）。

## 格子メッシュ 1 枚を、使い回す

どのノードも、同じ頂点数の格子を使います。例として、32×32 マス（33×33 頂点）にします。<strong>偶数にするのは、モーフィングのため</strong>です。奇数番の頂点が、粗いレベルでは存在しない頂点になるので、偶数でないと、きれいに対応しません。

```cpp
constexpr int kGridCells = 32;
constexpr int kGridVerts = kGridCells + 1;

struct GridVertex { float x, z; };  // 0〜1 の範囲

// 頂点: 0〜1 を kGridCells 等分
std::vector<GridVertex> vertices;
for (int j = 0; j < kGridVerts; ++j) {
  for (int i = 0; i < kGridVerts; ++i) {
    vertices.push_back({float(i) / kGridCells, float(j) / kGridCells});
  }
}

// インデックス: 偶数マスと奇数マスで、対角線の向きを変える。
// こうすると、粗いレベルの三角形に、モーフィング後の形がぴったり一致する。
std::vector<uint16_t> indices;
for (int j = 0; j < kGridCells; ++j) {
  for (int i = 0; i < kGridCells; ++i) {
    uint16_t a = j * kGridVerts + i, b = a + 1;
    uint16_t c = (j + 1) * kGridVerts + i, d = c + 1;
    if (((i + j) & 1) == 0) {
      indices.insert(indices.end(), {a, c, d, a, d, b});
    } else {
      indices.insert(indices.end(), {a, c, b, b, c, d});
    }
  }
}
```

!!! note "対角線の向き"
    粗いレベルの 1 マスは、細かいレベルの 2×2 マスです。モーフィングで、奇数番の頂点が偶数番に重なったとき、細かい 4 マスの三角形のうち、いくつかは、つぶれて消えます。残る三角形が、粗い 1 マスの、2 枚の三角形になるように、4 マスの対角線を、市松模様に切り替えます。

## DirectX 11 で描く

ノードごとに変わる値は、<strong>インスタンス データ</strong>として、頂点バッファに積みます。1 回の `DrawIndexedInstanced` で、選ばれたすべてのノードを描けます。順に、コードを見ていきます。

### ノードごとのデータを、決める

```cpp
// ノードごとのデータ。インスタンス バッファに、ノードの数だけ並べる。
struct NodeInstance {
  float origin_x, origin_z;   // ノードの左下のワールド XZ
  float size;                 // ノードの 1 辺（メートル）
  float level;                // LOD レベル
  float morph_start, morph_end;  // モーフィングを始める距離、終える距離
  float pad[2];
};
```

1 つのノードを描くのに、必要な情報は、<strong>どこに置くか</strong>（`origin`）、<strong>どれだけ大きいか</strong>（`size`）、どの細かさか（`level`）、いつから寄せ始めるか（`morph_start`、`morph_end`）の、5 つだけです。最後の `pad` は、構造体の大きさを、32 バイトにそろえるための、詰め物です（GPU は、16 バイトの倍数の並びを、扱いやすい）。

### 頂点バッファを、2 本つなぐ入力レイアウト

```cpp
// 入力レイアウト: 0 番スロット = 格子の頂点、1 番スロット = インスタンス
D3D11_INPUT_ELEMENT_DESC layout[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NODE", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 0, D3D11_INPUT_PER_INSTANCE_DATA, 1},
    {"MORPH", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 16, D3D11_INPUT_PER_INSTANCE_DATA, 1},
};
```

入力レイアウトは、「<strong>バッファの、どの位置の、何バイトを、シェーダーの、どの入力として、読むか</strong>」を、GPU に伝える表です。

- 1 行目の `POSITION` は、スロット 0（格子の頂点バッファ）から読み、`PER_VERTEX_DATA` なので、頂点ごとに、次の値へ進みます
- 2 行目の `NODE` は、スロット 1（インスタンス バッファ）の、先頭から 16 バイト（`origin_x`、`origin_z`、`size`、`level`）を読みます。最後の `1` は、1 インスタンスにつき 1 回だけ、次の値へ進む、という意味です
- 3 行目の `MORPH` は、同じスロット 1 の、16 バイト目から（`morph_start`、`morph_end`、`pad`）を読みます

つまり、<strong>同じ格子の頂点を、インスタンスの数だけ、繰り返し使い</strong>、そのたびに、<strong>インスタンス側の値だけが、切り替わる</strong>仕組みです。

### 毎フレーム、選んだノードを書き込む

```cpp
// 毎フレーム: 選ばれたノードを、インスタンス バッファに書く
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(instance_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);
std::memcpy(mapped.pData, instances.data(), instances.size() * sizeof(NodeInstance));
context->Unmap(instance_buffer.Get(), 0);
```

ノードの選択（上の「ノードを選ぶアルゴリズム」）が終わったら、結果を、GPU のバッファへ、コピーします。`D3D11_MAP_WRITE_DISCARD` は、「<strong>古い中身は、もう要らない</strong>」という指定で、GPU がまだ前のフレームを描いていても、<strong>待たされずに、新しい領域をもらえます</strong>。バッファは、`D3D11_USAGE_DYNAMIC` で作っておく必要があります。

### バッファを設定して、1 回で描く

```cpp
UINT strides[2] = {sizeof(GridVertex), sizeof(NodeInstance)};
UINT offsets[2] = {0, 0};
ID3D11Buffer* buffers[2] = {grid_vb.Get(), instance_buffer.Get()};
context->IASetVertexBuffers(0, 2, buffers, strides, offsets);
context->IASetIndexBuffer(grid_ib.Get(), DXGI_FORMAT_R16_UINT, 0);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
context->DrawIndexedInstanced(static_cast<UINT>(indices.size()),
                              static_cast<UINT>(instances.size()), 0, 0, 0);
```

前半の 4 行は、<strong>2 本の頂点バッファ</strong>（格子と、インスタンス）と、<strong>インデックス バッファ</strong>を、描画の入口（入力アセンブラー）に、つなぐ作業です。最後の `DrawIndexedInstanced` が、本番で、「この格子（インデックスの数）を、ノードの数だけ、繰り返して描け」という、1 回の命令です。ドローコールが、ノードの数に関係なく、1 回で済むのが、この方式の、利点です。

### 頂点シェーダー：定数と、入力

頂点シェーダーは、<strong>格子の位置</strong>（0〜1）を、<strong>ノードの位置と大きさ</strong>で、ワールド座標へ変えます。そのあと、モーフィングして、高さを読みます。まず、シェーダーが受け取る、定数と、入力です。

```hlsl
cbuffer FrameCB : register(b0) {
  float4x4 view_proj;
  float3 camera_position;
  float grid_size;               // 32
  float2 heightmap_origin;       // 高さマップの左下（ワールド XZ）
  float2 heightmap_size;         // 高さマップが覆うワールドの大きさ
  float height_scale;
  float height_offset;
  float2 pad;
};
```

`cbuffer` は、<strong>フレームに 1 回、CPU から渡す、共通の値</strong>の置き場です。カメラの位置（距離を測るため）、高さマップが、<strong>ワールドのどこを覆うか</strong>（UV を求めるため）、高さをメートルに直す係数（`height_scale`、`height_offset`）が入っています。

```hlsl
Texture2D<float> g_height : register(t0);   // R16_UNORM（線形補間ができる形式）
SamplerState g_linear_clamp : register(s0);

struct VSInput {
  float2 grid : POSITION;       // 0〜1
  float4 node : NODE;           // xy = 原点, z = 大きさ, w = レベル
  float4 morph : MORPH;         // x = 開始距離, y = 終了距離
};
```

高さマップは、<strong>頂点シェーダーから読む</strong>テクスチャです。`R16_UNORM`（16 ビットの、0〜1 の値）にしておくのは、<strong>32 ビット浮動小数点</strong>（`R32_FLOAT`）は、線形補間（フィルタリング）が、環境によって、使えないためです。`VSInput` は、さきほどの、入力レイアウトと、対応しています（`POSITION`、`NODE`、`MORPH`）。

### 高さを読む関数

```hlsl
float SampleHeight(float2 world_xz) {
  float2 uv = (world_xz - heightmap_origin) / heightmap_size;
  return g_height.SampleLevel(g_linear_clamp, uv, 0) * height_scale + height_offset;
}
```

ワールドの `(x, z)` から、<strong>高さマップの UV</strong>（0〜1）を求め、<strong>高さを読んで、メートルに直す</strong>、小さな関数です。頂点シェーダーでは、画面の微分が、使えないので、`Sample` ではなく、`SampleLevel`（ミップを、自分で指定）を使います。ここでは、ミップ 0 を、読んでいます（ミップの選び方は、[Heightmap LOD (Mips)](height-mip.md) で扱います）。

### 本体 1：まず、動かす前の位置で、距離を測る

```hlsl
float4 main(VSInput input) : SV_Position {
  // ① まず、モーフィングなしの XZ で、高さを読み、距離を測る
  float2 xz = input.node.xy + input.grid * input.node.z;
  float3 p = float3(xz.x, SampleHeight(xz), xz.y);
  float dist = distance(p, camera_position);
```

1 行目の計算で、<strong>格子の位置（0〜1）</strong>に、ノードの大きさを掛け、原点を足して、<strong>ワールドの XZ</strong> にします。次に、その位置の、高さを読んで、3 次元の位置 `p` を作り、カメラまでの、3 次元の距離を測ります。この距離が、どれだけ、モーフィングするかを、決める材料です。

### 本体 2：モーフ係数を、決める

```hlsl
  // ② モーフ係数: 開始距離まで 0、終了距離で 1
  float morph = saturate((dist - input.morph.x) / (input.morph.y - input.morph.x));
```

`dist` が、<strong>開始距離以下</strong>なら 0、<strong>終了距離以上</strong>なら 1 で、その間は、直線的に、0 から 1 へ増えます。`saturate` は、値を、0〜1 の範囲に、収める関数です。近いうちは 0（何もしない）で、LOD の境目に近づくと、1 に向かう、というのが、モーフィングの、時間割りです。

### 本体 3：奇数番の頂点を、寄せる

```hlsl
  // ③ 奇数番の頂点を、ひとつ前の偶数番の位置へ寄せる
  float2 frac_part = frac(input.grid * (grid_size * 0.5)) * (2.0 / grid_size);
  float2 grid_morphed = input.grid - frac_part * morph;
```

この 2 行が、モーフィングの、中心です。

- `input.grid * (grid_size * 0.5)` は、格子の位置を、マスの番号の、半分にします。偶数番の頂点では、整数になり、奇数番の頂点では、小数部が、0.5 になります
- `frac(...)` で、その小数部だけを取り出します。偶数番は 0、奇数番は 0.5 です
- `* (2.0 / grid_size)` で、格子 1 マス分の長さ（`1 / grid_size`）に、直します。つまり、偶数番は 0、奇数番は 1 マス分になります
- 最後に、`morph` を掛けて、位置から引きます。`morph = 1` のとき、奇数番の頂点だけが、1 マス分、手前（ひとつ前の偶数番）に、動きます

こうして、<strong>粗い LOD に存在しない頂点（奇数番）</strong>が、<strong>粗い LOD に存在する頂点（偶数番）に、重なって</strong>いきます。

### 本体 4：寄せた位置で、高さを読み直す

```hlsl
  // ④ 寄せた XZ で、高さを読み直す
  xz = input.node.xy + grid_morphed * input.node.z;
  p = float3(xz.x, SampleHeight(xz), xz.y);
  return mul(float4(p, 1.0), view_proj);
}
```

XZ が動いたので、<strong>動いた先の高さ</strong>を、もう一度、読みます。そうしないと、頂点が、<strong>元の高さのまま、横にずれて</strong>、地形が、崩れます。最後に、ビュー・射影行列を掛けて、画面上の位置にして、返します。行ベクトル（`mul(v, M)`）の、順序であることに、注意してください。

### 速度が出る理由

| 項目 | 内容 |
| --- | --- |
| CPU の仕事 | 数百個のノードを選ぶだけ。頂点データには触らない |
| ドローコール | 1 回（インスタンシング）。または、レベルごとに数回 |
| 頂点データ | 格子 1 枚。全ノードで共有する |
| LOD の切り替え | 頂点シェーダーが連続的に動かすので、ポップが出ない |
| カリング | ノードごとに、視錐台カリングができる（クリップマップより細かく捨てられる） |

## 論文と、実装でずれやすい点

| 項目 | 論文の考え方 | 実装で気をつけること |
| --- | --- | --- |
| 距離 | カメラから、頂点（または AABB）までの 3 次元の距離 | XZ の 2 次元の距離だと、高い山で、LOD が合わない |
| モーフの範囲 | 各レベルの範囲の後ろ側で、0 から 1 へ | 範囲いっぱいで動かすと、細かさが落ちる。後ろの 3 割程度にする実装が多い |
| 高さの読み方 | 頂点シェーダーでの、テクスチャ読み | `R32_FLOAT` の線形補間は、環境で、使えないことがある。`R16_UNORM` が安全 |
| 法線 | 高さマップから計算（またはテクスチャ） | 頂点で出さず、ピクセル シェーダーで、高さマップの差分から出すと、モーフ中も滑らか |
| ノードの AABB | 高さの最小・最大を、四分木の各ノードに事前計算 | 高さを編集したら、AABB も更新する |

法線を高さマップから計算する方法は、[Terrain Normals](../heightmap-mesh/normals.md) を見てください。

## よくあるミス

??? failure "LOD の範囲が狭すぎて、粗い所が目立つ"
    <strong>LOD の範囲を広げる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 距離に応じて、四分木を分割

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009（CDLOD の原典。作者の公開サンプル `fstrugar/CDLOD` が GitHub にある）
- Losasso, Hoppe, "Geometry Clipmaps: Terrain Rendering Using Nested Regular Grids", ACM Transactions on Graphics (SIGGRAPH 2004)
- Ulrich, "Rendering Massive Terrains Using Chunked Level of Detail Control", SIGGRAPH 2002 Course Notes（チャンク LOD、スカート、ジオモーフ）
- Duchaineau et al., "ROAM: Real-Time Optimally Adapting Meshes", IEEE Visualization 1997
- Microsoft Learn, "ID3D11DeviceContext::DrawIndexedInstanced"（インスタンシングの描画呼び出し）

## 関連ページ

- [Terrain LOD](index.md)
- [Geomorphing](morphing.md)
- [Cracks and Seams](cracks.md)
