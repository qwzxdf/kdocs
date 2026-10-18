---
title: Downsampling and the Mip Chain
tags:
  - 描画
---

# Downsampling and the Mip Chain

<strong>広くて自然なにじみ</strong>を、<strong>1 回の巨大なぼかし</strong>で作るのは重すぎます（ぼかしの半径が大きいほど、タップ数が増える）。そこで画像を半分・1/4・1/8…と縮小しながらぼかし、小さい画像で広いぼかしを安く得て、最後に拡大して足し合わせるのがブルームの標準です。この縮小の連なりがミップ チェーンです。このページでは、なぜ縮小するのか・縮小の方法（ボックス・13 タップ）・段数の決め方・拡大して足す方法・画質の工夫を説明します。

!!! tip "ポイント"
    - <strong>小さい画像で同じぼかしをかける</strong>と、<strong>元の画像では何倍も広いぼかし</strong>になる。<strong>しかも画素数が少なく、安い</strong>。
    - 縮小は<strong>半分ずつ（1/2・1/4・1/8…）</strong>で、<strong>5〜8 段</strong>が目安。
    - <strong>縮小のときにきちんとフィルタする</strong>（<strong>間引くとちらつく</strong>）。<strong>13 タップ</strong>が定番。
    - <strong>拡大は「テント」フィルタ</strong>で<strong>滑らかに</strong>、<strong>各段を足し合わせる</strong>。
    - <strong>各段の重み</strong>を決めると<strong>PSF の形</strong>（<strong>すそ野の長さ</strong>）を<strong>調整</strong>できる。
    - <strong>画面サイズの端数</strong>に注意（<strong>奇数サイズで半分にすると、ずれる</strong>）。

## なぜ縮小するのか

<strong>ぼかしの半径 R（ピクセル）を直接かけると、1 ピクセルあたり約 2R+1 回のタップ</strong>が<strong>要ります</strong>（分離可能ガウスでも）。画像を半分に縮小すれば、同じ半径 R のぼかしが、元の画像では 2R 相当の広さになります。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="ミップ チェーンの考え方">
<text x="20" y="26" class="fig-title">縮小 → ぼかし → 拡大：小さい画像のぼかしは、広い範囲に効く</text>
<g font-size="12">
<rect x="30" y="60" width="160" height="120" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="110" cy="120" r="6" fill="#f59e0b"/><text x="110" y="198" text-anchor="middle">元の画像（1/1）</text>
<rect x="230" y="75" width="110" height="90" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="285" cy="120" r="5" fill="#f59e0b" opacity="0.8"/><text x="285" y="198" text-anchor="middle">1/2</text>
<rect x="380" y="90" width="70" height="60" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="415" cy="120" r="5" fill="#f59e0b" opacity="0.6"/><text x="415" y="198" text-anchor="middle">1/4</text>
<rect x="490" y="100" width="44" height="40" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="512" cy="120" r="5" fill="#f59e0b" opacity="0.5"/><text x="512" y="198" text-anchor="middle">1/8</text>
<rect x="574" y="108" width="28" height="24" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="588" cy="120" r="4" fill="#f59e0b" opacity="0.4"/><text x="588" y="198" text-anchor="middle">1/16</text>
</g>
<text x="640" y="110" style="font-size:13px">段が深いほど、</text><text x="640" y="132" style="font-size:13px">画素が少なく、</text><text x="640" y="154" style="font-size:13px">広いぼかしが安い</text>
<text x="30" y="236" style="font-size:12px">コスト：各段は前の 1/4 の画素数 → 全段を足しても、元の画像 1 枚の約 1/3 増し</text>
</svg>

ぼかしの広さとコストを比べます。元の解像度で半径 64 のガウスをかけると、約 130 タップ（分離しても 2 パス）が必要で、広さは半径 64 です。ミップ 6 段で各段に小さなぼかしをかける方法は、各段で数タップに済み、画素数が急減するので、半径 64 以上の広さまでカバーできます。広いぼかしを、元の解像度で直接かけるのは、割に合いません。

