import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

SOUSA = '''Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005'''
WYMAN05 = '''Wyman, "An Approximate Image-Space Approach for Interactive Refraction", ACM Transactions on Graphics (SIGGRAPH 2005)'''
SCHLICK = '''Schlick, "An Inexpensive BRDF Model for Physically-based Rendering", Computer Graphics Forum, Vol. 13, No. 3, 1994'''
WALTER = '''Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（屈折、フレネル、透過の章）'''
HECHT = '''Hecht, "Optics", 5th Edition, Pearson, 2016（スネルの法則、フレネルの式、分散）'''
SELLMEIER = '''Sellmeier, "Zur Erklärung der abnormen Farbenfolge im Spectrum einiger Substanzen", Annalen der Physik und Chemie, Vol. 219, 1871（屈折率の波長依存の式）'''
D3D11_COPY = '''Microsoft Learn, "ID3D11DeviceContext::CopyResource"'''
MITTRING = '''Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games'''

# ---------------------------------------------------------------- screen space refraction
pg.Dedup("translucency/refraction/screen-space.md")
pg.Add("translucency/refraction/screen-space.md", '''
## 考え方：画面のコピーを、ずらして読む

本当の屈折は、**光線を、物体の中で、曲げて、追跡**する必要があり、**重い**です。**画面空間の屈折**は、すでに描いた**シーンの色**を、**テクスチャとして、コピー**し、**屈折する物体の、画素で、読む位置を、ずらす**ことで、**屈折らしい、歪み**を、安く作ります（Sousa、2005）。

```text
① 不透明な物を、すべて描く                       → シーンの色
② シーンの色を、テクスチャにコピーする           （CopyResource）
③ ガラスなどの屈折する物を描く:
     画素ごとに、法線から「ずらし量」を求め、
     コピーしたシーンを、ずらした位置で読んで、ガラスの色にする
```

## 実装

### ① シーンの色を、コピーする

屈折する物は、**画面に、すでに描かれた**、シーンの色を、**読み**ながら、**同じ画面に、描きます**。**読み書きが、同じテクスチャ**だと、衝突する（同時に、読めない）ので、**別のテクスチャに、コピー**します。

```cpp
// 不透明の描画の後、屈折する物を描く前に、シーンの色を、コピーする。
context->CopyResource(scene_copy_tex.Get(), scene_color_tex.Get());
// 屈折する物の描画では、scene_copy_srv を、読み取り元にする。書き込み先は、scene_color_rtv のまま。
```

`CopyResource` は、**同じ大きさと、形式**の、テクスチャ同士を、コピーします。MSAA のレンダー ターゲットを、コピーするには、**先に、リゾルブ**（`ResolveSubresource`）して、**1 サンプルの、テクスチャ**にします。

### ② ピクセル シェーダー

```hlsl
Texture2D<float4> g_scene_copy : register(t0);
Texture2D<float> g_scene_depth : register(t1);

float4 main(PSInput input) : SV_Target {
  float2 screen_uv = input.position.xy * g_inv_screen_size;

  // 法線を、ビュー空間に直して、その xy を「ずらし量」にする。
  float3 view_normal = mul((float3x3)g_view, normalize(input.world_normal));
  float2 offset = view_normal.xy * g_refraction_strength;
  float2 refract_uv = screen_uv + offset * float2(1, -1);          // 画面の y は、下向きなので、反転

  float3 refracted = g_scene_copy.Sample(g_linear_clamp, refract_uv).rgb;
  return float4(refracted * g_tint, 1.0);
}
```

| 要素 | 内容 |
| --- | --- |
| 法線 | **面が、傾いているほど、大きく、ずれる** |
| `g_refraction_strength` | **屈折の強さ**。0.02〜0.1。**屈折率の、違いと、物体の厚み**を、まとめた、調整値 |
| `g_tint` | ガラスの色（色付きガラスなら、透過色） |

## 品質を、高める、工夫

### ① 手前の物を、ずらさない

ずらした先に、**ガラスより、手前にある物**（ガラスの、手前に、立っている人）が、あると、その色を、**読んでしまい**、**人の色が、ガラスに、にじむ**ことがあります。**深度**で、判定します。

```hlsl
float scene_depth = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, refract_uv).r);
float glass_depth = LinearizeDepth(input.position.z);
if (scene_depth < glass_depth) refract_uv = screen_uv;        // ガラスより手前の物は、ずらさない
```

### ② 深度で、ずらし量を、変える

ガラスの**向こうの物**が、**遠いほど**、屈折の、**ずれ**は、大きく見えます（視線が、曲がって、遠くの物を、見るため）。

```hlsl
float behind = max(scene_depth - glass_depth, 0.0);            // ガラスの向こうの、物までの距離
offset *= saturate(behind / g_refraction_distance);              // 近い物は、あまりずらさない
```

### ③ 画面の端

ずらした UV が、**画面の外**になることがあります。**CLAMP** で、端の色を、伸ばすか、**ずらし量を、端で、弱め**ます。

```hlsl
float2 edge = saturate(min(refract_uv, 1.0 - refract_uv) * 10.0);        // 端から 0.1 の幅で、弱める
offset *= min(edge.x, edge.y);
```

### ④ 色の、分散（任意）

RGB を、**わずかに違うずらし量**で読むと、**縁が、虹色**になります（[Dispersion](dispersion.md)）。

## 限界

| 限界 | 内容 |
| --- | --- |
| **画面の外**が、映らない | 屈折で、画面の外の、物が、見える位置に、ずれても、**画面にない**ので、読めない（端の、色を、伸ばす） |
| **ガラスの手前**の物 | 上記の、深度チェックで、**ごまかす**。完全には、正しくない |
| **2 重の、屈折**（ガラス越しの、ガラス） | **コピーが、1 枚**なので、**ガラスの、向こうの、ガラスの、屈折が、反映されない**。ガラスを、**奥から手前**に、描き、**そのたびに、コピー**すると、近似できる（重い） |
| **内部の、反射**（全反射、複数回の、内部反射） | 扱えない |
| **正確さ** | 実際の、光の経路と、違う。**「それらしく、見える」**だけ |

## 向く場面と、向かない場面

| 場面 | 判断 |
| --- | --- |
| 窓ガラス、水面、氷、ガラス瓶（薄い、または、簡易） | **向く** |
| 水晶、宝石、**厚い**ガラスの、塊 | **不足**（内部の、屈折・反射が、重要）。**厚み・色**の、工夫が、必要（[Thin and Thick Glass](thin-thick.md)） |
| 画面の端の、ガラス | 注意（画面外を、読めない） |

''', before="## よくあるミス")
pg.Refs("translucency/refraction/screen-space.md", [SOUSA, WYMAN05, MITTRING, D3D11_COPY])

