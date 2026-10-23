---
title: Auto Exposure
tags:
  - 描画
---

# Auto Exposure

<strong>暗い所から明るい所へ出ると、目が慣れるまでまぶしい</strong>——この明暗順応を再現するのが自動露出（Eye Adaptation）です。画面の明るさを測って、適切な露出を決め、時間をかけて追従させます。これがないと明るさが大きく変わるゲームでは、どこかで真っ白か真っ暗になります。このページでは、平均輝度の測り方（縮小・ヒストグラム）・外れ値の除外・目標露出の決め方・時間的な追従・仕上げの工夫を説明します。

!!! tip "ポイント"
    - 自動露出 ＝ <strong>画面の明るさを測る → 目標露出を決める → 時間で追従する</strong>。
    - 明るさは<strong>対数平均（幾何平均）</strong>で測る。明るい点（太陽）に引きずられにくい。
    - ヒストグラムで外れ値を除くと頑健。縮小（ミップ）は簡単。
    - 追従は指数的：`1 − exp(−dt · 速度)`。フレームレートに依らない。
    - 明→暗は遅く、暗→明は速く（目は暗順応が遅い）。
    - 最小・最大の EV を制限し、露出補正で画作りを残す。

## 全体の流れ

<svg class="fig illust" viewBox="0 0 780 170" role="img" aria-label="自動露出の流れ">
<text x="20" y="26" class="fig-title">自動露出：測る → 決める → 追従する</text>
<defs><marker id="ae-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="13">
<rect x="20" y="56" width="170" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/><text x="105" y="86" text-anchor="middle" style="font-weight:700">① 明るさを測る</text><text x="105" y="108" text-anchor="middle" style="font-size:11px">対数平均・ヒストグラム</text>
<rect x="230" y="56" width="170" height="70" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/><text x="315" y="86" text-anchor="middle" style="font-weight:700">② 目標の露出</text><text x="315" y="108" text-anchor="middle" style="font-size:11px">EV に換算・補正・範囲</text>
<rect x="440" y="56" width="170" height="70" rx="8" fill="#e5484d" fill-opacity="0.18" stroke="#e5484d" stroke-width="2"/><text x="525" y="86" text-anchor="middle" style="font-weight:700">③ 時間で追従</text><text x="525" y="108" text-anchor="middle" style="font-size:11px">指数的・明暗で速度差</text>
<rect x="650" y="56" width="110" height="70" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/><text x="705" y="86" text-anchor="middle" style="font-weight:700">④ 適用</text><text x="705" y="108" text-anchor="middle" style="font-size:11px">HDR に掛ける</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="192" y1="91" x2="228" y2="91" marker-end="url(#ae-arrow)"/><line x1="402" y1="91" x2="438" y2="91" marker-end="url(#ae-arrow)"/><line x1="612" y1="91" x2="648" y2="91" marker-end="url(#ae-arrow)"/></g>
</svg>

## ① 明るさを測る

### 対数平均

<strong>単純な平均は太陽のような非常に明るい点に引きずられて、シーン全体が暗くなります</strong>。対数をとってから平均する（幾何平均）と、外れ値の影響が小さくなります。

<div class="formula">L_avg = exp( (1/N) · Σ log(L + ε) )</div>

| 方式 | 内容 | 特徴 |
| --- | --- | --- |
| 縮小（ミップ チェーン） | `log(L)` を 1×1 まで縮小して平均 | 簡単・速い。外れ値の除外はできない |
| ヒストグラム | 輝度を数十〜256 のビンに数える | 外れ値を除ける。頑健 |
| 中心重み | 画面中心を重くして平均 | 視線が中心にあると仮定 |

### 縮小で測る

```hlsl
float LogLuminance(float3 c) {
  return log(max(dot(c, float3(0.2126, 0.7152, 0.0722)), 1e-4));
}
```

画面の `log(L)` を書いたテクスチャをミップで 1×1 まで縮小し、`exp` で戻すと対数平均です。実装が最も簡単ですが明るい点・暗い点が混ざるのでシーンによっては安定しません。

### ヒストグラムで測る

輝度を `log2` 空間で、等間隔のビンに数える方式です。各ビンのピクセル数をコンピュートで集計します。

