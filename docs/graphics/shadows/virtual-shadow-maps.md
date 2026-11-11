---
title: Virtual Shadow Maps
tags:
  - 描画
---

# Virtual Shadow Maps

[Cascaded Shadow Maps (CSM)](cascaded.md) は、カスケードの数と解像度が固定です。近くを細かくしようとすると解像度（メモリ、描画）が膨らみます。しかもカスケードの境目で影の細かさが急に変わります。

<strong>仮想シャドウ マップ（Virtual Shadow Maps。[分散 VSM](vsm/index.md) とは別物）は途方もなく大きな解像度（例: 16K × 16K）の「仮想的な」シャドウ マップを考えて、画面に実際に必要な部分（ページ）だけを物理メモリに割り当てて描く方式です</strong>。テクスチャのバーチャル テクスチャリングと同じ発想で、画面の各画素にほぼ 1 テクセルが対応する精度の影を現実的なメモリで実現します。Unreal Engine 5 の標準的な影の方式です。このページでは構造、手順、必要なページ数の見積もり（シミュレーションつき）、キャッシュ、利点と注意を説明します。

!!! tip "ポイント"
    - 巨大な仮想解像度のシャドウ マップをページ（例 128 × 128）に分割して、必要なページだけを物理メモリに置きます。
    - どのページが必要かは画面の各画素から、ワールド位置、ライト空間、ページと逆引きして決めます。
    - 画素ごとに適切なミップ（解像度）が選ばれて、画面での影の細かさがほぼ一定になります（カスケードの境目なし）。
    - 平らな地面を見るだけなら実測の見積もりで、仮想 16K² の 1 GiB に対して、数 MiB のページで足ります。
    - 静的な物のページは保持して、動いた物があるページだけ再描画します（キャッシュ）。
    - 実装は複雑です。ページ管理、間接テーブル、間接描画が必要です。

!!! info "このページを読む前に"
    - [Shadows](index.md)（このセクション全体の地図と読む順番）

## 発想: 必要な所だけ細かく {#idea}

画面に映る影に本当に必要な解像度は画素ごとに決まります。近い画素は細かいシャドウ マップ、遠い画素は粗いもので足ります。カスケードはこれを階段状（3〜4 段）で近似します。仮想シャドウ マップは画素ごとに連続的に（ミップごとに）選びます。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="仮想シャドウ マップのページ">
<text x="20" y="24" class="fig-title">巨大な仮想テクスチャをページに分割し、画面に必要なページだけ実体化する</text>
<rect x="40" y="50" width="320" height="200" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/><text x="40" y="44" style="font-size:12px">仮想シャドウ マップ（巨大）</text>
<g stroke="currentColor" opacity="0.35"><line x1="120" y1="50" x2="120" y2="250"/><line x1="200" y1="50" x2="200" y2="250"/><line x1="280" y1="50" x2="280" y2="250"/><line x1="40" y1="100" x2="360" y2="100"/><line x1="40" y1="150" x2="360" y2="150"/><line x1="40" y1="200" x2="360" y2="200"/></g>
<rect x="120" y="100" width="80" height="50" fill="rgba(46,160,67,0.45)"/><rect x="200" y="100" width="80" height="50" fill="rgba(46,160,67,0.45)"/><rect x="200" y="150" width="80" height="50" fill="rgba(46,160,67,0.45)"/><rect x="280" y="150" width="80" height="50" fill="rgba(46,160,67,0.45)"/>
<text x="64" y="232" style="font-size:12px">（不要なページは未割り当て）</text>
<line x1="380" y1="150" x2="440" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#a)"/>
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="currentColor"/></marker></defs>
<rect x="450" y="90" width="260" height="120" fill="none" stroke="currentColor" stroke-width="2"/><text x="450" y="84" style="font-size:12px">物理メモリ（ページ プール）</text>
<rect x="460" y="100" width="50" height="40" fill="rgba(46,160,67,0.45)"/><rect x="515" y="100" width="50" height="40" fill="rgba(46,160,67,0.45)"/><rect x="570" y="100" width="50" height="40" fill="rgba(46,160,67,0.45)"/><rect x="625" y="100" width="50" height="40" fill="rgba(46,160,67,0.45)"/>
<text x="460" y="236" style="font-size:12px">必要なページだけ実体化（間接テーブルで対応付け）</text>
</svg>

