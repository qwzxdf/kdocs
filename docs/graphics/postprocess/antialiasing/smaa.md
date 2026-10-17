---
title: SMAA
tags:
  - 描画
---

# SMAA

<strong>SMAA（Subpixel Morphological Anti-Aliasing）</strong>は、<strong>FXAA と同じ「画像だけを見る後処理 AA」</strong>ですが<strong>縁の形（パターン）を分類して、縁がどれだけ画素を覆っているかを「計算」</strong>する**ので、FXAA より、文字や模様をぼかさず、縁がきれい**です。<strong>3 つのパス（縁検出 → 重みの計算 → ブレンド）</strong>で**構成**され、**FXAA より少し重い**ですが、**画質のバランスが良い**ので**広く使われます**。このページでは、<strong>3 パスの流れ・縁の検出・縁パターンと重みの計算（ルックアップ テクスチャ）・ブレンド・時間方向の拡張（SMAA T2x）</strong>を説明します。

!!! tip "ポイント"
    - SMAA ＝ <strong>縁を検出 → 縁の形を分類して、画素の覆われ具合（重み）を計算 → 重みで隣の画素と混ぜる</strong>。
    - <strong>3 パス</strong>：<strong>① 縁検出</strong>・<strong>② ブレンドの重み</strong>・<strong>③ 近傍ブレンド</strong>。
    - <strong>FXAA より、文字や細部をぼかさない</strong>。<strong>縁の形に応じて、正確に混ぜる</strong>。
    - <strong>事前計算した 2 枚のテクスチャ（Area・Search）</strong>を<strong>使う</strong>。
    - <strong>縁検出は輝度（または色・深度）の差</strong>で行う。
    - <strong>SMAA T2x</strong> は<strong>ジッターと時間蓄積を足した版</strong>（<strong>TAA の簡易版</strong>）。

## 3 つのパス

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="SMAA の 3 パス">
<text x="20" y="26" class="fig-title">SMAA：3 つのパス</text>
<defs><marker id="sm-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="13">
<rect x="20" y="56" width="210" height="100" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/><text x="125" y="86" text-anchor="middle" style="font-weight:700">① 縁の検出</text><text x="125" y="110" text-anchor="middle" style="font-size:11px">輝度の差が大きい画素に、</text><text x="125" y="126" text-anchor="middle" style="font-size:11px">左・上の縁フラグを立てる</text><text x="125" y="144" text-anchor="middle" style="font-size:11px">出力：縁テクスチャ（RG）</text>
<rect x="285" y="56" width="210" height="100" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/><text x="390" y="86" text-anchor="middle" style="font-weight:700">② ブレンドの重み</text><text x="390" y="110" text-anchor="middle" style="font-size:11px">縁の形（L・Z・U など）を</text><text x="390" y="126" text-anchor="middle" style="font-size:11px">分類して、重みを計算</text><text x="390" y="144" text-anchor="middle" style="font-size:11px">出力：重みテクスチャ（RGBA）</text>
<rect x="550" y="56" width="210" height="100" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/><text x="655" y="86" text-anchor="middle" style="font-weight:700">③ 近傍ブレンド</text><text x="655" y="110" text-anchor="middle" style="font-size:11px">重みに従って、</text><text x="655" y="126" text-anchor="middle" style="font-size:11px">元の画像の隣の画素と混ぜる</text><text x="655" y="144" text-anchor="middle" style="font-size:11px">出力：AA 済みの画像</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="232" y1="106" x2="283" y2="106" marker-end="url(#sm-arrow)"/><line x1="497" y1="106" x2="548" y2="106" marker-end="url(#sm-arrow)"/></g>
</svg>

| パス | 入力 | 出力 |
| --- | --- | --- |
| **① 縁検出** | **色（輝度）または深度** | <strong>縁テクスチャ（`R8G8`）：各画素の「左の縁」「上の縁」</strong> |
| **② ブレンドの重み** | **縁テクスチャ・Area・Search** | <strong>重みテクスチャ（`R8G8B8A8`）</strong> |
| **③ 近傍ブレンド** | **元の画像・重みテクスチャ** | **最終画像** |

