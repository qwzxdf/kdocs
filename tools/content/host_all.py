import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

RECIPES = "[D3D11 Pass Recipes](%sd3d11-recipes.md)"


def Note(rel):
    return '''
## DirectX 11 では動かない部分

<strong>DXR（DirectX Raytracing）は、DirectX 12 の機能です。DirectX 11 には、ありません。</strong>このページの `TraceRay`・`RayQuery` を使うコードは、D3D12 のレンダラーで動かします。D3D11 だけで、同じ効果を狙うときは、次のように、置き換えます。

| やりたいこと | D3D11 での代用 |
| --- | --- |
| レイと三角形の、交差 | 距離場（SDF）・ボクセル、またはスクリーン空間のレイマーチ（[Linear Marching](%sreflections/ssr-basics/linear-march.md)） |
| 影 | シャドウ マップ（[Shadow Map Basics](%sshadows/shadow-map-basics/index.md)） |
| 間接光 | ライトマップ・プローブ・SSGI・ボクセル GI（[Global Illumination (GI)](%sgi/index.md)） |

D3D12 側の、初期化（加速構造・ステート オブジェクト・シェーダー テーブル・`DispatchRays`）は、[DXR Host Setup](%sdxr-host.md) に、まとめています。

''' % ((rel,) * 4)


for path, rel in [
    ("ao/world-space/rtao.md", "../../"),
    ("reflections/rt-reflections/index.md", "../../"),
    ("gi/ddgi.md", "../"),
    ("gi/rt-gi/index.md", "../../"),
    ("shadows/ray-traced.md", "../"),
]:
    pg.Add(path, Note(rel), key="## DirectX 11 では動かない部分")

# ---------------------------------------------------------------- AO
pg.Add("ao/ssao-hemisphere.md", '''
## DirectX 11 で組む

ここまでの HLSL を、1 回の描画パスとして、動かすための、ホスト側の、準備です（共通の部品は、[D3D11 Pass Recipes](../d3d11-recipes.md) を参照）。

### 入力と出力

```cpp
// 出力: AO（1 チャンネル）。フル解像度でも、半分でもよい。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R8_UNORM;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &ao_texture);
device->CreateRenderTargetView(ao_texture.Get(), nullptr, &ao_rtv);
device->CreateShaderResourceView(ao_texture.Get(), nullptr, &ao_srv);
```

AO は、0〜1 の 1 チャンネルなので、`R8_UNORM` で足ります。ぼかしの、2 パスのために、同じ大きさの、もう 1 枚（`ao_blur_texture`）を、作ります。

### ノイズ テクスチャとカーネル

```cpp
// ノイズ: 4×4 の、ランダムな回転（xy の方向）。繰り返して、画面に敷く（WRAP）。
struct Noise { int8_t x, y, z, w; };
Noise noise[16];
for (auto& n : noise) {
  float angle = RandomFloat() * 6.2831853f;
  n = {int8_t(std::cos(angle) * 127), int8_t(std::sin(angle) * 127), 0, 0};
}
D3D11_TEXTURE2D_DESC nd = {};
nd.Width = nd.Height = 4;
nd.MipLevels = nd.ArraySize = 1;
nd.Format = DXGI_FORMAT_R8G8B8A8_SNORM;                         // 符号つき。−1〜1 で読める
nd.SampleDesc.Count = 1;
nd.Usage = D3D11_USAGE_IMMUTABLE;
nd.BindFlags = D3D11_BIND_SHADER_RESOURCE;
D3D11_SUBRESOURCE_DATA init = {noise, 4 * sizeof(Noise), 0};
device->CreateTexture2D(&nd, &init, &noise_texture);
device->CreateShaderResourceView(noise_texture.Get(), nullptr, &noise_srv);
```

ノイズは、4×4 の、小さなテクスチャを、画面いっぱいに、繰り返し（`WRAP` サンプラー）、画素ごとに、違う回転を、与えます。ぼかしで、この 4×4 の模様を、消します。サンプラーは、ノイズ用に、`POINT` と `WRAP`、深度用に、`POINT` と `CLAMP` の、2 つを、用意します。

```cpp
// カーネル: 半球のサンプル（64 個の float4）を、定数バッファに入れる。起動時に、1 度だけ作る。
struct SsaoConstants {
  DirectX::XMFLOAT4 kernel[64];                                 // xyz: 半球内のオフセット
  DirectX::XMFLOAT4X4 projection;
  DirectX::XMFLOAT2 noise_scale;                                // (画面幅 / 4, 画面高さ / 4): ノイズを、画面に敷く倍率
  float radius;
  float bias;
};
```

`noise_scale` は、`uv` に掛けて、ノイズの座標にする倍率です。画面が、1920×1080 なら、(480, 270) で、ノイズが、480×270 回、繰り返されます。

### パスの流れ

```cpp
// ① AO を描く（深度 SRV と、法線 SRV を、読む。DSV は、束ねない）。
context->OMSetRenderTargets(1, ao_rtv.GetAddressOf(), nullptr);
context->PSSetShaderResources(0, 1, depth_srv.GetAddressOf());      // t0: 深度
context->PSSetShaderResources(1, 1, normal_srv.GetAddressOf());     // t1: 法線
context->PSSetShaderResources(2, 1, noise_srv.GetAddressOf());      // t2: ノイズ
DrawFullscreenTriangle();

// ② ぼかし（水平 → 垂直）。入力と出力を、別のテクスチャにする。
context->OMSetRenderTargets(1, ao_blur_rtv.GetAddressOf(), nullptr);
context->PSSetShaderResources(0, 1, ao_srv.GetAddressOf());
DrawFullscreenTriangle();     // 水平
// （もう 1 回、ao_blur → ao へ、垂直）
```

深度の DSV を、束ねたままにすると、深度を、SRV で、読めません（[D3D11 Pass Recipes](../d3d11-recipes.md) の、束縛の衝突）。AO の、結果は、ライティングの、パスで、環境光に、掛けます（[Usage and Misconceptions of AO](theory/usage-misconceptions.md)）。

''', before="## パラメータ")