カスケードとの違いは次のとおりです。

- 解像度の選び方はカスケードが 3〜4 段で、仮想シャドウ マップは画素ごとに連続的です。
- 境目はカスケードがブレンドが必要で、仮想シャドウ マップはミップで連続なので、ありません。
- メモリはカスケードが各カスケードの全面で、仮想シャドウ マップは必要なページだけです。
- 近景の細かさはカスケードが解像度に上限があり仮想シャドウ マップは画素に 1 テクセル相当まで可能です。
- 実装はカスケードが比較的簡単で、仮想シャドウ マップは複雑です。

<!-- fig:vsm-pages:begin -->

<svg class="fig illust motion" data-fig="vsm-pages" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vsm-pages" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">仮想シャドウ マップ: 巨大な影の表を画面に見える所だけ、ページ単位で作る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">16×16 ページの仮想的な表(各ページ 128×128 マス)。カメラが動くと、見える所のページだけを確保・描画する</text>
<rect x="30" y="96" width="436.0" height="436.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">仮想的な表(青 = 確保済み、赤 = 今フレームで描いた)</text>
<rect x="40.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="170.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="196.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="222.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="274.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6200;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6222;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6244;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="378.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6289;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="404.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6311;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="430.0" y="110.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="170.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="196.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="222.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6200;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6222;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6244;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6289;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="378.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6311;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="404.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6333;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="430.0" y="136.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6356;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="40.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="170.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="196.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="222.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6222;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6244;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6289;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6311;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="378.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6333;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="404.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6356;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="430.0" y="162.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6378;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="40.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="170.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="196.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="222.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6244;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6289;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6311;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6333;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="378.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6356;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="404.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6378;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="430.0" y="188.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="40.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="170.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="196.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="222.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3578;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600;0.4400;0.6267;0.7067" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="274.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622;0.4400;0.6289;0.7067" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="300.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6311;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6333;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6356;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="378.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6378;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="404.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="430.0" y="214.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6422;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="40.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="170.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="196.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3578;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="222.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3644;0.4400;0.6311;0.7067" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="300.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3667;0.4400;0.6333;0.7067" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="326.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6356;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6378;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="378.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="404.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6422;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="430.0" y="240.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="170.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3578;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="196.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="222.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3644;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3667;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689;0.4400;0.6356;0.7067" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="326.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711;0.4400;0.6378;0.7067" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="352.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="378.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6422;0.7067" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="404.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="266.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911;0.1733;0.3578;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="170.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="196.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="222.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3644;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3667;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="292.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="66.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933;0.1733;0.3600;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="170.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956;0.1733;0.3622;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="196.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3644;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="222.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3667;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="318.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="66.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956;0.1733;0.3622;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="170.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978;0.1733;0.3644;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="196.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.1733;0.3667;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="222.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="352.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="344.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="66.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="170.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.1733;0.3667;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="196.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022;0.1733;0.3689;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="222.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="326.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="352.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="370.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="66.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="170.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="196.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044;0.1733;0.3711;0.4400" values="#f1f5f9;#fca5a5;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="222.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="248.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="274.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778;0.4400" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="300.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="326.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="352.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="396.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="66.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="170.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="196.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="222.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="274.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="300.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="326.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="352.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="422.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="66.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="170.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="196.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="222.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="274.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="300.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="326.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="352.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="448.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="92.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="118.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="144.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067;0.1733" values="#f1f5f9;#fca5a5;#93c5fd"/></rect>
<rect x="170.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="196.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="222.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="274.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="300.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="326.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="352.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="474.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="40.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="66.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="92.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="118.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="144.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="170.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="196.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="222.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="248.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="274.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="300.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="326.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="352.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="378.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="404.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<rect x="430.0" y="500.0" width="26.3" height="26.3" fill="#f1f5f9"/>
<g opacity="0.6"><line x1="66.0" y1="110.0" x2="66.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="92.0" y1="110.0" x2="92.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="118.0" y1="110.0" x2="118.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="144.0" y1="110.0" x2="144.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="170.0" y1="110.0" x2="170.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="196.0" y1="110.0" x2="196.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="222.0" y1="110.0" x2="222.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="248.0" y1="110.0" x2="248.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="274.0" y1="110.0" x2="274.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="300.0" y1="110.0" x2="300.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="326.0" y1="110.0" x2="326.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="352.0" y1="110.0" x2="352.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="378.0" y1="110.0" x2="378.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="404.0" y1="110.0" x2="404.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="430.0" y1="110.0" x2="430.0" y2="526.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="136.0" x2="456.0" y2="136.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="162.0" x2="456.0" y2="162.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="188.0" x2="456.0" y2="188.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="214.0" x2="456.0" y2="214.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="240.0" x2="456.0" y2="240.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="266.0" x2="456.0" y2="266.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="292.0" x2="456.0" y2="292.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="318.0" x2="456.0" y2="318.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="344.0" x2="456.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="370.0" x2="456.0" y2="370.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="396.0" x2="456.0" y2="396.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="422.0" x2="456.0" y2="422.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="448.0" x2="456.0" y2="448.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="474.0" x2="456.0" y2="474.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="40.0" y1="500.0" x2="456.0" y2="500.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="40.0" y="110.0" width="416.0" height="416.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<circle cx="118.0" cy="396.0" r="9" fill="#1f2937"><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2889;0.3289;0.5556;0.5956;1.0000" values="118;118;248;248;352;352"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2889;0.3289;0.5556;0.5956;1.0000" values="396;396;318;318;188;188"/></circle>
<rect x="520" y="96" width="410" height="230" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="520" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">かかった作業</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><text x="536" y="134" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">フレーム 1: 見えるページ 48 個</text>
<text x="536" y="156" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">新しく描いたページ 48 個(キャッシュ 0 個)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/><text x="536" y="194" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">フレーム 2: 見えるページ 52 個</text>
<text x="536" y="216" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">新しく描いたページ 43 個(キャッシュ 9 個)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/><text x="536" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">フレーム 3: 見えるページ 48 個</text>
<text x="536" y="276" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">新しく描いたページ 42 個(キャッシュ 6 個)</text>
</g>
<text x="40" y="470" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">描いたページ:</text>
<text x="170" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="170" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">48<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.3465;0.3467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="170" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">91<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3465;0.3467;0.6132;0.6133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="170" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">133<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6132;0.6133;1.0000" values="0;0;1;1"/></text>
<text x="210" y="474" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b">/ 全 256 ページ</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8443;0.8444;1.0000" values="0;0;1;1"/><rect x="520" y="344" width="410" height="130" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="536" y="368" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">全部を確保すると 16 MB(2048×2048 マスの表)</text>
<text x="536" y="391" text-anchor="start" style="font-size:15px;font-weight:700;fill:#166534">見えるページだけなら 3 MB</text>
<text x="536" y="415" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">動いても、新しく見えるページだけを描く(キャッシュ)</text>
<text x="536" y="437" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ライトが動かなければ、前のページをそのまま使う</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">巨大な表を全部持つのは無理。見える所だけ持つ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが動くと、新しく見える所だけを描き足す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8665;0.8667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">描くページが少ないので、高解像度の影が安く作れる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:vsm-pages:end -->

