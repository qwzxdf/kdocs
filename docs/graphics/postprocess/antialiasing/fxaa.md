---
title: FXAA
tags:
  - 描画
---

# FXAA

<strong>FXAA（Fast Approximate Anti-Aliasing）</strong>は、**完成した画像だけを見て、「縁らしい所」を見つけてぼかす**、**1 パスの後処理 AA** です。**深度も法線も速度も要らず、どんなレンダラーにも後付けできる**ので、**導入が非常に簡単**で**コストも小さい**です。**一方で縁以外（テクスチャの文字や細かい模様）まで少しぼかし、時間的なちらつきは直せません**。このページでは、**考え方・輝度による縁の検出・縁の向きと方向に沿ったぼかし・品質プリセット・弱点と使いどころ**を説明します。

!!! tip "ポイント"
    - FXAA ＝ <strong>最終画像の輝度から、コントラストが高い所（縁）を見つけ、縁に沿った方向と直交方向に、ぼかす</strong>。
    - <strong>入力は、1 枚の画像だけ</strong>。<strong>深度・速度が要らない</strong>。<strong>1 パス</strong>。
    - <strong>低コスト</strong>（1080p で 0.2〜0.5 ms）。<strong>どの描画方式にも付けられる</strong>。
    - <strong>欠点</strong>：<strong>文字・細かい模様も少しぼける</strong>。<strong>時間的なちらつきは残る</strong>。<strong>細い線は救えない</strong>。
    - <strong>輝度はガンマ空間（LDR・トーンマップ後）</strong>で<strong>判定する</strong>（<strong>人の見た目に近いコントラスト</strong>）。
    - <strong>UI を描く前に掛ける</strong>。

<!-- fig:fxaa-edge:begin -->

<svg class="fig illust motion" data-fig="fxaa-edge" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-fxaa-edge" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">FXAA:画像だけを見て、コントラストの高い画素を、縁に沿ってぼかす</text>
<rect x="60" y="80" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#353535"/></rect>
<rect x="60" y="136" width="55" height="55" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#f2f2f2;#bcbcbc"/></rect>
<rect x="60" y="192" width="55" height="55" fill="#f2f2f2"/>
<rect x="60" y="248" width="55" height="55" fill="#f2f2f2"/>
<rect x="60" y="304" width="55" height="55" fill="#f2f2f2"/>
<rect x="116" y="80" width="55" height="55" fill="#191919"/>
<rect x="116" y="136" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#505050"/></rect>
<rect x="116" y="192" width="55" height="55" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#f2f2f2;#d7d7d7"/></rect>
<rect x="116" y="248" width="55" height="55" fill="#f2f2f2"/>
<rect x="116" y="304" width="55" height="55" fill="#f2f2f2"/>
<rect x="172" y="80" width="55" height="55" fill="#191919"/>
<rect x="172" y="136" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#353535"/></rect>
<rect x="172" y="192" width="55" height="55" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#f2f2f2;#bcbcbc"/></rect>
<rect x="172" y="248" width="55" height="55" fill="#f2f2f2"/>
<rect x="172" y="304" width="55" height="55" fill="#f2f2f2"/>
<rect x="228" y="80" width="55" height="55" fill="#191919"/>
<rect x="228" y="136" width="55" height="55" fill="#191919"/>
<rect x="228" y="192" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#505050"/></rect>
<rect x="228" y="248" width="55" height="55" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#f2f2f2;#d7d7d7"/></rect>
<rect x="228" y="304" width="55" height="55" fill="#f2f2f2"/>
<rect x="284" y="80" width="55" height="55" fill="#191919"/>
<rect x="284" y="136" width="55" height="55" fill="#191919"/>
<rect x="284" y="192" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#353535"/></rect>
<rect x="284" y="248" width="55" height="55" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#f2f2f2;#bcbcbc"/></rect>
<rect x="284" y="304" width="55" height="55" fill="#f2f2f2"/>
<rect x="340" y="80" width="55" height="55" fill="#191919"/>
<rect x="340" y="136" width="55" height="55" fill="#191919"/>
<rect x="340" y="192" width="55" height="55" fill="#191919"/>
<rect x="340" y="248" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#505050"/></rect>
<rect x="340" y="304" width="55" height="55" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#f2f2f2;#d7d7d7"/></rect>
<rect x="396" y="80" width="55" height="55" fill="#191919"/>
<rect x="396" y="136" width="55" height="55" fill="#191919"/>
<rect x="396" y="192" width="55" height="55" fill="#191919"/>
<rect x="396" y="248" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#353535"/></rect>
<rect x="396" y="304" width="55" height="55" fill="#f2f2f2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#f2f2f2;#bcbcbc"/></rect>
<rect x="452" y="80" width="55" height="55" fill="#191919"/>
<rect x="452" y="136" width="55" height="55" fill="#191919"/>
<rect x="452" y="192" width="55" height="55" fill="#191919"/>
<rect x="452" y="248" width="55" height="55" fill="#191919"/>
<rect x="452" y="304" width="55" height="55" fill="#191919"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#191919;#353535"/></rect>
<rect x="62" y="82" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="62" y="138" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="118" y="138" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="118" y="194" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="174" y="138" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="174" y="194" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="230" y="194" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="230" y="250" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="286" y="194" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="286" y="250" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="342" y="250" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="342" y="306" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="398" y="250" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="398" y="306" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="454" y="306" width="51" height="51" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<text x="60" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">元の画像（階段状の縁）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 周りの明るさを比べて、コントラストが高い画素（橙）を探す<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;0.4797;0.4800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② その画素を、縁に垂直な方向の隣と混ぜる → 階段がやわらぐ<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">深度も法線も要らない。最終画像だけで動く（安い）。ただし、縁以外の細かい模様（文字・テクスチャ）も、少しぼけやすい。</text>
</svg>

