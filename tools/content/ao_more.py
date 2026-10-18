import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

# ---------------------------------------------------------------- usage-misconceptions
pg.Add("ao/theory/usage-misconceptions.md", '''
## 適用のコード

AO は、<strong>間接光（環境光）にだけ</strong>掛けます。ライティングのパスで、環境光の項に、AO を掛けます。

```hlsl
Texture2D<float> g_ao : register(t5);                          // AO（ぼかし・アップサンプル済み）

// GTAO のマルチ バウンス近似: 明るい色の面ほど、隅で、光が回り込むので、AO を、弱める（Jimenez 2016）。
float3 MultiBounceAO(float ao, float3 albedo) {
  float3 a = 2.0404 * albedo - 0.3324;
  float3 b = -4.7951 * albedo + 0.6417;
  float3 c = 2.7552 * albedo + 0.6903;
  return max(ao, ((ao * a + b) * ao + c) * ao);               // ao 自身より、暗くならない
}

// スペキュラ遮蔽: 拡散の AO を、鏡面反射の、遮蔽に、変換する（Lagarde と de Rousiers、2014）。
float SpecularOcclusion(float n_dot_v, float ao, float roughness) {
  return saturate(pow(n_dot_v + ao, exp2(-16.0 * roughness - 1.0)) - 1.0 + ao);
}

float3 AmbientLighting(float3 albedo, float3 f0, float roughness, float n_dot_v, float2 uv,
                       float3 diffuse_irradiance, float3 specular_ibl) {
  float ao = g_ao.SampleLevel(g_linear_clamp, uv, 0);
  float3 diffuse = diffuse_irradiance * albedo * MultiBounceAO(ao, albedo);   // 拡散の環境光に、掛ける
  float3 specular = specular_ibl * SpecularOcclusion(n_dot_v, ao, roughness); // 鏡面の環境光には、変換して掛ける
  return diffuse + specular;
}
// 直接光（太陽、ライト）には、AO を掛けない。直接光の影は、シャドウ マップが受け持つ。
```

数行ずつ見ると、<strong>拡散の環境光</strong>には、アルベドで、補正した `MultiBounceAO` を、<strong>鏡面の環境光</strong>には、粗さと視線の角度で、変換した `SpecularOcclusion` を掛けています。同じ `ao` を、そのまま、全部に掛けないのがコツです。

| 掛ける相手 | 掛けるもの | 理由 |
| --- | --- | --- |
| 拡散の環境光 | `MultiBounceAO(ao, albedo)` | 明るい面は、隅で、光が回り込む。素の AO は、暗すぎる |
| 鏡面の環境光 | `SpecularOcclusion(...)` | 鏡面は、反射方向の、狭い範囲だけが効く。粗いほど、AO に近く、つるつるなら、効きにくい |
| 直接光 | 掛けない | 直接光の影は、シャドウ マップが担当。二重に暗くなる |
| エミッシブ | 掛けない | 自分で光る物は、遮られない |

## 画面に出して、確認する

AO が、正しく掛かっているかは、<strong>AO だけ</strong>、<strong>ライティング済みの画面</strong>、<strong>AO を、掛けない画面</strong>を、キーで、切り替えて見ます。

```hlsl
// デバッグ表示: 切り替えで、AO だけを、白黒で出す。
if (g_debug_mode == kDebugAoOnly) return float4(ao.xxx, 1.0);
if (g_debug_mode == kDebugNoAo) return float4(AmbientLightingWithoutAo(...) + direct, 1.0);
```

隅と接地面が、<strong>自然に、暗く</strong>、日向や、大きな面が、<strong>暗くなっていない</strong>こと、そして、AO の効きが、動いても、ちらつかないことを、確認します。
''', before="## よくある誤解")

