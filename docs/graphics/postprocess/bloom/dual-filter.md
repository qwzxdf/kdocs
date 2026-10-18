---
title: Dual Filter
tags:
  - 描画
---

# Dual Filter

<strong>Dual Filter（Kawase の Dual Filtering）</strong>は、**縮小とぼかしを同時に行い、拡大とぼかしも同時に行う**方式です。**ガウスぼかしを別パスで行う必要がなくなり**、**ブルームのコストを大きく下げられます**。**モバイルのように帯域が厳しい環境**でも**定番**です。このページでは、**考え方・ダウンサンプル用とアップサンプル用のカーネル・実装・実質のぼかしの広がり・ガウスとの比較・注意点**を説明します。

!!! tip "ポイント"
    - Dual Filter ＝ <strong>縮小のときに周りも平均し（ぼかし）、拡大のときも周りを足す（ぼかし）</strong>。<strong>ぼかしだけの専用パスが要らない</strong>。
    - <strong>ダウンサンプル</strong>は<strong>5 タップ</strong>（中心 + 4 つの斜め）、<strong>アップサンプル</strong>は<strong>8 タップ</strong>（辺と斜め）。
    - 各タップは<strong>バイリニア</strong>で読むので、<strong>実質より多くの画素</strong>が混ざる。
    - <strong>広さは段数に比例して指数的に増える</strong>。
    - <strong>ガウスよりやや四角い形</strong>になるが、<strong>多段にすると見分けにくい</strong>。
    - <strong>オフセット（広がり）</strong>を<strong>パラメータ</strong>にして、<strong>ぼかしの強さを調整</strong>できる。

## 考え方

**従来**は、「縮小」と「ぼかし」を**別々のパス**で行いました。**Dual Filter は、縮小するときの「サンプルの取り方」自体をぼかしの形に**します。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="Dual Filter のカーネル">
<text x="20" y="26" class="fig-title">Dual Filter のカーネル（ダウン：5 タップ、アップ：8 タップ）</text>
<g transform="translate(60,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">ダウンサンプル（5 タップ）</text>
<rect x="0" y="0" width="200" height="150" fill="none" stroke="#94a3b8"/>
<g stroke="#e2e8f0"><line x1="50" y1="0" x2="50" y2="150"/><line x1="100" y1="0" x2="100" y2="150"/><line x1="150" y1="0" x2="150" y2="150"/><line x1="0" y1="37" x2="200" y2="37"/><line x1="0" y1="75" x2="200" y2="75"/><line x1="0" y1="112" x2="200" y2="112"/></g>
<circle cx="100" cy="75" r="9" fill="#2563eb"/><text x="116" y="70" style="font-size:12px">×4</text>
<circle cx="50" cy="37" r="7" fill="#e5484d"/><circle cx="150" cy="37" r="7" fill="#e5484d"/><circle cx="50" cy="112" r="7" fill="#e5484d"/><circle cx="150" cy="112" r="7" fill="#e5484d"/>
<text x="0" y="176" style="font-size:12px">中心 ×4 + 斜め 4 点 ×1（合計 ÷8）</text>
</g>
<g transform="translate(420,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">アップサンプル（8 タップ）</text>
<rect x="0" y="0" width="200" height="150" fill="none" stroke="#94a3b8"/>
<g stroke="#e2e8f0"><line x1="50" y1="0" x2="50" y2="150"/><line x1="100" y1="0" x2="100" y2="150"/><line x1="150" y1="0" x2="150" y2="150"/><line x1="0" y1="37" x2="200" y2="37"/><line x1="0" y1="75" x2="200" y2="75"/><line x1="0" y1="112" x2="200" y2="112"/></g>
<circle cx="100" cy="20" r="7" fill="#2563eb"/><circle cx="100" cy="130" r="7" fill="#2563eb"/><circle cx="25" cy="75" r="7" fill="#2563eb"/><circle cx="175" cy="75" r="7" fill="#2563eb"/>
<circle cx="63" cy="37" r="7" fill="#e5484d"/><circle cx="137" cy="37" r="7" fill="#e5484d"/><circle cx="63" cy="112" r="7" fill="#e5484d"/><circle cx="137" cy="112" r="7" fill="#e5484d"/>
<text x="0" y="176" style="font-size:12px">辺の 4 点 ×1、斜め 4 点 ×2（合計 ÷12）</text>
</g>
</svg>