# ---------------------------------------------------------------- fresnel
pg.Dedup("translucency/refraction/fresnel.md")
pg.Add("translucency/refraction/fresnel.md", '''
## 反射と、屈折の、割合

ガラスや水の表面に、光が、当たると、**反射する光**と、**屈折して、中へ入る光**に、分かれます。**反射の割合が、フレネル反射率 `F`**、**屈折（透過）の割合が `1 − F`** です（エネルギーは、保存される。吸収を、ここでは、無視する）。

```text
最終の色 = 反射の色 × F  +  屈折の色 × (1 − F)
```

`F` は、**見る角度**と、**屈折率**で、決まります。**真上から見る**と、反射は、少なく、**浅い角度で見る**ほど、反射が、増えます。

## 屈折率と F₀

**屈折率**（n）が、大きい物ほど、**真上から見たとき**の、反射率 `F₀` が、大きくなります。

```text
F₀ = ( (n − 1) / (n + 1) )²              空気（n = 1）から、屈折率 n の物へ
```

| 物質 | 屈折率 n | F₀ |
| --- | --- | --- |
| 水 | 1.33 | 0.020 |
| 氷 | 1.31 | 0.018 |
| ガラス（窓） | 1.5 | 0.040 |
| クリスタル ガラス | 1.6〜1.7 | 0.053〜0.067 |
| サファイア | 1.77 | 0.077 |
| ダイヤモンド | 2.42 | 0.172 |

ガラスの、**4%** が、反射します（正面から、見ても、ガラスに、**自分の、姿が、うっすら映る**のは、このため）。**ダイヤモンド**が、**よく光る**のは、屈折率が、高く、反射が、強いためです。

## Schlick 近似

```hlsl
float FresnelSchlick(float cos_theta, float f0) {
  return f0 + (1.0 - f0) * pow(1.0 - saturate(cos_theta), 5.0);
}
```

詳しい式と、近似の精度は、[Water Fresnel](../../water/shading/fresnel.md) で説明しています（水は `F₀ = 0.02`、ガラスは `0.04`）。ガラスでは、**`F₀` を、屈折率から、計算**して、渡します。

```hlsl
float F0FromIOR(float ior) {
  float r = (ior - 1.0) / (ior + 1.0);
  return r * r;
}
```

## ガラスの、見た目への、影響

| 見る角度 | F | 見え方 |
| --- | --- | --- |
| 真正面（0°） | 4% | **ほぼ透明**。向こうの景色が、はっきり見える。反射は、うっすら |
| 60° | 9% | 少し、反射が、見える |
| 80° | 33% | **反射が、強い**。景色が、はっきり映る |
| 89° | 90% | **ほぼ鏡** |

**ガラス窓を、斜めから見る**と、**向こうが、見えにくく**なり、**空や、周囲が、映る**のは、このためです。

## 実装

```hlsl
float3 normal = normalize(input.world_normal);
float3 view = normalize(g_camera_position - input.world_position);
float cos_theta = saturate(dot(normal, view));
float F = FresnelSchlick(cos_theta, F0FromIOR(1.5));

float3 reflection = SampleReflection(reflect(-view, normal));      // 環境マップ、SSR など
float3 refraction = SampleRefraction(...);                         // 画面のコピー、など
float3 color = lerp(refraction * tint, reflection, F);
```

**反射**は、環境マップ（[Reflection Probes](../../reflections/probes/index.md)）、SSR（[SSR](../../reflections/ssr-basics/index.md)）などで、与えます。

## ガラスの、**内側**から

ガラスの**中から、外を見る**（ガラスの、厚みの中を、通って、裏面に当たる光）とき、**屈折率の、関係が、逆**になります（`n₁ = 1.5`、`n₂ = 1.0`）。**入射角が、臨界角を、超える**と、**全反射**が起きます（ガラスで、約 41.8°、水で、約 48.6°）。

```text
臨界角 θ_c = asin(1 / n)          ガラス: asin(1/1.5) ≈ 41.8°、ダイヤ: asin(1/2.42) ≈ 24.4°
```

| 物質 | 臨界角 |
| --- | --- |
| 水 | 48.6° |
| ガラス（1.5） | 41.8° |
| ダイヤモンド（2.42） | 24.4° |

ダイヤモンドは、**臨界角が、小さい**ので、**内部で、多くの光が、全反射**を、繰り返し、**光が、閉じ込められ、きらめきます**（カットの、設計と、組み合わさる）。画面空間の屈折では、**内部の、複数回の反射は、扱えません**（[Thin and Thick Glass](thin-thick.md)）。

## 粗い面（すりガラス）

すりガラスや、荒れた水面は、**微小な、凹凸**で、反射と屈折が、**散らばります**。**GGX 分布**を、使った、屈折（Walter ら、2007）が、**理論的な、モデル**です。実用では、**反射も、屈折も、ぼかす**（粗さに応じて、ミップを、読む）。

```hlsl
// 粗さに応じて、背景（画面のコピー）の、ぼかした版を、読む。
float lod = roughness * kMaxMip;
float3 refracted = g_scene_copy_blurred.SampleLevel(g_linear_clamp, refract_uv, lod).rgb;
```

画面のコピーに、**ミップを、作って**（`GenerateMips`）おくと、**粗さ**に応じた、ぼけが、安く、得られます。

''', before="## よくあるミス")
pg.Refs("translucency/refraction/fresnel.md", [SCHLICK, HECHT, RTR, WALTER])

