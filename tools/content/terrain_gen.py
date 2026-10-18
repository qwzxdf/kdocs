import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

PERLIN85 = '''Perlin, "An Image Synthesizer", SIGGRAPH 1985（Perlin ノイズの原典）'''
PERLIN02 = '''Perlin, "Improving Noise", SIGGRAPH 2002（補間関数を 5 次式にし、勾配の選び方を直した改良版）'''
EBERT = '''Ebert, Musgrave, Peachey, Perlin, Worley, "Texturing and Modeling: A Procedural Approach", 3rd Edition, Morgan Kaufmann, 2002（fBm、マルチフラクタル、リッジ ノイズ）'''
MANDELBROT = '''Mandelbrot, Van Ness, "Fractional Brownian Motions, Fractional Noises and Applications", SIAM Review, Vol. 10, No. 4, 1968（fBm の原典）'''
MUSGRAVE89 = '''Musgrave, Kolb, Mace, "The Synthesis and Rendering of Eroded Fractal Terrains", SIGGRAPH 1989'''
QUILEZ_FBM = '''Quilez, "fBm" と "Domain Warping", iquilezles.org（ノイズの重ね合わせと、座標のゆがめ方の解説）'''
QUILEZ_DERIV = '''Quilez, "Value Noise Derivatives" / "Gradient Noise Derivatives", iquilezles.org（ノイズの解析的な微分を使った、侵食に見える地形）'''
HASH = '''Jarzynski, Olano, "Hash Functions for GPU Rendering", Journal of Computer Graphics Techniques, Vol. 9, No. 3, 2020'''
MEI = '''Mei, Decaudin, Hu, "Fast Hydraulic Erosion Simulation and Visualization on GPU", Pacific Graphics 2007'''
STAVA = '''Št'ava, Beneš, Brisbin, Křivánek, "Interactive Terrain Modeling Using Hydraulic Erosion", Symposium on Computer Animation 2008'''
OLSEN = '''Olsen, "Realtime Procedural Terrain Generation", University of Southern Denmark, 2004（熱による侵食と水による侵食の、単純な実装）'''
BEYER = '''Beyer, "Implementation of a Method for Hydraulic Erosion", Master's thesis, TU München, 2015（粒子（水滴）による侵食）'''
GENEVAUX = '''Génevaux, Galin, Guérin, Peytavie, Beneš, "Terrain Generation Using Procedural Models Based on Hydrology", ACM Transactions on Graphics (SIGGRAPH 2013)'''
GALIN = '''Galin, Guérin, Peytavie, Cordonnier, Cani, Beneš, Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR)'''
BARNES = '''Barnes, Lehman, Mulla, "Priority-Flood: An Optimal Depression-Filling and Watershed-Labeling Algorithm for Digital Elevation Models", Computers & Geosciences, Vol. 62, 2014'''
BRIDSON = '''Bridson, "Fast Poisson Disk Sampling in Arbitrary Dimensions", SIGGRAPH 2007 Sketches'''
LAGAE = '''Lagae, Dutré, "A Comparison of Methods for Generating Poisson Disk Distributions", Computer Graphics Forum, Vol. 27, No. 1, 2008'''
MUIJDEN = '''van Muijden, "GPU-Based Run-Time Procedural Placement in Horizon Zero Dawn", Game Developers Conference 2017'''

