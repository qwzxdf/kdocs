---
title: Drawing a Triangle
tags:
  - DirectX
---

# Drawing a Triangle

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

ここまでの、ページで、作った部品（ウィンドウ、デバイス、スワップ チェーン、RTV、シェーダー、頂点バッファ、入力レイアウト）を、<strong>パイプラインに、つないで、三角形を、描きます</strong>。D3D11 の「Hello World」です。描画が、1 つ、通れば、あとは、この、骨格の、上に、積み重ねていくだけです。

!!! tip "ポイント"
    - 描くには、<strong>入力アセンブラー（IA）→ 頂点シェーダー（VS）→ ラスタライザー（RS）→ ピクセル シェーダー（PS）→ 出力マージャー（OM）</strong>に、必要な物を、すべて、つなぐ。
    - 1 つでも、つなぎ忘れると、何も、描かれない（エラーも、出ないことが、多い）。
    - 毎フレーム、<strong>束ねる → クリア → 描く → Present</strong>。
    - 三角形が、見えないときは、「裏面」「ビューポート」「束縛の忘れ」を、疑う。
    - ステートを、作らないと、既定（深度テスト有り、裏面カリング有り、ブレンド無し）で、描かれる。

## パイプラインの、つなぎ方

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

D3D11 は、状態を、持つ API です。一度設定した束縛は、次の設定まで、残るので、毎フレーム、全部を、設定し直す、必要は、ありませんが、<strong>`Present` の後で、外れるもの（レンダー ターゲット）</strong>は、設定し直します。

## 描画を、1 つずつ

### 入力アセンブラー（IA）

```cpp
context->IASetInputLayout(input_layout.Get());

const UINT stride = sizeof(Vertex);
const UINT offset = 0;
context->IASetVertexBuffers(0, 1, vertex_buffer.GetAddressOf(), &stride, &offset);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
```

「頂点を、どう読み、どうつなぐか」を、決めます。ここまでは、[Input Layout](input-layout.md) と [Vertex Buffer](vertex-buffer.md) の、内容です。

### 頂点シェーダーと、ピクセル シェーダー

```cpp
context->VSSetShader(vertex_shader.Get(), nullptr, 0);     // 第 2・3 引数: クラス インスタンス（使わない）
context->PSSetShader(pixel_shader.Get(), nullptr, 0);
```

使う、シェーダーを、つなぎます（[Shaders and Compilation](shaders.md)）。ジオメトリ、ハル、ドメイン シェーダーを、使わない間は、設定しません（前に、設定した物が、残らないよう、`nullptr` で、外す）。

### ラスタライザーと、出力

```cpp
D3D11_VIEWPORT viewport = {0.0f, 0.0f, static_cast<float>(width), static_cast<float>(height), 0.0f, 1.0f};
context->RSSetViewports(1, &viewport);
context->RSSetState(rasterizer_state.Get());               // このサイトの規約: 反時計回りが表（下）

ID3D11RenderTargetView* targets[] = {rtv.Get()};
context->OMSetRenderTargets(1, targets, nullptr);
```

ビューポートは、[Viewport](viewport.md)、描き込み先は、[Render Target View (RTV)](render-target-view.md) です。

### 描く

```cpp
context->Draw(3, 0);
```

`Draw(頂点の数, 開始位置)` で、頂点シェーダーが、3 回、呼ばれ、3 頂点が、1 つの三角形に、なります。ラスタライザーが、三角形の、内側の、ピクセルを、列挙し、ピクセル シェーダーが、各ピクセルで、呼ばれます。

## 面の向き（カリング）