## 構造 {#structure}

仮想シャドウ マップはミップ マップの階層を持ちます。レベル 0 が最も細かく上のレベルほど粗くなります。各レベルを固定サイズの「ページ」に分割します。

- 仮想解像度は例えば 16384 × 16384（レベル 0）です。
- ページ サイズは例えば 128 × 128 テクセルです。
- ミップ階層は解像度を半分にしながら、1 ページまで続きます。
- 物理ページ プールは実際に確保したシャドウ マップの実体です（大きな 1 枚のテクスチャで、ページの寄せ集め）。
- ページ テーブル（間接テーブル）は、仮想ページから物理ページへの対応表です（GPU バッファ）。

数字を確かめます。レベル 0 は `16384 / 128 = 128` ページ四方で、16384 ページです。深度が 32 ビットなら 1 ページは `128 × 128 × 4 B = 64 KiB` です。全体を実体化すると `16384² × 4 B = 1 GiB` です。ページ テーブルは全ミップで `1 + 4 + 16 + … + 16384 ≒ 21845` 個（`(4⁸ − 1) / 3`）で、1 個 4 バイトなら約 85 KiB です。

ライトごとに仮想シャドウ マップを持ちます。平行光はクリップマップ（視点の周りにミップごとに粒度の違う範囲を置く）、ローカル ライトはキューブ（6 面）などです。

## 手順 {#steps}

### 必要なページの判定