# ---------------------------------------------------------------- dispersion
pg.Dedup("translucency/refraction/dispersion.md")
pg.Add("translucency/refraction/dispersion.md", '''
## 分散とは

ガラスの屈折率は、**光の波長によって、少し違います**。**青い光は、赤い光より、少し、大きく**曲がります。結果、**白い光が、プリズムを、通ると、虹色に、分かれます**。これが**分散**です。

| 色 | 波長 | 屈折率（クラウン ガラス） |
| --- | --- | --- |
| 赤 | 約 650 nm | 約 1.514 |
| 緑 | 約 550 nm | 約 1.519 |
| 青 | 約 450 nm | 約 1.527 |

差は、**わずか**（1% 以下）ですが、**曲がる角度の、わずかな違い**が、**距離を、進むと、はっきりした色の、ずれ**になります。ダイヤモンドの、**きらめき（ファイア）**、プリズム、**縁の、虹色**は、すべて、分散による現象です。

## 屈折率の、波長依存

屈折率は、波長に対して、**単調に、減る**（長い波長ほど、小さい）。経験式（Cauchy の式、Sellmeier の式）が、あります。

```text
Cauchy の式:  n(λ) = A + B / λ²                  λ は、マイクロメートル。A、B は、材料ごとの定数
```

| 材料 | A | B（μm²） |
| --- | --- | --- |
| 水 | 1.3199 | 0.00306 |
| クラウン ガラス | 1.5046 | 0.00420 |
| フリント ガラス | 1.7280 | 0.01342 |
| ダイヤモンド | 2.3780 | 0.01158 |

フリント ガラス（鉛を含み、分散が大きい）や、ダイヤモンドは、`B` が、大きく、**分散が、強い**。

```hlsl
// Cauchy の式で、波長（マイクロメートル）から屈折率を求める。
float CauchyIOR(float lambda_um, float A, float B) {
  return A + B / (lambda_um * lambda_um);
}
float ior_r = CauchyIOR(0.65, 1.5046, 0.00420);     // 赤
float ior_g = CauchyIOR(0.55, 1.5046, 0.00420);     // 緑
float ior_b = CauchyIOR(0.45, 1.5046, 0.00420);     // 青
```

## 実装：RGB を、別々に、屈折させる

最も、簡単な方法は、**赤・緑・青の、3 つの屈折率**で、**屈折ベクトルを、3 回**求め、**それぞれ、違う位置を、読む**ことです。

```hlsl
float3 view = normalize(input.world_position - g_camera_position);
float3 N = normalize(input.world_normal);

// RGB で、別の屈折率（空気 → ガラス: eta = 1 / n）。
float3 refr_r = refract(view, N, 1.0 / ior_r);
float3 refr_g = refract(view, N, 1.0 / ior_g);
float3 refr_b = refract(view, N, 1.0 / ior_b);

// 画面空間の屈折: それぞれの屈折ベクトルから、ずらし量を求め、別々に、読む。
float2 uv_r = screen_uv + ViewOffset(refr_r) * g_refraction_strength;
float2 uv_g = screen_uv + ViewOffset(refr_g) * g_refraction_strength;
float2 uv_b = screen_uv + ViewOffset(refr_b) * g_refraction_strength;

float3 refracted;
refracted.r = g_scene_copy.Sample(g_linear_clamp, uv_r).r;
refracted.g = g_scene_copy.Sample(g_linear_clamp, uv_g).g;
refracted.b = g_scene_copy.Sample(g_linear_clamp, uv_b).b;
```

簡易版は、**法線から、ずらし量を求め**、**RGB に、少しだけ違う係数**を、掛けます。

```hlsl
float2 offset = view_normal.xy * g_refraction_strength;
refracted.r = g_scene_copy.Sample(g_linear_clamp, screen_uv + offset * 0.95).r;     // 赤: 小さく曲がる
refracted.g = g_scene_copy.Sample(g_linear_clamp, screen_uv + offset * 1.00).g;
refracted.b = g_scene_copy.Sample(g_linear_clamp, screen_uv + offset * 1.05).b;     // 青: 大きく曲がる
```

0.95、1.00、1.05 の、**差**を、広げるほど、**虹色の、縁取り**が、強くなります。**水のように、分散が小さい物**では、差を、**ごく小さく**します。

## 3 色では、足りない

RGB の、**3 色だけ**だと、**色の、分離が、3 つの、ずれた、像**に、見えます（赤の像、緑の像、青の像）。**なめらかな、虹**にするには、**もっと多くの波長**で、サンプルします。

```hlsl
// 波長を 8 つに分けて、それぞれ屈折させ、RGB に、変換して足す（スペクトルの、近似）。
float3 acc = 0;
float3 weight_sum = 0;
for (int i = 0; i < 8; ++i) {
  float t = (i + 0.5) / 8.0;                           // 0（赤）〜 1（青）
  float lambda = lerp(0.70, 0.40, t);                   // 波長（μm）
  float ior = CauchyIOR(lambda, A, B);
  float3 refr = refract(view, N, 1.0 / ior);
  float3 sample_color = g_scene_copy.Sample(g_linear_clamp, screen_uv + ViewOffset(refr) * g_refraction_strength).rgb;
  float3 w = WavelengthToRGB(lambda);                   // 波長に対応する、RGB の重み（虹の色）
  acc += sample_color * w;
  weight_sum += w;
}
float3 refracted = acc / weight_sum;
```

`WavelengthToRGB` は、**波長（380〜700 nm）から、RGB の重みを返す関数**です（虹色の、グラデーションの近似）。8〜16 サンプルで、**なめらかな虹**に、なります。コストは、サンプル数に、比例して、増えます。

## どこに、現れるか

| 対象 | 分散の、見え方 |
| --- | --- |
| 窓ガラス | ほとんど、見えない（薄く、分散も小さい） |
| 水 | ほとんど、見えない（分散が、小さい） |
| **ガラスの、縁**、**切り子** | 縁の、**細い、虹色**。曲面で、強い |
| **プリズム** | 白い光が、**虹色**に、分かれる |
| **ダイヤモンド、宝石** | 内部の、反射・屈折で、**カラフルな、きらめき（ファイア）** |

**平らな、薄いガラス**では、**分散は、ほぼ、見えません**。**縁や、曲がった、厚い部分**で、効果が、現れるので、**そこに、使う**と、**コストの割に、見栄えが、よくなります**。

## 色収差（レンズ）との違い

[Chromatic Aberration](../../postprocess/lens-effects/chromatic-aberration.md) は、**カメラの、レンズ**が、起こす、**色の、ずれ**で、**画面の、周辺**に、現れます。**物体（ガラス）の分散**は、**ガラスの、**物体**の、部分だけ**に、現れます。**原因も、場所も、別**です。

''', before="## よくあるミス")
pg.Refs("translucency/refraction/dispersion.md", [HECHT, SELLMEIER, RTR, "Cauchy, \"Mémoire sur la dispersion de la lumière\", Prague, 1836（Cauchy の式）"])

