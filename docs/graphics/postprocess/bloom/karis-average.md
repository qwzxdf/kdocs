---
title: ファイアフライ（Karis）
tags:
  - 描画
---

# ファイアフライ（Karis）

**ブルームを動かすと小さくて非常に明るい点（スペキュラのハイライト・小さな光源）が、画面の隅々で「ぴかぴか」と点滅**することがあります。これを<strong>ファイアフライ（蛍）</strong>と呼びます。**原因は極端に明るい 1 画素が、縮小のたびに周りの数画素分の平均に混ざり、強い光が画素の位置次第で出たり消えたりする**からです。**対策が Karis Average**（Brian Karis）で、**明るい画素の重みを下げて平均**します。このページでは、**ちらつきの原因・Karis Average の式・どの段に使うか・クランプ・より良いやり方**を説明します。

!!! tip "ポイント"
    - ファイアフライ ＝ <strong>極端に明るい小さな点が、縮小でちらつくブルーム</strong>。
    - 原因 ＝ <strong>HDR の値が非常に大きい 1 画素が、平均に混ざる量が位置で変わる</strong>。
    - 対策 ＝ <strong>Karis Average</strong>：<strong>各サンプルの重みを `1 / (1 + 輝度)`</strong> にして、<strong>明るい画素の影響を抑える</strong>。
    - <strong>最初の縮小（1 段目）だけ</strong>に使えば<strong>十分</strong>。<strong>それ以降は普通の平均</strong>。
    - <strong>輝度のクランプ</strong>（上限を決める）も<strong>併用</strong>できる。
    - <strong>TAA</strong> があれば<strong>さらに安定</strong>する。

## ちらつきの原因

<strong>縮小は「周りの画素を平均して 1 画素にする」</strong>処理です。**ここにとても明るい（例：値 1000）画素が 1 つ混ざる**と、**平均の値がその 1 画素に支配されます**。**画面が少し動くとこの明るい画素がどの縮小画素に混ざるかが変わり**、**ある縮小画素は 1000 ÷ 4 = 250、次のフレームは別の画素に移って 0**——<strong>これが「ぴかぴか」</strong>です。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="ファイアフライの原因">
<text x="20" y="26" class="fig-title">非常に明るい 1 画素が、縮小の平均を支配する</text>
<g transform="translate(40,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">フレーム 1</text>
<g stroke="#94a3b8" fill="#f1f5f9"><rect x="0" y="0" width="40" height="40"/><rect x="40" y="0" width="40" height="40"/><rect x="0" y="40" width="40" height="40"/><rect x="40" y="40" width="40" height="40"/></g>
<rect x="0" y="0" width="40" height="40" fill="#f59e0b"/><text x="20" y="26" text-anchor="middle" style="font-size:12px;font-weight:700">1000</text>
<text x="100" y="26" style="font-size:12px">平均 ＝ 250</text>
<text x="0" y="104" style="font-size:12px">縮小画素は明るく光る</text>
</g>
<g transform="translate(300,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">フレーム 2（少し動いた）</text>
<g stroke="#94a3b8" fill="#f1f5f9"><rect x="0" y="0" width="40" height="40"/><rect x="40" y="0" width="40" height="40"/><rect x="0" y="40" width="40" height="40"/><rect x="40" y="40" width="40" height="40"/></g>
<text x="100" y="26" style="font-size:12px">明るい画素が、別の縮小画素へ</text>
<text x="100" y="48" style="font-size:12px">この縮小画素の平均 ＝ 0</text>
<text x="0" y="104" style="font-size:12px">光が消える → ちらつく</text>
</g>
<text x="40" y="206" style="font-size:13px">1 画素の値が大きすぎるので、平均に混ざる・混ざらないで、結果が極端に変わる。</text>
<text x="40" y="228" style="font-size:13px">対策は、明るい画素の「重み」を下げて、平均への影響を小さくすること。</text>
</svg>

## Karis Average

**サンプルごとに輝度に応じた重みを付けて、加重平均**します。

<div class="formula">重み w = 1 / (1 + 輝度)　、　平均 = Σ (w · 色) / Σ w</div>

```hlsl
float KarisWeight(float3 color) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return 1.0 / (1.0 + luma);
}

float3 KarisAverage(float3 a, float3 b, float3 c, float3 d) {
  float wa = KarisWeight(a);
  float wb = KarisWeight(b);
  float wc = KarisWeight(c);
  float wd = KarisWeight(d);
  return (a * wa + b * wb + c * wc + d * wd) / (wa + wb + wc + wd);
}
```