pg.Add("ao/filtering/pipeline.md", '''
## 各パスを、DirectX 11 で、つなぐ

AO、ぼかし、時間蓄積、アップサンプルを、つないだ、1 フレームの、ホスト側の、順序です。

```cpp
// 解像度は、AO を、半分で、計算し、フルへ戻す構成。
const UINT half_w = width / 2, half_h = height / 2;

// ① 深度・法線を、半分に縮める（最も近い、または、最も遠い、深度を選ぶ。平均しない）
SetViewport(half_w, half_h);
Draw(downsample_depth_ps, {depth_srv, normal_srv}, {half_depth_rtv, half_normal_rtv});

// ② AO を、半解像度で、計算する
Draw(ao_ps, {half_depth_srv, half_normal_srv, noise_srv}, {ao_raw_rtv});

// ③ 時間蓄積: 前のフレームの AO と、混ぜる（ピンポン）
Draw(temporal_ps, {ao_raw_srv, ao_history.Read(), velocity_srv, half_depth_srv}, {ao_history.Write()});
ao_history.Swap();

// ④ ぼかし（深度で、エッジを保つ）。水平 → 垂直
Draw(blur_h_ps, {ao_history.Read(), half_depth_srv}, {ao_blur_rtv});
Draw(blur_v_ps, {ao_blur_srv, half_depth_srv}, {ao_filtered_rtv});

// ⑤ フル解像度へ、アップサンプル（フル解像度の深度で、重みを付ける）
SetViewport(width, height);
Draw(upsample_ps, {ao_filtered_srv, half_depth_srv, depth_srv}, {ao_full_rtv});
```

`Draw(...)` は、「入力の SRV を、束ね、出力の RTV を、束ね、フルスクリーン三角形を、描く」を、まとめた、仮の関数です。パスごとに、<strong>ビューポートを、出力の、大きさに、合わせる</strong>のを、忘れないでください（忘れると、画面の、左上の、一部にしか、描かれません）。`ao_history` は、ピンポンの、構造体です（[D3D11 Pass Recipes](../../d3d11-recipes.md)）。

''', before="## パラメータの目安")

