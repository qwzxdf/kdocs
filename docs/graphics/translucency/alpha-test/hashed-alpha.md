---
title: Hashed Alpha
tags:
  - 描画
---

# Hashed Alpha

葉の板をアルファ 0.5 で `clip` すると、遠くで葉がやせてスカスカになり縁にはジャギーが出ます。アルファを 0.5 より下げた部分は、完全に消えてしまうからです。アルファを「消すか残すか」の 2 値ではなく、「残る確率」として扱えばこの問題を避けられます。

<strong>ハッシュド アルファはアルファを確率と見なして、画素ごとのランダムなしきい値と比べ捨てるか残すかを決めます</strong>。1 フレームではノイズ状ですが、TAA で時間方向に平均すると、アルファどおりの半透明に見えます。このページでは仕組みハッシュの選び方（実測つき）、ノイズが TAA でどこまで減るかオブジェクト空間のハッシュ、シェーダーでの使い方を説明します。

!!! tip "ポイント"
    - しきい値が 0〜1 の一様乱数ならアルファ `a` の画素が残る確率は、ちょうど `a` です。
    - 半透明の表現ができて、ソートが要らず深度も書けます。
    - ノイズが出るので、TAA が前提です。TAA がないと画面でざらつきが見えます。
    - ハッシュは一様であるだけでなく、近くの画素で偏りが出にくいものが望ましいです。IGN は 4×4 のまとまりのばらつきが、ランダムの半分以下でした。
    - 影のパスでも同じハッシュを使うと影も確率的に薄くなります。

!!! info "このページを読む前に"
    - [Alpha Testing](index.md)（このセクション全体の地図と読む順番）

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

## 仕組み: アルファを確率として扱う {#idea}

Wyman と McGuire（2017）は、アルファ テストを確率的に行う方法を示しました。画素ごとにランダムなしきい値を決めて、アルファがそのしきい値より大きければ、描きます。

```text
通常のアルファ テスト:   alpha > 0.5            （全画素でしきい値が同じ）
ハッシュド アルファ:     alpha > hash(位置)      （画素ごとにしきい値がランダム）
```

しきい値が 0〜1 の一様乱数ならアルファ `a` の画素が描かれる確率は、ちょうど `a` です。アルファ 0.3 なら画素の約 30 % が描かれます。複数のフレームで平均すれば 30 % の濃さの半透明に見えます。

通常のアルファ テストとの違いは次のとおりです。

- アルファ 0.3 の部分は通常は 0.5 で切るので消えます。ハッシュドでは 30 % の画素が描かれて、薄く見えます。
- 縁は通常は階段状（ジャギー）です。ハッシュドはノイズが混ざりながら、なめらかです。
- 遠くの葉は通常はミップでアルファが薄くなってスカスカになります。ハッシュドは薄くなったアルファが確率として残るので、平均すると元の密度に近くなります（[Foliage Translucency](../../terrain/vegetation/translucency.md)）。
- ノイズは通常はありません。ハッシュドはあります（TAA で減ります）。

## ハッシュの選び方 {#hash}

しきい値を作るハッシュには 2 つの性質が欲しくなります。分布が一様なこと（残る割合がアルファと一致すること）と近くの画素で偏りが出にくいことです。3 つのハッシュを Python で 512 × 512 画素に適用して測りました。

まず、サイン関数のハッシュです。手軽ですが実装によって精度が違います。

```hlsl
Texture2D<float4> g_albedo : register(t0);
SamplerState g_linear_wrap : register(s0);

cbuffer FrameConstants : register(b0) {
  float g_alpha_cutoff_scale;   // しきい値の倍率。1.0 が標準
  uint g_frame_index;           // TAA 用。フレームごとにパターンをずらす
  float2 _pad;
};

// 古典的なサイン関数のハッシュ。手軽だが、GPU によって結果が違うことがある
float HashSin(float2 p) {
  return frac(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
}
```

次に、整数のハッシュ（PCG）です。結果が GPU によらず決まります。

```hlsl
uint Pcg(uint v) {
  uint state = v * 747796405u + 2891336453u;
  uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
  return (word >> 22u) ^ word;
}

float HashPcg(uint2 p, uint frame) {
  uint h = Pcg(p.x + Pcg(p.y + Pcg(frame)));
  return (h & 0xffffffu) / 16777216.0;           // 24 ビットを 0..1 に
}
```

最後に、Interleaved Gradient Noise（IGN、Jimenez 2014）です。式が短く近い画素でばらつきが抑えられます。

```hlsl
float InterleavedGradientNoise(float2 pixel) {
  return frac(52.9829189 * frac(dot(pixel, float2(0.06711056, 0.00583715))));
}
```

測った結果は次のとおりです。