## ダウンサンプル（5 タップ）

<strong>中心（重み 4）と、斜めの 4 点（重み 1）</strong>を**バイリニアで読み、合計を 8 で割ります**。

```hlsl
float3 DualDown(Texture2D src, SamplerState linear_clamp, float2 uv, float2 half_pixel, float offset) {
  float3 sum = src.SampleLevel(linear_clamp, uv, 0).rgb * 4.0;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2(-1, -1) * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2( 1, -1) * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2(-1,  1) * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2( 1,  1) * offset, 0).rgb;
  return sum / 8.0;
}
```

コードの要点です。`half_pixel` は、ソース（縮小前）の 1 画素の半分の UV 幅（`0.5 / ソース幅`）です。`offset` は広がりのパラメータで、1.0 が標準、大きくすると広くぼけます。中心は 4 倍の重みで、出力 1 画素に対応する 2×2 の中央です。

## アップサンプル（8 タップ）

<strong>辺の 4 点（重み 1）と、斜めの 4 点（重み 2）</strong>を**バイリニアで読み、合計を 12 で割ります**。

```hlsl
float3 DualUp(Texture2D src, SamplerState linear_clamp, float2 uv, float2 half_pixel, float offset) {
  float3 sum = 0;
  sum += src.SampleLevel(linear_clamp, uv + float2(-1, 0) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(-1, 1) * half_pixel * offset, 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + float2(0, 1) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(1, 1) * half_pixel * offset, 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + float2(1, 0) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(1, -1) * half_pixel * offset, 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + float2(0, -1) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(-1, -1) * half_pixel * offset, 0).rgb * 2.0;
  return sum / 12.0;
}
```

**拡大側の `half_pixel`** は、**ソース（小さい画像）の半画素**です。

## 全体の手順

Dual Filter の手順は 3 段階です。ダウンは N 段繰り返し、各段で 5 タップで半分に縮小し、各段の結果を保存します。アップは最小の段から N 段繰り返し、8 タップで拡大して、1 つ上の段に加算ブレンドで足します。最後に、最上段の結果に強さを掛けて、元の絵に足します（[Compositing and Intensity](composite.md)）。

この方法は、Marius Bjørge（ARM）の SIGGRAPH 2015 の発表 "Bandwidth-Efficient Rendering" で紹介されました。モバイル GPU はメモリ帯域が貴重なので、縮小とぼかしを 1 回のパスで済ませる Dual Filter が考案されました。

<strong>全部で各段 1 パス × 2（ダウン・アップ）</strong>。**ガウスのように横・縦の 2 パスを各段で行う必要がありません**。

<!-- fig:dual-filter-passes:begin -->

