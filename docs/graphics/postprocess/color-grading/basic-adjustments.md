---
title: Basic Adjustments
tags:
  - 描画
---

# Basic Adjustments

**カラー グレーディングの土台**は、**露出・コントラスト・彩度・色相**という**4 つの基本操作**です。<strong>それぞれが「画素の色を変える関数」</strong>で、**組み合わせれば、ほとんどのルックを作れます**。このページでは、**各操作の式と効き方・どの空間で行うか（リニアか、ガンマか）・ピボットの選び方・彩度の注意点・調整の順序**を説明します。

!!! tip "ポイント"
    - <strong>露出</strong>：<strong>全体に倍率</strong>（<strong>2^EV</strong>）。
    - <strong>コントラスト</strong>：<strong>ピボット（中間灰）を中心に広げる・縮める</strong>。
    - <strong>彩度</strong>：<strong>輝度（モノクロ）と元の色を補間</strong>。<strong>0 でモノクロ、1 で元、1 超で鮮やか</strong>。
    - <strong>色相</strong>：<strong>色相環上で回す</strong>。
    - <strong>計算する空間</strong>：<strong>リニアで行うか、見た目に近いガンマ（または対数）で行うか</strong>で<strong>効き方が変わる</strong>。
    - <strong>順序で結果が変わる</strong>（<strong>非可換</strong>）。<strong>一定の順序を決める</strong>。

<!-- fig:basic-adjustments:begin -->

<svg class="fig illust motion" data-fig="basic-adjustments" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-basic-adjustments" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">基本の補正: 露出・コントラスト・彩度。順番を変えると、結果が変わる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">6 色のパレットに、補正を、1 つずつ足す。各段階の「平均の明るさ」と「平均の彩度」を、計算する</text>
<text x="70.0" y="104" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">元の色</text>
<rect x="70.0" y="108.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#e6887b"/></rect>
<rect x="148.0" y="108.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#f3ca6c"/></rect>
<rect x="226.0" y="108.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#94d288"/></rect>
<rect x="304.0" y="108.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067" values="#e5e7eb;#7bbae6"/></rect>
<rect x="382.0" y="108.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#ba94d9"/></rect>
<rect x="460.0" y="108.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#bababa"/></rect>
<rect x="70.0" y="108" width="468.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="0;0;1;1"/><text x="552.0" y="124" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の明るさ 0.478</text>
<text x="552.0" y="144" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の彩度 0.587</text>
</g>
<text x="70.0" y="174" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">+ 露出 +0.5 段</text>
<rect x="70.0" y="178.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2356" values="#e5e7eb;#ff9f90"/></rect>
<rect x="148.0" y="178.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2489" values="#e5e7eb;#ffed7e"/></rect>
<rect x="226.0" y="178.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2622" values="#e5e7eb;#adf59f"/></rect>
<rect x="304.0" y="178.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#90daff"/></rect>
<rect x="382.0" y="178.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#daadfe"/></rect>
<rect x="460.0" y="178.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#e5e7eb;#dadada"/></rect>
<rect x="70.0" y="178" width="468.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;1.0000" values="0;0;1;1"/><text x="552.0" y="194" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の明るさ 0.677</text>
<text x="552.0" y="214" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の彩度 0.587</text>
</g>
<text x="70.0" y="244" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">+ コントラスト 1.3</text>
<rect x="70.0" y="248.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4044" values="#e5e7eb;#ffae99"/></rect>
<rect x="148.0" y="248.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4178" values="#e5e7eb;#ffff81"/></rect>
<rect x="226.0" y="248.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4311" values="#e5e7eb;#c2ffae"/></rect>
<rect x="304.0" y="248.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4444" values="#e5e7eb;#99ffff"/></rect>
<rect x="382.0" y="248.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4578" values="#e5e7eb;#ffc2ff"/></rect>
<rect x="460.0" y="248.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#e5e7eb;#ffffff"/></rect>
<rect x="70.0" y="248" width="468.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;1.0000" values="0;0;1;1"/><text x="552.0" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の明るさ 1.036</text>
<text x="552.0" y="284" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の彩度 0.659</text>
</g>
<text x="70.0" y="314" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">+ 彩度 1.4</text>
<rect x="70.0" y="318.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5733" values="#e5e7eb;#ff956d"/></rect>
<rect x="148.0" y="318.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5867" values="#e5e7eb;#ffff00"/></rect>
<rect x="226.0" y="318.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6000" values="#e5e7eb;#8fff61"/></rect>
<rect x="304.0" y="318.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6133" values="#e5e7eb;#49ffff"/></rect>
<rect x="382.0" y="318.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267" values="#e5e7eb;#ffb5ff"/></rect>
<rect x="460.0" y="318.0" width="78.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400" values="#e5e7eb;#ffffff"/></rect>
<rect x="70.0" y="318" width="468.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6620;0.6622;1.0000" values="0;0;1;1"/><text x="552.0" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の明るさ 1.039</text>
<text x="552.0" y="354" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">平均の彩度 0.767</text>
</g>
<rect x="30" y="392" width="900" height="90" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="382" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">順番を入れ替えると(コントラスト → 彩度 と、 彩度 → コントラスト)</text>
<text x="50" y="430" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937" opacity="0">コントラスト → 彩度<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7420;0.7422;1.0000" values="0;0;1;1"/></text>
<rect x="50.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7422" values="#e5e7eb;#ff956d"/></rect>
<rect x="90.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7511" values="#e5e7eb;#ffff00"/></rect>
<rect x="130.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7600" values="#e5e7eb;#8fff61"/></rect>
<rect x="170.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7689" values="#e5e7eb;#49ffff"/></rect>
<rect x="210.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7778" values="#e5e7eb;#ffb5ff"/></rect>
<rect x="250.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7867" values="#e5e7eb;#ffffff"/></rect>
<rect x="50" y="436" width="240.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="490" y="430" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937" opacity="0">彩度 → コントラスト<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7420;0.7422;1.0000" values="0;0;1;1"/></text>
<rect x="490.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7422" values="#e5e7eb;#ff9b79"/></rect>
<rect x="530.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7511" values="#e5e7eb;#ffff00"/></rect>
<rect x="570.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7600" values="#e5e7eb;#99ff77"/></rect>
<rect x="610.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7689" values="#e5e7eb;#64ffff"/></rect>
<rect x="650.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7778" values="#e5e7eb;#ffb7ff"/></rect>
<rect x="690.0" y="436.0" width="40.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7867" values="#e5e7eb;#ffffff"/></rect>
<rect x="490" y="436" width="240.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="700" y="466" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">色の差(平均)0.029<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8309;0.8311;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">補正は、色に順番に掛けていく<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">露出で明るく、コントラストで、明暗の差を広げ、彩度で、鮮やかにする<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7420;0.7422;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">順番を変えると、結果が少し違う。決まった順番で、作る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7420;0.7422;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:basic-adjustments:end -->

