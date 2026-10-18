---
title: Hashed Alpha
tags:
  - 描画
---

# Hashed Alpha

**ハッシュド アルファは、画素ごとにランダムなしきい値で clip する手法**で、**平均すると、半透明に見えます**。**TAA と組み合わせると、ノイズが消えて、なめらかな半透明**になります。このページでは、**ハッシュド アルファの仕組み**を説明します。

!!! tip "ポイント"
    - **画素ごとのハッシュで、しきい値を変える**。
    - **平均すると、アルファ値どおりの透明度**。
    - **ソート不要・深度も書ける**。
    - **TAA が前提**（そうでないと、ノイズが見える）。

<!-- fig:hashed-alpha-sweep:begin -->

<svg class="fig illust motion" data-fig="hashed-alpha-sweep" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hashed-alpha-sweep" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ハッシュ アルファ: 画素ごとのでたらめなしきい値で切り、重ねるとなめらかになる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">アルファが左 0.1 → 右 0.9 の板。1 フレームだけだとザラザラ、8 フレーム平均で本来の濃さに近づく</text>
<rect x="30" y="100" width="408.0" height="136.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">1 フレームだけ(0 か 1 のザラザラ)</text>
<rect x="30.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="47.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="64.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="81.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="115.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="132.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="149.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="166.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="183.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="200.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="217.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="234.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="251.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="268.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="285.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="302.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="319.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="336.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="353.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="370.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="387.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="404.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="30.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="47.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="64.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="81.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="115.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="132.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="149.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="166.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="183.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="200.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="217.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="234.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="251.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="268.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="285.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="302.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="319.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="336.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="353.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="370.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="387.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="404.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="30.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="47.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="64.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="81.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="115.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="132.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="149.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="166.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="183.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="200.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="217.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="234.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="251.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="268.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="285.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="302.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="319.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="336.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="353.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="370.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="387.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="404.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="30.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="47.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="64.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="81.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="115.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="132.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="149.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="166.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="183.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="200.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="217.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="234.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="251.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="268.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="285.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="302.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="319.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="336.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="353.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="370.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="387.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="404.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="30.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="47.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="64.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="81.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="115.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="132.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="149.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="166.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="183.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="200.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="217.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="234.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="251.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="268.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="285.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="302.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="319.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="336.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="353.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="370.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="387.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="404.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="30.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="47.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="64.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="81.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="115.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="132.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="149.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="166.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="183.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="200.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="217.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="234.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="251.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="268.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="285.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="302.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="319.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="336.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="353.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="370.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="387.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="404.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="30.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="47.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="64.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="81.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="115.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="132.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="149.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="166.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="183.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="200.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="217.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="234.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="251.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="268.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="285.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="302.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="319.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="336.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="353.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="370.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="387.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="404.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="30.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="47.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="64.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="81.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="98.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="115.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="132.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="149.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="166.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="183.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="200.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="217.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="234.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="251.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="268.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="285.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="302.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="319.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="336.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="353.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="370.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="387.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="404.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#0f766e"/></rect>
<rect x="421.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="495" y="100" width="408.0" height="136.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="495" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">フレームを重ねた平均</text>
<rect x="495.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="512.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="529.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#bed9d8"/></rect>
<rect x="546.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="563.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="580.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#84b8b5;#9bc5c3;#84b8b5;#94c1bf;#a1c8c7"/></rect>
<rect x="597.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="614.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="631.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#84b8b5"/></rect>
<rect x="648.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#6caba7;#5da29d;#529c97;#66a8a3"/></rect>
<rect x="665.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#84b8b5;#9bc5c3;#84b8b5;#94c1bf;#84b8b5"/></rect>
<rect x="682.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#bed9d8"/></rect>
<rect x="699.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#bed9d8;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="716.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#368c86;#308982;#499792"/></rect>
<rect x="733.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#308982;#499792"/></rect>
<rect x="750.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#3e908a;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="767.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#5da29d;#529c97;#499792"/></rect>
<rect x="784.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#2c8680"/></rect>
<rect x="801.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#368c86;#308982;#2c8680"/></rect>
<rect x="818.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#529c97;#499792"/></rect>
<rect x="835.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#529c97;#499792"/></rect>
<rect x="852.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#308982;#499792"/></rect>
<rect x="869.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="886.0" y="100.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="495.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="512.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="529.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#b5d4d3;#a1c8c7"/></rect>
<rect x="546.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="563.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="580.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="597.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#c9e0e0;#d1e4e4;#b5d4d3;#bed9d8"/></rect>
<rect x="614.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#bed9d8"/></rect>
<rect x="631.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="648.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#84b8b5;#6caba7;#5da29d;#73afab;#84b8b5"/></rect>
<rect x="665.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#84b8b5"/></rect>
<rect x="682.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#368c86;#308982;#2c8680"/></rect>
<rect x="699.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#368c86;#308982;#499792"/></rect>
<rect x="716.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#bed9d8;#c9e0e0;#aacecd;#b5d4d3;#a1c8c7"/></rect>
<rect x="733.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#9bc5c3;#aacecd;#94c1bf;#84b8b5"/></rect>
<rect x="750.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#84b8b5;#73afab;#66a8a3"/></rect>
<rect x="767.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#84b8b5;#9bc5c3;#84b8b5;#94c1bf;#a1c8c7"/></rect>
<rect x="784.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#368c86;#308982;#499792"/></rect>
<rect x="801.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#6caba7;#84b8b5;#73afab;#66a8a3"/></rect>
<rect x="818.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#368c86;#308982;#2c8680"/></rect>
<rect x="835.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="852.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#368c86;#308982;#2c8680"/></rect>
<rect x="869.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="886.0" y="117.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#3e908a;#368c86;#529c97;#499792"/></rect>
<rect x="495.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="512.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="529.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="546.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="563.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#368c86;#529c97;#66a8a3"/></rect>
<rect x="580.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="597.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="614.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#b5d4d3;#bed9d8"/></rect>
<rect x="631.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="648.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="665.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#c9e0e0;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="682.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#6caba7;#5da29d;#529c97;#499792"/></rect>
<rect x="699.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#84b8b5;#9bc5c3;#84b8b5;#94c1bf;#a1c8c7"/></rect>
<rect x="716.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="733.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="750.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#5da29d;#529c97;#499792"/></rect>
<rect x="767.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#368c86;#529c97;#66a8a3"/></rect>
<rect x="784.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#6caba7;#5da29d;#529c97;#499792"/></rect>
<rect x="801.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="818.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="835.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="852.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#84b8b5;#6caba7;#84b8b5;#73afab;#84b8b5"/></rect>
<rect x="869.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="886.0" y="134.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="495.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="512.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="529.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="546.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d7e7e8;#dbeaea"/></rect>
<rect x="563.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#84b8b5;#6caba7;#5da29d;#529c97;#66a8a3"/></rect>
<rect x="580.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#bed9d8;#9bc5c3;#aacecd;#b5d4d3;#a1c8c7"/></rect>
<rect x="597.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="614.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="631.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="648.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#6caba7;#84b8b5;#94c1bf;#84b8b5"/></rect>
<rect x="665.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#84b8b5;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="682.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#368c86;#529c97;#66a8a3"/></rect>
<rect x="699.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#6caba7;#84b8b5;#73afab;#84b8b5"/></rect>
<rect x="716.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#368c86;#529c97;#66a8a3"/></rect>
<rect x="733.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#9bc5c3;#84b8b5;#73afab;#66a8a3"/></rect>
<rect x="750.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="767.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#84b8b5;#9bc5c3;#84b8b5;#73afab;#66a8a3"/></rect>
<rect x="784.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="801.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="818.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="835.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="852.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="869.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#308982;#2c8680"/></rect>
<rect x="886.0" y="151.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="495.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="512.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="529.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="546.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="563.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#84b8b5;#6caba7;#84b8b5;#94c1bf;#a1c8c7"/></rect>
<rect x="580.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#84b8b5;#9bc5c3;#aacecd;#b5d4d3;#a1c8c7"/></rect>
<rect x="597.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#b5d4d3;#a1c8c7"/></rect>
<rect x="614.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#bed9d8;#c9e0e0;#aacecd;#94c1bf;#84b8b5"/></rect>
<rect x="631.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="648.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="665.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#9bc5c3;#84b8b5;#94c1bf;#84b8b5"/></rect>
<rect x="682.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#bed9d8;#9bc5c3;#84b8b5;#94c1bf;#84b8b5"/></rect>
<rect x="699.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#5da29d;#73afab;#84b8b5"/></rect>
<rect x="716.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#6caba7;#84b8b5;#94c1bf;#a1c8c7"/></rect>
<rect x="733.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#6caba7;#5da29d;#529c97;#499792"/></rect>
<rect x="750.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="767.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#6caba7;#5da29d;#529c97;#499792"/></rect>
<rect x="784.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="801.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#6caba7;#5da29d;#529c97;#499792"/></rect>
<rect x="818.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="835.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="852.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#368c86;#308982;#499792"/></rect>
<rect x="869.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="886.0" y="168.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="495.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d7e7e8;#dbeaea"/></rect>
<rect x="512.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="529.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="546.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#84b8b5;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="563.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#84b8b5;#9bc5c3;#aacecd;#b5d4d3;#a1c8c7"/></rect>
<rect x="580.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#84b8b5;#73afab;#84b8b5"/></rect>
<rect x="597.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#bed9d8;#c9e0e0;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="614.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#6caba7;#84b8b5;#94c1bf;#a1c8c7"/></rect>
<rect x="631.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#368c86;#529c97;#66a8a3"/></rect>
<rect x="648.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#6caba7;#84b8b5;#73afab;#84b8b5"/></rect>
<rect x="665.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="682.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#84b8b5;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="699.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="716.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="733.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="750.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#84b8b5"/></rect>
<rect x="767.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#5da29d;#529c97;#499792"/></rect>
<rect x="784.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#84b8b5;#94c1bf;#84b8b5"/></rect>
<rect x="801.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#bed9d8;#9bc5c3;#aacecd;#94c1bf;#84b8b5"/></rect>
<rect x="818.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#6caba7;#84b8b5;#73afab;#66a8a3"/></rect>
<rect x="835.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#5da29d;#529c97;#499792"/></rect>
<rect x="852.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#499792"/></rect>
<rect x="869.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="886.0" y="185.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="495.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="512.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#b5d4d3;#a1c8c7"/></rect>
<rect x="529.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#bed9d8"/></rect>
<rect x="546.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="563.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#dbeaea"/></rect>
<rect x="580.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#bed9d8;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="597.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="614.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#c9e0e0;#d1e4e4;#b5d4d3;#a1c8c7"/></rect>
<rect x="631.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#aacecd;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="648.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#5da29d;#529c97;#499792"/></rect>
<rect x="665.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#5da29d;#73afab;#84b8b5"/></rect>
<rect x="682.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#84b8b5;#9bc5c3;#84b8b5;#73afab;#66a8a3"/></rect>
<rect x="699.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="716.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#84b8b5;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="733.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#bed9d8;#9bc5c3;#84b8b5;#73afab;#84b8b5"/></rect>
<rect x="750.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#368c86;#308982;#499792"/></rect>
<rect x="767.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#84b8b5;#6caba7;#5da29d;#529c97;#499792"/></rect>
<rect x="784.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="801.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#3e908a;#5da29d;#529c97;#499792"/></rect>
<rect x="818.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#3e908a;#5da29d;#529c97;#66a8a3"/></rect>
<rect x="835.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#308982;#2c8680"/></rect>
<rect x="852.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#6caba7;#5da29d;#73afab;#84b8b5"/></rect>
<rect x="869.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#308982;#2c8680"/></rect>
<rect x="886.0" y="202.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="495.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="512.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="529.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#6caba7;#84b8b5;#94c1bf;#a1c8c7"/></rect>
<rect x="546.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="563.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#bed9d8;#c9e0e0;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="580.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#f8fafc;#d1e4e4;#d7e7e8;#dbeaea"/></rect>
<rect x="597.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#bed9d8;#9bc5c3;#aacecd;#b5d4d3;#bed9d8"/></rect>
<rect x="614.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"/>
<rect x="631.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#aacecd;#84b8b5;#9bc5c3;#aacecd;#94c1bf;#a1c8c7"/></rect>
<rect x="648.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#6caba7;#84b8b5;#94c1bf;#84b8b5"/></rect>
<rect x="665.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#3e908a;#368c86;#529c97;#66a8a3"/></rect>
<rect x="682.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#9bc5c3;#aacecd;#b5d4d3;#a1c8c7"/></rect>
<rect x="699.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#6caba7;#84b8b5;#94c1bf;#84b8b5"/></rect>
<rect x="716.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#aacecd;#84b8b5;#6caba7;#5da29d;#529c97;#66a8a3"/></rect>
<rect x="733.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#6caba7;#5da29d;#529c97;#66a8a3"/></rect>
<rect x="750.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#499792;#6caba7;#5da29d;#529c97;#499792"/></rect>
<rect x="767.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="784.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#5da29d;#499792;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<rect x="801.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="818.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#84b8b5;#5da29d;#84b8b5;#6caba7;#84b8b5;#73afab;#66a8a3"/></rect>
<rect x="835.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#368c86;#308982;#2c8680"/></rect>
<rect x="852.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e;#0f766e"/></rect>
<rect x="869.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#0f766e;#0f766e;#0f766e;#499792;#3e908a;#368c86;#308982;#499792"/></rect>
<rect x="886.0" y="219.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0769;0.1641;0.2513;0.3385;0.4256;0.5128;0.6000;0.6872" values="#f8fafc;#f8fafc;#84b8b5;#5da29d;#499792;#6caba7;#5da29d;#73afab;#66a8a3"/></rect>
<text x="30" y="262" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">正解(アルファ通り)</text>
<rect x="30.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#e1edee"/></rect>
<rect x="47.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#d9e8e9"/></rect>
<rect x="64.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#d0e4e4"/></rect>
<rect x="81.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#c8dfdf"/></rect>
<rect x="98.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#c0dada"/></rect>
<rect x="115.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#b8d6d5"/></rect>
<rect x="132.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#b0d1d0"/></rect>
<rect x="149.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#a8cdcb"/></rect>
<rect x="166.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#a0c8c6"/></rect>
<rect x="183.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#98c3c1"/></rect>
<rect x="200.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#90bfbc"/></rect>
<rect x="217.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#88bab7"/></rect>
<rect x="234.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#7fb6b3"/></rect>
<rect x="251.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#77b1ae"/></rect>
<rect x="268.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#6fada9"/></rect>
<rect x="285.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#67a8a4"/></rect>
<rect x="302.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#5fa39f"/></rect>
<rect x="319.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#579f9a"/></rect>
<rect x="336.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#4f9a95"/></rect>
<rect x="353.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#479690"/></rect>
<rect x="370.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#3f918b"/></rect>
<rect x="387.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#378c86"/></rect>
<rect x="404.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#2e8881"/></rect>
<rect x="421.0" y="268.0" width="17.3" height="17.3" fill="#f8fafc"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#f8fafc;#26837c"/></rect>
<rect x="30" y="268" width="408.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="316" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">平均したフレーム数:</text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;1.0000" values="1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">1<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;0.1639;0.1641;1.0000" values="0;0;1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">2<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1639;0.1641;0.2511;0.2513;1.0000" values="0;0;1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">3<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2511;0.2513;0.3383;0.3385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">4<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3383;0.3385;0.4254;0.4256;1.0000" values="0;0;1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4254;0.4256;0.5126;0.5128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5126;0.5128;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">7<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;0.6870;0.6872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="205" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">8<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6870;0.6872;1.0000" values="0;0;1;1"/></text>
<rect x="495" y="290" width="408.0" height="110" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="495" y="280" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">正解とのずれ(小さいほど良い)</text>
<line x1="505" y1="318.0" x2="865" y2="318.0" stroke="#e5484d" stroke-width="2" stroke-dasharray="6 5"/>
<text x="865" y="313.0" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">1 フレーム 0.406</text>
<circle cx="511.0" cy="318.0" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;1.0000" values="0;0;1;1"/></circle>
<text x="511.0" y="310.0" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.406<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;1.0000" values="0;0;1;1"/></text>
<circle cx="559.0" cy="338.69" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1639;0.1641;1.0000" values="0;0;1;1"/></circle>
<text x="559.0" y="330.69" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.266<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1639;0.1641;1.0000" values="0;0;1;1"/></text>
<circle cx="607.0" cy="345.88" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2511;0.2513;1.0000" values="0;0;1;1"/></circle>
<text x="607.0" y="337.88" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.217<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2511;0.2513;1.0000" values="0;0;1;1"/></text>
<circle cx="655.0" cy="350.12" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3383;0.3385;1.0000" values="0;0;1;1"/></circle>
<text x="655.0" y="342.12" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.189<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3383;0.3385;1.0000" values="0;0;1;1"/></text>
<circle cx="703.0" cy="353.58" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4254;0.4256;1.0000" values="0;0;1;1"/></circle>
<text x="703.0" y="345.58" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.165<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4254;0.4256;1.0000" values="0;0;1;1"/></text>
<circle cx="751.0" cy="356.49" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5126;0.5128;1.0000" values="0;0;1;1"/></circle>
<text x="751.0" y="348.49" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.146<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5126;0.5128;1.0000" values="0;0;1;1"/></text>
<circle cx="799.0" cy="358.25" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/></circle>
<text x="799.0" y="350.25" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.134<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/></text>
<circle cx="847.0" cy="358.8" r="4.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6870;0.6872;1.0000" values="0;0;1;1"/></circle>
<text x="847.0" y="350.8" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#2563eb" opacity="0">0.130<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6870;0.6872;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.8049;0.8051;1.0000" values="0;0;1;1"/><rect x="30" y="420" width="900" height="86" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="444" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1e3a8a">1 フレーム: ずれ 0.406 → 8 フレーム平均: ずれ 0.130</text>
<text x="46" y="469" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">画素ごとのしきい値を毎フレーム変えるので、「画素ごとに違う運」が平均されて、アルファに近づく</text>
<text x="46" y="491" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">(TAA と組み合わせて使う。しきい値を毎フレーム変えないと、ずっとザラザラのまま)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">アルファが しきい値より大きい画素だけを描く(しきい値は画素ごとにでたらめ)<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">毎フレームしきい値を変えて、重ねる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;0.8049;0.8051;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">並べ替えも、特別な描画もいらないが、ノイズと引き換え<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.8049;0.8051;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:hashed-alpha-sweep:end -->

