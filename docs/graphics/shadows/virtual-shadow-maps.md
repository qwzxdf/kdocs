---
title: Virtual Shadow Maps
tags:
  - 描画
---

# Virtual Shadow Maps

[Cascaded Shadow Maps (CSM)](cascaded.md)は、**カスケードの数と解像度が固定**なので、**近くを細かくしようとすると、解像度（メモリ・描画）が膨らみ**ます。**仮想シャドウ マップ**（Virtual Shadow Maps、VSM。[分散 VSM](vsm/index.md) とは別物）は、**途方もなく大きな解像度（例：16K×16K 以上）の「仮想的な」シャドウ マップ**を考え、**画面に実際に必要な部分（ページ）だけ**を**物理メモリに割り当てて描く**方式です。**テクスチャのバーチャル テクスチャリング**と同じ発想で、**画面の各画素にちょうど 1 テクセルが対応する**精度の影を、**現実的なメモリ**で実現します。Unreal Engine 5 の標準的な影の方式です。

!!! tip "ポイント"
    - <strong>巨大な仮想解像度</strong>のシャドウ マップを<strong>ページ（例 128×128）に分割</strong>し、<strong>必要なページだけ</strong>を物理メモリに置く。
    - <strong>どのページが必要か</strong>は、<strong>画面の各画素</strong>から<strong>ワールド位置 → ライト空間 → ページ</strong>と<strong>逆引き</strong>して決める。
    - <strong>画素ごとに適切なミップ（解像度）</strong>が選ばれ、<strong>画面での影の細かさがほぼ一定</strong>（カスケードの境目なし）。
    - <strong>キャッシュ</strong>：<strong>静的な物のページは、保持</strong>。<strong>動いた物があるページだけ再描画</strong>。
    - <strong>Nanite など</strong>の<strong>GPU 駆動のジオメトリ</strong>と相性が良い（<strong>ページごとにカリング・描画</strong>）。
    - <strong>実装が複雑</strong>。<strong>ページ管理・間接テーブル・間接描画</strong>が必要。

## 発想：必要な所だけ、細かく

**画面に映る影**に**本当に必要な解像度**は、**画素ごと**に決まります。**近い画素**は**細かい**シャドウ マップ、**遠い画素**は**粗い**ものでよいのです。**カスケード**はこれを<strong>階段状（3〜4 段）</strong>で近似しますが**仮想シャドウ マップ**は、**画素ごとに連続的に**（ミップごとに）選びます。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="仮想シャドウ マップのページ">
<text x="20" y="24" class="fig-title">巨大な仮想テクスチャを、ページに分割し、画面に必要なページだけ実体化する</text>
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

| 項目 | カスケード | 仮想シャドウ マップ |
| --- | --- | --- |
| **解像度の選び方** | 段階的（3〜4 段） | **画素ごとに連続的** |
| **境目** | ブレンドが必要 | **なし**（ミップで連続） |
| **メモリ** | 各カスケードの全面 | **必要なページのみ** |
| **近景の細かさ** | 解像度に上限 | **画素に 1 テクセル相当**まで可能 |
| **実装** | 比較的簡単 | **複雑** |

<!-- fig:vsm-pages:begin -->

<svg class="fig illust motion" data-fig="vsm-pages" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vsm-pages" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">仮想シャドウ マップ: 巨大な影の表を、画面に見える所だけ、ページ単位で作る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">16×16 ページの仮想的な表(各ページ 128×128 マス)。カメラが動くと、見える所のページだけを、確保・描画する</text>
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
<text x="536" y="437" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ライトが動かなければ、前のページを、そのまま使う</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">巨大な表を全部持つのは無理。見える所だけ持つ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが動くと、新しく見える所だけを描き足す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8665;0.8667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">描くページが少ないので、高解像度の影が、安く作れる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:vsm-pages:end -->

## 構造

### ページとミップ