<svg class="fig illust motion" data-fig="dual-filter-passes" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dual-filter-passes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">デュアル フィルター: 縮小は「中心 + 四隅」、拡大は「8 方向」のタップ。少ない読み込みで、ガウスに近いぼかし</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素の光源。縮小(1/2)× 3 段、拡大 × 3 段を、実際に計算して、ガウスと比べる</text>
<text x="60" y="106" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">縮小 1(48 → 24)</text>
<rect x="60.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="90.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="120.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="150.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="180.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="210.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="240.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="270.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="300.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="330.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="360.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="390.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#fff4b8"/></rect>
<rect x="420.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#fff4b8"/></rect>
<rect x="450.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#fff4b8"/></rect>
<rect x="480.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="510.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="540.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="570.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="600.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="630.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="660.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="690.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="720.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="750.0" y="110.0" width="30.3" height="17.3" fill="#0f172a"/>
<rect x="60" y="110" width="720.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="170" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">縮小 2(24 → 12)</text>
<rect x="60.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="120.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="180.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="240.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="300.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="360.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#0f172a;#fff4b8"/></rect>
<rect x="420.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2614" values="#0f172a;#fff4b8"/></rect>
<rect x="480.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2670" values="#0f172a;#c4bd95"/></rect>
<rect x="540.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="600.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="660.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="720.0" y="174.0" width="60.3" height="17.3" fill="#0f172a"/>
<rect x="60" y="174" width="720.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="234" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">縮小 3(12 → 6)</text>
<rect x="60.0" y="238.0" width="120.3" height="17.3" fill="#0f172a"/>
<rect x="180.0" y="238.0" width="120.3" height="17.3" fill="#0f172a"/>
<rect x="300.0" y="238.0" width="120.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4084" values="#0f172a;#fff4b8"/></rect>
<rect x="420.0" y="238.0" width="120.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#0f172a;#fff4b8"/></rect>
<rect x="540.0" y="238.0" width="120.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4307" values="#0f172a;#414547"/></rect>
<rect x="660.0" y="238.0" width="120.3" height="17.3" fill="#0f172a"/>
<rect x="60" y="238" width="720.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="298" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">拡大して足す(6 → 12 → 24 → 48)</text>
<rect x="60.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="75.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="90.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="105.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="120.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="135.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="150.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="165.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="180.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="195.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5567" values="#0f172a;#141c2d"/></rect>
<rect x="210.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5581" values="#0f172a;#1e2533"/></rect>
<rect x="225.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5595" values="#0f172a;#2b313b"/></rect>
<rect x="240.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5609" values="#0f172a;#3c4145"/></rect>
<rect x="255.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5623" values="#0f172a;#4f5250"/></rect>
<rect x="270.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5637" values="#0f172a;#63645c"/></rect>
<rect x="285.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5651" values="#0f172a;#777768"/></rect>
<rect x="300.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5665" values="#0f172a;#8b8a74"/></rect>
<rect x="315.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5679" values="#0f172a;#a8a484"/></rect>
<rect x="330.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5693" values="#0f172a;#c6c097"/></rect>
<rect x="345.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5707" values="#0f172a;#e4dba8"/></rect>
<rect x="360.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5721" values="#0f172a;#fef3b7"/></rect>
<rect x="375.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5735" values="#0f172a;#fff4b8"/></rect>
<rect x="390.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5749" values="#0f172a;#fff4b8"/></rect>
<rect x="405.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5763" values="#0f172a;#fff4b8"/></rect>
<rect x="420.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5777" values="#0f172a;#fff4b8"/></rect>
<rect x="435.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5791" values="#0f172a;#fff4b8"/></rect>
<rect x="450.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5805" values="#0f172a;#fff4b8"/></rect>
<rect x="465.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5819" values="#0f172a;#fff4b8"/></rect>
<rect x="480.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5833" values="#0f172a;#fff4b8"/></rect>
<rect x="495.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5847" values="#0f172a;#f4eab1"/></rect>
<rect x="510.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5860" values="#0f172a;#d6cea0"/></rect>
<rect x="525.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5874" values="#0f172a;#b7b28e"/></rect>
<rect x="540.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5888" values="#0f172a;#9e9a7e"/></rect>
<rect x="555.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5902" values="#0f172a;#83816e"/></rect>
<rect x="570.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5916" values="#0f172a;#68695f"/></rect>
<rect x="585.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5930" values="#0f172a;#4f5250"/></rect>
<rect x="600.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5944" values="#0f172a;#3c4044"/></rect>
<rect x="615.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5958" values="#0f172a;#2b313b"/></rect>
<rect x="630.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5972" values="#0f172a;#1e2533"/></rect>
<rect x="645.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5986" values="#0f172a;#171e2f"/></rect>
<rect x="660.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6000" values="#0f172a;#151d2e"/></rect>
<rect x="675.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6014" values="#0f172a;#141b2d"/></rect>
<rect x="690.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#121a2c"/></rect>
<rect x="705.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#11192b"/></rect>
<rect x="720.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#10182b"/></rect>
<rect x="735.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#10182a"/></rect>
<rect x="750.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="765.0" y="302.0" width="15.3" height="17.3" fill="#0f172a"/>
<rect x="60" y="302" width="720.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="30" y="380" width="900" height="90" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="370" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">ガウス ぼかし(同じ広さ σ = 3.4 画素)との比較</text>
<rect x="60.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="75.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="90.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="105.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="120.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="135.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="150.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="165.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="180.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="195.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="210.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="225.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="240.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="255.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7205" values="#0f172a;#141c2d"/></rect>
<rect x="270.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7219" values="#0f172a;#1f2634"/></rect>
<rect x="285.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7233" values="#0f172a;#33383f"/></rect>
<rect x="300.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7247" values="#0f172a;#555753"/></rect>
<rect x="315.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7260" values="#0f172a;#83826f"/></rect>
<rect x="330.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7274" values="#0f172a;#b8b28e"/></rect>
<rect x="345.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7288" values="#0f172a;#e8dfaa"/></rect>
<rect x="360.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7302" values="#0f172a;#fff4b8"/></rect>
<rect x="375.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7316" values="#0f172a;#fff4b8"/></rect>
<rect x="390.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7330" values="#0f172a;#fff4b8"/></rect>
<rect x="405.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7344" values="#0f172a;#fff4b8"/></rect>
<rect x="420.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7358" values="#0f172a;#fff4b8"/></rect>
<rect x="435.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7372" values="#0f172a;#fff4b8"/></rect>
<rect x="450.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7386" values="#0f172a;#fff4b8"/></rect>
<rect x="465.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7400" values="#0f172a;#fff4b8"/></rect>
<rect x="480.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7414" values="#0f172a;#fff4b8"/></rect>
<rect x="495.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7428" values="#0f172a;#fff4b8"/></rect>
<rect x="510.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7442" values="#0f172a;#e8dfaa"/></rect>
<rect x="525.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7456" values="#0f172a;#b8b28e"/></rect>
<rect x="540.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7470" values="#0f172a;#83826f"/></rect>
<rect x="555.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7484" values="#0f172a;#555753"/></rect>
<rect x="570.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7498" values="#0f172a;#33383f"/></rect>
<rect x="585.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7512" values="#0f172a;#1f2634"/></rect>
<rect x="600.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7526" values="#0f172a;#141c2d"/></rect>
<rect x="615.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="630.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="645.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="660.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="675.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="690.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="705.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="720.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="735.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="750.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="765.0" y="400.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="60" y="400" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="75.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="90.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="105.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="120.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="135.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="150.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="165.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="180.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="195.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7149" values="#0f172a;#121a2c"/></rect>
<rect x="210.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7163" values="#0f172a;#182030"/></rect>
<rect x="225.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7177" values="#0f172a;#212835"/></rect>
<rect x="240.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191" values="#0f172a;#2c323b"/></rect>
<rect x="255.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7205" values="#0f172a;#3a3e43"/></rect>
<rect x="270.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7219" values="#0f172a;#484c4c"/></rect>
<rect x="285.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7233" values="#0f172a;#585a55"/></rect>
<rect x="300.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7247" values="#0f172a;#67685e"/></rect>
<rect x="315.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7260" values="#0f172a;#7f7e6c"/></rect>
<rect x="330.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7274" values="#0f172a;#9b987d"/></rect>
<rect x="345.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7288" values="#0f172a;#b7b28d"/></rect>
<rect x="360.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7302" values="#0f172a;#d2ca9d"/></rect>
<rect x="375.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7316" values="#0f172a;#fff4b8"/></rect>
<rect x="390.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7330" values="#0f172a;#fff4b8"/></rect>
<rect x="405.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7344" values="#0f172a;#fff4b8"/></rect>
<rect x="420.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7358" values="#0f172a;#fff4b8"/></rect>
<rect x="435.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7372" values="#0f172a;#fff4b8"/></rect>
<rect x="450.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7386" values="#0f172a;#fff4b8"/></rect>
<rect x="465.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7400" values="#0f172a;#fff4b8"/></rect>
<rect x="480.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7414" values="#0f172a;#fef3b7"/></rect>
<rect x="495.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7428" values="#0f172a;#c7c097"/></rect>
<rect x="510.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7442" values="#0f172a;#a9a585"/></rect>
<rect x="525.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7456" values="#0f172a;#8d8b74"/></rect>
<rect x="540.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7470" values="#0f172a;#767667"/></rect>
<rect x="555.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7484" values="#0f172a;#60625a"/></rect>
<rect x="570.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7498" values="#0f172a;#4c4f4e"/></rect>
<rect x="585.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7512" values="#0f172a;#3a3f43"/></rect>
<rect x="600.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7526" values="#0f172a;#2c323b"/></rect>
<rect x="615.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7540" values="#0f172a;#212835"/></rect>
<rect x="630.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7553" values="#0f172a;#192030"/></rect>
<rect x="645.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7567" values="#0f172a;#141c2d"/></rect>
<rect x="660.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7581" values="#0f172a;#131b2c"/></rect>
<rect x="675.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7595" values="#0f172a;#121a2c"/></rect>
<rect x="690.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7609" values="#0f172a;#11192b"/></rect>
<rect x="705.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7623" values="#0f172a;#10182b"/></rect>
<rect x="720.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7637" values="#0f172a;#10182a"/></rect>
<rect x="735.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="750.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="765.0" y="430.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="60" y="430" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="788" y="414" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">ガウス</text>
<text x="788" y="444" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">デュアル</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7970;0.7972;1.0000" values="0;0;1;1"/><rect x="520" y="484" width="410" height="44" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="536" y="508" text-anchor="start" style="font-size:13px;font-weight:700;fill:#166534">読み込み: デュアル 882 回 / ガウス 1104 回(1 分の 1)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光源を置く<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縮小で広い範囲を集め、拡大で、段ごとに足し戻す<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.7021;0.7023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ広さのガウスと並べる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7021;0.7023;0.7970;0.7972;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">形は近く、読み込みがずっと少ない(ピーク比 1.61)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7970;0.7972;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:dual-filter-passes:end -->

