import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

ZHUKOV = '''Zhukov, Iones, Kronin, "An Ambient Light Illumination Model", Rendering Techniques '98（Eurographics Workshop on Rendering 1998）（obscurance の原典）'''
IONES = '''Iones, Krupkin, Sbert, Zhukov, "Fast, Realistic Lighting for Video Games", IEEE Computer Graphics and Applications, 23(3), 2003'''
LANDIS = '''Landis, "Production-Ready Global Illumination", SIGGRAPH 2002 Course 16（ambient occlusion の、映画制作での、使われ方）'''
MITTRING = '''Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games'''
FILION = '''Filion, McNaughton, "StarCraft II: Effects & Techniques", SIGGRAPH 2008, Advances in Real-Time Rendering in 3D Graphics and Games（深度バッファによる、SSAO）'''
BAVOIL = '''Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks'''
ALCHEMY = '''McGuire, Osman, Bukowski, Hennessy, "The Alchemy Screen-Space Ambient Obscurance Algorithm", High-Performance Graphics 2011'''
SAO = '''McGuire, Mara, Luebke, "Scalable Ambient Obscurance", High-Performance Graphics 2012'''
GTAO = '''Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice'''
XEGTAO = '''Intel, XeGTAO（GitHub: GameTechDev/XeGTAO、GTAO の、HLSL 実装）'''
TOMASI = '''Tomasi, Manduchi, "Bilateral Filtering for Gray and Color Images", ICCV 1998'''
KOPF = '''Kopf, Cohen, Lischinski, Uyttendaele, "Joint Bilateral Upsampling", ACM Transactions on Graphics (SIGGRAPH 2007), 26(3)'''
KARIS = '''Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（時間蓄積・履歴のクランプ）'''
SALVI = '''Salvi, "An Excursion in Temporal Supersampling", GDC 2016（分散クリッピング）'''
GEORGIEV = '''Georgiev, Fajardo, "Blue-Noise Dithered Sampling", SIGGRAPH 2016 Talks'''
HEITZ19 = '''Heitz, Belcour, Ostromoukhov, Coeurjolly, Iehl, "A Low-Discrepancy Sampler that Distributes Monte Carlo Errors as a Blue Noise in Screen Space", SIGGRAPH 2019 Talks'''
SCHIED = '''Schied et al., "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017'''
BAVOIL_JANSEN = '''Bavoil, Jansen, "Particle Shadows & Cache-Efficient Post-Processing", GDC 2013（デインターリーブ テクスチャリング）'''
RITSCHEL = '''Ritschel, Grosch, Seidel, "Approximating Dynamic Global Illumination in Image Space", Symposium on Interactive 3D Graphics and Games (I3D) 2009（SSDO）'''
CRASSIN = '''Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011)'''
CRASSIN12 = '''Crassin, Green, "Octree-Based Sparse Voxelization Using the GPU Hardware Rasterizer", OpenGL Insights, Chapter 22, 2012'''
WRIGHT = '''Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Unreal Engine 4 の DFAO）'''
DXR = '''Microsoft, "DirectX Raytracing (DXR) Functional Spec"'''
BARRE = '''Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019'''
LAGARDE = '''Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（スペキュラ オクルージョン）'''
LEARN = '''de Vries, "SSAO", LearnOpenGL（半球カーネル・ノイズ・バイアス・範囲チェックの、実装解説）'''
NVHBAO = '''NVIDIA, "HBAO+"（NVIDIA GameWorks、公開ドキュメント）'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）'''
REINBOTHE = '''Reinbothe, Boubekeur, Alexa, "Hybrid Ambient Occlusion", Eurographics 2009 Areas Papers'''
KAJALIN = '''Kajalin, "Screen Space Ambient Occlusion", ShaderX7, 2009'''