**仮想シャドウ マップ**は、**ミップ マップ**の階層を持ちます。**レベル 0 が最も細かく**、**上のレベルほど粗く**なります。<strong>各レベルを固定サイズの「ページ」</strong>（例：128×128 テクセル）に**分割**します。

| 要素 | 内容 |
| --- | --- |
| **仮想解像度** | 例：16384×16384（レベル 0） |
| **ページ サイズ** | 例：128×128 テクセル |
| **ミップ階層** | 解像度を半分にしながら、1 ページまで |
| **物理ページ プール** | **実際に確保した、シャドウ マップの実体**（大きな 1 枚のテクスチャ。ページの寄せ集め） |
| <strong>ページ テーブル（間接テーブル）</strong> | **仮想ページ → 物理ページ**の対応表（GPU バッファ） |

### ライトごと

**ライトごとに仮想シャドウ マップ**を持ちます（**平行光**は**クリップマップ**（視点の周りに**ミップごとに粒度の違う範囲**を置く）、**ローカル ライト**は、<strong>キューブ（6 面）</strong>など）。

## 手順

### ① 必要なページの判定

**毎フレーム**、**画面の各画素**の**深度**から、**ワールド位置**を復元し、**ライト空間の位置**に変換します。<strong>その画素の影に必要な解像度（ミップ レベル）</strong>を、**画面での 1 画素の大きさ**から決め、**そのミップのそのページ**を<strong>「必要」とマーク</strong>します。

```hlsl
float3 world_pos = ReconstructWorldPosition(pixel, depth);
float3 light_ndc = ProjectToLightSpace(world_pos);
int mip = SelectMipForPixel(world_pos, pixel_footprint);
uint2 page = PageIndex(light_ndc.xy, mip);
MarkPageNeeded(mip, page);
```

コードの要点です。`pixel_footprint` は、画面の 1 画素がワールドで覆う大きさです（距離と視野角から求めます）。`SelectMipForPixel` は、シャドウ マップの 1 テクセルが画面の 1 画素にほぼ等しくなるミップを選びます。`MarkPageNeeded` は、フラグ バッファに InterlockedOr などで書き込み、並列に安全に必要なページを記録します。

### ② ページの割り当て

**必要とマークされ、まだ物理ページがない**ページに、**物理ページを割り当てます**。**使われなくなった**ページは、<strong>解放（再利用）</strong>します（**LRU など**）。

### ③ ページの描画

**割り当てられた（または無効になった）ページ**だけ、**シャドウ マップの描画**を行います。**各ページの範囲に入る物体**を、**カリングして**描きます。

ページの描画の工夫です。ページごとに、ページの範囲（ライト空間の箱）に入るクラスタや物体だけを描きます。ページ × オブジェクトの判定を GPU で行い、間接描画します（[GPU Driven](../../rendering/gpu-driven.md)）。Nanite の小さな三角形は、コンピュートでソフトウェア ラスタライズします。ハードウェアより効率が良いことがあります。

### ④ 影の参照

**ライティング時**、**画素のワールド位置**から、**ライト空間・ミップ・ページ**を求め、**ページ テーブルで物理ページ**を引き、**そこから深度をサンプル**します。

```hlsl
uint2 virtual_page = uint2(light_uv * pages_at_mip);
uint physical = page_table[VirtualPageIndex(mip, virtual_page)];
float2 physical_uv = PhysicalUV(physical, frac(light_uv * pages_at_mip));
float shadow = physical_pool.SampleCmpLevelZero(shadow_sampler, physical_uv, depth - bias);
```

**ページの境界**をまたぐ **PCF**は、**隣のページを引く必要**があるので、**境界の処理**に**注意**します。

## キャッシュ

**仮想シャドウ マップの大きな利点**は、**キャッシュ**です。

