---
title: Wave Animation Tricks
tags:
  - 描画
---

# Wave Animation Tricks

<strong>波を動かすには、時間を進めるだけではなく、「繰り返しを隠す」「遠くを省く」といった工夫</strong>が必要です。このページでは、<strong>波のアニメーションの工夫</strong>を説明します。

!!! tip "ポイント"
    - 波の位相に、ノイズを足して、規則性を崩す。
    - 距離に応じて、波の数を減らす（LOD）。
    - 時間の値が大きくなると、精度が落ちるので、周期でリセットする。
    - 風向きと強さで、波のパラメータを切り替える。

## 波の動かし方の工夫
| 工夫 | 内容 |
| --- | --- |
| 距離で波の本数を減らす | 遠くは細かい波を省略（LOD）。ちらつきの防止 |
| 風向き・強さのパラメータ | 風の向きで波の向きを風の強さで振幅・波長を変える |
| 波長から速さを決める | 深い水の波は`速さ = √(g·λ / 2π)`（長い波ほど速い）。自然な分散 |
| ランダム化 | 波ごとの向きを基準の向きの周りでばらす |

<div class="formula">波の速さ c = √( g · λ / (2π) )　（g = 9.8 m/s²、λ = 波長）</div>

### 分散関係の意味

水の波は、波長によって進む速さが違います。長い波（うねり）は速く進み、短い波（さざ波）は遅いです。これを<strong>分散</strong>といいます。深い水では、角周波数 ω と波数 k（= 2π/λ）の関係が `ω = √(g·k)` になります（g は重力加速度 9.8 m/s²）。波長が 100 m の波は、速さ約 12.5 m/s、波長が 1 m の波は約 1.25 m/s です。

この関係を使わずに、すべての波を同じ速さで進ませると、波の形が変わらずに滑っていくだけで、人工的に見えます。分散関係を使えば、長い波が短い波を追い越していくので、波の模様が時間とともに変化し続け、海らしい不規則さが自然に出ます。

## 水深が、波の速さを決める（分散関係）

[Summing Sine Waves](sine-waves.md) では、深い水の速さ `c = √(gλ / 2π)` を、使いました。<strong>水深が、浅くなると</strong>、波の速さは、変わります。一般の式（線形波動論）は、次のとおりです。

```text
ω² = g × k × tanh(k × d)        ω: 角周波数、k: 波数（2π/λ）、d: 水深
c  = ω / k                       位相速度
```

| 水深 d と波長 λ の関係 | `tanh(kd)` | 速さ c | 呼び方 |
| --- | --- | --- | --- |
| `d > λ/2`（深い） | ≈ 1 | `√(gλ / 2π)`（波長で決まる） | 深水波 |
| `d < λ/20`（浅い） | ≈ kd | `√(g d)`（水深で決まる） | 浅水波 |
| その間 | 1 と kd の間 | 上の式で計算 | 中間 |

浅くなると、<strong>波長に関係なく、同じ速さ</strong>になり、岸に近づくと、<strong>波が、遅くなって、波長が、縮み、波頭が、切り立ちます</strong>。この、岸に向かって、波が、変わる様子が、海岸の、波らしさです。

```hlsl
// 水深を考慮した、波の角周波数。
float WaveOmega(float k, float depth) {
  return sqrt(9.81 * k * tanh(k * depth));
}
```

地形の水深（[Color by Water Depth](../shading/depth-color.md) の、水深マップ）を読んで、<strong>各場所で、速さを変える</strong>と、波が、岸に向かって、<strong>曲がる</strong>（屈折）様子も、出せます。ただし、位相を、場所ごとに、変えると、位相が、ずれていって、波が、ねじれます。実際には、波の向きを、水深の勾配に、少し寄せる程度の、簡易な方法が、使われます。

## 風と、波の関係

波のパラメーターは、<strong>風の強さ</strong>から、決められます。

| 風速 U（m/s） | 波の状態 | 有義波高 H（m）の目安 |
| --- | --- | --- |
| 3 | さざ波 | 0.1 |
| 6 | 小さな波 | 0.5 |
| 10 | 白波が立つ | 2 |
| 15 | 荒れた海 | 4〜5 |
| 20 | 大しけ | 8 |

<strong>十分に、風が吹き続けた海</strong>（完全に発達した海）では、波の高さは、風速の 2 乗に、ほぼ比例します（Pierson と Moskowitz、1964）。

```text
有義波高 H ≈ 0.21 × U² / g
最も強い波の波長 λ_peak ≈ 2π U² / (1.13² × g)   ≈ 0.5 × U² （m）
```

風速 10 m/s なら、有義波高が、約 2 m、最も強い波の波長が、約 50〜60 m です。ゲームの設定画面や、天候システムの、風の強さから、波の振幅・波長を、計算できます。

```cpp
// 風速から、波のパラメーターを決める（完全に発達した海の近似）。
struct SeaState { float significant_height; float peak_wavelength; };
SeaState FromWindSpeed(float u) {
  const float g = 9.81f;
  return {0.21f * u * u / g, 0.5f * u * u};
}
```