# ---------------------------------------------------------------- bloom
pg.Add("postprocess/bloom/index.md", '''
## DirectX 11 で組む

ブルームは、半分ずつ、縮めながら、下へ降りる、ダウンサンプルと、同じ段を、逆に、昇る、アップサンプルの、2 つのパスの列です。ホスト側は、<strong>ミップのような、縮小列</strong>を、用意して、段ごとに、描きます。

### 縮小列を作る

```cpp
// 段ごとに、別のテクスチャにする（ミップマップではなく、別々の 6 枚）。1 段ごとに、縦横 1/2。
struct BloomLevel {
  Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv;
  Microsoft::WRL::ComPtr<ID3D11RenderTargetView> rtv;
  UINT width, height;
};
std::vector<BloomLevel> levels(6);
UINT w = width / 2, h = height / 2;
for (auto& level : levels) {
  D3D11_TEXTURE2D_DESC desc = {};
  desc.Width = level.width = std::max(w, 1u);
  desc.Height = level.height = std::max(h, 1u);
  desc.MipLevels = desc.ArraySize = 1;
  desc.Format = DXGI_FORMAT_R11G11B10_FLOAT;                    // HDR で、帯域が小さい（アルファなし）
  desc.SampleDesc.Count = 1;
  desc.Usage = D3D11_USAGE_DEFAULT;
  desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
  Microsoft::WRL::ComPtr<ID3D11Texture2D> t;
  device->CreateTexture2D(&desc, nullptr, &t);
  device->CreateShaderResourceView(t.Get(), nullptr, &level.srv);
  device->CreateRenderTargetView(t.Get(), nullptr, &level.rtv);
  w /= 2; h /= 2;
}
```

`R11G11B10_FLOAT` は、32 ビットで、HDR の色を持てるので、ブルームの、中間バッファに、向いています。アルファが、無い（ブルームは、色だけ）ので、足ります。段ごとに、別テクスチャにするのは、アップサンプルで、各段を、あとから、読むためです。

### 降りる

```cpp
// ダウンサンプル: シーン色 → levels[0] → levels[1] → …。各段で、ビューポートを、出力の大きさにする。
ID3D11ShaderResourceView* input = scene_srv.Get();
for (auto& level : levels) {
  context->OMSetRenderTargets(1, level.rtv.GetAddressOf(), nullptr);
  D3D11_VIEWPORT vp = {0, 0, float(level.width), float(level.height), 0, 1};
  context->RSSetViewports(1, &vp);
  context->PSSetShaderResources(0, 1, &input);
  DrawFullscreenTriangle();                                     // 13 タップのダウンサンプル（Karis 平均は 最初の段だけ）
  input = level.srv.Get();
}
```

最初の段は、Karis 平均（明るすぎる、点が、ちらつくのを、防ぐ）を、使い、ほかの段は、通常の、重みで、縮めます（[Karis Average](karis-average.md)）。

### 昇る

```cpp
// アップサンプル: 小さい段から、1 つ大きい段へ、加算ブレンドで、足し込む（置き換えない）。
context->OMSetBlendState(additive_blend.Get(), nullptr, 0xFFFFFFFF);   // SrcBlend = ONE、DestBlend = ONE
for (int i = int(levels.size()) - 2; i >= 0; --i) {
  context->OMSetRenderTargets(1, levels[i].rtv.GetAddressOf(), nullptr);
  SetViewport(levels[i].width, levels[i].height);
  context->PSSetShaderResources(0, 1, levels[i + 1].srv.GetAddressOf());
  DrawFullscreenTriangle();                                     // 3×3 のテント フィルタで、拡大
}
context->OMSetBlendState(nullptr, nullptr, 0xFFFFFFFF);
```

小さい段（広い、にじみ）を、1 つ大きい段へ、足し込み、それを、さらに、大きい段へ、足し込むと、段ごとの、にじみが、重なり合った、ブルームになります。最後に、`levels[0]` を、シーン色へ、強さを掛けて、足します（[Composite](composite.md)）。

''', before="## 関連ページ")

