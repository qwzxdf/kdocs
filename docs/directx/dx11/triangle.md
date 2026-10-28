---
title: Drawing a Triangle
tags:
  - DirectX
---

# Drawing a Triangle

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

ここまでのページで作った部品（ウィンドウ、デバイス、スワップ チェーン、RTV、シェーダー、頂点バッファ、入力レイアウト）を <strong>パイプラインにつないで三角形を描きます</strong>。D3D11 の「Hello World」です。描画が 1 つ通ればあとはこの骨格の上に積み重ねていくだけです。

!!! tip "ポイント"
    - 描くには <strong>入力アセンブラー（IA）→ 頂点シェーダー（VS）→ ラスタライザー（RS）→ ピクセル シェーダー（PS）→ 出力マージャー（OM）</strong>に、必要な物をすべてつなぐ。
    - 1 つでもつなぎ忘れると何も描かれない（エラーも出ないことが、多い）。
    - 毎フレーム、<strong>束ねる → クリア → 描く → Present</strong>。
    - 三角形が見えないときは「裏面」「ビューポート」「束縛の忘れ」を疑う。
    - ステートを作らないと既定（深度テスト有り裏面カリング有りブレンド無し）で描かれる。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## パイプラインのつなぎ方

```text
IASetInputLayout        … 頂点の並び
IASetVertexBuffers      … 頂点データ
IASetPrimitiveTopology  … 三角形リスト
VSSetShader             … 頂点シェーダー
RSSetViewports          … 画面のどこに描くか
RSSetState              … 面の向き・カリング（既定でよいなら省略）
PSSetShader             … ピクセル シェーダー
OMSetRenderTargets      … 描き込み先
Draw                    … 実行
```

D3D11 は状態を持つ API です。一度設定した束縛は次の設定まで、残るので毎フレーム、全部を設定し直す必要はありませんが、<strong>`Present` の後で外れるもの（レンダー ターゲット）</strong>は、設定し直します。

## 描画を 1 つずつ

### 入力アセンブラー（IA）

```cpp
context->IASetInputLayout(input_layout.Get());

const UINT stride = sizeof(Vertex);
const UINT offset = 0;
context->IASetVertexBuffers(0, 1, vertex_buffer.GetAddressOf(), &stride, &offset);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
```

「頂点をどう読みどうつなぐか」を決めます。ここまでは[Input Layout](input-layout.md) と [Vertex Buffer](vertex-buffer.md) の、内容です。

### 頂点シェーダーとピクセル シェーダー

```cpp
context->VSSetShader(vertex_shader.Get(), nullptr, 0);     // 第 2・3 引数: クラス インスタンス（使わない）
context->PSSetShader(pixel_shader.Get(), nullptr, 0);
```

使うシェーダーをつなぎます（[Shaders and Compilation](shaders.md)）。ジオメトリ、ハル、ドメイン シェーダーを使わない間は設定しません（前に設定した物が残らないよう `nullptr` で外す）。

### ラスタライザーと出力

```cpp
D3D11_VIEWPORT viewport = {0.0f, 0.0f, static_cast<float>(width), static_cast<float>(height), 0.0f, 1.0f};
context->RSSetViewports(1, &viewport);
context->RSSetState(rasterizer_state.Get());               // このサイトの規約: 反時計回りが表（下）

ID3D11RenderTargetView* targets[] = {rtv.Get()};
context->OMSetRenderTargets(1, targets, nullptr);
```

ビューポートは[Viewport](viewport.md)、描き込み先は[Render Target View (RTV)](render-target-view.md) です。

### 描く

```cpp
context->Draw(3, 0);
```

`Draw(頂点の数, 開始位置)` で頂点シェーダーが 3 回、呼ばれ 3 頂点が 1 つの三角形になります。ラスタライザーが三角形の内側のピクセルを列挙しピクセル シェーダーが各ピクセルで呼ばれます。

## 面の向き（カリング）

D3D11 の既定は <strong>時計回り（CW）が表</strong>で、<strong>裏面は捨てます</strong>。このサイトの規約は <strong>反時計回り（CCW）が表</strong>なので、ラスタライザー ステートを作って、合わせます。

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.FillMode = D3D11_FILL_SOLID;
desc.CullMode = D3D11_CULL_BACK;                           // 裏面を捨てる
desc.FrontCounterClockwise = TRUE;                         // 反時計回りを表とする
desc.DepthClipEnable = TRUE;
device->CreateRasterizerState(&desc, &rasterizer_state);
```

`FrontCounterClockwise` を設定せずに反時計回りの三角形を描くと裏面とみなされて <strong>何も見えません</strong>。三角形が見えないときの最初の疑いどころです（[Rasterizer State](rasterizer-state.md)）。

## 動く完全なプログラム

ここまでの部品を 1 つにまとめた完成形です。`triangle.hlsl` は[Shaders and Compilation](shaders.md) のシェーダーです。

```cpp
#include <d3d11.h>
#include <d3dcompiler.h>
#include <dxgi1_2.h>
#include <windows.h>
#include <wrl/client.h>

#include <DirectXMath.h>