## ダウンサンプルの方法

<strong>縮小のとき、ただ間引く（点サンプル）と、小さな明るい点が画素の位置次第で「出たり消えたり」して、ちらつきます</strong>。<strong>周りを平均して縮小</strong>する必要があります。

### バイリニア 1 回（2×2 の平均）

```hlsl
float3 DownsampleBilinear(Texture2D src, SamplerState linear_clamp, float2 uv) {
  return src.SampleLevel(linear_clamp, uv, 0).rgb;
}
```

<strong>GPU のバイリニア補間が、4 画素の平均</strong>を<strong>1 タップで</strong>与えます。速いですがちらつきを完全には防げません。

### 13 タップ（Call of Duty: Advanced Warfare 方式）

<strong>中心と周囲 13 点を、重み付きで平均</strong>する方式です。<strong>小さな明るい点のちらつきを、ほぼ消せる</strong>ため、定番です。

```hlsl
float3 Downsample13(Texture2D src, SamplerState linear_clamp, float2 uv, float2 texel) {
  float3 a = src.SampleLevel(linear_clamp, uv + texel * float2(-2, -2), 0).rgb;
  float3 b = src.SampleLevel(linear_clamp, uv + texel * float2( 0, -2), 0).rgb;
  float3 c = src.SampleLevel(linear_clamp, uv + texel * float2( 2, -2), 0).rgb;
  float3 d = src.SampleLevel(linear_clamp, uv + texel * float2(-2,  0), 0).rgb;
  float3 e = src.SampleLevel(linear_clamp, uv, 0).rgb;
  float3 f = src.SampleLevel(linear_clamp, uv + texel * float2( 2,  0), 0).rgb;
  float3 g = src.SampleLevel(linear_clamp, uv + texel * float2(-2,  2), 0).rgb;
  float3 h = src.SampleLevel(linear_clamp, uv + texel * float2( 0,  2), 0).rgb;
  float3 i = src.SampleLevel(linear_clamp, uv + texel * float2( 2,  2), 0).rgb;
  float3 j = src.SampleLevel(linear_clamp, uv + texel * float2(-1, -1), 0).rgb;
  float3 k = src.SampleLevel(linear_clamp, uv + texel * float2( 1, -1), 0).rgb;
  float3 l = src.SampleLevel(linear_clamp, uv + texel * float2(-1,  1), 0).rgb;
  float3 m = src.SampleLevel(linear_clamp, uv + texel * float2( 1,  1), 0).rgb;

  float3 center = (j + k + l + m) * 0.25;
  float3 box_a = (a + b + d + e) * 0.25;
  float3 box_b = (b + c + e + f) * 0.25;
  float3 box_c = (d + e + g + h) * 0.25;
  float3 box_d = (e + f + h + i) * 0.25;
  return center * 0.5 + (box_a + box_b + box_c + box_d) * 0.125;
}
```

| 点 | 説明 |
| --- | --- |
| `texel` | ソース画像の 1 画素の UV 幅（`1 / ソース幅`） |
| 重みの構成 | 中央の 2×2 に 0.5、周囲の 4 つの 2×2 ボックスに 0.125 ずつ（合計 1） |
| バイリニアと併用 | 各タップがバイリニアで 4 画素ずつを混ぜるので、実質 36 画素を平均 |
| 最初の段だけ使う | 2 段目以降は、軽い 4 タップでも足りる |


この 13 タップの縮小は、Jimenez の SIGGRAPH 2014 の発表 "Next Generation Post Processing in Call of Duty: Advanced Warfare" で紹介された方法です。単純な 4 タップのバイリニア縮小は、元の画素の一部しか使わないので、小さな明るい点が抜け落ちたり、ちらついたりします。13 タップなら、元画像の画素を漏れなく使えます。

