---
title: 波頂の泡：ヤコビアン
tags:
  - 描画
---

# 波頂の泡：ヤコビアン

**波頭が尖って、メッシュが縮む所に、泡が出る**のが**自然な波**です。**この縮み具合を、ヤコビアンという値で測れます**。このページでは、**ヤコビアンによる波頂の泡**を説明します。

!!! tip "ポイント"
    - **ヤコビアン ＝ 水面の面積の変化率**。
    - **値が小さい（縮む）所に、泡が出る**。
    - **Gerstner 波・FFT で、計算できる**。
    - **しきい値を決めて、泡のマスクにする**。

## 波頂の泡：ヤコビアン
**波が尖りすぎると頂が折れて砕けます**。**折れる所は水平変位の面積が潰れる所**で、<strong>ヤコビアン（変位の面積比）</strong>で**検出できます**。

<strong>水面の位置を `P = P₀ + D(P₀)`（`D` は水平変位）</strong>とすると**面積の変化率**は**次の行列式**です。

<div class="formula">J = (1 + ∂Dx/∂x)(1 + ∂Dz/∂z) − (∂Dx/∂z)(∂Dz/∂x)</div>

| 値 | 意味 |
| --- | --- |
| **J = 1** | **面積が変わらない**（平らな水面） |
| **J > 1** | **広がっている**（谷） |
| **J < 1** | **縮んでいる**（波頂に向かって粒子が集まる） |
| **J ≤ 0** | **折れている**（粒子が追い越した）。**泡が出る** |

**Gerstner 波なら、解析的に求まります**。

```hlsl
float3 GerstnerJacobian(float2 position, GerstnerWave wave, float time) {
  float k = 2.0 * 3.14159265 / wave.wavelength;
  float phase = k * dot(wave.direction, position) + time * wave.speed * k;
  float s = sin(phase) * wave.steepness;
  return float3(wave.direction.x * wave.direction.x * s,
                wave.direction.y * wave.direction.y * s,
                wave.direction.x * wave.direction.y * s);
}

float jacobian = 1.0;
float3 sum = float3(0, 0, 0);
for (int i = 0; i < kWaveCount; ++i) {
  sum += GerstnerJacobian(position, waves[i], time);
}
jacobian = (1.0 - sum.x) * (1.0 - sum.y) - sum.z * sum.z;

float crest_mask = saturate((foam_threshold - jacobian) / foam_softness);
```

| 点 | 説明 |
| --- | --- |
| **`foam_threshold`** | **この値より J が小さいと、泡**（例：0.7）。**1 より小さい値** |
| **`foam_softness`** | **泡が立ち上がる幅**（例：0.3） |
| **FFT 海面** | **ヤコビアンを変位マップから計算してテクスチャに出す**（[波のジオメトリ](../waves/index.md)） |

**FFT では水平変位マップの差分**から**ヤコビアンを求め**、**別のテクスチャに書き出す**のが**定番**です。

## よくあるミス

??? failure "波頭に、泡がまったく出ない"
    **ヤコビアンのしきい値**を**調整**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **波が尖る所に、泡**
    - [x] **ヤコビアンで測る**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [岸辺の泡](index.md)
- [Gerstner 波](../waves/gerstner.md)
- [FFT 海面](../waves/fft-ocean.md)