# ---------------------------------------------------------------- fbm
pg.Dedup("terrain/generation/fbm.md")
pg.Add("terrain/generation/fbm.md", '''
## fBm とは、何を足しているのか

fBm（fractional Brownian motion、分数ブラウン運動）は、もともとは、確率過程の名前です（Mandelbrot と Van Ness、1968）。地形の分野では、**「周波数が 2 倍になるたびに、振幅が、一定の割合で小さくなる、ノイズの重ね合わせ」**という意味で使います。

自然の山は、大きな起伏の上に、小さな起伏があり、その上にまた小さな起伏がある、という**自己相似**の形をしています。ノイズを、1 つだけ使うと、同じ大きさの、なだらかな丘しか作れません。**大きさの違うノイズを重ねる**と、山らしい形になります。

```text
オクターブ 0:  大きな起伏    周波数 1,   振幅 1
オクターブ 1:  中くらい       周波数 2,   振幅 0.5
オクターブ 2:  細かい         周波数 4,   振幅 0.25
オクターブ 3:  さらに細かい    周波数 8,   振幅 0.125
合計 = 山
```

## 式とパラメーター

```text
fBm(p) = Σ  gain^i × noise(p × lacunarity^i)         （i = 0, 1, …, octaves − 1）
```

| パラメーター | 一般的な値 | 意味 |
| --- | --- | --- |
| `octaves`（オクターブ数） | 4〜8 | 重ねる回数。多いほど細かいが、重い |
| `lacunarity`（空隙度） | 2.0 | 周波数が、毎回何倍になるか |
| `gain`（持続度、persistence） | 0.5 | 振幅が、毎回何倍になるか |

### gain と、地形の粗さ

`gain` が大きいと、細かい起伏が強く残り、**ごつごつ**した地形になります。小さいと、**なだらか**になります。理論的には、**ハースト指数 H**（0〜1）と、次の関係があります。

```text
gain = lacunarity^(−H)        （lacunarity = 2 なら、gain = 2^(−H)）
```

| H | gain | 見た目 |
| --- | --- | --- |
| 1.0 | 0.5 | なだらかで、滑らか |
| 0.5 | 0.707 | 標準的な山 |
| 0.0 | 1.0 | 非常にごつごつ（ホワイト ノイズに近い） |

`gain = 0.5`、`lacunarity = 2` は、H = 1 に当たり、なだらかな地形になります。ごつごつした山には、`gain = 0.6〜0.7` に上げます。

### 振幅の合計と正規化

オクターブごとの最大の振幅の合計は、`gain` の等比数列の和です。

```text
合計 = (1 − gain^octaves) / (1 − gain)
```

`gain = 0.5`、8 オクターブなら、約 1.99 です。**合計で割って、−1〜1（または 0〜1）に、収める**と、あとの計算（高さの変換）が、扱いやすくなります。

## 勾配ノイズ（Perlin ノイズ）

fBm の、土台になるノイズです。整数の格子点に、**ランダムな向きの勾配（ベクトル）**を置いて、その間を滑らかに補間します（Perlin、1985）。

```hlsl
// 整数のハッシュ（PCG）。sin を使うハッシュは、GPU によって結果が違うので、使わない。
uint Pcg(uint v) {
  uint state = v * 747796405u + 2891336453u;
  uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
  return (word >> 22u) ^ word;
}

float2 GradientAt(int2 p, uint seed) {
  uint h = Pcg(p.x + Pcg(p.y + seed));
  float angle = (h & 0xffffu) * (6.2831853 / 65536.0);
  return float2(cos(angle), sin(angle));      // 長さ 1 の勾配
}

float GradientNoise(float2 p, uint seed) {
  int2 i = (int2)floor(p);
  float2 f = frac(p);
  // 5 次式の補間（Perlin 2002）。3 次式（f*f*(3-2f)）より、格子の目立ちが、少ない。
  float2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);

  float a = dot(GradientAt(i + int2(0, 0), seed), f - float2(0, 0));
  float b = dot(GradientAt(i + int2(1, 0), seed), f - float2(1, 0));
  float c = dot(GradientAt(i + int2(0, 1), seed), f - float2(0, 1));
  float d = dot(GradientAt(i + int2(1, 1), seed), f - float2(1, 1));
  return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y) * 1.4142;   // おおよそ -1〜1
}
```

| 種類 | 内容 | 特徴 |
| --- | --- | --- |
| 値ノイズ（value noise） | 格子点に、ランダムな**値**を置いて補間 | 安いが、格子の形が、目立つ |
| 勾配ノイズ（Perlin） | 格子点に、ランダムな**向き**を置く | 自然。地形の標準 |
| シンプレックス ノイズ | 三角形の格子を使う | 次元が上がっても速い。方向の偏りが少ない |

## fBm の実装

```hlsl
float Fbm(float2 p, int octaves, float lacunarity, float gain, uint seed) {
  float sum = 0.0;
  float amplitude = 1.0;
  float norm = 0.0;
  for (int i = 0; i < octaves; ++i) {
    sum += amplitude * GradientNoise(p, seed + i);   // オクターブごとに、種を変える
    norm += amplitude;
    p *= lacunarity;
    amplitude *= gain;
  }
  return sum / norm;     // -1〜1 に収める
}
```

!!! warning "同じノイズを、そのまま重ねない"
    オクターブごとに、**座標をずらす**か、**種（seed）を変える**ことをします。同じ種で、周波数だけを 2 倍にすると、**格子点（座標 0）で、すべてのオクターブが、同時に 0 になり、原点の周りに、模様の偏りが出ます**。

## 計算シェーダーで、高さマップを作る

CPU で、数百万画素のノイズを計算すると、数秒かかります。**計算シェーダー（Compute Shader）**で行うと、数ミリ秒で終わります。

```hlsl
RWTexture2D<float> g_height : register(u0);   // R32_FLOAT、または R16_UNORM

cbuffer GenCB : register(b0) {
  float2 world_origin;     // このタイルの、左下のワールド座標
  float texel_size;        // 1 テクセルの、メートル
  float frequency;         // 基本の周波数（1 / メートル）
  int octaves;
  float lacunarity;
  float gain;
  uint seed;
};

[numthreads(8, 8, 1)]
void main(uint3 id : SV_DispatchThreadID) {
  // ワールド座標で、ノイズを計算する。
  // 隣のタイルも、同じ式なので、境界が、自動的に、つながる。
  float2 world = world_origin + float2(id.xy) * texel_size;
  float h = Fbm(world * frequency, octaves, lacunarity, gain, seed);
  g_height[id.xy] = h * 0.5 + 0.5;   // 0〜1 にして保存
}
```

```cpp
// C++ 側: 1024×1024 の高さマップを作る。
context->CSSetShader(noise_cs.Get(), nullptr, 0);
context->CSSetUnorderedAccessViews(0, 1, height_uav.GetAddressOf(), nullptr);
context->CSSetConstantBuffers(0, 1, gen_cb.GetAddressOf());
context->Dispatch(1024 / 8, 1024 / 8, 1);       // 8×8 スレッドのグループを、並べる
```

**座標を、ワールド座標で計算する**ことが、チャンク分割された地形で、継ぎ目を作らない、鍵です。タイル内の座標（0〜1）で計算すると、タイルごとに別のノイズになって、境界が合いません。

## 解析的な微分で、侵食らしく見せる

fBm のオクターブごとに、ノイズの**傾き（勾配）**も同時に計算できます。傾きが急な場所では、小さい起伏の振幅を、減らすと、**水で削られたように、斜面がなめらかで、谷底に細かい起伏が残る**地形になります（Quilez）。

```hlsl
// 勾配ノイズの値と、勾配（2 成分）を、同時に返す。
float3 GradientNoiseD(float2 p, uint seed);   // x = 値, yz = 勾配

float FbmEroded(float2 p, int octaves, float lacunarity, float gain, uint seed) {
  float sum = 0.0;
  float amplitude = 0.5;
  float2 slope_sum = 0.0;
  for (int i = 0; i < octaves; ++i) {
    float3 n = GradientNoiseD(p, seed + i);
    slope_sum += n.yz;
    // 傾きが、これまでに、急になっているほど、このオクターブの寄与を、小さくする。
    sum += amplitude * n.x / (1.0 + dot(slope_sum, slope_sum));
    p *= lacunarity;
    amplitude *= gain;
  }
  return sum;
}
```

水の流れの、シミュレーションは不要で、**1 回のノイズ計算で、侵食に似た形**が得られます。本格的な侵食（[Erosion](erosion.md)）に比べると、谷が、つながっていない点は、見破られます。

## 実装の注意点

| 項目 | 内容 |
| --- | --- |
| 精度 | 浮動小数点は、座標が大きい（数十 km）と、精度が落ちる。ワールド原点から、離れた場所では、タイルの原点を引いてから、計算する |
| オクターブ数 | 画素が、1 テクセル未満になる周波数は、意味がない。テクセルの大きさに合わせて、打ち切る |
| 再現性 | ハッシュは、`sin` ではなく、整数演算（PCG）を使う。GPU が違っても、同じ地形になる |
| 保存 | 高さは 16 ビット（`R16_UNORM`）で保存すると、メモリが、半分になる |

''', before="## よくあるミス")
pg.Refs("terrain/generation/fbm.md", [PERLIN85, PERLIN02, EBERT, MANDELBROT, QUILEZ_FBM, QUILEZ_DERIV, HASH])

# ---------------------------------------------------------------- ridge
pg.Dedup("terrain/generation/ridge.md")
pg.Add("terrain/generation/ridge.md", '''
## 通常の fBm は、山の稜線が、丸い

fBm は、ノイズの値（−1〜1）を、そのまま高さにするので、山頂は、**丸い丘**になります。現実の山脈には、**鋭い稜線（尾根）**があります。尾根を、作るには、ノイズの値を、**折り返す**加工をします。

## 尾根ノイズ（ridged multifractal）の考え方

ノイズの値は、0 の近くを、ゆっくり通り抜けます。**ノイズが 0 になる場所は、曲線（等値線）**を作ります。この曲線を、**山の尾根**にします。

1. ノイズの**絶対値**を、取る（0 の位置で、V の字に、折り返される）
2. 1 から引いて、**上下を、ひっくり返す**（0 の位置が、山頂の、尖った稜線になる）
3. 値を、**2 乗**して、尾根を、さらに鋭くする

```text
signal = 1 − |noise|        尾根が、尖る
signal = signal²            尾根が、さらに鋭く、谷が平らに
```

Musgrave が、この方式を、マルチフラクタルとして、整理しました（Ebert ら、2002）。

## 実装

```hlsl
// リッジ マルチフラクタル（Musgrave）。
float RidgedMulti(float2 p, int octaves, float lacunarity, float gain,
                  float offset, float weight_gain, uint seed) {
  float sum = 0.0;
  float amplitude = 1.0;
  float weight = 1.0;
  for (int i = 0; i < octaves; ++i) {
    float signal = GradientNoise(p, seed + i);
    signal = offset - abs(signal);        // 折り返し（offset は 1.0 が標準）
    signal *= signal;                      // 2 乗で、尾根を鋭く
    signal *= weight;                      // 下のオクターブの結果で、重みを変える

    sum += signal * amplitude;
    // 尾根の上（signal が大きい所）にだけ、次のオクターブの細かい起伏を、乗せる。
    weight = saturate(signal * weight_gain);

    p *= lacunarity;
    amplitude *= gain;
  }
  return sum;
}
```

| パラメーター | 一般的な値 | 意味 |
| --- | --- | --- |
| `offset` | 1.0 | 折り返しの高さ。小さくすると、尾根が低く、谷が広くなる |
| `weight_gain` | 2.0 | 次のオクターブへ、重みを渡す強さ |
| `gain` | 0.5 | 振幅の減り方 |

### 重み（weight）が、肝心

`weight` は、**前のオクターブで、尾根に近かった場所だけ、次のオクターブを強く足す**ための係数です。

| 場所 | 前の signal | weight | 次のオクターブ |
| --- | --- | --- | --- |
| 尾根の上 | 大きい | 大きい | 強く足される。尾根に、細かい起伏が付く |
| 谷 | 小さい | 小さい | ほとんど足されない。谷が、平らに残る |

結果として、**尾根は、ごつごつして、谷は、なだらか**になります。これが、リッジ ノイズと、fBm の、一番の違いです。山脈や、荒れた岩山で、よく使います。

## fBm と、組み合わせて使う

尾根ノイズだけでは、全体が、山脈になります。**平地・丘・山脈**を、混ぜる場合は、2 種類のノイズを、**マスク**で混ぜます。

```hlsl
// 低周波のノイズで「山の領域」を決め、その領域だけ、尾根ノイズを使う。
float height_fbm = Fbm(p, 6, 2.0, 0.5, seed);                         // 丘・平地
float height_ridge = RidgedMulti(p, 6, 2.0, 0.5, 1.0, 2.0, seed + 100);  // 山脈
float mountain_mask = smoothstep(0.2, 0.6, Fbm(p * 0.1, 3, 2.0, 0.5, seed + 200) * 0.5 + 0.5);
float height = lerp(height_fbm * 0.2, height_ridge, mountain_mask);
```

低周波のノイズ（`p * 0.1`）を、マスクにして、**地域ごとに、地形の性格を変える**のは、手続き的な地形の、基本の考え方です（[Converting Noise to Height](height-conversion.md)）。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 値の範囲 | `offset − |n|` を 2 乗するので、値は、0〜1 程度。fBm（−1〜1）と、混ぜるときは、範囲を、そろえる |
| 尾根が、直線的になる | 勾配ノイズの格子の向きが、出ることがある。座標を、少し回転させて、オクターブごとに、変える |
| 谷が、平らすぎる | `weight_gain` を下げる、または、谷にだけ、別の fBm を、足す |
| 傾きが急すぎる | 2 乗で、尾根が急になる。高さの変換（スケール）で、調整する |

''', before="## よくあるミス")
pg.Refs("terrain/generation/ridge.md", [EBERT, MUSGRAVE89, PERLIN02, QUILEZ_FBM])

