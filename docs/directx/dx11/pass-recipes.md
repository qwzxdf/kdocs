---
title: D3D11 Pass Recipes
tags:
  - DirectX
---

# D3D11 Pass Recipes

描画セクションの各ページには HLSL のコードがあります。しかし、シェーダーだけでは画面に何も出ません。<strong>テクスチャを作りビューを作りパスの順に束ねて描く（または、ディスパッチする）</strong>というホスト側（C++）の仕事が必要です。このページは各ページで繰り返し使うその定型を 1 か所にまとめます。以降のページはここにある部品を組み合わせてパスを作る前提で、書かれています。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））


## このページで扱うもの

| 部品 | 使う場面 |
| --- | --- |
| 1 つのテクスチャに 3 種類のビュー | G バッファ、HDR のシーン色、AO、ブルーム、ほぼ全部 |
| フルスクリーン三角形 | ポスト プロセス、ライティング、合成、全画面のパス |
| 計算シェーダーのディスパッチ | ぼかし、ヒストグラム、froxel、プローブ更新 |
| 定数バッファの更新 | 毎フレーム変わるパラメータ |
| 束縛の衝突（同じ物を読みつつ書く） | あらゆるパスのつなぎ目 |
| ピンポン | 時間方向の蓄積（TAA、泡、波） |
| 深度（typeless） | シャドウ マップ、SSAO、SSR |
| ステート（ブレンド・深度・ラスタライザー） | 半透明、シャドウ、ポスト プロセス |
| GPU タイマー | 各パスのミリ秒を測る |

## 1 つのテクスチャ、複数のビュー

D3D11 ではテクスチャ（リソース）そのものは、パイプラインに束ねられません。<strong>ビュー</strong>（RTV、SRV、UAV、DSV）を通して束ねます。同じテクスチャに複数のビューを作ると、「書いたパスの出力」を「次のパスの入力」にできます。

```cpp
// 1 枚の HDR テクスチャ。描く（RTV）、読む（SRV）、計算シェーダーで書く（UAV）の、3 通りに使う。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;                       // HDR のシーン色
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;
Microsoft::WRL::ComPtr<ID3D11Texture2D> texture;
device->CreateTexture2D(&desc, nullptr, &texture);
```

`BindFlags` に使う予定のビューの種類をすべて書きます。書かなかった種類のビューはあとから作れません。`UNORDERED_ACCESS` を付けると `R16G16B16A16_FLOAT` は D3D11 の機能レベル 11 で、サポートされます。

```cpp
// 3 種類のビュー。リソースは 1 つで、見る窓が 3 つ。
device->CreateRenderTargetView(texture.Get(), nullptr, &rtv);       // 描く: ピクセル シェーダーの出力先
device->CreateShaderResourceView(texture.Get(), nullptr, &srv);     // 読む: Texture2D として
device->CreateUnorderedAccessView(texture.Get(), nullptr, &uav);    // 書く: RWTexture2D として（計算シェーダー）
```

`nullptr` を渡すとリソースと同じ形式の既定のビューができます。ミップや配列の一部だけを見せたいときだけ記述子を指定します。

### フォーマットの選び方

| 用途 | フォーマット | 理由 |
| --- | --- | --- |
| HDR のシーン色 | `R16G16B16A16_FLOAT` | 1 を超える明るさを保てる。ブルーム、露出、トーン マッピングの前提 |
| 法線（G バッファ） | `R10G10B10A2_UNORM`、または `R16G16_FLOAT`（八面体） | 精度と帯域のバランス |
| アルベド・粗さ・金属度 | `R8G8B8A8_UNORM`（sRGB でない）／`R8G8B8A8_UNORM_SRGB`（色） | アルベドは、sRGB ビューで読むと自動で、リニアになる |
| AO・影・マスク（1 チャンネル） | `R8_UNORM`、または `R16_FLOAT` | 1 チャンネルで、足りる。帯域が小さい |
| 速度（モーション ベクトル） | `R16G16_FLOAT` | 画面のずれを負の値も含めて持つ |
| 深度 | `R32_TYPELESS`（DSV: `D32_FLOAT`、SRV: `R32_FLOAT`） | 次の節 |
| 最終的な画面 | スワップ チェーンは `R8G8B8A8_UNORM`、RTV を `R8G8B8A8_UNORM_SRGB` で作る | フリップ モデルは `_SRGB` を直接指定できない（[Swap Chain](swap-chain.md)）。RTV を `_SRGB` にしてリニアから sRGB への変換をハードウェアに任せる |