| 点 | 説明 |
| --- | --- |
| **`1 / (1 + 輝度)`** | **輝度 1000 のサンプルは、重みが約 0.001**。**暗いサンプルは約 1** |
| **加重平均** | **重みの合計で割る**ので**明るさは保たれる**（**明るい点の寄与だけが小さくなる**） |
| **結果** | **明るい 1 画素が平均を支配しない → ちらつかない** |

<!-- fig:karis-fireflies:begin -->
<!-- fig:karis-fireflies:end -->

## 13 タップ ダウンサンプルに組み込む

**13 タップの縮小**（[ダウンサンプル](downsample.md)）では、**5 つの 2×2 ボックス（中央 1・四隅 4）それぞれに Karis 重みを掛けて平均**します。

```hlsl
float3 Downsample13Karis(Texture2D src, SamplerState linear_clamp, float2 uv, float2 texel) {
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

  float3 group_center = KarisAverage(j, k, l, m);
  float3 group_a = KarisAverage(a, b, d, e);
  float3 group_b = KarisAverage(b, c, e, f);
  float3 group_c = KarisAverage(d, e, g, h);
  float3 group_d = KarisAverage(e, f, h, i);
  return group_center * 0.5 + (group_a + group_b + group_c + group_d) * 0.125;
}
```

**各グループの Karis 平均を、通常のボックス平均の代わりに使う**だけです。

## 最初の段だけに使う

**Karis Average は、重みが輝度で変わるので、すべての段に使う**と**広いにじみまで明るい部分が弱くなりすぎます**。**ちらつきの原因は、最初の縮小**（**元の高解像度 → 1/2**）で**極端な値が混ざること**なので、**最初の 1 段だけ**に**使い**、**2 段目以降は普通の平均**にします。

| 段 | 縮小の方式 |
| --- | --- |
| <strong>1 段目（元 → 1/2）</strong> | <strong>Karis Average（13 タップ）</strong> |
| **2 段目以降** | <strong>通常の平均（4 タップのバイリニア）</strong> |

## 輝度のクランプ

**もう 1 つの対策**は、<strong>輝度の上限（クランプ）</strong>です。**ブルームに入れる明るさを、たとえば 10 まで**に**切る**と、**極端な値が混ざらず、ちらつきが減ります**。

```hlsl
float3 ClampBloomInput(float3 color, float max_luma) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return color * min(1.0, max_luma / max(luma, 1e-4));
}
```

| 方式 | 長所 | 短所 |
| --- | --- | --- |
| **Karis Average** | **明るさを保ちつつ、ちらつきを消す** | **13 タップのコスト増** |
| **クランプ** | **簡単・安い** | **非常に明るい光源が弱くなる**（**太陽が控えめなブルーム**） |
| **併用** | **安定する** | **調整項目が増える** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **1 段目だけ Karis** | **コストを抑え、にじみの広がりを保つ** |
| **クランプを併用** | **極端な値（太陽・爆発）は上限を決める** |
| **TAA で時間方向に安定** | **残るちらつきを時間蓄積でなだらかに**（[TAA](../antialiasing/taa.md)） |
| **スペキュラ側で抑える** | **ライティングの段階で極端なハイライトを抑える**（**スペキュラ エイリアシングの対策**） |
| **ブルームの入力を半解像度に** | **最初から 1/2 で作ると、元の高解像度の極端な点が、混ざりにくい** |

## よくあるミス

??? failure "ブルームを動かすと、小さな光がぴかぴかする"
    **ファイアフライ**。**最初の縮小に Karis Average**、または**輝度クランプ**。

??? failure "全段に Karis を使って、にじみが弱く暗い"
    **1 段目だけ**に使う。

??? failure "重みの合計で割り忘れて、全体が暗くなる"
    **`Σ(w·色) / Σw`**。**必ず重みの合計で割る**。

??? failure "クランプを強くしすぎて、太陽が光らない"
    **上限を上げる**、または**Karis に切り替える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイアフライ ＝ <strong>極端に明るい小さな点が、縮小でちらつく</strong>
    - [x] <strong>Karis Average</strong> ＝ <strong>重み `1/(1+輝度)` の加重平均</strong>。<strong>明るさを保ちつつ、ちらつきを消す</strong>
    - [x] <strong>最初の縮小（1 段目）だけ</strong>に使う
    - [x] <strong>輝度クランプ</strong>も併用できる
    - [x] <strong>TAA</strong> で<strong>さらに安定</strong>

## 参考

- Brian Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013 Course）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）

## 関連ページ

- [ブルーム](index.md)
- [ダウンサンプルとミップ チェーン](downsample.md)
- [Dual Filter](dual-filter.md)
- [合成と強さ](composite.md)
