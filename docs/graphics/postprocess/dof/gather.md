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

<svg class="fig illust motion" data-fig="dof-gather-weight" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dof-gather-weight" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ギャザーの重み: ピントが合っている画素の色を、ぼけた画素に混ぜない(にじみを防ぐ)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">左 24 画素は、ピントの合った赤い物(CoC 0)。右は、ぼけた青い背景(CoC 4)。境目のぼけた側の画素は、周りを集めてぼかす</text>
<text x="60.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">入力(CoC を数字で示す: 0 = ピントが合っている)</text>
<rect x="60.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="78.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="96.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="114.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="132.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="150.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="168.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="186.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="204.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="222.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="240.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="258.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="276.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="294.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="312.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="330.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="348.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="366.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="384.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="402.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="420.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="438.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="456.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="474.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e63333"/></rect>
<rect x="492.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="510.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="528.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="546.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="564.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="582.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="600.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="618.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="636.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="654.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="672.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="690.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="708.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="726.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="744.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="762.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="780.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="798.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="816.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="834.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="852.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="870.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="888.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="906.0" y="112.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3366f2"/></rect>
<rect x="60.0" y="112" width="864.0" height="18.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="186" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">そのまま集める(境目で、赤がにじむ)</text>
<rect x="60.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#e63333"/></rect>
<rect x="78.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0689" values="#e5e7eb;#e63333"/></rect>
<rect x="96.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#e63333"/></rect>
<rect x="114.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0733" values="#e5e7eb;#e63333"/></rect>
<rect x="132.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#e63333"/></rect>
<rect x="150.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0778" values="#e5e7eb;#e63333"/></rect>
<rect x="168.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#e63333"/></rect>
<rect x="186.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0822" values="#e5e7eb;#e63333"/></rect>
<rect x="204.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#e63333"/></rect>
<rect x="222.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867" values="#e5e7eb;#e63333"/></rect>
<rect x="240.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#e63333"/></rect>
<rect x="258.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911" values="#e5e7eb;#e63333"/></rect>
<rect x="276.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#e63333"/></rect>
<rect x="294.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956" values="#e5e7eb;#e63333"/></rect>
<rect x="312.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#e63333"/></rect>
<rect x="330.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000" values="#e5e7eb;#e63333"/></rect>
<rect x="348.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#e63333"/></rect>
<rect x="366.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044" values="#e5e7eb;#e63333"/></rect>
<rect x="384.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067" values="#e5e7eb;#e63333"/></rect>
<rect x="402.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1089" values="#e5e7eb;#e63333"/></rect>
<rect x="420.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#e63333"/></rect>
<rect x="438.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1133" values="#e5e7eb;#e63333"/></rect>
<rect x="456.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1156" values="#e5e7eb;#e63333"/></rect>
<rect x="474.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1178" values="#e5e7eb;#e63333"/></rect>
<rect x="492.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#824f9d"/></rect>
<rect x="510.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1222" values="#e5e7eb;#6e55b2"/></rect>
<rect x="528.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#e5e7eb;#5b5bc8"/></rect>
<rect x="546.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1267" values="#e5e7eb;#4760dd"/></rect>
<rect x="564.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#3366f2"/></rect>
<rect x="582.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#e5e7eb;#3366f2"/></rect>
<rect x="600.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#3366f2"/></rect>
<rect x="618.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1356" values="#e5e7eb;#3366f2"/></rect>
<rect x="636.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#3366f2"/></rect>
<rect x="654.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1400" values="#e5e7eb;#3366f2"/></rect>
<rect x="672.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1422" values="#e5e7eb;#3366f2"/></rect>
<rect x="690.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1444" values="#e5e7eb;#3366f2"/></rect>
<rect x="708.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#3366f2"/></rect>
<rect x="726.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1489" values="#e5e7eb;#3366f2"/></rect>
<rect x="744.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1511" values="#e5e7eb;#3366f2"/></rect>
<rect x="762.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1533" values="#e5e7eb;#3366f2"/></rect>
<rect x="780.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1556" values="#e5e7eb;#3366f2"/></rect>
<rect x="798.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1578" values="#e5e7eb;#3366f2"/></rect>
<rect x="816.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#3366f2"/></rect>
<rect x="834.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1622" values="#e5e7eb;#3366f2"/></rect>
<rect x="852.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1644" values="#e5e7eb;#3366f2"/></rect>
<rect x="870.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1667" values="#e5e7eb;#3366f2"/></rect>
<rect x="888.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1689" values="#e5e7eb;#3366f2"/></rect>
<rect x="906.0" y="190.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1711" values="#e5e7eb;#3366f2"/></rect>
<rect x="60.0" y="190" width="864.0" height="18.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="264" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">重みを付けて集める(ピントの合った画素は混ぜない)</text>
<rect x="60.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#e63333"/></rect>
<rect x="78.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2911" values="#e5e7eb;#e63333"/></rect>
<rect x="96.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#e63333"/></rect>
<rect x="114.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2956" values="#e5e7eb;#e63333"/></rect>
<rect x="132.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#e63333"/></rect>
<rect x="150.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3000" values="#e5e7eb;#e63333"/></rect>
<rect x="168.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#e5e7eb;#e63333"/></rect>
<rect x="186.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3044" values="#e5e7eb;#e63333"/></rect>
<rect x="204.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3067" values="#e5e7eb;#e63333"/></rect>
<rect x="222.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3089" values="#e5e7eb;#e63333"/></rect>
<rect x="240.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3111" values="#e5e7eb;#e63333"/></rect>
<rect x="258.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3133" values="#e5e7eb;#e63333"/></rect>
<rect x="276.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3156" values="#e5e7eb;#e63333"/></rect>
<rect x="294.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3178" values="#e5e7eb;#e63333"/></rect>
<rect x="312.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3200" values="#e5e7eb;#e63333"/></rect>
<rect x="330.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3222" values="#e5e7eb;#e63333"/></rect>
<rect x="348.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3244" values="#e5e7eb;#e63333"/></rect>
<rect x="366.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3267" values="#e5e7eb;#e63333"/></rect>
<rect x="384.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3289" values="#e5e7eb;#e63333"/></rect>
<rect x="402.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3311" values="#e5e7eb;#e63333"/></rect>
<rect x="420.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#e63333"/></rect>
<rect x="438.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3356" values="#e5e7eb;#e63333"/></rect>
<rect x="456.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3378" values="#e5e7eb;#e63333"/></rect>
<rect x="474.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3400" values="#e5e7eb;#e63333"/></rect>
<rect x="492.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3422" values="#e5e7eb;#3366f2"/></rect>
<rect x="510.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#3366f2"/></rect>
<rect x="528.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3467" values="#e5e7eb;#3366f2"/></rect>
<rect x="546.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3489" values="#e5e7eb;#3366f2"/></rect>
<rect x="564.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3511" values="#e5e7eb;#3366f2"/></rect>
<rect x="582.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#3366f2"/></rect>
<rect x="600.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556" values="#e5e7eb;#3366f2"/></rect>
<rect x="618.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3578" values="#e5e7eb;#3366f2"/></rect>
<rect x="636.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#3366f2"/></rect>
<rect x="654.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622" values="#e5e7eb;#3366f2"/></rect>
<rect x="672.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3644" values="#e5e7eb;#3366f2"/></rect>
<rect x="690.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3667" values="#e5e7eb;#3366f2"/></rect>
<rect x="708.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#e5e7eb;#3366f2"/></rect>
<rect x="726.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711" values="#e5e7eb;#3366f2"/></rect>
<rect x="744.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#3366f2"/></rect>
<rect x="762.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756" values="#e5e7eb;#3366f2"/></rect>
<rect x="780.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778" values="#e5e7eb;#3366f2"/></rect>
<rect x="798.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3800" values="#e5e7eb;#3366f2"/></rect>
<rect x="816.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3822" values="#e5e7eb;#3366f2"/></rect>
<rect x="834.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3844" values="#e5e7eb;#3366f2"/></rect>
<rect x="852.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3867" values="#e5e7eb;#3366f2"/></rect>
<rect x="870.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3889" values="#e5e7eb;#3366f2"/></rect>
<rect x="888.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3911" values="#e5e7eb;#3366f2"/></rect>
<rect x="906.0" y="268.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#3366f2"/></rect>
<rect x="60.0" y="268" width="864.0" height="18.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="69.0" y="148" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#64748b">CoC 0</text>
<text x="285.0" y="148" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#64748b">CoC 0</text>
<text x="501.0" y="148" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#64748b">CoC 4</text>
<text x="717.0" y="148" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#64748b">CoC 4</text>
<text x="915.0" y="148" text-anchor="middle" style="font-size:9px;font-weight:700;fill:#64748b">CoC 4</text>
<rect x="438.0" y="186" width="162.0" height="26" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5243;0.5244;1.0000" values="0;0;1;1"/></rect>
<text x="60.0" y="340" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">画素 26(CoC 4)が集める 9 画素のうち、赤い(ピントの合った)画素は 3 個<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5243;0.5244;1.0000" values="0;0;1;1"/></text>
<text x="60.0" y="366" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">そのまま: 赤 3 / 9 が混ざる → 青い背景が赤みを帯びる。重みを付けると、赤 0 / 9<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5243;0.5244;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5909;0.5911;1.0000" values="0;0;1;1"/><rect x="60" y="400" width="860" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="76" y="424" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">赤のにじみ(境目から 8 画素の、赤成分の合計): そのまま 0.78 → 重み付き 0.00</text>
<text x="76" y="448" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">集める画素に、その画素自身の CoC を見て、「自分のぼけがここまで届く」ときだけ、混ぜる</text>
<text x="76" y="470" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ピントの合った物の輪郭が、ぼけた背景に、にじまなくなる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ぼけた画素は、周りを集めて平均する<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">そのまま集めると、ピントの合った画素の色が、混ざってにじむ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2887;0.2889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">各画素の CoC を見て、重みを付けると、混ざらない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;0.5909;0.5911;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ピントの合った物の輪郭が、くっきり残る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5909;0.5911;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
| **前景と背景を分ける** | **前景のにじみを正しく**（[Foreground and Background](near-far.md)） |
| **ボケの形に合わせた配置** | **多角形のボケ**（[Bokeh Shape](bokeh-shape.md)） |
| **ブルームと併用** | **明るい点が大きなボケの円盤になる**（[Scatter Method](scatter.md)の簡易版） |

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
