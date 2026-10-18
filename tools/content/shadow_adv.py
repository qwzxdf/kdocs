import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

DONNELLY = '''Donnelly, Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games 2006'''
LAURITZEN07 = '''Lauritzen, "Summed-Area Variance Shadow Maps", GPU Gems 3, Chapter 8, 2007'''
LAURITZEN08 = '''Lauritzen, McGuire, "Layered Variance Shadow Maps", Graphics Interface 2008（光漏れの、軽減）'''
ANNEN = '''Annen, Mertens, Seidel, Eisemann, Durand, "Exponential Shadow Maps", Graphics Interface 2008'''
PETERS = '''Peters, Klein, "Moment Shadow Mapping", Symposium on Interactive 3D Graphics and Games 2015'''
BRABEC02 = '''Brabec, Annen, Seidel, "Shadow Mapping for Hemispherical and Omnidirectional Light Sources", Advances in Modelling, Animation and Rendering (Computer Graphics International 2002)（放物面マッピング）'''
OLSSON = '''Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012'''
ENGEL = '''Engel, "Cascaded Shadow Maps", ShaderX5, 2006'''
ZHANG = '''Zhang, Sun, Zhu, "Parallel-Split Shadow Maps for Large-Scale Virtual Environments", ACM International Conference on Virtual Reality Continuum and its Applications in Industry 2006'''
DIMITROV = '''Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007'''
FERNANDO = '''Fernando, "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketches'''
REEVES = '''Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987'''
CROW = '''Crow, "Shadow Algorithms for Computer Graphics", SIGGRAPH 1977（シャドウ ボリュームの原典）'''
EVERITT = '''Everitt, Kilgard, "Practical and Robust Stenciled Shadow Volumes for Hardware-Accelerated Rendering", NVIDIA White Paper, 2002'''
WRIGHT = '''Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Unreal Engine 4 の、距離場の影）'''
QUILEZ = '''Quilez, "Soft Shadows in Raymarched SDFs", iquilezles.org（距離場のレイマーチによる、柔らかい影）'''
HART = '''Hart, "Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces", The Visual Computer, Vol. 12, 1996（距離場の、レイマーチ）'''
MCGUIRE_SSRT = '''McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014（スクリーン スペースの、レイトレース）'''
HEITZ = '''Heitz, Hill, McGuire, "Combining Analytic Direct Illumination and Stochastic Shadows", Symposium on Interactive 3D Graphics and Games 2018'''
SCHIED = '''Schied et al., "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017（SVGF）'''
FERNANDO01 = '''Fernando, Fernandez, Bala, Greenberg, "Adaptive Shadow Maps", SIGGRAPH 2001'''
LEFOHN = '''Lefohn, Sengupta, Owens, "Resolution-Matched Shadow Maps", ACM Transactions on Graphics, Vol. 26, No. 4, 2007'''
GIEGL = '''Giegl, Wimmer, "Queried Virtual Shadow Maps", Symposium on Interactive 3D Graphics and Games 2007'''
LOKOVIC = '''Lokovic, Veach, "Deep Shadow Maps", SIGGRAPH 2000（半透明の影）'''
KIM = '''Kim, Neumann, "Opacity Shadow Maps", Eurographics Workshop on Rendering 2001'''
BLINN = '''Blinn, "Me and My (Fake) Shadow", IEEE Computer Graphics and Applications, Vol. 8, No. 1, 1988'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）'''
MS_SHADOW = '''Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"'''
DXR = '''Microsoft, "DirectX Raytracing (DXR) Functional Spec"（DirectX 12 のレイトレーシング仕様）'''

# ================================================================ VSM family
pg.Dedup("shadows/vsm/index.md")
pg.Add("shadows/vsm/index.md", '''
## 通常の、シャドウ マップの、弱点

通常のシャドウ マップは、**「画素の深度」と「保存された深度」を、比較**して、**0 か 1** を、返します。この結果は、**フィルタ（ぼかし）**が、**かけられません**（**深度を、ぼかしてから**比べると、**間違った影**になる）。**PCF**は、**複数回、比較**して、平均しますが、**1 画素あたり、数十回の、読み込み**が、必要で、**重い**です。

**フィルタ可能な、シャドウ マップ**は、**深度を、ぼかして**から、**比較**できる、**表現**に、変えます。**ぼかしは、シャドウ マップに**、**1 回だけ**かけ、**シェーダーでは、1 回の、読み込み**で、**なめらかな影**が、得られます。

| 手法 | 保存するもの | ぼかしの、可否 |
| --- | --- | --- |
| 通常 | 深度 `z` | **ぼかせない**（比較結果の、平均が、必要） |
| **VSM**（Variance） | 深度の、**平均**と**2 乗の平均**（分散を、求めるため） | **ぼかせる**（ガウスぼかし、ミップ、異方性フィルタ） |
| **ESM**（Exponential） | `exp(c × z)` | **ぼかせる** |
| **EVSM** | `exp(c × z)` の、**平均と、2 乗の平均** + `exp(−c × z)` | **ぼかせる**。光漏れを、減らす |
| **MSM**（Moment） | 深度の、**4 つのモーメント**（`z`、`z²`、`z³`、`z⁴`） | **ぼかせる**。光漏れが、少ない |

## 共通の、利点

| 利点 | 内容 |
| --- | --- |
| **ぼかしを、安く** | シャドウ マップに、**ガウスぼかし**をかけるだけで、**柔らかい影**。1 画素あたり、**シェーダーで、1 回の読み込み** |
| **ミップマップ、異方性フィルタ** | **シャドウ マップに、ミップ**を、作れる。**遠くの影**の、**エイリアシング**が、減る |
| **影の、ハードウェア フィルタリング** | テクスチャの、**バイリニア**、**トライリニア**、**異方性**が、**そのまま、使える** |
| **バイアスが、小さい** | 比較は、確率的な、推定なので、**自己影が、出にくい** |

## 共通の、欠点

| 欠点 | 内容 |
| --- | --- |
| **光漏れ**（light bleeding） | **影の中**に、**明るい、斑点**が、出る。**重なる、遮蔽物**で、起きやすい（[Light Bleeding](light-bleeding.md)） |
| **メモリが、増える** | 深度 1 値ではなく、**2〜4 値**（`R32G32`、`R32G32B32A32`）を、保存する |
| **精度** | 浮動小数点の、精度が、**必要**（16 ビットでは、足りないことがある） |
| **シャドウ パスが、重い** | 深度を、**値の、変換**して、書き出す（ピクセル シェーダーが、必要） |

## 手法の、選び方

| 優先すること | 手法 |
| --- | --- |
| まず、フィルタ可能に（シンプル） | **VSM**（[VSM](#vsm)）。光漏れが、許容できる場面（遮蔽物が、単純） |
| 光漏れを、減らしたい | **EVSM**（[EVSM](evsm.md)）、**MSM**（[MSM](msm.md)） |
| 実装を、軽く（1 チャンネル） | **ESM**（[ESM](esm.md)）。遮蔽物と、受け手が、**離れている**場面（**光漏れ・影の、薄れ**が、出る） |
| PCF で、足りる | **VSM 系は、使わない**。PCF のほうが、**光漏れがなく**、**確実** |

近年は、**PCF と、ブルー ノイズ、TAA**（[PCF](../pcf.md)）、**ハードウェア レイトレーシング**で、**柔らかい影**を、得る方向に、移っています。VSM 系は、**特定の、場面**（特に、カスケードの、フィルタ、**ぼかしの、広い影**）で、**使われます**。

## VSM（分散シャドウ マップ） {#vsm}

Donnelly と Lauritzen（2006）の、**VSM**は、**シャドウ マップに、深度 `z` と、深度の 2 乗 `z²`** を、保存します。

```hlsl
// シャドウ パス: 深度と、深度の 2 乗を、書き出す（R32G32_FLOAT のレンダー ターゲット）。
float2 main(float4 pos : SV_Position) : SV_Target {
  float z = pos.z;                           // 0〜1 の深度（正射影では線形）
  float dx = ddx(z), dy = ddy(z);
  float moment2 = z * z + 0.25 * (dx * dx + dy * dy);       // 画素内の、深度の変化を、2 乗の項に加える
  return float2(z, moment2);
}
```

```hlsl
// メイン パス: ぼかした、2 つのモーメントから、チェビシェフの不等式で、光が当たる確率の、上限を求める。
float ChebyshevUpperBound(float2 moments, float t) {
  float mean = moments.x;                    // E[z]
  float variance = max(moments.y - mean * mean, 1e-5);       // E[z²] − E[z]²
  float d = t - mean;
  float p_max = variance / (variance + d * d);                // チェビシェフの不等式
  return (t <= mean) ? 1.0 : p_max;                           // 手前なら、完全に光が当たる
}

float lit = ChebyshevUpperBound(g_shadow_vsm.SampleLevel(g_linear_clamp, uv, 0).xy, depth);
```

**考え方**：シャドウ マップの、1 画素（ぼかした後は、周りの、複数の画素）に、**深度の分布**（平均 `μ` と、分散 `σ²`）が、**入っている**。**画素の深度 `t` が、`μ` より、遠い**とき、**「`t` より、手前に、遮蔽物がある確率」**の、**上限**を、**チェビシェフの不等式**で、**求めます**。

```text
P(z ≥ t) ≤ σ² / (σ² + (t − μ)²)             （t > μ のとき）
```

これが、**光が、当たる確率の、上限**で、**影の、なめらかさ**に、使います。

''', before="## よくあるミス")
pg.Refs("shadows/vsm/index.md", [DONNELLY, ANNEN, LAURITZEN08, PETERS, LAURITZEN07])