# ---------------------------------------------------------------- bilateral-blur
pg.Add("ao/filtering/bilateral-blur.md", '''
## DirectX 11 で、2 パスにつなぐ

バイラテラル ブラーは、<strong>横と縦の 2 パス</strong>で、フルスクリーン三角形で、行います（[D3D11 Pass Recipes](../../../directx/dx11/pass-recipes.md)）。

```cpp
// 入力: AO（R8_UNORM）、深度、法線。出力: 横ブラーの結果 → 縦ブラーの結果。
struct BlurCB {
  DirectX::XMFLOAT2 direction;      // (1, 0) で横、(0, 1) で縦
  DirectX::XMFLOAT2 texel_size;     // 1 ピクセルの大きさ（UV）
  float depth_sharpness;            // 大きいほど、境界を厳しく守る
  float pad[3];
};

// 横ブラー: ao_raw → ao_temp
SetBlurConstants({1, 0}, texel, 16.0f);
context->OMSetRenderTargets(1, ao_temp_rtv.GetAddressOf(), nullptr);
ID3D11ShaderResourceView* srvs_h[] = {ao_raw_srv.Get(), depth_srv.Get(), normal_srv.Get()};
context->PSSetShaderResources(0, 3, srvs_h);
DrawFullscreenTriangle();

// 縦ブラー: ao_temp → ao_blurred（同じテクスチャを、読み書きしない。別のテクスチャに出す）
SetBlurConstants({0, 1}, texel, 16.0f);
context->OMSetRenderTargets(1, ao_blurred_rtv.GetAddressOf(), nullptr);
ID3D11ShaderResourceView* srvs_v[] = {ao_temp_srv.Get(), depth_srv.Get(), normal_srv.Get()};
context->PSSetShaderResources(0, 3, srvs_v);
DrawFullscreenTriangle();
```

2 つのパスの間で、書き込みの束縛を、外してから、読み取りに切り替えます（読みながら書けない）。AO は、ポイント サンプラーで読み、<strong>隣の画素と、補間しない</strong>ようにします（補間すると、境界を、またいで、混ざります）。

## ガウスの重みを、作る

空間の重み（距離が近いほど大）は、ガウス関数で、起動時に、計算して、定数にします。

```cpp
// 半径 radius のガウスの重み（中心から片側 radius+1 個）を、合計が 1 になるように、正規化して作る。
std::vector<float> MakeGaussianWeights(int radius, float sigma) {
  std::vector<float> w(radius + 1);
  float sum = 0.0f;
  for (int i = 0; i <= radius; ++i) {
    w[i] = std::exp(-0.5f * (i * i) / (sigma * sigma));
    sum += (i == 0) ? w[i] : 2.0f * w[i];                    // 中心以外は、左右の 2 回ぶん
  }
  for (float& v : w) v /= sum;
  return w;
}
// radius = 4、sigma = 2 など。シェーダーの定数配列に渡す。
```

## パラメータの、目安

| パラメータ | 目安 | 効き方 |
| --- | --- | --- |
| 半径（片側） | 2〜4 画素 | 大きいほど、ノイズが消えるが、読み込みが増える。ノイズの周期（4×4）に合わせる |
| `depth_sharpness` | 8〜32 | 大きいほど、境界を、厳しく守る（ハローは減るが、ノイズが、境界の近くに、残る） |
| 法線の指数 | 4〜16 | 大きいほど、向きの違う面を、混ぜない |
| 解像度 | AO と同じ | 半分の解像度の AO なら、半分の解像度で、ぼかす（その後、アップサンプル） |

読み込みの回数は、半径 4 の分離ぼかしで、1 画素あたり、約 18 回（横 9 + 縦 9）。深度と法線も、読むので、実際は、約 3 倍の読み込みです。半分の解像度で行うと、ピクセル数が 1/4 になり、これが、大きな節約になります（[Upsampling](upsample.md)）。

## 見た目の確認

ぼかしの、効きは、<strong>AO だけを、画面に出して</strong>確認します。

| 見え方 | 原因 |
| --- | --- |
| 物の輪郭に、黒い縁・白い縁 | 境界を、またいで、混ぜている。`depth_sharpness` を上げる。法線の重みを足す |
| 平らな面に、ざらざらが残る | 半径が小さい、または、サンプル数が少ない。半径を上げる、時間蓄積を足す |
| 細い物の AO が、消える | 深度の重みが、強すぎて、周りを混ぜられない。値を、少し下げる |
| 遠くの AO が、にじむ | 深度の差を、中心の深度で、割っていない（相対差にする） |
''', before="## よくあるミス")

