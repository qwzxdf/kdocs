---
title: エイリアシングと安定化
tags:
  - 描画
---

# エイリアシングと安定化

**シャドウ マップの絵は、画面より低い解像度**であることが多く、**影の縁がギザギザ（エイリアシング）**になります。**エイリアシングには 2 種類**あり、**解像度不足（遠近）**と**テクセルの揺れ（カメラや光が動くと、縁が這う）**です。**後者は、光の行列をテクセルの単位に揃える「スナップ」**で**防げます**。このページでは、**2 種類の整理・テクセルのスナップ**を説明します。

!!! tip "ポイント"
    - **エイリアシング ＝ 画面の 1 画素が、マップの複数テクセルにまたがる / 逆**。
    - **遠近エイリアシング**：**近くで足りない**。**[カスケード](../cascaded.md)**で解決。
    - **揺れ**：**カメラが動くたびに、マップの格子と画面の対応が変わる**。**スナップ**で固定。
    - **スナップ ＝ 光の位置をテクセルの大きさの倍数に丸める**。

## 問題の整理
| 問題 | 症状 | 原因 | 対策 |
| --- | --- | --- | --- |
| **シャドウ アクネ** | 面に縞・斑点 | 深度の離散化で**自分自身を遮蔽物と誤判定** | [バイアス](../bias/index.md) |
| **ピーター パンニング** | 影が物体から**浮く** | バイアスが大きすぎる | バイアスの調整・法線オフセット |
| **エイリアシング** | 影の縁が**ギザギザ** | シャドウ マップの解像度が足りない | [カスケード](../cascaded.md)・高解像度・フィルタ |
| **縁がハード** | 影の縁がくっきりしすぎ | 点での比較（0/1）だけ | [PCF](../pcf.md)・[PCSS](../pcss.md) |
| **範囲外** | 画面の端で影が途切れる | シャドウ マップの範囲不足 | 範囲の設計・カスケード |
| **透明部分** | 葉・フェンスの影が板状 | 深度だけを描いている | [特殊なケース](../special-cases/index.md) |

<!-- fig:perspective-aliasing:begin -->

<svg class="fig illust motion" data-fig="perspective-aliasing" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-perspective-aliasing" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">遠近エイリアシング:近くはテクセルが粗く、遠くは細かすぎる</text>
<rect x="40" y="330" width="700" height="14" fill="#d6c7a1"/>
<circle cx="70" cy="150" r="9" fill="#2563eb"/>
<text x="60" y="136" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">カメラ</text>
<line x1="140" y1="344" x2="140" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="168" y1="344" x2="168" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="196" y1="344" x2="196" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="224" y1="344" x2="224" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="252" y1="344" x2="252" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="280" y1="344" x2="280" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="308" y1="344" x2="308" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="336" y1="344" x2="336" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="364" y1="344" x2="364" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="392" y1="344" x2="392" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="420" y1="344" x2="420" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="448" y1="344" x2="448" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="476" y1="344" x2="476" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="504" y1="344" x2="504" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="532" y1="344" x2="532" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="560" y1="344" x2="560" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="588" y1="344" x2="588" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="616" y1="344" x2="616" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="644" y1="344" x2="644" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="672" y1="344" x2="672" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="700" y1="344" x2="700" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="728" y1="344" x2="728" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="756" y1="344" x2="756" y2="356" stroke="#e5484d" stroke-width="2"/>
<line x1="784" y1="344" x2="784" y2="356" stroke="#e5484d" stroke-width="2"/>
<text x="140" y="374" text-anchor="start" style="font-size:12px;font-weight:500;fill:#e5484d">赤い目盛り = シャドウ マップのテクセル（地面上で等間隔）</text>
<line x1="70" y1="150" x2="1350.77" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.0905;0.0909;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="907.25" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1178;0.1182;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="686.88" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1451;0.1455;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="554.01" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1724;0.1727;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="464.37" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1996;0.2000;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="399.23" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2269;0.2273;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="349.31" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2542;0.2545;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="309.45" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2815;0.2818;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="276.58" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3087;0.3091;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="248.75" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3360;0.3364;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="224.64" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3633;0.3636;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="203.36" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3905;0.3909;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="184.23" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4178;0.4182;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="166.78" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4451;0.4455;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="150.64" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4724;0.4727;1.0000" values="0;0;1;1"/></line>
<line x1="70" y1="150" x2="135.51" y2="330" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4996;0.5000;1.0000" values="0;0;1;1"/></line>
<text x="40" y="56" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">画面の画素（青い線）は、等間隔に並ぶ<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.0905;0.0909;1.0000" values="1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">近く:1 画素が、地面の狭い範囲 → 1 テクセルに画素が何個も入る（粗い・ブロック状）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.0905;0.0909;0.5451;0.5455;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">遠く:1 画素が、地面の広い範囲 → 画素にテクセルが何個も入る（細かすぎて、ちらつく）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.5451;0.5455;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">対策:カスケード シャドウ マップ。近くは細かい別のマップ、遠くは粗いマップで、画素とテクセルの比を揃える。</text>
</svg>

<!-- fig:perspective-aliasing:end -->

## エイリアシングの 2 種類
シャドウ マップは、**解像度が有限**なので**縁がギザギザ**になります。その原因は 2 つに分けられます。

| 種類 | 原因 | 対策 |
| --- | --- | --- |
| **投影エイリアシング** | <strong>光の向きと面の向きが近い（斜め）</strong>と、**1 テクセルが面の上で細長く伸びる** | **スロープ バイアス・面の向きに応じた処理** |
| **遠近エイリアシング** | **カメラの近くは、画面上の 1 ピクセルが、シャドウ マップの 1 テクセルより小さい**（粗く見える）。**遠くは逆に過剰** | <strong>カスケード（距離ごとに分割）</strong>、**射影の工夫**（LiSPSM・TSM など） |

**カメラの近くで細かい影が必要**なのに**マップは全体を均等に**覆っているので、**近くが粗く**、**遠くが無駄**になります。**距離に応じて、解像度を配分**する方式（**カスケード**）が、これを解決します。

## 安定させる：テクセルのスナップ
カメラや光が動くと**シャドウ マップの範囲**が動き、**影の縁がちらつきます**（テクセルの境界がずれるため）。**範囲の位置をテクセル単位に揃える**と、ちらつきが止まります（[カスケード](../cascaded.md)）。

## よくあるミス

??? failure "カメラを動かすと、影の縁が泳ぐ（ちらつく）"
    **光の行列を、テクセル単位にスナップ**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **エイリアシングは、解像度不足と揺れの 2 種類**
    - [x] **テクセルのスナップで、揺れを防ぐ**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [シャドウ マップの基礎](index.md)
- [カスケード シャドウ マップ](../cascaded.md)
- [PCF](../pcf.md)