毎フレーム、画面の各画素の深度からワールド位置を復元して、ライト空間の位置に変換します。その画素の影に必要な解像度（ミップ レベル）を画面での 1 画素の大きさから決めて、そのミップのそのページを「必要」とマークします。

```hlsl
Texture2D<float> g_depth : register(t0);              // 視点深度（メートル）
RWStructuredBuffer<uint> g_page_flags : register(u0); // 必要なページのフラグ（仮想ページごとに 1 要素）

cbuffer PageConstants : register(b0) {
  float4x4 g_inv_view_proj;
  float4x4 g_world_to_light;     // ワールド → ライト空間（正射影。xy が -1..1 に収まる範囲）
  float3 g_camera_position;
  float g_pixel_angle;           // 1 画素の視野角（ラジアン）。2 tan(fov/2) / 高さ
  float g_light_extent;          // 仮想シャドウ マップが覆う 1 辺（メートル）。例: 327.68
  float g_mip0_texel;            // レベル 0 の 1 テクセルの大きさ（メートル）。例: 0.02
  uint g_page_texels;            // 1 ページの 1 辺（テクセル）。128
  uint g_mip_count;              // 例: 8
  uint2 g_screen_size;
  float2 _pad;
};

// 仮想ページの通し番号。レベル m の位置 (x, y) → 配列の添字。レベルごとに 4^(7−m) 個
uint VirtualPageIndex(uint mip, uint2 page, uint pages_at_mip0) {
  uint offset = 0;
  for (uint m = 0; m < mip; ++m) offset += (pages_at_mip0 >> m) * (pages_at_mip0 >> m);
  uint pages = pages_at_mip0 >> mip;
  return offset + page.y * pages + page.x;
}

[numthreads(8, 8, 1)]
void MarkPagesCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_screen_size)) return;
  float depth = g_depth.Load(int3(id.xy, 0));
  if (depth > 1e6) return;                                           // 空は影を受けない（足した処理）

  // ワールド位置の復元（簡略化: 視点深度とピクセルの向きから）
  float4 w = mul(float4((id.x + 0.5) / g_screen_size.x * 2.0 - 1.0, 1.0 - (id.y + 0.5) / g_screen_size.y * 2.0, 1.0, 1.0), g_inv_view_proj);
  float3 dir = normalize(w.xyz / w.w - g_camera_position);
  float3 world_pos = g_camera_position + dir * depth;

  // 画面の 1 画素がワールドで覆う大きさ（距離 × 視野角）。斜めの面での伸びは無視した簡略版
  float footprint = depth * g_pixel_angle;
  // テクセルの大きさが、footprint にほぼ等しくなるミップ
  uint mip = (uint)clamp(floor(log2(max(footprint, 1e-6) / g_mip0_texel)), 0.0, float(g_mip_count - 1));

  // ライト空間の位置 → そのミップのページ座標
  float2 light_uv = mul(float4(world_pos, 1.0), g_world_to_light).xy * 0.5 + 0.5;
  uint pages_at_mip0 = (uint)round(g_light_extent / (g_mip0_texel * g_page_texels));    // 128
  uint pages = pages_at_mip0 >> mip;
  uint2 page = min((uint2)(light_uv * pages), pages - 1);
  uint index = VirtualPageIndex(mip, page, pages_at_mip0);
  InterlockedOr(g_page_flags[index], 1u);                            // 必要なページを並列に安全に記録する
}
```

`footprint` は画面の 1 画素がワールドで覆う大きさで、距離と視野角から求めます。`mip` はシャドウ マップの 1 テクセルが、画面の 1 画素にほぼ等しくなる階層です。`InterlockedOr` で並列に安全に必要なページを記録します。

### ページの割り当てと描画

必要とマークされてまだ物理ページがないページに物理ページを割り当てます。使われなくなったページは解放します（LRU など）。割り当てられた（または無効になった）ページだけシャドウ マップを描きます。各ページの範囲に入る物体をカリングして描きます。

ページごとにページの範囲（ライト空間の箱）に入るクラスタや物体だけを描きます。ページと物体の判定を GPU で行って、間接描画します（[GPU Driven](../draw-call/gpu-driven.md)）。Nanite の小さな三角形はコンピュートでソフトウェア ラスタライズします。ハードウェアより効率が良いことがあります。

### 影の参照

