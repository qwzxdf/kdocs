import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

FOURNIER = '''Fournier, Reeves, "A Simple Model of Ocean Waves", SIGGRAPH 1986（Gerstner 波を、CG に持ち込んだ論文）'''
FINCH = '''Finch, "Effective Water Simulation from Physical Models", GPU Gems, Chapter 1, 2004（サイン波と Gerstner 波の、GPU 実装）'''
TESSENDORF = '''Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（FFT による海面の合成。ほとんどの FFT 海面の、出発点）'''
PHILLIPS = '''Phillips, "The Equilibrium Range in the Spectrum of Wind-Generated Waves", Journal of Fluid Mechanics, Vol. 4, 1958（Phillips スペクトル）'''
JONSWAP = '''Hasselmann et al., "Measurements of Wind-Wave Growth and Swell Decay during the Joint North Sea Wave Project (JONSWAP)", Deutsche Hydrographische Zeitschrift, Reihe A, Vol. 8, No. 12, 1973'''
HORVATH = '''Horvath, "Empirical Directional Wave Spectra for Computer Graphics", Digital Production Symposium 2015（方向分布を含む、実測に基づくスペクトル）'''
COOLEY = '''Cooley, Tukey, "An Algorithm for the Machine Calculation of Complex Fourier Series", Mathematics of Computation, Vol. 19, 1965（FFT の原典）'''
OLANO = '''Olano, Baker, "LEAN Mapping", Symposium on Interactive 3D Graphics and Games 2010（法線マップを、ミップで正しく平均する）'''
PIERSON = '''Pierson, Moskowitz, "A Proposed Spectral Form for Fully Developed Wind Seas Based on the Similarity Theory of S. A. Kitaigorodskii", Journal of Geophysical Research, Vol. 69, 1964'''
KERNER = '''Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015（船の浮力・抗力・水しぶき）'''
JENSEN = '''Jensen, Golias, "Deep-Water Animation and Rendering", Gamasutra, 2001'''

# ---------------------------------------------------------------- sine waves
pg.Dedup("water/waves/sine-waves.md")
pg.Add("water/waves/sine-waves.md", '''
## 波の式を、1 つずつ読む

進行波を、1 本ぶん、書き下します。位置を `p = (x, z)`、進行方向を単位ベクトル `D`、振幅を `A`、波長を `λ`、位相速度を `c` とします。

```text
h(p, t) = A × sin( ω × (D · p) + φ × t )

ω = 2π / λ          波数（1 m あたりの位相の進み）
φ = c × ω           時間方向の角周波数（1 秒あたりの位相の進み）
D · p               波の進む向きに、測った距離
```

`D · p` は、波の進行方向に沿った、距離です。これが 0 のとき、`x = 0` から見た、波頭の位置は変わりません。**位相が `ω (D·p) + φ t`** なので、時間が進むと、同じ位相の場所が、**`D` の向きに、`c` の速さで、進みます**。確かめます。位相が一定なら、`ω (D·p) + φ t = const` です。時間 `t` が `Δt` 進んだとき、`D·p` は、`−φ Δt / ω = −c Δt` だけ変わらなければなりません。符号を整理すると、波頭は `c` の速さで、`D` の逆向き、つまり、符号を `−φt` と書けば、`D` の向きに進みます。コードでは、`sin(ω D·p − φ t)` と書く実装もあります。**符号の、どちらを使うかを、CPU 側と GPU 側で、そろえます。**

### 波が複数あると

複数の波を足すだけです。

```text
h(p, t) = Σ_i A_i × sin( ω_i (D_i · p) + φ_i t + θ_i )
```

`θ_i` は、波ごとの、初期の位相のずれです。

## 振幅と波長の関係

波の形（尖り方）は、**振幅と波長の比**で、決まります。この比を、**急峻さ（steepness）**と呼びます。

```text
急峻さ = A / λ  （または 2πA / λ = ω A、波の、最大の傾き）
```

実際の海の波は、**波長が長いほど、振幅も大きく**、急峻さは、ほぼ一定です。

| 急峻さ ω·A | 見た目 |
| --- | --- |
| 0.05 | なだらかな、うねり |
| 0.2 | 標準的な、海の波 |
| 0.5 | 荒れた海。波頭が、尖る |
| 1.0 以上 | **物理的に、成り立たない**（波が砕ける） |

波を、手で作るとき、**「波長を決めて、振幅は、波長に比例させる」**とすると、見た目が、自然になります。

```cpp
// 波を、波長から作る。急峻さを、一定に保つ。
std::vector<Wave> MakeWaves(int count, float base_wavelength, float steepness, uint32_t seed) {
  std::vector<Wave> waves;
  Rng rng(seed);
  float wavelength = base_wavelength;
  for (int i = 0; i < count; ++i) {
    const float angle = rng.Uniform(-0.6f, 0.6f) + wind_angle;          // 風向きの周りに、ばらす
    Wave w;
    w.direction = {std::cos(angle), std::sin(angle)};
    w.wavelength = wavelength;
    w.amplitude = steepness * wavelength / (2.0f * 3.14159265f);         // A = steepness / ω
    w.speed = std::sqrt(9.81f * wavelength / (2.0f * 3.14159265f));      // 深い水の分散関係
    waves.push_back(w);
    wavelength *= rng.Uniform(0.55f, 0.75f);                             // 次の波は、短く（約 0.6 倍）
  }
  return waves;
}
```

「**次の波長を、前の 0.6 倍前後**」にすると、波の大きさが、**等比数列**で並びます。波長が 2 倍違えば、見え方が、違う波になるので、バラエティが出ます。

## 速さ：深い水の分散関係

波の速さ `c` は、勝手に決められません。**深い水（波長に比べて、水深が十分深い）**の波は、波長が決まれば、速さが決まります。

```text
c = sqrt( g λ / (2π) )         g = 9.81 m/s²
```

| 波長 λ | 速さ c |
| --- | --- |
| 1 m | 1.25 m/s |
| 10 m | 3.95 m/s |
| 100 m | 12.5 m/s |

長い波ほど、速く進みます。**すべての波を、同じ速さにすると、不自然**です（[Wave Animation Tricks](animation-tricks.md)）。

## 頂点シェーダーで、波を足す

```hlsl
struct Wave {
  float2 direction;     // 単位ベクトル
  float amplitude;
  float wavelength;
  float speed;
  float phase_offset;
  float2 pad;
};

cbuffer WaveCB : register(b2) {
  Wave g_waves[8];
  int g_wave_count;
  float g_time;
  float2 pad2;
};

// 高さと、偏微分（傾き）を、同時に計算する。
// 傾きは、法線のために使う（高さの微分を、解析的に、求められるのがサイン波の長所）。
float WaterHeight(float2 p, out float2 slope) {
  float h = 0.0;
  slope = 0.0;
  [unroll] for (int i = 0; i < 8; ++i) {
    if (i >= g_wave_count) break;
    float w = 2.0 * 3.14159265 / g_waves[i].wavelength;
    float phase = w * dot(g_waves[i].direction, p) + g_time * g_waves[i].speed * w + g_waves[i].phase_offset;
    h += g_waves[i].amplitude * sin(phase);
    // d/dp [A sin(phase)] = A × w × cos(phase) × D
    slope += g_waves[i].amplitude * w * cos(phase) * g_waves[i].direction;
  }
  return h;
}

float3 WaterNormal(float2 slope) {
  // 面 y = h(x, z) の法線: (-∂h/∂x, 1, -∂h/∂z)
  return normalize(float3(-slope.x, 1.0, -slope.y));
}
```

偏微分は、微分の公式（`sin` の微分は `cos`）から、**式で求まります**。隣の頂点を、読んで差分を取る必要がなく、正確です。

## 水面メッシュ

波を、頂点シェーダーで、足すなら、水面を、**格子メッシュ**にして、各頂点を、動かします。

| 項目 | 内容 |
| --- | --- |
| メッシュ | 平らな格子。カメラの周りを、細かく（[Geometry Clipmaps](../../terrain/lod/clipmap.md) と同じ構造が、よく使われる） |
| 頂点の間隔 | 波の、最も短い波長の、**半分以下**にする（ナイキスト）。それより粗いと、波が、**エイリアシング**する |
| 法線 | 頂点でなく、**ピクセル シェーダーで**、波を、もう一度、計算して、求める。細かい波の、陰影が出る |

### 短すぎる波を、消す

頂点の間隔が `d` のとき、**波長が `2d` より短い波**は、頂点では、正しく、表現できません。**消さずに足し込むと、波が、ちらつきます**。距離とともに、振幅を、減らします。

```hlsl
// 頂点の間隔に対して、短すぎる波は、振幅を 0 に近づける。
float AliasFade(float wavelength, float vertex_spacing) {
  return saturate((wavelength / vertex_spacing - 2.0) / 2.0);
}
```

## サイン波の、限界

| 限界 | 内容 |
| --- | --- |
| 形が、対称 | 波頭と谷が、同じ形（上下対称）。実際の波は、**波頭が尖って、谷が広い** |
| 水平には動かない | 頂点は、上下にしか動かない。波が、押し寄せる感じが、弱い |
| 規則的 | 波の数が少ないと、**周期が見える** |

尖った波頭が、欲しいときは、[Gerstner Waves](gerstner.md) に、進みます。

''', before="## よくあるミス")
pg.Refs("water/waves/sine-waves.md", [FINCH, FOURNIER, TESSENDORF, "Akenine-Möller et al., \"Real-Time Rendering\", 4th Edition, CRC Press, 2018（サンプリングとエイリアシング）"])