```hlsl
#define HISTOGRAM_BINS 256

RWStructuredBuffer<uint> histogram : register(u0);
Texture2D<float4> hdr_color : register(t0);

cbuffer HistogramConstants : register(b0) {
  uint2 size;
  float min_log_luminance;
  float inverse_log_luminance_range;
};
```

ヒストグラムは、256 個の、ビンで、輝度（の、対数）を、数えます。入力は、HDR の色で、出力は、全グループで、共有する、ヒストグラムの、バッファ（UAV）です。

```hlsl
groupshared uint s_histogram[HISTOGRAM_BINS];
```

グループ内で、まず、数えるための、共有メモリです。全画素が、直接、グローバルの、ヒストグラムに、足すと、同じビンに、衝突が、集中して、遅くなるので、グループ内で、数えてから、まとめて、足します。

```hlsl
uint LuminanceToBin(float luminance) {
  if (luminance < 0.001) return 0;
  float log_luminance = saturate((log2(luminance) - min_log_luminance) * inverse_log_luminance_range);
  return uint(log_luminance * 254.0 + 1.0);
}
```

輝度を、ビンの番号に、変えます。対数に直して、範囲に、正規化し、1〜255 に、割り当てます。ビン 0 は、ほぼ、真っ暗な画素（`0.001` 未満）を、数えて、平均から、除くための、専用です。

```hlsl
[numthreads(16, 16, 1)]
void HistogramMain(uint3 id : SV_DispatchThreadID, uint group_index : SV_GroupIndex) {
  s_histogram[group_index] = 0;
  GroupMemoryBarrierWithGroupSync();
```

共有メモリを、0 に、初期化して、グループ全体で、そろうのを、待ちます。

```hlsl
  if (all(id.xy < size)) {
    float3 color = hdr_color.Load(int3(id.xy, 0)).rgb;
    uint bin = LuminanceToBin(dot(color, float3(0.2126, 0.7152, 0.0722)));
    InterlockedAdd(s_histogram[bin], 1);
  }
```

画素の色を、読み、輝度（Rec.709 の、重み）から、ビンを、求めて、共有メモリの、カウンターを、1 増やします。`InterlockedAdd` で、グループ内の、スレッドが、同時に、足しても、正しく、数えられます。

```hlsl
  GroupMemoryBarrierWithGroupSync();
  InterlockedAdd(histogram[group_index], s_histogram[group_index]);
}
```

ヒストグラムのコードの要点です。共有メモリで先にグループ内を集計してから、グローバルへ足します（グローバルの原子操作を減らすため）。ビン 0 は、ほぼ黒の画素を除外するための専用のビンです。`log2` 空間で数えるので、EV と同じ単位で等間隔になり、人間の知覚に合います。

<!-- fig:auto-exposure-histogram:begin -->

