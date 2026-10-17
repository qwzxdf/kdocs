---
title: 地形の LOD
tags:
  - 描画
---

# 地形の LOD

**広大な地形を全部最高の細かさで描く**ことは**できません**。**近くは細かく、遠くは粗く**する**LOD**（Level of Detail、詳細度の切り替え）が**必要**です。**遠くの 1 マスは、画面上で 1 ピクセルより小さい**ので、**細かい三角形を描いても見た目は変わらず、無駄**になります。このページでは、**LOD の考え方・四分木（CDLOD）・クリップマップ・継ぎ目（クラック）の対策・ハードウェア テッセレーション・モーフィング**を説明します。

!!! tip "ポイント"
    - 目標 ＝ <strong>三角形 1 枚が、画面上で一定の大きさ（例：数ピクセル）</strong>になるようにする。
    - <strong>四分木（CDLOD）</strong>：<strong>広いタイルを近いほど 4 分割</strong>して細かくする。
    - <strong>クリップマップ</strong>：<strong>カメラ中心の入れ子の正方形リング</strong>（<strong>近いほど細かい</strong>）。
    - <strong>LOD の境目には「継ぎ目（クラック）」</strong>が出る：<strong>モーフィング</strong>か<strong>スカート</strong>で<strong>埋める</strong>。
    - <strong>モーフィング</strong> ＝ <strong>LOD が切り替わる手前で、細かい頂点を粗い側へ滑らかに寄せる</strong>（<strong>ポップを消す</strong>）。
    - <strong>ハードウェア テッセレーション</strong>は<strong>パッチを GPU で細分</strong>。<strong>距離でテッセレーション係数を変える</strong>。

## なぜ LOD が要るか

**透視投影では遠くの物は小さく見える**ので、**同じ大きさのマスでも遠くは画面上でとても小さい**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="距離とマスの大きさ">
<text x="20" y="24" class="fig-title">遠くのマスは、画面上で小さい：同じ細かさで描くと無駄</text>
<polygon points="60,200 740,200 740,60 60,120" fill="#2ea043" fill-opacity="0.15"/>
<g stroke="currentColor" stroke-opacity="0.5">
<line x1="60" y1="200" x2="60" y2="120"/><line x1="140" y1="200" x2="140" y2="128"/><line x1="220" y1="200" x2="220" y2="135"/><line x1="300" y1="200" x2="300" y2="141"/><line x1="380" y1="200" x2="380" y2="146"/><line x1="460" y1="200" x2="460" y2="150"/><line x1="540" y1="200" x2="540" y2="153"/><line x1="620" y1="200" x2="620" y2="156"/><line x1="700" y1="200" x2="700" y2="158"/>
</g>
<circle cx="40" cy="190" r="8" fill="#e5484d"/>
<text x="30" y="214" style="font-size:12px;fill:#e5484d">カメラ</text>
<text x="500" y="100" style="font-size:12px">遠く：マスが画面上で細く、数が多すぎる</text>
</svg>

| 目標 | 内容 |
| --- | --- |
| **画面上の誤差** | **LOD を下げたことによる、見た目のずれが数ピクセル以下** |
| **三角形の大きさ** | **画面上でおおむね均一**（**小さな三角形は、GPU が不得意**） |
| **総数の上限** | **視点がどこでも三角形の数がほぼ一定** |

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

## モーフィング

<strong>LOD が切り替わる瞬間に、地形の形が急に変わると「ポップ」</strong>が見えます。**モーフィング**は、**切り替わる手前から、細かい側の頂点を粗い側の位置へ滑らかに寄せる**手法です。

**粗い LOD では、頂点が 1 つおきに間引かれる**ので、**間引かれる側の頂点を両隣の頂点の中点へ寄せます**。

<div class="formula">位置 = lerp( 自分の高さ,　両隣の平均の高さ,　morph )　（morph：0 → 1）</div>

```hlsl
float MorphFactor(float distance_to_camera, float range_start, float range_end) {
  float t = (distance_to_camera - range_start) / (range_end - range_start);
  return saturate((t - 0.7) / 0.3);
}

float2 MorphXZ(float2 grid_position, float morph) {
  float2 fraction = frac(grid_position * (kGridSize * 0.5)) * 2.0 / kGridSize;
  return grid_position - fraction * morph;
}

float2 xz = MorphXZ(input.grid_position, morph) * node_size + node_origin;
float height = SampleHeight(xz);
```

| 点 | 説明 |
| --- | --- |
| **`morph` の範囲** | **LOD の距離範囲の最後の 30 %** で**0 → 1**。**範囲の前半はそのまま** |
| **奇数番の頂点を寄せる** | **粗い LOD に存在しない頂点が、偶数番の頂点の位置に重なる** |
| **効果** | **切り替え時に形が同じ**になり、**ポップが消える** |
| **高さも補間** | **XZ を寄せたうえで高さを読み直す** |

## 継ぎ目（クラック）