# ---------------------------------------------------------------- TAA
pg.Add("postprocess/antialiasing/taa.md", '''
## DirectX 11 で組む

### ジッターを、射影行列に入れる

```cpp
// 毎フレーム、サブピクセルのずれ（Halton 数列）を、射影行列に足す。
float jitter_x = (Halton(frame_index % 8 + 1, 2) - 0.5f) * 2.0f / width;     // NDC で、±1 画素の範囲
float jitter_y = (Halton(frame_index % 8 + 1, 3) - 0.5f) * 2.0f / height;
DirectX::XMFLOAT4X4 projection = base_projection;
projection._31 = -jitter_x;     // 右手系: w = −z_view なので、符号を反転すると、NDC で +jitter ずれる
projection._32 = -jitter_y;
```

行ベクトルの規約（`v * M`）では、`_31`、`_32` が、`z` に掛かり、`w = −z` で割られるので、ジッターが、NDC の、一定のずれ（`−_31`）になります。カメラが、止まっていても、毎フレーム、少しずつ違う位置で、サンプルされるので、時間で、平均すると、サブピクセルの、情報が、集まります。速度の計算と、履歴の、再投影では、ジッターを、引いて、使います（[Velocity Buffer](../motion-blur/velocity-buffer.md)）。

### 履歴テクスチャと、合成パス

```cpp
// 履歴: 2 枚のピンポン。HDR のまま持つ（トーン マッピングの前で、解決する）。
PingPong history;       // R16G16B16A16_FLOAT（作り方は、D3D11 Pass Recipes）

// 解決パス: 今のフレームの色 + 速度 + 深度 + 前の履歴 → 新しい履歴
context->OMSetRenderTargets(1, history.Write().GetAddressOf(), nullptr);
ID3D11ShaderResourceView* srvs[] = {scene_color_srv.Get(), history.Read(), velocity_srv.Get(), depth_srv.Get()};
context->PSSetShaderResources(0, 4, srvs);
context->PSSetSamplers(0, 1, linear_clamp.GetAddressOf());            // 履歴は、バイリニアで、読む
context->PSSetSamplers(1, 1, point_clamp.GetAddressOf());             // 速度・深度は、ポイントで読む
DrawFullscreenTriangle();
history.Swap();
```

出力は、新しい履歴で、同時に、画面に出す、画像でもあります（ブルームや、トーン マッピングへ渡す）。解決の、結果を、履歴に書き、同じ内容を、次の、ポスト プロセスにも使う、構成です。最初のフレーム、画面サイズの変更、カメラの、カットのときは、履歴を、捨てて（今のフレームの色を、そのまま、履歴にする）、ゴーストを、防ぎます。

''', before="## なぜクランプするのか")

# ---------------------------------------------------------------- SSS
pg.Add("skin-hair/skin/screen-space-sss.md", '''
## DirectX 11 で組む

### 拡散光と鏡面光を、別々に、持つ

画面空間 SSS は、<strong>拡散光だけ</strong>を、ぼかします。鏡面光（ハイライト）まで、ぼかすと、ハイライトが、にじんでしまうので、ライティングの、パスで、2 枚の、レンダー ターゲットに、分けて、出力します（MRT）。

```cpp
// ライティングの出力: 拡散（SSS の対象）と、鏡面（そのまま）を、別のターゲットへ。
ID3D11RenderTargetView* targets[2] = {diffuse_rtv.Get(), specular_rtv.Get()};
context->OMSetRenderTargets(2, targets, depth_dsv.Get());
```

```hlsl
// ピクセル シェーダー: 2 つの SV_Target に、別々に出す。
struct PSOut {
  float4 diffuse : SV_Target0;     // 皮膚の、拡散（アルベドは、まだ掛けない）
  float4 specular : SV_Target1;    // 鏡面
};
```

アルベド（皮膚の色）は、ぼかしの、あとに、掛けます（[Skin Albedo](#アルベドの扱い) の考え）。ぼかす前に、掛けると、色が、にじみ、皮膚の、模様が、失われます。

### ステンシルで、皮膚だけを、ぼかす

```cpp
// ジオメトリ パスで、皮膚のマテリアルの画素に、ステンシル値 1 を書く。
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;
ds.DepthFunc = D3D11_COMPARISON_LESS;
ds.StencilEnable = TRUE;
ds.StencilReadMask = ds.StencilWriteMask = 0xFF;
ds.FrontFace.StencilFunc = D3D11_COMPARISON_ALWAYS;
ds.FrontFace.StencilPassOp = D3D11_STENCIL_OP_REPLACE;                // 描いた画素に、参照値を書く
ds.FrontFace.StencilFailOp = ds.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_KEEP;
ds.BackFace = ds.FrontFace;
device->CreateDepthStencilState(&ds, &skin_write_state);
context->OMSetDepthStencilState(skin_write_state.Get(), 1);           // 参照値 1
```

```cpp
// ぼかしのパス: ステンシルが 1 の画素だけ、ピクセル シェーダーを走らせる（それ以外は、スキップ）。
D3D11_DEPTH_STENCIL_DESC test = {};
test.DepthEnable = FALSE;
test.StencilEnable = TRUE;
test.StencilReadMask = 0xFF;
test.FrontFace.StencilFunc = D3D11_COMPARISON_EQUAL;
test.FrontFace.StencilPassOp = test.FrontFace.StencilFailOp = test.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_KEEP;
test.BackFace = test.FrontFace;
device->CreateDepthStencilState(&test, &skin_test_state);
context->OMSetDepthStencilState(skin_test_state.Get(), 1);
```

ステンシル テストは、ピクセル シェーダーの、前に、行われるので、皮膚でない画素は、重い、ぼかしを、計算せずに、飛ばせます。ステンシルを、使うには、深度バッファを、`D24_UNORM_S8_UINT`（または `D32_FLOAT_S8X24_UINT`）の、形式に、して、DSV を、ぼかしのパスにも、束ねます（深度は、SRV で、別に、読みたいので、ステンシル付きの、typeless 形式で、作ります）。

### 水平と垂直の、2 パス

```cpp
// ① 水平: diffuse → blur_temp。ステンシルが 1 の画素だけ。深度で、輪郭を、またがない。
context->OMSetRenderTargets(1, blur_temp_rtv.GetAddressOf(), depth_dsv.Get());
context->PSSetShaderResources(0, 1, diffuse_srv.GetAddressOf());
context->PSSetShaderResources(1, 1, depth_srv.GetAddressOf());
SetBlurDirection(1.0f, 0.0f);                                       // 定数バッファで方向を渡す
DrawFullscreenTriangle();

// ② 垂直: blur_temp → sss_result。
context->OMSetRenderTargets(1, sss_result_rtv.GetAddressOf(), depth_dsv.Get());
context->PSSetShaderResources(0, 1, blur_temp_srv.GetAddressOf());
SetBlurDirection(0.0f, 1.0f);
DrawFullscreenTriangle();
```

最後に、ぼかした拡散光に、アルベドを掛け、鏡面光を、足して、HDR のシーン色に、合成します。深度の、SRV と、DSV を、同時に、束ねられない（[D3D11 Pass Recipes](../../d3d11-recipes.md)）ので、深度は、読み取り専用の、DSV（`D3D11_DSV_READ_ONLY_DEPTH`）で、束ね、同じ深度を、SRV でも、読みます。

''', before="## よくあるミス")

