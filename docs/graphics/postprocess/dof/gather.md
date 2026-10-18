---
title: Gather Method
tags:
  - 描画
---

# Gather Method

<strong>ギャザー（Gather）</strong>は、<strong>「各画素が自分の周りの画素を集めて平均する」</strong>方式の DOF です。**出力の画素ごとに、CoC の半径の円の中のサンプルを読み**、**加重平均**します。**実装が簡単で、GPU に向いていて速い**ので、**現代のゲームの標準**です。このページでは、**基本の考え方・サンプルの配置（ヴォーゲル螺旋）・「他の画素の CoC」を考慮した重み・ちらつきの対策・半解像度・コスト**を説明します。

!!! tip "ポイント"
    - ギャザー ＝ <strong>各出力画素が、周りの画素を CoC の半径で集めて平均する</strong>。
    - サンプルは<strong>円盤状に散らす</strong>（<strong>ヴォーゲル螺旋・ポアソン円盤</strong>）。<strong>16〜64 サンプル</strong>が目安。
    - <strong>重要</strong>：<strong>集める相手の CoC も見る</strong>。<strong>相手のボケが自分に届かないなら、混ぜない</strong>（<strong>ピント内の物にぼけた背景がにじむ</strong>のを防ぐ）。
    - <strong>半解像度</strong>で行い、<strong>フル解像度に合成</strong>すると<strong>コストが 1/4</strong>。
    - <strong>ノイズ的なサンプルの回転</strong>＋<strong>ぼかし</strong>で、<strong>サンプル数が少なくても滑らか</strong>。
    - <strong>前景は別処理</strong>（[Foreground and Background](near-far.md)）。

## 基本の考え方

**出力画素 P の CoC が R 画素なら、P を中心に半径 R の円内の画素を、集めて平均**します。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="ギャザー">
<text x="20" y="26" class="fig-title">ギャザー：出力画素が、周りを集める</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="220" height="180" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="110" cy="90" r="64" fill="#2563eb" fill-opacity="0.12" stroke="#2563eb" stroke-width="2" stroke-dasharray="5 4"/>
<circle cx="110" cy="90" r="7" fill="#e5484d"/><text x="122" y="86" style="font-size:12px">P（出力）</text>
<g fill="#2563eb"><circle cx="70" cy="60" r="4"/><circle cx="150" cy="62" r="4"/><circle cx="90" cy="130" r="4"/><circle cx="140" cy="120" r="4"/><circle cx="60" cy="100" r="4"/><circle cx="160" cy="95" r="4"/><circle cx="110" cy="45" r="4"/><circle cx="105" cy="140" r="4"/></g>
<text x="0" y="200" style="font-size:12px">P の CoC の円の中のサンプルを集める</text>
</g>
<g font-size="13"><text x="320" y="86" style="font-weight:700">手順</text>
<text x="320" y="112">① P の CoC（半径 R）を読む</text>
<text x="320" y="136">② 半径 R の円盤状に N 個のサンプル</text>
<text x="320" y="160">③ 各サンプルの色を、重み付きで平均</text>
<text x="320" y="196" style="font-weight:700">重み：サンプルの CoC が P まで届くか</text></g>
</svg>

## ヴォーゲル螺旋でサンプルを散らす

**円盤の中に均等に近い配置**で**サンプルを置く**には、<strong>ヴォーゲル螺旋（黄金角）</strong>が**簡単**です。

```hlsl
static const float kGoldenAngle = 2.39996323;

float2 VogelDisk(int index, int count, float phi) {
  float r = sqrt((index + 0.5) / count);
  float theta = index * kGoldenAngle + phi;
  return float2(r * cos(theta), r * sin(theta));
}
```

螺旋サンプルのコードの要点です。`sqrt((i+0.5)/N)` は、円盤の面積が均等になる半径を与えます。黄金角（約 2.4 rad）で、サンプルが重ならず偏らず散ります。`phi` を画素ごとにランダムに回して、縞をノイズに変えます。

## ギャザーの実装

```hlsl
Texture2D<float4> color_coc : register(t0);

float4 DofGather(float2 uv, float2 texel, float phi) {
  float4 center = color_coc.SampleLevel(linear_clamp, uv, 0);
  float center_coc = abs(center.a);
  float3 sum = center.rgb;
  float weight_sum = 1.0;

  const int kSamples = 32;
  for (int i = 0; i < kSamples; ++i) {
    float2 offset = VogelDisk(i, kSamples, phi) * center_coc;
    float2 sample_uv = uv + offset * texel;
    float4 s = color_coc.SampleLevel(linear_clamp, sample_uv, 0);
    float sample_coc = abs(s.a);
    float distance_in_pixels = length(offset);
    float w = saturate(sample_coc - distance_in_pixels + 1.0);
    sum += s.rgb * w;
    weight_sum += w;
  }
  return float4(sum / weight_sum, center.a);
}
```