R = pg.Refs
R("ao/index.md", [LANDIS, ZHUKOV, MITTRING, BAVOIL, GTAO, RTR])
R("ao/comparison.md", [MITTRING, BAVOIL, ALCHEMY, SAO, GTAO, RTR])
R("ao/ssao-crytek.md", [MITTRING, FILION, KAJALIN, LEARN])
R("ao/ssao-hemisphere.md", [LEARN, MITTRING, FILION, KAJALIN, RTR])
R("ao/hbao.md", [BAVOIL, NVHBAO, RTR])
R("ao/hbao-plus.md", [NVHBAO, BAVOIL_JANSEN, BAVOIL])
R("ao/gtao.md", [GTAO, XEGTAO, BAVOIL, LAGARDE])
R("ao/alchemy-ao.md", [ALCHEMY, SAO, ZHUKOV])
R("ao/sao.md", [SAO, ALCHEMY, BAVOIL])
R("ao/theory/index.md", [LANDIS, ZHUKOV, IONES, RTR])
R("ao/theory/from-rendering-equation.md", [LANDIS, RTR, "Kajiya, \"The Rendering Equation\", SIGGRAPH 1986"])
R("ao/theory/obscurance.md", [ZHUKOV, IONES, LANDIS])
R("ao/theory/approximation.md", [MITTRING, BAVOIL, ALCHEMY, GTAO])
R("ao/theory/screen-space-visibility.md", [MITTRING, FILION, BAVOIL, REINBOTHE])
R("ao/theory/usage-misconceptions.md", [LANDIS, GTAO, LAGARDE, RTR])
R("ao/artifacts/index.md", [MITTRING, BAVOIL, SAO, GTAO])
R("ao/artifacts/halo.md", [MITTRING, BAVOIL, ALCHEMY, GTAO])
R("ao/artifacts/self-occlusion.md", [BAVOIL, ALCHEMY, SAO, XEGTAO])
R("ao/artifacts/edge-thin.md", [MITTRING, GTAO, SAO])
R("ao/artifacts/noise-flicker.md", [GEORGIEV, HEITZ19, KARIS, SALVI])
R("ao/artifacts/application-mistakes.md", [GTAO, LAGARDE, RTR])
R("ao/filtering/index.md", [TOMASI, KOPF, KARIS, BAVOIL_JANSEN])
R("ao/filtering/bilateral-blur.md", [TOMASI, SAO, SCHIED])
R("ao/filtering/noise-pattern.md", [GEORGIEV, HEITZ19, BAVOIL_JANSEN, LEARN])
R("ao/filtering/pipeline.md", [SAO, GTAO, BAVOIL_JANSEN, KARIS])
R("ao/filtering/temporal.md", [KARIS, SALVI, SCHIED, GTAO])
R("ao/filtering/upsample.md", [KOPF, TOMASI, SAO, BAVOIL_JANSEN])
R("ao/world-space/index.md", [WRIGHT, CRASSIN, DXR, BARRE])
R("ao/world-space/comparison.md", [WRIGHT, CRASSIN, BARRE, RTR])
R("ao/world-space/dfao.md", [WRIGHT, "Quilez, \"Sphere soft shadows / Distance functions\"（距離関数の、基礎。iquilezles.org）", CRASSIN])
R("ao/world-space/rtao.md", [DXR, BARRE, SCHIED, "Pharr, Jakob, Humphreys, \"Physically Based Rendering: From Theory to Implementation\", 4th Edition, MIT Press, 2023（モンテカルロ積分、コサイン重みのサンプリング）"])
R("ao/world-space/vxao.md", [CRASSIN, CRASSIN12, "NVIDIA, \"VXAO\"（NVIDIA GameWorks）"])

# ---------------------------------------------------------------- additions on thin pages
pg.Add("ao/theory/approximation.md", '''
## 3 つの近似を、コードで比べる

### ① サンプルを撒く：コサイン分布の半球サンプリング

```hlsl
// コサイン重みの分布で、半球の方向を 1 つ選ぶ（ローカル座標。z が法線）。pdf = cosθ / π。
float3 CosineSampleHemisphere(float2 u) {
  float r = sqrt(u.x);
  float phi = 2.0 * 3.14159265 * u.y;
  return float3(r * cos(phi), r * sin(phi), sqrt(max(0.0, 1.0 - u.x)));
}
```

円盤の上に一様に点を取り、それを半球に持ち上げると、`cosθ` に比例した密度になります。AO の式の `(n·ω)` と、モンテカルロ法の `1/pdf` が打ち消し合い、残るのは可視性 V の平均だけです。

```hlsl
// 可視性を数えて、割合にする。Visible() は、方向ごとの遮蔽判定（レイ、または、深度の比較）。
float ao = 0.0;
for (uint i = 0; i < kSamples; ++i) {
  float3 w = TangentToWorld(CosineSampleHemisphere(Hammersley(i, kSamples)), normal);
  ao += Visible(position, w) ? 1.0 : 0.0;
}
ao /= kSamples;
```

これが、Crytek 系や半球 SSAO の、骨格です。サンプル数が少ないぶん、ノイズになります。

### ② 水平線を探す：スライスごとに解析的に積分する

```hlsl
// 1 本のスライスで、左右の水平線の角度 h1, h2（法線から測る）が分かれば、可視な弧の積分は式で出る（GTAO）。
float IntegrateArcCosWeighted(float h1, float h2, float n) {
  float cos_n = cos(n);
  float sin_n = sin(n);
  return 0.25 * (-cos(2.0 * h1 - n) + cos_n + 2.0 * h1 * sin_n
               + -cos(2.0 * h2 - n) + cos_n + 2.0 * h2 * sin_n);
}
```

水平線の角度を 2 つ探すだけで、そのスライスの可視度が、サンプルを撒かずに、閉じた式で得られます。サンプル点の数は、水平線を探す歩数だけで済みます（[GTAO](../gtao.md)）。

### ③ 式で近似する：遮蔽物の点ごとに寄与を足す

```hlsl
// Alchemy 型: 周りの点 q が p を遮る量を、ベクトル v = q - p だけで書き、足し合わせる。
float3 v = q - p;
float vv = dot(v, v);
float vn = dot(v, n);
occlusion += max(0.0, vn + p_depth * kBeta) / (vv + kEpsilon);
```

法線の向きにある点ほど（`vn` が大きい）、近い点ほど（`vv` が小さい）強く遮る、という形です。方向を探さないので軽く、ただし、物理的な厳密さは、水平線の方式に劣ります。

''', before="## よくあるミス")