# ---------------------------------------------------------------- Hillaire
pg.Add("atmosphere/scattering/hillaire.md", '''
## DirectX 11 で組む

4 つの LUT は、すべて、計算シェーダーで、書く、小さなテクスチャです。

### LUT の、テクスチャ

```cpp
auto MakeLut = [&](UINT w, UINT h, UINT d, DXGI_FORMAT fmt, Microsoft::WRL::ComPtr<ID3D11ShaderResourceView>& srv,
                   Microsoft::WRL::ComPtr<ID3D11UnorderedAccessView>& uav) {
  Microsoft::WRL::ComPtr<ID3D11Resource> res;
  if (d == 1) {
    D3D11_TEXTURE2D_DESC desc = {w, h, 1, 1, fmt, {1, 0}, D3D11_USAGE_DEFAULT,
                                 D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS, 0, 0};
    Microsoft::WRL::ComPtr<ID3D11Texture2D> t;
    device->CreateTexture2D(&desc, nullptr, &t);
    t.As(&res);
  } else {
    D3D11_TEXTURE3D_DESC desc = {w, h, d, 1, fmt, D3D11_USAGE_DEFAULT,
                                 D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS, 0, 0};
    Microsoft::WRL::ComPtr<ID3D11Texture3D> t;
    device->CreateTexture3D(&desc, nullptr, &t);
    t.As(&res);
  }
  device->CreateShaderResourceView(res.Get(), nullptr, &srv);
  device->CreateUnorderedAccessView(res.Get(), nullptr, &uav);
};
MakeLut(256, 64, 1, DXGI_FORMAT_R16G16B16A16_FLOAT, transmittance_srv, transmittance_uav);      // 透過率
MakeLut(32, 32, 1, DXGI_FORMAT_R16G16B16A16_FLOAT, multiscatter_srv, multiscatter_uav);         // 多重散乱
MakeLut(192, 108, 1, DXGI_FORMAT_R11G11B10_FLOAT, skyview_srv, skyview_uav);                    // Sky-View
MakeLut(32, 32, 32, DXGI_FORMAT_R16G16B16A16_FLOAT, aerial_srv, aerial_uav);                    // Aerial Perspective（3D）
```

4 つとも、サイズが、小さいので、毎フレーム、書き直しても、軽く済みます。Aerial Perspective だけが、3D テクスチャ（画面の 32×32 に、奥行き 32 段）です。

### 更新の順序

```cpp
// 透過率と多重散乱は、大気のパラメータが変わったときだけ（普通は、起動時の 1 回）。
if (atmosphere_changed) {
  Dispatch(transmittance_cs, {}, {transmittance_uav}, 256 / 8, 64 / 8, 1);
  Dispatch(multiscatter_cs, {transmittance_srv}, {multiscatter_uav}, 32, 32, 1);     // 1 グループ = 1 テクセル（内部で、並列に、積分）
}
// Sky-View と Aerial Perspective は、毎フレーム（太陽の向きや、カメラの高さが、変わるため）。
Dispatch(skyview_cs, {transmittance_srv, multiscatter_srv}, {skyview_uav}, 192 / 8, 108 / 8, 1);
Dispatch(aerial_cs, {transmittance_srv, multiscatter_srv}, {aerial_uav}, 32 / 8, 32 / 8, 32);
```

`Dispatch(...)` は、仮の関数で、「入力 SRV を、束ね、出力 UAV を、束ね、`Dispatch` を、呼び、終わったら、束縛を、外す」を、まとめたものです（[D3D11 Pass Recipes](../d3d11-recipes.md)）。後のパスが、前の LUT を、読むので、各 `Dispatch` の、あとで、UAV を、`nullptr` で、外します。毎フレーム更新するのは、2 枚だけなので、大気の計算が、軽くなります。

''', before="## 宇宙から、地上まで")