# ---------------------------------------------------------------- gerstner
pg.Dedup("water/waves/gerstner.md")
pg.Add("water/waves/gerstner.md", '''
## 水の粒は、円を描く

深い水を、進む波では、水の粒（水面の 1 点）は、**上下に動くだけでなく、波の進行方向にも、前後に動きます**。軌跡は、**円**です。波頭では、進行方向へ、谷では、逆向きに動きます。

```text
         波の進む向き →
      ╭───╮        ╭───╮
    ╭╯     ╰╮    ╭╯     ╰╮         ← 水面
  ╱         ╲╱╲╱         ╲
      ○ 粒は、円運動（波頭で前、谷で後ろ）
```

この動きを、そのまま、頂点に使ったのが、Gerstner 波です。粒の位置を、水平にも動かすと、**波頭の周りに、粒が集まって、尖り**、**谷では、粒が散って、広がります**。サイン波では、できない形です。

## 式

位置 `P₀ = (x₀, z₀)` にあった頂点が、時刻 `t` に、動く先は、次のとおりです。

```text
θ = ω (D · P₀) + φ t

x = x₀ + Σ Q A D.x cos θ
z = z₀ + Σ Q A D.z cos θ
y =      Σ     A       sin θ
```

| 記号 | 意味 |
| --- | --- |
| `A` | 振幅（円の半径に当たる） |
| `ω` | 波数（`2π / 波長`） |
| `φ` | 位相の速さ（`c × ω`） |
| `D` | 波の進む向き（単位ベクトル） |
| `Q` | 急峻さ（0 でサイン波、大きいほど波頭が尖る） |

`Q` を 0 にすると、水平の動きが 0 になり、サイン波と、一致します。

## 急峻さ Q の、上限

`Q` を大きくしすぎると、**波頭で、頂点が、追い越し合って、メッシュが、裏返ります**（ループができる）。裏返らない条件は、**水平の動きの、微分（ヤコビアン）が、正のまま**であることです。1 本の波なら、

```text
Q × ω × A ≤ 1       （1 本だけのとき）
```

複数の波があるとき、全部の波の水平の動きが、足し合わされるので、**合計で、1 を超えないように**します。

```text
Σ Q_i ω_i A_i ≤ 1
```

Finch（2004）は、これを、使いやすくする、**全体の急峻さ `Q`（0〜1）**を、1 つ決めて、波ごとに、次のように割る方法を、示しています。

```text
Q_i = Q / ( ω_i × A_i × 波の本数 )
```

| 全体の Q | 見た目 |
| --- | --- |
| 0 | サイン波と同じ |
| 0.5 | 適度に、尖った波頭 |
| 1.0 | 波頭が、ほぼ、ぎりぎりまで尖る（裏返らない限界） |

## 頂点シェーダー

```hlsl
struct GerstnerWave {
  float2 direction;
  float amplitude;
  float wavelength;
  float speed;
  float steepness;     // Q_i（上の式で、割った後の値）
  float2 pad;
};

cbuffer GerstnerCB : register(b2) {
  GerstnerWave g_waves[8];
  int g_wave_count;
  float g_time;
  float2 pad2;
};

// 元の位置 p0 に対する、水面の位置を返す。
float3 GerstnerDisplace(float2 p0, out float3 normal, out float jacobian) {
  float3 pos = float3(p0.x, 0.0, p0.y);
  float3 n = float3(0, 1, 0);
  // ヤコビアン（波頭が、折れているかの目安）を作る要素
  float dxdx = 0, dzdz = 0, dxdz = 0;

  [unroll] for (int i = 0; i < 8; ++i) {
    if (i >= g_wave_count) break;
    GerstnerWave w = g_waves[i];
    float k = 2.0 * 3.14159265 / w.wavelength;
    float theta = k * dot(w.direction, p0) + g_time * w.speed * k;
    float c = cos(theta), s = sin(theta);

    // 位置
    pos.x += w.steepness * w.amplitude * w.direction.x * c;
    pos.z += w.steepness * w.amplitude * w.direction.y * c;
    pos.y += w.amplitude * s;

    // 法線（Finch の式）。WA = ω A
    float wa = k * w.amplitude;
    n.x -= w.direction.x * wa * c;
    n.z -= w.direction.y * wa * c;
    n.y -= w.steepness * wa * s;

    // 水平変位の、偏微分（ヤコビアンのため）
    float ds = -w.steepness * w.amplitude * k * s;
    dxdx += ds * w.direction.x * w.direction.x;
    dzdz += ds * w.direction.y * w.direction.y;
    dxdz += ds * w.direction.x * w.direction.y;
  }
  normal = normalize(n);
  // ヤコビアン = (1 + ∂Dx/∂x)(1 + ∂Dz/∂z) − (∂Dx/∂z)(∂Dz/∂x)
  jacobian = (1.0 + dxdx) * (1.0 + dzdz) - dxdz * dxdz;
  return pos;
}
```

法線の式の `n.y` の項に、`steepness` が、掛かっていることに注意してください（サイン波の法線との違い）。

### ヤコビアンと、泡

最後の `jacobian` は、「**水平方向の、面積の変化率**」です。1 のとき変化なし、**0 に近づくと、頂点が、集まって（波頭が、折れそうに）**なり、**負になると、裏返っています**。**この値が、小さい場所に、泡を出す**のが、定番の方法です（[Crest Foam: The Jacobian](../shore-foam/crest-jacobian.md)）。

## 法線の、計算は、ピクセルで

頂点で求めた法線を、補間して渡すと、**細かい波の陰影が、出ません**。**ピクセル シェーダーでも、小さい波だけ、もう一度、計算**します。位置の水平変位が、画素ごとに、異なる点に、注意します（次の節）。

## 「元の位置」の、問題

Gerstner 波の式の入力は、**水平に動く前の位置 `P₀`** です。ところが、**画素に見えている水面の位置は、動いた後の位置 `P`** です。画素で、波の計算をするとき、`P` を `P₀` の代わりに使うと、**位置が、水平に、ずれます**。

| 状況 | 影響 |
| --- | --- |
| 頂点シェーダー | 格子の頂点が、`P₀`。そのまま使える |
| ピクセル シェーダーで、細かい波の法線を足す | `P` を、`P₀` の近似として使う。**誤差は、小さい**（急峻さが低いとき、水平の動きは小さい） |
| CPU で、浮かぶ物の、高さを求める | `P` から `P₀` を、**逆に求める**必要がある（[Floating Objects](floating.md)） |

## サイン波との、比較

| | サイン波 | Gerstner 波 |
| --- | --- | --- |
| 頂点の動き | 上下だけ | 上下 + 水平 |
| 波頭 | 丸い | **尖る** |
| 谷 | 丸い | 広い |
| 法線 | 簡単な式 | やや複雑な式 |
| コスト | `sin` 1 回 / 波 | `sin` と `cos` 1 回ずつ / 波（ほぼ同じ） |
| 泡（ヤコビアン） | 作れない | **作れる** |
| 破綻 | しない | `Q` が大きいと、メッシュが裏返る |

コストは、サイン波と、ほとんど変わりません。**Gerstner 波に、しない理由は、ほぼありません**。

''', before="## よくあるミス")
pg.Refs("water/waves/gerstner.md", [FOURNIER, FINCH, TESSENDORF, JENSEN])

