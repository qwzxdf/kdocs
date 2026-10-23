---
title: Multiple Scattering
tags:
  - 描画
---

# Multiple Scattering

<strong>光は何度も散乱しながら進みます</strong>。単散乱だけだと空の暗い部分（影・夕方）が暗すぎます。多重散乱を近似して足すと明るさが自然になります。このページでは多重散乱を説明します。

!!! tip "ポイント"
    - 単散乱だけだと暗すぎる。
    - 多重散乱は全方向からの光の和。
    - LUT で近似的に計算する（Hillaire 2020）。
    - 空の暗部・影・雲が、自然になる。

## 多重散乱
<strong>単散乱だけだと夕方や影の側の空が暗くなりすぎます</strong>。実際には一度散った光が何度も散ります（多重散乱）。地球の大気では昼間の空の明るさの 1〜2 割は多重散乱で、夕暮れの空の明るさは多重散乱で決まります。

多重散乱の近似は 3 通りあります。ambient の底上げは、単散乱に一定の環境光を足す方法で、手軽ですが粗いです。Bruneton の多重散乱は、散乱の次数ごとに事前計算を繰り返す方法で、正確ですが重いです。Hillaire の近似は、多重散乱を等方で無限級数の閉じた式で近似し、小さな 2D LUT にまとめます。軽く動的な大気にも使えます。

### Hillaire の近似の考え方

Hillaire の近似は大胆な仮定に基づいています。「2 次以降の散乱光は散乱のたびに方向がランダムになり、ほぼ等方（どの方向にも均等）になる」。この仮定のもとでは 2 次散乱の光の量 L₂ は、1 次散乱の量から簡単に求まります。3 次の量は 2 次の何倍か、4 次は 3 次の何倍かと考えると、次数ごとに同じ比率 f で減っていくと見なせます。すると、すべての次数を足した多重散乱は、等比級数の和になります。

<div class="formula">L_multi = L₂ · (1 + f + f² + …) = L₂ / (1 − f)</div>

ここで f は各散乱で光が次の散乱へ引き継がれる割合です。これは閉じた式なので無限に足す必要がありません。この式を高さと太陽の天頂角の 2 つのパラメータに対して事前に計算して 2D の表（多重散乱 LUT）にしておけば、実行時は 1 回引くだけで多重散乱の寄与が分かります。

この近似の誤差は小さく特に夕方や、地平線付近の空の明るさで単散乱だけの場合との差がはっきり出ます。単散乱だけだと太陽が地平線に近いとき、空が暗すぎる青みが足りないなどの問題が出ますが、多重散乱を足すと自然な明るさに近づきます。

<!-- fig:multi-scatter-sum:begin -->