<svg class="fig illust motion" data-fig="auto-exposure-histogram" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-auto-exposure-histogram" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">自動露出(ヒストグラム): 画面の明るさの分布を作り、暗い所と明るすぎる所を除いた平均で、露出を決める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">24×12 画素の HDR 画像(窓から日が差す部屋)。明るさを 8 段のビンに数える</text>
<rect x="30" y="96" width="352.0" height="184.0" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 入力(HDR)</text>
<rect x="38.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="262.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="276.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="290.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="304.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="318.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="332.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="346.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="360.0" y="104.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="262.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="276.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="290.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="304.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="318.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="332.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="346.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="360.0" y="118.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="262.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="276.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="290.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="304.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="318.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="332.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="346.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="360.0" y="132.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="262.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="276.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="290.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="304.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="318.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="332.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="346.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="360.0" y="146.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="262.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="276.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="290.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="304.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="318.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="332.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="346.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="360.0" y="160.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="262.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="276.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="290.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="304.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="318.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="332.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="346.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="360.0" y="174.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="262.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="276.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="290.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="304.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="318.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="332.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="346.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="360.0" y="188.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="80.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4e4e4e"/></rect>
<rect x="94.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="108.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="122.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4f4f4f"/></rect>
<rect x="136.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="150.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="164.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#505050"/></rect>
<rect x="178.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="192.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="206.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="262.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="276.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="290.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="304.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="318.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="332.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="346.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="360.0" y="202.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="80.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="94.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="108.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="122.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="136.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="150.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="164.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="178.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="192.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="206.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="262.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="276.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="290.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="304.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="318.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="332.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="346.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#ffffff"/></rect>
<rect x="360.0" y="216.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="80.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="94.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="108.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="122.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="136.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="150.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="164.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="178.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="192.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="206.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="262.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="276.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="290.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="304.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="318.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="332.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="346.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="360.0" y="230.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="80.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#0b0b0b"/></rect>
<rect x="94.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="108.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="122.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="136.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="150.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="164.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="178.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="192.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="206.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="262.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="276.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="290.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="304.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="318.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="332.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="346.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="360.0" y="244.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="38.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="52.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#4d4d4d"/></rect>
<rect x="66.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="80.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="94.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="108.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="122.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="136.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="150.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="164.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="178.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="192.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#7a7a7a"/></rect>
<rect x="206.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#515151"/></rect>
<rect x="220.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="234.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="248.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#525252"/></rect>
<rect x="262.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="276.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="290.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#535353"/></rect>
<rect x="304.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="318.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="332.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#545454"/></rect>
<rect x="346.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="360.0" y="258.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#555555"/></rect>
<rect x="410" y="96" width="520" height="200" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="410" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 明るさ(EV)ごとの画素数</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><rect x="428" y="269.22" width="46" height="1" fill="#0e7490" opacity="0.9"/>
<text x="451" y="264.22" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">1</text>
<text x="451" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">-6〜-5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="0;0;1;1"/><rect x="483" y="270.0" width="46" height="1" fill="#0891b2" opacity="0.9"/>
<text x="506" y="265.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">0</text>
<text x="506" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">-5〜-4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="0;0;1;1"/><rect x="538" y="120.0" width="46" height="150.0" fill="#38bdf8" opacity="0.9"/>
<text x="561" y="115.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">192</text>
<text x="561" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">-4〜-3</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;1.0000" values="0;0;1;1"/><rect x="593" y="239.53" width="46" height="30.47" fill="#60a5fa" opacity="0.9"/>
<text x="616" y="234.53" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">39</text>
<text x="616" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">-3〜-2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;1.0000" values="0;0;1;1"/><rect x="648" y="270.0" width="46" height="1" fill="#818cf8" opacity="0.9"/>
<text x="671" y="265.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">0</text>
<text x="671" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">-2〜-1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;1.0000" values="0;0;1;1"/><rect x="703" y="270.0" width="46" height="1" fill="#a78bfa" opacity="0.9"/>
<text x="726" y="265.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">0</text>
<text x="726" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">-1〜+0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/><rect x="758" y="270.0" width="46" height="1" fill="#f472b6" opacity="0.9"/>
<text x="781" y="265.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">0</text>
<text x="781" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">+0〜+1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3776;0.3778;1.0000" values="0;0;1;1"/><rect x="813" y="270.0" width="46" height="1" fill="#fb7185" opacity="0.9"/>
<text x="836" y="265.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">0</text>
<text x="836" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">+1〜+2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000" values="0;0;1;1"/><rect x="868" y="226.25" width="46" height="43.75" fill="#fbbf24" opacity="0.9"/>
<text x="891" y="221.25" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">56</text>
<text x="891" y="284" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">+2〜+3</text>
</g>
<rect x="80.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#0e7490" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.1109;0.1111;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="104.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="118.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="38.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="52.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="206.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="220.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="234.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="360.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#38bdf8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="230.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="244.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="66.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="80.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="94.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="108.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="122.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="150.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="164.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="178.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="192.0" y="258.0" width="14.0" height="14.0" fill="none" stroke="#60a5fa" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="132.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="146.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="160.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="174.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="188.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="202.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="248.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="262.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="276.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="290.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="318.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="332.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="346.0" y="216.0" width="14.0" height="14.0" fill="none" stroke="#fbbf24" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="428" y="140" width="46" height="130" fill="#ffffff" fill-opacity="0.65" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5022;1.0000" values="0;0;1;1"/></rect>
<rect x="483" y="140" width="46" height="130" fill="#ffffff" fill-opacity="0.65" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5022;1.0000" values="0;0;1;1"/></rect>
<text x="428" y="118" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">下位 10% と上位 10% を捨てる(白く薄れた所)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5022;1.0000" values="0;0;1;1"/></text>
<rect x="30" y="330" width="900" height="150" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="320" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">③ 平均の明るさと、そこから決める露出</text>
<text x="50" y="366" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">全画素の単純平均(明るい窓に引っぱられる)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5820;0.5822;1.0000" values="0;0;1;1"/></text>
<text x="540" y="366" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d" opacity="0">平均 1.64 → 露出 ×0.109<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5820;0.5822;1.0000" values="0;0;1;1"/></text>
<text x="50" y="406" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">ヒストグラムの中央を使った平均(窓と暗がりを除く)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6443;0.6444;1.0000" values="0;0;1;1"/></text>
<text x="540" y="406" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043" opacity="0">平均 EV -2.2 → 露出 ×0.823<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6443;0.6444;1.0000" values="0;0;1;1"/></text>
<text x="50" y="450" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">暗がりの見え方:</text>
<text x="170" y="450" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed" opacity="0">単純平均 → 画面の明るさ 0.18(つぶれる)/ ヒストグラム → 0.45(見える)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7154;0.7156;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">窓の外は明るすぎて、平均を引っぱってしまう<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画素を明るさ(EV)ごとのビンに数える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.5020;0.5022;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">暗すぎる画素と、明るすぎる画素を、捨てる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5022;0.5820;0.5822;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">残りの平均が、目に見えてほしい明るさ → 露出が決まる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5820;0.5822;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:auto-exposure-histogram:end -->

