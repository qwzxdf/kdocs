import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

WYMAN17 = '''Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017'''
CASTANO = '''Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正して、カバレッジを保つ）'''
BAYER = '''Bayer, "An Optimum Method for Two-Level Rendition of Continuous-Tone Pictures", IEEE International Conference on Communications, 1973（ベイヤー行列によるディザ）'''
JIMENEZ = '''Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（Interleaved Gradient Noise）'''
ULICHNEY = '''Ulichney, "Dithering with Blue Noise", Proceedings of the IEEE, Vol. 76, No. 1, 1988'''
GEORGIEV = '''Georgiev, Fajardo, "Blue-Noise Dithered Sampling", SIGGRAPH 2016 Talks'''
PORTER = '''Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）'''
SMITH = '''Smith, "Image Compositing Fundamentals", Microsoft Technical Memo 4, 1995（乗算済みアルファ）'''
LORACH = '''Lorach, "Soft Particles", NVIDIA White Paper, 2007'''
D3D11_BLEND = '''Microsoft Learn, "D3D11_BLEND_DESC"（`AlphaToCoverageEnable`、`D3D11_RENDER_TARGET_BLEND_DESC`）'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明と、アルファ合成の章）'''

# ---------------------------------------------------------------- alpha to coverage
pg.Dedup("translucency/alpha-test/alpha-to-coverage.md")
pg.Add("translucency/alpha-test/alpha-to-coverage.md", '''
## アルファ テストの、縁が、ギザギザになる理由

`clip(alpha - 0.5)` は、**画素の中心**で、アルファを調べて、残すか捨てるかを、決めます。**縁の画素は、残るか、消えるかの、二択**なので、**階段状の、ジャギー**になります。MSAA（マルチサンプル アンチエイリアス）を使っていても、**ピクセル シェーダーが、1 画素に 1 回しか、走らない**ので、`clip` の結果は、**4 つのサンプルすべてに、同じ**ように、適用されます。**ポリゴンの縁**には、MSAA が効きますが、**テクスチャの、アルファの縁**には、効きません。

## Alpha to Coverage の仕組み

**Alpha to Coverage（A2C）**は、**ピクセル シェーダーが、出力したアルファ**を、**MSAA の、カバレッジ**（その画素の、**サンプルのうち、何個を、描くか**）に、**変換する**機能です。

| アルファ | 4x MSAA で、描かれるサンプル |
| --- | --- |
| 0.0 | 0 個（何も描かない） |
| 0.25 | 1 個 |
| 0.5 | 2 個 |
| 0.75 | 3 個 |
| 1.0 | 4 個（すべて描く） |

画素は、**サンプルごとの、描く・描かない**が、決まり、**解像（リゾルブ）**のとき、**サンプルが、平均**されます。結果、**アルファが 0.5 の画素は、半分の明るさ**で、混ざります。**縁が、なめらかな、ブレンド**に見えます。

```text
アルファ テスト                 Alpha to Coverage（4x MSAA）
████████                       ████████
████▀▀▀▀                       ████▓▒░·       ← 縁の画素が、段階的に、薄くなる
████                           ████
```

**深度を、書き込み**ながら、**縁が、なめらか**になる、**ソート不要**の、半透明表現です。

## DirectX 11 で、設定する

MSAA の、レンダー ターゲットと、深度バッファを、作り、**ブレンド ステートで、A2C を、有効にします**。

```cpp
// ① MSAA のレンダー ターゲット（4x）を作る。
D3D11_TEXTURE2D_DESC color_desc = {};
color_desc.Width = width; color_desc.Height = height;
color_desc.MipLevels = 1; color_desc.ArraySize = 1;
color_desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
color_desc.SampleDesc.Count = 4;                         // 4x MSAA
color_desc.SampleDesc.Quality = 0;
color_desc.Usage = D3D11_USAGE_DEFAULT;
color_desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&color_desc, nullptr, &msaa_color);
// 深度バッファも、SampleDesc.Count = 4 で作る。

// ② ブレンド ステートで、Alpha to Coverage を有効にする。
D3D11_BLEND_DESC blend = {};
blend.AlphaToCoverageEnable = TRUE;                      // ここが肝心
blend.IndependentBlendEnable = FALSE;
blend.RenderTarget[0].BlendEnable = FALSE;               // 通常のブレンドは、使わない
blend.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&blend, &a2c_blend_state);

const float factor[4] = {0, 0, 0, 0};
context->OMSetBlendState(a2c_blend_state.Get(), factor, 0xffffffff);
```

| 設定 | 内容 |
| --- | --- |
| `AlphaToCoverageEnable` | `TRUE`。ピクセル シェーダーの、**SV_Target の、アルファ**を、カバレッジに変換する |
| `BlendEnable` | `FALSE`。A2C は、ブレンドではなく、**サンプルの、描く・描かない**で、動く |
| MSAA | **必須**。MSAA が無い（サンプル 1 つ）と、A2C は、**アルファ テストと、ほぼ同じ**で、意味がない |

```hlsl
// ピクセル シェーダー: アルファを、そのまま出力する。clip は、使わない。
float4 main(PSInput input) : SV_Target {
  float4 color = g_albedo.Sample(g_linear_wrap, input.uv);
  return float4(color.rgb, color.a);        // color.a が、カバレッジに変換される
}
```

## アルファの、**シャープ化**

テクスチャの、アルファが、**なだらかな、勾配**を持つ（ぼやけた縁）と、A2C の効果で、**縁が、広く、ぼやけて**しまいます。**しきい値の周りの、狭い範囲だけ**を、段階的にして、ぴったりの縁を、作ります。

```hlsl
// アルファを、しきい値の周りで、鋭くする（画面上の、1 画素の幅に合わせて）。
float alpha = g_albedo.Sample(g_linear_wrap, uv).a;
float width = fwidth(alpha);                              // 画面の 1 画素あたりの、アルファの変化
alpha = saturate((alpha - 0.5) / max(width, 1e-4) + 0.5); // しきい値 0.5 を中心に、1 画素の幅だけ、なだらか
```

`fwidth(alpha)` は、**隣の画素との、アルファの差**です。これを、**縁のなだらかさの、幅**に使うと、**どの距離でも、縁が、ちょうど、1 画素ぶん、なだらか**になります。**近くで、ぼやけず**、**遠くで、ちらつかない**、定番の、書き方です。

## MSAA の、サンプル数と、段階

| MSAA | アルファの段階 | 縁の見え方 |
| --- | --- | --- |
| 2x | 3 段階 | まだ、ジャギーが、残る |
| 4x | 5 段階 | まずまず。標準 |
| 8x | 9 段階 | なめらか。メモリ、帯域が、増える |

**サンプル数が、少ない**と、アルファの、段階が、粗く、**縁に、縞（バンディング）**が、出ます。ディザで、ごまかす手法もあります（次の節）。

## バンディングを、隠す

4x では、**5 段階しか**、**アルファを、表現できません**。広い範囲で、**なだらかに、薄くなる**表現（フェード）では、**縞**が見えます。画素ごとに、**ランダムな、オフセット**を、アルファに足して、段階を、ディザで、ならします。

```hlsl
// 画素ごとの、ノイズで、アルファを、少しずらして、バンディングを、細かい点に変える。
float noise = InterleavedGradientNoise(input.position.xy);           // 0〜1（Jimenez 2014）
float alpha_dithered = saturate(alpha + (noise - 0.5) * (1.0 / 4.0)); // サンプル数の逆数だけ、揺らす
return float4(color.rgb, alpha_dithered);
```

```hlsl
// Interleaved Gradient Noise（Jimenez 2014）。画面座標から、安い式で、ノイズを作る。
float InterleavedGradientNoise(float2 screen_pos) {
  float3 magic = float3(0.06711056, 0.00583715, 52.9829189);
  return frac(magic.z * frac(dot(screen_pos, magic.xy)));
}
```

## A2C の、**注意点**

| 項目 | 内容 |
| --- | --- |
| MSAA が必要 | **ディファード レンダリング**では、MSAA が、重いので、使いにくい。**フォワード**向き |
| 他の、アルファ | A2C を使うと、ブレンド ステートが、占有される。**通常のアルファ ブレンドと、併用できない** |
| 色 | アルファ以外の、出力（色）は、通常どおり。カバレッジが、決まるだけ |
| ミップ | 遠くで、アルファが、薄くなる問題は、残る（[Foliage Translucency](../../terrain/vegetation/translucency.md)） |
| 重なり | 複数の、A2C の面が、**同じ画素に、重なる**と、**同じサンプルが、取り合い**になる。**重なりに、強くない**（アルファの合計が、1 を超えると、もう、描けない） |
| 動き | **TAA**を使うなら、A2C なしでも、**ハッシュ アルファ**（時間方向に、平均）で、同等のことが、できる（[Hashed Alpha](hashed-alpha.md)） |

## 使いどころ

| 対象 | A2C |
| --- | --- |
| 木の葉、草（フォワード + MSAA） | **最も、有効**（縁が、なめらか、ソート不要、深度書き込み可） |
| フェンス、金網 | 有効 |
| 髪の毛 | 有効（ただし、重なりが、多い。[Hair Transparency](../../skin-hair/hair/transparency.md)） |
| ガラス、水など、本当の半透明 | **不向き**（アルファを、段階的な、サンプルに、変換するだけで、混ざらない） |

''', before="## よくあるミス")
pg.Refs("translucency/alpha-test/alpha-to-coverage.md", [D3D11_BLEND, CASTANO, JIMENEZ, WYMAN17, RTR])