| 点 | 説明 |
| --- | --- |
| **`color_coc`** | **RGB に色、A に符号付き CoC**を**入れた画像** |
| **`offset = Vogel × center_coc`** | **自分の CoC の半径で、サンプル位置を決める** |
| **`w = saturate(sample_coc − 距離 + 1)`** | **サンプルの CoC が、自分までの距離以上なら、重みが大きい**（**その画素のボケが自分に届く**） |
| **中心を 1 つ足す** | **サンプルが 0 でも自分自身は残す** |

### なぜ、サンプルの CoC を見るのか

**自分の CoC だけで円内を平均する**と、**ピントが合った前景の物のすぐ後ろに、ぼけた背景があるとき**、**ピント内の物の輪郭に背景の色がにじんで**しまいます。**サンプル側の CoC を見て、そのサンプルのボケが自分まで届かないなら重みを 0 に**することで、**ピントが合った物の輪郭が保たれます**。

<!-- fig:dof-gather-weight:begin -->

<svg class="fig illust motion" data-fig="dof-gather-weight" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dof-gather-weight" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ギャザー:サンプル側の CoC を見て、重みを決める</text>
<text x="40" y="72" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">重みなし（全サンプルを同じ重み）</text>
<rect x="40" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="70" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="100" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="130" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="160" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="190" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="220" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="250" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="280" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="310" y="100" width="29" height="30" fill="#e5484d"/>
<rect x="340" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="370" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="400" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="430" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="460" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="490" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="520" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="550" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="580" y="100" width="29" height="30" fill="#2563eb"/>
<rect x="610" y="100" width="29" height="30" fill="#2563eb"/>
<text x="43" y="146" text-anchor="start" style="font-size:12px;font-weight:500;fill:#e5484d">前景（ピントが合う・CoC 0）</text>
<text x="343" y="146" text-anchor="start" style="font-size:12px;font-weight:500;fill:#2563eb">背景（ぼける・CoC 6）</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2367;0.2370;1.0000" values="0;0;1;1;0;0"/><rect x="369" y="97" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="205.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="235.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="265.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="295.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="325.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="355.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="100" width="70" height="30" fill="#6f59ae" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="146" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/><rect x="399" y="97" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="235.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="265.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="295.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="325.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="355.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="100" width="70" height="30" fill="#605bba" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="146" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.5627;0.5630;1.0000" values="0;0;1;1;0;0"/><rect x="429" y="97" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="265.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="295.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="325.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="355.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="625.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="100" width="70" height="30" fill="#515dc7" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="146" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;0.7256;0.7259;1.0000" values="0;0;1;1;0;0"/><rect x="459" y="97" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="295.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="325.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="355.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="625.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="100" width="70" height="30" fill="#455ed1" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="146" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7256;0.7259;0.8886;0.8889;1.0000" values="0;0;1;1;0;0"/><rect x="489" y="97" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="325.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="355.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="625.0" cy="115.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="100" width="70" height="30" fill="#3661dd" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="146" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<text x="40" y="242" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">サンプルの CoC を見る（届かないサンプルは重み 0）</text>
<rect x="40" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="70" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="100" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="130" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="160" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="190" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="220" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="250" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="280" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="310" y="270" width="29" height="30" fill="#e5484d"/>
<rect x="340" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="370" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="400" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="430" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="460" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="490" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="520" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="550" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="580" y="270" width="29" height="30" fill="#2563eb"/>
<rect x="610" y="270" width="29" height="30" fill="#2563eb"/>
<text x="43" y="316" text-anchor="start" style="font-size:12px;font-weight:500;fill:#e5484d">前景（ピントが合う・CoC 0）</text>
<text x="343" y="316" text-anchor="start" style="font-size:12px;font-weight:500;fill:#2563eb">背景（ぼける・CoC 6）</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2367;0.2370;1.0000" values="0;0;1;1;0;0"/><rect x="369" y="267" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="205.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="205.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="235.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="235.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="265.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="265.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="295.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="295.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="325.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="325.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="355.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="270" width="70" height="30" fill="#2563eb" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="316" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/><rect x="399" y="267" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="235.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="235.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="265.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="265.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="295.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="295.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="325.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="325.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="355.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="270" width="70" height="30" fill="#2563eb" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="316" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.5627;0.5630;1.0000" values="0;0;1;1;0;0"/><rect x="429" y="267" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="265.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="265.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="295.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="295.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="325.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="325.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="355.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="625.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="270" width="70" height="30" fill="#2563eb" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="316" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;0.7256;0.7259;1.0000" values="0;0;1;1;0;0"/><rect x="459" y="267" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="295.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="295.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="325.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="325.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="355.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="625.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="270" width="70" height="30" fill="#2563eb" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="316" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7256;0.7259;0.8886;0.8889;1.0000" values="0;0;1;1;0;0"/><rect x="489" y="267" width="31" height="35" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="325.0" cy="285.0" r="5" fill="#475569" stroke="#1f2937" stroke-width="1.5"/>
<text x="325.0" y="289.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">×</text>
<circle cx="355.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="385.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="415.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="445.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="475.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="505.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="535.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="565.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="595.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<circle cx="625.0" cy="285.0" r="5" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<rect x="654" y="270" width="70" height="30" fill="#2563eb" stroke="#94a3b8" stroke-width="2"/>
<text x="689" y="316" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">結果の色</text>
</g>
<text x="40" y="396" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">背景の画素（橙の枠）が、半径 6 の範囲を集めて平均する<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">枠が前景に近づくにつれ、前景の赤が背景に混ざる（上）。下は混ざらない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8886;0.8889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">→ 重みなしは前景の輪郭に背景/前景の色がにじむ。サンプルの CoC が届かなければ捨てる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8886;0.8889;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:dof-gather-weight:end -->