## フルスクリーン三角形

ポスト プロセスやライティングは画面全体にパスを走らせます。画面を覆う四角形（三角形 2 枚）を描く代わりに <strong>画面より大きな三角形 1 枚</strong>を描きます。頂点バッファは要りません。

```hlsl
// 頂点 ID（0, 1, 2）だけから、画面を覆う、1 枚の三角形を作る。
struct VSOut {
  float4 position : SV_Position;
  float2 uv : TEXCOORD0;
};

VSOut FullscreenVS(uint id : SV_VertexID) {
  VSOut o;
  o.uv = float2((id << 1) & 2, id & 2);                        // (0,0) (2,0) (0,2)
  o.position = float4(o.uv * float2(2, -2) + float2(-1, 1), 0, 1);   // クリップ空間: (-1,1) (3,1) (-1,-3)
  return o;
}
```

`id` が 0、1、2 のとき `uv` は(0, 0)、(2, 0)、(0, 2) になりクリップ空間では、(−1, 1)、(3, 1)、(−1, −3) です。この三角形は画面（−1〜1）をすっぽり覆いはみ出した部分は、クリッピングで捨てられます。四角形と違い <strong>対角線が無い</strong>ので、対角線に沿った 2 回描きや境目のずれが、起きません。

```cpp
// 描く側: 頂点バッファも、入力レイアウトも、要らない。
context->IASetInputLayout(nullptr);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
context->VSSetShader(fullscreen_vs.Get(), nullptr, 0);
context->Draw(3, 0);                                           // 頂点 3 つ
```

`Draw(3, 0)` の 1 回で全画素にピクセル シェーダーが走ります。座標系は右手系 Y-up、前は −Z ですが画面の uv は左上が原点（Y が下向き）なので `uv.y` を反転してクリップ空間に直しています。

## 計算シェーダーのディスパッチ

画面全体のぼかしやヒストグラムのような「1 画素 = 1 スレッド」の処理は、計算シェーダーで書けます。

```hlsl
// 8×8 スレッドで、1 グループ。1 スレッドが 1 画素を受け持つ。
RWTexture2D<float4> g_output : register(u0);
Texture2D<float4> g_input : register(t0);

[numthreads(8, 8, 1)]
void MainCS(uint3 id : SV_DispatchThreadID) {
  uint width, height;
  g_output.GetDimensions(width, height);
  if (id.x >= width || id.y >= height) return;                 // 端の余り: 画面の外のスレッドは、何もしない
  g_output[id.xy] = g_input.Load(int3(id.xy, 0));
}
```

グループの大きさが 8×8 なので、画面の大きさが 8 の倍数でないとき最後のグループの一部のスレッドは、画面の外に出ます。必ず範囲チェックを入れます。

```cpp
// グループ数は、画面をグループの大きさで、割って、切り上げる。
UINT groups_x = (width + 7) / 8;
UINT groups_y = (height + 7) / 8;

context->CSSetShader(cs.Get(), nullptr, 0);
context->CSSetShaderResources(0, 1, srv.GetAddressOf());
context->CSSetUnorderedAccessViews(0, 1, uav.GetAddressOf(), nullptr);
context->Dispatch(groups_x, groups_y, 1);
```

`(width + 7) / 8` は切り上げの整数除算です。UAV を束ねるとき最後の引数はカウンターの初期値（通常は `nullptr` で、無視）です。

## 定数バッファの更新

毎フレーム変わるパラメータ（カメラ、時間、パスごとの設定）は定数バッファで、渡します。

```cpp
// HLSL の cbuffer と、同じ並びの、構造体。float4 の境界（16 バイト）にそろえる。
struct PassConstants {
  DirectX::XMFLOAT4X4 view_projection;
  DirectX::XMFLOAT3 camera_position;
  float time;
  DirectX::XMFLOAT2 screen_size;
  DirectX::XMFLOAT2 inv_screen_size;
};
static_assert(sizeof(PassConstants) % 16 == 0, "定数バッファは、16 バイトの倍数");

D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(PassConstants);
desc.Usage = D3D11_USAGE_DYNAMIC;                              // 毎フレーム、CPU から書く
desc.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
desc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
device->CreateBuffer(&desc, nullptr, &constant_buffer);
```