# ---------------------------------------------------------------- thickness color
pg.Dedup("translucency/refraction/thickness-color.md")
pg.Add("translucency/refraction/thickness-color.md", '''
## 色付きガラスは、厚いほど、濃い

色付きの、ガラス（緑のボトル、青い氷）は、**光が、ガラスの中を、通る距離が、長いほど、濃く**見えます。光が、**ガラスに吸収**されるためで、水の中の光と、**同じ原理**です（[Color by Water Depth](../../water/shading/depth-color.md)）。

```text
透過率 T = exp( −σ × 厚み )          σ: 吸収係数（RGB ごと）
```

| 厚み | 緑のガラス（赤と青を、吸収） |
| --- | --- |
| 薄い（縁の、とがった所） | ほぼ透明 |
| 中くらい | 薄い緑 |
| 厚い（底、中心） | 濃い緑 |

**厚みが、場所で違う**ことが、**ガラスの、立体感**を、作ります（コップの底が、濃い、ボトルの肩の、薄い所が、明るい）。

## 厚みを、求める

### ① 解析的な形（球、箱）

形が、単純なら、**視線が、物体を、通る長さ**を、数式で、求められます。

```hlsl
// 球: 視線（原点 ro、方向 rd）が、中心 c、半径 r の球を、通り抜ける長さ。
float SphereThickness(float3 ro, float3 rd, float3 c, float r) {
  float3 oc = ro - c;
  float b = dot(oc, rd);
  float h = b * b - (dot(oc, oc) - r * r);
  if (h < 0.0) return 0.0;                       // 当たらない
  return 2.0 * sqrt(h);                           // 入口と出口の距離
}
```

### ② 手前と奥の、深度の差

任意の形では、**物体の、背面の深度**と、**前面の深度**の、差が、**その画素での、厚み**です。**背面を、先に描いて、深度を、別のテクスチャに、保存**し、**前面を描くとき**に、読みます。

```text
① 背面だけを描く（表面をカリング）→ 背面の深度を、テクスチャに保存
② 前面を描く → 前面の深度と、保存した背面の深度の、差が、厚み
```

```hlsl
Texture2D<float> g_back_depth : register(t2);          // 背面の深度（視点深度）

float4 main(PSInput input) : SV_Target {
  float front = LinearizeDepth(input.position.z);
  float back = LinearizeDepth(g_back_depth.Load(int3(input.position.xy, 0)));
  float thickness = max(back - front, 0.0);
  // 視線方向の距離にする（視点深度の差は、カメラの前方向に沿っているので、cos で割る）
  thickness /= max(dot(normalize(input.world_position - g_camera_position), g_camera_forward), 0.1);

  float3 T = exp(-g_absorption * thickness);            // 色ごとの透過率
  float3 refracted = SampleBackground(...) * T;
  ...
}
```

### ③ 厚みを、テクスチャに、焼く

**物体ごとの、厚みの分布**を、事前に、テクスチャ（**厚みマップ**）に、**焼いて**おく方法です。**物体の内側から、外へ、レイを飛ばして**、厚みを、求め、**UV に、焼きます**（ツールで、事前計算）。**実行時は、テクスチャを、読むだけ**で、安いです。**視線の向きに、よらない**（近似）ので、**簡易**です。

| 方法 | 正確さ | コスト | 向き |
| --- | --- | --- | --- |
| 解析的 | 完全 | 最小 | 球、箱、円柱 |
| 背面の深度 | **視線に、正しい** | 追加のパス（背面を描く） | 任意の、凸な形 |
| 厚みマップ | 視線に依存しない（近似） | 最小 | 複雑な、静止物（彫像、瓶） |

背面の、深度を使う方法は、**凸な形**（瓶、球）で、正確です。**凹んだ形**（ドーナツ、コップ）では、視線が、物体を、**2 回以上**通るので、**不正確**になります。

## 色の付け方

### 吸収係数 σ を、色から作る

「**1 m の厚さで、この色になる**」と、アーティストが、色を指定し、そこから、`σ` を、逆算します。

```text
T(1m) = exp(−σ)   →   σ = −ln( T(1m) )
```

```hlsl
// 「1 メートル通ったあとの色」から、吸収係数を作る。
float3 AbsorptionFromColor(float3 color_at_1m) {
  return -log(max(color_at_1m, 0.001));
}
// 例: 緑のガラス（赤と青を吸収）
float3 sigma = AbsorptionFromColor(float3(0.2, 0.8, 0.3));
```

**ガラスは、薄い（数 mm〜数 cm）**ので、`color_at_1m` を、そのまま使うと、ほとんど、色が付きません。**厚みのスケール**（`thickness × scale`）を、調整するか、**「厚み 1 cm の色」**を、基準にします。

### 表面の色と、内部の色

| 色 | 原因 | 表現 |
| --- | --- | --- |
| **内部の吸収** | 光が、ガラスの中を、通る間に、吸収される | `exp(−σ × 厚み)`（このページ） |
| **表面の反射** | 表面の、反射。**色が、付かない**（ガラスは、反射が、白い）。**金属は、反射に、色が付く** | フレネル（[Fresnel](fresnel.md)）。白い反射 |
| **内部の散乱** | すりガラス、**乳白色**、氷の気泡 | 屈折を、ぼかし、**散乱の色**を、足す |

## 濁り（散乱）

すりガラス、氷、乳白色のガラスは、**内部の、散乱**で、**背景が、ぼやけます**。

```hlsl
// 厚みに応じて、背景を、ぼかす（粗さを、厚みで増やす）。
float lod = saturate(thickness / g_scatter_distance) * kMaxMip;
float3 background = g_scene_copy_blurred.SampleLevel(g_linear_clamp, refract_uv, lod).rgb;
// 散乱の色（白っぽい）を、厚みに応じて、足す
float scatter = 1.0 - exp(-thickness * g_scatter_coeff);
float3 color = lerp(background * T, g_scatter_color, scatter);
```

厚みが、増えるほど、**背景が、ぼやけ、散乱の色**（白、乳白）に、近づきます。

''', before="## よくあるミス")
pg.Refs("translucency/refraction/thickness-color.md", [RTR, HECHT, "Beer, \"Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten\", Annalen der Physik, 1852（吸収の法則）", SOUSA])