## ちらつきとノイズの扱い

**サンプル数が少ない**と**円盤が点の集まりに見えて、ざらつきます**。

| 対策 | 内容 |
| --- | --- |
| <strong>サンプルの回転（ノイズ）</strong> | **画素ごとに `phi` を変え、規則的な縞を細かいノイズに** |
| **ブルー ノイズ** | **ノイズの質が良く、後のぼかしで綺麗に消える** |
| **後処理のぼかし** | **ギャザーの後に、3×3 程度の小さなぼかし** |
| **サンプル数を CoC に応じて変える** | **ボケの小さい画素は、サンプルを減らす**（**半径 1 画素以下は、元のまま**） |
| **TAA で時間的に平均** | **毎フレーム `phi` を変え、TAA で滑らかに** |

## 半解像度で処理する

**ボケは低周波**なので**半解像度で計算して、フル解像度に戻して合成**しても、**見た目はほぼ変わりません**。**コストが 1/4**になります。

半解像度の手順は 3 段階です。色と CoC を半解像度にダウンサンプルします（CoC は重み付き平均）。半解像度でギャザーを行います。アップサンプルして、CoC に応じて元の絵と混ぜます（ボケが小さい所は元の絵を残します）。

## コスト

コストの目安です。サンプル数 32 で、1080p の半解像度なら約 0.3〜0.5 ms です。最大 CoC が大きいほど、サンプルの間隔が開いて、ノイズや粗さが出ます。帯域は、色と CoC の 8 バイト（FP16×4）の読み込みに、サンプル数を掛けた量です。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **サンプル側の CoC を使った重み** | **ピント内の輪郭を守る**（必須） |
| **ブルー ノイズで回転 ＋ TAA** | **少ないサンプルでも滑らか** |
| **半解像度 ＋ 合成** | **コストを 1/4** |
| **前景と背景を分ける** | **前景のにじみを正しく**（[前景と背景](near-far.md)） |
| **ボケの形に合わせた配置** | **多角形のボケ**（[ボケの形](bokeh-shape.md)） |
| **ブルームと併用** | **明るい点が大きなボケの円盤になる**（[スキャッター方式](scatter.md)の簡易版） |

## よくあるミス

??? failure "ピントが合った物の輪郭に、背景の色がにじむ"
    **サンプル側の CoC を重みに使っていない**。<strong>重みに「サンプルの CoC が自分まで届くか」</strong>を入れる。

??? failure "ボケが縞模様（同心円）になる"
    **サンプルが規則的**。<strong>画素ごとに回転（ノイズ）</strong>を入れる。

??? failure "CoC が大きい所で、サンプルが粗く、ざらざらする"
    **サンプル数を増やす**、**半解像度のぼかしを併用**、**最大 CoC を下げる**。

??? failure "前景がボケても、背景にしか効かず、輪郭がきつい"
    **前景を別に処理**し、**ぼけた前景が奥にも広がる**ようにする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ギャザー ＝ <strong>各画素が、CoC の半径で周りを集めて平均</strong>
    - [x] サンプルは<strong>ヴォーゲル螺旋 ＋ 画素ごとの回転</strong>
    - [x] <strong>サンプル側の CoC を見て重み付け</strong>（<strong>ピント内の輪郭を守る</strong>）
    - [x] <strong>半解像度</strong>で<strong>コスト 1/4</strong>
    - [x] <strong>前景は別処理</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Kleber & Hammon, "Bokeh depth of field"（解説）
- Kraus & Strengert, "Depth-of-Field Rendering by Pyramidal Image Processing"（2007）

## 関連ページ

- [Depth of Field (DOF)](index.md)
- [Circle of Confusion (CoC)](coc.md)
- [Scatter Method](scatter.md)
- [Foreground and Background](near-far.md)
- [Bokeh Shape](bokeh-shape.md)