この 13 タップの縮小は、Jimenez の SIGGRAPH 2014 の発表 "Next Generation Post Processing in Call of Duty: Advanced Warfare" で紹介された方法です。単純な 4 タップのバイリニア縮小は、元の画素の一部しか使わないので、小さな明るい点が抜け落ちたり、ちらついたりします。13 タップなら、元画像の画素を漏れなく使えます。

<!-- fig:bloom-mip-chain:begin -->

<svg class="fig illust motion" data-fig="bloom-mip-chain" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bloom-mip-chain" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">縮小ぼかし: 1 段下げるごとに、同じ 5 画素のぼかしが、2 倍の範囲をぼかす</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素の光源(1 つ)。縮小 → 小さい画像でぼかす → 拡大して足す。ぼけの広さと、読み込み回数を数える</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/><text x="60.0" y="106" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">段 0: 48 画素 → ぼかす → 元の大きさに拡大</text>
<rect x="60.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="74.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="88.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="102.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="116.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="130.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="144.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="158.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="172.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="186.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="200.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="214.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="228.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="242.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="256.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="270.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="284.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="298.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="312.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="326.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="340.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="354.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="368.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1191" values="#0f172a;#fff4b8"/></rect>
<rect x="382.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1205" values="#0f172a;#fff4b8"/></rect>
<rect x="396.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1219" values="#0f172a;#fff4b8"/></rect>
<rect x="410.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233" values="#0f172a;#fff4b8"/></rect>
<rect x="424.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1247" values="#0f172a;#fff4b8"/></rect>
<rect x="438.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="452.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="466.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="480.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="494.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="508.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="522.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="536.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="550.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="564.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="578.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="592.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="606.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="620.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="634.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="648.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="662.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="676.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="690.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="704.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="718.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="60.0" y="110" width="672.0" height="14.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="740.0" y="124" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">ぼけの広さ ±1.1 画素</text>
<text x="740.0" y="142" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">読み込み 240 回</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2277;0.2279;1.0000" values="0;0;1;1"/><text x="60.0" y="170" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">段 1: 24 画素 → ぼかす → 元の大きさに拡大</text>
<rect x="60.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="74.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="88.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="102.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="116.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="130.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="144.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="158.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="172.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="186.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="200.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="214.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="228.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="242.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="256.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="270.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="284.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="298.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="312.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="326.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2730" values="#0f172a;#6a6b60"/></rect>
<rect x="340.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2744" values="#0f172a;#c9c298"/></rect>
<rect x="354.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2758" values="#0f172a;#fff4b8"/></rect>
<rect x="368.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2772" values="#0f172a;#fff4b8"/></rect>
<rect x="382.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2786" values="#0f172a;#fff4b8"/></rect>
<rect x="396.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#0f172a;#fff4b8"/></rect>
<rect x="410.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2814" values="#0f172a;#fff4b8"/></rect>
<rect x="424.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2828" values="#0f172a;#fff4b8"/></rect>
<rect x="438.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2842" values="#0f172a;#fff4b8"/></rect>
<rect x="452.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2856" values="#0f172a;#fff4b8"/></rect>
<rect x="466.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2870" values="#0f172a;#c9c298"/></rect>
<rect x="480.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2884" values="#0f172a;#6a6b60"/></rect>
<rect x="494.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="508.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="522.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="536.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="550.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="564.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="578.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="592.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="606.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="620.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="634.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="648.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="662.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="676.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="690.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="704.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="718.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="60.0" y="174" width="672.0" height="14.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="740.0" y="188" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">ぼけの広さ ±2.4 画素</text>
<text x="740.0" y="206" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">読み込み 120 回</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3859;0.3860;1.0000" values="0;0;1;1"/><text x="60.0" y="234" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">段 2: 12 画素 → ぼかす → 元の大きさに拡大</text>
<rect x="60.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="74.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="88.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="102.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="116.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="130.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="144.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="158.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="172.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="186.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="200.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="214.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="228.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="242.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="256.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4242" values="#0f172a;#2b313a"/></rect>
<rect x="270.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4256" values="#0f172a;#585a55"/></rect>
<rect x="284.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4270" values="#0f172a;#7b7a6a"/></rect>
<rect x="298.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4284" values="#0f172a;#97947a"/></rect>
<rect x="312.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4298" values="#0f172a;#c0ba93"/></rect>
<rect x="326.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4312" values="#0f172a;#eae1ac"/></rect>
<rect x="340.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4326" values="#0f172a;#fff4b8"/></rect>
<rect x="354.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4340" values="#0f172a;#fff4b8"/></rect>
<rect x="368.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="#0f172a;#fff4b8"/></rect>
<rect x="382.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4367" values="#0f172a;#fff4b8"/></rect>
<rect x="396.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4381" values="#0f172a;#fff4b8"/></rect>
<rect x="410.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4395" values="#0f172a;#fff4b8"/></rect>
<rect x="424.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4409" values="#0f172a;#fff4b8"/></rect>
<rect x="438.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4423" values="#0f172a;#fff4b8"/></rect>
<rect x="452.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4437" values="#0f172a;#fff4b8"/></rect>
<rect x="466.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4451" values="#0f172a;#fff4b8"/></rect>
<rect x="480.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4465" values="#0f172a;#fff4b8"/></rect>
<rect x="494.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4479" values="#0f172a;#fff4b8"/></rect>
<rect x="508.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4493" values="#0f172a;#eae1ac"/></rect>
<rect x="522.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4507" values="#0f172a;#c0ba93"/></rect>
<rect x="536.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4521" values="#0f172a;#97947a"/></rect>
<rect x="550.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4535" values="#0f172a;#7b7a6a"/></rect>
<rect x="564.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4549" values="#0f172a;#585a55"/></rect>
<rect x="578.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4563" values="#0f172a;#2b313a"/></rect>
<rect x="592.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="606.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="620.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="634.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="648.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="662.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="676.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="690.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="704.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="718.0" y="238.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="60.0" y="238" width="672.0" height="14.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="740.0" y="252" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">ぼけの広さ ±4.8 画素</text>
<text x="740.0" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">読み込み 60 回</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5440;0.5442;1.0000" values="0;0;1;1"/><text x="60.0" y="298" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">段 3: 6 画素 → ぼかす → 元の大きさに拡大</text>
<rect x="60.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="74.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="88.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="102.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="116.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5684" values="#0f172a;#161e2e"/></rect>
<rect x="130.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5698" values="#0f172a;#242b37"/></rect>
<rect x="144.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5712" values="#0f172a;#31363e"/></rect>
<rect x="158.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5726" values="#0f172a;#3d4245"/></rect>
<rect x="172.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5740" values="#0f172a;#484c4c"/></rect>
<rect x="186.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5753" values="#0f172a;#535652"/></rect>
<rect x="200.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5767" values="#0f172a;#5d5f58"/></rect>
<rect x="214.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5781" values="#0f172a;#66675d"/></rect>
<rect x="228.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5795" values="#0f172a;#777767"/></rect>
<rect x="242.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5809" values="#0f172a;#8d8b75"/></rect>
<rect x="256.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5823" values="#0f172a;#a09c80"/></rect>
<rect x="270.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5837" values="#0f172a;#b0ab89"/></rect>
<rect x="284.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5851" values="#0f172a;#beb892"/></rect>
<rect x="298.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5865" values="#0f172a;#cbc499"/></rect>
<rect x="312.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5879" values="#0f172a;#d6cea0"/></rect>
<rect x="326.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5893" values="#0f172a;#e0d7a6"/></rect>
<rect x="340.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5907" values="#0f172a;#e7deaa"/></rect>
<rect x="354.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5921" values="#0f172a;#ede3ad"/></rect>
<rect x="368.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5935" values="#0f172a;#f2e8b0"/></rect>
<rect x="382.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5949" values="#0f172a;#f7ecb3"/></rect>
<rect x="396.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5963" values="#0f172a;#fbf1b6"/></rect>
<rect x="410.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5977" values="#0f172a;#fff4b8"/></rect>
<rect x="424.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5991" values="#0f172a;#fff4b8"/></rect>
<rect x="438.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6005" values="#0f172a;#fff4b8"/></rect>
<rect x="452.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6019" values="#0f172a;#fff4b8"/></rect>
<rect x="466.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6033" values="#0f172a;#fff4b8"/></rect>
<rect x="480.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6047" values="#0f172a;#fff4b8"/></rect>
<rect x="494.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6060" values="#0f172a;#fbf1b6"/></rect>
<rect x="508.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6074" values="#0f172a;#f7ecb3"/></rect>
<rect x="522.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6088" values="#0f172a;#f2e8b0"/></rect>
<rect x="536.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6102" values="#0f172a;#ede3ad"/></rect>
<rect x="550.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6116" values="#0f172a;#e7deaa"/></rect>
<rect x="564.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6130" values="#0f172a;#e0d7a6"/></rect>
<rect x="578.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6144" values="#0f172a;#d6cea0"/></rect>
<rect x="592.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6158" values="#0f172a;#cbc499"/></rect>
<rect x="606.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6172" values="#0f172a;#beb892"/></rect>
<rect x="620.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6186" values="#0f172a;#b0ab89"/></rect>
<rect x="634.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6200" values="#0f172a;#a09c80"/></rect>
<rect x="648.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6214" values="#0f172a;#8d8b75"/></rect>
<rect x="662.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6228" values="#0f172a;#777767"/></rect>
<rect x="676.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6242" values="#0f172a;#6a6b60"/></rect>
<rect x="690.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6256" values="#0f172a;#6a6b60"/></rect>
<rect x="704.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6270" values="#0f172a;#6a6b60"/></rect>
<rect x="718.0" y="302.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6284" values="#0f172a;#6a6b60"/></rect>
<rect x="60.0" y="302" width="672.0" height="14.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="740.0" y="316" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">ぼけの広さ ±9.5 画素</text>
<text x="740.0" y="334" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">読み込み 30 回</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7021;0.7023;1.0000" values="0;0;1;1"/><text x="60.0" y="362" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">段 4: 3 画素 → ぼかす → 元の大きさに拡大</text>
<rect x="60.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7209" values="#0f172a;#a39f81"/></rect>
<rect x="74.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7223" values="#0f172a;#a39f81"/></rect>
<rect x="88.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7237" values="#0f172a;#a39f81"/></rect>
<rect x="102.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7251" values="#0f172a;#a39f81"/></rect>
<rect x="116.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7265" values="#0f172a;#a39f81"/></rect>
<rect x="130.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7279" values="#0f172a;#a39f81"/></rect>
<rect x="144.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7293" values="#0f172a;#a39f81"/></rect>
<rect x="158.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7307" values="#0f172a;#a39f81"/></rect>
<rect x="172.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7321" values="#0f172a;#a4a082"/></rect>
<rect x="186.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7335" values="#0f172a;#a7a384"/></rect>
<rect x="200.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7349" values="#0f172a;#aaa585"/></rect>
<rect x="214.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7363" values="#0f172a;#aca887"/></rect>
<rect x="228.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7377" values="#0f172a;#afaa89"/></rect>
<rect x="242.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7391" values="#0f172a;#b1ac8a"/></rect>
<rect x="256.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7405" values="#0f172a;#b4af8c"/></rect>
<rect x="270.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7419" values="#0f172a;#b6b18d"/></rect>
<rect x="284.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7433" values="#0f172a;#b9b38e"/></rect>
<rect x="298.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7447" values="#0f172a;#bbb590"/></rect>
<rect x="312.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7460" values="#0f172a;#bdb791"/></rect>
<rect x="326.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7474" values="#0f172a;#bfb992"/></rect>
<rect x="340.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7488" values="#0f172a;#c2bb94"/></rect>
<rect x="354.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7502" values="#0f172a;#c4bd95"/></rect>
<rect x="368.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7516" values="#0f172a;#c6bf96"/></rect>
<rect x="382.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7530" values="#0f172a;#c8c197"/></rect>
<rect x="396.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7544" values="#0f172a;#c8c197"/></rect>
<rect x="410.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7558" values="#0f172a;#c6bf96"/></rect>
<rect x="424.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7572" values="#0f172a;#c4bd95"/></rect>
<rect x="438.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7586" values="#0f172a;#c2bb94"/></rect>
<rect x="452.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7600" values="#0f172a;#bfb992"/></rect>
<rect x="466.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7614" values="#0f172a;#bdb791"/></rect>
<rect x="480.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7628" values="#0f172a;#bbb590"/></rect>
<rect x="494.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7642" values="#0f172a;#b9b38e"/></rect>
<rect x="508.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7656" values="#0f172a;#b6b18d"/></rect>
<rect x="522.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7670" values="#0f172a;#b4af8c"/></rect>
<rect x="536.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7684" values="#0f172a;#b1ac8a"/></rect>
<rect x="550.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7698" values="#0f172a;#afaa89"/></rect>
<rect x="564.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7712" values="#0f172a;#aca887"/></rect>
<rect x="578.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7726" values="#0f172a;#aaa585"/></rect>
<rect x="592.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7740" values="#0f172a;#a7a384"/></rect>
<rect x="606.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7753" values="#0f172a;#a4a082"/></rect>
<rect x="620.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7767" values="#0f172a;#a39f81"/></rect>
<rect x="634.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7781" values="#0f172a;#a39f81"/></rect>
<rect x="648.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7795" values="#0f172a;#a39f81"/></rect>
<rect x="662.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7809" values="#0f172a;#a39f81"/></rect>
<rect x="676.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7823" values="#0f172a;#a39f81"/></rect>
<rect x="690.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7837" values="#0f172a;#a39f81"/></rect>
<rect x="704.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7851" values="#0f172a;#a39f81"/></rect>
<rect x="718.0" y="366.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7865" values="#0f172a;#a39f81"/></rect>
<rect x="60.0" y="366" width="672.0" height="14.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="740.0" y="380" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">ぼけの広さ ±13.1 画素</text>
<text x="740.0" y="398" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">読み込み 15 回</text>
</g>
<text x="40" y="450" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">読み込みの合計:</text>
<text x="180" y="454" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0882;0.0884;1.0000" values="1;1;0;0"/></text>
<text x="180" y="454" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">240<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0882;0.0884;0.2463;0.2465;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="454" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">360<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2463;0.2465;0.4045;0.4047;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="454" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">420<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4045;0.4047;0.5626;0.5628;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="454" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">450<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5626;0.5628;0.7207;0.7209;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="454" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">465<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7207;0.7209;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8417;0.8419;1.0000" values="0;0;1;1"/><rect x="400" y="470" width="530" height="52" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="416" y="494" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">5 段で、広さ ±13.1 画素のぼけ。読み込みは合計 465 回</text>
<text x="416" y="517" text-anchor="start" style="font-size:13px;font-weight:700;fill:#991b1b">直接ぼかすと、同じ広さに 2,544 回(約 5 倍)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光源を 1 点、置く<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画像を半分にするたびに、同じ 5 画素のぼかしが、倍の広さに効く<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.8603;0.8605;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">小さい画像ほど安い。全部足すと、裾の広い光になる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8603;0.8605;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bloom-mip-chain:end -->