ライティング時、画素のワールド位置からライト空間、ミップ、ページを求めてページ テーブルで物理ページを引いて、そこから深度をサンプルします。

```hlsl
Texture2D<float> g_physical_pool : register(t1);         // 物理ページ プール（ページの寄せ集め）
StructuredBuffer<uint> g_page_table : register(t2);      // 仮想ページ → 物理ページの番号（0xffffffff = 未割り当て）
SamplerComparisonState g_shadow_sampler : register(s0);

cbuffer LookupConstants : register(b1) {
  uint g_pool_pages_x;       // 物理プールの、横のページ数。例: 64
  float g_pool_inv_size;     // 1 / プールの幅（テクセル）
  uint2 _pad1;
};

float SampleVirtualShadow(float2 light_uv, float depth, uint mip, uint pages_at_mip0) {
  uint pages = pages_at_mip0 >> mip;
  float2 page_pos = light_uv * pages;
  uint2 page = min((uint2)page_pos, pages - 1);
  uint physical = g_page_table[VirtualPageIndex(mip, page, pages_at_mip0)];
  if (physical == 0xffffffffu) return 1.0;                           // 未割り当ては、影なしにする（粗いミップへのフォールバックが望ましい）

  float2 in_page = frac(page_pos);                                   // ページの中の位置 0..1
  uint2 slot = uint2(physical % g_pool_pages_x, physical / g_pool_pages_x);
  float2 physical_uv = (float2(slot) * g_page_texels + in_page * g_page_texels) * g_pool_inv_size;
  return g_physical_pool.SampleCmpLevelZero(g_shadow_sampler, physical_uv, depth);
}
```

ページの境界をまたぐ PCF は隣のページを引く必要があるので、境界の処理に注意します。境界に余分なテクセル（ボーダー）を持つ方法もあります。

## 必要なページ数を見積もる {#estimate}

平らな地面を立った視点（高さ 1.7 m）から見たとき何ページ必要かをシミュレーションで見積もりました（Python）。解像度 1920 × 1080、縦の画角 60°、地面のみを見る単純なシーンで、各画素について画面での 1 画素がワールドで覆う大きさからミップを選んで、そのページを数えました。レベル 0 の 1 テクセルを 2 cm（16384 テクセルで約 327 m）にしました。

必要だったページはレベル 0 が 34、レベル 1 が 18、レベル 2 が 16、レベル 3 が 8、レベル 4 が 8、レベル 5 が 10、レベル 6 が 4 で合計 98 ページでした。1 ページ 64 KiB なので、約 6.1 MiB です。仮想の全体（1 GiB）の約 0.6 % で、CSM の 4 カスケード × 2048² × 4 B（64 MiB）の約 10 分の 1 です。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="平らな地面を見たときに必要なページ数。ミップごと。仮想全体 1 GiB に対して約 6.1 MiB"><text x="14" y="22" class="fig-title">必要なページ（立った視点、平らな地面、実測の見積もり）</text>
<line x1="60" y1="190" x2="690" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"><rect x="90" y="50" width="60" height="140"/><rect x="170" y="116" width="60" height="74"/><rect x="250" y="124" width="60" height="66"/><rect x="330" y="157" width="60" height="33"/><rect x="410" y="157" width="60" height="33"/><rect x="490" y="149" width="60" height="41"/><rect x="570" y="173" width="60" height="17"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="120" y="44">34</text><text x="200" y="110">18</text><text x="280" y="118">16</text><text x="360" y="151">8</text><text x="440" y="151">8</text><text x="520" y="143">10</text><text x="600" y="167">4</text>
<text x="120" y="210">mip 0</text><text x="200" y="210">1</text><text x="280" y="210">2</text><text x="360" y="210">3</text><text x="440" y="210">4</text><text x="520" y="210">5</text><text x="600" y="210">6</text></g>
<text x="360" y="238" text-anchor="middle" style="font-size:12px">合計 98 ページ（約 6.1 MiB）。壁、木、動く物があると、実際はこれより増える</text></svg>

この見積もりは平らな地面だけの最も単純な場合です。壁、木、近くの物体、薄い影が重なる場面では必要なページが増えます。ページ プールの上限を決めて、足りなくなったときは粗いミップへフォールバックします。