| 状況 | 動作 |
| --- | --- |
| **静的な物だけのページ** | **前フレームの内容を保持**（**再描画しない**） |
| **動く物が入ったページ** | **そのページだけ**、<strong>再描画（または動的部分を重ねる）</strong> |
| **ライトが動いた** | **全ページ無効化**（太陽がゆっくり動くときは、**段階的に更新**） |
| **カメラが動いた** | **クリップマップ**が**スクロール**し、**新しく見える範囲のページ**だけ描く |

**静的な背景が多い**シーンでは、**毎フレームの描画ページ数**が**非常に少なく**なります。

## 利点と注意

| 利点 | 注意 |
| --- | --- |
| **画素ごとにほぼ 1 テクセルの精度**（カスケードの境目なし） | **実装が複雑**（ページ管理・間接参照・間接描画） |
| **メモリが見えている範囲に限定される** | **ページ テーブルの参照コスト**（毎画素） |
| **キャッシュで静的な影が安い** | **ページ プールの上限**（超えると粗いミップへフォールバック） |
| **小さな物体の影・遠景の細部**まで**一貫した品質** | **動く物体が多い**と**無効化が増える** |
| **Nanite などの GPU 駆動描画**と**相性が良い** | **ソフト シャドウ**は、別途（**PCF ＋ レイトレースで半影**など） |

### ソフト シャドウとの組み合わせ

**非常に細かい**シャドウ マップは、**エッジが鋭い**ので**半影**を作るため、**画素の周辺をシャドウ マップ上でレイ マーチ**し、**遮蔽物までの距離から、半影の幅**を求める**手法**（UE5 の **Shadow Map Ray Tracing**）があります。**PCSS**の**効率化版**とも言える方式です。

## 他の方式との使い分け

| 状況 | 向いている方式 |
| --- | --- |
| **大規模・高品質・GPU 駆動・次世代機/PC** | **仮想シャドウ マップ** |
| **一般的な PC / 家庭用機の標準** | **カスケード シャドウ マップ** |
| **モバイル** | **少数のカスケード ＋ 軽い PCF** |
| **RT 対応のハイエンド** | **レイトレース影** |

## よくあるミス

??? failure "必要なページの判定を、毎フレーム全画素で行って重い"
    **ダウンサンプルした深度**・**タイル単位の最小/最大**で、**判定を減らし**ます。

??? failure "ページ プールが足りなくなり、影が欠ける"
    **粗いミップへのフォールバック**・**プールの上限・解放の方針**を設計します。

??? failure "ライトが動くたびに、全ページを描き直して、重い"
    **ライトの動きを離散化**・**段階的に更新**します。

??? failure "ページ境界で、PCF が途切れて、継ぎ目が見える"
    **境界の隣のページ**も参照するか、**境界にテクセルを余分に持つ**（ボーダー）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 仮想シャドウ マップ ＝ <strong>巨大な仮想解像度</strong>を<strong>ページ</strong>に分割し、<strong>必要なページだけ</strong>実体化
    - [x] <strong>画面の各画素</strong>から、<strong>必要なミップとページ</strong>を逆引き。<strong>画素 ≒ 1 テクセル</strong>の精度
    - [x] <strong>ページ テーブル</strong>（間接）で、<strong>仮想 → 物理</strong>を対応付け。<strong>キャッシュ</strong>で静的な影を安く
    - [x] <strong>カスケードの境目がなく</strong>、<strong>Nanite など GPU 駆動</strong>と相性が良い
    - [x] <strong>実装が複雑</strong>で、<strong>ページ プールの管理</strong>が重要

## 参考

- Epic Games, "Virtual Shadow Maps"（Unreal Engine ドキュメント）
- Karis et al., "A Deep Dive into Nanite Virtualized Geometry"（SIGGRAPH 2021、仮想シャドウ マップにも言及）
- Lefohn et al., "Resolution-Matched Shadow Maps"（ACM TOG 2007）

## 関連ページ

- [Shadows](index.md)
- [Cascaded Shadow Maps (CSM)](cascaded.md)
- [PCSS](pcss.md)
- [GPU Driven Rendering](../../rendering/gpu-driven.md)