# ---------------------------------------------------------------- dither
pg.Dedup("translucency/alpha-test/dither.md")
pg.Add("translucency/alpha-test/dither.md", '''
## ディザリングとは

**ディザリング**は、**限られた段階しか、表現できないとき**に、**小さな点の、配置**で、**中間の濃さ**を、表現する方法です。新聞の、写真が、**黒い点の、大きさと密度**で、グレーを表すのと、同じです。

**透明の表現**に、使うと、**アルファ 0.5 を、画素の半分を描き、半分を捨てる**ことで、表します。**半透明のブレンドを使わず**、**深度を書き込み、ソートも不要**で、半透明に、見せられます。

## ディザ パターン

画素ごとに、**しきい値**を、決めておき、**アルファが、そのしきい値を、超えた画素だけ、描きます**。

```text
アルファ 0.25      0.50          0.75
□□□□              ■□■□          ■■■■
□■□□              □■□■          ■□■■
□□□□              ■□■□          ■■■■
□□□■              □■□■          ■■□■
```

### ベイヤー行列（Bayer）

古典的な、ディザ パターンです（Bayer、1973）。**規則的な、行列**で、しきい値を決めます。

```hlsl
// 4×4 のベイヤー行列。値は 0〜15。16 で割って、0〜1 のしきい値にする。
static const float kBayer4x4[16] = {
     0.0,  8.0,  2.0, 10.0,
    12.0,  4.0, 14.0,  6.0,
     3.0, 11.0,  1.0,  9.0,
    15.0,  7.0, 13.0,  5.0};

float BayerThreshold(float2 screen_pos) {
  uint2 p = uint2(screen_pos) & 3;                        // 画素の座標の、下位 2 ビット
  return (kBayer4x4[p.y * 4 + p.x] + 0.5) / 16.0;
}

// ディザ透明: アルファが、しきい値より小さい画素を、捨てる。
void DitherClip(float2 screen_pos, float alpha) {
  clip(alpha - BayerThreshold(screen_pos));
}
```

| 特徴 | 内容 |
| --- | --- |
| 規則的 | **格子状の、パターン**が、見える。近くで、見ると、目立つ |
| 17 段階 | 4×4 では、**17 段階**（0〜16 個の、画素）しか、表現できない |
| 安い | テーブル引きと、比較だけ |

### Interleaved Gradient Noise

Jimenez（2014）の、**画面座標から、安い式で、疑似ランダムな、しきい値**を作る方法です。ベイヤーより、**規則性が、目立ちません**。

```hlsl
float IGN(float2 screen_pos) {
  return frac(52.9829189 * frac(dot(screen_pos, float2(0.06711056, 0.00583715))));
}
void DitherClipIGN(float2 screen_pos, float alpha) { clip(alpha - IGN(screen_pos)); }
```

### ブルー ノイズ

**ブルー ノイズ**（Ulichney、1988）は、**低周波の成分が少なく、点が、均等に、散らばる**ノイズです。**規則性もなく、ダマにもならず**、**ディザに、最適**です。事前に作った、**ブルー ノイズの、テクスチャ**を、画面に、タイルして、しきい値として、読みます（Georgiev と Fajardo、2016）。

```hlsl
Texture2D<float> g_blue_noise : register(t8);             // 64×64 など（R8_UNORM、タイルできる）

float BlueNoiseThreshold(float2 screen_pos) {
  return g_blue_noise.Load(int3(int2(screen_pos) & 63, 0));
}
```

| パターン | 見た目 | コスト | 段階 |
| --- | --- | --- | --- |
| ベイヤー 4×4 | 格子状。規則性が見える | 最小 | 17 |
| IGN | 規則性が、目立たない | 小 | 実質、連続 |
| ブルー ノイズ | **最もなめらか**。粒が、均一 | 小（テクスチャ 1 回） | 実質、連続（64×64 なら、4,096 段階） |

## 用途 1：距離で、フェードして、消える

**近づきすぎた、物**（カメラの前の、木、柵）を、**ディザで、消す**と、**視界を、塞がず**、**ポップもしません**。

```hlsl
// カメラに近いほど、消える（ディザ フェード）。
float fade = saturate((distance_to_camera - near_fade_start) / (near_fade_end - near_fade_start));
clip(fade - BlueNoiseThreshold(input.position.xy));
```

## 用途 2：LOD の、切り替え

**2 つの LOD を、ディザで、混ぜて**、切り替える。**一方の、描く画素と、もう一方の、描く画素が、補い合う**ように、しきい値を、**反転**させます。

```hlsl
// LOD A: fade が 1 → 0 に向かうとき、少しずつ、消える。
clip(fade_a - BlueNoiseThreshold(input.position.xy));
// LOD B: 同じしきい値で、反転（A が捨てた画素を、B が描く）。
clip((1.0 - fade_a) - (1.0 - BlueNoiseThreshold(input.position.xy)));   // = clip(BlueNoise - fade_a)
```

**同じ、しきい値パターン**を、2 つの LOD で、使うことが、肝心です。**A が描かない画素を、B が描く**ので、重なりも、穴も、ありません。

## 用途 3：半透明を、**安く**

**ソートできない、大量の物**（草、髪）の、アルファを、ディザで、近似します。深度に、書き込め、ソートが不要です。

| 場面 | 内容 |
| --- | --- |
| 一時的な、フェード | キャラクターの、出現・消滅 |
| 遠くの、草 | 密度を、距離で、間引く（ディザで、**画素単位**に） |
| 透けるキャラ（ステルス） | 半透明風に |

## ディザの、**最大の問題**：ざらつき

ディザは、**点の、粗さ**が、見えます。**1 画素の粒**が、**ちらちら**して、**ザラザラ**した見た目です。

| 対策 | 内容 |
| --- | --- |
| TAA（時間的アンチエイリアス） | ディザのパターンを、**フレームごとに、ずらして**、TAA で、平均すると、**滑らかな、半透明**に見える（[TAA](../../postprocess/antialiasing/taa.md)） |
| ブルー ノイズ | 粒が、均一で、ダマにならず、**ザラつきが、目立たない** |
| 高解像度 | 画素が、小さい（4K）ほど、点が、目立たない |

TAA と組み合わせるときは、**パターンを、フレームごとに、ずらす**（ノイズの座標に、フレーム番号に応じた、オフセットを足す）。

```hlsl
// フレームごとに、ノイズの参照位置を、ずらす（TAA で、平均されて、なめらかに見える）。
float2 jitter = float2(frame_index * 17, frame_index * 31);
float threshold = g_blue_noise.Load(int3(int2(screen_pos + jitter) & 63, 0));
```

''', before="## よくあるミス")
pg.Refs("translucency/alpha-test/dither.md", [BAYER, JIMENEZ, ULICHNEY, GEORGIEV, WYMAN17])