### 外れ値を除いて平均を取る

ヒストグラムの下位 10〜40 %（暗い部分）・上位 5〜10 %（明るい部分）を除いた範囲で加重平均します。太陽・暗い隅・黒い UI の影響を抑えられます。

```hlsl
float AverageLogLuminance(float low_percent, float high_percent) {
  float total = 0.0;
  for (uint i = 1; i < HISTOGRAM_BINS; ++i) total += histogram[i];
  float low = total * low_percent;
  float high = total * high_percent;
  float accum = 0.0, sum = 0.0, weight = 0.0;
  for (uint j = 1; j < HISTOGRAM_BINS; ++j) {
    float count = histogram[j];
    float start = accum;
    float end = accum + count;
    float inside = max(0.0, min(end, high) - max(start, low));
    float log_lum = min_log_luminance + (float(j - 1) / 254.0) / inverse_log_luminance_range;
    sum += inside * log_lum;
    weight += inside;
    accum = end;
  }
  return exp2(sum / max(weight, 1.0));
}
```

## ② 目標の露出を決める

<strong>平均輝度を「中間灰」（約 0.18）にするよう</strong>、EV を決めます。

<div class="formula">露出 = キー値 / 平均輝度　（キー値 ≒ 0.18）</div>

```hlsl
float TargetExposure(float avg_luminance, float key_value, float compensation_ev, float min_ev, float max_ev) {
  float ev = log2(max(avg_luminance, 1e-4) / key_value);
  ev = clamp(ev, min_ev, max_ev) - compensation_ev;
  return exp2(-ev);
}
```

露出を決めるコードの要点です。キー値 0.18 は、中間灰を画面の平均的な明るさにする値で、写真の標準です。0.1〜0.3 で明暗のトーンが変わります。最小・最大 EV は、極端な暗所や明所で暴走しないようにする上下限です。補正 EV で、画作りに合わせて全体を明るく・暗くします。

## ③ 時間で追従する

<strong>目標が決まっても一気に変えず、時間をかけて近づけます</strong>。

```hlsl
float AdaptExposure(float current, float target, float delta_time, float speed_up, float speed_down) {
  float speed = (target < current) ? speed_up : speed_down;
  return current + (target - current) * (1.0 - exp(-delta_time * speed));
}
```

<!-- fig:auto-exposure-adapt:begin -->