# ---------------------------------------------------------------- noise-pattern
pg.Add("ao/filtering/noise-pattern.md", '''
## ノイズを、作るコード

AO のサンプルの向きは、画素ごとに、ずらします。ずらす値（ノイズ）は、シェーダーの中で、計算で作れます。

### Interleaved Gradient Noise（IGN）

画素の座標だけから、ブルー ノイズに近い値を、1 行で作ります（Jimenez）。テクスチャを読まないので、安く、TAA と相性が良いです。

```hlsl
// 画素の座標（SV_Position.xy）から、0〜1 のノイズを作る。
float InterleavedGradientNoise(float2 pixel) {
  return frac(52.9829189 * frac(dot(pixel, float2(0.06711056, 0.00583715))));
}

// フレームごとに、ずらして、時間方向にも、ばらつかせる（TAA や時間蓄積が、平均してくれる）。
float IgnTemporal(float2 pixel, uint frame) {
  return InterleavedGradientNoise(pixel + 5.588238 * (frame % 64));
}
```

### ブルー ノイズ テクスチャ

あらかじめ作った、ブルー ノイズの、小さな画像（64×64 など）を、画面に敷き詰めて、読みます。

```hlsl
Texture2D<float> g_blue_noise : register(t6);      // 64×64、R8_UNORM。WRAP サンプラーで、繰り返す

float BlueNoise(uint2 pixel, uint frame) {
  float n = g_blue_noise.Load(int3(pixel % 64, 0));
  // 黄金比で、フレームごとにずらす（0〜1 を、均等に巡る）。
  return frac(n + 0.61803398875 * (frame % 64));
}
```

| 方式 | 見た目 | コスト |
| --- | --- | --- |
| `frac(sin(…))` のハッシュ | 白色ノイズ。粒が目立つ | 最小（ただし、GPU ごとに、結果が違う） |
| IGN | ブルー ノイズに近い。縞は出にくい | 最小（計算だけ） |
| ブルー ノイズ テクスチャ | 最も、粒が細かく、均一 | 読み込み 1 回 |
| 4×4 のタイル テクスチャ | 4 画素周期の模様が出る。4×4 のぼかしで消せる | 読み込み 1 回 |

### ノイズを、サンプルの向きに使う

```hlsl
float noise = IgnTemporal(pos.xy, g_frame_index);               // 0〜1
float rotation = noise * 6.2831853;                             // 画素ごとに、サンプル全体を、回す角度
float2x2 rot = float2x2(cos(rotation), -sin(rotation), sin(rotation), cos(rotation));
for (int i = 0; i < kSamples; ++i) {
  float2 offset = mul(kernel[i].xy, rot);                       // 回したサンプル位置で、深度を読む
  ...
}
```

回転の角度が、画素ごとに違うので、同じ向きの取りこぼし（縞）が、細かい粒に変わり、ぼかしと、時間蓄積で、均されます。フレームごとに、ずらすのは、<strong>1 フレームだけでは、足りない分を、時間で、補う</strong>ためです（[Temporal Accumulation](temporal.md)）。
''', before="## よくあるミス")

# ---------------------------------------------------------------- edge-thin
pg.Add("ao/artifacts/edge-thin.md", '''
## 対策のコード

### 画面の外を、遮蔽なしにして、端でフェードする

```hlsl
// サンプル位置が、画面の外なら、深度が分からない。遮蔽なし（0）として、数えない。
float2 sample_uv = center_uv + offset_uv;
if (any(sample_uv < 0.0) || any(sample_uv > 1.0)) continue;        // ループの次のサンプルへ

// 画面の端に近い画素ほど、AO を弱める（外側の情報が、足りなくなるため）。
float2 edge = saturate((0.5 - abs(center_uv - 0.5)) * 12.0);        // 端から約 8% の幅で、0 → 1
float edge_fade = min(edge.x, edge.y);
ao = lerp(1.0, ao, edge_fade);                                       // 端では、AO なし（1.0）へ
```

画面の外は、誰も知らないので、「遮蔽されていない」として扱い、さらに、端の画素では、AO 自体を、弱めて、急に暗さが変わる、境目を、隠します。ガード バンド（画面より、少し広く描く）を使えば、端でも、外側の深度を、読めます。

### 厚みを仮定して、薄い物を、またげるようにする

```hlsl
// サンプルが、中心より手前でも、その差が、厚みより大きければ、薄い物の「向こう側」とみなして、遮蔽に数えない。
float dz = z_center - z_sample;                                      // 正なら、サンプルのほうが、手前
float occluded = (dz > kBias && dz < kThickness) ? 1.0 : 0.0;
```

`kThickness`（たとえば、半径の 2 倍）より、手前の物は、「その後ろにも、まだ、空間がある」とみなし、遮蔽に数えません。薄い板（フェンス、葉）が、後ろの面を、全部、暗くするのを防ぎます。ただし、本当に、厚い物が、遮るときも、弱くなるので、値は、見ながら、決めます。
''', before="## よくあるミス")
print("ok")
