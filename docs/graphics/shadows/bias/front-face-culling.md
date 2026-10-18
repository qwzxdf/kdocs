---
title: Front-Face Culling
tags:
  - 描画
---

# Front-Face Culling

**シャドウ マップを描くとき、前面（光に向いた面）ではなく、裏面だけを描く**と、**深度が、物体の「奥の面」の深度になり、受け手の表面との差が大きくなって、アクネが起きにくくなります**。**簡単な対策**ですが、**薄い物体では、影が欠ける・光が漏れる**ので**向き不向き**があります。このページでは、**考え方・設定・向く物と向かない物**を説明します。

!!! tip "ポイント"
    - **前面カリング ＝ シャドウ マップに裏面だけを描く**。
    - **受け手の表面（前面）より奥の深度が記録される**ので、**アクネが出にくい**。
    - **閉じた立体**で**有効**。**薄い板・片面の物では、影が欠ける**。
    - **ラスタライザの `CullMode = FRONT`** で**設定**。

<!-- fig:front-face-cull:begin -->

<svg class="fig illust motion" data-fig="front-face-cull" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-front-face-cull" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">前面カリング:裏面の深度を、シャドウ マップに入れる</text>
<text x="200" y="80" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#e5484d">表面を描く（通常）</text>
<rect x="130" y="130" width="140" height="150" fill="#b8794b" fill-opacity="0.5" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="80" cy="100" r="12" fill="#e5aa28"/>
<line x1="80" y1="100" x2="160" y2="130" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<line x1="40" y1="330" x2="370" y2="330" stroke="#a8a29e" stroke-width="3"/>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><line x1="130" y1="130" x2="270" y2="130" stroke="#e5484d" stroke-width="5"/>
<text x="200" y="120" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">記録される深度（表面）</text>
</g>
<circle cx="200" cy="130" r="7" fill="#ffffff" stroke="#1f2937" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;1.0000" values="0;0;1;1"/></circle>
<text x="40" y="366" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937" opacity="0">上面の点:記録と同じ深度 → 誤差で、縞（アクネ）が出る<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1849;0.1852;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="570" y="80" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">裏面を描く（前面カリング）</text>
<rect x="500" y="130" width="140" height="150" fill="#b8794b" fill-opacity="0.5" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="450" cy="100" r="12" fill="#e5aa28"/>
<line x1="450" y1="100" x2="530" y2="130" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<line x1="410" y1="330" x2="740" y2="330" stroke="#a8a29e" stroke-width="3"/>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;1.0000" values="0;0;1;1"/><line x1="500" y1="280" x2="640" y2="280" stroke="#2ea043" stroke-width="5"/>
<text x="570" y="304" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">記録される深度（裏面）</text>
</g>
<circle cx="570" cy="130" r="7" fill="#ffffff" stroke="#1f2937" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;1.0000" values="0;0;1;1"/></circle>
<text x="410" y="366" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937" opacity="0">上面の点:記録（裏面）よりずっと手前 → 余裕があり、縞が出ない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">代償:薄い板（厚みが無い物）では、裏面が表面に近く、余裕が足りない（光漏れしやすい）。</text>
</svg>

<!-- fig:front-face-cull:end -->

## 対策 5：前面カリングで描く（裏面レンダリング）
**シャドウ マップを描くとき**、<strong>表面（光に向いた面）ではなく、裏面（光に背を向けた面）</strong>を描く方法です。

表面を描く場合と裏面を描く場合の違いは、次のとおりです。表面（光に向いた面）を描くと、光に向いた面の深度が保存されます。受け手の面と深度がほぼ同じなので、アクネが出やすくなりますが、ピーター パンニングは小さいです。裏面（光に背を向けた面）を描くと、物体の裏側の深度が保存されます。これは表面より奥にあるので、表面は裏面より手前にあることになり、自己遮蔽にならず、アクネが出にくいです。その代わり、薄い物体では、裏面と表面の間隔が狭いために、影が離れたり漏れたりするピーター パンニングが出ます。

**閉じた、厚みのあるメッシュ**では、**裏面レンダリング**が**アクネを減らす**のに効きます。**薄い板・葉・布**には使えません（影が浮いたり、漏れたりする）。

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.CullMode = D3D11_CULL_FRONT;
```

**表裏の定義**は**時計回りが表**（[座標系](../../../gamemath/coordinate-systems.md)）に従います。**光から見て**、表を向いた面（光に面した面）が**カリングされ**、裏が描かれます。

## よくあるミス

??? failure "薄い板（葉・布）が、影を落とさなくなった"
    **薄い物は、両面描画に切り替える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **裏面だけを描いて、アクネを避ける**
    - [x] **閉じた立体向き**。**薄い物は不向き**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadow Bias](index.md)
- [Rendering Depth](../shadow-map-basics/render-depth.md)
- [Special Cases](../special-cases/index.md)