using Microsoft::WRL::ComPtr;

struct Vertex {
  DirectX::XMFLOAT3 position;
  DirectX::XMFLOAT4 color;
};

ComPtr<ID3D11Device> g_device;
ComPtr<ID3D11DeviceContext> g_context;
ComPtr<IDXGISwapChain1> g_swap_chain;
ComPtr<ID3D11RenderTargetView> g_rtv;
ComPtr<ID3D11VertexShader> g_vertex_shader;
ComPtr<ID3D11PixelShader> g_pixel_shader;
ComPtr<ID3D11InputLayout> g_input_layout;
ComPtr<ID3D11Buffer> g_vertex_buffer;
ComPtr<ID3D11RasterizerState> g_rasterizer_state;
UINT g_width = 1280, g_height = 720;

ComPtr<ID3DBlob> Compile(const wchar_t* path, const char* entry, const char* target) {
  ComPtr<ID3DBlob> code, errors;
  if (FAILED(D3DCompileFromFile(path, nullptr, D3D_COMPILE_STANDARD_FILE_INCLUDE, entry, target,
                                D3DCOMPILE_ENABLE_STRICTNESS, 0, &code, &errors))) {
    if (errors) OutputDebugStringA(static_cast<const char*>(errors->GetBufferPointer()));
    return nullptr;
  }
  return code;
}

void CreateRenderTarget() {
  ComPtr<ID3D11Texture2D> back_buffer;
  g_swap_chain->GetBuffer(0, IID_PPV_ARGS(&back_buffer));
  D3D11_RENDER_TARGET_VIEW_DESC desc = {};
  desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
  desc.ViewDimension = D3D11_RTV_DIMENSION_TEXTURE2D;
  g_device->CreateRenderTargetView(back_buffer.Get(), &desc, &g_rtv);
}

void InitD3D(HWND hwnd) {
  UINT flags = D3D11_CREATE_DEVICE_BGRA_SUPPORT;
#if defined(_DEBUG)
  flags |= D3D11_CREATE_DEVICE_DEBUG;
#endif
  const D3D_FEATURE_LEVEL levels[] = {D3D_FEATURE_LEVEL_11_1, D3D_FEATURE_LEVEL_11_0};
  D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, flags, levels, ARRAYSIZE(levels),
                    D3D11_SDK_VERSION, &g_device, nullptr, &g_context);

  ComPtr<IDXGIDevice> dxgi_device;
  g_device.As(&dxgi_device);
  ComPtr<IDXGIAdapter> adapter;
  dxgi_device->GetAdapter(&adapter);
  ComPtr<IDXGIFactory2> factory;
  adapter->GetParent(IID_PPV_ARGS(&factory));

  DXGI_SWAP_CHAIN_DESC1 sc = {};
  sc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
  sc.SampleDesc.Count = 1;
  sc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
  sc.BufferCount = 2;
  sc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;
  factory->CreateSwapChainForHwnd(g_device.Get(), hwnd, &sc, nullptr, nullptr, &g_swap_chain);
  factory->MakeWindowAssociation(hwnd, DXGI_MWA_NO_ALT_ENTER);
  CreateRenderTarget();

  auto vs = Compile(L"triangle.hlsl", "VSMain", "vs_5_0");
  auto ps = Compile(L"triangle.hlsl", "PSMain", "ps_5_0");
  g_device->CreateVertexShader(vs->GetBufferPointer(), vs->GetBufferSize(), nullptr, &g_vertex_shader);
  g_device->CreatePixelShader(ps->GetBufferPointer(), ps->GetBufferSize(), nullptr, &g_pixel_shader);

  const D3D11_INPUT_ELEMENT_DESC elements[] = {
      {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0},
      {"COLOR", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D11_INPUT_PER_VERTEX_DATA, 0},
  };
  g_device->CreateInputLayout(elements, ARRAYSIZE(elements), vs->GetBufferPointer(), vs->GetBufferSize(),
                              &g_input_layout);

  const Vertex vertices[] = {
      {{0.0f, 0.5f, 0.0f}, {1, 0, 0, 1}},
      {{-0.5f, -0.5f, 0.0f}, {0, 1, 0, 1}},
      {{0.5f, -0.5f, 0.0f}, {0, 0, 1, 1}},
  };
  D3D11_BUFFER_DESC bd = {};
  bd.ByteWidth = sizeof(vertices);
  bd.Usage = D3D11_USAGE_IMMUTABLE;
  bd.BindFlags = D3D11_BIND_VERTEX_BUFFER;
  D3D11_SUBRESOURCE_DATA init = {vertices};
  g_device->CreateBuffer(&bd, &init, &g_vertex_buffer);

  D3D11_RASTERIZER_DESC rd = {};
  rd.FillMode = D3D11_FILL_SOLID;
  rd.CullMode = D3D11_CULL_BACK;
  rd.FrontCounterClockwise = TRUE;
  rd.DepthClipEnable = TRUE;
  g_device->CreateRasterizerState(&rd, &g_rasterizer_state);
}

