---
title: fBm（フラクショナル ブラウン運動）
tags:
  - 描画
---

# fBm（フラクショナル ブラウン運動）

**fBm は、ノイズを、周波数を倍にしながら、振幅を半分にして、何層も重ねる手法**で、**自然な地形の基本**です。**山の大きな形から、細かい凹凸まで**を**1 つの式で作れます**。このページでは、**fBm のパラメータ**を説明します。

!!! tip "ポイント"
    - **オクターブ ＝ 重ねる層の数**。
    - **ラクナリティ ＝ 周波数の倍率（約 2）**。
    - **ゲイン ＝ 振幅の倍率（約 0.5）**。
    - **オクターブが多いと、細かいが、重い**。

## fBm（フラクショナル ブラウン運動）
**自然の地形は大きな山、小さな丘、岩、砂粒とどの縮尺でも起伏があります**（**自己相似**）。**ノイズを周波数を上げ、振幅を下げながら足し合わせる**と、**この性質を再現できます**。

<div class="formula">fBm(p) = Σ  gain^i · noise( p · lacunarity^i )　（i = 0 … オクターブ数 − 1）</div>

| パラメータ | 意味 |
| --- | --- |
| **オクターブ数** | **重ねる層の数**（普通 4〜8）。**多いほど細かい起伏** |
| <strong>lacunarity（周波数の倍率）</strong> | **層ごとに周波数を何倍にするか**（**通常 2.0**） |
| <strong>gain（振幅の倍率）</strong> | **層ごとに振幅を何倍にするか**（**通常 0.5**）。**小さいと滑らか、大きいとギザギザ** |

```hlsl
float Fbm(float2 p, int octaves, float lacunarity, float gain) {
  float sum = 0.0;
  float amplitude = 1.0;
  float max_amplitude = 0.0;
  for (int i = 0; i < octaves; ++i) {
    sum += amplitude * PerlinNoise(p);
    max_amplitude += amplitude;
    p *= lacunarity;
    amplitude *= gain;
  }
  return sum / max_amplitude;
}
```

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="fBm">
<text x="20" y="24" class="fig-title">fBm：周波数を上げ、振幅を下げた層を足す</text>
<polyline fill="none" stroke="#4c8bf5" stroke-width="2" points="40,60 120,45 200,70 280,55 360,60 440,48 520,66 600,52 680,58 740,50"/>
<text x="40" y="38" style="font-size:12px">1 層目：大きな起伏</text>
<polyline fill="none" stroke="#2ea043" stroke-width="2" points="40,125 70,120 100,130 130,118 160,128 190,121 220,131 250,119 280,127 310,120 340,130 370,122 400,128 430,120 460,131 490,119 520,127 550,121 580,130 610,120 640,128 670,121 700,129 740,123"/>
<text x="40" y="106" style="font-size:12px">2 層目：細かく、小さい</text>
<polyline fill="none" stroke="currentColor" stroke-width="3" points="40,205 70,188 100,214 130,190 160,208 190,185 220,215 250,188 280,206 310,186 340,214 370,190 400,205 430,184 460,214 490,189 520,208 550,186 580,213 610,189 640,206 670,187 700,212 740,190"/>
<text x="40" y="170" style="font-size:12px">合計：大きな起伏の上に細かい起伏</text>
</svg>

| 点 | 説明 |
| --- | --- |
| **`max_amplitude` で割る** | **値の範囲を揃える**（0〜1 などに） |
| **層ごとに位置をずらす** | **各層で座標をずらす**と**格子の揃いが目立たない** |
| **高さの調整** | **fBm の結果にカーブ（べき乗など）を掛けて、平地と山の比率を調整** |

## よくあるミス

??? failure "地形が、のっぺりしている"
    **オクターブを増やす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **周波数を倍・振幅を半分で、重ねる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形の生成](index.md)
- [リッジ ノイズ](ridge.md)