`cbuffer` の中身は 16 バイト（`float4`）の境目をまたぐメンバーを置けません。`float3` の次に `float` を置くのは 4 バイトで境目に収まるので問題ありませんが `float3` の次に `float3` を置くと、2 つ目が次の 16 バイトへ押し出されます。C++ 側の構造体とずれる典型的な原因です。`static_assert` でサイズを確かめます。

```cpp
// 毎フレーム: WRITE_DISCARD で、バッファを丸ごと、書き換える。
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(constant_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);
std::memcpy(mapped.pData, &constants, sizeof(constants));
context->Unmap(constant_buffer.Get(), 0);
context->VSSetConstantBuffers(0, 1, constant_buffer.GetAddressOf());
context->PSSetConstantBuffers(0, 1, constant_buffer.GetAddressOf());
```

`WRITE_DISCARD` は GPU がまだ前のフレームの内容を読んでいても待たずに新しい領域を割り当てます。行列は `XMMatrixTranspose` で転置してから書くか HLSL 側で `row_major` を付けてそろえます（行ベクトル、`v * M` の規約）。

## 束縛の衝突：読みながら、書けない

<strong>同じリソースを同時に読む（SRV）と書く（RTV、UAV、DSV）</strong>ことはできません。D3D11 はエラーを出さずに読む側の束縛を黙って外します。結果は真っ黒のテクスチャです。

```cpp
// パス A の出力（texture_a）をパス B の入力に使う前に A の書き込み先を外す。
ID3D11RenderTargetView* null_rtv = nullptr;
context->OMSetRenderTargets(1, &null_rtv, nullptr);            // 書き込みの束縛を外す
context->PSSetShaderResources(0, 1, srv_a.GetAddressOf());     // これで、安全に読める
```

パスを切り替えるたびに次の順で、行います。前のパスの出力を外し次のパスの入力を束ね新しい出力を束ねる。シェーダー リソースを先に外すほうが安全で `ID3D11ShaderResourceView* nulls[8] = {}` を `PSSetShaderResources(0, 8, nulls)` に渡して一括で、外します。デバッグ レイヤーを有効にすると `D3D11 WARNING: ... Resource being set to OM RenderTarget slot 0 is still bound on input` と警告が出ます。

## ピンポン：前のフレームを読みつつ今のフレームを書く

泡、波の高さ TAA の履歴のように「前の結果」を使って「今の結果」を作る処理は同じ内容のテクスチャを 2 枚用意して毎フレーム、読み書きを入れ替えます。

```cpp
// 2 枚のテクスチャ（それぞれ RTV と SRV を持つ）を交互に入力と出力にする。
struct PingPong {
  Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv[2];
  Microsoft::WRL::ComPtr<ID3D11RenderTargetView> rtv[2];
  int current = 0;                                             // 今、読むほう
  ID3D11ShaderResourceView* Read() { return srv[current].Get(); }
  ID3D11RenderTargetView* Write() { return rtv[1 - current].Get(); }
  void Swap() { current = 1 - current; }
};
```

`Read()` が前のフレームの結果、`Write()` が今のフレームの出力先です。パスの終わりに `Swap()` を呼ぶと次のフレームでは役割が入れ替わります。最初のフレームは履歴が無いので、黒（または今のフレームの値）で、初期化します。

## 深度：typeless で書く読む

深度を書き込み（DSV）と読み込み（SRV）の両方で、使うには `TYPELESS` のフォーマットで作りビューごとに型を決めます（シャドウ マップ、SSAO、SSR で必須）。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;                        // 型は、ビューで決める
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &depth_texture);

D3D11_DEPTH_STENCIL_VIEW_DESC dsv_desc = {};
dsv_desc.Format = DXGI_FORMAT_D32_FLOAT;                       // 書く: 深度として
dsv_desc.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_texture.Get(), &dsv_desc, &dsv);