# ---------------------------------------------------------------- domain warp
pg.Dedup("terrain/generation/domain-warp.md")
pg.Add("terrain/generation/domain-warp.md", '''
## ドメイン ワーピングとは

ノイズに、座標を渡す前に、**座標そのものを、別のノイズで、ずらす**手法です。ノイズ関数 `f(p)` の代わりに、`f(p + w(p))` を計算します。`w` は、ずらし量を返す、別のノイズ関数です。

```text
普通:        height = fbm(p)
ワーピング:   height = fbm(p + k × fbm2(p))
```

「domain（定義域）」は、関数の入力のことです。**入力を、ゆがめる**ので、この名前が付いています。

## なぜ、ゆがめるのか

fBm や、勾配ノイズの地形は、**どの方向にも、同じ性質**（等方的）です。人工的で、**砂の山のよう**に見えることがあります。現実の地形は、風・水・断層で、**流れるように曲がった形**をしています。ドメイン ワーピングを行うと、**ノイズが、渦を巻いたり、折れ曲がったりして**、ずっと有機的な形になります。

| 比較 | fBm | ワーピングした fBm |
| --- | --- | --- |
| 尾根・谷の形 | 同じ方向に、ばらばら | 曲がって、流れる |
| 全体の印象 | 砂山、小さな丘の集まり | 大陸、浸食された山地 |
| 細部 | 一様 | 場所によって、密度が変わる |

## 実装

```hlsl
// ずらし量を作る関数。2 つのノイズで、x と y を別々にずらす。
float2 Warp(float2 p, uint seed) {
  return float2(Fbm(p + float2(0.0, 0.0), 4, 2.0, 0.5, seed),
                Fbm(p + float2(5.2, 1.3), 4, 2.0, 0.5, seed + 1));   // 少し離れた場所から読む
}

float WarpedFbm(float2 p, float strength, uint seed) {
  float2 q = p + strength * Warp(p, seed);
  return Fbm(q, 6, 2.0, 0.5, seed + 2);
}
```

`float2(5.2, 1.3)` のような、**ずらしたオフセット**は、x と y の、ずらし量が、同じにならないようにするためです。同じノイズを使うと、斜め方向にしか、ずれません。

### 2 重のワーピング

Quilez は、**ワーピングの結果を、もう一度、ワーピングの入力にする**方法を紹介しています。

```hlsl
float WarpedFbm2(float2 p, float strength, uint seed) {
  float2 q = Warp(p, seed);                          // 1 回目
  float2 r = Warp(p + strength * q, seed + 10);      // 1 回目の結果で、ずらして、2 回目
  return Fbm(p + strength * r, 6, 2.0, 0.5, seed + 2);
}
```

```text
f(p + fbm(p + fbm(p)))
```

重ねるほど、渦や、折りたたまれた形が、複雑になります。そのかわり、**ノイズの計算が、回数分、増えます**（1 回で 3 つ、2 重で 5 つ分の fBm）。

## パラメーター

| パラメーター | 一般的な値 | 効果 |
| --- | --- | --- |
| `strength`（ずらし量） | 0.3〜2.0（周波数 1 に対して） | 小さいと、わずかなゆがみ。大きいと、渦、折りたたみ |
| ワーピング用の fBm の周波数 | 本体より、低い（1/2〜1/4） | 低いと、大きな、ゆっくりした曲がり。高いと、細かいゆがみ |
| ワーピング用の fBm の、オクターブ数 | 2〜4 | 少なくてもよい（形が、なめらかなので） |

!!! tip "ずらし量を、場所で変える"
    ずらし量を、**別の低周波ノイズで、変える**と、「あまりゆがんでいない平地」と「大きくゆがんだ山岳」が、同じ地形の中に共存します。`strength * mask(p)` の形です。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 傾きが、不連続になる | ずらし量が大きいと、座標の写像が、折りたたまれて、**高さが、鋭く切れる**ことがある。ずらし量を、控えめにする |
| コスト | fBm が、3〜5 個分に増える。オフラインで、焼き込むのが基本 |
| 傾きの解析的な計算 | 座標のずらしで、微分も、連鎖律で変わる。侵食風の式と組み合わせるときは、ワーピングの微分も、計算する必要がある |
| ワールド座標 | ずらしを加えた座標も、**ワールド座標**で計算する（タイルの継ぎ目をなくす）（[fBm](fbm.md)） |

## 使いどころ

| 場面 | 使い方 |
| --- | --- |
| 大陸・島の形 | 低周波に、強くワーピングして、海岸線を、複雑にする |
| 山岳地帯 | 尾根ノイズの座標を、ワーピングして、尾根を曲げる（[Ridged Noise](ridge.md)） |
| 砂漠 | 縞模様の砂丘を、少しだけ、ゆがめる |
| 地層・岩の模様 | 色のノイズを、ワーピングして、流れるような模様にする |

''', before="## よくあるミス")
pg.Refs("terrain/generation/domain-warp.md", [QUILEZ_FBM, EBERT, PERLIN02, GALIN])

