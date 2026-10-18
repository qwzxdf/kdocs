---
title: Hybrid Pipeline
tags:
  - 描画
---

# Hybrid Pipeline

**全画素にレイトレを使うと重いので、「SSR で当たった所は SSR、外れた所だけレイトレ」**という、**ハイブリッド構成**が**現実的**です。**さらに、粗さが高い所はプローブにフォールバック**します。このページでは、**ハイブリッドの組み立て方と、性能の工夫**を説明します。

!!! tip "ポイント"
    - **まず SSR。当たらなかった画素だけ、レイトレ**。
    - **粗さが高い画素は、プローブ**（ノイズが多く、レイトレの価値が低い）。
    - **半解像度でトレースして、アップサンプル**。
    - **レイの数・距離に、上限を設ける**。

<!-- fig:rt-hybrid-flow:begin -->

<svg class="fig illust motion" data-fig="rt-hybrid-flow" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rt-hybrid-flow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ハイブリッド:画素ごとに、使う方式を選ぶ</text>
<rect x="40" y="170" width="120" height="50" rx="8" fill="#1f2937" fill-opacity="0.18" stroke="#1f2937" stroke-width="2.5"/>
<text x="100.0" y="200.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">反射が必要な画素</text>
<rect x="210" y="170" width="150" height="50" rx="8" fill="#2563eb" fill-opacity="0.18" stroke="#2563eb" stroke-width="2.5"/>
<text x="285.0" y="200.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">SSR が当たった?</text>
<rect x="420" y="60" width="150" height="50" rx="8" fill="#2563eb" fill-opacity="0.18" stroke="#2563eb" stroke-width="2.5"/>
<text x="495.0" y="90.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">SSR の色を使う</text>
<rect x="420" y="170" width="150" height="50" rx="8" fill="#7c3aed" fill-opacity="0.18" stroke="#7c3aed" stroke-width="2.5"/>
<text x="495.0" y="200.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">粗さが高い?</text>
<rect x="620" y="120" width="130" height="50" rx="8" fill="#e5aa28" fill-opacity="0.18" stroke="#e5aa28" stroke-width="2.5"/>
<text x="685.0" y="150.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">プローブを使う</text>
<rect x="620" y="250" width="130" height="50" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2.5"/>
<text x="685.0" y="280.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">レイトレを使う</text>
<line x1="160" y1="195" x2="210" y2="195" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="360" y1="195" x2="420" y2="195" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="390" y1="185" x2="420" y2="90" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="570" y1="195" x2="620" y2="145" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="570" y1="200" x2="620" y2="270" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<text x="400" y="138" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2563eb">はい</text>
<text x="372" y="215" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">いいえ</text>
<text x="586" y="148" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5aa28">はい</text>
<text x="590" y="252" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">いいえ</text>
<circle cx="100" cy="195" r="10" fill="#e5484d" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.1310;0.1931;1.0000" values="100;100;285;495;495"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.1310;0.1931;1.0000" values="195;195;195;85;85"/></circle>
<text x="40" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d" opacity="0">画素 A(鏡面・当たった)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3446;0.3448;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="100" cy="195" r="10" fill="#2563eb" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.6066;0.6069;1.0000" values="0;0;1;1;0;0"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3448;0.4069;0.4690;0.5310;1.0000" values="100;100;285;495;685;685"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3448;0.4069;0.4690;0.5310;1.0000" values="195;195;195;195;275;275"/></circle>
<text x="40" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2563eb" opacity="0">画素 B(画面外へ出た・滑らか)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.6204;0.6207;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="100" cy="195" r="10" fill="#e5aa28" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;0.8825;0.8828;1.0000" values="0;0;1;1;0;0"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6207;0.6828;0.7448;0.8069;1.0000" values="100;100;285;495;685;685"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6207;0.6828;0.7448;0.8069;1.0000" values="195;195;195;195;145;145"/></circle>
<text x="40" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5aa28" opacity="0">画素 C(ざらざら・外れ)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;0.8963;0.8966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="390" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">SSR で当たれば最も安い。外れた画素だけ、レイトレかプローブへ。粗い面は、プローブで十分（ノイズが多く、レイトレの価値が低い）。</text>
</svg>

<!-- fig:rt-hybrid-flow:end -->

## ハイブリッド構成：SSR とレイトレの組み合わせ
**画面内に当たりがある**場合は、**SSR（Hi-Z）で足りる**ことが多いです。**画面に当たりがない**（画面外・裏側・失敗）レイだけを**レイトレ**にします。

ハイブリッド構成は、3 段階です。最初に、SSR（Hi-Z）を先に実行し、画面内で当たればその色を使います（安いため）。次に、当たらなかったレイだけをレイトレに回します。画面外へ出たレイや、厚みで弾かれたレイが対象です。最後に、両方の結果を画素ごとに選んで合成します。

利点は、レイトレのレイが大きく減ってコストが下がることと、SSR が画面内の細かさ（足元の映り込み）に強いことです。注意点は、SSR とレイトレで見た目（色・ぼけ）が違うと境目が見えることです。同じ BRDF・同じ色空間で揃えます。

**利点**：**レイトレのレイが大きく減る**（コスト削減）。<strong>SSR は画面内の細かさ（足元の映り込み）</strong>に強い。

**注意**：**SSR とレイトレで見た目（色・ぼけ）が違う**と**境目が見える**。**同じ BRDF・同じ色空間**でそろえます。

## 性能の工夫
| 工夫 | 内容 |
| --- | --- |
| **粗さによる、レイの省略** | 粗い面はレイを飛ばさない |
| **半分の解像度** | レイを半分の解像度で飛ばし、**アップサンプル** |
| **レイのソート・まとめ** | **似た方向・似たメッシュ**のレイを**まとめて処理**（コヒーレンス向上）。**シェーダー実行の並べ替え**（SER） |
| **レイの最大距離** | **短く**する（遠くは空・プローブ） |
| **インライン レイトレ**（`RayQuery`） | **コンピュート シェーダーから直接**（ヒット シェーダーなし）。**軽い処理**に向く |
| **LOD・簡易メッシュ** | **BVH 用に軽いメッシュ**を使う |
| **アルファ テスト** | **any-hit** は重い。**葉・フェンス**は必要最小限に |
| **動く物体の BVH 更新** | **リフィット**（再構築より安い）・**更新頻度の削減** |

## よくあるミス

??? failure "レイトレの負荷が、画面いっぱいで重い"
    **SSR で当たった画素は、レイトレを飛ばさない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **SSR → レイトレ → プローブ の順に、フォールバック**
    - [x] **半解像度とレイ数の上限で、コストを抑える**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [SSR Basics](../ssr-basics/index.md)
- [Denoising](denoise.md)