<svg class="fig illust motion" data-fig="multi-scatter-sum" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-multi-scatter-sum" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">多重散乱: 光は、何度も散る。アルベド(反射する割合)が高いほど、何回目まで足さないと、足りない</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 回目の散乱を 1 とする。散乱 k 回目の光は、アルベド^(k−1)。アルベド 0.5・0.8・0.95 で、合計がどう積み上がるかを計算する</text>
<rect x="30" y="96" width="640" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 散乱を k 回足したときの合計</text>
<text x="70.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">1</text>
<text x="169.1304347826087" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">5</text>
<text x="293.04347826086956" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">10</text>
<text x="416.95652173913044" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">15</text>
<text x="540.8695652173913" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">20</text>
<path d="M70.0,339.55 L94.78,334.32 L119.57,331.7 L144.35,330.4 L169.13,329.74 L193.91,329.42 L218.7,329.25 L243.48,329.17 L268.26,329.13 L293.04,329.11 L317.83,329.1 L342.61,329.1 L367.39,329.09 L392.17,329.09 L416.96,329.09 L441.74,329.09 L466.52,329.09 L491.3,329.09 L516.09,329.09 L540.87,329.09 L565.65,329.09 L590.43,329.09 L615.22,329.09 L640.0,329.09" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<line x1="70" y1="329.09" x2="640" y2="329.09" stroke="#2ea043" stroke-width="1.5" stroke-dasharray="4 4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/></line>
<text x="640" y="324.09" text-anchor="end" style="font-size:11px;font-weight:700;fill:#2ea043" opacity="0">上限 2.0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,339.55 L94.78,331.18 L119.57,324.49 L144.35,319.14 L169.13,314.86 L193.91,311.43 L218.7,308.69 L243.48,306.5 L268.26,304.74 L293.04,303.34 L317.83,302.22 L342.61,301.32 L367.39,300.6 L392.17,300.03 L416.96,299.57 L441.74,299.2 L466.52,298.9 L491.3,298.67 L516.09,298.48 L540.87,298.33 L565.65,298.21 L590.43,298.11 L615.22,298.04 L640.0,297.97" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="0;0;1;1"/></path>
<line x1="70" y1="297.73" x2="640" y2="297.73" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3022;1.0000" values="0;0;1;1"/></line>
<text x="640" y="292.73" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5aa28" opacity="0">上限 5.0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3022;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,339.55 L94.78,329.61 L119.57,320.18 L144.35,311.21 L169.13,302.7 L193.91,294.61 L218.7,286.93 L243.48,279.62 L268.26,272.69 L293.04,266.1 L317.83,259.84 L342.61,253.89 L367.39,248.24 L392.17,242.88 L416.96,237.78 L441.74,232.94 L466.52,228.33 L491.3,223.96 L516.09,219.81 L540.87,215.87 L565.65,212.12 L590.43,208.56 L615.22,205.17 L640.0,201.96" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;1.0000" values="0;0;1;1"/></path>
<line x1="70" y1="140.91" x2="640" y2="140.91" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5154;0.5156;1.0000" values="0;0;1;1"/></line>
<text x="640" y="135.91" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d" opacity="0">上限 20.0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5154;0.5156;1.0000" values="0;0;1;1"/></text>
<rect x="690" y="96" width="240" height="280" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="690" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">95% に届くまでの回数</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="0;0;1;1"/><text x="706" y="140" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">アルベド 0.50</text>
<text x="706" y="168" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043">5 回</text>
<text x="706" y="188" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">1 回だけでは 1/2.0 = 50%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;1.0000" values="0;0;1;1"/><text x="706" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">アルベド 0.80</text>
<text x="706" y="244" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5aa28">14 回</text>
<text x="706" y="264" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">1 回だけでは 1/5.0 = 20%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;1.0000" values="0;0;1;1"/><text x="706" y="292" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">アルベド 0.95</text>
<text x="706" y="320" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d">59 回</text>
<text x="706" y="340" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">1 回だけでは 1/20.0 = 5%</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">95% に必要な回数:</text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;0.3154;0.3156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">14<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;0.5287;0.5289;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">59<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6932;0.6933;1.0000" values="0;0;1;1"/><rect x="40" y="440" width="880" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="464" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">雲(アルベド 0.95 以上)は、1 回の散乱では、全体の 5% しか光らない。20 回以上必要</text>
<text x="56" y="487" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">毎回レイマーチで何十回も散らせるのは無理 → 少数の回数を、減衰を弱めて、足す近似(オクターブ)を使う</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光は、媒質の中で、何度も散る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">アルベドが高いほど、後の回数まで、光が残る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">雲や霧は、アルベドが高い。多重散乱を、近似で足す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:multi-scatter-sum:end -->

## 多重散乱：なぜ必要か

[Single-Scattering Integral](single-scattering.md) では <strong>光が、1 回だけ散乱</strong>する場合を扱いました。しかし、実際の光は 何度も散乱を繰り返します。2 回目以降の散乱を足さないと空が暗く色が、不足します。

| 散乱の回数 | 内容 |
| --- | --- |
| 1 回 | 太陽の光が 1 回だけ曲がって、カメラへ |
| 2 回 | 1 回目に曲がった光が、もう 1 回、別の点で曲がってカメラへ |
| 3 回以上 | さらに続く。光は回数が増えるほど弱く全方向に、均される |