# ---------------------------------------------------------------- erosion
pg.Dedup("terrain/generation/erosion.md")
pg.Add("terrain/generation/erosion.md", '''
## 侵食を、シミュレーションする理由

ノイズだけで作った地形は、**水に削られた跡**がありません。現実の山は、雨が降って、水が流れ、土を削り、運び、積もらせた結果、**谷が枝分かれして、麓に扇状の地形**ができます。この形は、ノイズでは、作れません。**侵食を、シミュレーションして、地形に、適用する**と、一気に本物らしくなります。

| 侵食 | 起きること | 地形への影響 |
| --- | --- | --- |
| 熱による侵食（thermal） | 急な斜面の土が、崩れて、麓に溜まる | 斜面が、一定の角度（安息角）以下になる |
| 水による侵食（hydraulic） | 水が流れて、土を削り、運び、積もらせる | 谷、枝分かれした水系、扇状地 |

Musgrave ら（1989）が、この 2 つを、地形生成に、取り入れました。

## 熱による侵食（thermal）

最も単純な侵食です。**隣の画素との、高さの差が、一定のしきい値（タロス角）を超えたら、差の一部を、低い方へ移す**だけです。

```hlsl
// 熱による侵食（1 回分）。隣の 4 つとの高さの差を見て、超えた分を、低い方へ移す。
Texture2D<float> g_src : register(t0);
RWTexture2D<float> g_dst : register(u0);

cbuffer ThermalCB : register(b0) {
  float talus;      // 隣との、高さの差の上限（= tan(安息角) × 1 マスの長さ）
  float rate;       // 1 回に動かす割合（0.5 が標準）
  int size;
};

[numthreads(8, 8, 1)]
void main(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  float h = g_src[p];
  float total_diff = 0.0;     // 自分から、低い隣へ流れる量の合計
  float received = 0.0;       // 高い隣から、自分へ流れてくる量の合計
  const int2 dirs[4] = {int2(1, 0), int2(-1, 0), int2(0, 1), int2(0, -1)};

  [unroll] for (int i = 0; i < 4; ++i) {
    int2 q = clamp(p + dirs[i], 0, size - 1);
    float diff = h - g_src[q];
    if (diff > talus) total_diff += (diff - talus);              // 自分が、高い → 流れ出る
    float diff2 = g_src[q] - h;
    if (diff2 > talus) {
      // 隣 q から見て、自分は低い隣。q の流れ出る量のうち、自分への取り分は、diff2 の比
      received += (diff2 - talus) * 0.25;
    }
  }
  g_dst[p] = h - total_diff * rate * 0.25 + received * rate;
}
```

上の実装は、簡略化したものです。**1 つの画素が、4 つの隣に、同時に、土を渡す**ので、「出る量」と「入る量」を、**対称に**書かないと、土の総量が、保存されません（総量が、増えたり、減ったりする）。実際には、**各画素が、自分から出る量を、計算し、隣の取り分も、同じ式で、計算する**形にします。

| 項目 | 内容 |
| --- | --- |
| 繰り返し | 数十〜数百回、繰り返す。出力と入力を、**交互に入れ替える**（ピンポン） |
| 効果 | 尖った山頂が、少し崩れ、麓に、緩やかな斜面ができる |
| 限界 | 水系が、できない。谷は、できない |

## 水による侵食：パイプ モデル（Mei ら 2007）

水による侵食は、**水の流れを、シミュレーションする**必要があります。Mei らは、**「隣り合う画素が、パイプで、つながっている」**というモデルで、GPU 上で、高速に動く方式を示しました。

### 各画素が持つもの

| 量 | 記号 | 内容 |
| --- | --- | --- |
| 地形の高さ | b | 地面の高さ |
| 水の深さ | d | 地面の上に、積もっている水 |
| 浮遊している土の量 | s | 水に運ばれている土 |
| 4 方向への、水の流量 | f（L、R、T、B） | 左・右・上・下の、隣へ流れる水 |
| 水の速度 | v | 流量から、求める |

水面の高さは、`b + d` です。

### 1 ステップの流れ

| 段階 | 内容 |
| --- | --- |
| ① 雨 | 水の深さ `d` に、雨の量を足す |
| ② 流量の更新 | 隣との、**水面の高さの差**から、各方向の流量を更新する。差が大きいほど、勢いよく流れる |
| ③ 水の深さの更新 | 4 方向の流量の、出入りから、`d` を更新する。速度 `v` も、ここで、求める |
| ④ 侵食・堆積 | 速度と、傾きから、**水が運べる土の量（容量 C）**を計算する。`s < C` なら、地面を削って `s` に足す。`s > C` なら、`s` から、地面へ、土を戻す |
| ⑤ 土の移流 | 浮遊している土 `s` を、水の速度 `v` で、運ぶ（半ラグランジュ法：速度の向きを遡って、読む） |
| ⑥ 蒸発 | `d` を、少し減らす |

### ② 流量の更新

```hlsl
// 流量（左・右・上・下）を、更新する。
// 水面の高さ H = b + d。隣との差が、大きいほど、流量が増える。
float4 UpdateFlux(float4 flux, float H, float4 H_neighbors, float d) {
  const float g = 9.81;          // 重力
  const float pipe_area = 1.0;   // パイプの断面積
  const float pipe_len = 1.0;    // パイプの長さ（マスの大きさ）

  // 4 方向の、水面の高さの差から、新しい流量を求める。負にはしない。
  float4 new_flux = max(0.0, flux + dt * pipe_area * g * (H - H_neighbors) / pipe_len);

  // 出ていく水の合計が、いまある水を超えないように、全体を、縮める。
  float outflow = dt * (new_flux.x + new_flux.y + new_flux.z + new_flux.w);
  float scale = min(1.0, d * cell_area / max(outflow, 1e-6));
  return new_flux * scale;
}
```

水が足りないのに、流量が大きいと、水の深さが負になるので、**出る量の合計を、縮める**処理が、必要です。

### ④ 侵食と堆積

水が、土を運べる量（容量）は、**水の速さと、地形の傾きが大きいほど、大きい**と考えます。

```text
C = Kc × sin(α) × |v|           α: 地面の傾き、v: 水の速さ、Kc: 容量の係数
```

| 状態 | 動き |
| --- | --- |
| `s < C`（運べる余裕がある） | 地面を削る：`b -= Ks × (C − s)`、`s += Ks × (C − s)` |
| `s > C`（運びきれない） | 土を落とす：`b += Kd × (s − C)`、`s -= Kd × (s − C)` |

`Ks`（溶解）と `Kd`（堆積）の係数が、**どのくらい、速く削る／積もらせるか**を、決めます。

```hlsl
float slope = max(sin_alpha, 0.05);              // 平らな場所でも、少しは、削れる下限
float capacity = Kc * slope * length(velocity);
if (sediment < capacity) {
  float amount = Ks * (capacity - sediment);
  height -= amount;
  sediment += amount;
} else {
  float amount = Kd * (sediment - capacity);
  height += amount;
  sediment -= amount;
}
```

## 水による侵食：粒子（水滴）モデル

パイプ モデルとは、別の、**水滴を 1 粒ずつ、転がして、シミュレーションする**方式です（Beyer、2015 の整理が、よく読まれています）。

| 手順 | 内容 |
| --- | --- |
| ① 生成 | ランダムな場所に、水滴を、1 つ置く |
| ② 転がる | その場所の、**勾配**（下り坂の向き）へ、少し、進む |
| ③ 土を運ぶ | 速度と、傾きから、運べる土の量を計算する。足りなければ、地面を削り、多ければ、落とす |
| ④ 蒸発 | 少しずつ、水を減らす。水が、無くなったら、終わり |

数十万〜数百万個の水滴を、順に転がすと、**谷が、現れます**。

| 比較 | パイプ モデル（Mei） | 粒子モデル |
| --- | --- | --- |
| 実装 | 画素ごとに、独立で、GPU 向き | 水滴ごとの処理。CPU でも実装が、簡単 |
| 水の連続性 | 本物の水の流れ。池、川が、できる | 水滴は、独立。池は、できにくい |
| GPU での並列化 | 自然（画素ごと） | 水滴が、同じ場所を、同時に書き換える。アトミック命令が、必要 |
| 結果 | 水系が、はっきり出る | 実装が簡単で、見た目も、十分によい |

## 実際の使い方

| ポイント | 内容 |
| --- | --- |
| 事前計算（オフライン） | 数百〜数千ステップが、必要。**ツールで、焼いて、結果の高さマップを、保存**するのが、普通 |
| 入力の高さ | ノイズ（[fBm](fbm.md)、[Ridged Noise](ridge.md)）を、そのまま入れる。**侵食で、形が整う** |
| 出力 | 侵食後の高さ。**堆積した土の量、水の流れの量（フロー マップ）**も、スプラットや、川の位置決めに使える |
| タイルの境目 | 地形が分割されている場合、**隣のタイルの高さが、侵食の途中で、変わる**ので、タイルの境目に、数画素の余白を持って計算する |
| 再現性 | 浮動小数点の、計算の順序が、実行環境で変わる。**同じ結果が要るときは、焼き込んで保存**する |

!!! note "侵食の結果は、ほかの処理にも使える"
    水が、集まった場所（フローの量が、多い場所）は、**川や、湿った土**にできます（[Rivers and Lakes](rivers.md)）。土が、堆積した場所は、**平らで、植生に向く**場所です（[Placement Generation](placement.md)）。

''', before="## よくあるミス")
pg.Refs("terrain/generation/erosion.md", [MUSGRAVE89, MEI, STAVA, OLSEN, BEYER, GALIN])

