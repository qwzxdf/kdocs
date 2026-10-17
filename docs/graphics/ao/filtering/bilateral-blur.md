---
title: Bilateral Blur
tags:
  - 描画
---

# Bilateral Blur

**AO のノイズを消すには、ぼかすのが基本**ですが、**普通のぼかしは、物体の境界（エッジ）をまたいでにじみ、境界に黒や白のハロー**ができます。**深度や法線が近い画素だけを混ぜる「バイラテラル ブラー」**なら、**エッジを保ったままノイズだけ消せます**。このページでは、**バイラテラル ブラーの考え方・重みの付け方・実装・パラメータ**を説明します。

!!! tip "ポイント"
    - **バイラテラル ブラー ＝ 空間的に近く、かつ、深度・法線も近い画素だけを混ぜる**。
    - **エッジをまたがない**ので**ハローが出ない**。
    - **横 → 縦の 2 パス**に**分離**する（**厳密には分離できないが、実用上は十分**）。
    - **重みは、ガウス ×（深度の差の重み）×（法線の差の重み）**。

## 空間フィルタ：バイラテラル ブラー
<!-- fig:bilateral-blur:begin -->

<svg class="fig illust motion" data-fig="bilateral-blur" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bilateral-blur" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">バイラテラル ブラー:深度の違う画素は、混ぜない</text>
<text x="60" y="80" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">入力の AO（ノイズあり）</text>
<text x="60" y="150" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">深度（左 = 手前、右 = 奥）</text>
<text x="60" y="250" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">普通のぼかし（箱）</text>
<text x="60" y="340" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">バイラテラル（深度で重み付け）</text>
<rect x="60" y="90" width="29" height="34" fill="#9f9f9f"/>
<rect x="60" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="90" y="90" width="29" height="34" fill="#a9a9a9"/>
<rect x="90" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="120" y="90" width="29" height="34" fill="#aeaeae"/>
<rect x="120" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="150" y="90" width="29" height="34" fill="#b9b9b9"/>
<rect x="150" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="180" y="90" width="29" height="34" fill="#a9a9a9"/>
<rect x="180" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="210" y="90" width="29" height="34" fill="#b8b8b8"/>
<rect x="210" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="240" y="90" width="29" height="34" fill="#575757"/>
<rect x="240" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="270" y="90" width="29" height="34" fill="#909090"/>
<rect x="270" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="300" y="90" width="29" height="34" fill="#b9b9b9"/>
<rect x="300" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="330" y="90" width="29" height="34" fill="#a1a1a1"/>
<rect x="330" y="160" width="29" height="24" fill="#2563eb"/>
<rect x="360" y="90" width="29" height="34" fill="#ffffff"/>
<rect x="360" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="390" y="90" width="29" height="34" fill="#dddddd"/>
<rect x="390" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="420" y="90" width="29" height="34" fill="#f1f1f1"/>
<rect x="420" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="450" y="90" width="29" height="34" fill="#e5e5e5"/>
<rect x="450" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="480" y="90" width="29" height="34" fill="#f5f5f5"/>
<rect x="480" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="510" y="90" width="29" height="34" fill="#f7f7f7"/>
<rect x="510" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="540" y="90" width="29" height="34" fill="#d7d7d7"/>
<rect x="540" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="570" y="90" width="29" height="34" fill="#e3e3e3"/>
<rect x="570" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="600" y="90" width="29" height="34" fill="#e7e7e7"/>
<rect x="600" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="630" y="90" width="29" height="34" fill="#ffffff"/>
<rect x="630" y="160" width="29" height="24" fill="#93c5fd"/>
<rect x="60" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0690" values="#f1f5f9;#a4a4a4"/></rect>
<rect x="90" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1034" values="#f1f5f9;#aaaaaa"/></rect>
<rect x="120" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1379" values="#f1f5f9;#acacac"/></rect>
<rect x="150" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1724" values="#f1f5f9;#b0b0b0"/></rect>
<rect x="180" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2069" values="#f1f5f9;#a5a5a5"/></rect>
<rect x="210" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2414" values="#f1f5f9;#9f9f9f"/></rect>
<rect x="240" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2759" values="#f1f5f9;#9f9f9f"/></rect>
<rect x="270" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3103" values="#f1f5f9;#9d9d9d"/></rect>
<rect x="300" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3448" values="#f1f5f9;#b1b1b1"/></rect>
<rect x="330" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3793" values="#f1f5f9;#c6c6c6"/></rect>
<rect x="360" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4138" values="#f1f5f9;#d8d8d8"/></rect>
<rect x="390" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4483" values="#f1f5f9;#e0e0e0"/></rect>
<rect x="420" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4828" values="#f1f5f9;#efefef"/></rect>
<rect x="450" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5172" values="#f1f5f9;#ededed"/></rect>
<rect x="480" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5517" values="#f1f5f9;#ececec"/></rect>
<rect x="510" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5862" values="#f1f5f9;#e9e9e9"/></rect>
<rect x="540" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6207" values="#f1f5f9;#e9e9e9"/></rect>
<rect x="570" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6552" values="#f1f5f9;#ebebeb"/></rect>
<rect x="600" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6897" values="#f1f5f9;#ededed"/></rect>
<rect x="630" y="260" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7241" values="#f1f5f9;#f5f5f5"/></rect>
<rect x="60" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0690" values="#f1f5f9;#a4a4a4"/></rect>
<rect x="90" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1034" values="#f1f5f9;#aaaaaa"/></rect>
<rect x="120" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1379" values="#f1f5f9;#acacac"/></rect>
<rect x="150" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1724" values="#f1f5f9;#b0b0b0"/></rect>
<rect x="180" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2069" values="#f1f5f9;#a5a5a5"/></rect>
<rect x="210" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2414" values="#f1f5f9;#9f9f9f"/></rect>
<rect x="240" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2759" values="#f1f5f9;#9f9f9f"/></rect>
<rect x="270" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3103" values="#f1f5f9;#9d9d9d"/></rect>
<rect x="300" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3448" values="#f1f5f9;#969696"/></rect>
<rect x="330" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3793" values="#f1f5f9;#a5a5a5"/></rect>
<rect x="360" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4138" values="#f1f5f9;#f0f0f0"/></rect>
<rect x="390" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4483" values="#f1f5f9;#ededed"/></rect>
<rect x="420" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4828" values="#f1f5f9;#efefef"/></rect>
<rect x="450" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5172" values="#f1f5f9;#ededed"/></rect>
<rect x="480" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5517" values="#f1f5f9;#ececec"/></rect>
<rect x="510" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5862" values="#f1f5f9;#e9e9e9"/></rect>
<rect x="540" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6207" values="#f1f5f9;#e9e9e9"/></rect>
<rect x="570" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6552" values="#f1f5f9;#ebebeb"/></rect>
<rect x="600" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6897" values="#f1f5f9;#ededed"/></rect>
<rect x="630" y="350" width="29" height="34" fill="#f1f5f9"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7241" values="#f1f5f9;#f5f5f5"/></rect>
<rect x="60" y="256" width="149" height="42" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="x" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0690;0.1034;0.1379;0.1724;0.2069;0.2414;0.2759;0.3103;0.3448;0.3793;0.4138;0.4483;0.4828;0.5172;0.5517;0.5862;0.6207;0.6552;0.6897;0.7241" values="60;0;30;60;90;120;150;180;210;240;270;300;330;360;390;420;450;480;510;540;570"/><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.7583;0.7586;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="60" y="346" width="149" height="42" fill="none" stroke="#2ea043" stroke-width="3" opacity="0"><animate attributeName="x" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0690;0.1034;0.1379;0.1724;0.2069;0.2414;0.2759;0.3103;0.3448;0.3793;0.4138;0.4483;0.4828;0.5172;0.5517;0.5862;0.6207;0.6552;0.6897;0.7241" values="60;0;30;60;90;120;150;180;210;240;270;300;330;360;390;420;450;480;510;540;570"/><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.7583;0.7586;1.0000" values="0;0;1;1;0;0"/></rect>
<g opacity="1"/>
<text x="60" y="420" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">窓(5 画素)を左から右へ動かして、各画素を平均する<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="60" y="420" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">上:全部混ぜる → 境界(10 番目付近)で、AO がにじむ。下:深度が近い画素だけ混ぜる → 境界がくっきり<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.7583;0.7586;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="420" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">→ 境界の AO の段差が残り、ハロー（にじみ）が出ない<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7583;0.7586;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bilateral-blur:end -->

