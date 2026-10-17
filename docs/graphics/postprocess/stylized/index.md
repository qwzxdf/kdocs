---
title: Outlines and Toon
tags:
  - 描画
---

# Outlines and Toon

**写実的ではなく、アニメやイラストのような絵**を**作る技法**が<strong>ノンフォトリアリスティック レンダリング（NPR）</strong>です。<strong>輪郭線（アウトライン）で形を強調し、陰影を数段階に区切る（セル シェーディング）</strong>ことで、<strong>「手描きのアニメ」風</strong>の絵になります。**どれも写実より優れているわけではなく、作品の画風に合うかどうかの好みの問題**です。このセクションでは、**背面法の輪郭線・画面空間のエッジ検出・セル シェーディング・ポスタライズとハーフトーン**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - NPR ＝ <strong>写実でなく、アニメ・イラスト・絵画のような絵</strong>。<strong>画風の選択</strong>。
    - <strong>輪郭線</strong>は<strong>2 通り</strong>：<strong>背面法（裏返したメッシュを膨らませる）</strong>と<strong>画面空間のエッジ検出（深度・法線・ID の差）</strong>。
    - <strong>セル シェーディング</strong> ＝ <strong>陰影を、数段階に区切る</strong>（<strong>ランプ テクスチャ</strong>）。
    - <strong>ポスタライズ</strong> ＝ <strong>色の段階を減らす</strong>。<strong>ハーフトーン</strong> ＝ <strong>網点で濃淡を表す</strong>。
    - <strong>方式の組み合わせ</strong>で<strong>画風を作る</strong>（<strong>輪郭 ＋ セル ＋ 質感</strong>）。
    - <strong>写実的な高品質とは別軸</strong>。<strong>画風に合うものを選ぶ</strong>。

## 動きで見る

<!-- fig:toon-stages:begin -->

<svg class="fig illust motion" data-fig="toon-stages" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-toon-stages" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="ts-smooth-100"><circle cx="100" cy="170" r="72"/>
</clipPath>
<radialGradient id="ts-grad-100" cx="0.35" cy="0.3" r="0.85"><stop offset="0" stop-color="#fff3c4"/>
<stop offset="0.5" stop-color="#f59e0b"/>
<stop offset="1" stop-color="#451a03"/>
</radialGradient>
<clipPath id="ts-bands-295"><circle cx="295" cy="170" r="72"/>
</clipPath>
<clipPath id="ts-outline-490"><circle cx="490" cy="170" r="72"/>
</clipPath>
<clipPath id="ts-both-685"><circle cx="685" cy="170" r="72"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">トゥーンの 3 工程:陰影を段にして、輪郭線を足す</text>
<g opacity="1"><circle cx="100" cy="170" r="72" fill="url(#ts-grad-100)"/>
</g>
<text x="100" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">① 普通のライティング</text>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;1.0000" values="0;0;1;1"/><line x1="178" y1="170" x2="212" y2="170" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-toon-stages)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="0;0;1;1"/><g clip-path="url(#ts-bands-295)"><circle cx="295" cy="170" r="72" fill="#78350f"/>
<circle cx="282.04" cy="155.6" r="68.39999999999999" fill="#d97706"/>
<circle cx="267.64" cy="139.76" r="43.199999999999996" fill="#fcd34d"/>
</g>
</g>
<text x="295" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">② ランプで段にする</text>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;1.0000" values="0;0;1;1"/><line x1="373" y1="170" x2="407" y2="170" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-toon-stages)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/><circle cx="490" cy="170" r="72" fill="#ffffff" stroke="#0b0b0b" stroke-width="6"/>
</g>
<text x="490" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">③ 輪郭線を作る</text>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000" values="0;0;1;1"/><line x1="568" y1="170" x2="602" y2="170" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-toon-stages)"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000" values="0;0;1;1"/><g clip-path="url(#ts-both-685)"><circle cx="685" cy="170" r="72" fill="#78350f"/>
<circle cx="672.04" cy="155.6" r="68.39999999999999" fill="#d97706"/>
<circle cx="657.64" cy="139.76" r="43.199999999999996" fill="#fcd34d"/>
</g>
<circle cx="685" cy="170" r="72" fill="none" stroke="#0b0b0b" stroke-width="6"/>
</g>
<text x="685" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">④ 重ねる</text>
<text x="40" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">陰影がなめらか<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="1;1;0;0"/></text>
<text x="40" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">明るさを 3 段に区切る（セル シェーディング）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">深度・法線の差から、縁だけを取り出す<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.6083;0.6087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">段の絵 ＋ 輪郭線 ＝ アニメ調<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:toon-stages:end -->

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Inverted Hull Outlines](outline-hull.md) | 裏返したメッシュを法線方向に膨らませて、黒く塗る |
| [Screen-Space Edge Detection](outline-edge.md) | 深度・法線・ID の差から、線を検出（Sobel） |
| [Cel Shading](cel-shading.md) | 陰影の段階化・ランプ テクスチャ・スペキュラとリム ライト |
| [Posterization and Halftone](posterize-halftone.md) | 色数を減らす・網点・漫画的表現 |

## 輪郭線の 2 方式

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| <strong>背面法（Inverted Hull）</strong> | **裏面を法線方向に膨らませて、黒く描く** | **線の太さ・色を物体ごとに制御・安い・綺麗** | **角の鋭い物の線が途切れる・内側の線は出ない** |
| **画面空間エッジ検出** | **深度・法線・ID の画像から、差の大きい所を線に** | **内側の線も出る・形状に依存しない** | **線の太さが一定になりにくい・コストは画面サイズ依存** |

## 関連ページ

- [Post-Processing](../index.md)
- [Color Grading](../color-grading/index.md)
- [PBR](../../../3d/pbr.md)
- [法線とライティング](../../../3d/lighting-normals.md)