# ---------------------------------------------------------------- height conversion
pg.Dedup("terrain/generation/height-conversion.md")
pg.Add("terrain/generation/height-conversion.md", '''
## ノイズの値は、そのままでは、地形の高さにならない

[fBm](fbm.md) や、[リッジ ノイズ](ridge.md) の出力は、**−1〜1（または 0〜1）の数字**です。これを、**メートル単位の高さ**にする作業が、「高さへの変換」です。単に、スケールを掛けるだけでも地形になりますが、**ひと工夫するだけで、見た目が、大きく変わります**。

## 1. 線形のスケール

```text
height = noise × max_height + base_height
```

最も単純です。高さが、均等に分布するので、**山頂も、谷も、同じくらいの数**になります。自然の地形は、**平地（低い所）が広く、山は、少ししかない**ので、人工的に見えます。

## 2. べき乗で、平地を広げる

ノイズの値（0〜1）を、**べき乗**すると、低い値が、さらに低くなります。

```hlsl
float h = pow(saturate(noise01), 2.0);      // 2 乗: 低い所が、ぺたんと平らに
```

| 指数 | 見た目 |
| --- | --- |
| 1.0 | 線形。起伏が、均等 |
| 2.0 | 平地が広がり、山が、鋭く残る |
| 3.0 以上 | ほとんどが平地。山は、ごく一部 |
| 0.5 以下 | 山の頂上が、平らになる（台地、メサ） |

## 3. 高さの分布を、カーブで変える

べき乗より、細かく、制御したいときは、**入力（ノイズ）と、出力（高さ）の対応を、カーブで描いて**、テーブルとして、引きます。

```text
出力
  1.0 |                ●────●
      |             ●
  0.5 |        ●───●        ← 平らな高原
      |    ●
  0.0 |●──●                 ← 平らな海底・平野
      +──────────────────── 入力
      0                  1
```

```cpp
// 制御点（入力, 出力）を並べて、区間ごとに、線形補間する。
struct CurvePoint { float in; float out; };

float EvaluateCurve(const std::vector<CurvePoint>& curve, float x) {
  if (x <= curve.front().in) return curve.front().out;
  for (size_t i = 1; i < curve.size(); ++i) {
    if (x <= curve[i].in) {
      const float t = (x - curve[i - 1].in) / (curve[i].in - curve[i - 1].in);
      return curve[i - 1].out + t * (curve[i].out - curve[i - 1].out);
    }
  }
  return curve.back().out;
}
```

アーティストが、**グラフを、手で描いて**、地形の性格を、調整できます。GPU では、カーブを、**1 次元のテクスチャ**（256 画素）に焼いて、`SampleLevel` で引きます。

```hlsl
Texture1D<float> g_height_curve : register(t3);
float h = g_height_curve.SampleLevel(g_linear_clamp, saturate(noise01), 0);
```

## 4. 階段状にする（テラス）

高さを、**階段状**に切ると、**棚田や、段々の高原**ができます。

```hlsl
// 高さを、steps 段の階段にする。sharpness が大きいほど、段が、はっきりする。
float Terrace(float h, float steps, float sharpness) {
  float x = h * steps;
  float f = frac(x);
  // 段の中は、ほぼ平らに、段の境目で、急に上がる
  float s = smoothstep(0.5 - 0.5 / sharpness, 0.5 + 0.5 / sharpness, f);
  return (floor(x) + s) / steps;
}
```

## 5. 複数のノイズを、領域ごとに混ぜる

大陸規模の地形は、1 つのノイズでは、表現できません。**複数の、性格の違うノイズを、マスクで混ぜます**。

| 層 | ノイズ | 内容 |
| --- | --- | --- |
| 大陸性（continentalness） | 低周波の fBm | 陸か海か（高さの下地） |
| 地形の起伏（roughness） | 中周波の fBm | その場所が、平らか、起伏が大きいか |
| 山脈 | リッジ ノイズ | 山のある場所だけ、足す |
| 細部 | 高周波の fBm | 小さな凹凸 |

```hlsl
float continent = Fbm(p * 0.001, 4, 2.0, 0.5, seed) * 0.5 + 0.5;    // 0 = 海、1 = 陸
float base = EvaluateBaseHeight(continent);                          // カーブで、海底〜陸の高さへ
float mountain_mask = smoothstep(0.55, 0.75, continent);             // 内陸だけ、山
float mountains = RidgedMulti(p * 0.003, 6, 2.0, 0.5, 1.0, 2.0, seed + 1) * mountain_mask;
float detail = Fbm(p * 0.02, 4, 2.0, 0.5, seed + 2) * 0.05;
float height = base + mountains * 800.0 + detail * 50.0;             // メートル
```

これで、「海岸線の近くは、平地。内陸に行くと、山脈」という、**地形の流れ**が作れます。

## 6. 高さマップの形式と、単位

| 項目 | 内容 |
| --- | --- |
| 保存形式 | `R16_UNORM`（0〜65535）。高さの範囲を、`height_scale`（メートル）で、決める |
| 解像度（高さ方向） | 16 ビットなら、最大高さ 1,000 m で、約 1.5 cm の刻み。8 ビットは、4 m の刻みで、階段が、見える |
| 海面 | 海面を、高さ 0 にするか、ある高さにするか、**先に決める**。後から、変えにくい |
| 範囲 | 保存の前に、`saturate` で、0〜1 に収める。範囲を超えた値は、切れる |

```cpp
// 高さ（メートル）→ R16_UNORM に変換
uint16_t EncodeHeight(float meters, float min_height, float max_height) {
  const float t = (meters - min_height) / (max_height - min_height);
  return static_cast<uint16_t>(std::clamp(t, 0.0f, 1.0f) * 65535.0f + 0.5f);
}
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| 変換の順番 | **べき乗やカーブの後に、侵食**をかける（侵食は、傾きに依存する）。逆にすると、侵食が、変換で崩れる |
| 傾き | 高さのスケールを、2 倍にすると、**傾きも 2 倍**になる。傾きの条件（岩、雪）は、スケールの後の、値で考える |
| ワールドの大きさ | 水平方向のスケール（1 テクセル何メートルか）と、垂直方向のスケールを、合わせて決める。縦だけ伸ばすと、針の山になる |

''', before="## よくあるミス")
pg.Refs("terrain/generation/height-conversion.md", [EBERT, GALIN, MUSGRAVE89])

