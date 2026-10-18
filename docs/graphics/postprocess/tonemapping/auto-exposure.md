---
title: Auto Exposure
tags:
  - 描画
---

# Auto Exposure

**暗い所から明るい所へ出ると、目が慣れるまでまぶしい**——この**明暗順応**を**再現**するのが<strong>自動露出（Eye Adaptation）</strong>です。**画面の明るさを測って、適切な露出を決め、時間をかけて追従**させます。**これがないと明るさが大きく変わるゲームでは、どこかで真っ白か真っ暗**になります。このページでは、**平均輝度の測り方（縮小・ヒストグラム）・外れ値の除外・目標露出の決め方・時間的な追従・仕上げの工夫**を説明します。

!!! tip "ポイント"
    - 自動露出 ＝ <strong>画面の明るさを測る → 目標露出を決める → 時間で追従する</strong>。
    - 明るさは<strong>対数平均（幾何平均）</strong>で測る。<strong>明るい点（太陽）に引きずられにくい</strong>。
    - <strong>ヒストグラム</strong>で<strong>外れ値を除く</strong>と<strong>頑健</strong>。<strong>縮小（ミップ）</strong>は<strong>簡単</strong>。
    - <strong>追従は指数的</strong>：<strong>`1 − exp(−dt · 速度)`</strong>。<strong>フレームレートに依らない</strong>。
    - <strong>明→暗は遅く、暗→明は速く</strong>（<strong>目は暗順応が遅い</strong>）。
    - <strong>最小・最大の EV を制限</strong>し、<strong>露出補正</strong>で画作りを残す。

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

**単純な平均は太陽のような非常に明るい点に引きずられて、シーン全体が暗くなります**。<strong>対数をとってから平均する（幾何平均）</strong>と、**外れ値の影響が小さくなります**。

<div class="formula">L_avg = exp( (1/N) · Σ log(L + ε) )</div>

平均輝度の求め方は 3 通りあります。<strong>縮小（ミップ チェーン）</strong>は、`log(L)` を 1×1 まで縮小して平均する方法で、簡単で速いですが、外れ値を除けません。<strong>ヒストグラム</strong>は、輝度を数十〜256 のビンに数えます。外れ値を除けて頑健です。<strong>中心重み</strong>は、画面中心を重くして平均する方法で、視線が中心にあると仮定します。

### 縮小で測る

```hlsl
float LogLuminance(float3 c) {
  return log(max(dot(c, float3(0.2126, 0.7152, 0.0722)), 1e-4));
}
```

**画面の `log(L)` を書いたテクスチャをミップで 1×1 まで縮小**し、**`exp` で戻す**と**対数平均**です。**実装が最も簡単**ですが**明るい点・暗い点が混ざる**ので**シーンによっては安定しません**。

### ヒストグラムで測る

**輝度を `log2` 空間で、等間隔のビンに数える**方式です。**各ビンのピクセル数をコンピュートで集計**します。

```hlsl
#define HISTOGRAM_BINS 256

RWStructuredBuffer<uint> histogram : register(u0);
Texture2D<float4> hdr_color : register(t0);

cbuffer HistogramConstants : register(b0) {
  uint2 size;
  float min_log_luminance;
  float inverse_log_luminance_range;
};

groupshared uint s_histogram[HISTOGRAM_BINS];

uint LuminanceToBin(float luminance) {
  if (luminance < 0.001) return 0;
  float log_luminance = saturate((log2(luminance) - min_log_luminance) * inverse_log_luminance_range);
  return uint(log_luminance * 254.0 + 1.0);
}

[numthreads(16, 16, 1)]
void HistogramMain(uint3 id : SV_DispatchThreadID, uint group_index : SV_GroupIndex) {
  s_histogram[group_index] = 0;
  GroupMemoryBarrierWithGroupSync();
  if (all(id.xy < size)) {
    float3 color = hdr_color.Load(int3(id.xy, 0)).rgb;
    uint bin = LuminanceToBin(dot(color, float3(0.2126, 0.7152, 0.0722)));
    InterlockedAdd(s_histogram[bin], 1);
  }
  GroupMemoryBarrierWithGroupSync();
  InterlockedAdd(histogram[group_index], s_histogram[group_index]);
}
```