- サイン関数: 一様性の誤差（KS 距離）は 0.0022 で、アルファ 0.3 で残る割合は 0.299 でした。4×4 の画素のまとまりで残る割合のばらつき（標準偏差）は 0.114 です。
- PCG: 一様性の誤差は 0.0009 で、残る割合は 0.301、4×4 のばらつきは 0.115 でした。
- IGN: 一様性の誤差は 0.0003 で、残る割合は 0.300、4×4 のばらつきは 0.051 でした。

独立なランダムなら 4×4 の 16 画素に残る個数は二項分布で、割合のばらつきは `sqrt(0.3 × 0.7 / 16) ≒ 0.115` です。サイン関数と PCG はこの値と一致しました。IGN はランダムの半分以下（0.051）で、近くの画素で偏りが出にくいことが分かります。近くの画素の平均（PCF の 4×4 や TAA のぼかし）で、きれいに薄まります。IGN は手軽さと質の両面で、よい選択です。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="アルファ 0.3 のとき、4×4 の画素のまとまりで残る割合のばらつき。IGN はランダムの半分以下"><text x="14" y="22" class="fig-title">4×4 の画素での「残る割合」のばらつき（小さいほど良い）</text>
<line x1="60" y1="190" x2="680" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="110" y="50" width="100" height="140" fill="rgba(229,72,77,0.25)" stroke="#e5484d"/><rect x="270" y="51" width="100" height="139" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="430" y="115" width="100" height="75" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="160" y="44">0.114</text><text x="320" y="45">0.115</text><text x="480" y="109">0.051</text>
<text x="160" y="210">サイン関数</text><text x="320" y="210">PCG</text><text x="480" y="210">IGN</text>
<text x="610" y="90" style="fill:#64748b">独立ランダムなら</text><text x="610" y="108" style="fill:#64748b">理論値 0.115</text></g>
<line x1="560" y1="50" x2="680" y2="50" stroke="#94a3b8" stroke-dasharray="5 4"/>
<text x="360" y="232" text-anchor="middle" style="font-size:12px">サイン関数と PCG は理論値と一致。IGN は半分以下で、近くの画素に偏りが出にくい</text></svg>

## ノイズが TAA でどこまで減るか {#taa}

TAA は過去のフレームを指数移動平均で足します。ブレンドの重みを `α`（0.1 など）、アルファを `a`、しきい値のノイズがフレームごとに独立だとすると、平均後の画素の値のばらつき（標準偏差）は、次の式になります。

<div class="formula">σ = sqrt( a (1 − a) · α / (2 − α) )</div>

`a = 0.3`、`α = 0.1` なら `sqrt(0.21 × 0.1 / 1.9) ≒ 0.105` です。シミュレーションでは 0.106 でした。1 フレームだけのばらつき（`sqrt(0.21) ≒ 0.458`）が、約 4 分の 1 になります。`α = 0.1` の指数移動平均は有効なフレーム数が約 19 です（`(2 − α) / α`）。単純に N フレームを平均するなら標準偏差は `sqrt(a(1 − a) / N)` で、N = 4 で 0.229、8 で 0.162、16 で 0.115 です。

したがって TAA を使っていても、ばらつきはゼロにはなりません。残るノイズを IGN の局所的な偏りの小ささで、さらに減らせます。物が動くと TAA の履歴が捨てられて、ノイズが戻ります。

## オブジェクト空間のハッシュ {#object}

画面座標からハッシュを作ると、カメラが動いてもパターンが画面に固定されて、ノイズが画面に貼りついたように見えます（スクリーン ドア効果）。TAA がフレームごとにパターンをずらして平均するならこれで問題ありません。TAA がなくてパターンを物に貼りつかせたいなら物の表面の位置（オブジェクト空間）からハッシュを作ります。物と一緒にパターンが動くので、安定します。

オブジェクト空間のハッシュにはスケールの問題があります。近づくとノイズの粒が大きく遠ざかると画素より小さくなります。画面上で一定の粒の大きさに保つには画面上の 1 画素に対応するオブジェクト空間の大きさで、ハッシュする座標を丸めます。Wyman と McGuire の方法は、画面の微分（`ddx`、`ddy`）から画素の大きさを求めます。

```hlsl
// 論文の考え方: 1 画素の大きさに合わせて、ハッシュ用の座標を丸める。
// 式は一般に知られた形を書いたもので、論文の原文では確かめていない
float HashedAlphaThreshold(float3 object_pos, float hash_scale) {
  float max_deriv = max(length(ddx(object_pos)), length(ddy(object_pos)));
  float pix_scale = 1.0 / max(hash_scale * max_deriv, 1e-6);          // 画素の大きさに比例（0 割りの防止は足した）
  // 2 の累乗に丸めた 2 つのスケールの間を補間する（距離が変わっても、粒の大きさが一定に近い）
  float2 pix_scales = float2(exp2(floor(log2(pix_scale))), exp2(ceil(log2(pix_scale))));
  float2 alpha_xy = float2(HashSin(floor(pix_scales.x * object_pos.xy)),
                           HashSin(floor(pix_scales.y * object_pos.xy)));
  float lerp_factor = frac(log2(pix_scale));
  float x = lerp(alpha_xy.x, alpha_xy.y, lerp_factor);
  // 補間で偏った分布を、一様に戻す補正
  float a = min(lerp_factor, 1.0 - lerp_factor);
  float3 cases = float3(x * x / (2.0 * max(a * (1.0 - a), 1e-6)),
                        (x - 0.5 * a) / (1.0 - a),
                        1.0 - ((1.0 - x) * (1.0 - x) / (2.0 * max(a * (1.0 - a), 1e-6))));
  float threshold = (x < (1.0 - a)) ? ((x < a) ? cases.x : cases.y) : cases.z;
  return clamp(threshold, 1e-6, 1.0);
}
```