# ---------------------------------------------------------------- rivers
pg.Dedup("terrain/generation/rivers.md")
pg.Add("terrain/generation/rivers.md", '''
## 川を作る、2 つの考え方

| 方式 | 順番 | 特徴 |
| --- | --- | --- |
| 地形から、川を求める | ① 地形を作る → ② 水の流れを、シミュレーションして、川の位置を決める | 簡単。川が、地形に、必ず合う。ただし、湖や、複雑な水系は、調整が必要 |
| 川から、地形を作る | ① 川の網（ネットワーク）を作る → ② 川に沿って、地形を、作る | 川の形を、制御できる。川が、必ず、海へつながる |

ここでは、**まず作りやすい、地形から求める方法**を、中心に説明します。**川から地形を作る方法**は、Génevaux ら（2013）が、体系的に整理しています。

## 地形から、川を求める

### ① 水が、どこへ流れるか

高さマップの、各画素に、「**どの隣へ流れるか**」を決めます。最も単純なのは、**8 つの隣のうち、いちばん低い隣へ流れる**方法です（D8 法）。

```cpp
// D8 法: 各セルについて、最も急に下る隣の方向を求める。
struct FlowDir { int dx, dy; };

FlowDir ComputeFlowDirection(const HeightMap& h, int x, int y) {
  FlowDir best = {0, 0};
  float best_slope = 0.0f;
  for (int dy = -1; dy <= 1; ++dy) {
    for (int dx = -1; dx <= 1; ++dx) {
      if (dx == 0 && dy == 0) continue;
      const float dist = (dx != 0 && dy != 0) ? 1.4142f : 1.0f;     // 斜めは、少し遠い
      const float slope = (h.At(x, y) - h.At(x + dx, y + dy)) / dist;
      if (slope > best_slope) {
        best_slope = slope;
        best = {dx, dy};
      }
    }
  }
  return best;   // {0, 0} なら、周りより低い（窪地）
}
```

### ② 窪地を埋める

水が、**周りより低い窪地**に、たどり着くと、そこで、止まります。実際の地形では、窪地は、**水が満たされた湖**です。そのまま続けると、流れが、途切れてしまうので、窪地を、**溢れる高さまで埋めて**、流れを、海へつなげます。

窪地を、効率的に埋めるアルゴリズムが、**Priority-Flood**（Barnes ら、2014）です。**外側（海、地形の縁）から、低い順に処理して、窪地を埋める**方法です。

```cpp
// Priority-Flood（簡略版）: 縁から、低い順に、内側へ広げながら、窪地を埋める。
struct Cell { float height; int x, y; };
struct Greater { bool operator()(const Cell& a, const Cell& b) const { return a.height > b.height; } };

void FillDepressions(HeightMap& h) {
  std::priority_queue<Cell, std::vector<Cell>, Greater> open;
  Grid<bool> closed(h.width, h.height, false);
  // 縁のセルを、すべて、開始点として入れる
  for (const auto& [x, y] : h.BorderCells()) {
    open.push({h.At(x, y), x, y});
    closed.At(x, y) = true;
  }
  while (!open.empty()) {
    const Cell c = open.top();
    open.pop();
    for (int dy = -1; dy <= 1; ++dy) {
      for (int dx = -1; dx <= 1; ++dx) {
        const int nx = c.x + dx, ny = c.y + dy;
        if (!h.InBounds(nx, ny) || closed.At(nx, ny)) continue;
        closed.At(nx, ny) = true;
        // 隣が、いまの水位より低ければ、水位まで持ち上げる（窪地を埋める）
        h.At(nx, ny) = std::max(h.At(nx, ny), c.height);
        open.push({h.At(nx, ny), nx, ny});
      }
    }
  }
}
```

実際には、埋めた量が、**湖の深さ**になるので、湖の水面の高さとして、保存しておきます。

### ③ 流量を数える（フロー アキュムレーション）

各画素が、**上流から、いくつの画素の水を、受けているか**を数えます。これを「流量（flow accumulation）」と呼びます。

```cpp
// 上流から下流へ、水を流して、流量を数える。
// 高い順に処理する（上流を先に処理すれば、下流に、足し込める）。
std::vector<int> order = SortCellsByHeightDescending(h);
Grid<float> flow(h.width, h.height, 1.0f);       // 各セルに、最初に、雨 1 を置く
for (int idx : order) {
  const auto [x, y] = ToXY(idx);
  const FlowDir d = dir.At(x, y);
  if (d.dx == 0 && d.dy == 0) continue;           // 流れ先が、ないセル（海、縁）
  flow.At(x + d.dx, y + d.dy) += flow.At(x, y);    // 自分の水を、下流に足す
}
```

### ④ しきい値で、川を決める

流量が、**あるしきい値を超えたセル**を、川とします。

| しきい値 | 結果 |
| --- | --- |
| 小さい | 小川が、たくさん。地形全体が、枝分かれした水系 |
| 大きい | 主要な川だけ |

流量が、**大きいほど、川幅を広くする**と、自然な水系になります。

```text
川幅 = k × (流量)^0.5      （流量が 4 倍で、川幅は 2 倍。実際の川の関係に近い）
```

## 川を、地形に刻む

求めた川の位置に、**地形を削って**、谷（川床）を作ります。

```hlsl
// 川に近い場所を、掘り下げる。
// river_dist は、最も近い川までの距離、river_width は、その川の幅。
float carve = smoothstep(river_width * 1.5, river_width * 0.5, river_dist);
float depth = river_depth * carve;
height -= depth;
```

| 工夫 | 内容 |
| --- | --- |
| 川底の勾配 | 川は、上流から下流へ、**必ず、下る**。川底を、緩やかに下る曲線に、整える（途中で、上り坂に、ならない） |
| 川の両岸 | 土手を、緩やかに、持ち上げる（滑らかな、マスク） |
| 川の水面 | 川床の高さ + 少し、の位置に、水面のメッシュを置く（[Water](../../water/index.md)） |

### 川の水面を作る

川の、水面のメッシュは、**川の経路に沿った、リボン（帯）状のメッシュ**で、作ります。

| 項目 | 内容 |
| --- | --- |
| 経路 | フローの、画素の列を、**なめらかなスプライン**に変換する |
| メッシュ | スプラインに沿って、幅と、高さを持つ、帯を作る |
| 流れ | 川の向きを、**フロー マップ**として、描く（[Flow Maps](../../water/interaction/flow-map.md)） |
| 水面の高さ | 川底の高さ + 水深。**下流に向かって、必ず下がる** |

## 湖

窪地を埋めたとき、**水位が、埋めた高さ**になります。その、**平らな水面**を、湖の水面とします。

| 項目 | 内容 |
| --- | --- |
| 水面の高さ | 窪地を埋めた、最終的な、高さ |
| 水深 | 埋めた量（水面の高さ − 元の高さ） |
| 岸 | 水深が 0 に、近づく場所が、岸（[Shore Foam](../../water/shore-foam/index.md)） |
| 出口 | 湖の最も低い縁が、川の、始まりになる |

## 川から、地形を作る方法（概要）

Génevaux ら（2013）の方式は、順序を逆にします。

| 段階 | 内容 |
| --- | --- |
| ① 川のグラフ | 河口から、上流へ向かって、**木構造**として、川の枝を、決める。川の流量（太さ）は、枝分かれで、決まる |
| ② 高さの制約 | 川の高さを、河口から、上流へ向かって、**必ず上がる**ように、決める |
| ③ 地形の生成 | 川の高さを、制約として、その間を、ノイズで、埋める |

利点は、**川が、必ず、河口につながる**ことと、**アーティストが、川の位置を、指定できる**ことです。ただし、実装が、複雑です。

''', before="## よくあるミス")
pg.Refs("terrain/generation/rivers.md", [GENEVAUX, BARNES, GALIN, "Kelley, Malin, Nielson, \"Terrain Simulation Using a Model of Stream Erosion\", SIGGRAPH 1988", "O'Callaghan, Mark, \"The Extraction of Drainage Networks from Digital Elevation Data\", Computer Vision, Graphics, and Image Processing, Vol. 28, 1984（D8 法の原典）"])