ヒストグラムのコードの要点です。共有メモリで先にグループ内を集計してから、グローバルへ足します（グローバルの原子操作を減らすため）。ビン 0 は、ほぼ黒の画素を除外するための専用のビンです。`log2` 空間で数えるので、EV と同じ単位で等間隔になり、人間の知覚に合います。

<!-- fig:auto-exposure-histogram:begin -->

<svg class="fig illust motion" data-fig="auto-exposure-histogram" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-auto-exposure-histogram" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">輝度ヒストグラム:外れ値を除いて、平均の明るさを測る</text>
<rect x="50" y="70" width="520" height="230" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="50" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">画素数</text>
<text x="570" y="334" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">輝度（log2、右ほど明るい）</text>
<rect x="52.0" y="292.33" width="28.5" height="7.67" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0518;0.0522;1.0000" values="0;0;1;1"/></rect>
<text x="66.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-8</text>
<rect x="84.5" y="284.67" width="28.5" height="15.33" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0623;0.0626;1.0000" values="0;0;1;1"/></rect>
<text x="98.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-7</text>
<rect x="117.0" y="265.5" width="28.5" height="34.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0727;0.0730;1.0000" values="0;0;1;1"/></rect>
<text x="131.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-6</text>
<rect x="149.5" y="231.0" width="28.5" height="69.0" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0831;0.0835;1.0000" values="0;0;1;1"/></rect>
<text x="163.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-5</text>
<rect x="182.0" y="185.0" width="28.5" height="115.0" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0936;0.0939;1.0000" values="0;0;1;1"/></rect>
<text x="196.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-4</text>
<rect x="214.5" y="131.33" width="28.5" height="168.67" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1040;0.1043;1.0000" values="0;0;1;1"/></rect>
<text x="228.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-3</text>
<rect x="247.0" y="100.67" width="28.5" height="199.33" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1144;0.1148;1.0000" values="0;0;1;1"/></rect>
<text x="261.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-2</text>
<rect x="279.5" y="123.67" width="28.5" height="176.33" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1249;0.1252;1.0000" values="0;0;1;1"/></rect>
<text x="293.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">-1</text>
<rect x="312.0" y="185.0" width="28.5" height="115.0" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1353;0.1357;1.0000" values="0;0;1;1"/></rect>
<text x="326.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<rect x="344.5" y="238.67" width="28.5" height="61.33" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1457;0.1461;1.0000" values="0;0;1;1"/></rect>
<text x="358.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<rect x="377.0" y="269.33" width="28.5" height="30.67" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;1.0000" values="0;0;1;1"/></rect>
<text x="391.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2</text>
<rect x="409.5" y="280.83" width="28.5" height="19.17" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1666;0.1670;1.0000" values="0;0;1;1"/></rect>
<text x="423.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">3</text>
<rect x="442.0" y="288.5" width="28.5" height="11.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1770;0.1774;1.0000" values="0;0;1;1"/></rect>
<text x="456.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<rect x="474.5" y="292.33" width="28.5" height="7.67" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1875;0.1878;1.0000" values="0;0;1;1"/></rect>
<text x="488.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">5</text>
<rect x="507.0" y="288.5" width="28.5" height="11.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1979;0.1983;1.0000" values="0;0;1;1"/></rect>
<text x="521.25" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">6</text>
<rect x="539.5" y="265.5" width="28.5" height="34.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2083;0.2087;1.0000" values="0;0;1;1"/></rect>
<text x="553.75" y="316" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">7</text>
<rect x="147.5" y="70" width="325.0" height="230" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000" values="0;0;0.18;0.18"/></rect>
<line x1="147.5" y1="70" x2="147.5" y2="300" stroke="#e5aa28" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000" values="0;0;1;1"/></line>
<line x1="472.5" y1="70" x2="472.5" y2="300" stroke="#e5aa28" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000" values="0;0;1;1"/></line>
<text x="141.5" y="90" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">下位 10 %<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="478.5" y="90" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">上位 10 %<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000;1.0000" values="0;0;1;1;0"/></text>
<polygon points="270.41,296 261.41,318 279.41,318" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="0;0;1;1"/></polygon>
<text x="560" y="122" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">▲ 平均 log2 ≒ -1.2<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="50" y="372" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">① 画素を明るさの段（log2）ごとに数える<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000" values="1;1;0;0"/></text>
<text x="50" y="372" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">② 暗すぎ・明るすぎる 10 % ずつは除く（ランプ・暗闇に引っ張られない）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;0.4344;0.4348;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="372" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">③ 残りの平均を求める → 平均 log2 ≒ -1.2<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.6953;0.6957;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="372" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">④ 平均が 0 EV になるよう露出を +1.2 EV 補正する<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6953;0.6957;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:auto-exposure-histogram:end -->