# ---------------------------------------------------------------- froxel
pg.Add("atmosphere/volumetric-fog/froxel.md", '''
## DirectX 11 で組む

### froxel の 3D テクスチャ

```cpp
// froxel: 画面を 160×90 に、奥行きを 64 段に分けた、3D テクスチャ。散乱・消散係数を、書く。
D3D11_TEXTURE3D_DESC desc = {};
desc.Width = 160;
desc.Height = 90;
desc.Depth = 64;
desc.MipLevels = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;                  // rgb: 散乱光、a: 消散係数
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;
device->CreateTexture3D(&desc, nullptr, &froxel_texture);
device->CreateShaderResourceView(froxel_texture.Get(), nullptr, &froxel_srv);
device->CreateUnorderedAccessView(froxel_texture.Get(), nullptr, &froxel_uav);
```

3D テクスチャの、大きさは、`160×90×64` で、約 90 万セルです。画面の 1/12 の、解像度で、十分な、なめらかさが、得られます。

### ディスパッチ

```cpp
// 1 スレッド = 1 セル。8×8×1 のグループで、奥行き方向は、1 層ずつ。
context->CSSetUnorderedAccessViews(0, 1, froxel_uav.GetAddressOf(), nullptr);
context->Dispatch((160 + 7) / 8, (90 + 7) / 8, 64);           // グループ数 = (20, 12, 64)
```

深度方向を、`Dispatch` の、第 3 引数に、割り当てると、`SV_DispatchThreadID.z` が、そのまま、奥行きの、段の番号になります。

### 3 つのステップを、つなぐ

```cpp
// ① 密度: 各セルの、霧の濃さ。② 注入: 各セルの、光を、計算。③ 積分: 奥へ、散乱光と、透過率を、足し込む。
Dispatch(density_cs, {noise_srv}, {froxel_uav}, 20, 12, 64);
Dispatch(inject_cs, {froxel_srv, shadow_srv}, {froxel_light_uav}, 20, 12, 64);     // 入力と出力は、別のテクスチャにする
Dispatch(integrate_cs, {froxel_light_srv}, {froxel_integrated_uav}, 20, 12, 1);    // 奥行きは、シェーダーの中で、ループ
```

積分のパスだけ、奥行き方向の、ディスパッチが、1 です。奥行き方向は、前から後ろへ、累積する（前の層の結果に、依存する）ので、1 つのスレッドが、奥行きを、ループします。結果は、画面に、霧を、描くとき、画素の、深度から、froxel を、引いて、使います（[Integration](integration.md)）。

''', before="## よくあるミス")