<svg class="fig illust motion" data-fig="auto-exposure-adapt" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-auto-exposure-adapt" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">自動露出の適応: 急に明るくなっても、露出はゆっくり追いかける(目の慣れ)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">部屋(明るさ 0.2)から、外(明るさ 8)へ出て、また戻る。露出が追いつく速さ(慣れの速さ)を 3 通りで比べる</text>
<rect x="30" y="96" width="900" height="200" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 画面に出る明るさ(1.0 = 白飛び)</text>
<line x1="70.0" y1="146.0" x2="890.0" y2="146.0" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="890.0" y="142.0" text-anchor="end" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
<rect x="252.22" y="100" width="318.89" height="190" fill="#fde68a" fill-opacity="0.25"/>
<text x="260.2222222222222" y="118" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">外へ出る(明るさ 0.2 → 8)</text>
<path d="M70.0,252.6 L79.11,252.6 L88.22,252.6 L97.33,252.6 L106.44,252.6 L115.56,252.6 L124.67,252.6 L133.78,252.6 L142.89,252.6 L152.0,252.6 L161.11,252.6 L170.22,252.6 L179.33,252.6 L188.44,252.6 L197.56,252.6 L206.67,252.6 L215.78,252.6 L224.89,252.6 L234.0,252.6 L243.11,252.6 L252.22,146.0 L261.33,146.0 L270.44,146.0 L279.56,146.0 L288.67,195.86 L297.78,223.47 L306.89,237.64 L316.0,244.92 L325.11,248.66 L334.22,250.58 L343.33,251.56 L352.44,252.07 L361.56,252.33 L370.67,252.46 L379.78,252.53 L388.89,252.56 L398.0,252.58 L407.11,252.59 L416.22,252.59 L425.33,252.6 L434.44,252.6 L443.56,252.6 L452.67,252.6 L461.78,252.6 L470.89,252.6 L480.0,252.6 L489.11,252.6 L498.22,252.6 L507.33,252.6 L516.44,252.6 L525.56,252.6 L534.67,252.6 L543.78,252.6 L552.89,252.6 L562.0,252.6 L571.11,273.02 L580.22,263.08 L589.33,257.98 L598.44,255.36 L607.56,254.02 L616.67,253.33 L625.78,252.97 L634.89,252.79 L644.0,252.7 L653.11,252.65 L662.22,252.63 L671.33,252.61 L680.44,252.61 L689.56,252.6 L698.67,252.6 L707.78,252.6 L716.89,252.6 L726.0,252.6 L735.11,252.6 L744.22,252.6 L753.33,252.6 L762.44,252.6 L771.56,252.6 L780.67,252.6 L789.78,252.6 L798.89,252.6 L808.0,252.6 L817.11,252.6 L826.22,252.6 L835.33,252.6 L844.44,252.6 L853.56,252.6 L862.67,252.6 L871.78,252.6 L880.89,252.6 L890.0,252.6" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/></path>
<text x="80" y="130" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">速い(τ = 0.3 秒): 戻るまで 1.2 秒、最大 6.5<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,252.6 L79.11,252.6 L88.22,252.6 L97.33,252.6 L106.44,252.6 L115.56,252.6 L124.67,252.6 L133.78,252.6 L142.89,252.6 L152.0,252.6 L161.11,252.6 L170.22,252.6 L179.33,252.6 L188.44,252.6 L197.56,252.6 L206.67,252.6 L215.78,252.6 L224.89,252.6 L234.0,252.6 L243.11,252.6 L252.22,146.0 L261.33,146.0 L270.44,146.0 L279.56,146.0 L288.67,146.0 L297.78,146.0 L306.89,146.0 L316.0,146.0 L325.11,146.0 L334.22,146.0 L343.33,146.0 L352.44,154.8 L361.56,172.52 L370.67,187.04 L379.78,198.92 L388.89,208.65 L398.0,216.62 L407.11,223.14 L416.22,228.48 L425.33,232.85 L434.44,236.43 L443.56,239.36 L452.67,241.76 L461.78,243.73 L470.89,245.34 L480.0,246.65 L489.11,247.73 L498.22,248.61 L507.33,249.34 L516.44,249.93 L525.56,250.41 L534.67,250.81 L543.78,251.13 L552.89,251.4 L562.0,251.62 L571.11,274.65 L580.22,270.65 L589.33,267.38 L598.44,264.7 L607.56,262.51 L616.67,260.71 L625.78,259.24 L634.89,258.04 L644.0,257.05 L653.11,256.24 L662.22,255.58 L671.33,255.04 L680.44,254.6 L689.56,254.24 L698.67,253.94 L707.78,253.7 L716.89,253.5 L726.0,253.34 L735.11,253.2 L744.22,253.09 L753.33,253.0 L762.44,252.93 L771.56,252.87 L780.67,252.82 L789.78,252.78 L798.89,252.75 L808.0,252.72 L817.11,252.7 L826.22,252.68 L835.33,252.67 L844.44,252.65 L853.56,252.64 L862.67,252.64 L871.78,252.63 L880.89,252.62 L890.0,252.62" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;1.0000" values="0;0;1;1"/></path>
<text x="80" y="150" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">ふつう(τ = 1 秒): 戻るまで 4.2 秒、最大 7.0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,252.6 L79.11,252.6 L88.22,252.6 L97.33,252.6 L106.44,252.6 L115.56,252.6 L124.67,252.6 L133.78,252.6 L142.89,252.6 L152.0,252.6 L161.11,252.6 L170.22,252.6 L179.33,252.6 L188.44,252.6 L197.56,252.6 L206.67,252.6 L215.78,252.6 L224.89,252.6 L234.0,252.6 L243.11,252.6 L252.22,146.0 L261.33,146.0 L270.44,146.0 L279.56,146.0 L288.67,146.0 L297.78,146.0 L306.89,146.0 L316.0,146.0 L325.11,146.0 L334.22,146.0 L343.33,146.0 L352.44,146.0 L361.56,146.0 L370.67,146.0 L379.78,146.0 L388.89,146.0 L398.0,146.0 L407.11,146.0 L416.22,146.0 L425.33,146.0 L434.44,146.0 L443.56,146.0 L452.67,146.0 L461.78,146.0 L470.89,146.0 L480.0,146.0 L489.11,146.0 L498.22,146.0 L507.33,146.0 L516.44,146.0 L525.56,146.0 L534.67,146.0 L543.78,146.0 L552.89,152.6 L562.0,159.05 L571.11,272.97 L580.22,271.66 L589.33,270.43 L598.44,269.28 L607.56,268.21 L616.67,267.2 L625.78,266.26 L634.89,265.38 L644.0,264.55 L653.11,263.78 L662.22,263.06 L671.33,262.39 L680.44,261.76 L689.56,261.16 L698.67,260.61 L707.78,260.1 L716.89,259.61 L726.0,259.16 L735.11,258.74 L744.22,258.34 L753.33,257.97 L762.44,257.62 L771.56,257.3 L780.67,257.0 L789.78,256.71 L798.89,256.45 L808.0,256.2 L817.11,255.97 L826.22,255.75 L835.33,255.55 L844.44,255.36 L853.56,255.18 L862.67,255.01 L871.78,254.86 L880.89,254.71 L890.0,254.58" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4679;0.4681;1.0000" values="0;0;1;1"/></path>
<text x="80" y="170" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb" opacity="0">ゆっくり(τ = 3 秒): 戻るまで 7.0 秒、最大 7.1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4679;0.4681;1.0000" values="0;0;1;1"/></text>
<rect x="30" y="316" width="900" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="306" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 露出の値(小さい = 絞っている)</text>
<path d="M70.0,350.0 L79.11,350.0 L88.22,350.0 L97.33,350.0 L106.44,350.0 L115.56,350.0 L124.67,350.0 L133.78,350.0 L142.89,350.0 L152.0,350.0 L161.11,350.0 L170.22,350.0 L179.33,350.0 L188.44,350.0 L197.56,350.0 L206.67,350.0 L215.78,350.0 L224.89,350.0 L234.0,350.0 L243.11,350.0 L252.22,352.93 L261.33,370.3 L270.44,387.05 L279.56,402.71 L288.67,416.63 L297.78,428.08 L306.89,436.6 L316.0,442.31 L325.11,445.78 L334.22,447.75 L343.33,448.82 L352.44,449.39 L361.56,449.68 L370.67,449.84 L379.78,449.92 L388.89,449.96 L398.0,449.98 L407.11,449.99 L416.22,449.99 L425.33,450.0 L434.44,450.0 L443.56,450.0 L452.67,450.0 L461.78,450.0 L470.89,450.0 L480.0,450.0 L489.11,450.0 L498.22,450.0 L507.33,450.0 L516.44,450.0 L525.56,450.0 L534.67,450.0 L543.78,450.0 L552.89,450.0 L562.0,450.0 L571.11,405.83 L580.22,366.11 L589.33,357.08 L598.44,353.41 L607.56,351.7 L616.67,350.86 L625.78,350.44 L634.89,350.22 L644.0,350.11 L653.11,350.06 L662.22,350.03 L671.33,350.02 L680.44,350.01 L689.56,350.0 L698.67,350.0 L707.78,350.0 L716.89,350.0 L726.0,350.0 L735.11,350.0 L744.22,350.0 L753.33,350.0 L762.44,350.0 L771.56,350.0 L780.67,350.0 L789.78,350.0 L798.89,350.0 L808.0,350.0 L817.11,350.0 L826.22,350.0 L835.33,350.0 L844.44,350.0 L853.56,350.0 L862.67,350.0 L871.78,350.0 L880.89,350.0 L890.0,350.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/></path>
<path d="M70.0,350.0 L79.11,350.0 L88.22,350.0 L97.33,350.0 L106.44,350.0 L115.56,350.0 L124.67,350.0 L133.78,350.0 L142.89,350.0 L152.0,350.0 L161.11,350.0 L170.22,350.0 L179.33,350.0 L188.44,350.0 L197.56,350.0 L206.67,350.0 L215.78,350.0 L224.89,350.0 L234.0,350.0 L243.11,350.0 L252.22,350.88 L261.33,356.15 L270.44,361.38 L279.56,366.58 L288.67,371.72 L297.78,376.81 L306.89,381.83 L316.0,386.77 L325.11,391.62 L334.22,396.35 L343.33,400.96 L352.44,405.41 L361.56,409.7 L370.67,413.8 L379.78,417.69 L388.89,421.34 L398.0,424.76 L407.11,427.91 L416.22,430.8 L425.33,433.41 L434.44,435.76 L443.56,437.85 L452.67,439.68 L461.78,441.29 L470.89,442.67 L480.0,443.86 L489.11,444.88 L498.22,445.74 L507.33,446.46 L516.44,447.07 L525.56,447.58 L534.67,448.0 L543.78,448.35 L552.89,448.64 L562.0,448.88 L571.11,427.27 L580.22,390.0 L589.33,377.07 L598.44,369.73 L607.56,364.92 L616.67,361.54 L625.78,359.05 L634.89,357.17 L644.0,355.72 L653.11,354.59 L662.22,353.7 L671.33,352.99 L680.44,352.42 L689.56,351.97 L698.67,351.6 L707.78,351.3 L716.89,351.06 L726.0,350.87 L735.11,350.71 L744.22,350.58 L753.33,350.47 L762.44,350.39 L771.56,350.32 L780.67,350.26 L789.78,350.21 L798.89,350.17 L808.0,350.14 L817.11,350.12 L826.22,350.09 L835.33,350.08 L844.44,350.06 L853.56,350.05 L862.67,350.04 L871.78,350.03 L880.89,350.03 L890.0,350.02" fill="none" stroke="#2ea043" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;1.0000" values="0;0;1;1"/></path>
<path d="M70.0,350.0 L79.11,350.0 L88.22,350.0 L97.33,350.0 L106.44,350.0 L115.56,350.0 L124.67,350.0 L133.78,350.0 L142.89,350.0 L152.0,350.0 L161.11,350.0 L170.22,350.0 L179.33,350.0 L188.44,350.0 L197.56,350.0 L206.67,350.0 L215.78,350.0 L224.89,350.0 L234.0,350.0 L243.11,350.0 L252.22,350.29 L261.33,352.05 L270.44,353.81 L279.56,355.56 L288.67,357.31 L297.78,359.06 L306.89,360.8 L316.0,362.54 L325.11,364.27 L334.22,366.0 L343.33,367.72 L352.44,369.44 L361.56,371.15 L370.67,372.86 L379.78,374.56 L388.89,376.25 L398.0,377.93 L407.11,379.61 L416.22,381.28 L425.33,382.94 L434.44,384.59 L443.56,386.23 L452.67,387.86 L461.78,389.48 L470.89,391.09 L480.0,392.68 L489.11,394.26 L498.22,395.83 L507.33,397.39 L516.44,398.93 L525.56,400.45 L534.67,401.96 L543.78,403.45 L552.89,404.93 L562.0,406.38 L571.11,405.46 L580.22,395.68 L589.33,388.92 L598.44,383.83 L607.56,379.8 L616.67,376.51 L625.78,373.75 L634.89,371.41 L644.0,369.38 L653.11,367.62 L662.22,366.06 L671.33,364.68 L680.44,363.45 L689.56,362.35 L698.67,361.36 L707.78,360.47 L716.89,359.66 L726.0,358.92 L735.11,358.25 L744.22,357.63 L753.33,357.07 L762.44,356.55 L771.56,356.08 L780.67,355.64 L789.78,355.24 L798.89,354.87 L808.0,354.53 L817.11,354.21 L826.22,353.92 L835.33,353.65 L844.44,353.4 L853.56,353.17 L862.67,352.95 L871.78,352.75 L880.89,352.56 L890.0,352.39" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4679;0.4681;1.0000" values="0;0;1;1"/></path>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6807;0.6809;1.0000" values="0;0;1;1"/><rect x="520" y="330" width="400" height="130" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="536" y="354" text-anchor="start" style="font-size:13px;font-weight:700;fill:#991b1b">速い: すぐ慣れるが、急に画面が変わって不自然</text>
<text x="536" y="376" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1e3a8a">ゆっくり: 長い間、白飛び(最大 7.1)</text>
<text x="536" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">ふつう: 戻るまで 4.2 秒</text>
<text x="536" y="421" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">明るい所へは速く、暗い所へは遅く、が自然(目と同じ)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">露出は、毎フレーム、目標の明るさへ、少しだけ近づける(指数関数的に)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">τ(慣れの時間)が小さいほど、速く追いつく<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;0.6807;0.6809;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">適正な速さは、ゲームの演出で決める<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6807;0.6809;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:auto-exposure-adapt:end -->

