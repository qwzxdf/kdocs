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

### 考え方

**手前の物ほど、重みを大きく**して、**平均**します。**順序を知らなくても、「手前らしさ」を深度から推定**して、**近似的な順序づけ**を得ます。

<div class="formula">C = Σ(Cᵢ · αᵢ · wᵢ) / Σ(αᵢ · wᵢ)　、　α_total = 1 − Π(1 − αᵢ)</div>

| 記号 | 意味 |
| --- | --- |
| **wᵢ** | **層 i の重み**（**深度が小さい＝手前ほど大きい**） |
| <strong>Σ(Cᵢ αᵢ wᵢ)</strong> | **重み付きの色の合計**（**アキュムレーション**） |
| <strong>Π(1 − αᵢ)</strong> | **全層の透過率の積**（<strong>リビール（背景の見える割合）</strong>） |

### 2 枚のレンダー ターゲット

| ターゲット | フォーマット | 内容 | ブレンド |
| --- | --- | --- | --- |
| **アキュムレーション** | `R16G16B16A16_FLOAT` | **`(Cᵢ·αᵢ·wᵢ, αᵢ·wᵢ)`** を**加算** | **ONE / ONE**（加算） |
| **リビール** | `R8_UNORM` | **`αᵢ`** を**透過率として乗算** | **ZERO / INV_SRC_COLOR**（`(1 − αᵢ)` を掛ける） |

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

| 点 | 説明 |
| --- | --- |
| **`weight`** | **McGuire らの、深度に基づく重み関数**。**手前（z 小）ほど大きい** |
| **`output.accumulation`** | **`(RGB·α·w, α·w)`**。**加算ブレンド**で**累積** |
| **`output.reveal`** | **`α`**。**乗算ブレンド**で、**`(1 − α)` の積**が**残る** |

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

| 点 | 説明 |
| --- | --- |
| <strong>`reveal`（背景の見える割合）</strong> | **1 なら、半透明が何もない**（**描かずに捨てる**） |
| **`average_color`** | **重み付き平均の色** |
| **出力アルファ `1 − reveal`** | **半透明全体の、不透明度**。**通常のアルファ ブレンドで、背景に重ねる** |

| 利点 | 欠点 |
| --- | --- |
| **1 パス・軽い**（**2 枚の RT**） | **近似**（**同じ色の層が多いと、順序が反映されない**） |
| **ソート不要** | **色が違う層の重なりで、順序が違う**（**手前の赤と奥の青が、混ざって見える**） |
| **パーティクル・草・髪などの大量の重なりに強い** | **重み関数の調整**が必要（**シーンの深度範囲**） |

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
