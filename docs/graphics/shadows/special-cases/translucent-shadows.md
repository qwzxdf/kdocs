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

半透明の影の表現は 6 通りあります。<strong>影を落とさない</strong>のが最も簡単です。<strong>スクリーン ドア（ステッポリング）</strong>は、透明度に応じた確率的なディザ パターンで、一部の画素を `clip` します。少し遮るので、PCF や TAA で平均されて薄い影に見えます。<strong>不透明として扱う</strong>のは、ガラスでも影を濃く落とす手軽な（嘘の）方法です。<strong>色付きシャドウ マップ</strong>は、別のシャドウ マップ（RGB と深度）に、半透明の物の色と透過率を乗算ブレンドで保存します。ステンドグラスのような色付きの影が出ますが、不透明の物の影とは別に引きます。<strong>多層（Deep Shadow Maps）</strong>は、深度ごとの透過率を保存します（煙・髪）。メモリが重く、専用です。<strong>レイトレース影（Any-Hit）</strong>は、Any-Hit シェーダーで透過率を累積します（[Ray-Traced Shadows](../ray-traced.md)）。

<!-- fig:stipple-shadow:begin -->

<svg class="fig illust motion" data-fig="stipple-shadow" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-stipple-shadow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">半透明の影:ステッポリング（点描）で、濃さを点の数で表す</text>
<rect x="60" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="84" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="108" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="132" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="156" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="180" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="204" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="228" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="252" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="276" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="300" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="324" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="348" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="372" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="396" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="420" y="90" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="60" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="84" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="108" y="114" width="23" height="23" fill="#f1f5f9"/>
<rect x="132" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="156" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="180" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="204" y="114" width="23" height="23" fill="#f1f5f9"/>
<rect x="228" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="252" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="276" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="300" y="114" width="23" height="23" fill="#f1f5f9"/>
<rect x="324" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="348" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="372" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="396" y="114" width="23" height="23" fill="#f1f5f9"/>
<rect x="420" y="114" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="60" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="84" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="108" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="132" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="156" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="180" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="204" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="228" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="252" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="276" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="300" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="324" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="348" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="372" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="396" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="420" y="138" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="60" y="162" width="23" height="23" fill="#f1f5f9"/>
<rect x="84" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="108" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="132" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="156" y="162" width="23" height="23" fill="#f1f5f9"/>
<rect x="180" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="204" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="228" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="252" y="162" width="23" height="23" fill="#f1f5f9"/>
<rect x="276" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="300" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="324" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="348" y="162" width="23" height="23" fill="#f1f5f9"/>
<rect x="372" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="396" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="420" y="162" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="60" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="84" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="108" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="132" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="156" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="180" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="204" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="228" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="252" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="276" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="300" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="324" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="348" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="372" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="396" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="420" y="186" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="60" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="84" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="108" y="210" width="23" height="23" fill="#f1f5f9"/>
<rect x="132" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="156" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="180" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="204" y="210" width="23" height="23" fill="#f1f5f9"/>
<rect x="228" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="252" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="276" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="300" y="210" width="23" height="23" fill="#f1f5f9"/>
<rect x="324" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="348" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="372" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="396" y="210" width="23" height="23" fill="#f1f5f9"/>
<rect x="420" y="210" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="60" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="84" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="108" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="132" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="156" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="180" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="204" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="228" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="252" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="276" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="300" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="324" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="348" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="372" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="396" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#1e293b;#1e293b;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="420" y="234" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b"/></rect>
<rect x="60" y="258" width="23" height="23" fill="#f1f5f9"/>
<rect x="84" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="108" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="132" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="156" y="258" width="23" height="23" fill="#f1f5f9"/>
<rect x="180" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="204" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="228" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="252" y="258" width="23" height="23" fill="#f1f5f9"/>
<rect x="276" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="300" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="324" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="348" y="258" width="23" height="23" fill="#f1f5f9"/>
<rect x="372" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<rect x="396" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#1e293b"/></rect>
<rect x="420" y="258" width="23" height="23" fill="#f1f5f9"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#f1f5f9;#f1f5f9;#1e293b;#1e293b;#1e293b"/></rect>
<text x="60" y="56" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">影の濃さ（アルファ）0.1 → 黒くする画素の割合 ≒ 10 %<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0830;0.0833;0.2663;0.2667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">影の濃さ（アルファ）0.3 → 黒くする画素の割合 ≒ 30 %<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2663;0.2667;0.4497;0.4500;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">影の濃さ（アルファ）0.5 → 黒くする画素の割合 ≒ 50 %<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4497;0.4500;0.6330;0.6333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">影の濃さ（アルファ）0.7 → 黒くする画素の割合 ≒ 70 %<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6330;0.6333;0.8163;0.8167;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="56" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">影の濃さ（アルファ）0.9 → 黒くする画素の割合 ≒ 90 %<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.8163;0.8167;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="330" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">ディザ(4×4 の閾値表)で、画素ごとに「影にする・しない」を決める。</text>
<text x="60" y="354" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">PCF でぼかすと、点が混ざって、薄い影に見える。アルファ ブレンドの影より安く、ソートも不要。</text>
<rect x="520" y="300" width="200" height="34" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0833;0.2667;0.4500;0.6333;0.8167" values="#f1f5f9;#e8e8ea;#bcbcbe;#8e8e94;#626268;#34343e"/></rect>
<text x="620" y="292" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">ぼかした結果</text>
</svg>

<!-- fig:stipple-shadow:end -->

### ステッポリングの例

```hlsl
float threshold = Bayer4x4(pixel_position);
clip(opacity - threshold);
```

<strong>ディザ（Bayer 行列・IGN）</strong>で、**透明度の割合**だけ**画素を残し**、**影の濃さ**を**確率的に**表現します。**ノイズ**が出るので、**PCF や TAA**で**消します**。

## よくあるミス

??? failure "ガラスが真っ黒な影を落とす"
    **半透明は影を落とさない・ステップリング・色付き影**のいずれか。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **深度のシャドウ マップは、半透明の薄い影を表せない**
    - [x] **ステップリング・色付きの影で近似**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Special Cases](index.md)
- [ブレンドとソート](../../translucency/blending-sorting/index.md)