pg.Dedup("shadows/vsm/esm.md")
pg.Add("shadows/vsm/esm.md", '''
## 考え方：深度を、指数に、変える

**ESM**（Exponential Shadow Maps、Annen ら、2008）は、**深度 `z`** の代わりに、**`exp(c × z)`** を、保存します。**`c` は、大きな正の定数**（80 など）です。

通常の、影の判定は、**`t ≤ z_保存` なら、光が当たる**（1）、**そうでなければ、影**（0）、という、**階段関数**です。これを、**指数関数で、近似**します。

```text
通常:   lit = (t ≤ z) ? 1 : 0
ESM:    lit = saturate( exp(c × z) × exp(−c × t) ) = saturate( exp(c × (z − t)) )
```

| 状況 | `z − t` | `exp(c(z−t))` | 意味 |
| --- | --- | --- | --- |
| 画素が、遮蔽物より、**手前**（光が当たる） | `z − t > 0` | **1 以上**（saturate で 1） | 光が当たる |
| 画素が、遮蔽物と、**同じ**位置 | 0 | 1 | 光が当たる（境界） |
| 画素が、遮蔽物の、**奥**（影の中） | `z − t < 0` | **0 に近い**（`c` が、大きいほど、急に 0） | 影 |

`c` が、**大きい**と、**階段関数に近づき**（影の縁が、鋭い）、**小さい**と、**なめらか**ですが、**影が、薄れます**。

## フィルタの、うまみ

**`exp(c × z)`** は、**ぼかして、平均しても、正しい**性質を持ちます。**平均の `exp` は、`exp` の平均**ではありませんが、**`exp(c × z)` を、ぼかした**ものは、**「周りの、遮蔽物の、深度の、重みつき平均」**として、**意味があります**。

```hlsl
// シャドウ パス: exp(c × z) を、書き出す（R32_FLOAT のレンダー ターゲット）。
// c が大きいと、浮動小数点が、あふれる。c × z を、ある範囲に、収める（c = 40〜80、z は、0〜1）。
float main(float4 pos : SV_Position) : SV_Target {
  return exp(kExponent * pos.z);
}
```

```hlsl
// メイン パス: ぼかした exp(c × z) を読み、exp(−c × t) を掛ける。
float stored = g_shadow_esm.SampleLevel(g_linear_clamp, uv, 0);
float lit = saturate(stored * exp(-kExponent * depth));
```

`exp(c × z)` は、**非常に大きい値**になります（`c = 80`、`z = 1` で、`e⁸⁰ ≈ 5×10³⁴`）。**32 ビット浮動小数点の、上限**（約 3.4×10³⁸）に、**近い**ので、`c` を、**大きくしすぎない**。**logarithmic ブラー**（`log(exp(a) + exp(b))` の形で、ぼかす）という、**あふれない、ぼかし方**も、あります。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **1 チャンネル**（メモリが、小さい）。**VSM より、光漏れが、起きにくい**（分散を、使わないので） |
| 長所 | 実装が、**簡単**。ぼかしも、**ミップも、使える** |
| 短所 | **影が、薄くなる**（遮蔽物から、**離れた所**で、影が、薄れる）。`exp(c(z−t))` は、**差が、大きいほど、0 に近づく**ので、**遠くの影は、濃い**が、**近くの影は、薄い**（逆の性質） |
| 短所 | **`c` の、調整が、必要**（大きすぎる→あふれる、小さすぎる→影が、薄い） |
| 短所 | **深度の、範囲**に、依存する（正規化した、深度の、範囲が、広いと、精度が、足りない） |

### 影が、薄れる、問題

**遮蔽物の、すぐ近く**（同じ面の、少し奥）では、`z − t` が、**小さい**ので、`exp(c(z − t))` は、**1 に近く**、**影が、薄い**（光が、当たると、判定）。遮蔽物から、**十分に、離れた**所（`z − t` が、大きい負）で、**初めて、濃い影**になります。**接地部分の、影が、薄くなる**ので、**足元が、浮いて**見える（[Peter Panning](../bias/peter-panning.md) に、似た見え方）。

| 対策 | 内容 |
| --- | --- |
| `c` を、**大きく** | 影が、濃くなるが、あふれる危険 |
| **EVSM** に、する | 2 つの、指数（正と負）で、影を、補強（[EVSM](evsm.md)） |

''', before="## よくあるミス")
pg.Refs("shadows/vsm/esm.md", [ANNEN, DONNELLY, "Salvi, \"Rendering Filtered Shadows with Exponential Shadow Maps\", ShaderX6, 2008", RTR])

