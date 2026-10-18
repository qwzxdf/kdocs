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

<svg class="fig illust motion" data-fig="vsm-pages" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vsm-pages" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">仮想シャドウ マップ:見えている所の「ページ」だけを、細かく用意する</text>
<rect x="40" y="76" width="29" height="29" fill="#f1f5f9"/>
<rect x="70" y="76" width="29" height="29" fill="#f1f5f9"/>
<rect x="100" y="76" width="29" height="29" fill="#f1f5f9"/>
<rect x="130" y="76" width="29" height="29" fill="#f1f5f9"/>
<rect x="160" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="220" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="250" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#bae6fd"/></rect>
<rect x="280" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#bae6fd"/></rect>
<rect x="310" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#bae6fd"/></rect>
<rect x="340" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#38bdf8"/></rect>
<rect x="370" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="400" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="430" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="460" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="490" y="76" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd"/></rect>
<rect x="40" y="106" width="29" height="29" fill="#f1f5f9"/>
<rect x="70" y="106" width="29" height="29" fill="#f1f5f9"/>
<rect x="100" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="160" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="220" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#bae6fd"/></rect>
<rect x="250" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#bae6fd"/></rect>
<rect x="280" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#bae6fd"/></rect>
<rect x="310" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="340" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="370" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#38bdf8"/></rect>
<rect x="400" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8"/></rect>
<rect x="430" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="460" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="490" y="106" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8"/></rect>
<rect x="40" y="136" width="29" height="29" fill="#f1f5f9"/>
<rect x="70" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="160" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="220" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="250" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="280" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="310" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8;#38bdf8"/></rect>
<rect x="340" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="370" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#1d4ed8"/></rect>
<rect x="400" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8"/></rect>
<rect x="430" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8"/></rect>
<rect x="460" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="490" y="136" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="40" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#f1f5f9;#f1f5f9;#f1f5f9"/></rect>
<rect x="70" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="160" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#f1f5f9"/></rect>
<rect x="220" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="250" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="280" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8;#38bdf8"/></rect>
<rect x="310" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8;#38bdf8"/></rect>
<rect x="340" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8;#1d4ed8"/></rect>
<rect x="370" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#1d4ed8"/></rect>
<rect x="400" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8"/></rect>
<rect x="430" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8"/></rect>
<rect x="460" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8"/></rect>
<rect x="490" y="166" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="40" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="70" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="160" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#f1f5f9"/></rect>
<rect x="220" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#1d4ed8;#38bdf8;#bae6fd"/></rect>
<rect x="250" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#1d4ed8;#bae6fd"/></rect>
<rect x="280" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#1d4ed8;#38bdf8"/></rect>
<rect x="310" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8;#38bdf8"/></rect>
<rect x="340" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8;#38bdf8"/></rect>
<rect x="370" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#1d4ed8;#1d4ed8"/></rect>
<rect x="400" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#1d4ed8"/></rect>
<rect x="430" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8"/></rect>
<rect x="460" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="490" y="196" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="40" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="70" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="160" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#38bdf8;#f1f5f9"/></rect>
<rect x="220" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#1d4ed8;#38bdf8;#bae6fd"/></rect>
<rect x="250" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#1d4ed8;#38bdf8;#bae6fd"/></rect>
<rect x="280" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#1d4ed8;#bae6fd"/></rect>
<rect x="310" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8;#38bdf8"/></rect>
<rect x="340" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#1d4ed8;#38bdf8"/></rect>
<rect x="370" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="400" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#1d4ed8"/></rect>
<rect x="430" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#38bdf8;#38bdf8"/></rect>
<rect x="460" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="490" y="226" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="40" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="70" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="160" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#bae6fd;#f1f5f9"/></rect>
<rect x="220" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#38bdf8;#f1f5f9"/></rect>
<rect x="250" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#1d4ed8;#38bdf8;#bae6fd"/></rect>
<rect x="280" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#1d4ed8;#38bdf8;#bae6fd"/></rect>
<rect x="310" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#1d4ed8;#bae6fd"/></rect>
<rect x="340" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#38bdf8;#38bdf8"/></rect>
<rect x="370" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="400" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="430" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="460" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="490" y="256" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#bae6fd"/></rect>
<rect x="40" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="70" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#f1f5f9;#f1f5f9"/></rect>
<rect x="160" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#bae6fd;#f1f5f9"/></rect>
<rect x="220" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#bae6fd;#f1f5f9"/></rect>
<rect x="250" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#38bdf8;#bae6fd"/></rect>
<rect x="280" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="310" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="340" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="370" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#38bdf8"/></rect>
<rect x="400" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#38bdf8"/></rect>
<rect x="430" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#38bdf8"/></rect>
<rect x="460" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#bae6fd"/></rect>
<rect x="490" y="286" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd"/></rect>
<rect x="40" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="70" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#f1f5f9;#f1f5f9"/></rect>
<rect x="160" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="190" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="220" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#1d4ed8;#bae6fd;#f1f5f9"/></rect>
<rect x="250" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="280" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="310" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#38bdf8;#bae6fd"/></rect>
<rect x="340" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#38bdf8;#bae6fd"/></rect>
<rect x="370" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#bae6fd"/></rect>
<rect x="400" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#bae6fd"/></rect>
<rect x="430" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#bae6fd"/></rect>
<rect x="460" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#bae6fd"/></rect>
<rect x="490" y="316" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd"/></rect>
<rect x="40" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#f1f5f9;#f1f5f9;#f1f5f9"/></rect>
<rect x="70" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="100" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="130" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#bae6fd;#f1f5f9;#f1f5f9"/></rect>
<rect x="160" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#1d4ed8;#38bdf8;#f1f5f9;#f1f5f9"/></rect>
<rect x="190" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="220" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="250" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#38bdf8;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="280" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#38bdf8;#bae6fd;#f1f5f9"/></rect>
<rect x="310" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#bae6fd;#bae6fd;#bae6fd;#f1f5f9"/></rect>
<rect x="340" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#bae6fd"/></rect>
<rect x="370" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#bae6fd;#bae6fd;#bae6fd"/></rect>
<rect x="400" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#bae6fd"/></rect>
<rect x="430" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd;#bae6fd"/></rect>
<rect x="460" y="346" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="#f1f5f9;#f1f5f9;#f1f5f9;#f1f5f9;#bae6fd"/></rect>
<rect x="490" y="346" width="29" height="29" fill="#f1f5f9"/>
<circle cx="145.0" cy="331.0" r="10" fill="#e5484d" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="145;145;235;325;415"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111;0.3037;0.4963;0.6889" values="331;331;271;211;181"/></circle>
<text x="538" y="110" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">凡例</text>
<rect x="538" y="124" width="22" height="18" fill="#1d4ed8"/>
<text x="568" y="138" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">カメラの近く:細かいページ</text>
<rect x="538" y="152" width="22" height="18" fill="#38bdf8"/>
<text x="568" y="166" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">中距離:中くらい</text>
<rect x="538" y="180" width="22" height="18" fill="#bae6fd"/>
<text x="568" y="194" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">遠く:粗い</text>
<rect x="538" y="208" width="22" height="18" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1"/>
<text x="568" y="222" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">不要（メモリを使わない）</text>
<text x="40" y="60" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">光から見た平面（上から）。赤い点 = カメラの位置（見えている場所）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="408" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カメラが動くと、必要なページが入れ替わる（使い終わったページは解放）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1108;0.1111;0.3034;0.3037;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="408" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カメラが動くと、必要なページが入れ替わる（使い終わったページは解放）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3034;0.3037;0.4960;0.4963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="408" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カメラが動くと、必要なページが入れ替わる（使い終わったページは解放）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.6886;0.6889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="408" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カメラが動くと、必要なページが入れ替わる（使い終わったページは解放）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6886;0.6889;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
- [GPU Driven（最適化）](../../rendering/gpu-driven.md)
