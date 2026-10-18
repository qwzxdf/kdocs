---
title: Sorting
tags:
  - 描画
---

# Sorting

**半透明は、奥から手前の順に描かないと、結果が崩れます**。**物体単位のソート・パーティクル単位のソート・面ごとのソート**など、**粒度**があります。このページでは、**ソートの方法と、順序の決め方**を説明します。

!!! tip "ポイント"
    - **物体の中心の、カメラからの距離でソート**するのが**基本**。
    - **物体同士が入り組むと、ソートでは直らない**（OIT が必要）。
    - **パーティクルは、系統ごと・距離でソート**。
    - **描画順は、不透明 → 半透明（奥から手前）**。

## Sorting {#ソート}
**奥から手前**の順に描くため、**半透明のオブジェクトを、カメラからの距離で並べ替えます**。

```cpp
struct TransparentDraw {
  float distance_squared;
  uint32_t draw_index;
};

std::vector<TransparentDraw> sorted;
for (uint32_t i = 0; i < transparent_draws.size(); ++i) {
  Vector3 to_object = transparent_draws[i].center - camera_position;
  sorted.push_back({to_object.LengthSquared(), i});
}
std::sort(sorted.begin(), sorted.end(),
          [](const TransparentDraw& a, const TransparentDraw& b) {
            return a.distance_squared > b.distance_squared;
          });
```

| 点 | 説明 |
| --- | --- |
| **`LengthSquared`** | **距離の比較だけ**なので、**平方根は不要** |
| <strong>降順（遠い順）</strong> | **一番遠い物から**描く |
| **距離の基準** | **オブジェクトの中心**（または、<strong>カメラの前方ベクトルへの射影（深度）</strong>）。**射影のほうが、横に並んだ物の順序が安定** |
| **ソートのキー** | **透明度の種類（加算など順序不要のもの）を分けて**、**通常のものだけソート** |

<strong>カメラの前方ベクトルへの射影（ビュー空間の z）</strong>で**並べる**と、**カメラが回転しても、順序が安定**します。

```cpp
float view_depth = Vector3::Dot(center - camera_position, camera_forward);
```

### Limits of Sorting {#ソートの限界}

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **オブジェクトが交差** | **1 つの順序では、表せない**（互いに食い込む） | **分割する**・**OIT** |
| **自己重なり** | **1 つのメッシュの手前の面と奥の面**（ガラス瓶） | <strong>背面を先、前面を後に描く（2 パス）</strong> |
| **大きな物体** | **中心では、順序を決められない** | **分割する**・**OIT** |
| **パーティクル** | **数が多い**ので、**ソートが重い** | **GPU ソート・加算ブレンドで回避** |
| **ポップ** | **カメラが動くと、順序が突然入れ替わり、見た目が変わる** | **中心の取り方・OIT** |

### Self-Overlap (Two Passes) {#自己重なり2-パス}

**ガラスの瓶**のように、**閉じたメッシュ**は、**背面（奥の面）を先に描き、前面（手前の面）を後に描く**と、**正しい順序**に近づきます。

```cpp
context->RSSetState(cull_front_state);
DrawMesh();
context->RSSetState(cull_back_state);
DrawMesh();
```

2 パス描画の内容です。1 回目は前面カリングで、奥の面（背面）を描きます。2 回目は背面カリングで、手前の面（前面）を描きます。

<!-- fig:alpha-sort-order:begin -->

<svg class="fig illust motion" data-fig="alpha-sort-order" viewBox="0 0 780 390" role="img"><rect x="0" y="0" width="780" height="390" rx="14" fill="#ffffff"/>
<defs><marker id="arr-alpha-sort-order" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<mask id="as-mask-1-1" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
</mask>
<mask id="as-mask-1-2" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
<rect x="486" y="134" width="130" height="130" fill="#000000"/>
</mask>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">半透明は奥から手前の順に描く。順番を間違えると、透けなくなる</text>
<text x="40" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">正しい順:奥 → 中 → 手前</text>
<rect x="40" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="290" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="60" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><rect x="106" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><rect x="152" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">間違った順:手前 → 中 → 奥（深度を書く）</text>
<rect x="420" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="670" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="532" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-1)"><rect x="486" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-2)"><rect x="440" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
</g>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">左:重なりに赤・緑・青が全部透けて見える。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">右:手前が先に深度を書くので、奥の物が消えて透けない。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:alpha-sort-order:end -->

## Deciding Blend Order (Summary) {#ブレンド順序の決め方まとめ}
| 物 | ブレンド | ソート |
| --- | --- | --- |
| **ガラス・水面** | 通常 | **必要** |
| **炎・爆発・魔法** | 加算 | **不要** |
| **煙** | 通常（または乗算済み） | **必要** |
| <strong>影の板（ブロブ）</strong> | 乗算 | **不要** |
| **UI** | 通常 | **描画順を、レイヤーで決める** |

## Common Mistakes {#よくあるミス}

??? failure "入り組んだ半透明が、前後逆に見える"
    **ソートの粒度を細かく**する、または **OIT**を使う。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **不透明の後に、半透明を奥から手前へ**
    - [x] **入り組むなら、OIT**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [Alpha Blending and Sorting](index.md)
- [OIT](../oit/index.md)
- [Blend State](blend-state.md)
