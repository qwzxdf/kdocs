---
title: Weighted Blended OIT（WBOIT）
tags:
  - 描画
---

# Weighted Blended OIT（WBOIT）

**WBOIT は、深度に応じた重みで、半透明の色を加重平均する、近似の手法**です。**1 パスで描けて、とても軽い**ので、**実用的**です。**ただし、近似なので、正確さは劣ります**。このページでは、**WBOIT の式と、重みの選び方**を説明します。

!!! tip "ポイント"
    - **色の合計と、アルファの積を、2 枚のバッファに蓄積**する。
    - **手前ほど重く**する**重み関数**を使う。
    - **1 パスで、ソート不要**。
    - **近似なので、色の順序が正確でない**。

## Weighted Blended OIT
**順序を無視**して、**深度に応じた「重み」を付けた加重平均**で**合成**する、**近似手法**です（**McGuire と Bavoil、2013**）。**1 パスで描け、レンダー ターゲット 2 枚だけ**なので、**軽く**、**ゲームで実用的**です。

<!-- fig:wboit-layers:begin -->

<svg class="fig illust motion" data-fig="wboit-layers" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-wboit-layers" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">WBOIT:ソートなしの重み付き平均は、正しいブレンドに近い</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><rect x="60" y="100" width="200" height="90" fill="#e5484d" fill-opacity="0.5" stroke="#e5484d" stroke-width="2"/>
<text x="68" y="120" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">層 1（α 0.5、深さ 0.2）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/><rect x="120" y="140" width="200" height="90" fill="#2ea043" fill-opacity="0.5" stroke="#2ea043" stroke-width="2"/>
<text x="128" y="160" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">層 2（α 0.5、深さ 0.5）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000" values="0;0;1;1"/><rect x="180" y="180" width="200" height="90" fill="#2563eb" fill-opacity="0.5" stroke="#2563eb" stroke-width="2"/>
<text x="188" y="200" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">層 3（α 0.5、深さ 0.8）</text>
</g>
<text x="450" y="90" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">正しい結果（ソート）</text>
<text x="620" y="90" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">WBOIT（順序なし）</text>
<rect x="450" y="100" width="140" height="80" fill="#ffffff" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.2963;0.5185" values="#ffffff;#f2a4a6;#be8c77;#a27874"/></rect>
<rect x="620" y="100" width="140" height="80" fill="#ffffff" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.2963;0.5185" values="#ffffff;#f2a4a6;#a79776;#85827f"/></rect>
<text x="450" y="220" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">層 1 まで重ねた結果の差:0 / 255<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="220" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">層 2 まで重ねた結果の差:12 / 255<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="220" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">層 3 まで重ねた結果の差:17 / 255<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="450" y="250" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">手前ほど重みを大きく（深さの関数）して平均する<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">式:色 = Σ(色 × α × w(z)) / Σ(α × w(z))、残りの透過率 = Π(1 − α)。</text>
<text x="60" y="366" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">色は少しずれるが、1 パス・ソートなしで、ほとんどの半透明で十分に見える（重なりが多いほど、誤差は増える）。</text>
</svg>

<!-- fig:wboit-layers:end -->

### 考え方

**手前の物ほど、重みを大きく**して、**平均**します。**順序を知らなくても、「手前らしさ」を深度から推定**して、**近似的な順序づけ**を得ます。

<div class="formula">C = Σ(Cᵢ · αᵢ · wᵢ) / Σ(αᵢ · wᵢ)　、　α_total = 1 − Π(1 − αᵢ)</div>

記号の意味です。wᵢ は層 i の重みで、深度が小さい（手前）ほど大きくなります。Σ(Cᵢ αᵢ wᵢ) は重み付きの色の合計（アキュムレーション）です。Π(1 − αᵢ) は全層の透過率の積で、リビール（背景の見える割合）と呼びます。

原典は、McGuire と Bavoil の "Weighted Blended Order-Independent Transparency"（Journal of Computer Graphics Techniques、2013）です。

### 2 枚のレンダー ターゲット

2 枚のレンダー ターゲットを使います。アキュムレーションは `R16G16B16A16_FLOAT` で、`(Cᵢ·αᵢ·wᵢ, αᵢ·wᵢ)` を加算します（ブレンドは ONE / ONE）。リビールは `R8_UNORM` で、`αᵢ` を透過率として乗算します（ブレンドは ZERO / INV_SRC_COLOR で、`(1 − αᵢ)` を掛けます）。

```hlsl
struct PsOutput {
  float4 accumulation : SV_Target0;
  float reveal : SV_Target1;
};

PsOutput PSWeighted(VsOutput input) {
  float4 color = Shade(input);
  float z = input.position.z;
  float weight = max(min(1.0, max(max(color.r, color.g), color.b) * color.a), color.a) *
                 clamp(0.03 / (1e-5 + pow(z / 200.0, 4.0)), 1e-2, 3e3);

  PsOutput output;
  output.accumulation = float4(color.rgb * color.a, color.a) * weight;
  output.reveal = color.a;
  return output;
}
```

出力のコードの要点です。`weight` は McGuire らの、深度に基づく重み関数で、手前（z 小）ほど大きくなります。`output.accumulation` は `(RGB·α·w, α·w)` で、加算ブレンドで累積します。`output.reveal` は `α` で、乗算ブレンドにより `(1 − α)` の積が残ります。

### 合成

```hlsl
float4 PSComposite(VsOutput input) : SV_Target {
  float4 accum = accumulation_texture.Load(int3(input.position.xy, 0));
  float reveal = reveal_texture.Load(int3(input.position.xy, 0)).r;
  if (reveal >= 0.999) discard;
  float3 average_color = accum.rgb / max(accum.a, 1e-5);
  return float4(average_color, 1.0 - reveal);
}
```

合成のコードの要点です。`reveal`（背景の見える割合）が 1 なら、半透明が何もないので、描かずに捨てます。`average_color` は重み付き平均の色です。出力アルファ `1 − reveal` は、半透明全体の不透明度で、通常のアルファ ブレンドで背景に重ねます。

WBOIT の利点は、1 パスで軽いこと（2 枚の RT）、ソート不要なこと、パーティクル・草・髪などの大量の重なりに強いことです。欠点は、近似であること（同じ色の層が多いと順序が反映されません）、色が違う層の重なりで順序が違って見えること（手前の赤と奥の青が混ざって見える）、重み関数の調整が必要なこと（シーンの深度範囲に合わせます）です。

## よくあるミス

??? failure "半透明の重なりの色が、不自然"
    **重み関数を調整**する、または **PPLL**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **重み付き平均で、近似**
    - [x] **軽くて、実用的**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [OIT](index.md)
- [PPLL](ppll.md)
- [ハイブリッド](hybrid.md)