<strong>天候が変わる</strong>（風が強くなる）とき、波の振幅を、<strong>急に変えると、水面が、ぱっと、動きます</strong>。パラメーターを、時間をかけて、補間します。

## 波の LOD

遠くの水面は、細かい波が、<strong>ちらつく</strong>ので、省きます。

| 距離 | 使う波 |
| --- | --- |
| 近い（〜30 m） | すべての波 + 法線マップ |
| 中間（30〜150 m） | 短い波を、減らす（振幅を、0 に近づける） |
| 遠い（150 m〜） | 長いうねりだけ。法線は、弱める |

```hlsl
// 波ごとに、距離に応じて、振幅を弱める。短い波は、近くまでしか見えない。
float visible_dist = wavelength * 40.0;              // 波長の約 40 倍まで見える
float fade = saturate(1.0 - dist / visible_dist);
amplitude *= fade;
```

<strong>波の本数を、変える</strong>よりも、<strong>振幅を、連続的に、減らす</strong>ほうが、切り替えのポップが出ません。

## 規則性を崩す

波が、<strong>同じ形で、一定の方向に、進み続ける</strong>と、機械的に見えます。

| 工夫 | 内容 |
| --- | --- |
| 向きを、ばらす | 波ごとの向きを、風向きの周りに、±30 度くらい、ばらつかせる |
| 波長を、不規則に | 波長を、等比数列にせず、少し、乱数で、ずらす |
| 位相に、ノイズ | 位置に依存する、低周波のノイズを、位相に足す。波頭が、まっすぐに、並ばない |
| 振幅の変動 | 振幅を、低周波のノイズで、場所ごとに、変える（波の、強い所と、弱い所） |
| 時間に、ゆらぎ | 振幅を、時間でも、ゆっくり、変える（突風、静けさ） |

```hlsl
// 位相に、位置に依存する、ゆらぎを足す。
float noise = g_noise.SampleLevel(g_linear_wrap, p * 0.01, 0);        // 低周波ノイズ
float phase = k * dot(dir, p) + omega * time + noise * 2.0;           // 位相を、最大 2 rad ずらす
```

## 時間の精度

`time` を、`float` で、増やし続けると、<strong>数時間後に、精度が落ち</strong>ます。`sin(omega × time)` の位相が、粗くなり、<strong>波の動きが、カクカクします</strong>。

| 経過時間 | `float` の精度（時間の刻み） |
| --- | --- |
| 1 分 | 約 0.000004 秒 |
| 1 時間 | 約 0.0002 秒 |
| 10 時間 | 約 0.002 秒（60 fps の、フレーム 1 つが 0.0167 秒なので、まだ、十分） |
| 100 時間 | 約 0.015 秒（フレーム 1 つと、同程度。動きが、粗くなる） |

位相は、`omega × time` なので、`omega` が大きい（短い波）と、<strong>位相の誤差が、さらに増幅</strong>されます。

<strong>対策：時間を、周期で折り返す</strong>。すべての波の周期の、<strong>公倍数</strong>で、折り返すと、継ぎ目が出ません。

```cpp
// 全ての波の周期の、最小公倍数に近い値で、折り返す。
// 周期を、きれいな値にそろえておくと、公倍数を、小さくできる。
float WrapTime(float t, float common_period) {
  return std::fmod(t, common_period);
}

// 周期を、そろえた波の作り方: ω を、基本の角周波数の整数倍にする
// ω_i = round(ω_i / ω_base) × ω_base   → 周期 2π/ω_base で、全体が一巡する。
```

波の角周波数を、<strong>基本の角周波数の、整数倍に、丸める</strong>と、全体の周期が、`2π / ω_base` に、収まり、その周期で、<strong>継ぎ目なく</strong>、折り返せます（波の速さは、わずかに、変わりますが、見た目では、気づきません）。

## よくあるミス

??? failure "長時間プレイすると、波がカクつく"
    <strong>時間を周期でラップ</strong>させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ノイズで規則性を崩し、遠くは省く
    - [x] 時間は周期でラップ

## 参考

- Pierson, Moskowitz, "A Proposed Spectral Form for Fully Developed Wind Seas Based on the Similarity Theory of S. A. Kitaigorodskii", Journal of Geophysical Research, Vol. 69, 1964
- Finch, "Effective Water Simulation from Physical Models", GPU Gems, Chapter 1, 2004（サイン波と Gerstner 波の、GPU 実装）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（FFT による海面の合成。ほとんどの FFT 海面の、出発点）
- Hasselmann et al., "Measurements of Wind-Wave Growth and Swell Decay during the Joint North Sea Wave Project (JONSWAP)", Deutsche Hydrographische Zeitschrift, Reihe A, Vol. 8, No. 12, 1973

## 関連ページ

- [Water Waves](index.md)
- [Summing Sine Waves](sine-waves.md)