pg.Dedup("shadows/vsm/evsm.md")
pg.Add("shadows/vsm/evsm.md", '''
## 考え方：VSM と ESM の、いいとこ取り

**EVSM**（Exponential Variance Shadow Maps）は、**VSM の分散**（チェビシェフの不等式）と、**ESM の指数**を、**組み合わせた**手法です。深度 `z` を、**指数に変換**してから、その**平均と 2 乗の平均**（分散）を、保存し、チェビシェフの不等式で、**判定**します。

```text
VSM:   z、z² を、保存
ESM:   exp(c × z) を、保存
EVSM:  warp(z) = exp(c × z)   →   warp(z) と warp(z)² を、保存し、チェビシェフで判定
```

**指数変換**で、深度の差を、**増幅**するため、**光漏れ**（VSM の、最大の、弱点）が、**大きく減ります**。

## 2 つの、指数（正と負）

EVSM は、**2 つの方向の指数**（`+c` と `−c`）を、使います。

| 指数 | 変換 | 役割 |
| --- | --- | --- |
| **正**の指数 | `exp(+c × z)` | 遮蔽物の**奥**（遠く）に、**影を落とす**。通常の、判定を、担当 |
| **負**の指数 | `−exp(−c × z)` | **反対向き**の、光漏れを、抑える。**2 つの判定の、小さい方**を、採用する |

```hlsl
// シャドウ パス: 4 チャンネル（正の指数の、1 次と 2 次、負の指数の、1 次と 2 次）を、書き出す。
float2 WarpDepth(float z, float2 exponents) {
  // exponents.x = c+、exponents.y = c−
  float pos = exp(exponents.x * z);
  float neg = -exp(-exponents.y * z);
  return float2(pos, neg);
}

float4 main(float4 pos_in : SV_Position) : SV_Target {
  float2 warped = WarpDepth(pos_in.z, g_exponents);
  // 4 チャンネル: (pos, pos², neg, neg²)
  return float4(warped.x, warped.x * warped.x, warped.y, warped.y * warped.y);
}
```

```hlsl
// メイン パス: 正と負の、それぞれで、チェビシェフの判定をして、小さい方（暗い方）を採用する。
float ChebyshevUpperBound(float2 moments, float t, float min_variance) {
  float variance = max(moments.y - moments.x * moments.x, min_variance);
  float d = t - moments.x;
  float p_max = variance / (variance + d * d);
  return (t <= moments.x) ? 1.0 : p_max;
}

float EvsmShadow(float4 moments, float depth) {
  float2 warped = WarpDepth(depth, g_exponents);
  float pos_lit = ChebyshevUpperBound(moments.xy, warped.x, g_min_variance_pos);
  float neg_lit = ChebyshevUpperBound(moments.zw, warped.y, g_min_variance_neg);
  return min(pos_lit, neg_lit);                      // どちらかが影なら影
}
```

## 精度の、問題

指数関数は、**非常に大きい値**になります。精度に、注意が必要です。

| 形式 | 指数の上限（`exp(c × z)` の、あふれない `c`） |
| --- | --- |
| 16 ビット浮動小数点（`R16G16B16A16_FLOAT`） | `c ≈ 5`（`e⁵ ≈ 148`、**16 ビットの上限は 65504**） |
| 32 ビット浮動小数点（`R32G32B32A32_FLOAT`） | `c ≈ 40`（`e⁴⁰ ≈ 2×10¹⁷`、2 乗しても、収まる）|

**16 ビット**では、`c` を、小さくせざるを得ず、**光漏れの、削減効果が、減ります**。**32 ビット**（メモリが、2 倍）が、**標準**です。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **光漏れが、VSM より、大きく減る** |
| 長所 | **ぼかし、ミップ、異方性**が、使える |
| 長所 | **バイアスが、ほぼ、不要**（確率的に、判定するため） |
| 短所 | **メモリ**：4 チャンネル × 32 ビット = **16 バイト / 画素**（通常の、深度の、4 倍） |
| 短所 | **指数の、調整**（`c` の、値）。**深度の範囲に、依存** |
| 短所 | **光漏れは、ゼロにならない**（重なる、遮蔽物では、残る） |
| 短所 | シャドウ パスが、**ピクセル シェーダー付き**（指数の、計算） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **ぼかしを、広くかけたい**（柔らかい影） | **有効**。ガウスぼかしを、シャドウ マップに、1 回かけるだけ |
| **カスケードの、**遠い**側**（広い範囲を、覆う、粗い、シャドウ マップ） | **有効**。ミップ、フィルタで、**エイリアシングを、減らせる** |
| **接触部分の、正確さ**が、必要 | PCF や、レイトレーシングの、ほうが、確実 |

''', before="## よくあるミス")
pg.Refs("shadows/vsm/evsm.md", [LAURITZEN08, ANNEN, DONNELLY, PETERS])

pg.Dedup("shadows/vsm/msm.md")
pg.Add("shadows/vsm/msm.md", '''
## 考え方：モーメントを、4 つ、持つ

**MSM**（Moment Shadow Mapping、Peters と Klein、2015）は、**深度の、モーメント**を、**4 つ**（`z`、`z²`、`z³`、`z⁴`）保存します。VSM は、**2 つ**（`z`、`z²`、つまり、平均と分散）でした。**モーメントが、多い**ほど、**深度の分布**を、**詳細に**、表せます。

| 手法 | 保存するモーメント | 表せる、分布 |
| --- | --- | --- |
| VSM | `z`、`z²`（2 つ） | 平均と、分散だけ。**1 つの、山**のような分布 |
| **MSM（4 モーメント）** | `z`、`z²`、`z³`、`z⁴` | **2 つの、遮蔽物**（2 層）を、区別できる |

**光漏れ**は、**複数の遮蔽物が、重なる**とき（シャドウ マップの、1 画素に、**2 つの、深度**が、混ざる）に、起きます。VSM は、2 つの深度を、**1 つの、平均と分散**に、潰してしまい、**両者の間の、隙間**に、**光漏れ**が、出ます。MSM は、**2 つの、深度を、区別**できるので、**光漏れが、少ない**です。

## 影の、判定

保存した、4 つの、モーメントから、**「画素の深度 `t` より、手前に、遮蔽物が、ある確率」の、下限**（影の、**最も、厳しい**見積もり）を、**数値的に**、**計算**します。VSM の、チェビシェフの不等式の、**一般化**に、あたります。

```hlsl
// 4 モーメントから、影の判定（Hamburger 4MSM。論文の、方法）。概略。
float ComputeMsmShadowIntensity(float4 moments, float depth, float depth_bias, float moment_bias) {
  // ① モーメントに、わずかな、バイアスを、混ぜて、数値的に、安定させる
  float4 b = lerp(moments, float4(0.5, 0.5, 0.5, 0.5), moment_bias);

  // ② 3×3 の、連立方程式（コレスキー分解）を、解いて、2 つの、遮蔽する深度（z2、z3）を、推定する
  float3 z;
  z[0] = depth - depth_bias;
  float L32D22 = mad(-b[0], b[1], b[2]);
  float D22 = mad(-b[0], b[0], b[1]);
  float squared_depth_variance = mad(-b[1], b[1], b[3]);
  float D33D22 = dot(float2(squared_depth_variance, -L32D22), float2(D22, L32D22));
  float inv_D22 = 1.0 / D22;
  float L32 = L32D22 * inv_D22;
  float3 c = float3(1.0, z[0], z[0] * z[0]);
  c[1] -= b.x;
  c[2] -= b.y + L32 * c[1];
  c[1] *= inv_D22;
  c[2] *= D22 / D33D22;
  c[1] -= L32 * c[2];
  c[0] -= dot(c.yz, b.xy);
  float p = c[1] / c[2];
  float q = c[0] / c[2];
  float D = (p * p * 0.25) - q;
  float r = sqrt(D);
  z[1] = -p * 0.5 - r;
  z[2] = -p * 0.5 + r;

  // ③ 得られた 2 つの深度（z[1]、z[2]）と、画素の深度 z[0] の、順序から、影の強さを、決める
  float4 switch_val = (z[2] < z[0]) ? float4(z[1], z[0], 1.0, 1.0)
                    : ((z[1] < z[0]) ? float4(z[0], z[1], 0.0, 1.0) : float4(0.0, 0.0, 0.0, 0.0));
  float quotient = (switch_val[0] * z[2] - b[0] * (switch_val[0] + z[2]) + b[1])
                 / ((z[2] - switch_val[1]) * (z[0] - z[1]));
  float shadow_intensity = switch_val[2] + switch_val[3] * quotient;
  return saturate(shadow_intensity);        // 1 = 完全に影、0 = 光が当たる
}
```

上のコードは、**論文の、アルゴリズムの、骨格**です。**数値的に、安定させる**ために、**バイアスや、コレスキー分解の、細かい手順**が、必要です。**実際の実装**では、**論文の、公開コード**を、参照して、**そのまま、移植**する方法が、確実です。

## 保存と、書き出し

4 つの、モーメントを、**最適な、形式**に、**変換**して、保存します（論文は、**量子化**によって、**16 ビット × 4** に、収める、**変換**も、提案）。

```hlsl
// シャドウ パス: 深度の 4 つのモーメントを、書き出す（R32G32B32A32_FLOAT、または、R16G16B16A16_UNORM + 最適化変換）。
float4 main(float4 pos : SV_Position) : SV_Target {
  float z = pos.z;
  float z2 = z * z;
  return float4(z, z2, z2 * z, z2 * z2);
}
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **光漏れが、少ない**（EVSM より、さらに、少ない場面が、多い） |
| 長所 | **ぼかし、ミップ、異方性フィルタ**が、使える |
| 長所 | **指数を、使わない**ので、**浮動小数点の、あふれ**の問題が、**ない** |
| 短所 | **4 チャンネル**（メモリが、通常の 4 倍。16 ビットに、量子化すれば、2 倍） |
| 短所 | **判定の、計算が、重い**（連立方程式を、解く） |
| 短所 | **数値的な、不安定さ**（バイアスの、調整が、必要。浮動小数点の、精度に、敏感） |
| 短所 | **実装が、複雑**（論文の、コードを、参考にしないと、難しい） |

## VSM 系の、手法の、比較

| 手法 | チャンネル | 光漏れ | 判定の、コスト | 実装 |
| --- | --- | --- | --- | --- |
| VSM | 2 | **大きい** | 小 | 簡単 |
| ESM | 1 | 影が、薄れる | 小 | 簡単 |
| EVSM | 4（32 ビット） | **小さい** | 中 | 中 |
| **MSM** | 4 | **最も小さい** | **大** | **複雑** |

''', before="## よくあるミス")
pg.Refs("shadows/vsm/msm.md", [PETERS, DONNELLY, LAURITZEN08, "Peters, Klein, \"Moment Shadow Mapping\" の公開コードと、補足資料（論文の Web ページ）"])