# ---------------------------------------------------------------- FFT ocean
pg.Add("water/waves/fft-ocean.md", '''
## DirectX 11 で組む

### テクスチャ

```cpp
const UINT N = 256;                                              // 1 タイルの、格子の数（2 のべき乗）
// 周波数空間の、複素数（実部・虚部）を、R32G32_FLOAT で持つ。UAV と SRV の両方で使う。
auto MakeComplexTexture = [&](Microsoft::WRL::ComPtr<ID3D11ShaderResourceView>& srv,
                              Microsoft::WRL::ComPtr<ID3D11UnorderedAccessView>& uav) {
  D3D11_TEXTURE2D_DESC desc = {N, N, 1, 1, DXGI_FORMAT_R32G32_FLOAT, {1, 0}, D3D11_USAGE_DEFAULT,
                               D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS, 0, 0};
  Microsoft::WRL::ComPtr<ID3D11Texture2D> t;
  device->CreateTexture2D(&desc, nullptr, &t);
  device->CreateShaderResourceView(t.Get(), nullptr, &srv);
  device->CreateUnorderedAccessView(t.Get(), nullptr, &uav);
};
// 高さ・水平変位 X・水平変位 Z の、それぞれに、2 枚（FFT のピンポン用）が要る。
```

複素数は、`R32G32_FLOAT` の、2 チャンネル（x = 実部、y = 虚部）で、持ちます。FFT の、途中の、精度が、必要なので、16 ビットでなく、32 ビットの、浮動小数に、します。最終的な、水面の、テクスチャ（高さ、変位、法線、泡）は、`R16G16B16A16_FLOAT` で、足ります。

### 毎フレームの、ディスパッチ

```cpp
const UINT groups = N / 8;
// ① 時間発展: h0 から、時刻 t のスペクトルを作る（Evolve）。
Dispatch(evolve_cs, {h0_srv}, {height_k_uav, dx_k_uav, dz_k_uav}, groups, groups, 1);

// ② 逆 FFT: 横方向 log2(N) 段 → 縦方向 log2(N) 段。段ごとに、入力と出力を、入れ替える（ピンポン）。
const int stages = 8;                                            // log2(256)
for (int s = 0; s < stages; ++s) {
  SetFftStage(s);                                                // 定数バッファに、段の番号
  DispatchButterfly(horizontal_cs, ping, pong, groups, groups);
  std::swap(ping, pong);
}
for (int s = 0; s < stages; ++s) {
  SetFftStage(s);
  DispatchButterfly(vertical_cs, ping, pong, groups, groups);
  std::swap(ping, pong);
}

// ③ 結果を、水面用のテクスチャにまとめる（高さ・水平変位・法線・ヤコビアン）。
Dispatch(assemble_cs, {height_srv, dx_srv, dz_srv}, {displacement_uav}, groups, groups, 1);
context->GenerateMips(displacement_srv.Get());                  // 遠くの水面は、ミップで読む（ちらつきを、減らす）
```

1 回の FFT が、段の数（`log2 N`）だけ、ディスパッチを、呼ぶので、`N = 256` なら、横 8 回、縦 8 回の、計 16 回です。1 回ごとに、UAV を、外して、次の、SRV として、読む、束縛の入れ替えが、必要です（[D3D11 Pass Recipes](../../d3d11-recipes.md)）。`GenerateMips` を、使うには、テクスチャに、`D3D11_BIND_RENDER_TARGET` と `D3D11_RESOURCE_MISC_GENERATE_MIPS` が、必要です。

''', before="## カスケード（繰り返しを隠す）")

# ---------------------------------------------------------------- SSR basics host
pg.Add("reflections/ssr-basics/index.md", '''
## DirectX 11 で組む

### 必要な入力

SSR は、次の 4 つを、必要とします。

| 入力 | 作り方 |
| --- | --- |
| 深度 | `R32_TYPELESS` の深度（DSV と SRV）。SSR の前に、DSV を、外す |
| 法線 | G バッファの、法線のターゲット |
| 粗さ・金属度 | G バッファの、材質のターゲット |
| 前フレームの、色 | 前のフレームの、最終色（HDR）を、ピンポンで、保存 |

### パス

```cpp
// SSR の出力: 反射色と、信頼度（a）。HDR で、半分の解像度でも、よい。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width / 2;                                          // 半分の解像度（コストが約 1/4）
desc.Height = height / 2;
desc.MipLevels = desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;                   // rgb: 反射色、a: 信頼度
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &ssr_texture);
```

```cpp
// SSR を描く。深度・法線・材質・前フレームの色を、読む。サンプラーは、深度が POINT、色が LINEAR。
context->OMSetRenderTargets(1, ssr_rtv.GetAddressOf(), nullptr);
ID3D11ShaderResourceView* srvs[] = {depth_srv.Get(), normal_srv.Get(), material_srv.Get(), prev_color.Read()};
context->PSSetShaderResources(0, 4, srvs);
ID3D11SamplerState* samplers[] = {point_clamp.Get(), linear_clamp.Get()};
context->PSSetSamplers(0, 2, samplers);
DrawFullscreenTriangle();
```

結果は、ライティングの、パスで、反射プローブと、信頼度で、混ぜて、間接鏡面光として、足します（[Combining with SSR](../probes/combine-ssr.md)）。深度を、DSV から、外し忘れると、`depth_srv` が、黒くなって、SSR が、何も、当たらなくなります（[D3D11 Pass Recipes](../../d3d11-recipes.md)）。

''', before="## よくあるミス")

