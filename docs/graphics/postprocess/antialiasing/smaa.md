---
title: SMAA
tags:
  - 描画
---

# SMAA

<strong>SMAA（Subpixel Morphological Anti-Aliasing）</strong>は、FXAA と同じ「画像だけを見る後処理 AA」ですが縁の形（パターン）を分類して、縁がどれだけ画素を覆っているかを「計算」するので、FXAA より、文字や模様をぼかさず、縁がきれいです。3 つのパス（縁検出 → 重みの計算 → ブレンド）で構成され、FXAA より少し重いですが、画質のバランスが良いので広く使われます。このページでは、3 パスの流れ・縁の検出・縁パターンと重みの計算（ルックアップ テクスチャ）・ブレンド・時間方向の拡張（SMAA T2x）を説明します。

!!! tip "ポイント"
    - SMAA ＝ <strong>縁を検出 → 縁の形を分類して、画素の覆われ具合（重み）を計算 → 重みで隣の画素と混ぜる</strong>。
    - <strong>3 パス</strong>：① 縁検出・② ブレンドの重み・③ 近傍ブレンド。
    - FXAA より、文字や細部をぼかさない。縁の形に応じて、正確に混ぜる。
    - 事前計算した 2 枚のテクスチャ（Area・Search）を使う。
    - 縁検出は輝度（または色・深度）の差で行う。
    - SMAA T2x はジッターと時間蓄積を足した版（TAA の簡易版）。