pg.Dedup("shadows/vsm/light-bleeding.md")
pg.Add("shadows/vsm/light-bleeding.md", '''
## 光漏れとは

**VSM**（分散シャドウ マップ）で、**影の中**に、**明るい斑点や、ぼんやりした光**が、出る現象です。**複数の遮蔽物が、重なる**場所で、起きやすいです。

```text
          光
          ↓
   ┌──────┐ 遮蔽物 A（深度 0.3）
   └──────┘
       ┌──────┐ 遮蔽物 B（深度 0.6）
       └──────┘
 ━━━━━━━━━━━━━━ 受け手（深度 0.9）

 受け手の、画素の位置では、A も B も遮蔽している（完全に、影のはず）。
 ところが、VSM は、「A の深度と B の深度の、平均と分散」しか持たず、
 A と B の「間」に、光が通る隙間があるように、見積もってしまう → 影が、薄くなる（光漏れ）
```

## 原因

VSM は、**シャドウ マップの、1 画素（ぼかした後は、周囲の、複数の画素）**に、**深度の、分布**を、**平均と分散**の、**2 つの数**で、**要約**して、保存します。**2 つの、離れた深度**（A と B）を、**1 つの、平均と、大きな分散**に、**潰す**ので、**画素の深度 `t`** が、A と B の、**どちらよりも、奥**にあっても、**分散が大きいため**、**チェビシェフの不等式**が、**「光が当たる確率の、上限」**として、**大きな値**を、返します。

| 状況 | VSM の見積もり | 実際 |
| --- | --- | --- |
| 遮蔽物 1 つ（単純） | 正しい | 正しい |
| 遮蔽物が、**2 つ、重なる**（深度が、離れている） | **光が、漏れる**（上限が、大きく出る） | 完全に影 |
| 遮蔽物の、**縁**の、ぼかし | 縁が、わずかに、明るい | — |

**チェビシェフの不等式**は、**上限**を、与える（**確率が、これ以下**）ので、**最悪の場合**を、**見積もる**。**影は、薄い方へ、ずれ**ます。

## 対策

### ① 光漏れの、削減（クランプ）

**得られた確率**を、**ある値以下を、0 に切り、残りを、再スケール**します。**薄い光漏れが、消えます**。

```hlsl
// 光漏れの、削減: 確率 p が、amount 以下なら 0 にし、残りを 0〜1 に、引き伸ばす。
float ReduceLightBleeding(float p_max, float amount) {
  return saturate((p_max - amount) / (1.0 - amount));
}

float lit = ChebyshevUpperBound(moments, depth);
lit = ReduceLightBleeding(lit, 0.3);       // 0.2〜0.5。大きいほど、光漏れが、減るが、影の縁が、鋭くなる
```

| `amount` | 効果 |
| --- | --- |
| 0 | 削減なし（元の、VSM） |
| 0.2〜0.3 | **光漏れが、かなり、減る**。影の縁は、ほぼ、なめらか |
| 0.5 | **光漏れは、ほぼ、消える**。縁が、鋭く、**ぼかしの、効果が、弱まる** |

**簡単**で、**ほぼ、全員が、使う**対策です。**縁が、硬くなる**（ぼかしを、狭める）、**トレード オフ**があります。

### ② 指数を、使う（EVSM）

**深度を、指数に、変換**して、**深度の差を、増幅**します。**遮蔽物 A と B の、深度の差**が、**大きく**広がり、**分布の、潰れ方が、小さく**なります（[EVSM](evsm.md)）。

### ③ モーメントを、増やす（MSM）

**4 つの、モーメント**で、**2 つの、遮蔽物を、区別**します（[MSM](msm.md)）。**光漏れが、原理的に、少ない**。

### ④ 層に、分ける（Layered VSM）

**深度の範囲を、複数の層に、分け**、**層ごとに、別の、シャドウ マップ**を、作ります（Lauritzen と McGuire、2008）。**各層の中**では、**遮蔽物が、1 つ**なので、**光漏れが、出ません**。**層の数だけ、メモリと、コスト**が、増えます。

| 方式 | 光漏れ | コスト |
| --- | --- | --- |
| 削減（クランプ） | 減る（縁が、鋭くなる） | **なし** |
| EVSM | **かなり、減る** | メモリ 2 倍、少し重い |
| MSM | **最も、少ない** | メモリ 2 倍、判定が、重い |
| Layered VSM | 減る | **層の数**に、比例 |

### ⑤ 配置を、工夫する

| 工夫 | 内容 |
| --- | --- |
| 遮蔽物の、**重なりを、減らす** | 光の方向から見て、**複数の物が、重ならない**ように、シーンを、設計（難しい） |
| 光漏れが、**目立たない**場所だけ、**使う** | 遠景の、カスケード（遠くの、影は、細部が、見えない） |
| **PCF と、併用** | 近景は、PCF（光漏れなし）、遠景は、VSM 系（ぼかしが、安い）と、**使い分ける** |

## 光漏れを、見つけるには

| 方法 | 内容 |
| --- | --- |
| **重なる**遮蔽物の、場面を、用意 | 複数の、板を、重ねて、その下に、受け手を置く |
| 影の、**真ん中**を見る | 影の中央に、**明るい斑点**が、無いか（VSM の、光漏れの、典型的な、出方） |

''', before="## よくあるミス")
pg.Refs("shadows/vsm/light-bleeding.md", [DONNELLY, LAURITZEN08, ANNEN, PETERS])

