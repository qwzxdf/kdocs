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

## 考え方：裏面を、描く

通常、シャドウ パスでは、**光に向いた面（表面）**の、深度が、シャドウ マップに、保存されます。メイン パスで、**同じ表面**を、描くとき、**保存された深度と、画素の深度が、ほぼ同じ**になり、**自己影**（シャドウ アクネ）が、出やすくなります。

**表面を、カリング**し、**裏面**（光から、遠い側の面）だけを、**描く**と、シャドウ マップには、**物の、奥側の面の深度**が、保存されます。メイン パスで、**表面を、描くとき**、**保存された深度（奥側）**は、**画素の深度（表側）より、物の厚みぶん、遠い**ので、**自己影に、なりません**。**物の厚みが、そのまま、バイアスの役割**を、果たします。

```text
              光
              ↓
           ┌────┐   ← 表面（光に、向いた面）  カリングして、描かない
           │ 物 │
           └────┘   ← 裏面（光から、遠い面）  これを、描く → シャドウ マップに、保存される
 ━━━━━━━━━━━━━━━━━━  地面

 メイン パスで、物の表面を描くとき:  画素の深度（表面） < 保存された深度（裏面）  → 光が当たる（自己影なし）
```

## 実装

シャドウ パスの、ラスタライザー ステートで、**表面を、カリング**します（`CULL_FRONT`）。**このサイトの、座標系は、反時計回りが表**なので、`FrontCounterClockwise = TRUE` と、組み合わせます。

```cpp
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_FRONT;                 // 光に向いた面（表面）を、描かない = 裏面を、描く
rs.FrontCounterClockwise = TRUE;                // 反時計回りが表
rs.DepthClipEnable = TRUE;
device->CreateRasterizerState(&rs, &shadow_rs_front_cull);
```

| 設定 | 内容 |
| --- | --- |
| `CullMode = FRONT` | **表面を、描かない**（裏面だけが、深度に、書かれる） |
| `FrontCounterClockwise` | **表裏の判定**の、向き。メインの描画と、**同じ**にする |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **バイアスが、ほぼ、不要**（物の厚みが、バイアスの代わり） |
| 長所 | **ピーター パンニングが、起きにくい**（接地部分で、影が、地面に、つながる） |
| 長所 | 設定が、**ラスタライザー ステートの、1 つだけ** |
| 短所 | **薄い物**（壁、板、葉）では、**表裏の、間隔が、無く**、影が、**欠ける**、または、**自己影が、残る** |
| 短所 | **閉じていない、メッシュ**（地面、1 枚の板）には、裏面が、無い。**地面は、表面を描く**必要 |
| 短所 | **地面（受け手）の、影**は、地面の、表面が、**自己影を、起こす**。地面は、**裏面を描いて**も、**意味がない**（地面の、下には、何もない） |

## 使い分け

**影を落とす物**（キャラクター、建物、木）と、**影を受ける物**（地面）で、**扱いを、分けます**。

| 物 | シャドウ パスで、描く面 | 理由 |
| --- | --- | --- |
| **閉じた、厚みのある物**（キャラクター、岩、建物の、塊） | **裏面**（表面を、カリング） | 厚みが、バイアスになる |
| **地面**（地形）| **表面**（通常）+ バイアス | 地面は、閉じていない。裏面を描くと、地面全体が、影を、**落とさなく**なる |
| **薄い物**（壁、フェンス、葉） | **両面** | 厚みが、無いので、どちらの面も、必要 |

実装では、**物（マテリアル）ごと**に、シャドウ パスの、**ラスタライザー ステートを、切り替えます**。

```cpp
// マテリアルごとに、シャドウ パスの、カリングを、選ぶ。
for (const Mesh& m : shadow_casters) {
  switch (m.shadow_cull) {
    case ShadowCull::Back:  context->RSSetState(rs_cull_back.Get());  break;   // 地面（表面を描く）
    case ShadowCull::Front: context->RSSetState(rs_cull_front.Get()); break;   // 厚みのある物（裏面を描く）
    case ShadowCull::None:  context->RSSetState(rs_cull_none.Get());  break;   // 薄い物（両面）
  }
  Draw(m);
}
```

## 裏面を描く方法の、落とし穴

| 落とし穴 | 内容 |
| --- | --- |
| **影の、始まり**が、**少し、ずれる** | 物の、**奥側**の深度を、使うので、**影が、物の厚み分、奥から、始まる**。**接地**は、きれいだが、**影の始まりが、物の、足元より、後ろ**になることがある |
| **光が、物の、側面に、当たる**とき | 側面（光と、ほぼ平行）では、**表裏の、区別が、あいまい**。**側面の、影の、境目**が、ちらつくことがある |
| **カメラが、物の中**に入る | 描画では、メッシュの内側を、見る。影には、影響しない |

**単独で、使う**というより、**他のバイアス**（法線オフセット、小さな、定数バイアス）と、**組み合わせて**、**バイアスの、量を、小さく**する目的で、使うのが、現実的です。

## よくあるミス

??? failure "薄い板（葉・布）が、影を落とさなくなった"
    **薄い物は、両面描画に切り替える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **裏面だけを描いて、アクネを避ける**
    - [x] **閉じた立体向き**。**薄い物は不向き**

## 参考

- Wang, Molnar, "Second-Depth Shadow Mapping", UNC Technical Report TR94-019, 1994（第 2 深度シャドウ マップ。裏面を使う考え方）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）
- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）

## 関連ページ

- [Shadow Bias](index.md)
- [Rendering Depth](../shadow-map-basics/render-depth.md)
- [Special Cases](../special-cases/index.md)
