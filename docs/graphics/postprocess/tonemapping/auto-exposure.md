---
title: 自動露出
tags:
  - 描画
---

# 自動露出

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

| 方式 | 内容 | 特徴 |
| --- | --- | --- |
| <strong>縮小（ミップ チェーン）</strong> | **`log(L)` を 1×1 まで縮小**して平均 | **簡単・速い**。**外れ値の除外はできない** |
| **ヒストグラム** | **輝度を数十〜256 のビンに数える** | **外れ値を除ける**。**頑健** |
| **中心重み** | **画面中心を重くして平均** | **視線が中心にあると仮定** |

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

| 点 | 説明 |
| --- | --- |
| **共有メモリで先に集計** | **グループ内でまとめてから、グローバルへ足す**（**グローバルの原子操作を減らす**） |
| **ビン 0** | **ほぼ黒の画素を除外**するための専用ビン |
| **`log2` 空間** | **EV と同じ単位で等間隔**（**人間の知覚に合う**） |

<!-- fig:auto-exposure-histogram:begin -->
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

| 点 | 説明 |
| --- | --- |
| **キー値 0.18** | <strong>「中間灰」を、画面の平均的な明るさにする</strong>（**写真の標準**）。**0.1〜0.3 で明暗のトーンが変わる** |
| **最小・最大 EV** | **極端な暗所・明所で暴走しない**ようにする |
| **補正 EV** | **画作りに合わせて、全体を明るく・暗く** |

## ③ 時間で追従する

**目標が決まっても一気に変えず、時間をかけて近づけます**。

```hlsl
float AdaptExposure(float current, float target, float delta_time, float speed_up, float speed_down) {
  float speed = (target < current) ? speed_up : speed_down;
  return current + (target - current) * (1.0 - exp(-delta_time * speed));
}
```

<!-- fig:auto-exposure-adapt:begin -->
<!-- fig:auto-exposure-adapt:end -->

| 点 | 説明 |
| --- | --- |
| **`1 − exp(−dt · speed)`** | **フレームレートに依存せず、同じ時間で同じだけ近づく** |
| **速度の差** | **暗くなる（露出が上がる）のはゆっくり**（目の暗順応は遅い）。**明るくなる（露出が下がる）のは速く** |
| **典型の速度** | **明るくなるとき 約 3〜5 /秒、暗くなるとき 約 1〜2 /秒** |
| **EV の空間で補間** | **露出の倍率ではなく、EV（対数）の値を補間する**と**自然** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **ヒストグラムを使う** | **外れ値を除き、頑健**にする |
| **中心重み・領域の重み** | **画面中心やプレイヤー周辺を重視** |
| **エリアごとの EV を併用** | **屋内外の境でデザイナーが補正を指定**（**自動だけに頼らない**） |
| **EV の範囲を決める** | **シーンの最小・最大の明るさに合わせて制限** |
| **前フレームの値で計算** | **GPU から CPU への読み戻しを避け、露出の値を GPU に置いたまま使う**（**1 フレーム遅れでよい**） |
| **シーン切り替えで即時リセット** | **カットやロード後は、追従を飛ばして目標値へ** |
| **UI は露出の外** | **UI は露出・トーンマップの後に描く**（UI の明るさが変わらない） |

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

- [トーンマッピングと露出](index.md)
- [露出](exposure.md)
- [ガンマと HDR 出力](gamma-srgb.md)
- [ブルーム](../bloom/index.md)