### 通常のぼかしの問題

AO の画像を**そのままぼかす**と**物体の境界**で**手前の物体の AO と、奥の物体の AO が混ざり**ます。手前の物体の縁に**暗い輪**が出たり、**接地の暗さがにじんで広がる**ことがあります。

### バイラテラル：「近いもの」だけを混ぜる

**バイラテラル フィルタ**は、中心の画素と**似た画素だけ**を、重み付きで混ぜます。**似ている**とは、AO では**深度（と法線）が近い**ことです。

<div class="formula">AO′(p) = Σ_q w(p, q) · AO(q) / Σ_q w(p, q)　、　w = w_空間 · w_深度 · w_法線</div>

| 重み | 式の例 | 意味 |
| --- | --- | --- |
| **w_空間** | ガウス、または一様 | 距離が近いほど大 |
| **w_深度** | `exp(−\|z_p − z_q\| · k)` または `1 / (ε + \|z_p − z_q\|)` | **深度が近い**ほど大。**別の面なら 0 に近づく** |
| **w_法線** | `pow(saturate(dot(n_p, n_q)), 8)` | **法線が近い**ほど大。**向きの違う面を混ぜない** |

```hlsl
float BilateralBlur(float2 uv, float2 dir) {
  float center_z = LinearDepth(uv);
  float3 center_n = Normal(uv);
  float sum = 0.0;
  float weight_sum = 0.0;

  [unroll] for (int i = -kRadius; i <= kRadius; ++i) {
    float2 suv = uv + dir * texel_size * i;
    float ao = ao_tex.SampleLevel(point_sampler, suv, 0).r;
    float z = LinearDepth(suv);

    float w = gaussian[abs(i)];
    w *= exp(-abs(center_z - z) * depth_sharpness / center_z);
    w *= pow(saturate(dot(center_n, Normal(suv))), 8.0);

    sum += ao * w;
    weight_sum += w;
  }
  return sum / max(weight_sum, 1e-4);
}
```

