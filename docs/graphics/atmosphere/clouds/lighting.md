---
title: Cloud Lighting
tags:
  - 描画
---

# Cloud Lighting

**雲は、光が内部で散乱するので、明るく、ふわふわに見えます**。**各点で太陽の方向にもう一度進んで、光の減衰（自己影）を求めます**。このページでは、**雲のライティング**を説明します。

!!! tip "ポイント"
    - **太陽方向へ、短くマーチして、光の減衰を求める**。
    - **位相関数（前方散乱）で、縁が光る**。
    - **多重散乱の近似を足して、暗くなりすぎを防ぐ**。
    - **パウダー効果で、縁が暗く沈む表現**。

## 光の計算
### Beer の法則

**太陽に向かって雲の中を進むと、水滴にぶつかって光が減ります**。**密度を太陽方向に積分した「厚み」から、届く光が決まります**。

<div class="formula">届く光 = exp( −厚み × 消散係数 )</div>

```hlsl
float LightMarch(float3 position, float3 sun_dir) {
  float optical_depth = 0;
  float step_length = kLightStepLength;
  for (int i = 1; i <= kLightStepCount; ++i) {
    float3 p = position + sun_dir * step_length * i;
    float density = CloudDensity(p, HeightFraction(p));
    optical_depth += density * step_length;
    step_length *= 1.5;
  }
  return optical_depth;
}
```

コードの要点です。サンプル数は 4〜6 個に抑えます。視線のサンプルごとに必要になるからです。ステップを伸ばしていく（`step *= 1.5`）のは、近くを細かく、遠くを粗くするためです。コストは、視線 N 回に光 M 回を掛けた量で、これが雲の描画が重い主な理由です。

### Powder 効果

**雲の縁（薄い所）は、Beer の法則だと「明るすぎる」ですが実際には暗いことがあります**。**散乱された光が雲の奥から出てこないため**です。**Powder 効果**は**これを近似**します。

<div class="formula">Powder = 1 − exp( −2 · density )</div>

```hlsl
float PowderEffect(float density) {
  return 1.0 - exp(-density * 2.0);
}
```

**Beer（薄いほど明るい）と Powder（薄いほど暗い）を掛ける**と**縁が暗く、中が明るい**という**実際の雲の見え方**に**近づきます**（**Beer-Powder**）。

### 位相関数

**雲の水滴は大きいため、光を前方に強く散らします**。**太陽の方を見ると雲の縁が銀色に光る（シルバーライニング）のはこれが理由**です。**前方ローブと後方ローブを混ぜた二重 Henyey-Greenstein** を使います。

```hlsl
float CloudPhase(float cos_theta) {
  float forward = HenyeyGreenstein(cos_theta, 0.8);
  float backward = HenyeyGreenstein(cos_theta, -0.3);
  return lerp(backward, forward, 0.7);
}
```

### 多重散乱の近似

**雲の中では光が何度も散らされ、明るく見えます**。**Beer の法則だけだと、厚い雲が暗くなりすぎます**。**消散・位相の寄与を数オクターブ分、減衰させながら足す近似**で、**厚い雲を適度に明るくします**。

```hlsl
float3 MultiScatteredLight(float optical_depth, float phase_cos) {
  float3 luminance = 0;
  float attenuation = 1.0;
  float contribution = 1.0;
  float phase_attenuation = 1.0;
  for (int octave = 0; octave < 4; ++octave) {
    float p = CloudPhaseWithG(phase_cos, 0.8 * phase_attenuation);
    luminance += contribution * p * exp(-optical_depth * attenuation) * sun_color;
    attenuation *= 0.5;
    contribution *= 0.5;
    phase_attenuation *= 0.5;
  }
  return luminance;
}
```

### 4 つの項目の関係

ここまでの要素が、雲の明るさにどう関わるかをまとめます。ある点の明るさは、次の形で書けます。

<div class="formula">L = 太陽光 × 位相関数 × 透過率（太陽まで）× Powder + 環境光</div>

太陽光は、太陽から来る光の強さです。位相関数は、散乱の方向依存性（前方に強く散らす）で、縁の銀色の輝き（シルバー ライニング）を作ります。太陽までの透過率は、Beer の法則で、雲の奥ほど暗くします（自己影）。Powder は、薄い縁を暗く沈ませる補正です。環境光は、空からの光で、太陽の当たらない雲の底面や影を青白く照らします。

雲の下側（底）は暗く、青みがかります。これは、雲の中を通り抜けた太陽光がほとんど残らず、空と地面からの環境光が主になるためです。環境光を考えずに太陽光だけで描くと、雲の底が真っ黒になって不自然です。環境光は、高さに応じて、底で暗く、上で明るくなるグラデーションにすると、簡単で効果的です。

### 多重散乱が必要な理由

厚い積乱雲の中心は、Beer の法則だけでは、太陽光が届かず真っ暗になってしまいます。しかし実際には、雲の中で光が何度も散乱して、雲全体が白く明るく見えます。多重散乱の近似（上のコード）は、この「何度も散乱した光」を、消散を弱めながら、位相関数を等方に近づけながら、数回分重ねて表現します。Wrenninge らの Production Volume Rendering（2012）で紹介された方法で、Schneider の Horizon Zero Dawn のあとも、Hillaire ら多くのゲーム エンジンの雲で使われています。

## よくあるミス

??? failure "雲が、のっぺり白い・立体感がない"
    **自己影（太陽方向のマーチ）**を**入れる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **自己影・前方散乱・多重散乱の近似**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Clouds](index.md)
- [Phase Functions](../scattering/phase-function.md)
- [Multiple Scattering](../scattering/multiple-scattering.md)