# ---------------------------------------------------------------- thin thick
pg.Dedup("translucency/refraction/thin-thick.md")
pg.Add("translucency/refraction/thin-thick.md", '''
## 薄いガラスと、厚いガラス

屈折の、扱い方は、**ガラスの、厚み**で、大きく変わります。

| | 薄いガラス（窓、ガラス板、水面） | 厚いガラス（瓶、球、宝石、水晶） |
| --- | --- | --- |
| 光の、通り道 | **入口と出口が、平行**（ほぼ同じ向きで、出る）。**ほぼ、まっすぐ**通る | **内部で、大きく、曲がる**。出口の向きが、入口と、大きく違う |
| 見え方 | 向こうが、**ほぼ、そのまま**見える。**わずかに、ずれる** | 向こうが、**大きく、歪む**。**上下左右が、逆転**することも |
| 必要な、計算 | **ごく小さな、ずらし**（画面空間で、十分） | **入口の屈折 + 出口の屈折**（2 回の屈折）。内部の反射 |
| 代表例 | 窓、コップの壁、ガラス板 | 水晶球、ガラス玉、ダイヤモンド、水の入った、コップ（全体） |

## 薄いガラス：1 回で、十分

薄い、平行な、ガラス板では、**入射の屈折**と、**出射の屈折**が、**ちょうど、打ち消し合い**、光は、**元の向きのまま**、少し、ずれて、出てきます。**ずれ**は、**厚みと、入射角**で決まり、**薄ければ、ごくわずか**です。

```text
 空気 | ガラス | 空気
      ╲       ╲
       ╲___    ╲        入射の向きと、出射の向きは、同じ（平行）
            ╲    ╲___   ずれ（横ずれ）は、厚みに比例
```

このため、**窓ガラス**は、**画面空間の屈折**（[Screen-Space Refraction](screen-space.md)）で、**十分**です。**ずらし量を、ごく小さく**するか、**ほぼ、ゼロ**に、します。**フレネル反射**と、**表面の汚れ**、**厚みによる、わずかな色**が、見た目の、主役です。

## 厚いガラス：屈折が、2 回

球や、瓶のような、**厚い**ガラスでは、光が、**入口で、1 回曲がり**、**内部を通って**、**出口で、もう 1 回曲がります**。

```text
 空気 | ガラス球                 | 空気
      ╲╲         ╲╲
       ╲╲ ←入口で屈折  ╲╲ ←出口で屈折
```

**入口の、屈折ベクトル**と、**物体の、内部を、通った、出口の位置・法線**が、必要です。

### 近似の方法

| 方法 | 内容 | 精度 |
| --- | --- | --- |
| **背面の法線を、使う**（Wyman、2005） | 1. 背面の、**深度と、法線**を、テクスチャに描く。2. 前面で、**入口の屈折**を計算し、**背面までの距離**を推定する。3. **出口の位置と、背面の法線**で、**2 回目の、屈折**を計算する | **凸な形**で、よく合う |
| **解析的な形** | 球、箱に対して、レイと、形の、交差を、数式で、解く | 完全（形が、単純なら） |
| **レイトレーシング** | 実際に、光線を、追跡する | 完全。**重い** |

Wyman（2005）の、**画像空間の、近似**は、次のとおりです。

1. 物体の、**背面**を、描いて、**深度（視点からの、距離）と、法線**を、テクスチャに、保存する
2. 前面の、画素で、**入口の屈折ベクトル** `T₁` を、`refract(V, N_front, 1/n)` で、求める
3. 物体の**厚み** `d`（前面と背面の、深度の差）から、**出口の位置**を、`P_out ≈ P_front + T₁ × d` と、推定する
4. 出口の位置の、**背面の法線** `N_back` で、**2 回目の屈折**を、`T₂ = refract(T₁, −N_back, n)` で、求める
5. `T₂` の、方向に、シーンを、サンプルする（画面空間の、ずらし）

```hlsl
// 厚いガラスの、2 回屈折（Wyman 2005 の考え方）。
float3 V = normalize(input.world_position - g_camera_position);
float3 N_front = normalize(input.world_normal);

// ① 入口の屈折
float3 T1 = refract(V, N_front, 1.0 / g_ior);

// ② 背面までの距離（厚み）。背面の深度から。
float thickness = ThicknessFromBackDepth(input);

// ③ 出口の位置を、推定
float3 P_out = input.world_position + T1 * thickness;

// ④ 出口での、背面の法線で、2 回目の屈折
float3 N_back = FetchBackNormal(P_out);                       // 背面の法線テクスチャから
float3 T2 = refract(T1, -N_back, g_ior);
if (dot(T2, T2) < 1e-5) T2 = reflect(T1, -N_back);            // 全反射したら、反射させる（内部反射）

// ⑤ T2 の向きで、シーンを読む（出口の位置から、T2 の向きに、少し進んだ点を、画面に投影）
float3 sample_pos = P_out + T2 * g_refract_distance;
float2 uv = ProjectToScreenUV(sample_pos);
float3 refracted = g_scene_copy.Sample(g_linear_clamp, uv).rgb;
```

`refract` が、ゼロ ベクトルを返したときは、**全反射**です。**反射の向き**で、代用します（内部反射の、1 回分の、近似）。

## 凹んだ形、複雑な形

背面を、1 層だけ、使う近似は、**凸な形**（視線が、入口と出口で、1 回ずつ通る）を、前提にしています。**凹んだ形**（コップ、ドーナツ、複雑な彫像）では、**視線が、複数回、通る**ので、**うまく**いきません。

| 形 | 対応 |
| --- | --- |
| 凸（球、瓶、宝石の、単純なカット） | 背面の法線を使う近似で、よい |
| 軽く、凹む | 近似の、誤差を、**許容** |
| 強く、凹む、複雑 | **レイトレーシング**、または、**事前に、焼いた、キューブマップ**（物体の、内部の、屈折を、焼く） |
| 宝石（ダイヤモンド） | **内部の、複数回の反射**が、見た目の本質。**キューブマップに、焼く**、**または、専用の、トリック**（[Dispersion](dispersion.md) と組み合わせる） |

## 厚みと、薄さの、中間

ほとんどの、ゲームの、ガラス（コップ、瓶、窓）は、**薄い壁**の、**空洞**です。

| 物 | 扱い |
| --- | --- |
| ガラスの、コップ | **薄い壁**として、扱う（画面空間の、小さなずらし + フレネル + 厚みによる色）。**中の、水**は、別（水のシェーダー） |
| ワインの、ボトル | 壁は、薄いが、**中の液体**が、屈折を、起こす。**液体を、別メッシュ**として、**厚い**ガラスの、近似で |
| 魚の、水槽 | 水が、**大きな、塊**。**水の、体積**として、扱う（[Water](../../water/index.md)） |
| 氷の、塊 | **厚い**。内部の、散乱、屈折。**厚み**と、**ぼかし**で、近似（[Thickness and Color](thickness-color.md)） |

''', before="## よくあるミス")
pg.Refs("translucency/refraction/thin-thick.md", [WYMAN05, SOUSA, HECHT, RTR])