# ---------------------------------------------------------------- placement
pg.Dedup("terrain/generation/placement.md")
pg.Add("terrain/generation/placement.md", '''
## 配置の、3 つの問題

木・岩・草を、地形の上に置くとき、次の 3 つを、解く必要があります。

| 問題 | 内容 |
| --- | --- |
| ① どこに置くか（密度） | 条件（高さ、傾き、湿度）から、場所ごとの、**置く確率**を決める |
| ② どう散らすか（分布） | 点が、かたまらず、**自然に、ばらける**ようにする |
| ③ 同じ結果にする（決定性） | **何度、生成しても、同じ位置に**置く。セーブ データと、ネットワークで、位置が食い違わないように |

## ① 密度マップ

条件から、**0〜1 の密度**を、地形全体に、計算します。

```hlsl
// 木の密度: 平らで、湿っていて、高すぎない場所に多い。
float TreeDensity(float3 world_pos, float3 normal, float moisture) {
  float slope = 1.0 - saturate(normal.y);
  float flat_ok = 1.0 - smoothstep(0.15, 0.35, slope);                 // 急斜面には生えない
  float altitude_ok = 1.0 - smoothstep(tree_line - 50.0, tree_line, world_pos.y);  // 森林限界
  float wet = smoothstep(0.2, 0.6, moisture);                          // 乾いた所は、疎ら
  float noise = Fbm(world_pos.xz * 0.01, 3, 2.0, 0.5, 42) * 0.5 + 0.5; // 森のかたまりを作る
  return flat_ok * altitude_ok * wet * noise;
}
```

| 入力 | 内容 |
| --- | --- |
| 高さ | 森林限界、海岸近くの植物 |
| 傾き | 急斜面は、木が生えない（岩だけ） |
| 湿度・水からの距離 | 川の近くは、植物が、多い |
| 低周波のノイズ | 森の、かたまりと、空き地を、作る |
| 手描きのマスク | アーティストが、「ここには置かない」を、塗る |
| 道・建物 | 道や、建物の周りは、密度を 0 にする |

## ② 点を、どう散らすか

### 悪い例：一様乱数

座標を、**一様な乱数**で、決めると、点が、**かたまったり、空いたり**します。木が、一直線や、ダマに、並びます。

### 良い例 1：ジッタード グリッド

地形を、格子に分けて、**各セルに、1 つずつ点を、置き**、セルの中の位置を、乱数で、ずらします。**簡単で、速く**、点の間隔が、ある程度、そろいます。

```cpp
// ジッタード グリッド: 各セルに 1 つ、ランダムな位置に、点を置く。
for (int cy = 0; cy < cells_y; ++cy) {
  for (int cx = 0; cx < cells_x; ++cx) {
    const uint32_t seed = HashCell(cx, cy, global_seed);        // セル座標から、乱数の種
    const float2 jitter = {Random01(seed), Random01(seed + 1)};
    const float2 p = (float2(cx, cy) + jitter) * cell_size;
    if (Random01(seed + 2) < Density(p)) {                       // 密度で、間引く
      points.push_back(p);
    }
  }
}
```

### 良い例 2：ポアソン円盤サンプリング

**どの 2 点も、最小距離 r 以上、離れている**ように、点を置きます（ポアソン円盤分布）。ブルー ノイズに近く、**自然な散らばり**です。Bridson（2007）の方法が、O(n) で、速く、広く使われています。

```cpp
// Bridson のポアソン円盤サンプリング（2D、簡略版）。
std::vector<float2> PoissonDisk(float width, float height, float r, int k, uint32_t seed) {
  const float cell = r / std::sqrt(2.0f);            // 1 セルに、点は最大 1 つしか入らない
  Grid<int> grid(int(width / cell) + 1, int(height / cell) + 1, -1);
  std::vector<float2> points, active;
  Rng rng(seed);

  auto add = [&](float2 p) {
    grid.At(int(p.x / cell), int(p.y / cell)) = int(points.size());
    points.push_back(p);
    active.push_back(p);
  };
  add({rng.Uniform(0, width), rng.Uniform(0, height)});

  while (!active.empty()) {
    const int i = rng.Index(active.size());
    bool found = false;
    for (int n = 0; n < k; ++n) {                     // k 回（30 回が標準）、候補を試す
      // 半径 r〜2r の環の中から、候補を選ぶ
      const float angle = rng.Uniform(0, 6.2831853f);
      const float dist = rng.Uniform(r, 2 * r);
      const float2 c = active[i] + float2(std::cos(angle), std::sin(angle)) * dist;
      if (c.x < 0 || c.y < 0 || c.x >= width || c.y >= height) continue;
      if (FarEnough(grid, points, c, r, cell)) {      // 周りの 5×5 セルだけを調べれば、十分
        add(c);
        found = true;
        break;
      }
    }
    if (!found) active.erase(active.begin() + i);      // 置けなくなった点は、外す
  }
  return points;
}
```

### 密度に合わせて、半径を変える

密度が高い所は、半径 r を小さく、低い所は、大きくします。**場所ごとに、半径が変わる**ポアソン円盤です。簡単な方法は、**最も細かい半径で、点を、密に作り**、**密度に応じて、間引く**ことです。

```cpp
// 密度で、間引く。点ごとに、決定的な乱数を使う。
for (const float2& p : dense_points) {
  const float d = Density(p);
  if (HashToFloat(p, global_seed) < d) kept.push_back(p);
}
```

### 方法の比較

| 方法 | 見た目 | 速さ | 特徴 |
| --- | --- | --- | --- |
| 一様乱数 | ダマになる | 最速 | 使わない |
| ジッタード グリッド | まずまず | 速い（並列化が簡単） | セルの境目の、点が、近づくことがある |
| ポアソン円盤 | 自然 | やや遅い（順序が、必要） | GPU での並列化が、難しい |
| ブルー ノイズ テクスチャ | 自然 | 速い（テクスチャを引くだけ） | 密度の閾値で、間引くと、ブルー ノイズが、保たれる |

Lagae と Dutré（2008）は、ポアソン円盤を、作る、さまざまな方法を、比較しています。

## ③ 決定性（同じ結果にする）

配置が、**生成のたびに、変わる**と、セーブ後に、木の位置が、変わり、消した木が、元に戻ります。**位置を、座標から、決定的に決める**ようにします。

| 方法 | 内容 |
| --- | --- |
| 座標から、乱数の種を作る | `seed = Hash(cell_x, cell_y, world_seed)`。同じセルは、必ず、同じ点 |
| 乱数を、共有しない | 「全体で、1 つの乱数列を、順に消費する」と、生成順が変わると、結果も変わる。**セルごとに、独立した乱数**を使う |
| 変更は、差分で保存 | 「このセルの、3 番目の木を、伐採した」だけを、保存する。木の位置自体は、保存しない |

```hlsl
// セルの座標と、全体の種から、決定的な乱数を作る（PCG ハッシュ）。
float Random01(int2 cell, uint world_seed, uint channel) {
  uint h = Pcg(cell.x + Pcg(cell.y + Pcg(world_seed + channel)));
  return (h & 0xffffffu) / 16777216.0;
}
```

## 実行時の配置（GPU で生成する）

近年の、大規模なゲームでは、**配置を、実行時に、GPU の計算シェーダーで、生成**します。van Muijden（2017）は、Horizon Zero Dawn で、プレイヤーの周りに、**木・岩・草を、リアルタイムに配置する**仕組みを、発表しています。

| 項目 | 内容 |
| --- | --- |
| 入力 | 高さ、傾き、植生マスク、道のマスクなど、地形の属性マップ |
| 処理 | 計算シェーダーが、各セルで、決定的に、点の位置と、種類、サイズ、回転を計算する |
| 出力 | **インスタンス バッファ**（位置、回転、スケール）。そのまま、描画に使う |
| 利点 | ディスクに、配置データを、持たなくてよい。地形を編集すると、配置が、自動で更新される |
| 注意 | 毎フレームでなく、**カメラが、動いた分の、新しい範囲だけ**、生成する（タイルのキャッシュ） |

生成した点を、描画へつなぐ方法は、[Instancing](../vegetation/instancing.md) と [Vegetation Culling](../vegetation/culling.md) を見てください。

## 配置の、優先度と、除外

複数の種類（木、低木、草、岩）を、重ならないように置くとき、**大きいものから先に、置きます**。

| 順 | 種類 | 理由 |
| --- | --- | --- |
| 1 | 岩・大木 | 大きく、数が少ない。先に置いて、場所を確保 |
| 2 | 低木・小さい木 | 大きな物の周りを、避けて置く |
| 3 | 草・花 | 残った場所に、密に、置く |

| 除外する場所 | 内容 |
| --- | --- |
| 道・建物の敷地 | 密度マップで、0 にする |
| 先に置いた物の周り | 半径 r の中には、置かない（ポアソン円盤の、最小距離を、種類ごとに変える） |
| 水の中 | 水位より、低い場所 |

''', before="## よくあるミス")
pg.Refs("terrain/generation/placement.md", [BRIDSON, LAGAE, MUIJDEN, HASH, "Cook, \"Stochastic Sampling in Computer Graphics\", ACM Transactions on Graphics, Vol. 5, No. 1, 1986（ジッタード サンプリングと、ブルー ノイズ的な分布）"])