pg.Dedup("shadows/vsm/comparison.md")
pg.Add("shadows/vsm/comparison.md", '''
## PCF と、VSM 系の、違い

| 観点 | **PCF**（比較サンプラー + 複数回） | **VSM 系**（VSM、ESM、EVSM、MSM） |
| --- | --- | --- |
| 保存するもの | **深度**（1 チャンネル） | モーメント（**2〜4 チャンネル**） |
| 縁の、なめらかさ | **複数回、読み込む**（3×3 で 9 回、5×5 で 25 回）。**サンプルが、増えるほど**、重い | **シャドウ マップを、ぼかして**、1 回読む。**ぼかしの、大きさは、自由** |
| 読み込み（画素あたり） | 数回〜数十回 | **1 回** |
| 広い、ぼかし | **重い**（サンプルが、半径の 2 乗で、増える） | **安い**（ぼかしの、半径を、変えても、シェーダーは、同じ） |
| ミップ・異方性 | 使えない（深度の、ミップは、意味がない） | **使える**（遠くの影の、エイリアシングを、減らせる） |
| **光漏れ** | **ない** | **ある**（VSM、ESM）。EVSM、MSM で、軽減 |
| バイアス | **必要**（自己影を、防ぐ） | **小さくて、よい**（確率的な、判定） |
| メモリ | **小さい** | 2〜4 倍 |
| シャドウ パス | **深度のみ**（ピクセル シェーダー不要。**速い**） | **ピクセル シェーダーが、必要**（モーメントを、計算） |
| 実装 | **簡単** | **やや複雑**（ぼかしパス、光漏れ対策） |

## 速さの、違い（目安）

| 手法 | シャドウ パス | ぼかし | メイン パスの、読み込み |
| --- | --- | --- | --- |
| PCF 3×3（ハードウェア 2×2 × 9 = 実質 4 サンプル） | **最速** | 不要 | 4〜9 回 |
| PCF 5×5 | 最速 | 不要 | 25 回 |
| VSM（`R32G32`） | 少し重い | **ガウスぼかし**（シャドウ マップ全体で、1 回） | **1 回** |
| EVSM（`R32G32B32A32`） | 重い | ガウスぼかし（4 チャンネル） | 1 回 |
| MSM | 重い | ガウスぼかし | 1 回 + 判定の計算 |

PCF は、**画素ごとの、サンプル数**が、コストの、大部分を占めます。VSM 系は、**シャドウ マップの、ぼかし**（解像度ぶん）が、コストの、大部分で、**画素ごとのコストは、一定**です。

## どちらを、選ぶか

| 状況 | おすすめ |
| --- | --- |
| **標準的な、ゲーム**（太陽 + 数個のライト） | **PCF**（3×3〜5×5）。シンプルで、安定。**まず、これ** |
| **広い、ぼかしの、影**（柔らかい影、PCSS 風） | PCF だと、**非常に、重い**。VSM 系が、**有利**（ただし、光漏れの、対策が、必要） |
| **遠景の、カスケード**（粗い、シャドウ マップ） | **VSM 系 + ミップ**で、エイリアシングを、減らす |
| **光漏れが、許せない**（重なる物が、多い、細かい構造） | **PCF** |
| メモリが、厳しい | PCF（1 チャンネル） |

## 近年の、傾向

| 傾向 | 内容 |
| --- | --- |
| **PCF + ブルー ノイズ + TAA** | **少ないサンプル**（4〜8）を、**画素ごとに、ずらして**、**時間方向に、平均**。**光漏れなし**で、**ぼかしも、柔軟** |
| **ハードウェア レイトレーシング** | **ソフトな影**を、**正確に**（[Ray-Traced Shadows](../ray-traced.md)） |
| **VSM 系の、使いどころは、狭まった** | 光漏れの、対策が、複雑。**PCF + TAA** で、品質が、十分に、得られるため |

''', before="## よくあるミス")
pg.Refs("shadows/vsm/comparison.md", [DONNELLY, REEVES, ANNEN, PETERS, LAURITZEN08])

# ================================================================ local lights
pg.Dedup("shadows/local-lights/index.md")
pg.Add("shadows/local-lights/index.md", '''
## 点光源・スポットライトの、影の、特徴

**太陽**は、**平行光源**で、**1 枚の、正射影シャドウ マップ**で、足ります。**点光源**（電球、たいまつ）と、**スポットライト**（懐中電灯、街灯）は、**位置を持ち**、**光が、広がります**。そのため、**影の作り方が、違います**。

| 光 | 光の広がり | シャドウ マップ | ページ |
| --- | --- | --- | --- |
| **スポットライト** | **円錐**（片側に、向かう） | **透視投影の、1 枚** | [Spot Lights](spot-light.md) |
| **点光源** | **全方向**（球） | **キューブマップ（6 枚）**、または、**放物面マップ（2 枚）** | [Point Lights: Cube Maps](point-cubemap.md)、[Dual Paraboloid](dual-paraboloid.md) |
| **多数の光** | — | **コスト管理が、必須** | [Shadows for Many Lights](many-lights.md) |

## 光の数と、コスト

影を、落とす光が、1 つ増えるごとに、**シーンを、もう一度、描く**必要があります。

| 光 | シャドウ パスの、描画回数 |
| --- | --- |
| 太陽（CSM、4 カスケード） | 4（カスケードごと） |
| スポットライト 1 つ | **1** |
| 点光源 1 つ（キューブマップ） | **6**（各面） |
| 点光源 1 つ（放物面） | 2 |

**点光源 10 個**（キューブマップ）で、**60 回**の、シーンの、描画に、**なります**。**影を落とす光の数を、制限**し、**範囲外の光の影は、省き**、**更新を、間引く**、といった、**管理**が、不可欠です（[Shadows for Many Lights](many-lights.md)）。

## 実装の、共通点

| 項目 | 内容 |
| --- | --- |
| 射影 | **透視投影**（深度が、**非線形**）。**バイアスは、距離で、変わる** |
| 光の、範囲 | **光の、到達距離**（range）。**ファー面 = range**。範囲外は、**描かない** |
| 深度の形式 | **距離（光からの、実際の距離）**を、保存する方法もある（透視投影の、非線形性を、避ける） |
| カリング | **光の、範囲球**と、物の、バウンディングで、**範囲外の物**を、**シャドウ パスから、外す** |

### 距離を、保存する

**透視投影**の、深度は、**非線形**で、**バイアスが、距離で、変わり**、扱いにくいです。**光からの、実際の距離**を、**ピクセル シェーダー**で、計算して、**保存**する方法です。

```hlsl
// 点光源のシャドウ パス: 光からの距離（0〜1 に、正規化）を、書き出す。
float main(PSInput input) : SV_Target {
  float dist = length(input.world_position - g_light_position);
  return dist / g_light_range;                    // 0〜1
}

// メイン パス: 同じ式で、画素の距離を求めて、保存された距離と、比べる。
float3 to_pixel = world_pos - g_light_position;
float dist = length(to_pixel) / g_light_range;
float stored = g_shadow_cube.SampleLevel(g_linear_clamp, to_pixel, 0);      // 方向ベクトルで、キューブを読む
float lit = (dist - kBias <= stored) ? 1.0 : 0.0;
```

距離を、保存すると、**バイアスが、距離に、依存せず、線形**になり、**扱いやすい**。ただし、**ピクセル シェーダー**が、必要で、**ハードウェアの、深度比較**（比較サンプラー、PCF）が、**使えません**。

''', before="## よくあるミス")
pg.Refs("shadows/local-lights/index.md", [BRABEC02, OLSSON, RTR, MS_SHADOW])

