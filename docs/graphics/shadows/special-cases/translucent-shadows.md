---
title: Translucent Shadows
tags:
  - 描画
---

# Translucent Shadows

**ガラス・水・煙のような半透明な物の影**は、**通常のシャドウ マップ（深度のみ）では表せません**。**深度は「あるか・ないか」しか記録しない**ためです。**近似として、ステップリング（網点で一部だけ影を落とす）や、色付きの影を別のマップに描く**方法が**あります**。このページでは、**半透明の影の近似方法・ステップリング・色付きの影**を説明します。

!!! tip "ポイント"
    - **深度は 0 か 1 の判定**。**半透明の「薄い影」は表せない**。
    - **ステップリング ＝ 網点のパターンで一部だけ影を落とす**。**フィルタで薄い影に見える**。
    - **色付きの影**：**半透明の色を、別の画像に描き、影に掛ける**。
    - **簡易には、半透明は影を落とさない**ことも**多い**。

## Translucent Shadows {#半透明の影}
**ガラス・煙・半透明の布**は**光を部分的に通します**。**シャドウ マップは、深度しか持たない**ので<strong>「完全に遮る」か「完全に通す」</strong>の**2 択**になります。

| 方法 | 内容 |
| --- | --- |
| **影を落とさない** | **一番簡単**。**半透明の物**は**影を落とさない**設定 |
| <strong>スクリーン ドア（ステッポリング）</strong> | <strong>透明度に応じた、確率的（ディザ パターン）</strong>に、**一部の画素を `clip`**。**少し遮る**。**PCF・TAA**で**平均され**て、**薄い影**に見える |
| **不透明として扱う** | **ガラスでも影を濃く**落とす（**嘘だが手軽**） |
| **色付きシャドウ マップ** | **別のシャドウ マップ**（**RGB ＋ 深度**）に、**半透明の物の色と透過率**を**乗算ブレンド**で保存。**ステンドグラス**のような**色付きの影**。**不透明の物の影とは、別に引く** |
| <strong>多層（Deep Shadow Maps）</strong> | **深度ごとの透過率**を保存（**煙・髪**）。**メモリが重く**、**専用** |
| <strong>レイトレース影（Any-Hit）</strong> | **Any-Hit シェーダー**で、**透過率を累積**（[レイトレース影](../ray-traced.md)） |

<!-- fig:stipple-shadow:begin -->