ポイントはスケールを 2 の累乗に丸めて、2 つを補間することです。距離が変わっても粒の大きさが画面上でほぼ一定になります。

実用上は画面座標から作る簡単な方法（IGN など）と TAA で十分なことが多いです。

## シェーダーでの使い方 {#usage}

```hlsl
struct PsInput {
  float4 position : SV_Position;
  float2 uv : TEXCOORD0;
  float3 object_pos : TEXCOORD1;
};

// 画面座標 + フレームごとのずらしで、しきい値を作る（TAA 向け）
float ScreenThreshold(float2 pixel) {
  // フレームごとに、パターンを少しずらす。IGN の入力を動かす
  float2 shifted = pixel + float2(g_frame_index % 8u, (g_frame_index / 8u) % 8u) * 5.588238;
  return InterleavedGradientNoise(shifted);
}

void HashedAlphaPS(PsInput i) {
  float alpha = g_albedo.Sample(g_linear_wrap, i.uv).a;
  clip(alpha - ScreenThreshold(i.position.xy));
}
```

`clip` を使うので深度に書き込んで、色の計算も残った画素だけで行われます。組み合わせは次のとおりです。

- TAA と一緒に使うとノイズが平均されて、半透明のように見えます。
- MSAA とは Alpha to Coverage と併用して、縁をさらになめらかにできます。ただし重くなります。
- 影のパスでも同じハッシュで描くと影も確率的に薄くなります（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)）。
- TAA がなければノイズが目立ちます。静止画でざらつきます。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で `HashedAlphaPS` とそこから呼ぶ関数をコンパイルして、エラーが出ないことを確かめました。ハッシュの一様性と 4×4 のばらつき TAA の標準偏差は、Python で 512 × 512 画素と 10 万画素のシミュレーションで測った値です。GPU での描画は確認していません。論文の補正式は原文では確かめていません。

## 使い分け {#choice}

- アルファ テストは縁がジャギーで、半透明がなくノイズもありません。何も必要としません。
- A2C は縁がなめらかで、半透明は段階的です。ノイズがなく MSAA が必要です。
- ディザは粒状で確率の半透明があります。ノイズがあります。TAA があるとよいです。
- ハッシュド アルファは TAA があれば縁がなめらかで、確率の半透明があります。ノイズがあります。TAA が必要です。

TAA がすでにあるゲームではハッシュド アルファが最も手軽で、品質が良い選択です。

## よくあるミス {#mistakes}

??? failure "ハッシュド アルファのノイズが消えない"
    原因は TAA が効いていないかパターンがフレームごとに変わっていないことです。TAA を有効にしてハッシュの入力にフレーム番号などを混ぜて、フレームごとにパターンをずらします。パターンが毎フレーム同じだと平均してもノイズが減りません。

??? failure "同じ画素が、いつも同じ判定で葉がまだらに欠ける"
    原因はハッシュが画面に固定されていることです。パターンを物に貼りつかせたいならオブジェクト空間のハッシュを使います。TAA でぼかしたいならフレームごとにパターンを動かします。

??? failure "動くものだけノイズが強い"
    原因は TAA が動く物の履歴を捨てて、1 フレームのノイズがそのまま出ることです。動く物にはノイズが少ない IGN を使うか動く物は通常のアルファ テストに戻します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] ランダムなしきい値で `clip` すると、アルファが「残る確率」になります。
    - [x] TAA で平均すると、なめらかな半透明になります。ばらつきは `α = 0.1` で約 4 分の 1 になります。
    - [x] IGN は近くの画素で偏りが出にくく、手軽です。
    - [x] フレームごとにパターンをずらさないと TAA で平均してもノイズが減りません。

## 参考 {#references}

このページは次の資料を読まずに書きました。ハッシュの数字と TAA の式は Python で自分で測って、確かめています。

- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（Interleaved Gradient Noise）
- Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正してカバレッジを保つ）
- Georgiev, Fajardo, "Blue-Noise Dithered Sampling", SIGGRAPH 2016 Talks

## 関連ページ

- [Alpha Testing](index.md)
- [TAA](../../postprocess/antialiasing/taa.md)
- [Dithered Transparency](dither.md)