## 実質の広がり

**バイリニアで読むので、1 タップが 2×2 画素を混ぜます**。**ダウンサンプルは、ソースの 約 6×6 画素**を**混ぜている**ことになります。**これを数段重ねる**と**十分に広く滑らか**です。

段数と、実質のぼかしの半径の関係です。3 段で約 12〜16 画素、5 段で約 50〜64 画素、7 段で約 200〜250 画素になります。段が深くなるにつれて、半径が約 2 倍ずつ広がります。

**`offset` を大きくする**と、**段数を増やさずに広がりを増やせます**。**ただし大きすぎるとサンプルがまばらになり、格子状の模様**が**出ます**。

## ガウスとの比較

| 項目 | ガウス（分離・ミップ） | Dual Filter |
| --- | --- | --- |
| <strong>パス数（N 段）</strong> | **ダウン N ＋ ぼかし 2N ＋ アップ N** | **ダウン N ＋ アップ N** |
| **タップ数** | **多い** | **少ない**（5 / 8） |
| **形** | **滑らかな円形** | **やや四角い**（多段でほぼ円） |
| **帯域** | **大きい** | **小さい** |
| **向く場面** | <strong>品質重視（PC・コンソール）</strong> | <strong>帯域重視（モバイル・VR）</strong> |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **最初の段に 13 タップを使う** | **ちらつき対策**（[Downsampling and the Mip Chain](downsample.md)・[Karis](karis-average.md)） |
| **段ごとに `offset` を変える** | **広がりを調整**（**奥の段ほど大きく**） |
| **アップを加算ブレンドで書く** | **足し算のパスを省く** |
| **半精度フォーマット** | **R11G11B10_FLOAT で帯域を減らす** |
| **動的な段数** | **画面サイズ・品質設定で段数を変える** |

