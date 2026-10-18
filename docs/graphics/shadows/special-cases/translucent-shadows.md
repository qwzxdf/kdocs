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

## 半透明の影
**ガラス・煙・半透明の布**は**光を部分的に通します**。**シャドウ マップは、深度しか持たない**ので<strong>「完全に遮る」か「完全に通す」</strong>の**2 択**になります。

| 方法 | 内容 |
| --- | --- |
| **影を落とさない** | **一番簡単**。**半透明の物**は**影を落とさない**設定 |
| <strong>スクリーン ドア（ステッポリング）</strong> | <strong>透明度に応じた、確率的（ディザ パターン）</strong>に、**一部の画素を `clip`**。**少し遮る**。**PCF・TAA**で**平均され**て、**薄い影**に見える |
| **不透明として扱う** | **ガラスでも影を濃く**落とす（**嘘だが手軽**） |
| **色付きシャドウ マップ** | **別のシャドウ マップ**（**RGB ＋ 深度**）に、**半透明の物の色と透過率**を**乗算ブレンド**で保存。**ステンドグラス**のような**色付きの影**。**不透明の物の影とは、別に引く** |
| <strong>多層（Deep Shadow Maps）</strong> | **深度ごとの透過率**を保存（**煙・髪**）。**メモリが重く**、**専用** |
| <strong>レイトレース影（Any-Hit）</strong> | **Any-Hit シェーダー**で、**透過率を累積**（[Ray-Traced Shadows](../ray-traced.md)） |

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

### ステッポリングの例

```hlsl
float threshold = Bayer4x4(pixel_position);
clip(opacity - threshold);
```

<strong>ディザ（Bayer 行列・IGN）</strong>で、**透明度の割合**だけ**画素を残し**、**影の濃さ**を**確率的に**表現します。**ノイズ**が出るので、**PCF や TAA**で**消します**。

## 問題：半透明の物は、光を、一部、通す

ガラス窓、色付きの、ステンド グラス、煙、薄い、布は、**光を、一部だけ、通します**。通常の、シャドウ マップは、**光が通るか、完全に遮られるか**の、**二択**です。そのまま、**半透明の物を、描く**と、**完全な影**に、なるか、**影が、まったく、できない**かの、**どちらか**に、なってしまいます。

| 物 | 現実の影 | 通常のシャドウ マップ（不透明として、描く） | 描かない場合 |
| --- | --- | --- | --- |
| 無色の、ガラス | ほぼ、透明（わずかに、暗い） | **真っ黒**（間違い） | 影なし（近い） |
| 色付きガラス | **色付きの影** | 真っ黒 | 影なし |
| 煙・霧 | **薄い**影（密度に、比例） | 真っ黒 | 影なし |

## 方法 1：影を、落とさない（最も簡単）

**半透明の物は、シャドウ パスで、描かない**。**無色の、ガラス**や、**薄い**物は、これで、**十分**な場合が、多いです。

## 方法 2：アルファに応じた、確率的な影

**アルファが、0.3 の、物**を、**30% の画素だけ、不透明として、シャドウ マップに、描きます**。**PCF**で、読むと、**平均されて、30% の、濃さの影**に、なります（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。

```hlsl
// 半透明の影: アルファを、ランダムなしきい値と、比べて、確率的に、深度を書く。
void main(float4 pos : SV_Position, float2 uv : TEXCOORD0) {
  float alpha = g_albedo.Sample(g_linear_wrap, uv).a * g_opacity;
  clip(alpha - BlueNoiseThreshold(pos.xy));        // アルファが小さいほど、深度が書かれにくい
}
```

| 長所 | 短所 |
| --- | --- |
| 簡単。**PCF が、そのまま、使える** | **ノイズ**（TAA や、広い PCF で、減らす） |
| 半透明の度合いが、**反映**される | **色**は、反映されない（影は、グレー） |

## 方法 3：色付きの、影

**色付きガラス**の、影は、**ガラスの色**に、染まります。**光が、ガラスを、通る間に、吸収**されて、**ガラスの色**だけが、残るためです。**色付きの、影**を、作るには、**シャドウ マップを、2 枚**、使います。

| シャドウ マップ | 内容 |
| --- | --- |
| ① **不透明な物だけ**の、深度 | 通常のシャドウ マップ |
| ② **半透明な物の、色（透過色）** | **半透明な物**を、描き、**各画素の、光の、透過色**を、**乗算ブレンド**で、書き込む（カラー テクスチャ） |