### 外れ値を除いて平均を取る

**ヒストグラムの下位 10〜40 %（暗い部分）・上位 5〜10 %（明るい部分）を除いた範囲**で**加重平均**します。**太陽・暗い隅・黒い UI の影響を抑えられます**。

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

**平均輝度を「中間灰」（約 0.18）にするよう**、**EV を決めます**。

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

**目標が決まっても一気に変えず、時間をかけて近づけます**。

```hlsl
float AdaptExposure(float current, float target, float delta_time, float speed_up, float speed_down) {
  float speed = (target < current) ? speed_up : speed_down;
  return current + (target - current) * (1.0 - exp(-delta_time * speed));
}
```

<!-- fig:auto-exposure-adapt:begin -->

<svg class="fig illust motion" data-fig="auto-exposure-adapt" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-auto-exposure-adapt" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">時間で追従:暗い所から明るい所へ出ると、一瞬まぶしい</text>
<rect x="50" y="70" width="470" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="167.5" y1="70" x2="167.5" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="130.0" x2="520" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="285.0" y1="70" x2="285.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="520" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="402.5" y1="70" x2="402.5" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="250.0" x2="520" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="520" y="330" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">時間（秒）</text>
<path d="M50.0,293.33 L54.7,293.33 L59.4,293.33 L64.1,293.33 L68.8,293.33 L73.5,293.33 L78.2,293.33 L82.9,293.33 L87.6,293.33 L92.3,293.33 L97.0,293.33 L101.7,293.33 L106.4,293.33 L111.1,293.33 L115.8,293.33 L120.5,293.33 L125.2,293.33 L129.9,293.33 L134.6,293.33 L139.3,293.33 L144.0,110.0 L148.7,110.0 L153.4,110.0 L158.1,110.0 L162.8,110.0 L167.5,110.0 L172.2,110.0 L176.9,110.0 L181.6,110.0 L186.3,110.0 L191.0,110.0 L195.7,110.0 L200.4,110.0 L205.1,110.0 L209.8,110.0 L214.5,110.0 L219.2,110.0 L223.9,110.0 L228.6,110.0 L233.3,110.0 L238.0,110.0 L242.7,110.0 L247.4,110.0 L252.1,110.0 L256.8,110.0 L261.5,110.0 L266.2,110.0 L270.9,110.0 L275.6,110.0 L280.3,110.0 L285.0,110.0 L289.7,110.0 L294.4,110.0 L299.1,110.0 L303.8,110.0 L308.5,110.0 L313.2,110.0 L317.9,110.0 L322.6,110.0 L327.3,110.0 L332.0,110.0 L336.7,110.0 L341.4,110.0 L346.1,110.0 L350.8,110.0 L355.5,110.0 L360.2,110.0 L364.9,110.0 L369.6,110.0 L374.3,110.0 L379.0,110.0 L383.7,110.0 L388.4,110.0 L393.1,110.0 L397.8,110.0 L402.5,110.0 L407.2,110.0 L411.9,110.0 L416.6,110.0 L421.3,110.0 L426.0,110.0 L430.7,110.0 L435.4,110.0 L440.1,110.0 L444.8,110.0 L449.5,110.0 L454.2,110.0 L458.9,110.0 L463.6,110.0 L468.3,110.0 L473.0,110.0 L477.7,110.0 L482.4,110.0 L487.1,110.0 L491.8,110.0 L496.5,110.0 L501.2,110.0 L505.9,110.0 L510.6,110.0 L515.3,110.0 L520.0,110.0" fill="none" stroke="#64748b" stroke-width="3" stroke-dasharray="5 4"/>
<path d="M50.0,274.0 L54.7,274.0 L59.4,274.0 L64.1,274.0 L68.8,274.0 L73.5,274.0 L78.2,274.0 L82.9,274.0 L87.6,274.0 L92.3,274.0 L97.0,274.0 L101.7,274.0 L106.4,274.0 L111.1,274.0 L115.8,274.0 L120.5,274.0 L125.2,274.0 L129.9,274.0 L134.6,274.0 L139.3,274.0 L144.0,110.0 L148.7,110.0 L153.4,156.37 L158.1,190.09 L162.8,210.13 L167.5,223.36 L172.2,232.72 L176.9,239.66 L181.6,245.0 L186.3,249.21 L191.0,252.61 L195.7,255.4 L200.4,257.73 L205.1,259.69 L209.8,261.35 L214.5,262.78 L219.2,264.01 L223.9,265.08 L228.6,266.02 L233.3,266.85 L238.0,267.57 L242.7,268.21 L247.4,268.78 L252.1,269.29 L256.8,269.74 L261.5,270.15 L266.2,270.51 L270.9,270.84 L275.6,271.13 L280.3,271.4 L285.0,271.64 L289.7,271.85 L294.4,272.05 L299.1,272.22 L303.8,272.38 L308.5,272.53 L313.2,272.66 L317.9,272.78 L322.6,272.89 L327.3,272.99 L332.0,273.08 L336.7,273.16 L341.4,273.23 L346.1,273.3 L350.8,273.36 L355.5,273.42 L360.2,273.47 L364.9,273.51 L369.6,273.56 L374.3,273.59 L379.0,273.63 L383.7,273.66 L388.4,273.69 L393.1,273.72 L397.8,273.74 L402.5,273.76 L407.2,273.79 L411.9,273.8 L416.6,273.82 L421.3,273.84 L426.0,273.85 L430.7,273.86 L435.4,273.88 L440.1,273.89 L444.8,273.9 L449.5,273.9 L454.2,273.91 L458.9,273.92 L463.6,273.93 L468.3,273.93 L473.0,273.94 L477.7,273.94 L482.4,273.95 L487.1,273.95 L491.8,273.96 L496.5,273.96 L501.2,273.96 L505.9,273.97 L510.6,273.97 L515.3,273.97 L520.0,273.98" fill="none" stroke="#2563eb" stroke-width="4"/>
<text x="59.4" y="244.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">実際の明るさ（点線）</text>
<text x="162.8" y="102.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">画面の明るさ（青）</text>
<circle cx="50.0" cy="274.0" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0522;0.0600;0.0678;0.0757;0.0835;0.0913;0.0991;0.1070;0.1148;0.1226;0.1304;0.1383;0.1461;0.1539;0.1617;0.1696;0.1774;0.1852;0.1930;0.2009;0.2087;0.2165;0.2243;0.2322;0.2400;0.2478;0.2557;0.2635;0.2713;0.2791;0.2870;0.2948;0.3026;0.3104;0.3183;0.3261;0.3339;0.3417;0.3496;0.3574;0.3652;0.3730;0.3809;0.3887;0.3965;0.4043;0.4122;0.4200;0.4278;0.4357;0.4435;0.4513;0.4591;0.4670;0.4748;0.4826;0.4904;0.4983;0.5061;0.5139;0.5217;0.5296;0.5374;0.5452;0.5530;0.5609;0.5687;0.5765;0.5843;0.5922;0.6000;0.6078;0.6157;0.6235;0.6313;0.6391;0.6470;0.6548;0.6626;0.6704;0.6783;0.6861;0.6939;0.7017;0.7096;0.7174;0.7252;0.7330;0.7409;0.7487;0.7565;0.7643;0.7722;0.7800;0.7878;0.7957;0.8035;0.8113;0.8191;0.8270;0.8348;1.0000" values="50;50;54.7;59.4;64.1;68.8;73.5;78.2;82.9;87.6;92.3;97;101.7;106.4;111.1;115.8;120.5;125.2;129.9;134.6;139.3;144;148.7;153.4;158.1;162.8;167.5;172.2;176.9;181.6;186.3;191;195.7;200.4;205.1;209.8;214.5;219.2;223.9;228.6;233.3;238;242.7;247.4;252.1;256.8;261.5;266.2;270.9;275.6;280.3;285;289.7;294.4;299.1;303.8;308.5;313.2;317.9;322.6;327.3;332;336.7;341.4;346.1;350.8;355.5;360.2;364.9;369.6;374.3;379;383.7;388.4;393.1;397.8;402.5;407.2;411.9;416.6;421.3;426;430.7;435.4;440.1;444.8;449.5;454.2;458.9;463.6;468.3;473;477.7;482.4;487.1;491.8;496.5;501.2;505.9;510.6;515.3;520;520"/><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0522;0.0600;0.0678;0.0757;0.0835;0.0913;0.0991;0.1070;0.1148;0.1226;0.1304;0.1383;0.1461;0.1539;0.1617;0.1696;0.1774;0.1852;0.1930;0.2009;0.2087;0.2165;0.2243;0.2322;0.2400;0.2478;0.2557;0.2635;0.2713;0.2791;0.2870;0.2948;0.3026;0.3104;0.3183;0.3261;0.3339;0.3417;0.3496;0.3574;0.3652;0.3730;0.3809;0.3887;0.3965;0.4043;0.4122;0.4200;0.4278;0.4357;0.4435;0.4513;0.4591;0.4670;0.4748;0.4826;0.4904;0.4983;0.5061;0.5139;0.5217;0.5296;0.5374;0.5452;0.5530;0.5609;0.5687;0.5765;0.5843;0.5922;0.6000;0.6078;0.6157;0.6235;0.6313;0.6391;0.6470;0.6548;0.6626;0.6704;0.6783;0.6861;0.6939;0.7017;0.7096;0.7174;0.7252;0.7330;0.7409;0.7487;0.7565;0.7643;0.7722;0.7800;0.7878;0.7957;0.8035;0.8113;0.8191;0.8270;0.8348;1.0000" values="274;274;274;274;274;274;274;274;274;274;274;274;274;274;274;274;274;274;274;274;274;110;110;156.37;190.09;210.13;223.36;232.72;239.66;245;249.21;252.61;255.4;257.73;259.69;261.35;262.78;264.01;265.08;266.02;266.85;267.57;268.21;268.78;269.29;269.74;270.15;270.51;270.84;271.13;271.4;271.64;271.85;272.05;272.22;272.38;272.53;272.66;272.78;272.89;272.99;273.08;273.16;273.23;273.3;273.36;273.42;273.47;273.51;273.56;273.59;273.63;273.66;273.69;273.72;273.74;273.76;273.79;273.8;273.82;273.84;273.85;273.86;273.88;273.89;273.9;273.9;273.91;273.92;273.93;273.93;273.94;273.94;273.95;273.95;273.96;273.96;273.96;273.97;273.97;273.97;273.98;273.98"/></circle>
<rect x="555" y="90" width="170" height="110" fill="#757575" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0522;0.0600;0.0678;0.0757;0.0835;0.0913;0.0991;0.1070;0.1148;0.1226;0.1304;0.1383;0.1461;0.1539;0.1617;0.1696;0.1774;0.1852;0.1930;0.2009;0.2087;0.2165;0.2243;0.2322;0.2400;0.2478;0.2557;0.2635;0.2713;0.2791;0.2870;0.2948;0.3026;0.3104;0.3183;0.3261;0.3339;0.3417;0.3496;0.3574;0.3652;0.3730;0.3809;0.3887;0.3965;0.4043;0.4122;0.4200;0.4278;0.4357;0.4435;0.4513;0.4591;0.4670;0.4748;0.4826;0.4904;0.4983;0.5061;0.5139;0.5217;0.5296;0.5374;0.5452;0.5530;0.5609;0.5687;0.5765;0.5843;0.5922;0.6000;0.6078;0.6157;0.6235;0.6313;0.6391;0.6470;0.6548;0.6626;0.6704;0.6783;0.6861;0.6939;0.7017;0.7096;0.7174;0.7252;0.7330;0.7409;0.7487;0.7565;0.7643;0.7722;0.7800;0.7878;0.7957;0.8035;0.8113;0.8191;0.8270;0.8348;1.0000" values="#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#ffffff;#ffffff;#e2e2e2;#cacaca;#bababa;#aeaeae;#a6a6a6;#9f9f9f;#999999;#949494;#919191;#8d8d8d;#8b8b8b;#888888;#868686;#848484;#838383;#818181;#808080;#7f7f7f;#7e7e7e;#7d7d7d;#7c7c7c;#7c7c7c;#7b7b7b;#7a7a7a;#7a7a7a;#7a7a7a;#797979;#797979;#787878;#787878;#787878;#787878;#777777;#777777;#777777;#777777;#777777;#767676;#767676;#767676;#767676;#767676;#767676;#767676;#767676;#767676;#767676;#767676;#767676;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575;#757575"/></rect>
<text x="640" y="82" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">画面</text>
<text x="555" y="232" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">暗い部屋の中<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2083;0.2087;1.0000" values="1;1;0;0"/></text>
<text x="555" y="232" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">外へ出た!まぶしい<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2083;0.2087;0.3475;0.3478;1.0000" values="0;0;1;1;0;0"/></text>
<text x="555" y="232" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">目が慣れて、見やすくなる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3475;0.3478;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="555" y="256" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">露出が少しずつ下がる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3475;0.3478;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">追従の速さ(係数)で、慣れるまでの時間が決まる。明るい所への適応は速く、暗い所へは遅くする。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:auto-exposure-adapt:end -->