地球の大気では 2 回目以降の、散乱が 空の明るさの 2 割〜3 割を、占めます。夕方・夜明け（太陽が低い）では割合が、さらに大きくなります。

## 光が何度も散乱すると

<strong>散乱を繰り返す</strong>たびに光の向きは、ばらばらになります。3 回目以降は向きがほぼ均一（等方）と、みなせます。これを利用した近似があります。

## Hillaire の近似

Hillaire（2020）は、多重散乱を <strong>次の 2 つの仮定</strong>で、近似しました。

1. 2 回目以降の散乱は位相関数が、等方（`1 / 4π`）
2. ある点での多重散乱の光は、その点の周りの情報で決まる（空間的に、ゆるやかに変化する）

この仮定の下では 多重散乱の、総和は 等比級数で解析的に、表せます。

```text
全散乱 = L₂ × (1 + f + f² + f³ + …) = L₂ / (1 − f)        （f < 1）
```

`L₂` は 2 回散乱の光、`f` は 「1 回散乱するたびに光が、散乱して再びその点の周りへ戻ってくる、割合」です。

## 多重散乱 LUT

<strong>高度</strong>と 太陽の天頂角の、2 変数に依存する `L₂` と `f` を小さな、LUT（Hillaire は 32×32）に、事前計算します。

### 計算の考え方

各点（高度 `h`、太陽の天頂角 `θ_s`）で 球面上の、全方向に視線を 飛ばし、各方向の 1 回散乱の光（`L₂` の、材料）とその方向の透過率（`f` の材料）を、積分します。

```hlsl
// 多重散乱 LUT の、1 つの画素（= 1 つの、高度と、太陽の角度）を、計算する。
// 全方向（64 方向）に、視線を飛ばし、2 つの量を、平均する:
//   L2: 等方な位相関数で、1 回散乱した光（= 2 回目の散乱の、光源）
//   f:  各方向の、散乱で、再び、その点へ戻る、割合
[numthreads(1, 1, 64)]
void MultiScatteringCS(uint3 id : SV_DispatchThreadID, uint group_index : SV_GroupIndex) {
  // 画素から、高度と、太陽の天頂角の cos を求める。
  float2 uv = (id.xy + 0.5) / float2(32, 32);
  float cos_sun_zenith = uv.x * 2.0 - 1.0;
  float view_height = g_bottom_radius + uv.y * (g_top_radius - g_bottom_radius);
```

LUT の 横軸が太陽の天頂角、縦軸が高度です。64 本の方向をグループ内の、スレッド（`id.z`）に割り当てます。

```hlsl
  float3 sun_dir = float3(0.0, cos_sun_zenith, sqrt(saturate(1.0 - cos_sun_zenith * cos_sun_zenith)));
  float3 world_pos = float3(0.0, view_height, 0.0);

  // 球面上の 64 方向（フィボナッチ螺旋などで、均等に）。各スレッドが、1 方向を担当。
  float3 ray_dir = SphereDirection(group_index, 64);
  float3 L2 = 0.0;                                    // この方向の、「等方な 1 回散乱」
  float3 f_ms = 0.0;                                  // この方向の、「戻ってくる割合」
```

方向の選び方は 球面を均等に、覆うパターンです。64 方向で滑らかな LUT が、得られます。

```hlsl
  // この方向に、視線を進めて、1 回散乱（位相関数は、等方 = 1/4π）を、積分する。
  IntegrateMultiScatter(world_pos, ray_dir, sun_dir, /*out*/ L2, /*out*/ f_ms);

  // 64 方向を、グループ内で、合計して、平均する（共有メモリで、リダクション）。
  // ... 合計の処理 ...

  // 最終結果: 等比級数の、和。f が 1 に近いほど、多重散乱が、強い。
  float3 multi_scattering = L2 / (1.0 - f_ms);
  g_multi_scattering_lut[id.xy] = multi_scattering;
}
```

