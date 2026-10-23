---
title: Domain Warping
tags:
  - 描画
---

# Domain Warping

<strong>ノイズの入力座標を別のノイズでゆがませる</strong>と、うねった有機的な形になります。直線的な規則性が崩れて自然に見えます。このページではドメイン ワーピングを説明します。

!!! tip "ポイント"
    - f(p) → f(p + g(p)) の形にする。
    - ゆがみの強さで形が変わる。
    - fBm と組み合わせる。
    - コストはノイズの評価が増える分。

!!! info "このページを読む前に"
    - [Terrain Generation](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:domain-warp:begin -->

<svg class="fig illust motion" data-fig="domain-warp" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-domain-warp" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ドメイン ワープ: 地形を読む「座標」を、別のノイズでゆがめると、自然な曲がりくねりができる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">縞模様(直線)を、座標ゆがめの強さ 0 → 2 → 5 → 9 で、ゆがめる。縞の曲がり具合を、計算する</text>
<rect x="30" y="100" width="220.0" height="76.0" fill="#ffffff" stroke="#64748b" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#64748b">強さ 0</text>
<rect x="32.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0676" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0684" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0693" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0676" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0684" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0693" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0684" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0693" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0693" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0960" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0960" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="32.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#1e293b"/></rect>
<rect x="39.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#1e293b"/></rect>
<rect x="46.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#1e293b"/></rect>
<rect x="53.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="60.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="68.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="75.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#1e293b"/></rect>
<rect x="82.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#1e293b"/></rect>
<rect x="89.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#1e293b"/></rect>
<rect x="96.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="104.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="111.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="118.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#1e293b"/></rect>
<rect x="125.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#1e293b"/></rect>
<rect x="132.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#1e293b"/></rect>
<rect x="140.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="147.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="154.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="161.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#1e293b"/></rect>
<rect x="168.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#1e293b"/></rect>
<rect x="176.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#1e293b"/></rect>
<rect x="183.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="190.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="197.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="204.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0960" values="#e5e7eb;#1e293b"/></rect>
<rect x="212.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#1e293b"/></rect>
<rect x="219.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#1e293b"/></rect>
<rect x="226.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="233.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="240.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#e5e7eb;#f8fafc"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1332;0.1333;1.0000" values="0;0;1;1"/><text x="30" y="196" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">縞の曲がり幅 0 画素</text>
</g>
<rect x="255" y="100" width="220.0" height="76.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="255" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">強さ 2</text>
<rect x="257.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2667" values="#e5e7eb;#f8fafc"/></rect>
<rect x="264.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2676" values="#e5e7eb;#f8fafc"/></rect>
<rect x="271.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2684" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#1e293b"/></rect>
<rect x="285.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#1e293b"/></rect>
<rect x="307.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="329.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#1e293b"/></rect>
<rect x="350.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#1e293b"/></rect>
<rect x="372.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="393.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#1e293b"/></rect>
<rect x="408.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#1e293b"/></rect>
<rect x="415.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="429.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="451.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#1e293b"/></rect>
<rect x="257.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2676" values="#e5e7eb;#f8fafc"/></rect>
<rect x="264.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2684" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#e5e7eb;#1e293b"/></rect>
<rect x="285.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#1e293b"/></rect>
<rect x="307.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="329.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#1e293b"/></rect>
<rect x="372.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="393.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#1e293b"/></rect>
<rect x="408.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#1e293b"/></rect>
<rect x="415.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="429.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="451.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2684" values="#e5e7eb;#f8fafc"/></rect>
<rect x="264.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="285.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#1e293b"/></rect>
<rect x="307.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="329.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#1e293b"/></rect>
<rect x="372.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="393.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#1e293b"/></rect>
<rect x="408.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#1e293b"/></rect>
<rect x="429.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="451.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#f8fafc"/></rect>
<rect x="264.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="285.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#1e293b"/></rect>
<rect x="307.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#1e293b"/></rect>
<rect x="329.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#1e293b"/></rect>
<rect x="372.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="393.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#1e293b"/></rect>
<rect x="408.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#1e293b"/></rect>
<rect x="429.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="451.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="264.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="285.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#1e293b"/></rect>
<rect x="307.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#1e293b"/></rect>
<rect x="329.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#1e293b"/></rect>
<rect x="372.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#1e293b"/></rect>
<rect x="393.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#1e293b"/></rect>
<rect x="408.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#1e293b"/></rect>
<rect x="429.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#1e293b"/></rect>
<rect x="451.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#1e293b"/></rect>
<rect x="264.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="285.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="307.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#1e293b"/></rect>
<rect x="329.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#1e293b"/></rect>
<rect x="372.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#1e293b"/></rect>
<rect x="393.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="408.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#1e293b"/></rect>
<rect x="429.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#1e293b"/></rect>
<rect x="451.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#1e293b"/></rect>
<rect x="264.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="285.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="307.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#1e293b"/></rect>
<rect x="329.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#1e293b"/></rect>
<rect x="372.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#1e293b"/></rect>
<rect x="393.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="408.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="429.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#1e293b"/></rect>
<rect x="451.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#1e293b"/></rect>
<rect x="264.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="285.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="307.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#1e293b"/></rect>
<rect x="329.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="372.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#1e293b"/></rect>
<rect x="393.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="408.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="429.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#1e293b"/></rect>
<rect x="451.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#1e293b"/></rect>
<rect x="264.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#1e293b"/></rect>
<rect x="285.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="307.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#1e293b"/></rect>
<rect x="329.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="350.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="372.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="386.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#1e293b"/></rect>
<rect x="393.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="408.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="429.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#e5e7eb;#1e293b"/></rect>
<rect x="451.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="257.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#1e293b"/></rect>
<rect x="264.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#1e293b"/></rect>
<rect x="271.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#1e293b"/></rect>
<rect x="278.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#1e293b"/></rect>
<rect x="285.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="293.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="307.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#1e293b"/></rect>
<rect x="314.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#1e293b"/></rect>
<rect x="321.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#1e293b"/></rect>
<rect x="329.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="343.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#1e293b"/></rect>
<rect x="350.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#1e293b"/></rect>
<rect x="357.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#1e293b"/></rect>
<rect x="365.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="372.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="379.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#1e293b"/></rect>
<rect x="386.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#1e293b"/></rect>
<rect x="393.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#1e293b"/></rect>
<rect x="401.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#1e293b"/></rect>
<rect x="408.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="415.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="422.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="429.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#1e293b"/></rect>
<rect x="437.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#e5e7eb;#1e293b"/></rect>
<rect x="444.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#1e293b"/></rect>
<rect x="451.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="458.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="465.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#e5e7eb;#f8fafc"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/><text x="255" y="196" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">縞の曲がり幅 3 画素</text>
</g>
<rect x="480" y="100" width="220.0" height="76.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="480" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">強さ 5</text>
<rect x="482.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4667" values="#e5e7eb;#1e293b"/></rect>
<rect x="489.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4676" values="#e5e7eb;#f8fafc"/></rect>
<rect x="496.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#f8fafc"/></rect>
<rect x="503.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#e5e7eb;#1e293b"/></rect>
<rect x="510.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="525.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#1e293b"/></rect>
<rect x="532.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#1e293b"/></rect>
<rect x="539.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="546.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="554.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="561.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#1e293b"/></rect>
<rect x="568.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#1e293b"/></rect>
<rect x="575.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#1e293b"/></rect>
<rect x="582.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#1e293b"/></rect>
<rect x="597.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#1e293b"/></rect>
<rect x="604.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="611.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="618.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="626.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#1e293b"/></rect>
<rect x="633.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#1e293b"/></rect>
<rect x="640.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="647.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="654.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="669.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#1e293b"/></rect>
<rect x="690.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4676" values="#e5e7eb;#f8fafc"/></rect>
<rect x="489.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#f8fafc"/></rect>
<rect x="496.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#e5e7eb;#1e293b"/></rect>
<rect x="503.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#1e293b"/></rect>
<rect x="510.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="525.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#1e293b"/></rect>
<rect x="532.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#1e293b"/></rect>
<rect x="539.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="546.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="554.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="561.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="582.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#1e293b"/></rect>
<rect x="597.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#1e293b"/></rect>
<rect x="604.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="611.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="618.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="626.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#1e293b"/></rect>
<rect x="633.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#1e293b"/></rect>
<rect x="640.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="647.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="669.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#1e293b"/></rect>
<rect x="683.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#1e293b"/></rect>
<rect x="690.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#f8fafc"/></rect>
<rect x="489.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#e5e7eb;#f8fafc"/></rect>
<rect x="496.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#1e293b"/></rect>
<rect x="503.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="510.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#1e293b"/></rect>
<rect x="525.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#1e293b"/></rect>
<rect x="532.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#1e293b"/></rect>
<rect x="539.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="546.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="554.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="561.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="582.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#1e293b"/></rect>
<rect x="597.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#1e293b"/></rect>
<rect x="604.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="611.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="618.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#1e293b"/></rect>
<rect x="626.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#1e293b"/></rect>
<rect x="633.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="640.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#1e293b"/></rect>
<rect x="647.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="669.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#1e293b"/></rect>
<rect x="690.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#e5e7eb;#f8fafc"/></rect>
<rect x="489.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#1e293b"/></rect>
<rect x="496.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#1e293b"/></rect>
<rect x="503.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="510.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#1e293b"/></rect>
<rect x="525.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#1e293b"/></rect>
<rect x="532.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#1e293b"/></rect>
<rect x="539.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#1e293b"/></rect>
<rect x="546.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#1e293b"/></rect>
<rect x="554.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#1e293b"/></rect>
<rect x="561.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="582.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#1e293b"/></rect>
<rect x="597.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#1e293b"/></rect>
<rect x="604.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="611.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="618.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#1e293b"/></rect>
<rect x="626.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="633.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="640.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#1e293b"/></rect>
<rect x="647.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="662.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="669.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="690.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="489.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#1e293b"/></rect>
<rect x="496.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#1e293b"/></rect>
<rect x="503.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="510.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#1e293b"/></rect>
<rect x="525.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#1e293b"/></rect>
<rect x="532.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#1e293b"/></rect>
<rect x="539.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#1e293b"/></rect>
<rect x="546.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#1e293b"/></rect>
<rect x="554.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#1e293b"/></rect>
<rect x="561.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="582.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#1e293b"/></rect>
<rect x="597.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#1e293b"/></rect>
<rect x="604.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="611.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#1e293b"/></rect>
<rect x="618.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#1e293b"/></rect>
<rect x="626.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="633.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="640.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#1e293b"/></rect>
<rect x="647.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="662.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="669.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="690.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#1e293b"/></rect>
<rect x="489.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#1e293b"/></rect>
<rect x="496.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#1e293b"/></rect>
<rect x="503.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="510.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#1e293b"/></rect>
<rect x="525.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="532.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#1e293b"/></rect>
<rect x="539.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#1e293b"/></rect>
<rect x="546.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#1e293b"/></rect>
<rect x="554.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#1e293b"/></rect>
<rect x="561.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="582.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#1e293b"/></rect>
<rect x="597.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="604.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="611.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#1e293b"/></rect>
<rect x="618.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="626.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="633.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="640.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#1e293b"/></rect>
<rect x="647.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="669.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="690.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#1e293b"/></rect>
<rect x="489.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#1e293b"/></rect>
<rect x="496.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="503.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="510.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="525.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="532.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="539.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#1e293b"/></rect>
<rect x="546.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#1e293b"/></rect>
<rect x="554.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="561.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#1e293b"/></rect>
<rect x="582.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#1e293b"/></rect>
<rect x="597.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="604.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#1e293b"/></rect>
<rect x="611.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#1e293b"/></rect>
<rect x="618.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="626.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="633.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#1e293b"/></rect>
<rect x="640.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#1e293b"/></rect>
<rect x="647.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#1e293b"/></rect>
<rect x="669.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="690.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#1e293b"/></rect>
<rect x="489.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#1e293b"/></rect>
<rect x="496.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="503.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="510.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="518.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="525.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="532.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="539.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#1e293b"/></rect>
<rect x="546.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#1e293b"/></rect>
<rect x="554.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="561.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#1e293b"/></rect>
<rect x="582.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#1e293b"/></rect>
<rect x="590.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="597.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="604.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#1e293b"/></rect>
<rect x="611.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#1e293b"/></rect>
<rect x="618.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="626.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="633.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="640.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#1e293b"/></rect>
<rect x="647.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#1e293b"/></rect>
<rect x="669.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="690.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#e5e7eb;#1e293b"/></rect>
<rect x="482.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#1e293b"/></rect>
<rect x="489.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#1e293b"/></rect>
<rect x="496.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#1e293b"/></rect>
<rect x="503.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#1e293b"/></rect>
<rect x="510.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#1e293b"/></rect>
<rect x="518.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="525.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="532.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="539.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#1e293b"/></rect>
<rect x="546.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#1e293b"/></rect>
<rect x="554.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="561.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="575.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#1e293b"/></rect>
<rect x="582.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="590.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="597.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#1e293b"/></rect>
<rect x="604.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#1e293b"/></rect>
<rect x="611.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#1e293b"/></rect>
<rect x="618.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="626.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="633.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="640.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="647.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#e5e7eb;#1e293b"/></rect>
<rect x="669.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="690.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="482.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#e5e7eb;#1e293b"/></rect>
<rect x="489.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#1e293b"/></rect>
<rect x="496.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#e5e7eb;#1e293b"/></rect>
<rect x="503.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#1e293b"/></rect>
<rect x="510.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#1e293b"/></rect>
<rect x="518.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="525.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="532.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#1e293b"/></rect>
<rect x="539.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#e5e7eb;#1e293b"/></rect>
<rect x="546.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#1e293b"/></rect>
<rect x="554.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="561.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="568.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#e5e7eb;#1e293b"/></rect>
<rect x="575.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#1e293b"/></rect>
<rect x="582.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="590.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="597.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#1e293b"/></rect>
<rect x="604.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#1e293b"/></rect>
<rect x="611.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#1e293b"/></rect>
<rect x="618.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="626.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="633.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="640.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="647.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#1e293b"/></rect>
<rect x="654.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#e5e7eb;#1e293b"/></rect>
<rect x="662.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#1e293b"/></rect>
<rect x="669.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="676.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="683.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="690.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#e5e7eb;#f8fafc"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5332;0.5333;1.0000" values="0;0;1;1"/><text x="480" y="196" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">縞の曲がり幅 4 画素</text>
</g>
<rect x="705" y="100" width="220.0" height="76.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="705" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">強さ 9</text>
<rect x="707.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6676" values="#e5e7eb;#1e293b"/></rect>
<rect x="721.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6684" values="#e5e7eb;#f8fafc"/></rect>
<rect x="728.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6693" values="#e5e7eb;#1e293b"/></rect>
<rect x="735.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="743.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="750.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#1e293b"/></rect>
<rect x="757.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="771.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="779.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#1e293b"/></rect>
<rect x="793.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#1e293b"/></rect>
<rect x="800.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#1e293b"/></rect>
<rect x="836.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#1e293b"/></rect>
<rect x="843.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="851.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="858.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#1e293b"/></rect>
<rect x="872.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="879.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#1e293b"/></rect>
<rect x="887.0" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.2" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#1e293b"/></rect>
<rect x="901.4" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#1e293b"/></rect>
<rect x="908.6" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="915.8" y="102.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="707.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6676" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6684" values="#e5e7eb;#1e293b"/></rect>
<rect x="721.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6693" values="#e5e7eb;#f8fafc"/></rect>
<rect x="728.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6702" values="#e5e7eb;#1e293b"/></rect>
<rect x="735.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="743.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#1e293b"/></rect>
<rect x="757.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="771.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="779.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="793.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="800.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="822.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#1e293b"/></rect>
<rect x="836.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#1e293b"/></rect>
<rect x="843.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="851.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#1e293b"/></rect>
<rect x="858.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="872.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#1e293b"/></rect>
<rect x="879.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#1e293b"/></rect>
<rect x="894.2" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#1e293b"/></rect>
<rect x="901.4" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#1e293b"/></rect>
<rect x="908.6" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="915.8" y="109.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="707.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6684" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6693" values="#e5e7eb;#f8fafc"/></rect>
<rect x="721.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6702" values="#e5e7eb;#1e293b"/></rect>
<rect x="728.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#f8fafc"/></rect>
<rect x="735.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="743.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#1e293b"/></rect>
<rect x="757.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="771.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="779.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="786.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#1e293b"/></rect>
<rect x="793.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="800.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#1e293b"/></rect>
<rect x="836.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="843.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="851.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#1e293b"/></rect>
<rect x="858.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="865.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#1e293b"/></rect>
<rect x="872.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="879.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#1e293b"/></rect>
<rect x="894.2" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#1e293b"/></rect>
<rect x="901.4" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#1e293b"/></rect>
<rect x="908.6" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#1e293b"/></rect>
<rect x="915.8" y="116.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#1e293b"/></rect>
<rect x="707.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6693" values="#e5e7eb;#f8fafc"/></rect>
<rect x="714.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6702" values="#e5e7eb;#1e293b"/></rect>
<rect x="721.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#1e293b"/></rect>
<rect x="728.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#f8fafc"/></rect>
<rect x="735.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#1e293b"/></rect>
<rect x="743.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#1e293b"/></rect>
<rect x="757.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="771.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#1e293b"/></rect>
<rect x="779.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#1e293b"/></rect>
<rect x="793.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#1e293b"/></rect>
<rect x="800.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#1e293b"/></rect>
<rect x="836.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="843.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#1e293b"/></rect>
<rect x="851.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="858.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#1e293b"/></rect>
<rect x="872.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="879.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#1e293b"/></rect>
<rect x="894.2" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#1e293b"/></rect>
<rect x="901.4" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#1e293b"/></rect>
<rect x="908.6" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#1e293b"/></rect>
<rect x="915.8" y="123.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6951" values="#e5e7eb;#1e293b"/></rect>
<rect x="707.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6702" values="#e5e7eb;#f8fafc"/></rect>
<rect x="714.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#1e293b"/></rect>
<rect x="721.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#1e293b"/></rect>
<rect x="728.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="735.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#1e293b"/></rect>
<rect x="743.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#1e293b"/></rect>
<rect x="757.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#1e293b"/></rect>
<rect x="764.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#1e293b"/></rect>
<rect x="771.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#1e293b"/></rect>
<rect x="779.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#1e293b"/></rect>
<rect x="793.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="800.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="836.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#1e293b"/></rect>
<rect x="843.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="851.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#1e293b"/></rect>
<rect x="858.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#1e293b"/></rect>
<rect x="872.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="879.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.2" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="901.4" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#1e293b"/></rect>
<rect x="908.6" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6951" values="#e5e7eb;#1e293b"/></rect>
<rect x="915.8" y="130.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#1e293b"/></rect>
<rect x="707.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#1e293b"/></rect>
<rect x="721.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#f8fafc"/></rect>
<rect x="728.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="735.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#1e293b"/></rect>
<rect x="743.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="757.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="771.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="779.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="793.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="800.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#f8fafc"/></rect>
<rect x="829.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="836.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#1e293b"/></rect>
<rect x="843.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="851.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#1e293b"/></rect>
<rect x="858.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="872.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="879.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.2" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="901.4" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="908.6" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#1e293b"/></rect>
<rect x="915.8" y="138.0" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6969" values="#e5e7eb;#1e293b"/></rect>
<rect x="707.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#1e293b"/></rect>
<rect x="721.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="728.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="735.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="743.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#f8fafc"/></rect>
<rect x="750.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#f8fafc"/></rect>
<rect x="757.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="771.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#1e293b"/></rect>
<rect x="779.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#f8fafc"/></rect>
<rect x="793.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="800.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#1e293b"/></rect>
<rect x="815.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="829.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#1e293b"/></rect>
<rect x="836.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="843.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="851.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#1e293b"/></rect>
<rect x="858.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="872.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="879.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.2" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="901.4" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="908.6" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6969" values="#e5e7eb;#1e293b"/></rect>
<rect x="915.8" y="145.2" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6978" values="#e5e7eb;#1e293b"/></rect>
<rect x="707.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#f8fafc"/></rect>
<rect x="721.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="728.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#f8fafc"/></rect>
<rect x="735.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#1e293b"/></rect>
<rect x="743.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#f8fafc"/></rect>
<rect x="757.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="771.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#1e293b"/></rect>
<rect x="779.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#f8fafc"/></rect>
<rect x="793.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="800.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#1e293b"/></rect>
<rect x="807.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#1e293b"/></rect>
<rect x="815.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="822.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#f8fafc"/></rect>
<rect x="836.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="843.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#1e293b"/></rect>
<rect x="851.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#1e293b"/></rect>
<rect x="858.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#1e293b"/></rect>
<rect x="872.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#1e293b"/></rect>
<rect x="879.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.2" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="901.4" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="908.6" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6978" values="#e5e7eb;#1e293b"/></rect>
<rect x="915.8" y="152.4" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6987" values="#e5e7eb;#1e293b"/></rect>
<rect x="707.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6738" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#f8fafc"/></rect>
<rect x="721.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#1e293b"/></rect>
<rect x="728.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#1e293b"/></rect>
<rect x="735.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#1e293b"/></rect>
<rect x="743.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#1e293b"/></rect>
<rect x="757.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#1e293b"/></rect>
<rect x="771.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#1e293b"/></rect>
<rect x="779.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#1e293b"/></rect>
<rect x="786.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="793.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="800.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#1e293b"/></rect>
<rect x="807.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#f8fafc"/></rect>
<rect x="836.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="843.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#1e293b"/></rect>
<rect x="851.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#1e293b"/></rect>
<rect x="858.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#1e293b"/></rect>
<rect x="872.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#1e293b"/></rect>
<rect x="879.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6951" values="#e5e7eb;#f8fafc"/></rect>
<rect x="887.0" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.2" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="901.4" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="908.6" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="915.8" y="159.6" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="707.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#1e293b"/></rect>
<rect x="714.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#1e293b"/></rect>
<rect x="721.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#1e293b"/></rect>
<rect x="728.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#1e293b"/></rect>
<rect x="735.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#1e293b"/></rect>
<rect x="743.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#1e293b"/></rect>
<rect x="750.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#f8fafc"/></rect>
<rect x="757.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#f8fafc"/></rect>
<rect x="764.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#1e293b"/></rect>
<rect x="771.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#1e293b"/></rect>
<rect x="779.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#f8fafc"/></rect>
<rect x="786.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#f8fafc"/></rect>
<rect x="793.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#1e293b"/></rect>
<rect x="800.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6862" values="#e5e7eb;#f8fafc"/></rect>
<rect x="807.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#f8fafc"/></rect>
<rect x="815.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#1e293b"/></rect>
<rect x="822.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#1e293b"/></rect>
<rect x="829.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6898" values="#e5e7eb;#f8fafc"/></rect>
<rect x="836.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#f8fafc"/></rect>
<rect x="843.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6916" values="#e5e7eb;#f8fafc"/></rect>
<rect x="851.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#f8fafc"/></rect>
<rect x="858.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#1e293b"/></rect>
<rect x="865.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#1e293b"/></rect>
<rect x="872.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6951" values="#e5e7eb;#1e293b"/></rect>
<rect x="879.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#1e293b"/></rect>
<rect x="887.0" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6969" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.2" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6978" values="#e5e7eb;#f8fafc"/></rect>
<rect x="901.4" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6987" values="#e5e7eb;#f8fafc"/></rect>
<rect x="908.6" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6996" values="#e5e7eb;#f8fafc"/></rect>
<rect x="915.8" y="166.8" width="7.5" height="7.5" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7004" values="#e5e7eb;#f8fafc"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7332;0.7333;1.0000" values="0;0;1;1"/><text x="705" y="196" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">縞の曲がり幅 5 画素</text>
</g>
<rect x="30" y="240" width="900" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="230" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">1 本の線で見る(座標 x を、ノイズでずらして、縞を読む)</text>
<path d="M60.0,372.0 L72.5,372.0 L85.0,332.0 L97.5,332.0 L110.0,332.0 L122.5,332.0 L135.0,332.0 L147.5,372.0 L160.0,372.0 L172.5,372.0 L185.0,372.0 L197.5,372.0 L210.0,332.0 L222.5,332.0 L235.0,332.0 L247.5,332.0 L260.0,332.0 L272.5,332.0 L285.0,372.0 L297.5,372.0 L310.0,372.0 L322.5,372.0 L335.0,372.0 L347.5,372.0 L360.0,372.0 L372.5,332.0 L385.0,332.0 L397.5,332.0 L410.0,332.0 L422.5,332.0 L435.0,332.0 L447.5,332.0 L460.0,372.0 L472.5,372.0 L485.0,372.0 L497.5,372.0 L510.0,372.0 L522.5,372.0 L535.0,332.0 L547.5,332.0 L560.0,332.0 L572.5,332.0 L585.0,332.0 L597.5,372.0 L610.0,372.0 L622.5,372.0 L635.0,372.0 L647.5,372.0 L660.0,332.0 L672.5,332.0 L685.0,332.0 L697.5,332.0 L710.0,332.0 L722.5,372.0 L735.0,372.0 L747.5,372.0 L760.0,372.0 L772.5,372.0 L785.0,332.0 L797.5,332.0" fill="none" stroke="#2563eb" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000" values="0;0;1;1"/></path>
<path d="M60.0,372.0 L72.5,372.0 L85.0,372.0 L97.5,372.0 L110.0,332.0 L122.5,332.0 L135.0,332.0 L147.5,372.0 L160.0,372.0 L172.5,372.0 L185.0,372.0 L197.5,372.0 L210.0,332.0 L222.5,332.0 L235.0,332.0 L247.5,332.0 L260.0,332.0 L272.5,372.0 L285.0,372.0 L297.5,372.0 L310.0,372.0 L322.5,372.0 L335.0,372.0 L347.5,372.0 L360.0,372.0 L372.5,372.0 L385.0,372.0 L397.5,372.0 L410.0,372.0 L422.5,332.0 L435.0,332.0 L447.5,332.0 L460.0,332.0 L472.5,332.0 L485.0,332.0 L497.5,372.0 L510.0,372.0 L522.5,372.0 L535.0,372.0 L547.5,332.0 L560.0,332.0 L572.5,332.0 L585.0,332.0 L597.5,332.0 L610.0,372.0 L622.5,372.0 L635.0,372.0 L647.5,332.0 L660.0,332.0 L672.5,332.0 L685.0,372.0 L697.5,372.0 L710.0,372.0 L722.5,372.0 L735.0,372.0 L747.5,372.0 L760.0,332.0 L772.5,332.0 L785.0,332.0 L797.5,332.0" fill="none" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9198;0.9200;1.0000" values="0;0;1;1"/></path>
<path d="M60.0,332.0 L72.5,332.0 L85.0,332.0 L97.5,372.0 L110.0,372.0 L122.5,332.0 L135.0,332.0 L147.5,332.0 L160.0,372.0 L172.5,372.0 L185.0,372.0 L197.5,332.0 L210.0,332.0 L222.5,332.0 L235.0,332.0 L247.5,332.0 L260.0,372.0 L272.5,372.0 L285.0,372.0 L297.5,372.0 L310.0,372.0 L322.5,372.0 L335.0,332.0 L347.5,372.0 L360.0,372.0 L372.5,372.0 L385.0,372.0 L397.5,372.0 L410.0,372.0 L422.5,372.0 L435.0,372.0 L447.5,372.0 L460.0,372.0 L472.5,332.0 L485.0,332.0 L497.5,332.0 L510.0,372.0 L522.5,372.0 L535.0,372.0 L547.5,372.0 L560.0,372.0 L572.5,332.0 L585.0,332.0 L597.5,332.0 L610.0,372.0 L622.5,372.0 L635.0,372.0 L647.5,332.0 L660.0,332.0 L672.5,372.0 L685.0,372.0 L697.5,372.0 L710.0,332.0 L722.5,332.0 L735.0,332.0 L747.5,332.0 L760.0,332.0 L772.5,372.0 L785.0,372.0 L797.5,372.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9732;0.9733;1.0000" values="0;0;1;1"/></path>
<path d="M60.0,332.0 L72.5,332.0 L85.0,332.0 L97.5,332.0 L110.0,332.0 L122.5,332.0 L135.0,372.0 L147.5,372.0 L160.0,372.0 L172.5,372.0 L185.0,372.0 L197.5,372.0 L210.0,332.0 L222.5,332.0 L235.0,332.0 L247.5,332.0 L260.0,332.0 L272.5,332.0 L285.0,372.0 L297.5,372.0 L310.0,372.0 L322.5,372.0 L335.0,372.0 L347.5,372.0 L360.0,332.0 L372.5,332.0 L385.0,332.0 L397.5,332.0 L410.0,332.0 L422.5,332.0 L435.0,372.0 L447.5,372.0 L460.0,372.0 L472.5,372.0 L485.0,372.0 L497.5,372.0 L510.0,332.0 L522.5,332.0 L535.0,332.0 L547.5,332.0 L560.0,332.0 L572.5,332.0 L585.0,372.0 L597.5,372.0 L610.0,372.0 L622.5,372.0 L635.0,372.0 L647.5,372.0 L660.0,332.0 L672.5,332.0 L685.0,332.0 L697.5,332.0 L710.0,332.0 L722.5,332.0 L735.0,372.0 L747.5,372.0 L760.0,372.0 L772.5,372.0 L785.0,372.0 L797.5,372.0" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="4 4"/>
<text x="40" y="430" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1332;0.1333;1.0000" values="1;1;0;0"/></text>
<text x="40" y="430" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1332;0.1333;0.3332;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="430" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;0.5332;0.5333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="430" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5332;0.5333;0.7332;0.7333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="430" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7332;0.7333;1.0000" values="0;0;1;1"/></text>
<text x="100" y="430" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">画素(縞の曲がり幅)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="0;0;1"/><rect x="480" y="410" width="450" height="74" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">読む座標を、ノイズで動かす = ワープ</text>
<text x="496" y="457" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">強さを上げるほど、直線が、蛇行する。ノイズを重ねてもよい</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">まっすぐな縞(高さの元になる模様)がある<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">読む場所を、別のノイズで動かすと、縞が曲がる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">強さが大きいほど、複雑に、うねる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:domain-warp:end -->

## ドメイン ワーピング
<strong>ノイズの入力座標を別のノイズでゆがめる</strong>と、自然に曲がりくねった形になります。

```hlsl
float WarpedFbm(float2 p) {
  float2 q = float2(Fbm(p, 4, 2.0, 0.5), Fbm(p + float2(5.2, 1.3), 4, 2.0, 0.5));
  float2 r = float2(Fbm(p + 4.0 * q + float2(1.7, 9.2), 4, 2.0, 0.5),
                    Fbm(p + 4.0 * q + float2(8.3, 2.8), 4, 2.0, 0.5));
  return Fbm(p + 4.0 * r, 4, 2.0, 0.5);
}
```

| 点 | 説明 |
| --- | --- |
| ワープの強さ（4.0） | 大きいと渦のようにねじれる |
| 層を重ねる | q → r → 最終と2 段で複雑に |
| コスト | fBm を何度も呼ぶので重い。生成時（ベイク）に使い実行時には焼いたテクスチャを読む |

## ドメイン ワーピングとは

ノイズに座標を渡す前に <strong>座標そのものを、別のノイズでずらす</strong>手法です。ノイズ関数 `f(p)` の代わりに `f(p + w(p))` を計算します。`w` はずらし量を返す別のノイズ関数です。

```text
普通:        height = fbm(p)
ワーピング:   height = fbm(p + k × fbm2(p))
```

「domain（定義域）」は、関数の入力のことです。入力をゆがめるのでこの名前が付いています。

## なぜゆがめるのか

fBm や勾配ノイズの地形は、<strong>どの方向にも同じ性質</strong>（等方的）です。人工的で 砂の山のように見えることがあります。現実の地形は風・水・断層で流れるように曲がった形をしています。ドメイン ワーピングを行うと、ノイズが渦を巻いたり折れ曲がったりして、ずっと有機的な形になります。

| 比較 | fBm | ワーピングした fBm |
| --- | --- | --- |
| 尾根・谷の形 | 同じ方向に、ばらばら | 曲がって流れる |
| 全体の印象 | 砂山、小さな丘の集まり | 大陸、浸食された山地 |
| 細部 | 一様 | 場所によって、密度が変わる |

## 実装

```hlsl
// ずらし量を作る関数。2 つのノイズで、x と y を別々にずらす。
float2 Warp(float2 p, uint seed) {
  return float2(Fbm(p + float2(0.0, 0.0), 4, 2.0, 0.5, seed),
                Fbm(p + float2(5.2, 1.3), 4, 2.0, 0.5, seed + 1));   // 少し離れた場所から読む
}

float WarpedFbm(float2 p, float strength, uint seed) {
  float2 q = p + strength * Warp(p, seed);
  return Fbm(q, 6, 2.0, 0.5, seed + 2);
}
```

`float2(5.2, 1.3)` のような <strong>ずらしたオフセット</strong>は、x と y のずらし量が同じにならないようにするためです。同じノイズを使うと斜め方向にしか、ずれません。

### 2 重のワーピング

Quilez は ワーピングの結果を、もう一度、ワーピングの入力にする方法を紹介しています。

```hlsl
float WarpedFbm2(float2 p, float strength, uint seed) {
  float2 q = Warp(p, seed);                          // 1 回目
  float2 r = Warp(p + strength * q, seed + 10);      // 1 回目の結果で、ずらして、2 回目
  return Fbm(p + strength * r, 6, 2.0, 0.5, seed + 2);
}
```

```text
f(p + fbm(p + fbm(p)))
```

重ねるほど渦や折りたたまれた形が、複雑になります。そのかわり ノイズの計算が回数分、増えます（1 回で 3 つ、2 重で 5 つ分の fBm）。

## パラメーター

| パラメーター | 一般的な値 | 効果 |
| --- | --- | --- |
| `strength`（ずらし量） | 0.3〜2.0（周波数 1 に対して） | 小さいと、わずかなゆがみ。大きいと渦、折りたたみ |
| ワーピング用の fBm の周波数 | 本体より、低い（1/2〜1/4） | 低いと大きな、ゆっくりした曲がり。高いと細かいゆがみ |
| ワーピング用の fBm の、オクターブ数 | 2〜4 | 少なくてもよい（形が、なめらかなので） |

!!! tip "ずらし量を、場所で変える"
    ずらし量を <strong>別の低周波ノイズで、変える</strong>と「あまりゆがんでいない平地」と「大きくゆがんだ山岳」が、同じ地形の中に共存します。`strength * mask(p)` の形です。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 傾きが不連続になる | ずらし量が大きいと、座標の写像が折りたたまれて高さが、鋭く切れることがある。ずらし量を控えめにする |
| コスト | fBm が 3〜5 個分に増える。オフラインで焼き込むのが基本 |
| 傾きの解析的な計算 | 座標のずらしで微分も、連鎖律で変わる。侵食風の式と組み合わせるときは、ワーピングの微分も計算する必要がある |
| ワールド座標 | ずらしを加えた座標も、ワールド座標で計算する（タイルの継ぎ目をなくす）（[fBm](fbm.md)） |

## 使いどころ

| 場面 | 使い方 |
| --- | --- |
| 大陸・島の形 | 低周波に、強くワーピングして海岸線を複雑にする |
| 山岳地帯 | 尾根ノイズの座標を、ワーピングして尾根を曲げる（[Ridged Noise](ridge.md)） |
| 砂漠 | 縞模様の砂丘を、少しだけゆがめる |
| 地層・岩の模様 | 色のノイズを、ワーピングして流れるような模様にする |

## よくあるミス

??? failure "地形に、規則的な模様が見える"
    <strong>ドメイン ワーピング</strong>でゆがめる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 座標をノイズでゆがませる

## 参考

- Quilez, "fBm" と "Domain Warping", iquilezles.org（ノイズの重ね合わせと、座標のゆがめ方の解説）
- Ebert, Musgrave, Peachey, Perlin, Worley, "Texturing and Modeling: A Procedural Approach", 3rd Edition, Morgan Kaufmann, 2002（fBm、マルチフラクタル、リッジ ノイズ）
- Perlin, "Improving Noise", SIGGRAPH 2002（補間関数を 5 次式にし、勾配の選び方を直した改良版）
- Galin, Guérin, Peytavie, Cordonnier, Cani, Beneš, Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR)

## 関連ページ

- [Terrain Generation](index.md)
- [fBm](fbm.md)
