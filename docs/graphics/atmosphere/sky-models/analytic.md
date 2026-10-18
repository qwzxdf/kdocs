---
title: Analytic Sky Models
tags:
  - 描画
---

# Analytic Sky Models

<strong>Preetham や Hosek-Wilkie などは、太陽の位置と大気の濁りから空の色を式で求めるモデル</strong>です。<strong>グラデーションより物理的で、積分も要りません</strong>。このページでは解析的な空のモデルを説明します。

!!! tip "ポイント"
    - 太陽の高さと濁り（タービディティ）で、空の色が決まる。
    - Hosek-Wilkie は、Preetham より精度が高い。
    - 1 画素ごとに式を評価するだけ。
    - 宇宙からの視点には、向かない。

## 解析的な空のモデル
<strong>Preetham（1999）・Hosek-Wilkie（2012）</strong>は、<strong>空の輝度分布を少数のパラメータの数式で近似</strong>します。<strong>パラメータは太陽の高さ（天頂角）と、大気の濁り（turbidity）</strong>です。<strong>実測・シミュレーションにフィットさせた式</strong>なので、手作業のグラデーションより自然で、時刻による移り変わりも連続します。

### Preetham（Perez の式）

<strong>Perez の式</strong>で<strong>視線ごとの輝度（Y）と色度（x, y）</strong>を<strong>求めます</strong>。

<div class="formula">F(θ, γ) = (1 + A·e^(B / cos θ)) · (1 + C·e^(D·γ) + E·cos²γ)</div>

記号の意味です。θ は視線の天頂角（真上から何度か）、γ は視線と太陽のなす角です。A〜E は係数で turbidity（大気の濁り）から線形式で決まります。

<strong>最終的な空の輝度は天頂の輝度に比をかけて出します</strong>。

<div class="formula">Y = Y_zenith · F(θ, γ) / F(0, θ_sun)</div>

```hlsl
float Perez(float cos_theta, float gamma, float cos_gamma, PerezCoefficients coeff) {
  return (1.0 + coeff.A * exp(coeff.B / max(cos_theta, 0.01)))
       * (1.0 + coeff.C * exp(coeff.D * gamma) + coeff.E * cos_gamma * cos_gamma);
}
```

コードの要点です。`max(cos θ, 0.01)` は地平線で発散するのを防ぎます。xyY から RGB への変換は、色度 (x, y) と輝度 Y を、XYZ から sRGB（線形）へ変換する処理です。輝度が絶対値（cd/m²）なので、露出で合わせます。

### Hosek-Wilkie

<strong>Hosek-Wilkie</strong> は <strong>Preetham の改良版</strong>で、特に太陽が低いとき地面の反射率（アルベド）を考慮したときに精度が高いです。<strong>係数テーブル（9 つのパラメータ × 3 色 × turbidity × albedo × 高さ）</strong>を公開データとして持ち、式の形は Preetham に似ています。

| 項目 | Preetham | Hosek-Wilkie |
| --- | --- | --- |
| 精度 | 太陽が低いと不正確 | より正確 |
| パラメータ | turbidity | turbidity ＋ 地面のアルベド |
| データ | <strong>数式の係数のみ（少ない）</strong> | <strong>係数テーブルが必要（大きい）</strong> |
| 用途 | 軽量・手軽 | 品質重視 |


原典は Preetham らの "A Practical Analytic Model for Daylight"（SIGGRAPH 1999）と、Hosek と Wilkie の "An Analytic Model for Full Spectral Sky-Dome Radiance"（SIGGRAPH 2012）です。どちらも、実測や物理計算の結果を少数のパラメータの式にあてはめた経験式で、大気の散乱を直接は計算しません。そのため、非常に軽い代わりに地上の視点から見た空にしか使えず、宇宙から見た地球や遠景のかすみ（空気遠近法）は扱えません。

原典は Preetham らの "A Practical Analytic Model for Daylight"（SIGGRAPH 1999）と、Hosek と Wilkie の "An Analytic Model for Full Spectral Sky-Dome Radiance"（SIGGRAPH 2012）です。どちらも、実測や物理計算の結果を少数のパラメータの式にあてはめた経験式で、大気の散乱を直接は計算しません。そのため、非常に軽い代わりに地上の視点から見た空にしか使えず、宇宙から見た地球や遠景のかすみ（空気遠近法）は扱えません。

<strong>どちらも空の見た目だけ</strong>で<strong>大気の中を通る光（遠景の霞・光の筋）</strong>は<strong>別に計算</strong>する必要があります。そこは[Atmospheric Scattering](../scattering/index.md)の担当です。

## 解析的な空のモデル

<strong>解析的なモデル</strong>は <strong>観測や、シミュレーション</strong>の結果に数式を、当てはめたものです。太陽の高さと大気の濁り（turbidity）を、入れると空の各方向の色が式 1 つで、返ります。積分も LUT も不要です。

| モデル | 特徴 |
| --- | --- |
| Perez の式（1993） | 空の輝度の分布を、5 つの係数で表す古典的な式。後続のモデルの土台 |
| Preetham（1999） | Perez の式の係数を、濁りの関数として決めた。簡単で広く使われた。昼の空だけ（太陽が地平線より、上） |
| Hošek–Wilkie（2012） | Preetham より精度が高く太陽が、低いとき（朝夕）もうまく動く。スペクトル全体でフィット |

## Perez の式