```hlsl
// 半透明の、シャドウ パス（②）: 光の透過色を、乗算で積む（RGB のレンダー ターゲット）。
// ブレンド: SrcBlend = ZERO、DestBlend = SRC_COLOR（現在の値 × 出力色）。初期値は (1,1,1)。
float4 main(PSInput input) : SV_Target {
  float4 tint = g_albedo.Sample(g_linear_wrap, input.uv);
  // 透過色: α が小さい（透明）ほど、白（影響なし）。α が大きいほど、ガラスの色。
  float3 transmit = lerp(float3(1, 1, 1), tint.rgb, tint.a);
  return float4(transmit, 1.0);
}
```

```hlsl
// メイン パス: 不透明な影（深度）で光を遮り、半透明な影（色）で光を染める。
float opaque_lit = SampleOpaqueShadow(world_pos);             // 0 or 1（PCF 込み）
float3 tint = g_translucent_shadow.Sample(g_linear_clamp, uv).rgb;   // 光が、ガラスを通ったあとの、色
// ただし、ガラスより、手前にある画素だけ、色を受ける（ガラスの、奥にある物だけが、染まる）。
float glass_depth = g_translucent_depth.Sample(g_linear_clamp, uv);
float3 light_color = (depth > glass_depth) ? g_light_color * tint : g_light_color;
float3 lit = light_color * opaque_lit;
```

**「画素が、ガラスの、奥にあるか」**を、判定するために、**ガラスの、深度**（半透明な物の、最も、手前の深度）も、**別に、保存**します。

## 方法 4：深度の、分布を、保存する（Deep / Opacity シャドウ マップ）

**半透明の物が、複数、重なる**（煙、髪、葉）と、**光は、重なった層を、順に、通る**ので、**通過した、光の割合**は、**奥に進むほど、減っていきます**。この、**深度ごとの、光の通過率**を、**シャドウ マップに、保存**する方法です。

| 手法 | 内容 |
| --- | --- |
| **Deep Shadow Maps**（Lokovic と Veach、2000） | 画素ごとに、**深度に対する、透過率の、関数**（区分的な、線形）を、保存。**映画の、レンダリング**で、使われた |
| **Opacity Shadow Maps**（Kim と Neumann、2001） | 深度を、**複数の層**（スライス）に、分け、**各層での、不透明度**を、**テクスチャ**に、保存 |

```text
Opacity Shadow Maps:
   層 1（手前） 層 2    層 3    層 4（奥）
   ┌────┐     ┌────┐  ┌────┐  ┌────┐        各層で、そこまでの、累積した、不透明度を、保存
   │ 0.2│     │ 0.5│  │ 0.8│  │ 0.9│
   └────┘     └────┘  └────┘  └────┘
画素の深度が、層 3 と 4 の間 → 層 3 と 4 の、不透明度を、補間 → 約 0.85 の、影
```

実装は、**複雑**で、**メモリも、重い**（層の数だけ、テクスチャ）。**髪の毛**（[Hair Shadows](../../skin-hair/hair/shadows.md)）、**煙・雲**（[Cloud Shadows](../../atmosphere/clouds/shadows.md)）など、**半透明の層が、密に重なる**物で、使われます。

## 使い分け

| 物 | 方法 |
| --- | --- |
| 無色の、窓ガラス | **影を、落とさない**（方法 1） |
| 薄い、布、半透明の、植物 | **確率的な影**（方法 2） |
| **色付きガラス**、ステンド グラス | **色付きの影**（方法 3）。重要な、演出なら |
| 煙、霧、パーティクル | **確率的な影**、または、**ボリューム ライティング**（[Volumetric Fog](../../atmosphere/volumetric-fog/index.md)） |
| 髪、雲（密に重なる、層） | **Deep / Opacity シャドウ マップ**、または、専用の手法 |

## よくあるミス

??? failure "ガラスが真っ黒な影を落とす"
    **半透明は影を落とさない・ステップリング・色付き影**のいずれか。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **深度のシャドウ マップは、半透明の薄い影を表せない**
    - [x] **ステップリング・色付きの影で近似**

## 参考

- Lokovic, Veach, "Deep Shadow Maps", SIGGRAPH 2000（半透明の、影）
- Kim, Neumann, "Opacity Shadow Maps", Eurographics Workshop on Rendering 2001
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Special Cases](index.md)
- [Alpha Blending and Sorting](../../translucency/blending-sorting/index.md)