pg.Add("ao/theory/screen-space-visibility.md", '''
## 深度バッファから、サンプル点の可視性を求める

### 再構成：深度から、ビュー空間の位置へ

```hlsl
// 深度（0〜1）と uv から、ビュー空間の位置を復元する（右手系、前は −Z）。
float3 ViewPosition(float2 uv, float depth) {
  float4 clip = float4(uv * float2(2.0, -2.0) + float2(-1.0, 1.0), depth, 1.0);
  float4 view = mul(clip, g_inv_proj);
  return view.xyz / view.w;
}
```

AO の計算は、ほぼすべてビュー空間で行います。カメラが原点で、深度の比較が、単純になるからです。

### サンプル点を投影して、深度と比べる

```hlsl
// 点 p の近くのサンプル点 s が、見えている面の奥にあるか。
float3 s = p + offset;                                              // offset は、法線の向きの半球内
float4 clip = mul(float4(s, 1.0), g_proj);
float2 uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
float scene_z = ViewPosition(uv, g_depth.SampleLevel(g_point_clamp, uv, 0)).z;   // その画素で見えている面の、z
bool occluded = scene_z >= s.z + g_bias;                            // −Z が前なので、z が大きいほど手前。面が手前にあれば、遮蔽
```

サンプル点 `s` をカメラの射影で画面に落とし、その画素に見えている面の深度と比べます。面が `s` より手前なら、`s` はその面の裏にあるので、遮られていると数えます。`g_bias` は、同じ面の上の点を、自分で遮ってしまわないための、わずかな余裕です。

### 範囲チェック：遠い面を、遮蔽に数えない

```hlsl
// 手前にあるのが、ずっと手前の別の物体（柱の向こうの壁など）なら、遮蔽に数えない。
float range = smoothstep(0.0, 1.0, g_radius / abs(p.z - scene_z));
occlusion += occluded ? range : 0.0;
```

深度の差が半径より大きい場合、その面は、`p` の周りの遮蔽物ではなく、ただ手前を横切っているだけです。放置すると、物体の輪郭に沿って、暗いハローが出ます（[Halo](../artifacts/halo.md)）。

## D3D11 での、深度の準備

```cpp
// 深度は、typeless で作り、DSV（書き込み）と SRV（AO の読み込み）の両方から見る。
D3D11_TEXTURE2D_DESC desc = {};
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
// DSV: DXGI_FORMAT_D32_FLOAT、SRV: DXGI_FORMAT_R32_FLOAT
```

AO のパスを走らせる前に、深度の DSV を外してから SRV として束ねます（同じリソースを、書き込みと読み込みで同時に束ねない）。

''', before="## よくあるミス")