時間追従のコードの要点です。`1 − exp(−dt · speed)` は、フレームレートに依存せず、同じ時間で同じだけ近づく係数です。速度は、暗くなる（露出が上がる）のはゆっくり、明るくなる（露出が下がる）のは速くします。目の暗順応は遅いためです。典型的な速度は、明るくなるとき約 3〜5 /秒、暗くなるとき約 1〜2 /秒です。補間は、露出の倍率でなく、EV（対数）の値で行うと自然です。

## より良いやり方

より良いやり方を挙げます。ヒストグラムで外れ値を除き、頑健にします。中心重みや領域の重みで、画面中心やプレイヤー周辺を重視します。エリアごとの EV を併用し、屋内外の境でデザイナーが補正を指定します（自動だけに頼りません）。EV の範囲をシーンの最小・最大の明るさに合わせて制限します。前フレームの値で計算し、GPU から CPU への読み戻しを避けて、露出の値を GPU に置いたまま使います（1 フレーム遅れでかまいません）。シーン切り替え（カットやロード）の後は、追従を飛ばして目標値へ即時にリセットします。UI は露出・トーンマップの後に描き、UI の明るさが変わらないようにします。

## よくあるミス

??? failure "太陽が画面に入ると、全体が暗くなる"
    **単純平均**になっている。**対数平均・ヒストグラム（上位を除く）・中心重み**を使う。