## 段数の決め方

| 項目 | 内容 |
| --- | --- |
| 段数 | 5〜8 段（最小の段が 画面の 1/32〜1/128） |
| 広さ | 段が深いほど、画面の広い範囲に光が回る（<strong>大きな「もや」</strong>） |
| 解像度に依らない見た目 | 段数を画面の大きさから決める（4K でも、1080p でも同じ見た目） |
| 最初の段 | 画面の 1/2 で始める（フル解像度で始めると重い） |

<strong>画面の端数</strong>に注意します。<strong>奇数の幅を半分にすると、1 画素ずつずれ</strong>、光が少し動いて見えます。切り上げ（`(w + 1) / 2`）で作り、サンプルの位置も合わせると安定します。

## アップサンプルして足し合わせる

<strong>小さい方から、順に拡大して、1 段上に足していきます</strong>。

<div class="formula">段 i の結果 = ぼかした段 i + アップサンプル( 段 i+1 の結果 )</div>

```hlsl
float3 UpsampleTent(Texture2D src, SamplerState linear_clamp, float2 uv, float2 texel) {
  float3 sum = 0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2(-1, -1), 0).rgb * 1.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 0, -1), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 1, -1), 0).rgb * 1.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2(-1,  0), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv, 0).rgb * 4.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 1,  0), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2(-1,  1), 0).rgb * 1.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 0,  1), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 1,  1), 0).rgb * 1.0;
  return sum / 16.0;
}
```