| 点 | 説明 |
| --- | --- |
| **深度の差を中心の深度で割る** | **遠いほど、深度の差が大きく出る**ので、相対的な差で比べる |
| **`depth_sharpness`** | 大きいほど、境界を厳しく守る |
| **ポイント サンプリング** | AO と深度は、**補間せず**に読む |

### 分離可能にする（横 → 縦）

2D のぼかしを**横 1 回 ＋ 縦 1 回**に分けると、**N² → 2N** 回の読み込みで済みます。**バイラテラルは、厳密には分離できません**（重みが、2D の位置に依存）が、**実用上は分離して近似**します。

| 方式 | 読み込み回数（半径 4 の例） | 品質 |
| --- | --- | --- |
| <strong>2D（全画素）</strong> | 81 | 正確 |
| <strong>分離（横 → 縦）</strong> | 18 | 縦横の斜めでわずかな乱れ |

### 4×4 ノイズに合わせた、ボックス ぼかし

**4×4 のノイズ テクスチャ**を使った SSAO（[Hemisphere SSAO](../ssao-hemisphere.md)）では**ノイズが 4 画素周期**で繰り返すので、**4×4 のボックス ぼかし**で、**周期のパターンがちょうど消えます**。**深度の重み付き**にすれば、境界も守れます。

## よくあるミス

??? failure "通常のガウスでぼかして、物の輪郭に AO のにじみ（ハロー）が出る"
    **深度・法線で重みを付ける**（バイラテラル）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **深度・法線が近い画素だけ混ぜる**
    - [x] **エッジを保って、ノイズだけ消す**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [AO Filtering](index.md)
- [Upsampling](upsample.md)
- [Gaussian Blur](../../postprocess/bloom/gaussian.md)
