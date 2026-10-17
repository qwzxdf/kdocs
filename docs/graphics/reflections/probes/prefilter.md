---
title: Prefiltering (Split-Sum)
tags:
  - 描画
---

# Prefiltering (Split-Sum)

**粗い面の反射は、周囲の広い範囲の光の平均**になります。**これを、毎回ピクセルごとに計算するのは重すぎる**ので、**粗さごとに、キューブマップを事前にぼかして、ミップに入れておきます**。**Split-Sum 近似**と呼ばれる、**ほとんどのエンジンで使われる方式**です。このページでは、**事前フィルタの考え方とミップの使い方**を説明します。

!!! tip "ポイント"
    - **粗さ ＝ ミップ レベル**（粗いほど、ぼけたミップ）。
    - **事前に、GGX 分布で重み付けして、ぼかす**。
    - **もう 1 つの項（BRDF の積分）は、LUT に入れておく**。
    - **実行時は、ミップ 1 回 ＋ LUT 1 回の読み出しだけ**。

## 粗さへの対応：事前フィルタ（Split-Sum）
粗い面の反射は、**BRDF の山の範囲の景色を、重み付きで平均**したものでした（[Reflections](../index.md)）。これを**表面ごとに実行時に計算するのは重い**ので、**事前計算**します。Epic の Karis が提案した **Split-Sum 近似**が、標準になっています。

### 式を 2 つに分ける

<div class="formula">∫ L_i · f_spec · cosθ dω　≈　( ∫ L_i · D · cosθ dω ) × ( ∫ f_spec · cosθ dω )</div>

2 つの項を、順に説明します。<strong>第 1 項</strong>は、事前フィルタした環境マップです。粗さごとに環境をぼかしたキューブマップ（のミップ）で、プローブごとに事前計算します。<strong>第 2 項</strong>は、BRDF の積分（スケールとバイアス）で、`F0 · A + B` の形をしています。A と B は `n·v` と粗さから引く値で、BRDF LUT（2D テクスチャ）を<strong>1 つだけ</strong>事前計算しておけば、すべてのプローブで共有できます。

Karis が Unreal Engine 4 で提案した split-sum 近似（"Real Shading in Unreal Engine 4"、SIGGRAPH 2013）は、本来は 1 つの積分である鏡面反射を、環境光の項と BRDF の項に「分けて」近似することで、事前計算を可能にしました。この分割は厳密な等式ではなく、視線と法線と反射方向が一致する（`n = v = r`）という仮定を置いた近似ですが、見た目の誤差は小さく、現代の PBR のほぼ標準になっています。

詳しい導出は、[PBR](../../../3d/pbr.md)の IBL を参照してください。

<!-- fig:prefilter-mips:begin -->