# ---------------------------------------------------------------- boundary
pg.Dedup("translucency/refraction/boundary.md")
pg.Add("translucency/refraction/boundary.md", '''
## 画面空間の、屈折は、**境界**で、破綻する

屈折を、**画面のコピー**の、**ずらし**で、表現する方法（[Screen-Space Refraction](screen-space.md)）は、**簡単で、速い**反面、**ガラスの、境界**（輪郭の、まわり）で、**いくつかの、破綻**を、起こします。

## 問題 1：手前の物が、にじむ

屈折で、**ずらして、読む位置**が、**ガラスの、手前にある物**（ガラスの前に、立っている人）に、当たると、その**色が、ガラスの中**に、**にじみ**ます。

```text
ガラス（背後を、屈折）
   ┃
 人 ┃    ← 人が、ガラスの、手前にいる
   ┃
ずらした先が、人にかかると、人の色が、ガラスの中に出てくる（本来は、人は、ガラスの前にいるので、ガラスの中には、映らない）
```

### 対策：深度で、チェックする

**ずらした先の、深度**が、**ガラスより、手前**なら、**ずらさず**に、**元の位置**を、読みます。

```hlsl
float scene_depth = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, refract_uv).r);
float glass_depth = LinearizeDepth(input.position.z);
if (scene_depth < glass_depth) refract_uv = screen_uv;
```

**完全には、解決しません**。境界の、**1 画素の、幅**で、**不連続**が、残ります。

### より良い対策：マスクを、持つ

**ガラスの、手前にある物**を、**別の、テクスチャ（マスク）**に、記録しておく方法です。**屈折する物を描く前**に、**ガラスより、手前の物**を、**ステンシル**や、**別のレンダー ターゲット**に、描いておきます。

| 方法 | 内容 |
| --- | --- |
| 深度の、チェックのみ | 簡単。**境界で、少し、にじむ** |
| 手前の、物を、マスク | **正確**。ただし、**描画の順序**（手前の物を先に、別に描く）が、複雑 |
| 2 回に、分けて描く | ガラスの**奥の物**を、描いて、コピーし、ガラスを描いてから、**手前の物**を、描く（**描画順を、変える**） |

## 問題 2：画面の端

ずらした UV が、**画面の外**に、出ることがあります。画面の外の、情報は、**無い**ので、**端の色が、引き伸ばされた**見た目になります。

| 対策 | 内容 |
| --- | --- |
| ずらし量を、**端で、弱める** | 画面の端に、近づくほど、ずらしを、小さくする |
| **画面より、少し大きく、描く** | 画面より、広い範囲を、レンダリングして、端でも、情報が、あるようにする（コストが、増える） |
| 気にしない | 薄い、ガラスは、ずらしが、小さく、**ほぼ、目立たない** |

```hlsl
// 画面の端（0〜10%）で、ずらし量を、弱める。
float2 edge_dist = min(screen_uv, 1.0 - screen_uv);
float edge_fade = saturate(min(edge_dist.x, edge_dist.y) / 0.1);
offset *= edge_fade;
```

## 問題 3：ガラスの、**中の、ガラス**（重なり）

**ガラスの向こうに、別のガラス**があると、**コピーが、1 枚**しかないので、**向こうの、ガラスの屈折**が、**手前のガラスの、屈折に、反映されません**。向こうの、ガラスは、**まだ、描かれていない**（または、描かれていても、コピーに、含まれない）ためです。

| 対策 | 内容 |
| --- | --- |
| **奥から手前の順**に描く | 奥のガラスを、先に描いて、**コピーを更新**し、手前のガラスを、描く。**ガラスごとに、コピー**が、必要（重い） |
| ガラスが、**重ならない**ように、設計する | レベルの、設計で、避ける |
| **不透明の、ガラス**として、**近似** | 2 枚目以降は、ブレンド（屈折なし） |

## 問題 4：ガラスの縁の、**黒い線**・**ハロー**

屈折で、ずらした先が、**ガラスの、縁**の、**外側**（背景）を、読むとき、**縁が、にじむ**ことが、あります。**アンチエイリアス**（MSAA、TAA）で、**縁の画素**が、**ガラスと背景の、混ざった色**になると、**屈折の、読み先が、ずれて**、**縁が、輝いたり、暗くなります**。

| 対策 | 内容 |
| --- | --- |
| 縁で、**屈折を、弱める** | 法線が、**視線に、垂直に近い**（縁）ほど、ずらし量を、小さくする（`saturate(dot(N, V))` を、掛ける） |
| **TAA** | 縁の、ちらつきを、時間方向に、平均する |

```hlsl
// 縁（法線が、視線に垂直）では、屈折を弱める。
float facing = saturate(dot(normal, view));
offset *= facing;
```

## 問題 5：水面と、地形が、交わる、境目

水や、ガラスが、**地形（不透明な物）と、交わる線**では、**ずらした先**が、**ガラスの、前後の、どちらか**で、**大きく、違う結果**になります。**深度の、チェック**で、**ごまかし**ますが、**境界線が、ギザギザ**に、なることがあります。

| 対策 | 内容 |
| --- | --- |
| 境界で、**アルファを、フェード** | 深度の差が、小さい所で、屈折の、強さを、下げる（[Soft Particles](../blending-sorting/soft-particles.md) と同じ考え方） |
| 境界に、**泡や、縁の効果**を、重ねる | 水の場合、岸の、泡で、**境目を、隠す**（[Shore Foam: Depth Difference](../../water/shore-foam/shore-depth.md)） |

## まとめ：境界の、扱い

| 境界の、問題 | 対策 |
| --- | --- |
| 手前の物が、にじむ | 深度チェック、マスク |
| 画面の端 | 端で、屈折を、弱める |
| ガラスの中の、ガラス | 奥から手前に描く、ガラスごとに、コピー |
| 縁の、にじみ | 縁で、屈折を、弱める、TAA |
| 地形との、交差 | アルファの、フェード、泡 |

**どれも、完全な解決は、ない**ので、**「目立たないように、ごまかす」**ことが、実際の、仕事です。**屈折の、強さを、控えめに**する（ずらし量が、小さいほど、破綻も、目立たない）のが、**最も、効果が、大きい**対策です。

''', before="## よくあるミス")
pg.Refs("translucency/refraction/boundary.md", [SOUSA, WYMAN05, MITTRING, RTR])