空の <strong>ある方向の輝度</strong>を <strong>天頂の輝度に対する、割合</strong>として表します。

```text
F(θ, γ) = (1 + A × exp(B / cosθ)) × (1 + C × exp(D × γ) + E × cos²γ)

θ: 視線の、天頂角
γ: 視線と、太陽の、間の角度
A, B, C, D, E: 係数（天候・濁りで、決まる）
```

| 項 | 意味 |
| --- | --- |
| `(1 + A × exp(B / cosθ))` | 地平線に近づくほど、明るく（霞）。`A`、`B` が地平線の明るさを決める |
| `(1 + C × exp(D × γ) + E × cos²γ)` | 太陽の周りが明るい（`C`、`D`）。太陽と反対側のわずかな明るさ（`E`） |

```hlsl
// Perez の式（天頂に対する、割合）。coefficients は、A..E の 5 つ。
float PerezFunction(float cos_theta, float gamma, float cos_gamma, float A, float B, float C, float D, float E) {
  return (1.0 + A * exp(B / max(cos_theta, 0.01))) * (1.0 + C * exp(D * gamma) + E * cos_gamma * cos_gamma);
}
```

`cos_theta` が <strong>0 に近い</strong>（地平線）と `B / cosθ` が、<strong>大きな値</strong>になり `exp` が暴走するので、下限（`max(…, 0.01)`）を設けます。

## Preetham の使い方

Preetham は <strong>空の色</strong>を、<strong>CIE xyY 色空間</strong>で、Perez の式を 3 回（Y、x、y それぞれ）、計算して得ます。各係数は濁り `T` の 1 次式で、決まります。

```text
係数 A_Y = 0.1787 × T − 1.4630,  B_Y = −0.3554 × T + 0.4275,  C_Y = −0.0227 × T + 5.3251,
        D_Y = 0.1206 × T − 2.5771,  E_Y = −0.0670 × T + 0.3703
（x、y チャンネルにも、別の係数。論文の表を参照）
```

<strong>天頂の色</strong>（輝度 Y、色 x、y）も <strong>太陽の天頂角と濁り</strong>から式で、決まります。最終的な色は天頂の値 × `F(θ, γ) / F(0, θ_s)` です。

```hlsl
// Preetham の概略（輝度 Y のみ。色 x, y も、同様に、別の係数で計算する）。
float PreethamLuminance(float3 view_dir, float3 sun_dir, float turbidity) {
  float cos_theta = max(view_dir.y, 0.0);
  float cos_gamma = dot(view_dir, sun_dir);
  float gamma = acos(clamp(cos_gamma, -1.0, 1.0));
  float cos_theta_s = max(sun_dir.y, 0.0);

  // 濁り（turbidity）から、Perez の係数を求める（Y チャンネルの例）
  float A = 0.1787 * turbidity - 1.4630;
  float B = -0.3554 * turbidity + 0.4275;
  float C = -0.0227 * turbidity + 5.3251;
  float D = 0.1206 * turbidity - 2.5771;
  float E = -0.0670 * turbidity + 0.3703;

  float f_view = PerezFunction(cos_theta, gamma, cos_gamma, A, B, C, D, E);
  float f_zenith = PerezFunction(1.0, acos(cos_theta_s), cos_theta_s, A, B, C, D, E);
  float Y_zenith = ...;       // 天頂の輝度（太陽の天頂角と濁りから、論文の式で）
  return Y_zenith * f_view / f_zenith;
}
```

<strong>濁り（turbidity）</strong>は、<strong>2（非常に澄んだ）〜 10（霞んだ）</strong>の範囲を、使います。大きいほど空が白っぽく霞んで見えます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 実行時のコストが、小さい（数十命令）。事前計算も LUT も不要 |
| 長所 | パラメーターが、少ない（太陽の高さ濁り）。調整が簡単 |
| 長所 | 昼のリアルな空が、得られる |
| 短所 | 太陽が低い（朝夕）、地平線の下（薄明）では精度が、落ちる（Preetham）。Hošek–Wilkie で、改善 |
| 短所 | カメラが地上に固定。高い山、飛行機、宇宙では使えない |
| 短所 | 空気遠近法（遠景の霞）を、別の方法で与える必要がある（空の色と、整合させる） |
| 短所 | 大気のパラメーターを自由に、変えられない（濁り以外） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| 昼間の地上（時間帯があまり動かない） | 適している |
| 時間帯が動く（朝夕、夜） | Hošek–Wilkie、または Hillaire（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)） |
| 宇宙、高高度 | 使えない（大気散乱の方式を、使う） |
| 環境光（IBL）の元に使う | 空を、キューブマップに描いてライティングの、元にする（[Using the Sky for Lighting](sky-lighting.md)） |

## よくあるミス

??? failure "日没近くで、空の色が不自然"
    <strong>Hosek-Wilkie</strong> などの<strong>精度の高いモデル</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 式で空の色を求める。軽い

## 参考

- Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight", SIGGRAPH 1999
- Hošek, Wilkie, "An Analytic Model for Full Spectral Sky-Dome Radiance", ACM Transactions on Graphics (SIGGRAPH 2012)
- Perez, Seals, Michalsky, "All-Weather Model for Sky Luminance Distribution — Preliminary Configuration and Validation", Solar Energy, Vol. 50, No. 3, 1993
- Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017

## 関連ページ

- [Sky Models](index.md)
- [Atmospheric Scattering](../scattering/index.md)