pg.Add("ao/world-space/vxao.md", '''
## ボクセル化を、D3D11 で組む

### 3D テクスチャと UAV

```cpp
// 占有度を持つ、ボクセル格子（128³、1 チャンネル）。ピクセル シェーダーから UAV で書き、後でミップを作る。
D3D11_TEXTURE3D_DESC desc = {};
desc.Width = desc.Height = desc.Depth = 128;
desc.MipLevels = 0;                                                    // 全ミップ（円錐トレースで使う）
desc.Format = DXGI_FORMAT_R8_UNORM;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS | D3D11_BIND_RENDER_TARGET;
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;
device->CreateTexture3D(&desc, nullptr, &voxel_tex);
```

ピクセル シェーダーから UAV に書き込むために、レンダー ターゲットは、無しにして、`OMSetRenderTargetsAndUnorderedAccessViews` で、UAV だけを束ねます。ビューポートは、格子の解像度（128×128）に合わせます。

### 三角形の向きを選んで、ラスタライズする

```hlsl
// ジオメトリ シェーダー: 三角形の法線が、最も大きい軸（X / Y / Z）に向けて、直交投影し直す。面積が最大になる軸で描くと、取りこぼしが少ない。
[maxvertexcount(3)]
void VoxelizeGS(triangle VSOut input[3], inout TriangleStream<GSOut> stream) {
  float3 n = abs(cross(input[1].world - input[0].world, input[2].world - input[0].world));
  uint axis = (n.x > n.y && n.x > n.z) ? 0 : (n.y > n.z ? 1 : 2);
  for (uint i = 0; i < 3; ++i) {
    GSOut o;
    o.world = input[i].world;
    float3 p = (input[i].world - g_voxel_origin) / g_voxel_extent * 2.0 - 1.0;   // 格子の範囲を −1〜1 に
    o.position = float4(axis == 0 ? p.yzx : (axis == 1 ? p.zxy : p.xyz), 1.0);  // 軸ごとに、向きを回す
    stream.Append(o);
  }
}
```

三角形を、その面積が最大に見える軸から描くと、ラスタライザーが、三角形をほぼ漏れなく、画素（= ボクセル）に分けてくれます。細い三角形の取りこぼしは、保守的ラスタライズ（D3D11.3 / D3D12 の機能）で防げます。

```hlsl
// ピクセル シェーダー: 当たったボクセルの占有度を 1 にする。
RWTexture3D<float> g_voxel : register(u1);
void VoxelizePS(GSOut input) {
  int3 voxel = (int3)((input.world - g_voxel_origin) / g_voxel_extent * 128.0);
  g_voxel[voxel] = 1.0;
}
```

ここで書くのは、占有度だけです。色や法線まで保存すると、GI 用のボクセルになります（[Voxel GI](../../gi/voxel-gi.md)）。

### ミップを作る：占有度の平均

```cpp
context->GenerateMips(voxel_srv.Get());   // 8 つのボクセルの平均。粗いミップほど、「部分的に埋まっている」を表す
```

円錐の直径が大きくなるほど、粗いミップを読みます。ミップの値は、領域のうち、埋まっている割合なので、円錐の中の、遮蔽の割合として、そのまま使えます。

''', before="## よくあるミス")

pg.Add("ao/world-space/index.md", '''
## 3 つの方式の、距離の測り方

| 方式 | 何を持つか | 空間の問い | 更新 |
| --- | --- | --- | --- |
| RTAO | 三角形の BVH | 「この方向のレイは、近くで何かに当たるか」を、直接調べる | TLAS を毎フレーム更新 |
| DFAO | メッシュごとの、距離場（SDF） | 「この点から、どれだけ進んでも、物に当たらないか」を、距離で知る | 動く物は、変換だけ。メッシュ自体の変形は不可 |
| VXAO | ボクセル格子 | 「この円錐の中は、どれだけ埋まっているか」を、ミップで知る | 動く物を、毎フレーム再ボクセル化 |

どれも、**画面の外や、手前の物の裏側の遮蔽**を扱える点が、スクリーン空間の AO との違いです（[Screen-Space Visibility](../theory/screen-space-visibility.md)）。そのかわり、ジオメトリをもう 1 つ（BVH、SDF、ボクセル）持つコストと、手間がかかります。

''', before="## よくあるミス")

pg.Add("ao/artifacts/index.md", '''
## 原因で、見分ける

| 見た目 | 主な原因 | 詳しく |
| --- | --- | --- |
| 物体の周りの、白い／黒い縁 | 範囲チェックの欠如、深度の不連続 | [Halo](halo.md) |
| 平らな面が、縞や斑になる | サンプル点が、自分の面に当たる | [Self-Occlusion](self-occlusion.md) |
| 画面端で、AO が消える／細い物に付かない | 画面外の情報が、無い。深度が、細い物を拾えない | [Screen Edges and Thin Objects](edge-thin.md) |
| ざらざら、縞（バンディング）、ちらつき | サンプル数が少ない。ノイズの並びが、規則的／毎フレーム違う | [Noise, Banding and Flicker](noise-flicker.md) |
| 光の当たる所まで、暗い | AO を、直接光にも掛けている／二重に掛けている | [Application Mistakes](application-mistakes.md) |

見た目から原因を当てるには、AO の生の出力（ぼかし前）と、ぼかし後を、別々に画面に出して見るのが近道です。ざらつきはぼかしで消え、ハローや自己遮蔽はぼかしでは消えません。

''', before="## よくあるミス")
print("ok")