`IntegrateMultiScatter` の中身は 1 回散乱の積分（[Single-Scattering Integral](single-scattering.md)）と、ほぼ同じですが位相関数が、等方（`1 / 4π`）で同時に `f_ms` も足します。

## 空の計算で使う

<strong>多重散乱 LUT</strong> は 1 回散乱の、ループの中で各点に足すだけです。

```hlsl
    // 各サンプル点で、多重散乱の光を、足す（LUT を、1 回、読むだけ）。
    float2 ms_uv = float2(saturate(cos_sun_zenith_at_p * 0.5 + 0.5), saturate((h - g_bottom_radius) / (g_top_radius - g_bottom_radius)));
    float3 multi = g_multi_scattering_lut.SampleLevel(g_linear_clamp, ms_uv, 0).rgb;
    float3 scatter = (g_rayleigh_scatter * density_r + g_mie_scatter * density_m) * (sun_t * phase_term * sun_illuminance + multi * sun_illuminance);
```

多重散乱の光は位相関数なし（等方）で、散乱係数だけを掛けて足します。1 回散乱（太陽の透過率 × 位相関数）と、多重散乱（LUT）を足し合わせる形です。

## 効果

| 状況 | 1 回散乱のみ | 多重散乱あり |
| --- | --- | --- |
| 昼の空の明るさ | 暗め | 実際の明るさ |
| 太陽が低い空 | 暗く色が、不足 | 全体が明るく紫〜青の、グラデーション |
| 雲の中や霧の中 | 暗い（光が奥まで、届かない） | 明るい（光が散乱を、繰り返して奥まで届く） |

## 雲・霧の多重散乱

雲は <strong>ミー散乱が強く</strong>、アルベド（散乱の割合）が非常に、高い（ほぼ 1）ため光が何十回も、散乱します。多重散乱を無視すると雲の内部が暗く、墨のようになります。

| 方法 | 内容 |
| --- | --- |
| オクターブによる近似（Wrenninge、2015） | 散乱を数段階（オクターブ）に分け、各段階で減衰を弱め位相関数を等方に、近づける。各オクターブを足し合わせる |
| 事前計算 | 雲の密度から、多重散乱のライトマップを作る |

```hlsl
// Wrenninge の、オクターブによる、多重散乱の、近似（雲のライティングで、使われる）。
float3 MultiScatterOctaves(float density_along_light, float cos_theta) {
  float3 sum = 0.0;
  float a = 1.0, b = 1.0, c = 1.0;           // 各オクターブの、散乱量、減衰、位相関数の、偏りの、倍率
  for (int octave = 0; octave < 4; ++octave) {
    float phase = DualLobePhase(cos_theta, 0.8 * c, -0.5 * c, 0.7);
    sum += a * phase * exp(-density_along_light * g_sigma_t * b);
    a *= 0.5;                                // 散乱量は、半分ずつ
    b *= 0.25;                               // 減衰は、弱く（光が、深くまで、届く）
    c *= 0.5;                                // 位相関数の、偏りは、弱く（等方に近づく）
  }
  return sum;
}
```

オクターブが進むほど、散乱量が減り（`a`）、減衰が弱まり（`b`、光が深く届く）、位相関数が等方に近づく（`c`）。この 3 つの調整が多重散乱の、性質（弱く深く均一）を模倣します（[Cloud Lighting](../clouds/lighting.md)）。

## よくあるミス

??? failure "影になる部分の空が、真っ黒"
    <strong>多重散乱</strong>を足す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何度も散乱した光を、近似で足す

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)（4 つの LUT を使う方式。公開デモの実装がある）
- Wrenninge, "Art-Directable Multiple Volumetric Scattering", SIGGRAPH 2015 Talks（多重散乱の、オクターブによる近似）
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大気散乱、参加媒質の章）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Hillaire 2020](hillaire.md)