# ---------------------------------------------------------------- fft ocean
pg.Dedup("water/waves/fft-ocean.md")
pg.Add("water/waves/fft-ocean.md", '''
## なぜ、FFT を使うのか

サイン波や Gerstner 波を、足すだけの海は、**8 本ほど**が限界で、**周期が、見えて**しまいます。本物の海は、**非常に多くの、波長と向きの波が、ランダムに、重なって**います。数千本の波を、足し合わせたいのですが、**1 頂点で、数千回の `sin` は、計算できません**。

**高速フーリエ変換（FFT、Cooley と Tukey、1965）**を使うと、**N×N 個の、周波数成分を、`O(N² log N)` で、一度に、空間の高さに変換**できます。256×256 の海面（65,536 本の波）を、数ミリ秒で、合成できます。Tessendorf（2001）の方法が、ほとんどの、FFT 海面の、出発点です。

## 全体の流れ

```text
① 初期スペクトル h0(k)        （起動時に 1 回、ランダムに生成する）
        ↓
② 時間発展 h(k, t)            （毎フレーム: 各周波数の位相を回す）
        ↓
③ 逆 FFT                      （周波数空間 → 空間。高さ、水平変位、傾きの、3〜5 枚）
        ↓
④ 水面の頂点シェーダーが、結果のテクスチャを読んで、頂点を動かす
```

## ① 初期スペクトル

海の波は、波数ベクトル `k = (kx, kz)`（向きと波長を表す）ごとに、**強さ（スペクトル）**を持ちます。**Phillips スペクトル**（1958）は、風が、十分に吹き続けた海の、統計を表します。

```text
P(k) = A × exp( −1 / (|k| L)² ) / |k|⁴ × | k̂ · ŵ |²

L = V² / g          風速 V の風が、作る最大の波の、大きさ
ŵ                    風向き（単位ベクトル）
k̂ = k / |k|         波の向き
A                    全体の強さ（調整用）
```

| 項 | 意味 |
| --- | --- |
| `exp(−1/(kL)²)` | `L` より、長い波は、存在しない（`k` が小さいと、0 に近づく） |
| `1 / k⁴` | 短い波ほど、弱い（波長が半分になると、強さが 1/16） |
| `|k̂ · ŵ|²` | 風と同じ向きの波が、強い。直角の波は、弱い |

実装では、風と**逆向き**の波（`k̂·ŵ < 0`）を、さらに弱めたり、**非常に短い波を、消す**（`exp(−k² l²)`、`l` は小さい長さ）項を、足したりします。

### 初期値 h0 を、乱数で作る

各 `k` について、**ガウス分布の乱数 2 つ**（`ξr`、`ξi`）を、使って、複素数の `h0(k)` を作ります。

```text
h0(k) = (1/√2) × (ξr + i ξi) × √P(k)
```

```cpp
// CPU で、起動時に 1 回、h0(k) を作る（GPU の乱数も、ガウス分布を作るのが面倒なため）。
std::vector<float4> h0(N * N);          // xy = h0(k)、zw = h0(-k) の共役
for (int m = 0; m < N; ++m) {
  for (int n = 0; n < N; ++n) {
    const float kx = (n - N / 2) * 2.0f * kPi / patch_size;
    const float kz = (m - N / 2) * 2.0f * kPi / patch_size;
    const float2 k = {kx, kz};
    const float ph = PhillipsSpectrum(k, wind, amplitude);
    const float2 g = Gaussian2(rng);                       // 標準正規分布の乱数 2 つ
    const float s = std::sqrt(ph * 0.5f);
    h0[m * N + n] = {g.x * s, g.y * s, 0, 0};
  }
}
// h0(-k) も、同じ配列から引いて、zw に入れる（中心について、反対側の要素）。
```

スペクトルは、**Phillips 以外**も、あります。JONSWAP（1973）は、**波が、育つ距離（吹送距離）**も考慮し、Horvath（2015）は、**方向の広がり**まで含めた、実測に基づくモデルを、示しています。**Phillips は、簡単で、十分に、海らしい**ので、まず、これで作ります。

## ② 時間発展

各周波数成分を、**時間とともに、位相を回し**ます。回る速さは、**分散関係**で、波長ごとに、決まります（深い水）。

```text
ω(k) = sqrt( g × |k| )

h(k, t) = h0(k) × e^{ i ω t }  +  conj( h0(−k) ) × e^{ −i ω t }
```

2 つの項は、**反対向きに進む、同じ波長の波**を表します。足し合わせると、**逆 FFT の結果が、実数**になります（海面の高さは、実数であるため）。

```hlsl
Texture2D<float4> g_h0 : register(t0);            // xy = h0(k)、zw = h0(-k)
RWTexture2D<float2> g_height_k : register(u0);    // h(k, t)
RWTexture2D<float2> g_dx_k : register(u1);        // 水平変位 x（周波数空間）
RWTexture2D<float2> g_dz_k : register(u2);        // 水平変位 z

cbuffer EvolveCB : register(b0) {
  float g_time;
  float g_patch_size;
  int g_n;
  float g_choppy;       // 水平変位の強さ（尖り具合）
};

float2 ComplexMul(float2 a, float2 b) { return float2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }

[numthreads(8, 8, 1)]
void Evolve(uint3 id : SV_DispatchThreadID) {
  float2 k = (float2(id.xy) - g_n * 0.5) * (2.0 * 3.14159265 / g_patch_size);
  float k_len = max(length(k), 1e-4);
  float w = sqrt(9.81 * k_len);

  float4 h0 = g_h0[id.xy];
  float c = cos(w * g_time), s = sin(w * g_time);

  // h(k,t) = h0(k) e^{iwt} + conj(h0(-k)) e^{-iwt}
  float2 a = ComplexMul(h0.xy, float2(c, s));
  float2 b = ComplexMul(float2(h0.z, -h0.w), float2(c, -s));
  float2 hk = a + b;
  g_height_k[id.xy] = hk;

  // 水平変位（Tessendorf の式）: D(k) = −i (k / |k|) h(k)
  float2 minus_i_h = float2(hk.y, -hk.x);                      // −i × h
  g_dx_k[id.xy] = minus_i_h * (k.x / k_len) * g_choppy;
  g_dz_k[id.xy] = minus_i_h * (k.y / k_len) * g_choppy;
}
```

## ③ 逆 FFT

周波数空間の画像（複素数）を、空間の画像に、変換します。**2 次元の FFT は、行ごとに 1 次元の FFT をして、そのあと、列ごとに、1 次元の FFT をする**ことで、行えます。

### 1 次元の FFT（バタフライ演算）

N 点の FFT は、`log₂ N` 段の**バタフライ**で、できます。N = 256 なら、8 段です。各段で、**2 つの要素から、2 つの要素を作ります**。

```text
段 s（0 〜 log₂N − 1）、要素 x について:
  span = 2^s
  上の翼（top）か:  (x mod 2^(s+1)) < span
  相手: top なら (x, x + span)、bottom なら (x − span, x)
  twiddle w = e^{ 2πi × (x mod 2^(s+1)) / 2^(s+1) }       （逆変換なので、符号は +）
  出力[x] = 入力[lo] + w × 入力[hi]                         （lo = 小さい方の番号、hi = 大きい方）
```

最初の段（`s = 0`）だけ、入力を、**ビット反転した番号**から読みます（`x = 0b001` なら `0b100`）。これは、FFT の、決まりごとです。

```hlsl
// バタフライ 1 段（横方向）。ping-pong する 2 枚のテクスチャで、段ごとに、読み書きを入れ替える。
Texture2D<float2> g_src : register(t0);
RWTexture2D<float2> g_dst : register(u0);

cbuffer FftCB : register(b0) { int g_stage; int g_n; int2 pad; };

uint BitReverse(uint x, uint bits) { return reversebits(x) >> (32 - bits); }

[numthreads(8, 8, 1)]
void ButterflyHorizontal(uint3 id : SV_DispatchThreadID) {
  uint x = id.x;
  uint span = 1u << g_stage;
  uint group = x & ((span << 1) - 1);                 // x mod 2^(s+1)
  bool top = group < span;
  uint lo = top ? x : x - span;
  uint hi = lo + span;
  float angle = 2.0 * 3.14159265 * float(group) / float(span << 1);
  float2 w = float2(cos(angle), sin(angle));

  uint bits = firstbithigh((uint)g_n);                // log2(N)
  uint lo_idx = (g_stage == 0) ? BitReverse(lo, bits) : lo;
  uint hi_idx = (g_stage == 0) ? BitReverse(hi, bits) : hi;
  float2 p = g_src[uint2(lo_idx, id.y)];
  float2 q = g_src[uint2(hi_idx, id.y)];
  g_dst[id.xy] = p + ComplexMul(w, q);
}
// 縦方向は、同じ計算を、x と y を入れ替えて行う。
```

実際の実装では、**1 つの計算シェーダーで、行全体を、グループ共有メモリに載せて、全段を一度に行う**ほうが、はるかに速いです（読み書きが、段ごとにメモリを往復しないため）。まず、上のように、段ごとの実装で、仕組みを理解してから、最適化します。

### 符号の補正

`h(k)` の、`k` の原点を、**画像の中心**に、置いたので、逆 FFT の結果は、**1 画素おきに、符号が反転**しています。`(−1)^(x+z)` を、掛けて、補正します。

```hlsl
float sign_fix = ((id.x + id.y) & 1) ? -1.0 : 1.0;
height = fft_result.x * sign_fix;
```

## ④ 水面に使う

逆 FFT で、次の画像が得られます。

| 画像 | 内容 | 使い方 |
| --- | --- | --- |
| 高さ `h` | 水面の高さ | 頂点の y 座標 |
| 水平変位 `Dx`、`Dz` | 頂点の水平の動き（尖らせるため） | 頂点の x、z 座標に足す |
| 傾き `∂h/∂x`、`∂h/∂z` | 法線の元 | ピクセルの法線 |
| ヤコビアン | 波頭が折れているか | 泡（[Crest Foam: The Jacobian](../shore-foam/crest-jacobian.md)） |

```hlsl
// 頂点シェーダー: FFT の結果を読んで、頂点を動かす。
float3 disp = g_displacement.SampleLevel(g_linear_wrap, p0 / g_patch_size, 0).xyz;   // x = Dx, y = h, z = Dz
float3 world = float3(p0.x + disp.x, disp.y, p0.y + disp.z);
```

## カスケード（繰り返しを隠す）

FFT の結果は、**`patch_size` ごとに、同じ模様が、繰り返します**（周期的）。1 枚だけだと、**遠くで、繰り返しが、見えます**。

**大きさの違う、複数の FFT（カスケード）**を、重ねて、解決します。

| カスケード | 領域の大きさ | 担当する波 |
| --- | --- | --- |
| 0 | 約 1,000 m | 長いうねり |
| 1 | 約 200 m | 中くらいの波 |
| 2 | 約 30 m | 短いさざ波 |

大きさを、**互いに素に近い比**（たとえば 250 m と 37 m）にすると、**全体の、繰り返しの周期が、非常に、長く**なります。各カスケードには、**それぞれが担当する波長の範囲**のスペクトルだけを、入れます（重複を、避けるため）。

## コストと、使い分け

| 項目 | 目安 |
| --- | --- |
| FFT の大きさ | 256×256（標準）、512×512（高品質） |
| 1 カスケードの、FFT | 高さ・水平変位・傾きで、3〜5 回の逆 FFT。GPU で、0.1〜0.5 ms |
| カスケード 3 つ | 数 ms 以内 |
| メモリ | 256×256 の `R32G32_FLOAT` が、数枚（数 MB） |

| 場面 | 方式 |
| --- | --- |
| 近景（プレイヤーの周り） | FFT（細かい波、波頭の折れ、泡） |
| 遠景 | 低周波のカスケードだけ、または、サイン波 |
| 低スペックの環境 | Gerstner 波（[Gerstner Waves](gerstner.md)） |

FFT 海面は、**物を浮かべる**ときに、CPU でも、高さが必要になります（[Floating Objects](floating.md)）。

''', before="## よくあるミス")
pg.Refs("water/waves/fft-ocean.md", [TESSENDORF, PHILLIPS, JONSWAP, HORVATH, COOLEY, PIERSON])