D3D11 の、既定は、<strong>時計回り（CW）が表</strong>で、<strong>裏面は、捨てます</strong>。このサイトの規約は、<strong>反時計回り（CCW）が表</strong>なので、ラスタライザー ステートを、作って、合わせます。

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.FillMode = D3D11_FILL_SOLID;
desc.CullMode = D3D11_CULL_BACK;                           // 裏面を、捨てる
desc.FrontCounterClockwise = TRUE;                         // 反時計回りを、表とする
desc.DepthClipEnable = TRUE;
device->CreateRasterizerState(&desc, &rasterizer_state);
```

`FrontCounterClockwise` を、設定せずに、反時計回りの、三角形を、描くと、裏面と、みなされて、<strong>何も、見えません</strong>。三角形が、見えないときの、最初の、疑いどころです（[Rasterizer State](rasterizer-state.md)）。

## 動く、完全なプログラム

ここまでの、部品を、1 つにまとめた、完成形です。`triangle.hlsl` は、[Shaders and Compilation](shaders.md) の、シェーダーです。

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

リンクするライブラリは、`d3d11.lib`、`d3dcompiler.lib`、`dxgi.lib` です（`#pragma comment(lib, …)` か、プロジェクトの設定）。`triangle.hlsl` は、実行ファイルの、作業ディレクトリに、置きます。ウィンドウの、大きさ変更（`WM_SIZE`）は、省いています（[Window Resize and Device Removal](resize.md)）。

## 何も、見えないときの、チェックリスト

| 順 | 確認 | 原因の例 |
| --- | --- | --- |
| 1 | クリアの色は、出ているか | 出ない → スワップ チェーン・RTV・`Present` の問題 |
| 2 | ビューポートは、設定したか | 設定忘れ（大きさ 0） |
| 3 | 三角形の、頂点の並びは、反時計回りか | 時計回りで、裏面として、捨てられている |
| 4 | シェーダーは、コンパイルできたか | エラー文を、見ていない |
| 5 | 入力レイアウトと、頂点の構造体は、合うか | 頂点が、化けて、画面外に |
| 6 | `OMSetRenderTargets` を、毎フレーム、呼んでいるか | `Present` で、外れている |
| 7 | デバッグ レイヤーの、メッセージは、無いか | 警告に、原因が、出ている（[Debug Layer](debug-layer.md)） |
| 8 | グラフィックス デバッガーで、1 フレーム、撮る | 各段の、入出力を、目で見る |

## よくあるミス

??? failure "クリアの色は、出るが、三角形が、見えない"
    反時計回りの三角形を、時計回りが表の、既定で、描いて、裏面として、捨てられている。`FrontCounterClockwise = TRUE`。または、`Draw` の前に、ビューポートや、シェーダーを、つなぎ忘れている。

??? failure "最初のフレームだけ、描けて、以降、真っ黒"
    `Present` の後で、レンダー ターゲットの、束縛が、外れる。毎フレーム、`OMSetRenderTargets` を、呼ぶ。

??? failure "三角形の色が、想定と、違う（暗い、明るい）"
    RTV が `_SRGB` で、色を、リニアとして、書いている。見た目の色を、出したいなら、リニアに、直した値を、渡すか、頂点の色の、変換を、考える。

??? failure "ビルドは、通るが、起動すると、すぐ、終了する"
    `triangle.hlsl` が、作業ディレクトリに、無く、コンパイルが、失敗して、`nullptr` の、ブロブを、使っている。パスと、エラー出力を、確認する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 描くには、IA・VS・RS・PS・OM の、全部を、つなぐ
    - [x] 毎フレーム: `OMSetRenderTargets` → ビューポート → `Clear` → 束縛 → `Draw` → `Present`
    - [x] 反時計回りが表なら、`FrontCounterClockwise = TRUE`
    - [x] 見えないときは、クリア → ビューポート → 向き → シェーダーの順に疑う
    - [x] デバッグ レイヤーと、グラフィックス デバッガーを、味方にする

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Input Layout](input-layout.md)
- [Constant Buffer](constant-buffer.md)
- [Rasterizer State](rasterizer-state.md)
- [Debug Layer](debug-layer.md)
- [描画の流れ（入門）](../../3d/render-flow/index.md)