D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_R32_FLOAT;                       // 読む: 通常の float として
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv_desc.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(depth_texture.Get(), &srv_desc, &depth_srv);
```

DSV を束ねたまま同じ深度を SRV で読むと先の節の「束縛の衝突」になります。AO の前に `OMSetRenderTargets` で DSV を外します。読み取り専用の DSV（`D3D11_DSV_READ_ONLY_DEPTH`）を作ると、深度テストはしつつ同じ深度を SRV で読めます（半透明のソフト パーティクルなど）。

## ステート：ブレンド・深度・ラスタライザー

パスごとに必要なステートが違います。ステートは `Create*State` で一度だけ作りパスで `OMSet*` で、切り替えます。

```cpp
// 半透明の、通常のアルファ ブレンド（奥から手前の、順に描く）。
D3D11_BLEND_DESC blend = {};
auto& rt = blend.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOp = D3D11_BLEND_OP_ADD;
rt.SrcBlendAlpha = D3D11_BLEND_ONE;
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&blend, &alpha_blend);
```

```cpp
// 深度テストだけ（書き込みは、しない）。半透明、ソフト パーティクル、ポスト プロセスの、背景判定。
D3D11_DEPTH_STENCIL_DESC depth = {};
depth.DepthEnable = TRUE;
depth.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;            // 書かない
depth.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
device->CreateDepthStencilState(&depth, &depth_test_only);

// ポスト プロセスは、深度テストも書き込みも、要らない。
D3D11_DEPTH_STENCIL_DESC none = {};
none.DepthEnable = FALSE;
device->CreateDepthStencilState(&none, &depth_off);
```

```cpp
// シャドウ パス: 面の表裏、深度バイアスをラスタライザー ステートで、指定する。
D3D11_RASTERIZER_DESC raster = {};
raster.FillMode = D3D11_FILL_SOLID;
raster.CullMode = D3D11_CULL_BACK;
raster.FrontCounterClockwise = TRUE;                           // 三角形は、反時計回りが、表（右手系）
raster.DepthBias = 1000;                                       // 整数のバイアス（深度の最小単位に対する、倍数）
raster.SlopeScaledDepthBias = 2.0f;                            // 面の傾きに、比例する、バイアス
raster.DepthClipEnable = TRUE;
device->CreateRasterizerState(&raster, &shadow_raster);
```

`FrontCounterClockwise = TRUE` はこのサイトの規約（三角形は CCW が表）に合わせた設定です。`DepthBias` の単位は深度フォーマットに依存するので調整が必要です（[Shadow Bias](../../graphics/shadows/bias/index.md)）。

## パスのつなぎ方：全体の骨格

ここまでの部品を組み合わせると、1 フレームは次の骨格になります。

```cpp
// 1 フレームの、骨格。各パスの、詳しい中身は、各ページの「DirectX 11 で…」の節を参照。
void RenderFrame() {
  UpdatePassConstants();                                        // 定数バッファを更新

  // ① シャドウ: 光源から見た深度を描く（DSV だけ。ピクセル シェーダーなし）
  RenderShadowMaps();

  // ② ジオメトリ: G バッファ（MRT）と、深度を描く
  context->OMSetRenderTargets(kGBufferCount, gbuffer_rtv, depth_dsv.Get());
  DrawOpaqueGeometry();

  // ③ スクリーン空間のパス: AO、SSR など（深度と法線を SRV で読む。DSV は、外す）
  context->OMSetRenderTargets(0, nullptr, nullptr);
  RunAmbientOcclusion();

  // ④ ライティング: フルスクリーン三角形で、HDR のシーン色を作る
  context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), nullptr);
  RunLighting();

  // ⑤ 半透明・大気・水: 深度テストだけで、HDR に重ねる
  context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), depth_readonly_dsv.Get());
  DrawTranslucent();

  // ⑥ ポスト プロセス: ブルーム、露出、トーン マッピングで、LDR の画面へ
  RunPostProcess();
  swap_chain->Present(1, 0);
}
```

パスの順は「深度が先、色が後」「不透明が先、半透明が後」「HDR のうちに光の計算、LDR に落とすのは最後」の 3 つの原則で、決まります。

## GPU タイマー：パスのミリ秒を測る

このセクションの各ページにある、ミリ秒の目安は自分の環境で測れます。

```cpp
// タイムスタンプ クエリ。フレームの開始と終了、パスの開始と終了を記録する。
D3D11_QUERY_DESC q = {};
q.Query = D3D11_QUERY_TIMESTAMP_DISJOINT;
device->CreateQuery(&q, &disjoint_query);
q.Query = D3D11_QUERY_TIMESTAMP;
device->CreateQuery(&q, &start_query);
device->CreateQuery(&q, &end_query);