アップサンプルのコードの要点です。テント フィルタ（3×3）は、中心 4、辺 2、角 1 の重みで、滑らかに拡大できます。加算ブレンドで、1 段上の画像にブレンド（加算）で書き込むと、足し算のパスが不要になります。バイリニアの拡大だけでは、ブロック状のアーティファクトが出るので、テントで滑らかにします。

## 各段の重みで PSF を調整する

<strong>各段を足すときの重み</strong>を<strong>変える</strong>と、にじみの形（すそ野の長さ）を調整できます。

各段を足すときの重みを変えると、にじみの形（すそ野の長さ）を調整できます。均等なら、標準的なにじみです。小さい段（細かい段）を強くすると、すそ野が短くてくっきりします。大きい段（粗い段）を強くすると、広い「もや」が目立ち、眩しい夢のような絵になります。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 13 タップで最初の段を縮小 | ちらつきを抑える |
| 2 段目以降は軽い縮小 | 4 タップのバイリニアで十分 |
| アップサンプル時に加算ブレンド | パス数と帯域を減らす |
| <strong>半精度（R11G11B10）</strong> | メモリと帯域を減らす（HDR でもブルームは精度が低くてよい） |
| 解像度を画面の高さで決める | 段数が画面サイズで変わっても、見た目をそろえる |
| Dual Filter を使う | 縮小とぼかしを兼ねて、さらに安く（[Dual Filter](dual-filter.md)） |