# ---------------------------------------------------------------- motion blur / DoF flow host
pg.Add("postprocess/motion-blur/index.md", '''
## DirectX 11 で組む

### 速度バッファを、G バッファに、混ぜる

```cpp
// 速度は、G バッファの MRT の 1 枚として、ジオメトリのパスで、同時に書く。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16_FLOAT;                         // 画面上のずれ（UV 単位）。負の値も持てる
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &velocity_texture);
```

動く物は、ジオメトリのパスで、速度を、書きます。動かない物（背景）は、カメラの動きだけで、決まるので、速度を、書く必要が、なく、パスの、最後に、深度から、計算して、補います（[Velocity Buffer](velocity-buffer.md)）。

### 3 つのパス

```cpp
// ① タイル最大: 速度を、16×16 画素のタイルごとの、最大に、縮める（計算シェーダー）。
const UINT tile = 16;
Dispatch(tile_max_cs, {velocity_srv}, {tile_max_uav}, (width + tile - 1) / tile, (height + tile - 1) / tile, 1);

// ② 近傍最大: 周りの 3×3 タイルの、最大を、取る（広がりを、隣へ伝える）。
Dispatch(neighbor_max_cs, {tile_max_srv}, {neighbor_max_uav}, tile_groups_x, tile_groups_y, 1);

// ③ ブラー: 近傍最大の方向へ、シーン色を、サンプル（フルスクリーン）。
context->OMSetRenderTargets(1, motion_blur_rtv.GetAddressOf(), nullptr);
ID3D11ShaderResourceView* srvs[] = {scene_srv.Get(), velocity_srv.Get(), depth_srv.Get(), neighbor_max_srv.Get()};
context->PSSetShaderResources(0, 4, srvs);
DrawFullscreenTriangle();
```

タイル最大は、「このタイルの近くで、最も速く動く物は、どちらへ、動いているか」を、教えます。ブラーのパスは、この方向を、基準に、サンプルするので、速い物の、輪郭の、外側まで、にじみます（[Tile Max](tile-max.md)）。

''', before="## 関連ページ")

pg.Add("postprocess/dof/index.md", '''
## DirectX 11 で組む

```cpp
// ① CoC（錯乱円の大きさ）: 深度から、符号付きの CoC を計算し、シーン色と、一緒に出す。
//    出力: rgb = シーン色、a = CoC（手前は負、奥は正）。HDR のまま。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &coc_color_texture);
```

```cpp
// ② 半解像度に縮小（CoC で重みを付けて）→ ③ 近景・遠景を、別々に、ぼかす（ギャザー）→ ④ フル解像度に合成。
SetViewport(width / 2, height / 2);
Draw(downsample_coc_ps, {coc_color_srv}, {half_rtv});
Draw(gather_ps, {half_srv}, {far_blur_rtv, near_blur_rtv});            // 2 枚の MRT に、近景と遠景を、別々に出す
SetViewport(width, height);
Draw(composite_ps, {scene_srv, far_blur_srv, near_blur_srv, coc_color_srv}, {final_rtv});
```

ギャザーを、半解像度で行うと、コストが、約 1/4 に、なります。近景と、遠景を、別々の、ターゲットに、出すのは、近景のボケは、手前の物の、輪郭を、越えて、奥へ、にじむ（遠景は、越えない）という、性質の違いを、合成の時点で、扱うためです（[Near and Far Fields](near-far.md)）。

''', before="## 関連ページ")
print("ok")