# ---------------------------------------------------------------- normals
pg.Dedup("water/waves/normals.md")
pg.Add("water/waves/normals.md", '''
## 法線の、3 つの源

水面の、陰影を決める法線は、**複数の源を、重ねて**作ります。

| 源 | 内容 | 波長の目安 |
| --- | --- | --- |
| 大きな波（頂点で動かすもの） | 波の式の、解析的な微分、または FFT の傾き | 数メートル以上 |
| 中くらいの波 | ピクセルで、もう一度、波の式を計算する | 数十センチ〜数メートル |
| 細かいさざ波 | **法線マップ**を、2 枚、逆向きに流して重ねる | 数センチ〜数十センチ |

頂点の間隔より、細かい波は、**ジオメトリには、現れません**。**法線だけで、表現**します。

## 解析的な法線

高さ関数 `h(x, z)` が、式で書けるなら、**偏微分も、式で書けます**。法線は、`(−∂h/∂x, 1, −∂h/∂z)` を、正規化したものです。

```hlsl
// サイン波の高さの偏微分: A × ω × cos(phase) × D
float2 slope = 0;
[unroll] for (int i = 0; i < kWaveCount; ++i) {
  float w = 2.0 * 3.14159265 / g_waves[i].wavelength;
  float phase = w * dot(g_waves[i].direction, p) + g_time * g_waves[i].speed * w;
  slope += g_waves[i].amplitude * w * cos(phase) * g_waves[i].direction;
}
float3 normal = normalize(float3(-slope.x, 1.0, -slope.y));
```

Gerstner 波の法線の式は、[Gerstner Waves](gerstner.md) にあります。**差分で求める**（隣の点との高さの差）方法より、**速く、正確**です。差分は、頂点の間隔より、細かい波を、取りこぼします。

## 法線マップを、2 枚、流す

細かいさざ波は、**タイルできる法線マップ**を使い、**向きを変えて、2 枚**を、**逆向きに、流して**重ねます。1 枚だと、**一方向に、流れているだけ**に、見えます。

```hlsl
Texture2D<float2> g_normal_map : register(t3);        // R8G8: xz の傾きを、格納

float3 DetailNormal(float2 world_xz, float time) {
  // 2 枚を、異なる大きさ、向き、速さで、読む。
  float2 uv1 = world_xz * 0.13 + float2( 0.03, 0.02) * time;
  float2 uv2 = world_xz * 0.07 + float2(-0.02, 0.04) * time;
  float2 n1 = g_normal_map.Sample(g_linear_wrap, uv1) * 2.0 - 1.0;
  float2 n2 = g_normal_map.Sample(g_linear_wrap, uv2) * 2.0 - 1.0;
  // 傾きを足し合わせる（法線マップの、傾きは、そのまま足してよい）。
  float2 slope = n1 + n2;
  return normalize(float3(-slope.x, 1.0, -slope.y));
}
```

法線ベクトルを、そのまま足すのではなく、**傾き（`xz` 成分）を、足してから、`y = 1` で正規化**します。傾きは、足し合わせて、良い量です。

### 大きな波と、細かい波を、組み合わせる

大きな波の、法線 `N_big` の上に、細かい波の傾きを、**乗せます**。

```hlsl
// 大きな波の法線の、傾きと、細かい波の傾きを足す（簡易な合成）。
float2 slope_big = float2(-N_big.x, -N_big.z) / max(N_big.y, 1e-3);
float2 slope_total = slope_big + slope_detail;
float3 N = normalize(float3(-slope_total.x, 1.0, -slope_total.y));
```

法線マップの合成方法は、ほかにも、いくつかあります（UDN、whiteout、RNM。[Triplanar Mapping](../../terrain/texturing/triplanar.md) の、法線の混ぜ方の表を、参照）。水面は、**ほぼ水平**なので、傾きを、足す、簡易な方法で、十分です。

## 距離で、弱める（エイリアシングを防ぐ）

遠くの水面で、**細かい法線が、ちらつきます**。1 画素の中に、法線の細かい凹凸が、**何周期も**入るためです。距離とともに、**法線の傾きを、弱めます**。

```hlsl
// 距離に応じて、細かい波の傾きを弱める（1 画素に収まる凹凸は、平均すると、ほぼ平らになるため）。
float fade = saturate(1.0 - (dist - fade_start) / (fade_end - fade_start));
slope_detail *= fade;
```

| 距離 | 細かい波の傾き |
| --- | --- |
| 近い（〜50 m） | そのまま |
| 中間（50〜200 m） | だんだん、弱める |
| 遠い（200 m〜） | 0（水面は、ほぼ平ら） |

ただし、**傾きを、弱めるだけだと、遠くの水面の、反射が、鏡のように**、なります。実際の水面は、細かい凹凸のために、**ぼやけた反射**になります。弱めた分は、**粗さ（roughness）に、足します**。

### 法線の分散を、粗さに

細かい凹凸を、**法線の、ばらつき（分散）**として、粗さへ、反映する考え方があります（LEAN マッピング、Olano と Baker、2010）。

```hlsl
// 傾きの、平均と、2 乗の平均を、ミップで、保存しておく（LEAN マッピング）。
// ミップを下がると、傾きの平均は、0 に近づくが、「ばらつき」は、残る。
float2 mean_slope = lean_b.Sample(g_linear_wrap, uv).xy;                 // 傾きの平均
float3 mean_sq = lean_a.Sample(g_linear_wrap, uv).xyz;                   // 傾きの 2 乗の平均
float2 variance = float2(mean_sq.x - mean_slope.x * mean_slope.x,
                         mean_sq.y - mean_slope.y * mean_slope.y);
float roughness_add = sqrt(max(variance.x + variance.y, 0.0));            // 遠くで、粗さが増える
```

法線マップを、そのまま、ミップで、平均すると、**遠くの傾きが、0 に近づいて、水面が、ピカピカの鏡**になります。LEAN マッピングは、この問題を解決する方法です。簡易には、**距離で、粗さを、上げていく**（`roughness = lerp(r0, r1, fade)`）だけでも、効果があります。

## FFT 海面の法線

FFT の逆変換で、**高さ**だけでなく、**傾き（∂h/∂x、∂h/∂z）**も、得られます。周波数空間で、`i k h(k)` を計算して、逆 FFT します。

```hlsl
// 傾きの、周波数空間での計算: ∂h/∂x ↔ i kx h(k)、∂h/∂z ↔ i kz h(k)
float2 i_h = float2(-hk.y, hk.x);                // i × h
g_slope_x_k[id.xy] = i_h * k.x;
g_slope_z_k[id.xy] = i_h * k.y;
```

水平変位（Gerstner 波や FFT の、尖った波頭）が、あるときは、**法線に、水平変位の影響を、補正**します。

```text
N = normalize( −slope_x / (1 + ∂Dx/∂x),  1,  −slope_z / (1 + ∂Dz/∂z) )
```

波頭で、水平に頂点が、集まっているところは、**面積が小さく**、補正がないと、法線が、やや、緩く、出ます。

''', before="## よくあるミス")
pg.Refs("water/waves/normals.md", [FINCH, TESSENDORF, OLANO, "Toksvig, \"Mipmapping Normal Maps\", Journal of Graphics Tools, Vol. 10, No. 3, 2005"])