??? failure "フレームごとに露出がちらつく"
    **追従が無い**、または**速すぎる**。**指数的な追従**にし、**ヒストグラムで安定**させる。

??? failure "フレームレートによって、順応の速さが変わる"
    **`dt` を使わずに一定の割合で補間**している。**`1 − exp(−dt · speed)`** にする。

??? failure "カットシーンの切り替えで、露出が遅れて、真っ白が数秒続く"
    **カット時に露出を目標値へ即時ジャンプ**させる。

??? failure "GPU の結果を CPU へ読み戻して、パイプラインが止まる"
    **露出は GPU のバッファのまま、シェーダーが読む**。**CPU は触らない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自動露出 ＝ <strong>測る（対数平均・ヒストグラム）→ 目標露出 → 指数的に追従</strong>
    - [x] <strong>対数平均</strong>と<strong>ヒストグラムの外れ値除外</strong>で<strong>太陽に引きずられない</strong>
    - [x] <strong>キー値 0.18</strong>で<strong>中間灰を平均に</strong>。<strong>EV の範囲を制限</strong>
    - [x] <strong>追従は `1 − exp(−dt · speed)`</strong>。<strong>暗くなるほうが遅い</strong>
    - [x] <strong>読み戻しを避け</strong>、<strong>カットでリセット</strong>

## 参考

- Reinhard et al., "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）
- Pattanaik et al., "Time-Dependent Visual Adaptation for Fast Realistic Image Display"（SIGGRAPH 2000）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering"（SIGGRAPH 2014）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Exposure](exposure.md)
- [Gamma and HDR Output](gamma-srgb.md)
- [Bloom](../bloom/index.md)
