---
title: Fireflies (Karis Average)
tags:
  - 描画
---

# Fireflies (Karis Average)

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

コードの要点です。`1 / (1 + 輝度)` の重みは、輝度 1000 のサンプルなら約 0.001、暗いサンプルなら約 1 になります。加重平均なので、重みの合計で割り、全体の明るさは保たれます（明るい点の寄与だけが小さくなります）。結果として、明るい 1 画素が平均を支配せず、ちらつきません。

この重み付けは、Karis Average と呼ばれ、Jimenez の SIGGRAPH 2014 の発表で広く知られるようになりました。

<!-- fig:karis-fireflies:begin -->

<svg class="fig illust motion" data-fig="karis-fireflies" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-karis-fireflies" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">1 画素だけ極端に明るいと、普通の平均は暴れる（ファイアフライ）</text>
<text x="40" y="76" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">4×4 の 1 ブロック</text>
<rect x="40" y="90" width="32" height="32" fill="#e2e8f0"/>
<rect x="74" y="90" width="32" height="32" fill="#e2e8f0"/>
<rect x="108" y="90" width="32" height="32" fill="#e2e8f0"/>
<rect x="142" y="90" width="32" height="32" fill="#e2e8f0"/>
<rect x="40" y="124" width="32" height="32" fill="#e2e8f0"/>
<rect x="74" y="124" width="32" height="32" fill="#e2e8f0"/>
<rect x="108" y="124" width="32" height="32" fill="#e2e8f0"/>
<rect x="142" y="124" width="32" height="32" fill="#e2e8f0"/>
<rect x="40" y="158" width="32" height="32" fill="#e2e8f0"/>
<rect x="74" y="158" width="32" height="32" fill="#e2e8f0"/>
<rect x="108" y="158" width="32" height="32" fill="#e2e8f0"/>
<rect x="142" y="158" width="32" height="32" fill="#e2e8f0"/>
<rect x="40" y="192" width="32" height="32" fill="#e2e8f0"/>
<rect x="74" y="192" width="32" height="32" fill="#e2e8f0"/>
<rect x="108" y="192" width="32" height="32" fill="#e2e8f0"/>
<rect x="142" y="192" width="32" height="32" fill="#e2e8f0"/>
<rect x="108" y="124" width="32" height="32" fill="#fef08a" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.3127;0.3130;0.4344;0.4348;0.5562;0.5565;1.0000" values="0;0;1;1;0;0;1;1;0;0"/></rect>
<text x="123" y="145" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">50<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.3127;0.3130;1.0000" values="0;0;1;1;0;0"/></text>
<text x="123" y="145" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">50<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.5562;0.5565;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 1:入っていない<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;0.1910;0.1913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 2:明るい画素が入った<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.3127;0.3130;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 3:入っていない<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;0.4344;0.4348;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 4:明るい画素が入った<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.5562;0.5565;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 5:入っていない<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;0.6779;0.6783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 6:入っていない<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6779;0.6783;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="290" y="76" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">縮小後の画素の明るさ</text>
<line x1="290" y1="280" x2="730" y2="280" stroke="#1f2937" stroke-width="1.5"/>
<rect x="304" y="237.78" width="26" height="42.22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000" values="0;0;1;1"/></rect>
<rect x="332" y="237.78" width="26" height="42.22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000" values="0;0;1;1"/></rect>
<text x="331" y="296" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<rect x="374" y="108.47" width="26" height="171.53" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="0;0;1;1"/></rect>
<rect x="402" y="232.38" width="26" height="47.62" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="0;0;1;1"/></rect>
<text x="401" y="296" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2</text>
<rect x="444" y="237.78" width="26" height="42.22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000" values="0;0;1;1"/></rect>
<rect x="472" y="237.78" width="26" height="42.22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000" values="0;0;1;1"/></rect>
<text x="471" y="296" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">3</text>
<rect x="514" y="108.47" width="26" height="171.53" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="0;0;1;1"/></rect>
<rect x="542" y="232.38" width="26" height="47.62" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="0;0;1;1"/></rect>
<text x="541" y="296" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<rect x="584" y="237.78" width="26" height="42.22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;1.0000" values="0;0;1;1"/></rect>
<rect x="612" y="237.78" width="26" height="42.22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;1.0000" values="0;0;1;1"/></rect>
<text x="611" y="296" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">5</text>
<rect x="654" y="237.78" width="26" height="42.22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6779;0.6783;1.0000" values="0;0;1;1"/></rect>
<rect x="682" y="237.78" width="26" height="42.22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6779;0.6783;1.0000" values="0;0;1;1"/></rect>
<text x="681" y="296" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">6</text>
<rect x="290" y="313" width="14" height="14" fill="#e5484d"/>
<text x="310" y="324" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">普通の平均(1.0 ↔ 4.1 とちらつく)</text>
<rect x="540" y="313" width="14" height="14" fill="#2ea043"/>
<text x="560" y="324" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">Karis 平均(1.00 ↔ 1.13 安定)</text>
<text x="40" y="356" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">Karis 平均:各画素に 1 / (1 + 輝度) の重みを付けて平均 → 極端に明るい画素の影響が小さい</text>
</svg>

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

Karis Average は、重みが輝度で変わるので、すべての段に使うと、広いにじみまで明るい部分が弱くなりすぎます。ちらつきの原因は最初の縮小（元の高解像度から 1/2）なので、1 段目だけ Karis Average（13 タップ）を使い、2 段目以降は通常の平均（4 タップのバイリニア）にします。

## 輝度のクランプ

**もう 1 つの対策**は、<strong>輝度の上限（クランプ）</strong>です。**ブルームに入れる明るさを、たとえば 10 まで**に**切る**と、**極端な値が混ざらず、ちらつきが減ります**。

```hlsl
float3 ClampBloomInput(float3 color, float max_luma) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return color * min(1.0, max_luma / max(luma, 1e-4));
}
```

ちらつき対策の方式を比べます。Karis Average は、明るさを保ちつつちらつきを消しますが、13 タップのコストが増えます。クランプは、簡単で安いですが、非常に明るい光源が弱くなります（太陽が控えめなブルームになります）。併用すると安定しますが、調整項目が増えます。

## より良いやり方

より良いやり方を挙げます。1 段目だけ Karis を使い、コストを抑えてにじみの広がりを保ちます。極端な値（太陽・爆発）には上限を決めるクランプを併用します。TAA で時間方向に安定させて、残るちらつきを時間蓄積でなだらかにします（[TAA](../antialiasing/taa.md)）。スペキュラ側で抑える方法として、ライティングの段階で極端なハイライトを抑えます（スペキュラ エイリアシングの対策）。ブルームの入力を半解像度にすると、元の高解像度の極端な点が混ざりにくくなります。

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

- [Bloom](index.md)
- [Downsampling and the Mip Chain](downsample.md)
- [Dual Filter](dual-filter.md)
- [Compositing and Intensity](composite.md)
