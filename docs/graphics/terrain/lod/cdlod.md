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

<!-- fig:terrain-quadtree:begin -->

<svg class="fig illust motion" data-fig="terrain-quadtree" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-terrain-quadtree" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">四分木 LOD:カメラに近いほど、タイルを 4 つに分けて細かくする</text>
<rect x="30" y="52" width="336" height="336" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<rect x="31.0" y="53.0" width="334.0" height="334.0" fill="#bfdbfe" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="31.0" y="53.0" width="166.0" height="166.0" fill="#bbf7d0" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;1;1;1;1;0;0;1;1;1"/></rect>
<rect x="199.0" y="53.0" width="166.0" height="166.0" fill="#bbf7d0" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;1;0;0;0;0;0;1;1;1"/></rect>
<rect x="31.0" y="221.0" width="166.0" height="166.0" fill="#bbf7d0" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;1;0;0;0;0"/></rect>
<rect x="199.0" y="221.0" width="166.0" height="166.0" fill="#bbf7d0" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;0;0;0;1;1;0;0;0;1"/></rect>
<rect x="31.0" y="53.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;1;1;0;0;0"/></rect>
<rect x="115.0" y="53.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;1;1;0;0;0"/></rect>
<rect x="199.0" y="53.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;1;0;0;1;0;0;0"/></rect>
<rect x="283.0" y="53.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;1;1;0;0;0"/></rect>
<rect x="31.0" y="137.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;1;1;0;0;0"/></rect>
<rect x="115.0" y="137.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="199.0" y="137.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;0;1;0;0;0"/></rect>
<rect x="283.0" y="137.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;1;1;0;0;0"/></rect>
<rect x="31.0" y="221.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;1;1;0;0;0;1;0;1;1"/></rect>
<rect x="115.0" y="221.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;0;1;0;0;0;0;0;1;1"/></rect>
<rect x="199.0" y="221.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;1;0;0;0;1;1;0"/></rect>
<rect x="283.0" y="221.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;1;0;0;1;1;1;0"/></rect>
<rect x="31.0" y="305.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;1;0;0;0;1;1;0;0"/></rect>
<rect x="115.0" y="305.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;1;0;0;0"/></rect>
<rect x="199.0" y="305.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;1;0;0;1;1;1;0"/></rect>
<rect x="283.0" y="305.0" width="82.0" height="82.0" fill="#fde68a" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;1;1;0;0;1;1;1;0"/></rect>
<rect x="31.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="73.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="115.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="157.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="199.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;1;1;0;0;0;0"/></rect>
<rect x="241.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;1;1;0;0;0;0"/></rect>
<rect x="283.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="325.0" y="53.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="31.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="73.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="115.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="157.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="199.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;1;1;0;0;0;0"/></rect>
<rect x="241.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;1;1;0;0;0;0"/></rect>
<rect x="283.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="325.0" y="95.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="31.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="73.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="115.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;1;1;0;0;0"/></rect>
<rect x="157.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;1;1;0;0;0"/></rect>
<rect x="199.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;1;1;1;0;0;0;0"/></rect>
<rect x="241.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;1;1;1;0;0;0;0"/></rect>
<rect x="283.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="325.0" y="137.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="31.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="73.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="115.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;1;1;0;0;0"/></rect>
<rect x="157.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;1;1;0;0;0"/></rect>
<rect x="199.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;1;1;1;0;0;0;0"/></rect>
<rect x="241.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;1;1;1;0;0;0;0"/></rect>
<rect x="283.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="325.0" y="179.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;1;1;0;0;0;0;0"/></rect>
<rect x="31.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;0;0;1;0;0"/></rect>
<rect x="73.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;0;0;1;0;0"/></rect>
<rect x="115.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;1;1;0;0"/></rect>
<rect x="157.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;1;1;0;0"/></rect>
<rect x="199.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;1;0;0;0"/></rect>
<rect x="241.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;1;0;0;0"/></rect>
<rect x="283.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;0;0;0;0"/></rect>
<rect x="325.0" y="221.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;0;0;0;0"/></rect>
<rect x="31.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;0;0;1;0;0"/></rect>
<rect x="73.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;0;0;0;0;0;1;0;0"/></rect>
<rect x="115.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;1;1;0;0"/></rect>
<rect x="157.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;1;1;0;0"/></rect>
<rect x="199.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;1;0;0;0"/></rect>
<rect x="241.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;1;0;0;0"/></rect>
<rect x="283.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;0;0;0;0"/></rect>
<rect x="325.0" y="263.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;0;1;0;0;0;0;0;0;0"/></rect>
<rect x="31.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;0;0;0;0;0;0;0;1;1"/></rect>
<rect x="73.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;0;0;0;0;0;0;0;1;1"/></rect>
<rect x="115.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;1;0;0;0;0;0;1;1;1"/></rect>
<rect x="157.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;1;0;0;0;0;0;1;1;1"/></rect>
<rect x="199.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;0;0;0;0"/></rect>
<rect x="241.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;0;0;0;0"/></rect>
<rect x="283.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="325.0" y="305.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="31.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;0;0;0;0;0;0;0;1;1"/></rect>
<rect x="73.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;0;0;0;0;0;0;0;1;1"/></rect>
<rect x="115.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;1;0;0;0;0;0;1;1;1"/></rect>
<rect x="157.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;1;1;0;0;0;0;0;1;1;1"/></rect>
<rect x="199.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;0;0;0;0"/></rect>
<rect x="241.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826" values="0;0;1;0;0;0;0;0;0;0;0"/></rect>
<rect x="283.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<rect x="325.0" y="347.0" width="40.0" height="40.0" fill="#fecaca" stroke="#64748b" stroke-width="1" opacity="0"/>
<circle cx="90" cy="352" r="9" fill="#e5484d" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826;1.0000" values="90;90;180;260;310;290;230;170;140;130;90;90"/><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.1488;0.2280;0.3072;0.3865;0.4657;0.5449;0.6242;0.7034;0.7826;1.0000" values="352;352;322;252;172;122;152;232;302;352;352;352"/></circle>
<text x="30" y="418" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">カメラ（赤）が動くと、近いタイルが分割され、遠いタイルは粗いまま</text>
<text x="410" y="90" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">いま描くタイルの数</text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">13 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;0.1484;0.1488;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">19 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1484;0.1488;0.2277;0.2280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">22 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2277;0.2280;0.3069;0.3072;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">19 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3069;0.3072;0.3861;0.3865;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">19 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3861;0.3865;0.4654;0.4657;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">19 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4654;0.4657;0.5446;0.5449;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">25 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5446;0.5449;0.6238;0.6242;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">19 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6238;0.6242;0.7030;0.7034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">16 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7030;0.7034;0.7823;0.7826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="410" y="130" text-anchor="start" style="font-size:34px;font-weight:700;fill:#1f2937" opacity="0">13 枚<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7823;0.7826;1.0000;1.0000" values="0;0;1;1;0"/></text>
<rect x="410" y="170" width="22" height="18" fill="#bfdbfe" stroke="#64748b"/>
<text x="442" y="184" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">レベル 0（いちばん粗い）</text>
<rect x="410" y="200" width="22" height="18" fill="#bbf7d0" stroke="#64748b"/>
<text x="442" y="214" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">レベル 1（粗い）</text>
<rect x="410" y="230" width="22" height="18" fill="#fde68a" stroke="#64748b"/>
<text x="442" y="244" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">レベル 2（細かい）</text>
<rect x="410" y="260" width="22" height="18" fill="#fecaca" stroke="#64748b"/>
<text x="442" y="274" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">レベル 3（いちばん細かい）</text>
<text x="410" y="320" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b">全部を最高の細かさで描くと 64 枚。</text>
<text x="410" y="344" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b">カメラの近くだけ細かくして、数を抑える。</text>
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
- [継ぎ目](cracks.md)