# ---------------------------------------------------------------- hashed alpha
pg.Dedup("translucency/alpha-test/hashed-alpha.md")
pg.Add("translucency/alpha-test/hashed-alpha.md", '''
## ハッシュ アルファの、考え方

Wyman と McGuire（2017）は、**アルファ テストを、確率的に行う**方法を、示しました。**画素ごとに、ランダムなしきい値**を、決め、アルファが、そのしきい値より大きければ、描きます。

```text
通常のアルファ テスト:    alpha > 0.5          （全画素で、しきい値が、同じ）
ハッシュ アルファ:        alpha > hash(位置)    （画素ごとに、しきい値が、ランダム）
```

**確率の考え方**：しきい値が、0〜1 の、一様乱数なら、**アルファ `a` の画素が、描かれる確率は、ちょうど `a`** です。**アルファ 0.3 なら、画素の 30% が、描かれる**。TAA で、複数フレームを、平均すると、**30% の濃さの半透明**に、見えます。

## 通常の、アルファ テストとの違い

| | アルファ テスト（0.5 で切る） | ハッシュ アルファ |
| --- | --- | --- |
| しきい値 | 0.5（固定） | **ランダム**（画素ごと） |
| アルファ 0.3 の部分 | **常に、捨てる**（消える） | **30% の画素が、描かれる**（薄く見える） |
| 縁 | 階段状（ジャギー） | なめらか（ノイズが、混ざる） |
| 半透明の表現 | 不可（0 か 1 か） | **可能**（確率的に） |
| 遠くの、葉 | ミップで、アルファが、薄くなり、**スカスカ** | 薄くなった、アルファが、**確率として、残る** |
| ノイズ | なし | **あり**（TAA で、減る） |

アルファ 0.3 の部分が、**通常の、アルファ テストでは、消えますが**、ハッシュ アルファでは、**30% の確率で、描かれて**、**ミップで、薄くなった、遠くの葉**が、**スカスカに、ならずに**、**平均すると、元の、密度**に近くなります（[Foliage Translucency](../../terrain/vegetation/translucency.md)）。

## ハッシュの、作り方：安定させる

しきい値は、**画素ごと**に、決まりますが、**フレームごとに、変わる**と、**ちらつき**ます。TAA を、使わないなら、**同じ物の、同じ点が、いつも、同じしきい値**を、持ってほしいです。そこで、**画面の座標ではなく、物の表面の位置**（オブジェクト空間）から、ハッシュを作ります。

```hlsl
// 画面ではなく、物体の表面の位置から、安定した乱数を作る（カメラが動いても、同じ点は、同じしきい値）。
float Hash(float2 p) {
  return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453);
}

// オブジェクト空間の位置から作る。
float HashedThreshold(float3 object_pos) {
  return Hash(object_pos.xy + Hash(object_pos.zz));
}
```

| 方法 | 動き | 向く場面 |
| --- | --- | --- |
| 画面座標から作る | カメラが動くと、パターンは、画面に固定。**画面に、ノイズが、貼り付いた**ように見える（スクリーン ドア効果） | TAA あり（フレームごとに、ずらして、平均） |
| オブジェクト空間から作る | **物に、パターンが、貼り付く**。物と一緒に動く。安定している | TAA なしでも、安定。ただし、**物に、ざらざらの模様**が、貼り付いて見える |

## スケールの、問題

オブジェクト空間の、ハッシュは、**近づくと、ノイズの粒が、大きく**、**遠ざかると、小さく**（画素より小さく）なります。**画面上で、一定の、粒の大きさ**に、保つには、**画面上の、1 画素に、対応する、オブジェクト空間の、大きさ**で、ハッシュを、**スケール**する必要があります。

Wyman と McGuire の、方法は、**画面の微分**（`ddx`、`ddy`）から、**画素の、大きさ**を、求めて、**ハッシュする座標を、離散化**（その大きさに、丸める）します。

```hlsl
// 論文の考え方: 1 画素の大きさに合わせて、ハッシュ用の座標を丸める。
float HashedAlphaThreshold(float3 object_pos, float hash_scale) {
  // 画素の、オブジェクト空間での大きさ（最大の微分の長さ）
  float max_deriv = max(length(ddx(object_pos)), length(ddy(object_pos)));
  float pix_scale = 1.0 / (hash_scale * max_deriv);                  // 画素の大きさに、比例
  // 2 の累乗に丸めて、座標を離散化（スケールが、なめらかに、切り替わるよう、2 つを補間）
  float2 pix_scales = float2(exp2(floor(log2(pix_scale))), exp2(ceil(log2(pix_scale))));
  float2 alpha_xy = float2(Hash(floor(pix_scales.x * object_pos.xy)),
                           Hash(floor(pix_scales.y * object_pos.xy)));
  float lerp_factor = frac(log2(pix_scale));
  float x = lerp(alpha_xy.x, alpha_xy.y, lerp_factor);
  // 一様な分布にするための、補正（論文の式）
  float a = min(lerp_factor, 1.0 - lerp_factor);
  float3 cases = float3(x * x / (2.0 * a * (1.0 - a)),
                        (x - 0.5 * a) / (1.0 - a),
                        1.0 - ((1.0 - x) * (1.0 - x) / (2.0 * a * (1.0 - a))));
  float threshold = (x < (1.0 - a)) ? ((x < a) ? cases.x : cases.y) : cases.z;
  return clamp(threshold, 1e-6, 1.0);
}
```

上のコードは、論文の、実装の骨子です。**ポイント**は、**スケールを、2 の累乗に、丸めて、2 つを、補間する**ことで、**距離が変わっても、粒の大きさが、画面上で、ほぼ一定**になる点です。

実用上は、**画面座標から作る、簡単な方法（ブルー ノイズ、IGN）+ TAA**が、十分なことが、多いです。

## シェーダーでの、使い方

```hlsl
float alpha = g_albedo.Sample(g_linear_wrap, input.uv).a;
float threshold = HashedAlphaThreshold(input.object_pos, 1.0);
clip(alpha - threshold);
```

| 項目 | 内容 |
| --- | --- |
| 組み合わせる | **TAA** と一緒に使うと、ノイズが、平均されて、**半透明のように、見える** |
| MSAA との併用 | A2C と併用すると、**縁が、さらに、なめらか**（ただし、重い） |
| 影 | **影のパス**でも、同じハッシュで、描く。影も、**確率的に、薄く**なる（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)） |
| ノイズ | TAA が、**なければ**、ノイズが、目立つ。静止画で、ざらつく |

## 使い分け

| 方式 | 縁 | 半透明 | ノイズ | 必要なもの |
| --- | --- | --- | --- | --- |
| アルファ テスト | ジャギー | なし | なし | なし |
| A2C | なめらか | 段階的 | なし | MSAA |
| ディザ | 粒状 | あり（確率） | あり | なし（TAA が、あると良い） |
| ハッシュ アルファ | なめらか（TAA あり） | あり（確率） | あり | **TAA** |

TAA が、すでにあるゲームでは、**ハッシュ アルファ**が、**最も、手軽で、品質が良い**選択です。

''', before="## よくあるミス")
pg.Refs("translucency/alpha-test/hashed-alpha.md", [WYMAN17, JIMENEZ, CASTANO, GEORGIEV])