pg.Dedup("shadows/local-lights/spot-light.md")
pg.Add("shadows/local-lights/spot-light.md", '''
## スポットライトの、影は、1 枚

スポットライトは、**円錐状**に、光を出すので、**透視投影の、シャドウ マップ 1 枚**で、**影を、作れます**。**光の位置**に、カメラを置き、**円錐の、向き**を、見て、**円錐の、開き角**を、**視野角**にします。

```cpp
using namespace DirectX::SimpleMath;

// スポットライトの、光の行列（右手系、行ベクトル）。
Matrix SpotLightMatrix(const SpotLight& spot) {
  Vector3 position = spot.position;
  Vector3 target = spot.position + spot.direction;
  // 上方向は、光の向きと、平行にならない軸を選ぶ。
  Vector3 up = (std::abs(spot.direction.y) > 0.99f) ? Vector3::UnitZ : Vector3::UnitY;
  Matrix view = Matrix::CreateLookAt(position, target, up);

  // 視野角 = 外側の円錐の全角。170° を超えない（透視投影が破綻する）。
  float fov = std::min(2.0f * spot.outer_angle, DirectX::XMConvertToRadians(170.0f));
  Matrix proj = Matrix::CreatePerspectiveFieldOfView(fov, 1.0f, spot.near_z, spot.range);
  return view * proj;
}
```

| パラメーター | 目安 | 内容 |
| --- | --- | --- |
| `fov` | `2 × 外側の円錐の半角` | 円錐が、ちょうど、シャドウ マップに、収まる |
| `near_z` | 0.1〜1 m | **できるだけ、大きく**（深度の精度を、守る） |
| `range` | 光の、到達距離 | これを超えた所は、光が、当たらない。**ファー面** |

## 深度の、精度とバイアス

**透視投影**では、深度が、**非線形**です。**近くで、精度が、高く**、**遠くで、粗い**。**同じバイアスでも、距離によって、ワールドでの、大きさが違う**ので、**調整が、難しい**です。

| 対策 | 内容 |
| --- | --- |
| `near_z` を、大きく | ニア面を、**可能な限り、遠く**に。精度の、無駄が、減る |
| **線形深度**で、比べる | シャドウ パスで、**距離（線形）**を、書き込み、比較する（上の、[Point and Spot Light Shadows](index.md) の、距離の保存） |
| **法線オフセット** | 深度を、いじらず、**位置を**ずらす。**距離に応じて、ずらす量を、スケール**（[Normal Offset](../bias/normal-offset.md)） |
| **ハードウェアの、傾き依存バイアス** | `SlopeScaledDepthBias`（[Slope-Scale Bias](../bias/slope-scale-bias.md)） |

```hlsl
// 透視投影の、シャドウ マップの、画素の、ワールドでの、大きさ（距離に比例）を、法線オフセットに使う。
float texel_world = 2.0 * distance_to_light * tan(0.5 * fov) / shadow_resolution;
float3 offset = world_normal * (sin_theta * texel_world * 2.0);
```

## スポット ライトの、影の、判定

```hlsl
float SpotShadow(float3 world_pos, float3 world_normal) {
  // 法線オフセット（上記）
  float3 p = world_pos + world_normal * normal_offset;
  float4 light_clip = mul(float4(p, 1.0), g_spot_view_proj);
  // 透視投影なので、w で割る（正射影と違う）
  float3 ndc = light_clip.xyz / light_clip.w;
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;

  // 光の後ろ側（w が負）は、影の判定をしない（光が当たらない）
  if (light_clip.w <= 0.0) return 1.0;
  if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;                // 円錐の外
  return g_spot_shadow.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z);
}
```

**`w` で割る**ことを、**忘れない**（太陽の、正射影では、`w = 1`）。**光の後ろ側**（`w ≤ 0`）の画素は、**円錐の外**なので、**そもそも、光が、当たらない**。

## 効率

| 工夫 | 内容 |
| --- | --- |
| **円錐に、収まる物だけを、描く** | 光の、**視錐台**で、物を、**カリング** |
| **解像度を、光の、画面上の大きさに、合わせる** | **画面で、小さい光**は、**シャドウ マップも、小さく**（512×512 など）。大きな光は、大きく（2048×2048） |
| **更新を、間引く** | **静止した光 + 静止した物**なら、**一度作って、保存**（キャッシュ）。**動く物だけ**を、毎フレーム、足す（[Shadows for Many Lights](many-lights.md)） |
| **光の、範囲外**では、**影を、省く** | 画面に、映らない、光の影は、**描かない** |

## 複数の、スポットライト

**複数の、スポットライトの、シャドウ マップ**は、**1 枚の、大きなテクスチャ（アトラス）**に、**並べる**、または、**テクスチャ配列**に、まとめます。

| 方法 | 内容 |
| --- | --- |
| **アトラス** | 1 枚の、大きなテクスチャに、各ライトの、シャドウ マップを、**タイルとして**配置。**1 つのテクスチャ**を、シェーダーに、渡せる。**ライトごとに、UV の、変換**が、必要 |
| **テクスチャ配列** | `Texture2DArray`。**スライス番号**で、ライトを、選ぶ。**同じ解像度**が、必要 |

''', before="## よくあるミス")
pg.Refs("shadows/local-lights/spot-light.md", [WILLIAMS := '''Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978''', MS_SHADOW, OLSSON, RTR])

pg.Dedup("shadows/local-lights/point-cubemap.md")
pg.Add("shadows/local-lights/point-cubemap.md", '''
## キューブマップで、全方向を、覆う

点光源の、光は、**全方向**に、広がります。全方向の、影を、**1 枚の透視投影**では、作れません。**6 つの面**（+X、−X、+Y、−Y、+Z、−Z）、それぞれを、**視野角 90° の、透視投影**で、描き、**キューブマップ**に、保存します。**画素の、光からの方向**で、**どの面を、読むか**が、決まります。

```text
        +Y
         │
   −X ───┼─── +X       （キューブマップの、6 面）
        ╱│
      +Z  −Y                  光を、中心とした、立方体の 6 面に、深度を、保存
```

## DirectX 11 で、キューブマップを、作る

6 つの面を、**テクスチャ配列**（6 スライス）として、作り、**キューブとして、読む**ように、ビューを、設定します。

```cpp
// 点光源のシャドウ キューブマップ（1024×1024 × 6 面）。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 1024;
desc.Height = 1024;
desc.MipLevels = 1;
desc.ArraySize = 6;                                         // 6 面
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
desc.MiscFlags = D3D11_RESOURCE_MISC_TEXTURECUBE;           // キューブとして、使える
device->CreateTexture2D(&desc, nullptr, &shadow_cube_tex);

// 各面に書き込む DSV（6 つ）。
for (UINT face = 0; face < 6; ++face) {
  D3D11_DEPTH_STENCIL_VIEW_DESC dsv = {};
  dsv.Format = DXGI_FORMAT_D32_FLOAT;
  dsv.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2DARRAY;
  dsv.Texture2DArray.FirstArraySlice = face;
  dsv.Texture2DArray.ArraySize = 1;
  device->CreateDepthStencilView(shadow_cube_tex.Get(), &dsv, &face_dsv[face]);
}

// 読み取り用: キューブとして。
D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R32_FLOAT;
srv.ViewDimension = D3D11_SRV_DIMENSION_TEXTURECUBE;
srv.TextureCube.MipLevels = 1;
device->CreateShaderResourceView(shadow_cube_tex.Get(), &srv, &shadow_cube_srv);
```

## 6 面の、行列

各面の、**向き**（前、上方向）を、**決まりに従って**、決めます。**視野角は、90°**、**アスペクト比 1**。

```cpp
using namespace DirectX::SimpleMath;

// キューブの 6 面の、向きと、上方向。+X, −X, +Y, −Y, +Z, −Z の順（DirectX の、キューブの面の順）。
const Vector3 kForward[6] = {{1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};
const Vector3 kUp[6] =      {{0, 1, 0}, {0, 1, 0}, {0, 0, -1}, {0, 0, 1}, {0, 1, 0}, {0, 1, 0}};

for (int face = 0; face < 6; ++face) {
  Matrix view = Matrix::CreateLookAt(light.position, light.position + kForward[face], kUp[face]);
  Matrix proj = Matrix::CreatePerspectiveFieldOfView(DirectX::XM_PIDIV2, 1.0f, near_z, light.range);
  face_view_proj[face] = view * proj;
}
```

!!! warning "面の、向きと、上方向は、DirectX の、キューブの規約に、合わせる"
    キューブマップの、各面の、**上方向と、左右**は、**規約**で、決まっています。**間違えると**、**面が、回転、反転**して、**影が、ずれたり、つぎはぎ**になります。**シェーダーの、キューブの読み方**（方向ベクトル）と、**シャドウ パスの、行列**を、**合わせる**。**書き込みと、読み込みで、同じ規約**を、使うことが、肝心です。

## 6 面を、描く

```cpp
// 6 面のそれぞれに、深度を描く。各面ごとに、光の行列を、変える。
for (int face = 0; face < 6; ++face) {
  context->OMSetRenderTargets(0, nullptr, face_dsv[face].Get());
  context->ClearDepthStencilView(face_dsv[face].Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
  UpdateLightCB(face_view_proj[face]);
  DrawShadowCasters(face);                   // この面の視錐台に入る物だけ（面ごとに、カリング）
}
```

**面ごとの、視錐台カリング**が、重要です。**ある面の、視錐台に入らない物**は、その面で、**描かない**。**全部の物を、6 回描く**と、**重い**です。

## シェーダーで、読む

**画素の、光からの方向ベクトル**で、キューブマップを、読みます。**どの面を、読むか**は、**ハードウェアが、方向の、最大の成分**から、**自動で**、決めます。

```hlsl
TextureCube<float> g_shadow_cube : register(t6);
SamplerComparisonState g_shadow_sampler : register(s5);

float PointShadow(float3 world_pos, float3 world_normal) {
  float3 to_pixel = world_pos - g_light_position;               // 光から、画素へ向かう、方向
  // 法線オフセット（距離に応じて）
  float dist = length(to_pixel);
  float3 offset = world_normal * normal_offset;
  float3 dir = to_pixel + offset;

  // この方向で、どの面か、ハードウェアが、決めて、その面の、深度を読む。
  // 比較に使う深度は、その面の、射影で変換した値。面ごとに、射影を適用する必要がある。
  float3 abs_dir = abs(dir);
  float major = max(abs_dir.x, max(abs_dir.y, abs_dir.z));        // 最大の成分（奥行き方向の距離）
  // 透視投影の、深度（非線形）を、再現する: z' = (f / (f − n)) × (1 − n / major)
  float depth = (g_far / (g_far - g_near)) * (1.0 - g_near / major);
  return g_shadow_cube.SampleCmpLevelZero(g_shadow_sampler, dir, depth);
}
```

**深度の、再現**が、ポイントです。シャドウ パスで、書かれた、深度は、**面の透視投影**で、変換された値で、**その面での、奥行き成分**（`dir` の、最大成分）で、決まります。**メイン パスでも、同じ変換**を、**再現**して、比べる必要があります。

**距離を、直接、保存**する方法（[Point and Spot Light Shadows](index.md)）なら、**この変換**は、**不要**になります。

## 面の、継ぎ目

キューブの、**面の境界**で、PCF などの、フィルタが、**隣の面**の、情報を、**読めない**ことがあります。**境界で、影が、途切れる**、**線が出る**ことがあります。

| 対策 | 内容 |
| --- | --- |
| **視野角を、少し、広げる**（90° → 91°〜92°） | 各面が、**隣の面と、少し、重なる**。境界の、フィルタが、**自分の面の、内側**で、完結する |
| キューブマップの、**ハードウェア フィルタ** | `TextureCube` の、サンプラーは、**面の境界を、またいで**、補間する（シームレス キューブマップ。DirectX 11 では、標準） |

## 解像度と、コスト

| 解像度 | メモリ（`D32_FLOAT`、6 面） | 用途 |
| --- | --- | --- |
| 512×512 | 6 MB | 小さい光、遠くの光 |
| 1024×1024 | 24 MB | 標準 |
| 2048×2048 | 96 MB | 主要な光（高品質） |

**1 つの、点光源**で、**6 面**を、描き、メモリも、大きいので、**影を、落とす点光源の数は、限る**（**画面の、近くの、重要な、光だけ**）。

''', before="## よくあるミス")
pg.Refs("shadows/local-lights/point-cubemap.md", [BRABEC02, OLSSON, MS_SHADOW, "Microsoft Learn, \"D3D11_RESOURCE_MISC_FLAG\"（`D3D11_RESOURCE_MISC_TEXTURECUBE`）"])