<svg class="fig illust motion" data-fig="stipple-shadow" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-stipple-shadow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">半透明の影: 透明度に応じて、シャドウ マップに「点描」で書き込み、PCF でなめらかにする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 24 マスの影の表に、透明度の違う 3 枚の板の影を書く。点描のパターンのままだと粗いが、PCF で平均すると、薄い影になる</text>
<text x="60.0" y="100" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">① 透明度の違う 3 枚(α = 0.25、0.5、0.8)</text>
<rect x="60.0" y="108" width="238.0" height="22" fill="#94a3b8" fill-opacity="0.25"/>
<text x="180.0" y="124" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">α = 0.25</text>
<rect x="300.0" y="108" width="238.0" height="22" fill="#94a3b8" fill-opacity="0.5"/>
<text x="420.0" y="124" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">α = 0.50</text>
<rect x="540.0" y="108" width="238.0" height="22" fill="#94a3b8" fill-opacity="0.8"/>
<text x="660.0" y="124" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">α = 0.80</text>
<rect x="52.0" y="150" width="736.0" height="134" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="52.0" y="140" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 影の表への書き込み(黒 = 書く、白 = 書かない)</text>
<rect x="60.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732" values="#ffffff;#334155"/></rect>
<rect x="90.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0878" values="#ffffff;#334155"/></rect>
<rect x="150.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1024" values="#ffffff;#334155"/></rect>
<rect x="210.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1171" values="#ffffff;#334155"/></rect>
<rect x="270.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1317" values="#ffffff;#334155"/></rect>
<rect x="330.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="360.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1463" values="#ffffff;#334155"/></rect>
<rect x="390.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="420.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1610" values="#ffffff;#334155"/></rect>
<rect x="450.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="480.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1756" values="#ffffff;#334155"/></rect>
<rect x="510.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="540.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1902" values="#ffffff;#334155"/></rect>
<rect x="570.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2049" values="#ffffff;#334155"/></rect>
<rect x="630.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2195" values="#ffffff;#334155"/></rect>
<rect x="690.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2341" values="#ffffff;#334155"/></rect>
<rect x="750.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="90.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="150.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="210.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="270.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="330.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1390" values="#ffffff;#334155"/></rect>
<rect x="360.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="390.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1537" values="#ffffff;#334155"/></rect>
<rect x="420.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="450.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1683" values="#ffffff;#334155"/></rect>
<rect x="480.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="510.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1829" values="#ffffff;#334155"/></rect>
<rect x="540.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1902" values="#ffffff;#334155"/></rect>
<rect x="570.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="630.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2195" values="#ffffff;#334155"/></rect>
<rect x="690.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="750.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732" values="#ffffff;#334155"/></rect>
<rect x="90.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0878" values="#ffffff;#334155"/></rect>
<rect x="150.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1024" values="#ffffff;#334155"/></rect>
<rect x="210.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1171" values="#ffffff;#334155"/></rect>
<rect x="270.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1317" values="#ffffff;#334155"/></rect>
<rect x="330.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="360.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1463" values="#ffffff;#334155"/></rect>
<rect x="390.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="420.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1610" values="#ffffff;#334155"/></rect>
<rect x="450.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="480.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1756" values="#ffffff;#334155"/></rect>
<rect x="510.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="540.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1902" values="#ffffff;#334155"/></rect>
<rect x="570.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2049" values="#ffffff;#334155"/></rect>
<rect x="630.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2195" values="#ffffff;#334155"/></rect>
<rect x="690.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2341" values="#ffffff;#334155"/></rect>
<rect x="750.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="90.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="150.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="210.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="270.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="330.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1390" values="#ffffff;#334155"/></rect>
<rect x="360.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="390.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1537" values="#ffffff;#334155"/></rect>
<rect x="420.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="450.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1683" values="#ffffff;#334155"/></rect>
<rect x="480.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="510.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1829" values="#ffffff;#334155"/></rect>
<rect x="540.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="570.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="630.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="690.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="750.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="158" width="720.0" height="120.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="318" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">③ 平均する(PCF): 4 マス × 4 行</text>
<rect x="60.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2780" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="90.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2820" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="120.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2859" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="150.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="180.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2937" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="210.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2976" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="240.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3015" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="270.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3054" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="300.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3093" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="330.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3132" values="#e5e7eb;#808080"/></rect>
<rect x="360.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3171" values="#e5e7eb;#808080"/></rect>
<rect x="390.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3210" values="#e5e7eb;#808080"/></rect>
<rect x="420.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3249" values="#e5e7eb;#808080"/></rect>
<rect x="450.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3288" values="#e5e7eb;#808080"/></rect>
<rect x="480.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3327" values="#e5e7eb;#707070"/></rect>
<rect x="510.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3366" values="#e5e7eb;#505050"/></rect>
<rect x="540.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3405" values="#e5e7eb;#505050"/></rect>
<rect x="570.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#303030"/></rect>
<rect x="600.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3483" values="#e5e7eb;#303030"/></rect>
<rect x="630.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3522" values="#e5e7eb;#303030"/></rect>
<rect x="660.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3561" values="#e5e7eb;#303030"/></rect>
<rect x="690.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#303030"/></rect>
<rect x="720.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3639" values="#e5e7eb;#202020"/></rect>
<rect x="750.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3678" values="#e5e7eb;#202020"/></rect>
<rect x="60.0" y="326" width="720.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="378" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">④ 本当の影の濃さ(正解)</text>
<rect x="60.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2780" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="90.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2820" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="120.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2859" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="150.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="180.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2937" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="210.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2976" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="240.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3015" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="270.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3054" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="300.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3093" values="#e5e7eb;#808080"/></rect>
<rect x="330.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3132" values="#e5e7eb;#808080"/></rect>
<rect x="360.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3171" values="#e5e7eb;#808080"/></rect>
<rect x="390.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3210" values="#e5e7eb;#808080"/></rect>
<rect x="420.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3249" values="#e5e7eb;#808080"/></rect>
<rect x="450.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3288" values="#e5e7eb;#808080"/></rect>
<rect x="480.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3327" values="#e5e7eb;#808080"/></rect>
<rect x="510.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3366" values="#e5e7eb;#808080"/></rect>
<rect x="540.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3405" values="#e5e7eb;#333333"/></rect>
<rect x="570.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#333333"/></rect>
<rect x="600.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3483" values="#e5e7eb;#333333"/></rect>
<rect x="630.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3522" values="#e5e7eb;#333333"/></rect>
<rect x="660.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3561" values="#e5e7eb;#333333"/></rect>
<rect x="690.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#333333"/></rect>
<rect x="720.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3639" values="#e5e7eb;#333333"/></rect>
<rect x="750.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3678" values="#e5e7eb;#333333"/></rect>
<rect x="60.0" y="386" width="720.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4008;0.4010;1.0000" values="0;0;1;1"/><rect x="60" y="436" width="840" height="74" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="76" y="460" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">正解とのずれ: 点描のまま(縦に平均)0.146 → PCF 0.040</text>
<text x="76" y="484" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">点描は、1 マスに 0 か 1 しか書けない。周りの平均で、薄い影を作る(特別なテクスチャは不要)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">シャドウ マップは「物がある / ない」の 2 値。薄い影は書けない<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">透明度を、点描(しきい値との比較)で、書く / 書かないに変える<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;0.2779;0.2780;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">PCF で平均すると、点描が混ざって、薄い影になる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2780;0.4008;0.4010;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">透明度に近い濃さになる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4008;0.4010;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:stipple-shadow:end -->

### Example of Stippling {#ステッポリングの例}

```hlsl
float threshold = Bayer4x4(pixel_position);
clip(opacity - threshold);
```

<strong>ディザ（Bayer 行列・IGN）</strong>で、**透明度の割合**だけ**画素を残し**、**影の濃さ**を**確率的に**表現します。**ノイズ**が出るので、**PCF や TAA**で**消します**。

## Common Mistakes {#よくあるミス}

??? failure "ガラスが真っ黒な影を落とす"
    **半透明は影を落とさない・ステップリング・色付き影**のいずれか。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **深度のシャドウ マップは、半透明の薄い影を表せない**
    - [x] **ステップリング・色付きの影で近似**

## References {#参考}

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## Related Pages {#関連ページ}

- [Special Cases](index.md)
- [ブレンドとソート](../../translucency/blending-sorting/index.md)