context->Begin(disjoint_query.Get());
context->End(start_query.Get());          // 計測したいパスの、直前
RunPass();
context->End(end_query.Get());            // 直後
context->End(disjoint_query.Get());
```

```cpp
// 数フレーム後に結果を読む（すぐに読むと、GPU の完了を待って、止まる）。
D3D11_QUERY_DATA_TIMESTAMP_DISJOINT disjoint;
UINT64 t0, t1;
if (context->GetData(disjoint_query.Get(), &disjoint, sizeof(disjoint), 0) == S_OK && !disjoint.Disjoint &&
    context->GetData(start_query.Get(), &t0, sizeof(t0), 0) == S_OK &&
    context->GetData(end_query.Get(), &t1, sizeof(t1), 0) == S_OK) {
  double ms = double(t1 - t0) / double(disjoint.Frequency) * 1000.0;
}
```

`Disjoint` が `TRUE` のフレーム（クロックが途中で、変わった）は捨てます。結果は 1 フレーム以上、遅れて取り出す（複数のクエリをリングで回す）と CPU が GPU を待たずに済みます。

## よくあるミス

??? failure "真っ黒、または前のフレームのままで描かれない"
    同じリソースを読みつつ書いている（束縛の衝突）。パスのつなぎ目で `OMSetRenderTargets(0, nullptr, nullptr)` や `PSSetShaderResources` に `nullptr` を渡して外す。デバッグ レイヤーの警告で見つかる。

??? failure "定数バッファの値がずれる"
    HLSL の `cbuffer` は 16 バイトの境目をまたげない。C++ の構造体にパディングを入れ `static_assert(sizeof(...) % 16 == 0)` で、確かめる。行列は転置が必要か確かめる。

??? failure "画面の右端・下端が処理されないまたはメモリ外に書く"
    計算シェーダーのグループ数を切り捨てで計算した（`width / 8`）、または範囲チェックが無い。`(width + 7) / 8` にしてシェーダーで `id.x >= width` を確かめる。

??? failure "深度を SRV で読むとエラーになる"
    深度を `D32_FLOAT` で作ると SRV を作れない。`R32_TYPELESS` で作り DSV と SRV で、別の型を指定する。

??? failure "HDR が、白飛び・暗いまま"
    シーン色を `R8G8B8A8_UNORM` で作っている（1 を超える値が切れる）。`R16G16B16A16_FLOAT` にしトーン マッピングで、LDR に落とす。

## これだけ覚える

!!! abstract "まとめ"
    - [x] テクスチャは 1 つビュー（RTV・SRV・UAV・DSV）は、用途ごとに作る。`BindFlags` は最初に全部書く
    - [x] 全画面のパスは頂点バッファなしのフルスクリーン三角形（`Draw(3, 0)`）
    - [x] 計算シェーダーは、`(size + 7) / 8` グループ。範囲チェックを入れる
    - [x] 定数バッファは 16 バイト境界。`WRITE_DISCARD` で毎フレーム更新
    - [x] 読みながら、書けない。パスのつなぎ目で束縛を外す
    - [x] 深度は `R32_TYPELESS`。DSV と SRV で型を分ける
    - [x] 前の結果を使うときはピンポン

## 関連ページ

- [Shadow Map Basics](../../graphics/shadows/shadow-map-basics/index.md)
- [Typical Pipeline](../../graphics/ao/filtering/pipeline.md)
- [Post-Processing](../../graphics/postprocess/index.md)
- [フレームの流れ](../../3d/render-flow/frame-passes.md)
- [Microsoft Learn: Direct3D 11 Graphics](https://learn.microsoft.com/ja-jp/windows/win32/direct3d11/atoc-dx-graphics-direct3d-11)