# ---------------------------------------------------------------- floating
pg.Dedup("water/waves/floating.md")
pg.Add("water/waves/floating.md", '''
## CPU でも、水面の高さが、必要になる

船、浮き輪、樽、プレイヤーの泳ぎを、波に合わせるには、**CPU（ゲームのロジックや、物理）が**、水面の高さを、知る必要があります。水面は、GPU の頂点シェーダーで、動いているので、**CPU が、同じ式で、計算**するか、GPU から、結果を、取り出します。

| 方法 | 内容 | 向く波 |
| --- | --- | --- |
| 同じ式を、CPU で、計算する | シェーダーの式を、C++ で、書き直す。**時間も、同じ値を、使う** | サイン波、Gerstner 波 |
| GPU の結果を、読み戻す | 浮かぶ物の位置だけ、高さを、GPU で、計算して、ステージング バッファで、CPU へ返す。**数フレーム遅れる** | FFT |
| 低解像度の、近似を、CPU で持つ | 大きな波（低周波のカスケード）だけを、CPU で、計算する | FFT（大きなうねりだけで、船が、動くなら十分） |

## 「元の位置」を、逆算する

Gerstner 波では、頂点が**水平にも動く**ので、「`(x, z)` の位置の水面の高さ」は、**単純に、式に `(x, z)` を代入しても、求まりません**。式の入力は、動く前の位置 `P₀` で、見えている位置 `P` は、動いた後だからです。

```text
P = P₀ + D(P₀)         ← D は、水平の動き。P が、与えられたとき、P₀ を求めたい
```

**不動点反復**で、近似的に、解けます。

```cpp
// 位置 p（見えている位置）に対応する、動く前の位置 p0 を、反復で求める。
float2 FindUndisplacedPosition(float2 p, float time, int iterations = 4) {
  float2 p0 = p;                                  // 最初の推定: 動いていないとする
  for (int i = 0; i < iterations; ++i) {
    const float2 d = HorizontalDisplacement(p0, time);   // 推定した p0 での、水平の動き
    p0 = p - d;                                    // p = p0 + d を、p0 について解く
  }
  return p0;
}

float WaterHeightAt(float2 p, float time) {
  const float2 p0 = FindUndisplacedPosition(p, time);
  return Height(p0, time);                         // 求めた p0 で、高さを計算
}
```

反復は、**3〜4 回**で、ほぼ収束します。急峻さが小さい（`Q` が小さい）ほど、速く収束します。

## 浮力：簡単な方法（点サンプリング）

物体の、何点か（船体の、四隅や、底の複数点）で、水面の高さを調べ、**「水面より、下にある分だけ、上向きの力を、かける」**という方法です。

```cpp
struct FloatPoint { float3 local_position; };       // 物体のローカル座標での、浮力点

void ApplyBuoyancy(RigidBody& body, const std::vector<FloatPoint>& points, float time) {
  const float rho = 1000.0f;                         // 水の密度 (kg/m³)
  const float g = 9.81f;
  const float point_volume = body.volume / points.size();   // 各点が、受け持つ体積の目安

  for (const FloatPoint& fp : points) {
    const float3 world = body.LocalToWorld(fp.local_position);
    const float surface_y = WaterHeightAt({world.x, world.z}, time);
    const float depth = surface_y - world.y;         // 水面の下にある深さ（正なら、水の中）
    if (depth <= 0.0f) continue;                      // 水面より上: 力なし

    // 浮力: 沈んでいる体積の、水の重さ。深く沈むほど、強い（ただし、点の体積が、上限）
    const float submerged = std::clamp(depth / point_height, 0.0f, 1.0f);
    const float3 buoyancy = {0.0f, rho * g * point_volume * submerged, 0.0f};
    body.ApplyForceAtPoint(buoyancy, world);

    // 水の抵抗（動きを、減衰させる）
    const float3 v = body.VelocityAtPoint(world);
    body.ApplyForceAtPoint(-v * drag_coefficient * submerged, world);
  }
}
```

| 項目 | 内容 |
| --- | --- |
| 点の数 | 4〜16 点。多いほど、傾きの表現が、正確 |
| 抵抗 | 速度に比例した力を、かけて、**揺れを、収束**させる。ないと、跳ね続ける |
| 回転 | 点で力をかけると、**トルク（回転力）**も、自然に生じ、波の傾きに、合わせて、傾く |
| 安定性 | 浮力が、強すぎると、**物理が発振**する。抵抗と、物体の質量で、調整する |

## 浮力：より、現実的な方法

Kerner（2015）は、船の、水との相互作用を、**船体の三角形ごとに**、扱う方法を、整理しています。

| 力 | 内容 |
| --- | --- |
| 静水圧（浮力） | 水面の下の、三角形ごとに、**水深に比例した圧力**を、法線の向きに、かける |
| 粘性抗力 | 水と、船体の、相対速度に比例した、摩擦。三角形ごと |
| 圧力抗力 | 船体が、水を、押しのける力。進行方向を向いた、三角形が、強く受ける |
| スラミング（衝撃） | 船体が、水面に、叩きつけられたときの、衝撃の力 |

点サンプリングより、**計算は、重い**ですが、船の動きが、はるかに自然です。**水に浸かっている三角形を、求める**処理（水面と三角形の、切り取り）が、必要になります。

## FFT 海面での、高さ

FFT の海面は、頂点シェーダーが、テクスチャから、高さを読んでいます。CPU で、同じ高さを知るには、

| 方法 | 内容 |
| --- | --- |
| 読み戻し | 高さのテクスチャを、**ステージング テクスチャにコピー**して、CPU が読む。**1〜3 フレーム遅れる**。遅れを、許容できるほど、ゆっくりした動き（船）なら、問題ない |
| 低周波だけを、CPU で、計算する | 大きなカスケードの、**高さマップを、CPU 側にも持ち**、双線形補間で読む |
| 数点だけ、GPU で、計算する | 浮力点の位置だけを、計算シェーダーで、サンプリングして、小さなバッファへ書き、読み戻す |

```cpp
// 高さのテクスチャを、読み戻す（非同期）。
context->CopyResource(staging.Get(), height_texture.Get());
// 次のフレーム（以降）に、Map して読む。すぐに Map すると、GPU の完了を待ってしまう。
D3D11_MAPPED_SUBRESOURCE m;
if (SUCCEEDED(context->Map(staging_prev.Get(), 0, D3D11_MAP_READ, D3D11_MAP_FLAG_DO_NOT_WAIT, &m))) {
  // CPU 側のコピーを、更新する
  context->Unmap(staging_prev.Get(), 0);
}
```

`D3D11_MAP_FLAG_DO_NOT_WAIT` を指定すると、**GPU が、まだ終わっていないとき、待たずに、失敗を返す**ので、フレームを、止めません。失敗したら、次のフレームに、もう一度、試します。

## 時間を、そろえる

GPU の見た目と、CPU の浮力の、**時間の値**が、ずれると、**船が、波と合わずに、浮きます**。

| 注意点 | 内容 |
| --- | --- |
| 同じ時間を、使う | シェーダーに渡す `time` と、CPU の波の計算の `time` を、**同じ変数**から、作る |
| 時間の折り返し | 折り返す（`fmod`）なら、両方で、同じ周期を、使う（[Wave Animation Tricks](animation-tricks.md)） |
| 読み戻しの遅れ | 1〜3 フレーム遅れた高さを、使うなら、**遅れた時間の、波**として、扱う（その時間に、読み戻した値だから） |

''', before="## よくあるミス")
pg.Refs("water/waves/floating.md", [KERNER, FINCH, TESSENDORF, "Microsoft Learn, \"D3D11_MAP_FLAG\"（`D3D11_MAP_FLAG_DO_NOT_WAIT`）"])