## Hashed Alpha (Stochastic Alpha Test) {#ハッシュド-アルファ確率的アルファ-テスト}
**アルファを「確率」と見なし、画素ごとのノイズ（ハッシュ）と比べて、捨てるか残すか**を決めます。**1 フレームでは、ノイズ状**ですが、**TAA（時間蓄積）で平均されて、滑らかな半透明**に見えます。

```hlsl
float Hash(float2 p) {
  return frac(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
}

float alpha = albedo_texture.Sample(linear_sampler, input.uv).a;
float threshold = Hash(input.position.xy);
clip(alpha - threshold);
```

| 点 | 説明 |
| --- | --- |
| <strong>`threshold`（ランダム）</strong> | **画素ごとに違う閾値**。**アルファが 0.3 なら、約 30% の画素が残る** |
| **TAA と併用** | **毎フレーム、違うノイズ**にすると、**時間平均で滑らかな半透明** |
| **ミップにも強い** | **アルファが薄くなっても、確率的に残る**ので、**スカスカにならない** |
| **欠点** | **TAA がないと、ノイズが見える** |

**ハッシュ（ノイズ）を、ワールド座標・オブジェクト座標**から作る（**Wyman と McGuire の Hashed Alpha Testing**）と、**動いても、ノイズが物体に貼りつく**ので**安定**します。

## Common Mistakes {#よくあるミス}

??? failure "ハッシュド アルファのノイズが消えない"
    **TAA を有効**にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **ランダムなしきい値で clip**
    - [x] **TAA でなめらかになる**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [Alpha Testing](index.md)
- [TAA](../../postprocess/antialiasing/taa.md)
- [Dithered Transparency](dither.md)