## よくあるミス

??? failure "縮小を点サンプルにして、小さな明るい点がちらつく"
    <strong>バイリニア（最低）、できれば 13 タップ</strong>で縮小。<strong>さらに[ファイアフライ対策](karis-average.md)</strong>。

??? failure "段数を固定して、4K ではにじみが狭く見える"
    <strong>画面の高さから、段数・最小サイズを決める</strong>。

??? failure "奇数サイズで縮小して、光が 1 画素ずつ動く"
    <strong>切り上げのサイズで作り、UV を合わせる</strong>。

??? failure "アップサンプルをバイリニアだけにして、四角いブロックが見える"
    <strong>テント フィルタ（3×3）</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>縮小しながらぼかす</strong>と、<strong>広いぼかしが安い</strong>（<strong>ミップ チェーン</strong>）
    - [x] <strong>縮小は、きちんとフィルタ</strong>（<strong>13 タップ</strong>）。<strong>間引くとちらつく</strong>
    - [x] <strong>5〜8 段</strong>。<strong>画面の高さから決める</strong>
    - [x] <strong>拡大はテント</strong>、<strong>加算ブレンドで足し合わせる</strong>
    - [x] <strong>各段の重み</strong>で<strong>すそ野の長さ</strong>を調整

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Mittring, "A Bit More Deferred - CryEngine 3"（GDC 2009）
- Williams, "Pyramidal Parametrics"（SIGGRAPH 1983）

## 関連ページ

- [Bloom](index.md)
- [Threshold](threshold.md)
- [Gaussian Blur](gaussian.md)
- [Dual Filter](dual-filter.md)
- [Fireflies (Karis Average)](karis-average.md)