## ① 縁の検出

**画素とその左・上の画素の輝度を比べ、差がしきい値以上なら縁**です（<strong>さらに「局所コントラストの適応」</strong>で、**近くにより強い縁があれば、弱い縁を無視**します）。

```hlsl
float2 EdgeDetection(float2 uv) {
  float l = Luma(color.SampleLevel(point_clamp, uv, 0).rgb);
  float l_left = Luma(color.SampleLevel(point_clamp, uv + float2(-1, 0) * texel, 0).rgb);
  float l_top = Luma(color.SampleLevel(point_clamp, uv + float2(0, -1) * texel, 0).rgb);
  float2 delta = abs(l - float2(l_left, l_top));
  float2 edges = step(kThreshold, delta);
  return edges;
}
```

| 点 | 説明 |
| --- | --- |
| **左と上** | **各画素が自分の「左の境」「上の境」の縁を担当**（**重複を避ける**） |
| <strong>`kThreshold`（0.05〜0.1）</strong> | **縁とみなす輝度差** |
| **局所コントラスト適応** | <strong>「近くにもっと強い縁がある」とき、弱い縁を捨てる</strong>（**テクスチャの細部を縁と誤認しない**） |
| **深度・色での検出** | **輝度のほか、深度や色（RGB の差）でも検出できる** |

## ② ブレンドの重み

<strong>縁を縁に沿って両方向へたどり、縁の端の形（L 字・Z 字・U 字など）</strong>を**判定**します。<strong>その形と画素の位置から、「この画素のうち、反対側に属する面積の割合（＝ブレンドの重み）」</strong>を**計算**します。

| 形 | 意味 |
| --- | --- |
| **直線** | <strong>まっすぐな縁（端が両方開いている）</strong> |
| **L 字** | **縁の端が直角に曲がっている** |
| **Z・U 字** | **縁の端がジグザグ・コの字** |

**面積の計算は事前に計算した 2 枚のテクスチャ**で**表引き**します。

| テクスチャ | 内容 |
| --- | --- |
| **Area テクスチャ** | <strong>縁の形と画素の位置 → 覆われる面積（重み）</strong> |
| **Search テクスチャ** | **縁をたどるときの探索の歩数を効率よく決める** |

これらは**公開されているデータ**をそのまま使います（**自分で作る必要はありません**）。

<!-- fig:smaa-edge-weights:begin -->