**LOD の違うタイルが隣り合う**と、<strong>境界で頂点の位置が合わず、隙間（クラック）</strong>ができます。**細かい側の境界の頂点が、粗い側の辺の上にないため**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="LOD の継ぎ目">
<text x="20" y="24" class="fig-title">LOD の継ぎ目：細かい側の頂点が、粗い側の辺から浮く</text>
<line x1="120" y1="150" x2="420" y2="150" stroke="currentColor" stroke-opacity="0.7" stroke-width="2"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="2" points="120,150 195,128 270,150 345,118 420,150"/>
<circle cx="195" cy="128" r="4" fill="#e5484d"/><circle cx="345" cy="118" r="4" fill="#e5484d"/>
<text x="120" y="190" style="font-size:12px">粗い側の辺 / 細かい側（青）の中間頂点が、辺から離れる → 隙間</text>
<line x1="500" y1="150" x2="740" y2="150" stroke="currentColor" stroke-opacity="0.7" stroke-width="2"/>
<polyline fill="none" stroke="#2ea043" stroke-width="2" points="500,150 560,150 620,150 680,150 740,150"/>
<text x="500" y="190" style="font-size:12px">対策：中間頂点を、辺の上へ寄せる</text>
</svg>

| 対策 | 内容 |
| --- | --- |
| **モーフィング** | **境界の頂点が粗い側の辺の上に来るまで、距離で寄せる**。<strong>連続的（CDLOD はこれ）</strong> |
| **スカート** | **タイルの縁から、下向きに垂れ幕を追加**して**隙間を隠す**。**簡単だが見た目が少し粗い** |
| **境界専用のインデックス** | **隣が粗いとき、細かい側の境界を三角形の貼り方で繋ぐ**（**LOD の組み合わせごとにメッシュが要る**） |
| **共通の頂点を使う** | **境界の頂点の高さを両側で同じ式（粗い側の補間）で決める** |
| **隣のレベル差を 1 までに制限** | **隣接するタイルの LOD の差を 1 以内**にする（**四分木の制約**） |

## クリップマップ

**ジオメトリ クリップマップ**（Losasso & Hoppe、2004）は、**カメラを中心に入れ子になった正方形リング**で**LOD を表現**します。**一番内側が最も細かく、外側ほど 2 倍ずつ粗く**なります。

| 項目 | 内容 |
| --- | --- |
| **構造** | **同じ頂点数の正方形リングが、倍々の大きさで重なる**（例：各 255×255） |
| **カメラ追従** | **カメラが動くとリングをグリッド単位でスクロール**（**円環バッファ**で高さを更新） |
| **利点** | **三角形の数が一定**。**構造が単純**。**GPU に向く** |
| **欠点** | **視点から遠くてもリングの数だけは描く**（**画面外を捨てにくい**）。**高さデータをリングごとに管理** |
| **用途** | **広大な地形・海面**（[水面のクリップマップ](../water/waves.md)と同じ構造） |

**四分木はノードごとにカリングができて柔軟**、**クリップマップは、構造が単純で三角形数が一定**という**違い**があります。

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

## 高さマップの LOD（ミップ）

**メッシュだけでなく、高さマップもミップを使います**。**遠くの頂点は粗いミップから読む**と**ちらつかず、メモリ アクセスも減ります**。

| 点 | 説明 |
| --- | --- |
| **ミップ レベル = LOD レベル** | **LOD が 1 下がるごとに、ミップを 1 上げる** |
| **フィルタ** | **高さのミップは、平均**でよいが**最大値のミップ**も**カリング**に使える |
| **最小・最大の高さ** | **ノードの境界ボックスに使う** |

## LOD の選び方の目安

| 状況 | 向く方式 |
| --- | --- |
| <strong>標準的なゲーム（数 km）</strong> | <strong>四分木（CDLOD）</strong>。**モーフィング付き** |
| **無限に近い地形・海** | **クリップマップ** |
| **既存のエンジンで簡単に** | **テッセレーション ＋ 距離係数** |
| **非常に大規模・密** | **メッシュ シェーダー ＋ GPU ドリブン**（[GPU Driven](../../rendering/index.md)） |

## よくあるミス

??? failure "LOD の切り替えで、地形がポップする"
    **モーフィング**を入れる。**切り替え範囲の最後の 30 % で寄せる**。

??? failure "LOD の境界に、隙間（空が見える）ができる"
    **境界の頂点を寄せる・スカートを付ける**。

??? failure "テッセレーションの係数が隣と違って、割れる"
    **辺の係数は辺の両端のパッチで同じ値**を使う（**辺の中心の位置から計算**）。

??? failure "遠景のミップを使わず、遠くの地形がちらつく"
    **LOD に合わせて、高さマップのミップ レベルを上げる**。

??? failure "当たり判定を LOD のメッシュに合わせて、足がずれる"
    **当たり判定は最も細かい高さマップ**で取る。

## これだけ覚える

!!! abstract "まとめ"
    - [x] LOD ＝ <strong>近くは細かく、遠くは粗く</strong>。<strong>画面上の三角形の大きさを揃える</strong>
    - [x] <strong>四分木（CDLOD）</strong>は<strong>近いノードを 4 分割</strong>。<strong>全ノード同じ格子を使い回す</strong>
    - [x] <strong>モーフィング</strong>で<strong>ポップと継ぎ目</strong>を<strong>同時に消す</strong>
    - [x] <strong>クリップマップ</strong>は<strong>入れ子のリング</strong>。<strong>三角形数が一定</strong>
    - [x] <strong>テッセレーション</strong>は<strong>辺の係数を隣と揃える</strong>

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps: Terrain Rendering Using Nested Regular Grids"（SIGGRAPH 2004）
- Ulrich, "Rendering Massive Terrains using Chunked Level of Detail Control"（SIGGRAPH 2002）

## 関連ページ

- [地形](index.md)
- [高さマップとメッシュ](heightmap-mesh.md)
- [地形のテクスチャ](texturing.md)
- [波のジオメトリ](../water/waves.md)
