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

<!-- fig:cloud-beer-powder:begin -->

<svg class="fig illust motion" data-fig="cloud-beer-powder" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-beer-powder" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Beer（奥ほど暗い）× Powder（縁は暗い）= 縁が暗く、中が明るい雲</text>
<rect x="70" y="70" width="640" height="250" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="132.5" x2="710" y2="132.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="195.0" x2="710" y2="195.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="257.5" x2="710" y2="257.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">明るさ</text>
<text x="710" y="356" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">光が雲の中を通った厚み（密度の積分）</text>
<path d="M70.0,81.9 L76.4,88.94 L82.8,95.77 L89.2,102.4 L95.6,108.83 L102.0,115.07 L108.4,121.13 L114.8,127.0 L121.2,132.71 L127.6,138.24 L134.0,143.61 L140.4,148.83 L146.8,153.89 L153.2,158.8 L159.6,163.56 L166.0,168.18 L172.4,172.67 L178.8,177.02 L185.2,181.25 L191.6,185.35 L198.0,189.33 L204.4,193.19 L210.8,196.94 L217.2,200.58 L223.6,204.11 L230.0,207.53 L236.4,210.86 L242.8,214.08 L249.2,217.21 L255.6,220.25 L262.0,223.2 L268.4,226.06 L274.8,228.84 L281.2,231.53 L287.6,234.14 L294.0,236.68 L300.4,239.14 L306.8,241.53 L313.2,243.85 L319.6,246.1 L326.0,248.29 L332.4,250.41 L338.8,252.46 L345.2,254.46 L351.6,256.4 L358.0,258.28 L364.4,260.1 L370.8,261.87 L377.2,263.59 L383.6,265.26 L390.0,266.87 L396.4,268.44 L402.8,269.97 L409.2,271.45 L415.6,272.88 L422.0,274.27 L428.4,275.63 L434.8,276.94 L441.2,278.21 L447.6,279.44 L454.0,280.64 L460.4,281.81 L466.8,282.94 L473.2,284.03 L479.6,285.09 L486.0,286.13 L492.4,287.13 L498.8,288.1 L505.2,289.04 L511.6,289.96 L518.0,290.84 L524.4,291.71 L530.8,292.54 L537.2,293.35 L543.6,294.14 L550.0,294.9 L556.4,295.65 L562.8,296.37 L569.2,297.06 L575.6,297.74 L582.0,298.4 L588.4,299.04 L594.8,299.66 L601.2,300.26 L607.6,300.84 L614.0,301.41 L620.4,301.96 L626.8,302.49 L633.2,303.01 L639.6,303.51 L646.0,304.0 L652.4,304.47 L658.8,304.93 L665.2,305.38 L671.6,305.81 L678.0,306.23 L684.4,306.63 L690.8,307.03 L697.2,307.41 L703.6,307.78 L710.0,308.15" fill="none" stroke="#2563eb" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></path>
<text x="90" y="100" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">Beer  exp(−d)<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,320.0 L76.4,306.13 L82.8,293.08 L89.2,280.78 L95.6,269.2 L102.0,258.29 L108.4,248.02 L114.8,238.34 L121.2,229.23 L127.6,220.65 L134.0,212.57 L140.4,204.96 L146.8,197.8 L153.2,191.05 L159.6,184.69 L166.0,178.71 L172.4,173.07 L178.8,167.76 L185.2,162.76 L191.6,158.05 L198.0,153.62 L204.4,149.44 L210.8,145.51 L217.2,141.8 L223.6,138.32 L230.0,135.03 L236.4,131.94 L242.8,129.02 L249.2,126.28 L255.6,123.7 L262.0,121.26 L268.4,118.97 L274.8,116.81 L281.2,114.78 L287.6,112.86 L294.0,111.06 L300.4,109.36 L306.8,107.76 L313.2,106.26 L319.6,104.84 L326.0,103.5 L332.4,102.25 L338.8,101.06 L345.2,99.95 L351.6,98.9 L358.0,97.91 L364.4,96.97 L370.8,96.1 L377.2,95.27 L383.6,94.49 L390.0,93.76 L396.4,93.07 L402.8,92.42 L409.2,91.81 L415.6,91.23 L422.0,90.69 L428.4,90.18 L434.8,89.69 L441.2,89.24 L447.6,88.81 L454.0,88.41 L460.4,88.03 L466.8,87.67 L473.2,87.34 L479.6,87.02 L486.0,86.72 L492.4,86.44 L498.8,86.18 L505.2,85.93 L511.6,85.7 L518.0,85.48 L524.4,85.27 L530.8,85.07 L537.2,84.89 L543.6,84.71 L550.0,84.55 L556.4,84.4 L562.8,84.25 L569.2,84.11 L575.6,83.99 L582.0,83.86 L588.4,83.75 L594.8,83.64 L601.2,83.54 L607.6,83.45 L614.0,83.36 L620.4,83.27 L626.8,83.19 L633.2,83.12 L639.6,83.05 L646.0,82.98 L652.4,82.92 L658.8,82.86 L665.2,82.8 L671.6,82.75 L678.0,82.7 L684.4,82.66 L690.8,82.61 L697.2,82.57 L703.6,82.53 L710.0,82.49" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3040;0.3043;1.0000" values="0;0;1;1"/></path>
<text x="90" y="120" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">Powder  1 − exp(−2d)<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3040;0.3043;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,320.0 L76.4,293.09 L82.8,269.29 L89.2,248.31 L95.6,229.88 L102.0,213.77 L108.4,199.75 L114.8,187.62 L121.2,177.2 L127.6,168.32 L134.0,160.83 L140.4,154.6 L146.8,149.49 L153.2,145.39 L159.6,142.19 L166.0,139.82 L172.4,138.16 L178.8,137.16 L185.2,136.74 L191.6,136.83 L198.0,137.37 L204.4,138.32 L210.8,139.63 L217.2,141.24 L223.6,143.13 L230.0,145.25 L236.4,147.58 L242.8,150.09 L249.2,152.74 L255.6,155.52 L262.0,158.4 L268.4,161.37 L274.8,164.4 L281.2,167.49 L287.6,170.62 L294.0,173.77 L300.4,176.94 L306.8,180.11 L313.2,183.28 L319.6,186.44 L326.0,189.59 L332.4,192.7 L338.8,195.79 L345.2,198.85 L351.6,201.87 L358.0,204.85 L364.4,207.78 L370.8,210.67 L377.2,213.51 L383.6,216.3 L390.0,219.04 L396.4,221.72 L402.8,224.35 L409.2,226.93 L415.6,229.45 L422.0,231.92 L428.4,234.33 L434.8,236.69 L441.2,238.99 L447.6,241.24 L454.0,243.44 L460.4,245.58 L466.8,247.67 L473.2,249.7 L479.6,251.69 L486.0,253.62 L492.4,255.51 L498.8,257.34 L505.2,259.13 L511.6,260.87 L518.0,262.56 L524.4,264.21 L530.8,265.81 L537.2,267.37 L543.6,268.89 L550.0,270.37 L556.4,271.8 L562.8,273.2 L569.2,274.56 L575.6,275.87 L582.0,277.16 L588.4,278.4 L594.8,279.61 L601.2,280.79 L607.6,281.93 L614.0,283.04 L620.4,284.12 L626.8,285.17 L633.2,286.19 L639.6,287.18 L646.0,288.14 L652.4,289.08 L658.8,289.98 L665.2,290.86 L671.6,291.72 L678.0,292.55 L684.4,293.35 L690.8,294.14 L697.2,294.9 L703.6,295.63 L710.0,296.35" fill="none" stroke="#e5484d" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></path>
<text x="90" y="140" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">積（Beer × Powder）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">雲の明るさを、2 つの項で決める<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">Beer: 厚いほど光が減る（縁が最も明るくなってしまう）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.3040;0.3043;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">Powder: 薄い縁は、内側から出る光が少なく暗い<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3040;0.3043;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">掛け合わせて、中間の厚みが最も明るい（積を 2 倍して表示）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-beer-powder:end -->

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