<svg class="fig illust motion" data-fig="smaa-edge-weights" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-smaa-edge-weights" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">SMAA:縁を見つけ、本当の線の面積を求めて、画素を混ぜる</text>
<rect x="40" y="90" width="61" height="61" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#191919;#4c4c4c"/></rect>
<rect x="102" y="90" width="61" height="61" fill="#191919"/>
<rect x="164" y="90" width="61" height="61" fill="#191919"/>
<rect x="226" y="90" width="61" height="61" fill="#191919"/>
<rect x="288" y="90" width="61" height="61" fill="#191919"/>
<rect x="350" y="90" width="61" height="61" fill="#191919"/>
<rect x="412" y="90" width="61" height="61" fill="#191919"/>
<rect x="474" y="90" width="61" height="61" fill="#191919"/>
<rect x="40" y="152" width="61" height="61" fill="#f2f2f2"/>
<rect x="102" y="152" width="61" height="61" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#f2f2f2;#ababab"/></rect>
<rect x="164" y="152" width="61" height="61" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#191919;#383838"/></rect>
<rect x="226" y="152" width="61" height="61" fill="#191919"/>
<rect x="288" y="152" width="61" height="61" fill="#191919"/>
<rect x="350" y="152" width="61" height="61" fill="#191919"/>
<rect x="412" y="152" width="61" height="61" fill="#191919"/>
<rect x="474" y="152" width="61" height="61" fill="#191919"/>
<rect x="40" y="214" width="61" height="61" fill="#f2f2f2"/>
<rect x="102" y="214" width="61" height="61" fill="#f2f2f2"/>
<rect x="164" y="214" width="61" height="61" fill="#f2f2f2"/>
<rect x="226" y="214" width="61" height="61" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#f2f2f2;#979797"/></rect>
<rect x="288" y="214" width="61" height="61" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#191919;#2a2a2a"/></rect>
<rect x="350" y="214" width="61" height="61" fill="#191919"/>
<rect x="412" y="214" width="61" height="61" fill="#191919"/>
<rect x="474" y="214" width="61" height="61" fill="#191919"/>
<rect x="40" y="276" width="61" height="61" fill="#f2f2f2"/>
<rect x="102" y="276" width="61" height="61" fill="#f2f2f2"/>
<rect x="164" y="276" width="61" height="61" fill="#f2f2f2"/>
<rect x="226" y="276" width="61" height="61" fill="#f2f2f2"/>
<rect x="288" y="276" width="61" height="61" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#f2f2f2;#e5e5e5"/></rect>
<rect x="350" y="276" width="61" height="61" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#191919;#828282"/></rect>
<rect x="412" y="276" width="61" height="61" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#191919;#202020"/></rect>
<rect x="474" y="276" width="61" height="61" fill="#191919"/>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="0;0;1;1"/><line x1="40" y1="152" x2="102" y2="152" stroke="#e5aa28" stroke-width="5"/>
<line x1="102" y1="152" x2="164" y2="152" stroke="#e5aa28" stroke-width="5"/>
<line x1="164" y1="152" x2="164" y2="214" stroke="#e5aa28" stroke-width="5"/>
<line x1="164" y1="214" x2="226" y2="214" stroke="#e5aa28" stroke-width="5"/>
<line x1="226" y1="214" x2="288" y2="214" stroke="#e5aa28" stroke-width="5"/>
<line x1="288" y1="214" x2="288" y2="276" stroke="#e5aa28" stroke-width="5"/>
<line x1="288" y1="276" x2="350" y2="276" stroke="#e5aa28" stroke-width="5"/>
<line x1="350" y1="276" x2="350" y2="338" stroke="#e5aa28" stroke-width="5"/>
</g>
<line x1="40" y1="121.0" x2="536" y2="393.8" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></line>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;0.6797;0.6800;1.0000" values="0;0;1;1;0;0"/><text x="71.0" y="126.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.77</text>
<text x="133.0" y="188.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.33</text>
<text x="195.0" y="188.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.86</text>
<text x="257.0" y="250.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.42</text>
<text x="319.0" y="250.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.92</text>
<text x="319.0" y="312.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.06</text>
<text x="381.0" y="312.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.52</text>
<text x="443.0" y="312.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">0.97</text>
</g>
<text x="40" y="370" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">元の画像:縁がギザギザ（階段）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="1;1;0;0"/></text>
<text x="40" y="370" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 隣り合う画素の明るさの差で、縁（橙）を見つける<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="370" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 縁の形（階段のパターン）から、本当の線（青）を推定する<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4797;0.4800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="370" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 各画素の中で、線が覆う面積（0〜1）を求める<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;0.6797;0.6800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="370" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ その面積で、隣の画素と混ぜる → なめらかな縁<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6797;0.6800;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:smaa-edge-weights:end -->

## ③ 近傍ブレンド

**重みテクスチャの値に従い、元の画像の隣の画素の色を混ぜます**。**重みが 0 なら、元のまま**です。