## Four Basic Operations {#4-つの基本操作}

| 操作 | 内容 | 式 |
| --- | --- | --- |
| **露出** | **全体の明るさ** | **色 × 2^EV** |
| **コントラスト** | **明暗の差** | <strong>(色 − ピボット) × 係数 + ピボット</strong> |
| **彩度** | **鮮やかさ** | <strong>lerp(輝度, 色, 彩度)</strong> |
| **色相** | **色の種類** | **色相環で回転** |

## Contrast {#コントラスト}

**ピボット（中心）より明るい部分はより明るく、暗い部分はより暗く**します。

<div class="formula">c' = (c − pivot) × contrast + pivot</div>

```hlsl
float3 ApplyContrast(float3 color, float contrast, float pivot) {
  return (color - pivot) * contrast + pivot;
}
```

コントラストのコードの要点です。`contrast > 1` ならコントラストが強くなり（メリハリ）、`contrast < 1` なら弱くなります（眠い、フラット）。`pivot` は変わらない点で、リニアなら約 0.18（中間灰）、ガンマ空間なら約 0.5 です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="コントラスト">
<text x="20" y="26" class="fig-title">コントラスト：ピボットを中心に、傾きを変える</text>
<line x1="80" y1="200" x2="420" y2="200" stroke="currentColor" stroke-opacity="0.5"/><line x1="80" y1="50" x2="80" y2="200" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4" points="80,200 420,50"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="80,200 150,196 250,125 350,64 420,56"/>
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="80,180 250,125 420,70"/>
<circle cx="250" cy="125" r="5" fill="#1f2937"/><text x="258" y="146" style="font-size:12px">ピボット</text>
<text x="440" y="90" style="font-size:12px;fill:#e5484d">赤：コントラスト強（S 字）</text>
<text x="440" y="116" style="font-size:12px;fill:#2563eb">青：コントラスト弱</text>
<text x="440" y="142" style="font-size:12px;fill:#64748b">灰色の点線：変化なし</text>
</svg>

**線形のコントラスト**は、**0〜1 の外にはみ出す**ことがあるので、<strong>S 字（シグモイド）</strong>や**クランプ**で**抑える**ことが**あります**。

## Saturation {#彩度}

```hlsl
float3 ApplySaturation(float3 color, float saturation) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return lerp(float3(luma, luma, luma), color, saturation);
}
```

彩度の値による見た目です。0 ならモノクロ、1 ならそのまま、1 より大きければ鮮やかになります（1.2〜1.5 がよく使われます）。

**注意**：**彩度を上げすぎるとすでに鮮やかな色が範囲外（> 1）に出たり、色が不自然**になります。<strong>「鮮やかな色ほど効きにくい」振る舞い（バイブランス）</strong>にすると**自然**です。

```hlsl
float3 ApplyVibrance(float3 color, float vibrance) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float max_c = max(color.r, max(color.g, color.b));
  float min_c = min(color.r, min(color.g, color.b));
  float current_saturation = max_c - min_c;
  float amount = vibrance * (1.0 - current_saturation);
  return lerp(float3(luma, luma, luma), color, 1.0 + amount);
}
```