!!! info "このページを読む前に"
    - [Anti-Aliasing](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

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
| ① 縁検出 | 色（輝度）または深度 | <strong>縁テクスチャ（`R8G8`）：各画素の「左の縁」「上の縁」</strong> |
| ② ブレンドの重み | 縁テクスチャ・Area・Search | 重みテクスチャ（`R8G8B8A8`） |
| ③ 近傍ブレンド | 元の画像・重みテクスチャ | 最終画像 |

## ① 縁の検出

<strong>画素とその左・上の画素の輝度を比べ、差がしきい値以上なら縁</strong>です（さらに「局所コントラストの適応」で、近くにより強い縁があれば、弱い縁を無視します）。

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
| 左と上 | 各画素が自分の「左の境」「上の境」の縁を担当（重複を避ける） |
| `kThreshold`（0.05〜0.1） | 縁とみなす輝度差 |
| 局所コントラスト適応 | 「近くにもっと強い縁がある」とき、弱い縁を捨てる（テクスチャの細部を縁と誤認しない） |
| 深度・色での検出 | 輝度のほか、深度や色（RGB の差）でも検出できる |

## ② ブレンドの重み

<strong>縁を縁に沿って両方向へたどり、縁の端の形（L 字・Z 字・U 字など）</strong>を判定します。その形と画素の位置から、「この画素のうち、反対側に属する面積の割合（＝ブレンドの重み）」を計算します。

縁の端の形は、3 種類に分類します。直線は、まっすぐな縁で端が両方開いています。L 字は、縁の端が直角に曲がっています。Z 字や U 字は、縁の端がジグザグやコの字になっています。

面積の計算は事前に計算した 2 枚のテクスチャで表引きします。

面積の計算は、事前に計算した 2 枚のテクスチャで表引きします。Area テクスチャは、縁の形と画素の位置から、覆われる面積（重み）を引きます。Search テクスチャは、縁をたどるときの探索の歩数を効率よく決めます。

原典は、Jimenez らの "SMAA: Enhanced Subpixel Morphological Antialiasing"（Eurographics 2012）です。

これらは公開されているデータをそのまま使います（自分で作る必要はありません）。

<!-- fig:smaa-edge-weights:begin -->

<svg class="fig illust motion" data-fig="smaa-edge-weights" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-smaa-edge-weights" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">SMAA: 縁を見つけ、階段の長さを調べて、画素ごとに、混ぜる割合を決める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">緩い傾き(1/6)の縁。階段の 1 段が 6 画素。画素ごとに、縁の上下の色を、面積の割合で混ぜる</text>
<rect x="30" y="100" width="300.0" height="100.0" fill="#ffffff" stroke="#64748b" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#64748b">① 入力(階段)</text>
<rect x="30.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="42.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="55.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="67.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="80.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="92.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="105.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="117.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="130.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="142.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="155.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="167.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="180.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="205.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="217.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="230.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="242.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="255.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="267.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="280.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="292.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="305.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="317.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="42.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="55.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="67.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="80.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="92.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="105.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="117.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="130.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="142.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="155.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="167.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="180.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="205.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="217.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="230.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="242.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="255.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="267.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="280.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="292.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="305.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="317.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="42.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="55.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="67.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="80.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="92.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="105.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="117.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="130.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="142.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="155.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="167.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="180.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="205.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="217.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="230.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="242.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="255.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="267.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="280.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="292.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="305.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="317.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="42.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="55.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="67.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="80.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="92.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="105.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="117.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="130.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="142.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="155.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="167.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="180.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="205.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="217.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="230.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="242.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="255.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="267.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="280.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="292.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="305.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="317.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="42.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="55.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="67.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="80.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="92.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="105.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="117.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="130.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="142.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="155.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="167.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="180.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="205.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="217.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="230.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="242.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="255.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="267.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="280.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="292.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="305.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="317.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="42.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="55.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="67.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="80.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="92.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="105.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="117.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="130.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="142.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="155.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="167.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="180.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="192.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="205.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="217.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="230.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="242.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="255.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="267.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="280.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="292.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="305.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="317.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="42.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="55.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="67.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="80.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="92.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="105.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="117.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="130.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="142.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="155.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="167.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="180.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="192.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="205.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="217.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="230.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="242.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="255.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="267.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="280.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="292.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="305.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="317.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="42.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="55.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="67.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="80.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="92.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="105.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="117.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="130.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="142.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="155.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="167.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="180.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="192.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="205.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="217.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="230.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="242.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="255.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="267.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="280.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="292.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="305.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="317.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="335" y="100" width="300.0" height="100.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="335" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">② 縁の画素(赤枠)と階段の長さ</text>
<rect x="335.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="347.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="360.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="372.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="385.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="397.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="410.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="422.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="435.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="447.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="460.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="472.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="485.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="497.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="510.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="522.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="535.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="547.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="560.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="572.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="585.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="597.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="610.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="622.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="347.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="360.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="372.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="385.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="397.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="410.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="422.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="435.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="447.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="460.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="472.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="485.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="497.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="510.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="522.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="535.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="547.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="560.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="572.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="585.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="597.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="610.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="622.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="347.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="360.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="372.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="385.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="397.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="410.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="422.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="435.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="447.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="460.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="472.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="485.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="497.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="510.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="522.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="535.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="547.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="560.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="572.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="585.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="597.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="610.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="622.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="347.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="360.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="372.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="385.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="397.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="410.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="422.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="435.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="447.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="460.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="472.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="485.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="497.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="510.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="522.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="535.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="547.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="560.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="572.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="585.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="597.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="610.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="622.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="347.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="360.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="372.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="385.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="397.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="410.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="422.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="435.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="447.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="460.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="472.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="485.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="497.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="510.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="522.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="535.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="547.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="560.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="572.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="585.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="597.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="610.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="622.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="347.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="360.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="372.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="385.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="397.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="410.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="422.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="435.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="447.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="460.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="472.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="485.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="497.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="510.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="522.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="535.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="547.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="560.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="572.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="585.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="597.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="610.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="622.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="347.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="360.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="372.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="385.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="397.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="410.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="422.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="435.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="447.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="460.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="472.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="485.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="497.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="510.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="522.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="535.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="547.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="560.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="572.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="585.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="597.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="610.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="622.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="347.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="360.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="372.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="385.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="397.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="410.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="422.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="435.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="447.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="460.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="472.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="485.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="497.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="510.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="522.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="535.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="547.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="560.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="572.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="585.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="597.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="610.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="622.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="335.0" y="137.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></rect>
<rect x="347.5" y="137.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0705;0.0707;1.0000" values="0;0;1;1"/></rect>
<rect x="360.0" y="137.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0745;0.0747;1.0000" values="0;0;1;1"/></rect>
<rect x="372.5" y="150.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0785;0.0787;1.0000" values="0;0;1;1"/></rect>
<rect x="385.0" y="150.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0827;1.0000" values="0;0;1;1"/></rect>
<rect x="397.5" y="150.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0865;0.0867;1.0000" values="0;0;1;1"/></rect>
<rect x="410.0" y="150.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0905;0.0907;1.0000" values="0;0;1;1"/></rect>
<rect x="422.5" y="150.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0945;0.0947;1.0000" values="0;0;1;1"/></rect>
<rect x="435.0" y="150.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0985;0.0987;1.0000" values="0;0;1;1"/></rect>
<rect x="447.5" y="162.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1025;0.1027;1.0000" values="0;0;1;1"/></rect>
<rect x="460.0" y="162.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1065;0.1067;1.0000" values="0;0;1;1"/></rect>
<rect x="472.5" y="162.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1105;0.1107;1.0000" values="0;0;1;1"/></rect>
<rect x="485.0" y="162.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1145;0.1147;1.0000" values="0;0;1;1"/></rect>
<rect x="497.5" y="162.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1185;0.1187;1.0000" values="0;0;1;1"/></rect>
<rect x="510.0" y="162.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1225;0.1227;1.0000" values="0;0;1;1"/></rect>
<rect x="522.5" y="175.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1265;0.1267;1.0000" values="0;0;1;1"/></rect>
<rect x="535.0" y="175.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1305;0.1307;1.0000" values="0;0;1;1"/></rect>
<rect x="547.5" y="175.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1345;0.1347;1.0000" values="0;0;1;1"/></rect>
<rect x="560.0" y="175.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1385;0.1387;1.0000" values="0;0;1;1"/></rect>
<rect x="572.5" y="175.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1425;0.1427;1.0000" values="0;0;1;1"/></rect>
<rect x="585.0" y="175.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1465;0.1467;1.0000" values="0;0;1;1"/></rect>
<rect x="597.5" y="187.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1505;0.1507;1.0000" values="0;0;1;1"/></rect>
<rect x="610.0" y="187.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1545;0.1547;1.0000" values="0;0;1;1"/></rect>
<rect x="622.5" y="187.5" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1585;0.1587;1.0000" values="0;0;1;1"/></rect>
<rect x="640" y="100" width="300.0" height="100.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="640" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">③ 割合で混ぜた結果</text>
<rect x="640.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="652.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="665.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="677.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="690.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="702.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="715.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="727.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="740.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="752.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="765.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="777.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="790.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="802.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="815.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="827.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="840.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="852.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="865.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="877.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="890.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="902.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="915.0" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="927.5" y="100.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="652.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="665.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="677.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="690.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="702.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="715.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="727.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="740.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="752.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="765.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="777.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="790.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="802.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="815.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="827.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="840.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="852.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="865.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="877.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="890.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="902.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="915.0" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="927.5" y="112.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#aeaeae"/></rect>
<rect x="652.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="665.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="677.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="690.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="702.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="715.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="727.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="740.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="752.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="765.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="777.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="790.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="802.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="815.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="827.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="840.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="852.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="865.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="877.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="890.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="902.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="915.0" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="927.5" y="125.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#262626"/></rect>
<rect x="652.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#262626"/></rect>
<rect x="665.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#6a6a6a"/></rect>
<rect x="677.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#9d9d9d"/></rect>
<rect x="690.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="702.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="715.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="727.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="740.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="752.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="765.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="777.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="790.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="802.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="815.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="827.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="840.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="852.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="865.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="877.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="890.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="902.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="915.0" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="927.5" y="137.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#262626"/></rect>
<rect x="652.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#262626"/></rect>
<rect x="665.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#262626"/></rect>
<rect x="677.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#262626"/></rect>
<rect x="690.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#262626"/></rect>
<rect x="702.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#262626"/></rect>
<rect x="715.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#373737"/></rect>
<rect x="727.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#595959"/></rect>
<rect x="740.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="752.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#9d9d9d"/></rect>
<rect x="765.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="777.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="790.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="802.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="815.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="827.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="840.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="852.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="865.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="877.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="890.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="902.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="915.0" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="927.5" y="150.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#262626"/></rect>
<rect x="652.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#262626"/></rect>
<rect x="665.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#262626"/></rect>
<rect x="677.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#262626"/></rect>
<rect x="690.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#262626"/></rect>
<rect x="702.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#262626"/></rect>
<rect x="715.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#262626"/></rect>
<rect x="727.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#262626"/></rect>
<rect x="740.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#262626"/></rect>
<rect x="752.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#262626"/></rect>
<rect x="765.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#262626"/></rect>
<rect x="777.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#262626"/></rect>
<rect x="790.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#373737"/></rect>
<rect x="802.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#595959"/></rect>
<rect x="815.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="827.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#9d9d9d"/></rect>
<rect x="840.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="852.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="865.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="877.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="890.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="902.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="915.0" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="927.5" y="162.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#262626"/></rect>
<rect x="652.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#262626"/></rect>
<rect x="665.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#262626"/></rect>
<rect x="677.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#262626"/></rect>
<rect x="690.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#262626"/></rect>
<rect x="702.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#262626"/></rect>
<rect x="715.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#262626"/></rect>
<rect x="727.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#262626"/></rect>
<rect x="740.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#262626"/></rect>
<rect x="752.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#262626"/></rect>
<rect x="765.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#262626"/></rect>
<rect x="777.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#262626"/></rect>
<rect x="790.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#262626"/></rect>
<rect x="802.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#262626"/></rect>
<rect x="815.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#262626"/></rect>
<rect x="827.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#262626"/></rect>
<rect x="840.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#262626"/></rect>
<rect x="852.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#262626"/></rect>
<rect x="865.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#373737"/></rect>
<rect x="877.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#595959"/></rect>
<rect x="890.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="902.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#aeaeae"/></rect>
<rect x="915.0" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="927.5" y="175.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#262626"/></rect>
<rect x="652.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3373" values="#e5e7eb;#262626"/></rect>
<rect x="665.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3413" values="#e5e7eb;#262626"/></rect>
<rect x="677.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3453" values="#e5e7eb;#262626"/></rect>
<rect x="690.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3493" values="#e5e7eb;#262626"/></rect>
<rect x="702.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#262626"/></rect>
<rect x="715.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3573" values="#e5e7eb;#262626"/></rect>
<rect x="727.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3613" values="#e5e7eb;#262626"/></rect>
<rect x="740.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3653" values="#e5e7eb;#262626"/></rect>
<rect x="752.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#262626"/></rect>
<rect x="765.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#262626"/></rect>
<rect x="777.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3773" values="#e5e7eb;#262626"/></rect>
<rect x="790.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#262626"/></rect>
<rect x="802.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3853" values="#e5e7eb;#262626"/></rect>
<rect x="815.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3893" values="#e5e7eb;#262626"/></rect>
<rect x="827.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#262626"/></rect>
<rect x="840.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3973" values="#e5e7eb;#262626"/></rect>
<rect x="852.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4013" values="#e5e7eb;#262626"/></rect>
<rect x="865.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4053" values="#e5e7eb;#262626"/></rect>
<rect x="877.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#262626"/></rect>
<rect x="890.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#262626"/></rect>
<rect x="902.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#e5e7eb;#262626"/></rect>
<rect x="915.0" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4213" values="#e5e7eb;#262626"/></rect>
<rect x="927.5" y="187.5" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#6a6a6a"/></rect>
<text x="335" y="224" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">検出した縁の画素: 24 個</text>
<text x="30" y="270" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">階段の長さ(連続する縁):</text>
<text x="250" y="270" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed" opacity="0">3、6、6、6、3(画素)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;1.0000" values="0;0;1;1"/></text>
<rect x="30" y="296" width="900" height="120" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="30" y="286" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">④ 長さ 6 の階段の、画素ごとの混ぜる割合(縁の位置で変わる)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/><rect x="60" y="340" width="120" height="24" fill="#d1fae5" stroke="#16a34a" stroke-width="1.5"/>
<rect x="60" y="340" width="50.0" height="24" fill="#16a34a" opacity="0.8"/>
<text x="60" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">1 番目: 割合 0.42</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3554;0.3556;1.0000" values="0;0;1;1"/><rect x="200" y="340" width="120" height="24" fill="#d1fae5" stroke="#16a34a" stroke-width="1.5"/>
<rect x="200" y="340" width="30.0" height="24" fill="#16a34a" opacity="0.8"/>
<text x="200" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">2 番目: 割合 0.25</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3776;0.3778;1.0000" values="0;0;1;1"/><rect x="340" y="340" width="120" height="24" fill="#d1fae5" stroke="#16a34a" stroke-width="1.5"/>
<rect x="340" y="340" width="10.0" height="24" fill="#16a34a" opacity="0.8"/>
<text x="340" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">3 番目: 割合 0.08</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/><rect x="480" y="340" width="120" height="24" fill="#d1fae5" stroke="#16a34a" stroke-width="1.5"/>
<rect x="480" y="340" width="110.0" height="24" fill="#16a34a" opacity="0.8"/>
<text x="480" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">4 番目: 割合 0.92</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000" values="0;0;1;1"/><rect x="620" y="340" width="120" height="24" fill="#d1fae5" stroke="#16a34a" stroke-width="1.5"/>
<rect x="620" y="340" width="90.0" height="24" fill="#16a34a" opacity="0.8"/>
<text x="620" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">5 番目: 割合 0.75</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4443;0.4444;1.0000" values="0;0;1;1"/><rect x="760" y="340" width="120" height="24" fill="#d1fae5" stroke="#16a34a" stroke-width="1.5"/>
<rect x="760" y="340" width="70.0" height="24" fill="#16a34a" opacity="0.8"/>
<text x="760" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">6 番目: 割合 0.58</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5554;0.5556;1.0000" values="0;0;1;1"/><rect x="30" y="436" width="900" height="76" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="460" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">正解とのずれ(平均): 入力 0.025 → SMAA 0.007</text>
<text x="46" y="484" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">手順: 縁を見つける → 階段の長さを数える → 長さと位置から、混ぜる割合(面積)を決める → 隣の画素と混ぜる</text>
<text x="46" y="505" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ぼかさず、縁の画素だけを、面積に合わせて混ぜる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ジャギーは、階段の形<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">輝度の差から、縁の画素に印を付け、階段の長さを調べる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.3332;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">階段の長さと、位置から、面積の割合を決める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;0.5554;0.5556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">その割合で混ぜて、なめらかな縁にする<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5554;0.5556;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:smaa-edge-weights:end -->

## ③ 近傍ブレンド

<strong>重みテクスチャの値に従い、元の画像の隣の画素の色を混ぜます</strong>。重みが 0 なら、元のままです。

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

重みが 0 の画素（大半）は、そのまま返すので縁でない領域は、まったくぼけません。

## FXAA との違い

| 項目 | FXAA | SMAA |
| --- | --- | --- |
| パス数 | 1 | 3 |
| 縁の扱い | 経験則でぼかす | 形を分類し、面積から重みを計算 |
| 文字・細部のぼけ | やや出る | 少ない |
| 斜めの縁 | そこそこ | きれい |
| コスト | 最小 | FXAA の 2〜3 倍 |

## SMAA T2x（時間方向）

<strong>SMAA に、TAA のようなジッターと時間蓄積</strong>を足したのがSMAA T2xです。1 フレームごとに半画素ずらして描き、前のフレームと混ぜることで、時間的なちらつきも抑えます（[TAA](taa.md)）。SMAA 1x（空間のみ）で足りない場合の軽量な代替です。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 公開実装を使う | Area・Search テクスチャも含め、そのまま |
| 縁の検出は輝度＋深度 | テクスチャの細部を縁と誤認しにくい |
| LDR（トーンマップ後）で、UI の前に | FXAA と同様 |
| 品質プリセットを選ぶ | <strong>Low・Medium・High・Ultra（探索の歩数）</strong> |
| ステンシルで縁の画素だけ処理 | 2・3 パス目を縁のある所だけに限定して速くする |

## よくあるミス

??? failure "Area・Search テクスチャを自作して、縁がおかしい"
    <strong>公開されているテクスチャ・データをそのまま使う</strong>。

??? failure "縁テクスチャを、sRGB 形式で作って、値がずれる"
    UNORM（リニア）で作る。

??? failure "HDR のまま SMAA を掛けて、縁の検出が不安定"
    LDR（トーンマップ後）で行う。

??? failure "テクスチャの細部が、縁と誤検出されて、ぼやける"
    しきい値を上げる、局所コントラスト適応を有効に、深度で検出する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SMAA ＝ <strong>縁検出 → 縁の形を分類して、面積から重みを計算 → ブレンド</strong>。3 パス
    - [x] FXAA より、文字・細部をぼかさず、縁がきれい
    - [x] Area・Search テクスチャは公開データを使う
    - [x] LDR・UI の前に掛ける
    - [x] 時間的なちらつきには、SMAA T2x か TAA

## 参考

- Jimenez et al., "SMAA: Enhanced Subpixel Morphological Antialiasing"（Eurographics 2012）
- iryoku/smaa（GitHub, 公式実装）
- Reshetov, "Morphological Antialiasing"（HPG 2009）

## 関連ページ

- [Anti-Aliasing](index.md)
- [FXAA](fxaa.md)
- [TAA](taa.md)
- [Comparison and Choosing](comparison.md)