```hlsl
float4 NeighborhoodBlending(float2 uv) {
  float4 weights;
  weights.x = blend_weights.SampleLevel(point_clamp, uv + float2(0, 1) * texel, 0).a;
  weights.y = blend_weights.SampleLevel(point_clamp, uv + float2(1, 0) * texel, 0).g;
  weights.zw = blend_weights.SampleLevel(point_clamp, uv, 0).xz;

  if (dot(weights, 1.0) < 1e-5) {
    return color.SampleLevel(linear_clamp, uv, 0);
  }
  bool horizontal = max(weights.x, weights.z) > max(weights.y, weights.w);
  float4 offset = horizontal ? float4(weights.x > weights.z ? -1 : 1, 0, 0, 0) : float4(0, weights.y > weights.w ? -1 : 1, 0, 0);
  float amount = horizontal ? max(weights.x, weights.z) : max(weights.y, weights.w);
  float3 center = color.SampleLevel(linear_clamp, uv, 0).rgb;
  float3 neighbor = color.SampleLevel(linear_clamp, uv + offset.xy * texel, 0).rgb;
  return float4(lerp(center, neighbor, amount), 1.0);
}
```

**重みが 0 の画素（大半）は、そのまま返す**ので**縁でない領域は、まったくぼけません**。

## FXAA との違い

| 項目 | FXAA | SMAA |
| --- | --- | --- |
| **パス数** | **1** | **3** |
| **縁の扱い** | **経験則でぼかす** | **形を分類し、面積から重みを計算** |
| **文字・細部のぼけ** | **やや出る** | **少ない** |
| **斜めの縁** | **そこそこ** | **きれい** |
| **コスト** | **最小** | **FXAA の 2〜3 倍** |

## SMAA T2x（時間方向）

**SMAA に、TAA のようなジッターと時間蓄積**を**足した**のが**SMAA T2x**です。**1 フレームごとに半画素ずらして描き、前のフレームと混ぜる**ことで、**時間的なちらつきも抑えます**（[TAA](taa.md)）。**SMAA 1x（空間のみ）で足りない場合の軽量な代替**です。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **公開実装を使う** | **Area・Search テクスチャも含め、そのまま** |
| **縁の検出は輝度＋深度** | **テクスチャの細部を縁と誤認しにくい** |
| **LDR（トーンマップ後）で、UI の前に** | **FXAA と同様** |
| **品質プリセットを選ぶ** | <strong>Low・Medium・High・Ultra（探索の歩数）</strong> |
| **ステンシルで縁の画素だけ処理** | **2・3 パス目を縁のある所だけに限定**して速くする |

## よくあるミス

??? failure "Area・Search テクスチャを自作して、縁がおかしい"
    **公開されているテクスチャ・データをそのまま使う**。

??? failure "縁テクスチャを、sRGB 形式で作って、値がずれる"
    <strong>UNORM（リニア）</strong>で作る。

??? failure "HDR のまま SMAA を掛けて、縁の検出が不安定"
    **LDR（トーンマップ後）で行う**。

??? failure "テクスチャの細部が、縁と誤検出されて、ぼやける"
    **しきい値を上げる**、**局所コントラスト適応を有効に**、**深度で検出**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SMAA ＝ <strong>縁検出 → 縁の形を分類して、面積から重みを計算 → ブレンド</strong>。<strong>3 パス</strong>
    - [x] <strong>FXAA より、文字・細部をぼかさず、縁がきれい</strong>
    - [x] <strong>Area・Search テクスチャ</strong>は<strong>公開データを使う</strong>
    - [x] <strong>LDR・UI の前</strong>に掛ける
    - [x] <strong>時間的なちらつきには、SMAA T2x か TAA</strong>

## 参考

- Jimenez et al., "SMAA: Enhanced Subpixel Morphological Antialiasing"（Eurographics 2012）
- iryoku/smaa（GitHub, 公式実装）
- Reshetov, "Morphological Antialiasing"（HPG 2009）

## 関連ページ

- [アンチエイリアシング](index.md)
- [FXAA](fxaa.md)
- [TAA](taa.md)
- [比較と選び方](comparison.md)