pg.Dedup("shadows/local-lights/dual-paraboloid.md")
pg.Add("shadows/local-lights/dual-paraboloid.md", '''
## 考え方：6 面を、2 面に

キューブマップは、**6 面**を、描くので、重いです。**放物面マッピング**（Brabec ら、2002）は、**全方向を、2 枚**のテクスチャで、覆います。**前半球**と**後半球**を、**放物面**（パラボロイド）で、それぞれ、**1 枚に、投影**します。**描画は、2 回**で、済みます。

```text
 光を中心に:
   前半球 → 放物面 1（1 枚のテクスチャ）
   後半球 → 放物面 2（1 枚のテクスチャ）
```

放物面への、投影は、**頂点シェーダー**で、行います。**方向ベクトルから、2D 座標**に、変換します。

```hlsl
// 前半球の、放物面投影。dir は、光から頂点への、単位方向（光の座標系）。
float2 ParaboloidProject(float3 dir) {
  // dir.z が、前向き（+Z）の半球。
  return dir.xy / (1.0 + dir.z);        // 放物面の、写像（−1〜1 の範囲に収まる）
}
```

## 頂点シェーダー

```hlsl
cbuffer ParaboloidCB : register(b0) {
  float4x4 g_world_to_light;     // ワールド → 光の座標系（位置だけ引いて、向きを合わせる）
  float g_light_range;
  float g_direction_sign;        // +1 = 前半球、−1 = 後半球
  float2 pad;
};

struct VSOut {
  float4 position : SV_Position;
  float clip_z : TEXCOORD0;      // 半球の外（反対側）を、クリップするため
};

VSOut main(float3 position : POSITION) {
  float3 p = mul(float4(position, 1.0), g_world_to_light).xyz;       // 光の座標系での、頂点位置
  float dist = length(p);
  float3 dir = p / dist;
  dir.z *= g_direction_sign;                                          // 後半球は、反転して、前半球と同じ式で

  VSOut o;
  float2 xy = dir.xy / (1.0 + dir.z);                                 // 放物面投影
  o.position = float4(xy, dist / g_light_range, 1.0);                 // z には、光からの距離（0〜1）
  o.clip_z = dir.z + 0.0;                                             // 半球の外は、クリップ（負の値）
  return o;
}
```

| 要素 | 内容 |
| --- | --- |
| `dir.xy / (1 + dir.z)` | **放物面の、写像**。`dir.z = 1`（真正面）で、`xy = dir.xy / 2`、`dir.z = 0`（真横）で、`xy = dir.xy`（円周） |
| 深度 | **光からの、距離**（`dist / range`）を、**直接**、書く（放物面は、**透視投影の、深度が、定義できない**ため） |
| 半球の、クリップ | `dir.z < 0` の頂点は、反対側の半球なので、**クリップ** |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **描画が、2 回**（キューブマップは 6 回）。**シャドウ パスが、安い** |
| 長所 | **メモリが、小さい**（2 枚）。キューブマップの、1/3 |
| 短所 | **非線形な、投影を、頂点シェーダーで**、行う。**三角形が、直線でなく、曲線に、変形される**のに、**頂点だけ変換**するので、**大きな三角形で、歪む**。**メッシュを、細かく**（テッセレーション）、する必要 |
| 短所 | **解像度が、不均一**（中心で、高く、縁で、低い） |
| 短所 | **半球の、境界**（真横）で、**継ぎ目**ができる |
| 短所 | **ハードウェアの、比較サンプラー**（PCF）が、**使えない**（距離を、保存するため） |
| 短所 | **現代では、あまり、使われない**（キューブマップの、描画が、**ジオメトリ シェーダー**や、**1 回のインスタンス描画**で、**効率化**できるため） |

### 歪みの、問題

**放物面の、投影**は、**直線を、曲線に、変換**します。ところが、ラスタライザーは、**投影後の、頂点を、結ぶ**、**直線の三角形**として、描きます。**大きな三角形**（地面）では、**頂点間の、曲線**が、**直線で、近似**され、**影が、歪みます**。

| 対策 | 内容 |
| --- | --- |
| **メッシュを、細分化** | 大きな三角形を、**細かく**、分割する（テッセレーションで、**シャドウ パス**だけ） |
| 影を落とす物を、**細かいメッシュ**に限る | 地面などは、**影を、落とさない**（受けるだけ）にする |

## キューブマップとの、比較

| | キューブマップ | 放物面（デュアル） |
| --- | --- | --- |
| 描画回数 | 6（面ごとに、視錐台カリングで、減らせる） | 2 |
| 歪み | **なし**（通常の、透視投影） | **あり**（細分化が、必要） |
| PCF（ハードウェア） | **使える** | 使えない（距離保存） |
| 精度 | 面の全体で、**比較的、均一** | 中心が、高く、縁が、低い |
| 実装 | **簡単** | やや複雑（頂点シェーダー、クリップ） |
| 現状 | **標準** | **古い手法**。**メモリが、厳しい、古い環境**で、使われた |

**現在の、ゲーム**では、**キューブマップ**が、標準で、**放物面は、ほとんど、使われません**。**歴史的な手法として**、知っておく程度で、十分です。

''', before="## よくあるミス")
pg.Refs("shadows/local-lights/dual-paraboloid.md", [BRABEC02, "Heidrich, Seidel, \"View-Independent Environment Maps\", Eurographics/SIGGRAPH Graphics Hardware Workshop 1998（放物面による、環境マップ）", OLSSON, RTR])