# ---------------------------------------------------------------- timing
pg.Dedup("terrain/generation/timing.md")
pg.Add("terrain/generation/timing.md", '''
## 地形は、いつ作るか

地形の生成（ノイズ、侵食、配置）を、**いつ実行するか**は、設計の、最初の分かれ道です。

| タイミング | 内容 | 向くもの |
| --- | --- | --- |
| オフライン（ツール） | 制作時に、地形を生成して、結果を、ファイルに保存する。**ゲームは、読み込むだけ** | 手作りの、ステージ。侵食など、重い処理を使う地形 |
| ロード時 | 起動、またはステージ開始時に、生成する。数秒〜数十秒、待つ | 毎回違う、ランダム生成のステージ（シード値から） |
| ストリーミング（実行時） | プレイヤーが、近づいた範囲だけを、**その場で、生成する** | 巨大な、あるいは、無限の世界（マインクラフト型、ノーマンズ スカイ型） |
| 毎フレーム | 毎フレーム、GPU で計算する | 動く地形（水面、砂漠の風紋）、軽いノイズだけ |

## 選ぶときの基準

| 観点 | オフライン | ロード時 | ストリーミング |
| --- | --- | --- | --- |
| 生成の重さの許容 | **いくらでも重くできる** | 数秒〜数十秒 | 1 タイルあたり、数ミリ秒（フレームを止めない） |
| 侵食の使用 | 使える（数千ステップ） | 軽い侵食のみ | 難しい（タイル間の、整合性） |
| 結果の再現性 | **保存したデータなので、完全に同じ** | シードから、同じ（環境によって、浮動小数点の差に、注意） | 同じ（決定的な式で、組む必要がある） |
| ディスク容量 | **大きい**（地形データを持つ） | 小さい（シードだけ） | 小さい |
| 編集 | アーティストが、手で、直せる | 生成後に、直せない | 直せない（ルールを直す） |
| 世界の広さ | ディスクの容量に、比例 | メモリに、収まる範囲 | **事実上、無限** |

## オフライン生成の流れ

ほとんどの、手作りのゲームは、この方式です。

```text
ツール:  ノイズ → 高さの変換 → 侵食 → 川 → 手で修正 → 配置のルール適用
              ↓
          保存: 高さマップ、スプラット マップ、配置データ（バイナリ）
              ↓
ゲーム:  読み込んで、描画する
```

| 利点 | 内容 |
| --- | --- |
| 品質 | 重い処理が使える。アーティストが、**何度でも調整して、気に入った形で、確定できる** |
| 起動の速さ | 読み込むだけ |
| 安定性 | 環境が、違っても、結果が、変わらない |

## 実行時の生成：落とし穴

### ① 継ぎ目をなくす

地形を、チャンクに分けて生成すると、**隣のチャンクとの境目**で、形が食い違いやすくなります。

| 方法 | 内容 |
| --- | --- |
| ワールド座標で、ノイズを計算する | チャンクごとに、座標が、ずれても、同じ式で、同じ値になる（[fBm](fbm.md)） |
| 侵食には、余白を付ける | 侵食は、周りの画素に、影響される。チャンクの周りに、数十画素の、余白を足して、計算し、余白は、捨てる |
| 境界の高さを共有する | 隣り合うチャンクが、同じ境界の画素を、**同じ値で、持つ** |

### ② フレームを、止めない

1 つのチャンクの生成が、数十ミリ秒かかると、**画面が、カクつきます**。

| 対策 | 内容 |
| --- | --- |
| 非同期で生成する | ワーカー スレッド（CPU）、または、非同期コンピュート（GPU）で、裏で作る |
| 予算を決める | 1 フレームに、生成に使う時間を、制限する（例：2 ms まで） |
| 細かく分割する | 1 つのチャンクを、数フレームに分けて、少しずつ作る |
| 先読みする | プレイヤーが、近づく前に、方向を予測して、作り始める |
| 低解像度から作る | まず、粗い地形を出して、後から、細かくする（LOD と、組み合わせる） |

### ③ 決定性を守る

実行時に、同じ場所が、同じ地形でないと、**ゲームが成り立ちません**（セーブしても、地形が違う、マルチプレイで、人によって地形が違う）。

| 注意点 | 内容 |
| --- | --- |
| 乱数 | グローバルな、乱数列を使わず、**座標から、種を作る**（[Placement Generation](placement.md)） |
| 浮動小数点 | GPU が違うと、`sin`、`cos`、`pow` の、結果が、わずかに違う。整数のハッシュと、基本的な演算だけを使う。重要な値は、**CPU で、計算する** |
| 生成の順序 | 生成の順序が変わっても、同じ結果になること（チャンクが、ほかのチャンクに、依存しないこと） |
| 変更の保存 | プレイヤーが、地形を変えたら、**元の地形からの差分**を、保存する |

## キャッシュ

実行時に、生成した地形を、**ディスクに、キャッシュ**しておくと、2 回目以降は、生成が、省けます。

| 項目 | 内容 |
| --- | --- |
| キャッシュのキー | シード、チャンクの座標、**生成アルゴリズムのバージョン** |
| バージョン管理 | アルゴリズムを、変えたら、**古いキャッシュを、無効にする**（バージョンを、キーに含める） |
| 容量の上限 | 古いものから、削除する（LRU） |

## 実際の組み合わせ

多くのゲームは、**1 つの方式だけでなく、組み合わせて**います。

| 組み合わせ | 例 |
| --- | --- |
| オフライン ＋ 実行時の配置 | 地形は、手作りで、焼いて保存。草・木の配置は、実行時に、GPU で生成（Horizon Zero Dawn のような構成） |
| ロード時の生成 ＋ 手作りの特別な場所 | 全体は、シードから、生成。拠点などの重要な場所だけ、手作りの地形で、上書きする |
| ストリーミング ＋ 低解像度の、事前計算 | 遠景は、事前に作った、粗い地形。近景だけ、実行時に、細かくする |

''', before="## よくあるミス")
pg.Refs("terrain/generation/timing.md", [MUIJDEN, GALIN, EBERT, HASH])

pg.Refs("terrain/generation/index.md", [EBERT, PERLIN02, MUSGRAVE89, MEI, GENEVAUX, GALIN])
print("ok")