<!-- fig:fxaa-edge:end -->

## 考え方

**FXAA は画像を見て、次の 3 段階**を**行います**。

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="FXAA の流れ">
<text x="20" y="26" class="fig-title">FXAA：縁を見つけて、縁に沿って分析し、縁をまたいでぼかす</text>
<defs><marker id="fx-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="13">
<rect x="20" y="56" width="200" height="90" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/><text x="120" y="86" text-anchor="middle" style="font-weight:700">① 縁を探す</text><text x="120" y="108" text-anchor="middle" style="font-size:11px">周囲 5 画素の輝度差が、</text><text x="120" y="124" text-anchor="middle" style="font-size:11px">しきい値以上なら縁</text>
<rect x="290" y="56" width="200" height="90" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/><text x="390" y="86" text-anchor="middle" style="font-weight:700">② 縁の向きと端</text><text x="390" y="108" text-anchor="middle" style="font-size:11px">水平か垂直か、</text><text x="390" y="124" text-anchor="middle" style="font-size:11px">縁がどこまで続くか</text>
<rect x="560" y="56" width="200" height="90" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/><text x="660" y="86" text-anchor="middle" style="font-weight:700">③ 縁と直交にぼかす</text><text x="660" y="108" text-anchor="middle" style="font-size:11px">縁の位置に応じた、</text><text x="660" y="124" text-anchor="middle" style="font-size:11px">サブピクセルのずれで混ぜる</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="222" y1="101" x2="288" y2="101" marker-end="url(#fx-arrow)"/><line x1="492" y1="101" x2="558" y2="101" marker-end="url(#fx-arrow)"/></g>
</svg>

## ① 縁の検出

**画素とその上下左右の 5 画素の輝度**を**調べ、最大と最小の差**が**しきい値より小さければ、縁ではない**として**そのまま返します**（**早期終了**）。