pg.Dedup("shadows/local-lights/many-lights.md")
pg.Add("shadows/local-lights/many-lights.md", '''
## 問題：影を落とす光は、数に限りがある

光が、**100 個**あっても、**すべてに、シャドウ マップを、作る**ことは、できません（点光源 1 つで、シーンを、6 回、描く）。**どの光に、影を、与えるか**、**どう効率よく、作るか**を、設計する必要があります。

## 影を、落とす光を、選ぶ

| 基準 | 内容 |
| --- | --- |
| **画面に、映っている** | 視錐台の外にある光（光の、範囲球が、視錐台と、交わらない）は、**影を、作らない** |
| **画面上の、大きさ** | 光が、画面に、**大きく**映る（近い、明るい光）ほど、**優先** |
| **明るさ** | 暗い光は、影が、見えない。**影を、省く** |
| **距離** | **遠い光**は、影が、細かく見えない。**影なし**、または、**低解像度** |
| **重要さ** | ゲームの、**演出上、重要な光**（プレイヤーの懐中電灯、重要な、ランプ）は、**優先** |

```cpp
// 光ごとに、「影の優先度」を、計算して、上位 N 個だけ、影を作る。
float ShadowPriority(const Light& light, const Camera& camera) {
  const float dist = Distance(light.position, camera.position);
  if (dist > light.range + camera.far_plane) return 0.0f;
  if (!camera.frustum.Intersects(Sphere{light.position, light.range})) return 0.0f;
  // 画面上の、おおよその大きさ（半径 / 距離）× 明るさ
  const float screen_size = light.range / std::max(dist, 1.0f);
  return screen_size * light.intensity * light.importance;
}

// 優先度の高い順に、N 個（8 個など）を選んで、シャドウ マップを割り当てる。
std::sort(lights.begin(), lights.end(), [&](auto& a, auto& b) { return a.priority > b.priority; });
for (int i = 0; i < std::min<int>(kMaxShadowLights, lights.size()); ++i) lights[i].shadow_slot = i;
```

## シャドウ マップを、アトラスに

影を、落とす、光が、複数あるとき、シャドウ マップを、**1 枚の大きなテクスチャ（アトラス）**に、**まとめます**。ライトごとに、テクスチャを、**バインドし直す**必要が、なくなります。

```text
┌──────────┬──────┬──────┐
│          │ 光 2 │ 光 3 │
│  光 1     ├──────┼──────┤
│ (2048²)  │ 光 4 │ 光 5 │
│          │ (512²)│(512²)│
└──────────┴──────┴──────┘
   4096×4096 のアトラスに、解像度の違う、シャドウ マップを、詰める
```

| 利点 | 内容 |
| --- | --- |
| **1 つのテクスチャ** | シェーダーに、渡す、リソースが、1 つ |
| **解像度を、光ごとに、変えられる** | 画面上で、大きい光は、**大きなタイル**。小さい光は、**小さなタイル** |

各光の、**アトラス内の、位置と大きさ**（`offset`、`scale`）を、**定数バッファ**に、持たせ、**UV を、変換**して、読みます。

```hlsl
struct ShadowTile { float4 uv_scale_offset; };      // xy = スケール、zw = オフセット（アトラス内の位置）
StructuredBuffer<ShadowTile> g_tiles : register(t10);

float SampleShadowAtlas(uint tile_index, float2 local_uv, float depth) {
  ShadowTile t = g_tiles[tile_index];
  float2 atlas_uv = local_uv * t.uv_scale_offset.xy + t.uv_scale_offset.zw;
  return g_shadow_atlas.SampleCmpLevelZero(g_shadow_sampler, atlas_uv, depth);
}
```

**タイルの境界**では、**PCF が、隣のタイルを、読んで**しまうので、**タイルの縁に、余白**を設け、**UV を、余白の内側に、クランプ**します。

## 描画の、頻度を、減らす

**すべての光の影を、毎フレーム、更新**する必要は、ありません。

| 光の種類 | 更新 |
| --- | --- |
| **静止した光 + 静止した物** | **一度作って、保存**（キャッシュ）。**更新しない** |
| **静止した光 + 動く物** | **静止した物の、シャドウ マップ**を、キャッシュし、**動く物だけ**を、毎フレーム、描き足す（2 枚を、合成） |
| **動く光** | 毎フレーム更新（重い）。**数を、制限** |
| **遠い光** | **数フレームに 1 回**（影が、少し、遅れても、気づかない） |

### 静止物のキャッシュ

```text
キャッシュ（起動時、または、変更時に 1 回）:  静止した物だけを、深度に描く → static_shadow_map
毎フレーム:  static_shadow_map を、コピー → dynamic_shadow_map に、動く物を、描き足す（深度テストで、手前が、勝つ）
```

```cpp
// 静止物の影のキャッシュを、毎フレームの、シャドウ マップに、コピーしてから、動く物を、描き足す。
context->CopyResource(shadow_map.Get(), static_shadow_cache.Get());     // 静止物の深度を、コピー
context->OMSetRenderTargets(0, nullptr, shadow_dsv.Get());
// ここでは、Clear しない（コピーした深度を、残したまま、動く物を、重ねて描く）
DrawDynamicShadowCasters();
```

**動く物が、少なければ**、**シャドウ パスが、劇的に、軽くなります**。

## ライトの、種類による、判断

| 光 | 影の扱い |
| --- | --- |
| **太陽**（1 つ） | CSM、毎フレーム更新（[CSM](../cascaded.md)） |
| **プレイヤーの、懐中電灯** | **スポットライト**の、影。毎フレーム更新。高解像度 |
| **近くの、点光源**（数個） | キューブマップ。静止物は、キャッシュ |
| **遠くの、点光源**（多数） | **影なし**（または、低解像度、更新を、間引く） |
| **小さな、装飾の光**（ろうそく） | **影なし**。コンタクト シャドウで、補う（[Contact Shadows](../contact-shadows.md)） |

## 影なしの光に、影の、効果を

影を、落とさない、光でも、**暗さの、手がかり**が、欲しい場面があります。

| 方法 | 内容 |
| --- | --- |
| **コンタクト シャドウ** | 画面空間で、**短い距離**の、影を作る（[Contact Shadows](../contact-shadows.md)） |
| **AO**（アンビエント オクルージョン） | 物の、隙間・接触部分を、暗くする（[AO](../../ao/index.md)） |
| **距離フィールドの、影** | 全体に、**安く**、ソフトな影（[Distance Field Shadows](../sdf-shadows.md)） |

## クラスタード シェーディングとの、関係

数百の光を、**画面の、小さな領域（クラスター）**ごとに、**影響する光を、絞って**、シェーディングする方法です（Olsson ら、2012）。**影を、落とす光**は、**クラスターごとの、光のリスト**の中で、**影のアトラスの、タイル番号**を、持ちます。

```hlsl
// クラスターの、光のリストを、走査して、影つきの光だけ、シャドウ マップを読む。
for (uint i = 0; i < light_count_in_cluster; ++i) {
  Light light = g_lights[light_indices[i]];
  float shadow = 1.0;
  if (light.shadow_tile >= 0) shadow = SampleLightShadow(light, world_pos, normal);
  color += ShadeLight(light, ...) * shadow;
}
```

''', before="## よくあるミス")
pg.Refs("shadows/local-lights/many-lights.md", [OLSSON, "Harada, McKee, Yang, \"Forward+: Bringing Deferred Lighting to the Next Level\", Eurographics 2012 Short Papers", BRABEC02, RTR])
print("ok")