| 点 | 説明 |
| --- | --- |
| `1 − exp(−dt · speed)` | フレームレートに依存せず、同じ時間で同じだけ近づく |
| 速度の差 | 暗くなる（露出が上がる）のはゆっくり（目の暗順応は遅い）。明るくなる（露出が下がる）のは速く |
| 典型の速度 | 明るくなるとき 約 3〜5 /秒、暗くなるとき 約 1〜2 /秒 |
| EV の空間で補間 | 露出の倍率ではなく、EV（対数）の値を補間すると自然 |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| ヒストグラムを使う | 外れ値を除き、頑健にする |
| 中心重み・領域の重み | 画面中心やプレイヤー周辺を重視 |
| エリアごとの EV を併用 | 屋内外の境でデザイナーが補正を指定（自動だけに頼らない） |
| EV の範囲を決める | シーンの最小・最大の明るさに合わせて制限 |
| 前フレームの値で計算 | GPU から CPU への読み戻しを避け、露出の値を GPU に置いたまま使う（1 フレーム遅れでよい） |
| シーン切り替えで即時リセット | カットやロード後は、追従を飛ばして目標値へ |
| UI は露出の外 | UI は露出・トーンマップの後に描く（UI の明るさが変わらない） |

## よくあるミス

??? failure "太陽が画面に入ると、全体が暗くなる"
    <strong>単純平均</strong>になっている。対数平均・ヒストグラム（上位を除く）・中心重みを使う。

