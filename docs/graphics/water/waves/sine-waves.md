---
title: サイン波の重ね合わせ
tags:
  - 描画
---

# サイン波の重ね合わせ

**水面の高さを、複数のサイン波の足し合わせで表す**のが**最も簡単な方法**です。**波ごとに、向き・波長・振幅・速さを変える**と、**それらしい波**になります。このページでは、**サイン波の式と、パラメータの決め方**を説明します。

!!! tip "ポイント"
    - **高さ ＝ Σ 振幅 × sin(向き・位置 × 周波数 ＋ 時間 × 速さ)**。
    - **波は 4〜8 本**が**目安**。
    - **向きをばらつかせる**と、**規則的に見えない**。
    - **波長と振幅は、比例させる**（長い波ほど大きい）。

## サイン波の重ね合わせ
**1 本のサイン波**は、**進行方向 `D`・波長 `λ`・振幅 `A`・速さ `s`** で決まります。

<div class="formula">h(x, z, t) = A · sin( ω · (D · (x, z)) + φ · t )　（ω = 2π/λ、φ = s · ω）</div>

| 記号 | 意味 |
| --- | --- |
| **A** | **振幅**（波の高さの半分） |
| **λ** | **波長**（波頭から次の波頭までの距離）。**ω = 2π / λ** が**波数** |
| **D** | **波の進む向き**（2D の単位ベクトル） |
| **s** | **波の速さ**。**φ = s · ω** |
| **t** | **時間** |

```hlsl
struct Wave {
  float2 direction;
  float amplitude;
  float wavelength;
  float speed;
};

float WaveHeight(float2 position, Wave wave, float time) {
  float frequency = 2.0 * 3.14159265 / wave.wavelength;
  float phase = wave.speed * frequency;
  return wave.amplitude * sin(dot(wave.direction, position) * frequency + time * phase);
}
```

**方向・波長・振幅を変えた波を、4〜8 本重ね**ると**ランダムな海面**に見えます。**波長を倍々に（大きい波から小さい波へ）、振幅を半分ずつ**と**減らす**のが**定番**です。

| 波 | 波長 | 振幅 | 向き |
| --- | --- | --- | --- |
| **1** | 長い（例：20 m） | 大 | 風向き |
| **2** | 中 | 中 | 少しずらす |
| **3** | 短い | 小 | さらにずらす |
| **4** | 非常に短い | 極小 | 別の向き |

**欠点**：**サイン波は波頂が丸く、谷も同じ形**で**海の「尖った波頂・広い谷」の形にならない**。

## よくあるミス

??? failure "波が、規則的な縞に見える"
    **向き・波長をばらつかせる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **サイン波を足して、波を作る**
    - [x] **向きと波長をばらつかせる**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水面の波](index.md)
- [Gerstner 波](gerstner.md)