# ---------------------------------------------------------------- animation tricks
pg.Dedup("water/waves/animation-tricks.md")
pg.Add("water/waves/animation-tricks.md", '''
## 水深が、波の速さを決める（分散関係）

[Summing Sine Waves](sine-waves.md) では、深い水の速さ `c = √(gλ / 2π)` を、使いました。**水深が、浅くなると**、波の速さは、変わります。一般の式（線形波動論）は、次のとおりです。

```text
ω² = g × k × tanh(k × d)        ω: 角周波数、k: 波数（2π/λ）、d: 水深
c  = ω / k                       位相速度
```

| 水深 d と波長 λ の関係 | `tanh(kd)` | 速さ c | 呼び方 |
| --- | --- | --- | --- |
| `d > λ/2`（深い） | ≈ 1 | `√(gλ / 2π)`（波長で決まる） | 深水波 |
| `d < λ/20`（浅い） | ≈ kd | `√(g d)`（水深で決まる） | 浅水波 |
| その間 | 1 と kd の間 | 上の式で計算 | 中間 |

浅くなると、**波長に関係なく、同じ速さ**になり、岸に近づくと、**波が、遅くなって、波長が、縮み、波頭が、切り立ちます**。この、岸に向かって、波が、変わる様子が、**海岸の、波らしさ**です。

```hlsl
// 水深を考慮した、波の角周波数。
float WaveOmega(float k, float depth) {
  return sqrt(9.81 * k * tanh(k * depth));
}
```

地形の水深（[Color by Water Depth](../shading/depth-color.md) の、水深マップ）を読んで、**各場所で、速さを変える**と、波が、岸に向かって、**曲がる**（屈折）様子も、出せます。ただし、位相を、場所ごとに、変えると、**位相が、ずれていって、波が、ねじれます**。実際には、**波の向きを、水深の勾配に、少し寄せる**程度の、簡易な方法が、使われます。

## 風と、波の関係

波のパラメーターは、**風の強さ**から、決められます。

| 風速 U（m/s） | 波の状態 | 有義波高 H（m）の目安 |
| --- | --- | --- |
| 3 | さざ波 | 0.1 |
| 6 | 小さな波 | 0.5 |
| 10 | 白波が立つ | 2 |
| 15 | 荒れた海 | 4〜5 |
| 20 | 大しけ | 8 |

**十分に、風が吹き続けた海**（完全に発達した海）では、波の高さは、風速の 2 乗に、ほぼ比例します（Pierson と Moskowitz、1964）。

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

**天候が変わる**（風が強くなる）とき、波の振幅を、**急に変えると、水面が、ぱっと、動きます**。パラメーターを、**時間をかけて、補間**します。

## 波の LOD

遠くの水面は、細かい波が、**ちらつく**ので、省きます。

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

**波の本数を、変える**よりも、**振幅を、連続的に、減らす**ほうが、切り替えのポップが出ません。

## 規則性を崩す

波が、**同じ形で、一定の方向に、進み続ける**と、機械的に見えます。

| 工夫 | 内容 |
| --- | --- |
| 向きを、ばらす | 波ごとの向きを、風向きの周りに、**±30 度**くらい、ばらつかせる |
| 波長を、不規則に | 波長を、等比数列にせず、**少し、乱数**で、ずらす |
| 位相に、ノイズ | 位置に依存する、低周波のノイズを、位相に足す。波頭が、まっすぐに、並ばない |
| 振幅の変動 | 振幅を、**低周波のノイズ**で、場所ごとに、変える（波の、強い所と、弱い所） |
| 時間に、ゆらぎ | 振幅を、時間でも、ゆっくり、変える（突風、静けさ） |

```hlsl
// 位相に、位置に依存する、ゆらぎを足す。
float noise = g_noise.SampleLevel(g_linear_wrap, p * 0.01, 0);        // 低周波ノイズ
float phase = k * dot(dir, p) + omega * time + noise * 2.0;           // 位相を、最大 2 rad ずらす
```

## 時間の精度

`time` を、`float` で、増やし続けると、**数時間後に、精度が落ち**ます。`sin(omega × time)` の位相が、粗くなり、**波の動きが、カクカクします**。

| 経過時間 | `float` の精度（時間の刻み） |
| --- | --- |
| 1 分 | 約 0.000004 秒 |
| 1 時間 | 約 0.0002 秒 |
| 10 時間 | 約 0.002 秒（60 fps の、フレーム 1 つが 0.0167 秒なので、まだ、十分） |
| 100 時間 | 約 0.015 秒（フレーム 1 つと、同程度。動きが、粗くなる） |

位相は、`omega × time` なので、`omega` が大きい（短い波）と、**位相の誤差が、さらに増幅**されます。

**対策：時間を、周期で折り返す**。すべての波の周期の、**公倍数**で、折り返すと、継ぎ目が出ません。

```cpp
// 全ての波の周期の、最小公倍数に近い値で、折り返す。
// 周期を、きれいな値にそろえておくと、公倍数を、小さくできる。
float WrapTime(float t, float common_period) {
  return std::fmod(t, common_period);
}

// 周期を、そろえた波の作り方: ω を、基本の角周波数の整数倍にする
// ω_i = round(ω_i / ω_base) × ω_base   → 周期 2π/ω_base で、全体が一巡する。
```

波の角周波数を、**基本の角周波数の、整数倍に、丸める**と、全体の周期が、`2π / ω_base` に、収まり、その周期で、**継ぎ目なく**、折り返せます（波の速さは、わずかに、変わりますが、見た目では、気づきません）。

''', before="## よくあるミス")
pg.Refs("water/waves/animation-tricks.md", [PIERSON, FINCH, TESSENDORF, JONSWAP])

pg.Refs("water/waves/index.md", [FINCH, TESSENDORF, FOURNIER, HORVATH, KERNER])
pg.Refs("water/index.md", [TESSENDORF, FINCH, "Vlachos, \"Water Flow in Portal 2\", SIGGRAPH 2010, Advances in Real-Time Rendering in 3D Graphics and Games", KERNER])
print("ok")