# ---------------------------------------------------------------- performance
pg.Dedup("translucency/alpha-test/performance.md")
pg.Add("translucency/alpha-test/performance.md", '''
## アルファ テストが、**GPU にとって、高い**理由

アルファ テスト（`clip` / `discard`）を、使うと、GPU の、**高速化の機能**の、一部が、**使えなくなります**。

### ① Early-Z が、効かなくなる

GPU は、ふつう、**ピクセル シェーダーを、実行する前**に、**深度テスト**を行い（**Early-Z**）、**手前に、別の物があって、見えない画素は、シェーダーを、実行せずに、捨てます**。ところが、**ピクセル シェーダーの中で、`clip` する**場合、**その画素が、残るかどうかは、シェーダーを、実行しないと、分かりません**。そのため、**深度の書き込みは、シェーダーの後**でなければ、できず、**Early-Z が、制限**されます。

| | 通常の描画 | `clip` を使う描画 |
| --- | --- | --- |
| 深度テスト | **シェーダーの前**（Early-Z） | シェーダーの後（Late-Z）、または、制限付きの、Early-Z |
| 隠れた画素 | **シェーダーを、実行しない** | シェーダーを実行してから、捨てる |
| 深度の書き込み | シェーダーの前でも、可能 | シェーダーの後 |

**葉や、草のように、画面を、何重にも、覆う物**を、`clip` で描くと、**奥の葉まで、すべての、ピクセル シェーダーが、実行**されます（**オーバードロー**が、そのままコストに）。

### ② HiZ（階層的な、深度）の、更新

GPU は、**階層化された深度**（HiZ）を、持ち、**タイル（数十画素）ごとに、まとめて、深度テストして**、隠れた、タイルを、一気に、捨てます。`clip` を使うと、**そのタイルが、完全に、塗りつぶされるか、分からない**ので、**HiZ の、更新が、制限**されます（実装は、GPU ごとに、異なる）。

## 影響を、減らす 5 つの方法

### 方法 1：不透明な、部分を、分ける（ジオメトリで、切り抜く）

葉を、**四角い板に、絵を貼る**のではなく、**葉の形に、ジオメトリを、切り抜く**と、`clip` が、**不要な部分**が、増えます。

| 部分 | 描き方 |
| --- | --- |
| 葉の、**中の、完全に、不透明な部分** | `clip` なしの、メッシュ（Early-Z が、効く） |
| 葉の、**縁**（アルファの、ある部分） | `clip` ありの、メッシュ |

メッシュを、**2 つに、分けて**、描きます。**不透明な部分**で、先に、深度を書き、**縁の部分**は、あとで、描くと、**Early-Z が、効いた状態**で、縁の描画が、できます。

### 方法 2：Z プリパス（深度だけを、先に描く）

**画面全体の、深度**を、**先に、軽いシェーダーで、描いて**、**本描画**では、**深度が、一致する画素だけ**を、実行します。

```text
パス 1（Z プリパス）: 深度だけを描く。色は計算しない。clip は必要（アルファ テストする物は、clip する）。
パス 2（本描画）  : 深度テストを「等しい」にして描く。Early-Z が効き、隠れた画素は、重いシェーダーを実行しない。
```

| パス | 内容 |
| --- | --- |
| 1. 深度プリパス | **軽い**ピクセル シェーダー（テクスチャを、読んで、`clip` するだけ）で、深度を書く |
| 2. 本描画 | **重い**ライティングを、行う。深度テストは、`EQUAL`（または `LESS_EQUAL`）。**深度が、一致した画素だけ**、実行される |

```cpp
// 本描画: 深度の書き込みを、無効にし、テストを「等しい」にする。
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;          // 書き込まない（プリパスで、書いた）
ds.DepthFunc = D3D11_COMPARISON_EQUAL;                    // プリパスの深度と、一致する画素だけ
device->CreateDepthStencilState(&ds, &depth_equal_state);
```

**プリパスで、アルファ テストした結果**が、深度に入るので、**本描画では、`clip` が、不要**になります。**重いシェーダーが、実行される画素は、最終的に、見える画素だけ**です。

!!! warning "プリパスと、本描画の、深度を、完全に、同じにする"
    プリパスと、本描画で、頂点シェーダーの、**計算が、1 ビットでも違う**と、深度が、一致せず、**画素が、欠けます**（`EQUAL` の、落とし穴）。同じ、**頂点シェーダーを、共有**し、`invariant` な計算を、保つ。DirectX 11 では、**同じ頂点シェーダーを使えば、同じ結果**になることが、一般的ですが、**別の、シェーダーを使う**と、ずれる可能性があります。

### 方法 3：アルファの、**範囲**を、狭める

葉の板（カード）に、**透明部分**が、**多すぎる**と、**透明な、画素の、シェーダーが、無駄**です。**板の形を、葉の輪郭に、合わせて、切る**（**タイトなメッシュ**）と、**透明な画素が、減り**、オーバードロー（**重なり**）も、減ります。

| 板の形 | 透明な部分 | 無駄なシェーダー実行 |
| --- | --- | --- |
| 正方形 | 約 60% | 多い |
| 葉の輪郭に、合わせて、8〜12 頂点で、切る | 約 15% | 少ない |

**頂点数を、少し増やして、ピクセルを、大きく減らす**のは、**よい取引**です。

### 方法 4：ミップ レベルを、コントロール

アルファの、ミップが、薄くなる問題（[Foliage Translucency](../../terrain/vegetation/translucency.md)）を、**補正した**ミップを、使えば、**遠くで、葉が、スカスカになりません**。結果、**カード（板）を、増やして、補う必要が、なくなり**、**オーバードローが、減ります**。

### 方法 5：遠景は、アルファを、**使わない**

遠くの木は、**インポスター**（板 1 枚）、または、**アルファを使わない、メッシュ**（LOD で、葉を、塊の、不透明な、形にする）に、置き換えます（[Trees](../../terrain/vegetation/trees.md)）。

## 影のパスでの、アルファ テスト

シャドウ マップを、描くときも、**葉を、アルファで、切り抜く**必要があります。**影のパスは、深度だけ**を、書くので、**軽いピクセル シェーダー**（テクスチャを読んで、`clip` するだけ）を、使います。

| 工夫 | 内容 |
| --- | --- |
| 影用の、軽い、シェーダー | アルファの、テクスチャだけを、読む。ライティングは、しない |
| 影用の、アルファ テクスチャ | **低解像度の、ミップ**を、読む（影は、細かい形が、不要） |
| 遠くの、葉は、影を落とさない | 影に、描く、距離を、限る |
| 影用の LOD | 描画より、**粗い LOD** を、使う |

## 計測する

| 項目 | 方法 |
| --- | --- |
| オーバードロー | **色で、可視化**する（描かれた回数を、加算ブレンドで、数える） |
| ピクセル シェーダーの、実行回数 | PIX、RenderDoc、GPU プロファイラーの、カウンター |
| `clip` の、影響 | `clip` を、**一時的に、無効**にして、フレーム時間を、比べる |

```hlsl
// オーバードロー可視化: 描かれるたびに、少しずつ加算する（加算ブレンド）。
return float4(0.1, 0.05, 0.02, 1.0);
// 結果の、明るい所ほど、重なって描かれた画素が、多い
```

草原や、森の、場面では、**オーバードローが、10 倍を超える**ことも、あります。**測らずに、最適化しない**ことが、大切です（[パフォーマンス プロファイラー](../../../vs/profiler.md)）。

''', before="## よくあるミス")
pg.Refs("translucency/alpha-test/performance.md", [RTR, WYMAN17, "Akeley, Hanrahan, et al., \"Real-Time Graphics Architecture\", Stanford CS448 講義資料（Early-Z、HiZ の、基本）", D3D11_BLEND])