```hlsl
float Luma(float3 rgb) {
  return dot(rgb, float3(0.299, 0.587, 0.114));
}

float4 FxaaPS(float2 uv) {
  float3 c = color.SampleLevel(linear_clamp, uv, 0).rgb;
  float luma_m = Luma(c);
  float luma_n = Luma(color.SampleLevel(linear_clamp, uv + float2(0, -1) * texel, 0).rgb);
  float luma_s = Luma(color.SampleLevel(linear_clamp, uv + float2(0, 1) * texel, 0).rgb);
  float luma_w = Luma(color.SampleLevel(linear_clamp, uv + float2(-1, 0) * texel, 0).rgb);
  float luma_e = Luma(color.SampleLevel(linear_clamp, uv + float2(1, 0) * texel, 0).rgb);

  float luma_min = min(luma_m, min(min(luma_n, luma_s), min(luma_w, luma_e)));
  float luma_max = max(luma_m, max(max(luma_n, luma_s), max(luma_w, luma_e)));
  float range = luma_max - luma_min;
  if (range < max(kEdgeThresholdMin, luma_max * kEdgeThreshold)) {
    return float4(c, 1);
  }
  // 続きは ② ③
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`Luma`（0.299, 0.587, 0.114）</strong> | **輝度の近似**（**緑のチャンネルだけで代用する簡易版もある**） |
| <strong>`kEdgeThreshold`（約 0.125〜0.166）</strong> | **明るさに対する相対のしきい値**（**暗い所でも検出できる**） |
| <strong>`kEdgeThresholdMin`（約 0.0312）</strong> | **暗すぎる所は無視**する下限 |
| **早期終了** | **縁でない画素（大半）は、ここで終わる → 速い** |

## ② 縁の向きと端の探索

**縁が水平か垂直か**を**判定**し、**縁に沿って両方向へ進み、縁の端**を**探します**。

縁の判定です。縁の向きは、水平方向の輝度の変化と、垂直方向の変化の大きさを比べて決めます。縁の反対側は、縁をまたぐ輝度差が大きい側（上か下、左か右）を決めます。端の探索は、縁に沿って進み、輝度がある程度変わった所（縁の終わり）まで行います。

**縁の端までの距離**から、**画素が縁のどの位置にあるか**が**分かり**、<strong>ぼかす量（サブピクセルのずらし）</strong>を**決めます**。

## ③ 縁と直交方向のぼかし

<strong>画素の位置（縁の端に近いか、中央か）</strong>に**応じて**、**縁と直交する方向にサンプル位置をずらして読み**ます。**バイリニア補間が隣の画素と混ぜてくれる**ので、**縁がなめらか**になります。

ぼかしの要点です。サブピクセルのずれは、縁に対する画素の位置から、ずらす量を決めます。ずらした位置を読むだけで、バイリニア補間が隣と混ぜてくれます（サンプル 1 回）。孤立した細い線や点には、別計算のサブピクセル AA で、周りと平均してぼかします（係数で強さを調整できます）。

## 品質プリセット

**FXAA には、品質プリセット**（**サンプル数・端の探索の歩数**が違う）が**あります**。

| プリセット | 内容 | コスト |
| --- | --- | --- |
| <strong>低（10）</strong> | **探索の歩数が少ない** | **最小** |
| <strong>中（15）</strong> | **標準** | **小** |
| <strong>高（29）</strong> | **歩数が多い・端の探索が丁寧** | **少し大きい** |

**実際の実装**（**Timothy Lottes の FXAA 3.11**）は、**数百行の HLSL**です。**公開されているものをそのまま使う**のが**一般的**です。

## 弱点

| 弱点 | 理由 |
| --- | --- |
| **文字・細かい模様がぼける** | **コントラストの高い所を、すべて縁とみなす** |
| **時間的なちらつきは残る** | **1 フレームの画像だけを見ている** |
| **細い線・点の途切れは救えない** | **画像に情報がない** |
| **斜めの縁の品質は、MSAA に劣る** | **推測で補う** |
| **半透明・パーティクルの縁にも作用** | **画像なので区別できない** |


原典は、Timothy Lottes（NVIDIA）の "FXAA" の白書（2009）です。

原典は、Timothy Lottes（NVIDIA）の "FXAA" の白書（2009）です。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **UI の前に掛ける** | **文字がぼけない** |
| **ガンマ空間（トーンマップ後）で** | **HDR のままだと縁の検出がずれる** |
| **しきい値を調整** | **強すぎるとぼやけ、弱すぎると残る** |
| **ミニマムなコスト用途に** | **低スペック・モバイル・ウェブ** |
| **他の方式に置き換える** | **品質重視なら SMIL・TAA**（[SMAA](smaa.md)・[TAA](taa.md)） |
| **文字をマスクして除外** | **ぼけを避ける** |

## よくあるミス

??? failure "UI や文字まで、ぼけてしまう"
    **UI を描く前**に FXAA を掛ける。**UI は別パス**。

??? failure "HDR のまま FXAA を掛けて、縁が検出されない・おかしい"
    **トーンマップ後（ガンマ空間）の LDR で**行う。

??? failure "動くとちらつきが残る"
    **FXAA は時間方向を見ない**。**TAA を併用または置換**。

??? failure "シーン全体がぼやけて見える"
    **しきい値を上げる**、**サブピクセル AA の係数を下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] FXAA ＝ <strong>最終画像の輝度から縁を見つけ、縁と直交方向にぼかす</strong>。<strong>1 パス</strong>
    - [x] <strong>深度・速度が不要</strong>で<strong>どんな描画にも後付け</strong>、<strong>低コスト</strong>
    - [x] <strong>弱点</strong>：<strong>文字もぼける・ちらつきは残る・細い線は救えない</strong>
    - [x] <strong>LDR（トーンマップ後）で、UI の前</strong>に掛ける
    - [x] <strong>品質重視なら SMAA・TAA</strong>

## 参考

- Lottes, "FXAA"（NVIDIA White Paper, 2009）
- Lottes, "FXAA 3.11 Source"
- Jimenez et al., "Filtering Approaches for Real-Time Anti-Aliasing"（SIGGRAPH 2011 Course）

## 関連ページ

- [Anti-Aliasing](index.md)
- [MSAA](msaa.md)
- [SMAA](smaa.md)
- [TAA](taa.md)