??? failure "フレームごとに露出がちらつく"
    追従が無い、または速すぎる。指数的な追従にし、ヒストグラムで安定させる。

??? failure "フレームレートによって、順応の速さが変わる"
    `dt` を使わずに一定の割合で補間している。`1 − exp(−dt · speed)` にする。

??? failure "カットシーンの切り替えで、露出が遅れて、真っ白が数秒続く"
    カット時に露出を目標値へ即時ジャンプさせる。

??? failure "GPU の結果を CPU へ読み戻して、パイプラインが止まる"
    露出は GPU のバッファのまま、シェーダーが読む。CPU は触らない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自動露出 ＝ <strong>測る（対数平均・ヒストグラム）→ 目標露出 → 指数的に追従</strong>
    - [x] 対数平均とヒストグラムの外れ値除外で太陽に引きずられない
    - [x] キー値 0.18で中間灰を平均に。EV の範囲を制限
    - [x] 追従は `1 − exp(−dt · speed)`。暗くなるほうが遅い
    - [x] 読み戻しを避け、カットでリセット

## 参考

- Reinhard et al., "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）
- Pattanaik et al., "Time-Dependent Visual Adaptation for Fast Realistic Image Display"（SIGGRAPH 2000）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering"（SIGGRAPH 2014）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Exposure](exposure.md)
- [Gamma and HDR Output](gamma-srgb.md)
- [Bloom](../bloom/index.md)