!!! note "確かめた範囲"
    HLSL は `fxc` で、`MarkPagesCS`（`cs_5_0`）と `SampleVirtualShadow` を使うピクセル シェーダーをコンパイルして、エラーが出ないことを確かめました。ページ数は Python のシミュレーション（平らな地面のみ）です。仮想シャドウ マップ全体を GPU で動かしたものではありません。UE5 の実装は読んでいません。

## キャッシュ {#cache}

仮想シャドウ マップの大きな利点はキャッシュです。

- 静的な物だけのページは前フレームの内容を保持して、再描画しません。
- 動く物が入ったページはそのページだけ再描画します（または動的部分を重ねます）。
- ライトが動いたら全ページを無効化します。太陽がゆっくり動くときは段階的に更新します。
- カメラが動いたらクリップマップがスクロールして、新しく見える範囲のページだけを描きます。

静的な背景が多いシーンでは毎フレームの描画ページ数が少なくなります。

## 利点と注意 {#pros-cons}

利点は画素ごとにほぼ 1 テクセルの精度が得られること（カスケードの境目なし）、メモリが見えている範囲に限定されることキャッシュで静的な影が安いこと小さな物体の影や遠景の細部まで一貫した品質が出ること、Nanite などの GPU 駆動描画と相性が良いことです。

注意点は実装が複雑なこと（ページ管理、間接参照、間接描画）、ページ テーブルの参照コストが毎画素にかかることページ プールの上限を超えると粗いミップへフォールバックすること、動く物体が多いと無効化が増えることソフト シャドウは別途必要なこと（PCF とレイトレースで半影など）です。

### ソフト シャドウとの組み合わせ

細かいシャドウ マップはエッジが鋭いので、半影を作るために画素の周辺をシャドウ マップ上でレイ マーチして、遮蔽物までの距離から半影の幅を求める手法があります（UE5 の Shadow Map Ray Tracing）。PCSS の効率化版とも言える方式です。

## 他の方式との使い分け {#choice}

- 大規模、高品質、GPU 駆動、次世代機や PC では仮想シャドウ マップです。
- 一般的な PC や家庭用機の標準は、カスケード シャドウ マップです。
- モバイルは少数のカスケードと軽い PCF です。
- RT 対応のハイエンドはレイトレース影です。

## よくあるミス {#mistakes}

??? failure "必要なページの判定を毎フレーム全画素で行って重い"
    原因は判定のコストが画素数に比例することです。ダウンサンプルした深度やタイル単位の最小・最大で、判定を減らします。

??? failure "ページ プールが足りなくなって、影が欠ける"
    原因は必要なページが、プールの上限を超えたことです。粗いミップへのフォールバック、プールの上限、解放の方針を設計します。

??? failure "ライトが動くたびに全ページを描き直して重い"
    原因はライトの動きで、すべてのキャッシュが無効になることです。ライトの動きを離散化して段階的に更新します。

??? failure "ページ境界で、PCF が途切れて継ぎ目が見える"
    原因は境界の隣のページを参照していないことです。隣のページも参照するか境界にテクセルを余分に持ちます（ボーダー）。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 仮想シャドウ マップは、巨大な仮想解像度をページに分割して、必要なページだけを実体化します。
    - [x] 画面の各画素から、必要なミップとページを逆引きします。画素 ≒ 1 テクセルの精度です。
    - [x] ページ テーブル（間接）で、仮想から物理へ対応付けます。キャッシュで静的な影が安くなります。
    - [x] 平らな地面のみの見積もりでは、1 GiB の仮想に対して約 6.1 MiB でした。
    - [x] 実装が複雑で、ページ プールの管理が重要です。

## 参考 {#references}

このページは次の資料を読まずに書きました。ページ数は自分で書いたシミュレーションの値です。

- Fernando, Fernandez, Bala, Greenberg, "Adaptive Shadow Maps", SIGGRAPH 2001
- Lefohn, Sengupta, Owens, "Resolution-Matched Shadow Maps", ACM Transactions on Graphics, Vol. 26, No. 4, 2007
- Giegl, Wimmer, "Queried Virtual Shadow Maps", Symposium on Interactive 3D Graphics and Games 2007
- Epic Games, "Virtual Shadow Maps", Unreal Engine 5 ドキュメント

## 関連ページ

- [Shadows](index.md)
- [Cascaded Shadow Maps (CSM)](cascaded.md)
- [PCSS](pcss.md)
- [GPU Driven Rendering](../draw-call/gpu-driven.md)