鮮やかさの調整には、2 つの方式があります。<strong>彩度（Saturation）</strong>は、全体を同じ割合で変えます。<strong>バイブランス（Vibrance）</strong>は、もともと地味な色をより強く鮮やかにします。肌の色などを不自然にしないための方式です。

## Hue {#色相}

**色相環（色の輪）の上で色を回転**させます。**RGB を直接回すより、色相・彩度・明度（HSV）や YCoCg に変換して回す**のが**一般的**です。

```hlsl
float3 RotateHue(float3 color, float angle_radians) {
  float c = cos(angle_radians);
  float s = sin(angle_radians);
  float3x3 m = {
    0.299 + 0.701 * c + 0.168 * s, 0.587 - 0.587 * c + 0.330 * s, 0.114 - 0.114 * c - 0.497 * s,
    0.299 - 0.299 * c - 0.328 * s, 0.587 + 0.413 * c + 0.035 * s, 0.114 - 0.114 * c + 0.292 * s,
    0.299 - 0.300 * c + 1.250 * s, 0.587 - 0.588 * c - 1.050 * s, 0.114 + 0.886 * c - 0.203 * s
  };
  return mul(m, color);
}
```

**色相の回転**は**ゲームでは特殊効果（毒・凍結・サイケデリック）や、全体の色味の調整**に**使われます**。

## Space to Compute In {#計算する空間}

計算する空間によって、調整の効き方が変わります。<strong>リニア</strong>（光の量）は、物理的に正しい空間ですが、コントラストの効きが暗部に弱く、明部に強くなります。<strong>ガンマ（sRGB）</strong>は、見た目に近く、画像編集ソフトの感覚と合います。<strong>対数（Log）</strong>は、広いダイナミック レンジを均等に扱え、映画のグレーディングで標準です。

**アーティストが写真編集ソフトの感覚で調整できる**ように、**ガンマ空間か、対数空間で調整**する**のが一般的**です（[3D LUT](lut-3d.md)）。

## Order of Tuning {#調整の順序}

**これらの調整は、順序を入れ替えると結果が変わります**（**非可換**）。**ゲーム（エンジン）で順序を決めて固定**します。

| 順序の例 | 内容 |
| --- | --- |
| **① 露出** | **全体の明るさ** |
| **② ホワイト バランス** | **光源の色を打ち消す** |
| **③ リフト/ガンマ/ゲイン** | **暗部・中間・明部** |
| **④ コントラスト** | **ピボット中心で** |
| **⑤ 彩度** | **最後に鮮やかさ** |

## Better Approaches {#より良いやり方}

| 工夫 | 内容 |
| --- | --- |
| **LUT に焼く** | **すべての調整を、1 つの 3D LUT に**（[3D LUT](lut-3d.md)） |
| **ガンマ・対数空間で調整** | **見た目に近い感覚で** |
| **バイブランスを併用** | **鮮やかになりすぎない** |
| **範囲外をクランプ** | **0〜1 に収める** |
| **順序を固定** | **結果を再現できる** |
| **パラメータをボリュームで管理** | **場所ごとに補間**（[LUT の作り方](lut-authoring.md)） |

## Common Mistakes {#よくあるミス}

??? failure "コントラストを強くしたら、暗部が真っ黒、明部が真っ白"
    <strong>S 字（シグモイド）</strong>にする、**ピボットを正しく**、**適度に**。

??? failure "彩度を上げたら、色が派手すぎて不自然"
    **バイブランス**にする、**上げ幅を抑える**。

??? failure "リニア空間でコントラストを掛けて、見た目が思ったのと違う"
    **ピボットを 0.18**にする、または**ガンマ・対数空間で調整**。

??? failure "調整の順序を変えて、ルックが変わった"
    **順序を固定**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] 基本は<strong>露出・コントラスト・彩度・色相</strong>
    - [x] <strong>コントラスト</strong> ＝ <strong>ピボットを中心に傾きを変える</strong>。<strong>彩度</strong> ＝ <strong>輝度と元の色の補間</strong>
    - [x] <strong>バイブランス</strong>で<strong>鮮やかな色を、増やしすぎない</strong>
    - [x] <strong>リニア・ガンマ・対数</strong>で<strong>効き方が違う</strong>。<strong>ピボットを合わせる</strong>
    - [x] <strong>順序を固定</strong>。<strong>LUT に焼く</strong>

## References {#参考}

- Hable, "Color Grading with Look-Up Tables"（解説）
- Colourist Guide, "Color Grading Fundamentals"
- Selan, "Cinematic Color: From Your Monitor to the Big Screen"（SIGGRAPH 2012）

## Related Pages {#関連ページ}

- [Color Grading](index.md)
- [Lift, Gamma, Gain](lift-gamma-gain.md)
- [3D LUT](lut-3d.md)
- [Exposure](../tonemapping/exposure.md)