<svg class="fig illust motion" data-fig="prefilter-mips" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-prefilter-mips" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="pf-clip-0"><rect x="40" y="110" width="120" height="80"/>
</clipPath>
<filter id="pf-1" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2"/>
</filter>
<clipPath id="pf-clip-1"><rect x="180" y="110" width="120" height="80"/>
</clipPath>
<filter id="pf-2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/>
</filter>
<clipPath id="pf-clip-2"><rect x="320" y="110" width="120" height="80"/>
</clipPath>
<filter id="pf-3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/>
</filter>
<clipPath id="pf-clip-3"><rect x="460" y="110" width="120" height="80"/>
</clipPath>
<filter id="pf-4" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="14"/>
</filter>
<clipPath id="pf-clip-4"><rect x="600" y="110" width="120" height="80"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">事前フィルタ:粗さごとに、ぼかしたキューブ マップを用意しておく</text>
<g clip-path="url(#pf-clip-0)"><rect x="40" y="110" width="120" height="80" fill="#0f172a"/>
<circle cx="64" cy="140" r="9" fill="#fde68a"/>
<circle cx="120" cy="162" r="12" fill="#fca5a5"/>
<circle cx="100" cy="128" r="6" fill="#93c5fd"/>
<circle cx="140" cy="134" r="8" fill="#bbf7d0"/>
</g>
<rect x="40" y="110" width="120" height="80" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="100" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ミップ 0</text>
<text x="100" y="210" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">粗さ 0.00</text>
<g clip-path="url(#pf-clip-1)"><rect x="180" y="110" width="120" height="80" fill="#0f172a"/>
<circle cx="204" cy="140" r="9" fill="#fde68a" filter="url(#pf-1)"/>
<circle cx="260" cy="162" r="12" fill="#fca5a5" filter="url(#pf-1)"/>
<circle cx="240" cy="128" r="6" fill="#93c5fd" filter="url(#pf-1)"/>
<circle cx="280" cy="134" r="8" fill="#bbf7d0" filter="url(#pf-1)"/>
</g>
<rect x="180" y="110" width="120" height="80" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="240" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ミップ 1</text>
<text x="240" y="210" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">粗さ 0.25</text>
<g clip-path="url(#pf-clip-2)"><rect x="320" y="110" width="120" height="80" fill="#0f172a"/>
<circle cx="344" cy="140" r="9" fill="#fde68a" filter="url(#pf-2)"/>
<circle cx="400" cy="162" r="12" fill="#fca5a5" filter="url(#pf-2)"/>
<circle cx="380" cy="128" r="6" fill="#93c5fd" filter="url(#pf-2)"/>
<circle cx="420" cy="134" r="8" fill="#bbf7d0" filter="url(#pf-2)"/>
</g>
<rect x="320" y="110" width="120" height="80" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="380" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ミップ 2</text>
<text x="380" y="210" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">粗さ 0.50</text>
<g clip-path="url(#pf-clip-3)"><rect x="460" y="110" width="120" height="80" fill="#0f172a"/>
<circle cx="484" cy="140" r="9" fill="#fde68a" filter="url(#pf-3)"/>
<circle cx="540" cy="162" r="12" fill="#fca5a5" filter="url(#pf-3)"/>
<circle cx="520" cy="128" r="6" fill="#93c5fd" filter="url(#pf-3)"/>
<circle cx="560" cy="134" r="8" fill="#bbf7d0" filter="url(#pf-3)"/>
</g>
<rect x="460" y="110" width="120" height="80" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="520" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ミップ 3</text>
<text x="520" y="210" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">粗さ 0.75</text>
<g clip-path="url(#pf-clip-4)"><rect x="600" y="110" width="120" height="80" fill="#0f172a"/>
<circle cx="624" cy="140" r="9" fill="#fde68a" filter="url(#pf-4)"/>
<circle cx="680" cy="162" r="12" fill="#fca5a5" filter="url(#pf-4)"/>
<circle cx="660" cy="128" r="6" fill="#93c5fd" filter="url(#pf-4)"/>
<circle cx="700" cy="134" r="8" fill="#bbf7d0" filter="url(#pf-4)"/>
</g>
<rect x="600" y="110" width="120" height="80" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="660" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ミップ 4</text>
<text x="660" y="210" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">粗さ 1.00</text>
<rect x="36" y="106" width="128" height="88" fill="none" stroke="#e5aa28" stroke-width="4"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.2222;0.3852;0.5481;0.7111" values="36;36;176;316;456;596"/></rect>
<text x="40" y="290" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">粗さ 0.00 → ミップ 0 を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2219;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="290" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">粗さ 0.25 → ミップ 1 を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.3849;0.3852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="290" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">粗さ 0.50 → ミップ 2 を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3849;0.3852;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="290" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">粗さ 0.75 → ミップ 3 を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.7108;0.7111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="290" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">粗さ 1.00 → ミップ 4 を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7108;0.7111;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="322" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">鏡のような面:くっきりしたミップ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2219;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="322" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">少し粗い面:ぼけたミップ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="322" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ざらざらの面:とてもぼけたミップ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="380" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">実行時は、粗さからミップを選んで 1 回読むだけ。ぼかしは事前に計算済み（Split-Sum 近似）。</text>
</svg>

<!-- fig:prefilter-mips:end -->

### ミップ レベルの選び方

**粗さが大きいほど、ぼけた（高いミップの）レベル**を読みます。

```hlsl
float3 SpecularIBL(float3 N, float3 V, float3 albedo, float metallic, float roughness) {
  float3 R = reflect(-V, N);
  float mip = roughness * (max_mip - 1.0);
  float3 prefiltered = env_cube.SampleLevel(linear_sampler, R, mip).rgb;

  float n_dot_v = saturate(dot(N, V));
  float2 brdf = brdf_lut.Sample(linear_sampler, float2(n_dot_v, roughness)).rg;

  float3 F0 = lerp(0.04, albedo, metallic);
  return prefiltered * (F0 * brdf.x + brdf.y);
}
```

コードの要点です。`mip = roughness × (最大ミップ)` で、粗さ 0 ならミップ 0（くっきり）、粗さ 1 なら最大のミップ（ぼんやり）を引きます。BRDF LUT は、`n·v` と粗さを入力にした 2 値（スケール・バイアス）で、プロジェクト全体で 1 枚です。`F0` は、非金属で約 0.04、金属ではアルベド色です。ミップ間はトリリニア補間で、粗さが滑らかに変わります。

### 事前フィルタの作り方

**各ミップ**は**その粗さの GGX 分布**で、**環境マップを重要度サンプリング**して作ります。

各ミップは、その粗さの GGX 分布で環境マップを重要度サンプリングして作ります。ミップ 0 は粗さ 0 で、元のキューブマップそのものです。ミップ 1 以降は、粗さを段階的に上げながら、GGX の重要度サンプリングで各テクセルを再計算します（コンピュート シェーダーやピクセル シェーダーで実行）。

**重要度サンプリング**は、**分布の山の部分から多くサンプル**する手法で、**サンプル数を減らせます**（[Stochastic SSR](../ssr-stochastic.md)で詳しく）。

## よくあるミス

??? failure "粗い面の反射が、鏡のようにくっきり"
    **粗さに応じたミップ**を選ぶ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **粗さごとに、事前にぼかす**
    - [x] **実行時は、ミップと LUT を読むだけ**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflection Probes](index.md)
- [Parallax Correction](parallax.md)
- [Stochastic SSR](../ssr-stochastic.md)