void RenderFrame() {
  ID3D11RenderTargetView* targets[] = {g_rtv.Get()};
  g_context->OMSetRenderTargets(1, targets, nullptr);
  const D3D11_VIEWPORT viewport = {0, 0, static_cast<float>(g_width), static_cast<float>(g_height), 0, 1};
  g_context->RSSetViewports(1, &viewport);
  const float clear_color[4] = {0.1f, 0.15f, 0.3f, 1.0f};
  g_context->ClearRenderTargetView(g_rtv.Get(), clear_color);

  g_context->IASetInputLayout(g_input_layout.Get());
  const UINT stride = sizeof(Vertex), offset = 0;
  g_context->IASetVertexBuffers(0, 1, g_vertex_buffer.GetAddressOf(), &stride, &offset);
  g_context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  g_context->VSSetShader(g_vertex_shader.Get(), nullptr, 0);
  g_context->PSSetShader(g_pixel_shader.Get(), nullptr, 0);
  g_context->RSSetState(g_rasterizer_state.Get());
  g_context->Draw(3, 0);

  g_swap_chain->Present(1, 0);
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wparam, LPARAM lparam) {
  if (message == WM_DESTROY) {
    PostQuitMessage(0);
    return 0;
  }
  return DefWindowProcW(hwnd, message, wparam, lparam);
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int show) {
  WNDCLASSEXW wc = {sizeof(wc)};
  wc.lpfnWndProc = WindowProc;
  wc.hInstance = instance;
  wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
  wc.lpszClassName = L"TriangleWindow";
  RegisterClassExW(&wc);
  RECT rect = {0, 0, static_cast<LONG>(g_width), static_cast<LONG>(g_height)};
  AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);
  HWND hwnd = CreateWindowExW(0, wc.lpszClassName, L"Triangle", WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT,
                              rect.right - rect.left, rect.bottom - rect.top, nullptr, nullptr, instance, nullptr);
  ShowWindow(hwnd, show);
  InitD3D(hwnd);

  MSG msg = {};
  while (msg.message != WM_QUIT) {
    if (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {
      TranslateMessage(&msg);
      DispatchMessageW(&msg);
    } else {
      RenderFrame();
    }
  }
  return 0;
}
```

リンクするライブラリは `d3d11.lib`、`d3dcompiler.lib`、`dxgi.lib` です（`#pragma comment(lib, …)` かプロジェクトの設定）。`triangle.hlsl` は実行ファイルの作業ディレクトリに置きます。ウィンドウの大きさ変更（`WM_SIZE`）は省いています（[Window Resize and Device Removal](resize.md)）。

## 何も見えないときのチェックリスト

| 順 | 確認 | 原因の例 |
| --- | --- | --- |
| 1 | クリアの色は出ているか | 出ない → スワップ チェーン・RTV・`Present` の問題 |
| 2 | ビューポートは設定したか | 設定忘れ（大きさ 0） |
| 3 | 三角形の頂点の並びは反時計回りか | 時計回りで、裏面として捨てられている |
| 4 | シェーダーはコンパイルできたか | エラー文を見ていない |
| 5 | 入力レイアウトと頂点の構造体は合うか | 頂点が化けて、画面外に |
| 6 | `OMSetRenderTargets` を毎フレーム、呼んでいるか | `Present` で外れている |
| 7 | デバッグ レイヤーのメッセージは無いか | 警告に原因が出ている（[Debug Layer](debug-layer.md)） |
| 8 | グラフィックス デバッガーで、1 フレーム、撮る | 各段の入出力を目で見る |

## よくあるミス

??? failure "クリアの色は出るが、三角形が見えない"
    反時計回りの三角形を時計回りが表の既定で描いて裏面として、捨てられている。`FrontCounterClockwise = TRUE`。または、`Draw` の前にビューポートやシェーダーをつなぎ忘れている。

??? failure "最初のフレームだけ描けて以降、真っ黒"
    `Present` の後でレンダー ターゲットの束縛が外れる。毎フレーム、`OMSetRenderTargets` を呼ぶ。

??? failure "三角形の色が想定と違う（暗い明るい）"
    RTV が `_SRGB` で色をリニアとして書いている。見た目の色を出したいならリニアに直した値を渡すか頂点の色の変換を考える。

??? failure "ビルドは通るが、起動するとすぐ終了する"
    `triangle.hlsl` が作業ディレクトリに無く、コンパイルが失敗して `nullptr` のブロブを使っている。パスとエラー出力を確認する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 描くには IA・VS・RS・PS・OM の全部をつなぐ
    - [x] 毎フレーム: `OMSetRenderTargets` → ビューポート → `Clear` → 束縛 → `Draw` → `Present`
    - [x] 反時計回りが表なら `FrontCounterClockwise = TRUE`
    - [x] 見えないときはクリア → ビューポート → 向き → シェーダーの順に疑う
    - [x] デバッグ レイヤーとグラフィックス デバッガーを味方にする

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Input Layout](input-layout.md)
- [Constant Buffer](constant-buffer.md)
- [Rasterizer State](rasterizer-state.md)
- [Debug Layer](debug-layer.md)
- [描画の流れ（入門）](../../3d/render-flow/index.md)