# ---------------------------------------------------------------- implementation
pg.Dedup("translucency/refraction/implementation.md")
pg.Add("translucency/refraction/implementation.md", '''
## 屈折の、描画パイプライン

屈折する物（ガラス、水）を、描くには、**不透明な物を、先に描き**、**その結果（色と深度）を、読みながら**、屈折する物を、描きます。

```text
① シャドウ マップなどの、準備パス
② 不透明な物を描く                     → シーンの色（レンダー ターゲット）と、深度
③ シーンの色を、コピーする             → 屈折用の、テクスチャ
④ （必要なら）シーンの色の、ミップマップを作る  → すりガラスの、ぼかし用
⑤ 屈折する物を描く（奥から手前）        → コピーを、読み、ずらして、シーンの色に、書き込む
⑥ 半透明（パーティクルなど）を、描く
⑦ ポストプロセス
```

## DirectX 11 での、実装

### ① リソースを、作る

```cpp
// シーンの色: レンダー ターゲットとして、描き、シェーダー リソースとしても、読む。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width; desc.Height = height;
desc.MipLevels = 0;                                     // 全ミップ（すりガラスの、ぼかし用）
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
desc.SampleDesc.Count = 1;                               // MSAA を使うなら、別途リゾルブが必要
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;      // GenerateMips を使う
device->CreateTexture2D(&desc, nullptr, &scene_color);
device->CreateTexture2D(&desc, nullptr, &scene_copy);    // コピー先（屈折用）
```

### ② 毎フレームの、処理

```cpp
// ② 不透明の描画
context->OMSetRenderTargets(1, scene_color_rtv.GetAddressOf(), depth_dsv.Get());
DrawOpaque();

// ③ シーンの色を、コピー（MSAA なら、ResolveSubresource を使う）
context->CopySubresourceRegion(scene_copy.Get(), 0, 0, 0, 0, scene_color.Get(), 0, nullptr);

// ④ ミップを作る（すりガラス、粗い屈折のため）
context->GenerateMips(scene_copy_srv.Get());

// ⑤ 屈折する物を描く（深度は、読み取り専用の DSV にして、深度 SRV と、共存させる）
context->OMSetRenderTargets(1, scene_color_rtv.GetAddressOf(), depth_dsv_readonly.Get());
ID3D11ShaderResourceView* srvs[2] = {scene_copy_srv.Get(), depth_srv.Get()};
context->PSSetShaderResources(0, 2, srvs);
DrawRefractive();
```

| 手順 | 理由 |
| --- | --- |
| コピーを作る | 読み書きを、**同じ、テクスチャで、同時に、できない** |
| `GenerateMips` | すりガラスや、粗い面の、**ぼかし**を、ミップで安く作る |
| 読み取り専用の DSV | **深度を、読み取って、深度テストは、する**、**書き込みは、しない**。同じ、深度テクスチャを、SRV としても、読める（[Color by Water Depth](../../water/shading/depth-color.md)） |

## コスト

| 処理 | コスト（1080p の目安） |
| --- | --- |
| シーンの色の、コピー | 0.05〜0.1 ms（帯域） |
| `GenerateMips` | 0.1〜0.3 ms |
| 屈折する物の、描画 | 画面を、占める面積に、比例。**テクスチャ読み込み 1〜3 回**/画素 |
| 画面全体を、覆う、ガラス（水面） | 全画素が、屈折の、テクスチャ読み込みを、行う。**水の描画は、数 ms** |

**コピーは、1 フレームに、1 回**で、済ませます。**屈折する物が、複数**あっても、**同じコピー**を、読みます（**物同士の、屈折が、反映されない**制約と、引き換え）。

### 節約の、工夫

| 工夫 | 内容 |
| --- | --- |
| **低解像度**のコピー | コピーを、画面の半分の、解像度に。ぼかす、屈折（すりガラス）には、十分 |
| 屈折する物が、**無いとき**は、コピーを、**省く** | 画面に、ガラスが、映っていないフレームでは、コピーも、`GenerateMips` も、不要 |
| **範囲を、限る** | ガラスの、周りの、**矩形だけ**、コピーする（`CopySubresourceRegion` の、範囲指定） |
| 遠くの、ガラスは、**屈折なし** | 遠くでは、ずれが、小さい。**反射と、色だけ**で、描く |

## シェーダーの、構成

屈折する物の、シェーダーは、**複数の、要素の合成**です。

```hlsl
float4 main(PSInput input) : SV_Target {
  float3 N = normalize(input.world_normal);
  float3 V = normalize(g_camera_position - input.world_position);

  // ① 屈折（画面のコピーを、ずらして、読む）
  float3 refracted = SampleRefraction(input, N, V);             // Screen-Space Refraction
  // ② 色（厚みによる、吸収）
  float thickness = ComputeThickness(input);
  refracted *= exp(-g_absorption * thickness);                  // Thickness and Color
  // ③ 反射（環境マップ、SSR）
  float3 reflected = SampleReflection(reflect(-V, N), g_roughness);
  // ④ フレネル
  float F = FresnelSchlick(saturate(dot(N, V)), g_f0);
  // ⑤ 合成
  float3 color = lerp(refracted, reflected, F);
  // ⑥ スペキュラー（光源のハイライト）
  color += SpecularHighlight(N, V, g_light_dir, g_light_color, g_roughness);
  return float4(color, 1.0);
}
```

最終的に、**ブレンドせず**に、**不透明として**、書き込みます（背景の色は、すでに、**屈折の、読み込みの中**に、含まれている）。**アルファ ブレンドは、不要**です。

## 深度の、扱い

屈折する物は、**深度を、書き込む**か、どうかを、決めます。

| 設定 | 内容 |
| --- | --- |
| 書き込む | 屈折する物の、**後ろに、描く半透明**（パーティクル）が、**隠される**。ガラスの、向こうの、煙は、見えない。**正しい**場合が多い |
| 書き込まない | 屈折する物の**向こうに**、あとから、描く物が、**ガラスを、貫いて**見える。ガラスの、向こうの、パーティクルが、**ガラスの上に、重なって**見える（**間違い**） |

**通常は、深度を、書き込みます**（不透明の物として、扱うので）。**ガラスの、向こうの、半透明**は、**ガラスの前に、先に、描いて**、**コピーに、含めて**おきます。

## 描画の、順番

| 順 | 描くもの |
| --- | --- |
| 1 | 不透明 |
| 2 | **ガラスの、向こうに、見える、半透明**（パーティクル、植物の、葉） |
| 3 | コピー |
| 4 | **屈折するもの**（ガラス、水） |
| 5 | ガラスの**手前に**、見える、半透明 |

**屈折する物の、後ろにある、半透明**を、**コピーの前に**、描くのが、ポイントです。

''', before="## よくあるミス")
pg.Refs("translucency/refraction/implementation.md", [SOUSA, MITTRING, D3D11_COPY, "Microsoft Learn, \"ID3D11DeviceContext::GenerateMips\""])
pg.Refs("translucency/refraction/index.md", [SOUSA, WYMAN05, SCHLICK, WALTER, HECHT])
pg.Refs("translucency/index.md", [RTR, SOUSA, "McGuire, Bavoil, \"Weighted Blended Order-Independent Transparency\", Journal of Computer Graphics Techniques, Vol. 2, No. 2, 2013", "Wyman, McGuire, \"Hashed Alpha Testing\", Symposium on Interactive 3D Graphics and Games 2017"])
print("ok")