## よくあるミス

??? failure "`half_pixel` の基準が、ダウン（ソース側）とアップ（小さい画像側）で混同される"
    **どちらも「読む側のテクスチャ」の半画素**。**読むテクスチャごとに計算**する。

??? failure "`offset` を大きくしすぎて、格子状の模様が出る"
    **段数を増やして広げる**。**`offset` は 1〜2 程度**。

??? failure "最上段で足す強さが強すぎて、全体がぼんやりする"
    **強さを下げる**（[Compositing and Intensity](composite.md)）。

??? failure "四角いにじみが目立つ"
    **段数が少ない**。**4 段以上、またはガウスと併用**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Dual Filter ＝ <strong>縮小・拡大のサンプルの取り方自体をぼかしにする</strong>
    - [x] <strong>ダウン 5 タップ、アップ 8 タップ</strong>。<strong>バイリニアで読む</strong>
    - [x] <strong>パス数が少なく、帯域が小さい</strong>（<strong>モバイル向き</strong>）
    - [x] <strong>`offset`</strong> で<strong>広がりを調整</strong>。<strong>大きすぎると格子模様</strong>
    - [x] <strong>やや四角い形</strong>だが、<strong>多段でほぼ円</strong>

## 参考

- Marius Bjørge, "Bandwidth-Efficient Rendering"（SIGGRAPH 2015, ARM）
- Masaki Kawase, "Frame Buffer Postprocessing Effects in DOUBLE-S.T.E.A.L"（GDC 2003）

## 関連ページ

- [Bloom](index.md)
- [Downsampling and the Mip Chain](downsample.md)
- [Gaussian Blur](gaussian.md)
- [Compositing and Intensity](composite.md)