# ---------------------------------------------------------------- comparison / index (refs only + short additions)
pg.Dedup("translucency/alpha-test/comparison.md")
pg.Add("translucency/alpha-test/comparison.md", '''
## 5 つの方式を、並べて比べる

| 観点 | アルファ テスト | Alpha to Coverage | ディザ | ハッシュ アルファ | アルファ ブレンド |
| --- | --- | --- | --- | --- | --- |
| 縁 | ジャギー | **なめらか** | 粒状 | なめらか（TAA で） | なめらか |
| 半透明 | 0 か 1 | 段階的（MSAA の段階） | 確率的 | 確率的 | **連続** |
| 深度の書き込み | 可能 | 可能 | 可能 | 可能 | **不可**（普通は） |
| ソート | **不要** | **不要** | **不要** | **不要** | **必要** |
| 前提 | なし | **MSAA** | なし | **TAA**（推奨） | なし |
| ノイズ | なし | なし | あり | あり | なし |
| コスト | Early-Z が、効かない | 同左 + MSAA | 同左 | 同左 | ブレンドの帯域 |
| 向く対象 | 柵、金網 | **葉、草（フォワード）** | フェード、LOD | **葉、髪（TAA あり）** | ガラス、煙、水 |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| まず、動かしたい | アルファ テスト |
| フォワード + MSAA の、植生 | **Alpha to Coverage** |
| ディファード + TAA の、植生 | **ハッシュ アルファ**（または、IGN / ブルー ノイズのディザ） |
| LOD の切り替え、近接フェード | ディザ（ブルー ノイズ） |
| 本当の、半透明（ガラス、煙） | アルファ ブレンド（[Alpha Blending and Sorting](../blending-sorting/index.md)）、OIT |

## 組み合わせる

1 つだけでなく、**組み合わせる**のが、普通です。

| 組み合わせ | 内容 |
| --- | --- |
| A2C + アルファの、シャープ化 | 縁を、1 画素幅に、保つ（[Alpha to Coverage](alpha-to-coverage.md)） |
| ハッシュ アルファ + TAA | ノイズを、時間方向に、平均して、なめらかに |
| ディザ + LOD | 2 つの LOD を、補い合うパターンで、切り替える |
| Z プリパス + 上のどれか | 隠れた画素の、重いシェーダーを、省く（[Performance and Shadow Passes](performance.md)） |

''', before="## よくあるミス")
pg.Refs("translucency/alpha-test/comparison.md", [WYMAN17, CASTANO, JIMENEZ, RTR])
pg.Refs("translucency/alpha-test/index.md", [WYMAN17, CASTANO, RTR, D3D11_BLEND])
print("ok")
