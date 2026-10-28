---
title: 第 38 章 入力とエディタ カメラ
tags:
  - C#連携
---

# 第 38 章 入力とエディタ カメラ

ここまでのビューポートは、色が変わるだけでした。この章では、地面のグリッドと座標軸を描いて、マウスでカメラを動かせるようにします。3D エディタらしい画面にぐっと近づきます。

!!! info "このページを読む前に"
    - [第 37 章 描画ループとスレッド](37-render-loop.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


作業は 3 つあります。エンジンに線を描く仕組み（デバッグ描画）を足すこと、エディタ用のカメラを足すこと、そして WPF の子ウィンドウで受けたマウスとキーをエンジンに送ることです。

## 入力の意味づけは、エンジンが持つ

マウスを動かしたとき、カメラを動かす計算は、C# とエンジンのどちらがやるべきでしょうか。C# で計算して行列をエンジンに渡す案もありますが、それだと Player（C++ だけ）にも同じカメラが必要になり、二重に書くことになります。

そこで、エンジンが計算する方式にします。C# は生の入力（マウスの動き、ボタン、ホイール）をそのまま送るだけで、カメラの計算はエンジンの中で行います。こうすれば、エディタ以外でも同じ入力処理が使えます。C# の仕事は、WPF（Win32）の入力をエンジンが分かる形に変換して送ることだけです。

### 座標系の約束

3D に入る前にこの教材の約束を確認しておきます。

| 項目 | 約束 |
| --- | --- |
| 座標系 | 左手系、Y が上 |
| 前方向 | +Z |
| 行列の掛け方 | 行ベクトル（`v * M`）。掛け順は左から右 |
| 三角形の表 | 時計回り（CW）が表 |
| 角度 | ラジアン |
| 数学ライブラリ | SimpleMath（DirectX Tool Kit） |

## SimpleMath を使えるようにする

`Engine` の数学ライブラリには、DirectX Tool Kit の SimpleMath を使います。vcpkg で入れる方法が手軽です（[導入手順](../libs/index.md)、[Visual Studio の外部ライブラリ](../vs/index.md) も参照してください）。

1. `vcpkg install directxtk12:x64-windows`（SimpleMath は DirectXTK12 に含まれています）。
2. `vcpkg integrate install` で、Visual Studio に連携します。
3. `Engine` のコードから `#include <SimpleMath.h>` と書きます。

vcpkg を使いたくなければ、SimpleMath は `SimpleMath.h`、`SimpleMath.inl`、`SimpleMath.cpp` の 3 ファイルだけで動くので、DirectX Tool Kit のリポジトリからこれらを `Engine\third_party\simplemath\` に置く方法でも使えます。

```cpp
#include <SimpleMath.h>
using DirectX::SimpleMath::Vector3;
using DirectX::SimpleMath::Matrix;
```

## 線を描くシェーダー

線を描く最小のシェーダーです。頂点は位置と色だけ、変換は 1 つの行列（ビュー × 射影）だけです。

```cpp title="Engine/src/Shaders.h"
#pragma once

namespace mini {

// 実行時にコンパイルする HLSL。行ベクトル（mul(v, M)）で、行列は row_major で受け取る。
inline constexpr const char* kLineShader = R"(
cbuffer Constants : register(b0) {
  row_major float4x4 g_view_proj;
};

struct VSInput {
  float3 position : POSITION;
  float4 color    : COLOR;
};

struct VSOutput {
  float4 position : SV_POSITION;
  float4 color    : COLOR;
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  output.position = mul(float4(input.position, 1.0), g_view_proj);
  output.color = input.color;
  return output;
}

float4 PSMain(VSOutput input) : SV_TARGET {
  return input.color;
}
)";

}  // namespace mini
```

`R"( ... )"` は C++ の生文字列リテラルで、エスケープなしで複数行の文字列を書けます。HLSL をソースに埋め込むのに便利です。

HLSL は、既定では行列を列優先（`column_major`）で読みます。ところが DirectXMath（SimpleMath）の行列は行優先なので、`row_major` と明示して、そのまま渡せるようにしています。`mul(float4(position, 1.0), g_view_proj)` は「行ベクトル × 行列」で、この教材の約束（`v * M`）と一致します。

## LineRenderer：線を描くクラス

まずヘッダーです。

```cpp title="Engine/src/LineRenderer.h"
#pragma once

#include <d3d12.h>
#include <wrl/client.h>

#include <SimpleMath.h>

#include <array>
#include <vector>

namespace mini {

struct LineVertex {
  DirectX::SimpleMath::Vector3 position;
  DirectX::SimpleMath::Vector4 color;
};

// 線の頂点列を GPU に送って描くクラス。
class LineRenderer {
 public:
  static constexpr UINT kFrameCount = 3;
  static constexpr UINT kMaxVertices = 65536;

  LineRenderer(ID3D12Device* device, DXGI_FORMAT render_target_format);

  // list にコマンドを積む。slot は、フレームのスロット（0〜2）
  void Draw(ID3D12GraphicsCommandList* list, UINT slot, const DirectX::SimpleMath::Matrix& view_proj,
            const std::vector<LineVertex>& vertices);

 private:
  template <typename T>
  using ComPtr = Microsoft::WRL::ComPtr<T>;

  ComPtr<ID3D12RootSignature> root_signature_;
  ComPtr<ID3D12PipelineState> pipeline_state_;
  std::array<ComPtr<ID3D12Resource>, kFrameCount> vertex_buffers_;    // アップロード ヒープ
  std::array<LineVertex*, kFrameCount> mapped_ = {};                  // 常時マップしたアドレス
};

}  // namespace mini
```

コンストラクターは、ルート シグネチャ、シェーダー、パイプライン、頂点バッファーの順に作ります。

```cpp title="Engine/src/LineRenderer.cpp"
#include "LineRenderer.h"

#include <d3dcompiler.h>
#include <d3dx12.h>

#include <cstring>

#include "Dx12Util.h"
#include "Shaders.h"

#pragma comment(lib, "d3dcompiler.lib")

namespace mini {

LineRenderer::LineRenderer(ID3D12Device* device, DXGI_FORMAT render_target_format) {
  // ① ルート シグネチャ：16 個の 32 ビット値（4x4 行列）をルート定数で受け取る
  CD3DX12_ROOT_PARAMETER parameter;
  parameter.InitAsConstants(16, 0, 0, D3D12_SHADER_VISIBILITY_VERTEX);
  CD3DX12_ROOT_SIGNATURE_DESC root_desc;
  root_desc.Init(1, &parameter, 0, nullptr, D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT);

  ComPtr<ID3DBlob> serialized, error;
  ThrowIfFailed(D3D12SerializeRootSignature(&root_desc, D3D_ROOT_SIGNATURE_VERSION_1, &serialized, &error),
                "ルート シグネチャのシリアライズ");
  ThrowIfFailed(device->CreateRootSignature(0, serialized->GetBufferPointer(), serialized->GetBufferSize(),
                                            IID_PPV_ARGS(&root_signature_)),
                "ルート シグネチャの作成");

  // ② シェーダーのコンパイル
  ComPtr<ID3DBlob> vs, ps, compile_error;
  const std::size_t source_size = std::strlen(kLineShader);
  if (FAILED(D3DCompile(kLineShader, source_size, "LineShader", nullptr, nullptr, "VSMain", "vs_5_0", 0, 0, &vs,
                        &compile_error)) ||
      FAILED(D3DCompile(kLineShader, source_size, "LineShader", nullptr, nullptr, "PSMain", "ps_5_0", 0, 0, &ps,
                        &compile_error))) {
    throw std::runtime_error(compile_error ? static_cast<const char*>(compile_error->GetBufferPointer())
                                           : "シェーダーのコンパイルに失敗");
  }

  // ③ 頂点のレイアウトと、パイプライン ステート
  const D3D12_INPUT_ELEMENT_DESC layout[] = {
      {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
      {"COLOR", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
  };

  D3D12_GRAPHICS_PIPELINE_STATE_DESC pso = {};
  pso.pRootSignature = root_signature_.Get();
  pso.VS = {vs->GetBufferPointer(), vs->GetBufferSize()};
  pso.PS = {ps->GetBufferPointer(), ps->GetBufferSize()};
  pso.InputLayout = {layout, _countof(layout)};
  pso.RasterizerState = CD3DX12_RASTERIZER_DESC(D3D12_DEFAULT);
  pso.RasterizerState.FrontCounterClockwise = FALSE;              // CW が表
  pso.RasterizerState.CullMode = D3D12_CULL_MODE_NONE;            // 線なのでカリングしない
  pso.BlendState = CD3DX12_BLEND_DESC(D3D12_DEFAULT);
  pso.DepthStencilState.DepthEnable = FALSE;
  pso.SampleMask = UINT_MAX;
  pso.PrimitiveTopologyType = D3D12_PRIMITIVE_TOPOLOGY_TYPE_LINE;
  pso.NumRenderTargets = 1;
  pso.RTVFormats[0] = render_target_format;
  pso.SampleDesc.Count = 1;
  ThrowIfFailed(device->CreateGraphicsPipelineState(&pso, IID_PPV_ARGS(&pipeline_state_)), "パイプライン ステートの作成");
```

ルート シグネチャは、`InitAsConstants(16, 0, 0, ...)` で、16 個の 32 ビット値（ちょうど 4×4 行列 1 つ分）をシェーダー レジスタ `b0` に直接渡す形にしています。この方法なら、定数バッファーを作らずに済みます。`D3DCompile` は、HLSL を実行時にコンパイルする関数で、`"vs_5_0"` はシェーダー モデル 5.0 の頂点シェーダーを意味します。失敗したときのメッセージは `compile_error` に入るので、例外にして外に出しています。

頂点のレイアウトは、`POSITION` が 12 バイト（`float3`）、`COLOR` がその後ろの 12 バイト目から 16 バイト（`float4`）です。パイプラインでは、`FrontCounterClockwise = FALSE` で「CW が表」の約束を明示し、`RTVFormats[0]` は、第 3 章のレンダー ターゲットと同じフォーマットにします。DX12 のパイプラインの各項目は、[PSO](../directx/dx12/pso.md) と [Root Signature](../directx/dx12/root-signature.md) のページで説明しています。

```cpp
  // ④ フレームごとの頂点バッファー（CPU から書ける領域を常時マップしておく）
  const UINT64 size = sizeof(LineVertex) * kMaxVertices;
  const CD3DX12_HEAP_PROPERTIES upload_heap(D3D12_HEAP_TYPE_UPLOAD);
  const CD3DX12_RESOURCE_DESC buffer_desc = CD3DX12_RESOURCE_DESC::Buffer(size);
  for (UINT i = 0; i < kFrameCount; ++i) {
    ThrowIfFailed(device->CreateCommittedResource(&upload_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                                  D3D12_RESOURCE_STATE_GENERIC_READ, nullptr,
                                                  IID_PPV_ARGS(&vertex_buffers_[i])),
                  "頂点バッファーの作成");
    const CD3DX12_RANGE no_read(0, 0);               // CPU は書くだけで、読まない
    ThrowIfFailed(vertex_buffers_[i]->Map(0, &no_read, reinterpret_cast<void**>(&mapped_[i])), "Map");
  }
}
```

頂点バッファーは `D3D12_HEAP_TYPE_UPLOAD`（CPU が書いて GPU が読む領域）に作り、`Map` で CPU から書けるアドレスを得ます。アップロード ヒープは、マップしたまま使い続けてよい決まりです。フレームごとに 3 つ作るのは、GPU が前のフレームを読んでいる最中に CPU が同じバッファーを書き換えないようにするためです（第 3 章のスロットと同じ考え方です）。

描く関数はこうです。

```cpp
void LineRenderer::Draw(ID3D12GraphicsCommandList* list, UINT slot, const DirectX::SimpleMath::Matrix& view_proj,
                        const std::vector<LineVertex>& vertices) {
  if (vertices.empty()) return;
  const UINT count = static_cast<UINT>(std::min<std::size_t>(vertices.size(), kMaxVertices));
  std::memcpy(mapped_[slot], vertices.data(), sizeof(LineVertex) * count);

  D3D12_VERTEX_BUFFER_VIEW view = {};
  view.BufferLocation = vertex_buffers_[slot]->GetGPUVirtualAddress();
  view.SizeInBytes = sizeof(LineVertex) * count;
  view.StrideInBytes = sizeof(LineVertex);

  list->SetGraphicsRootSignature(root_signature_.Get());
  list->SetPipelineState(pipeline_state_.Get());
  list->SetGraphicsRoot32BitConstants(0, 16, &view_proj, 0);
  list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_LINELIST);
  list->IASetVertexBuffers(0, 1, &view);
  list->DrawInstanced(count, 1, 0, 0);
}

}  // namespace mini
```

頂点をマップ済みのバッファーに `memcpy` でコピーします。GPU が実際に読むのは、このフレームのコマンドが実行されるときです。`SetGraphicsRoot32BitConstants` で、`Matrix`（メモリ上で 16 個の `float` が行優先に並んだもの）をそのままルート定数に書きます。`LINELIST` は、頂点 2 つで 1 本の線を表すトポロジーです。

## エディタ カメラ

エディタの定番のオービット カメラ（注視点の周りを回るカメラ）を作ります。

```cpp title="Engine/src/EditorCamera.h"
#pragma once

#include <SimpleMath.h>

namespace mini {

// 注視点の周りを回るカメラ。左手系、Y が上、前は +Z。
class EditorCamera {
 public:
  using Vector3 = DirectX::SimpleMath::Vector3;
  using Matrix = DirectX::SimpleMath::Matrix;

  void Orbit(float delta_x_pixels, float delta_y_pixels);   // 回転
  void Pan(float delta_x_pixels, float delta_y_pixels);     // 平行移動
  void Zoom(float notches);                                 // 拡大縮小（ホイールの目盛り数）
  void Focus(const Vector3& target, float radius);          // 対象へ寄る

  Vector3 Position() const;
  Matrix View() const;
  Matrix Projection(float aspect) const;

 private:
  Vector3 target_ = Vector3::Zero;
  float yaw_ = 0.6f;        // Y 軸まわりの角度（ラジアン）
  float pitch_ = 0.5f;      // 上下の角度（ラジアン）。正のとき、上から見下ろす
  float distance_ = 8.0f;   // 注視点までの距離
  float fov_ = 1.0471976f;  // 縦の視野角 60 度（ラジアン）
};

}  // namespace mini
```

```cpp title="Engine/src/EditorCamera.cpp"
#include "EditorCamera.h"

#include <algorithm>
#include <cmath>

namespace mini {

namespace {
constexpr float kOrbitSpeed = 0.005f;    // 1 ピクセルあたりのラジアン
constexpr float kPitchLimit = 1.55f;     // 約 89 度。真上・真下でひっくり返らないように
constexpr float kNear = 0.05f;
constexpr float kFar = 1000.0f;
}  // namespace

EditorCamera::Vector3 EditorCamera::Position() const {
  // 球面座標。yaw = 0, pitch = 0 のとき、注視点の -Z 側に居て、+Z 方向を見る。
  const float cp = std::cos(pitch_);
  return target_ + Vector3(cp * std::sin(yaw_), std::sin(pitch_), -cp * std::cos(yaw_)) * distance_;
}

EditorCamera::Matrix EditorCamera::View() const {
  return DirectX::XMMatrixLookAtLH(Position(), target_, Vector3::Up);
}

EditorCamera::Matrix EditorCamera::Projection(float aspect) const {
  return DirectX::XMMatrixPerspectiveFovLH(fov_, aspect, kNear, kFar);
}

void EditorCamera::Orbit(float dx, float dy) {
  yaw_ -= dx * kOrbitSpeed;
  pitch_ = std::clamp(pitch_ + dy * kOrbitSpeed, -kPitchLimit, kPitchLimit);
}

void EditorCamera::Pan(float dx, float dy) {
  // カメラの右方向と上方向（ビュー行列の逆）に沿って、注視点を動かす。
  const Matrix view = View();
  const Vector3 right(view._11, view._21, view._31);
  const Vector3 up(view._12, view._22, view._32);
  const float scale = distance_ * std::tan(fov_ * 0.5f) * 2.0f / 720.0f;   // 1 ピクセルが注視点付近で何メートルか（高さ 720 を仮定）
  target_ += (-right * dx + up * dy) * scale;
}

void EditorCamera::Zoom(float notches) {
  distance_ = std::clamp(distance_ * std::pow(0.9f, notches), 0.2f, 500.0f);
}

void EditorCamera::Focus(const Vector3& target, float radius) {
  target_ = target;
  distance_ = std::max(radius * 2.5f, 1.0f);
}

}  // namespace mini
```

カメラの位置は、球面座標（`yaw` が横、`pitch` が縦、`distance` が距離）から求めます。注視点を中心にした球の上をカメラが動く形です。`XMMatrixLookAtLH` と `XMMatrixPerspectiveFovLH` は、DirectXMath の左手系の関数で、前が +Z になります（SimpleMath の `Matrix::CreateLookAt` などは右手系なので使いません）。視野角は縦の角度です。

`Pan` の中の `view._11, _21, _31` は、ビュー行列の第 1 列で、カメラの右方向（ワールド空間）を表しています。行ベクトルの規約では、行列の列が基底の向きになるためです。移動量の `scale` は、注視点付近で 1 ピクセルが何メートルに当たるかです。遠いほど、同じマウスの動きで大きく動きます（今はビューポートの高さを 720 と仮定した近似です）。`Zoom` は、ホイール 1 目盛りで距離を 0.9 倍にします。

## 入力イベントを C の API に足す

まず C の構造体と関数です。`EngineApi.h` に追加します。

```c
/* 入力イベント（28 バイト） */
typedef struct MeInputEvent {
  int32_t  type;       /* MeInputType */
  int32_t  button;     /* 0: 左, 1: 右, 2: 中央 */
  float    x;          /* ビューポート内のマウス座標（ピクセル） */
  float    y;
  float    delta;      /* ホイールの目盛り数（1 目盛り = 1.0） */
  int32_t  key;        /* 仮想キーコード（VK_*） */
  uint32_t modifiers;  /* ビット: 1 = Shift, 2 = Ctrl, 4 = Alt */
} MeInputEvent;

enum {
  ME_INPUT_MOUSE_MOVE = 0,
  ME_INPUT_BUTTON_DOWN = 1,
  ME_INPUT_BUTTON_UP = 2,
  ME_INPUT_WHEEL = 3,
  ME_INPUT_KEY_DOWN = 4,
  ME_INPUT_KEY_UP = 5,
  ME_INPUT_FOCUS_LOST = 6
};

ME_API MeResult me_engine_send_input(MeEngine* engine, const MeInputEvent* event);
```

実装は、これまでと同じ形です（`Guard` と引数の検査）。

```cpp
MeResult me_engine_send_input(MeEngine* engine, const MeInputEvent* event) {
  return Guard([&]() -> MeResult {
    if (!engine || !event) {
      SetLastError("引数が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    mini::InputEvent e;
    e.type = static_cast<mini::InputType>(event->type);
    e.button = event->button;
    e.x = event->x;
    e.y = event->y;
    e.delta = event->delta;
    e.key = event->key;
    e.modifiers = event->modifiers;
    engine->engine->OnInput(e);
    return ME_OK;
  });
}
```

エンジン側の公開ヘッダー `Engine.h` には、入力の型と関数を足します。

```cpp
enum class InputType : std::int32_t { MouseMove, ButtonDown, ButtonUp, Wheel, KeyDown, KeyUp, FocusLost };

struct InputEvent {
  InputType type = InputType::MouseMove;
  std::int32_t button = 0;
  float x = 0, y = 0, delta = 0;
  std::int32_t key = 0;
  std::uint32_t modifiers = 0;
};

// class Engine の中
void OnInput(const InputEvent& event);
```

`Engine.cpp` の `Impl` にカメラと入力の状態を持たせて、`OnInput` で処理します。

```cpp
struct Engine::Impl {
  // ...
  EditorCamera camera;
  bool button_down[3] = {};
  float last_x = 0, last_y = 0;
};

void Engine::OnInput(const InputEvent& e) {
  auto& s = *impl_;
  switch (e.type) {
    case InputType::ButtonDown:
      if (e.button >= 0 && e.button < 3) s.button_down[e.button] = true;
      s.last_x = e.x;
      s.last_y = e.y;
      break;
    case InputType::ButtonUp:
      if (e.button >= 0 && e.button < 3) s.button_down[e.button] = false;
      break;
    case InputType::MouseMove: {
      const float dx = e.x - s.last_x;
      const float dy = e.y - s.last_y;
      s.last_x = e.x;
      s.last_y = e.y;
      if (s.button_down[1]) s.camera.Orbit(dx, dy);        // 右ドラッグ：回転
      else if (s.button_down[2]) s.camera.Pan(dx, dy);     // 中ドラッグ：平行移動
      break;
    }
    case InputType::Wheel:
      s.camera.Zoom(e.delta);
      break;
    case InputType::FocusLost:
      for (bool& b : s.button_down) b = false;             // 離したのに通知が来ない場合の保険
      break;
    default:
      break;
  }
}
```

## Tick で描く

`Renderer::Render` が、線の頂点とカメラの行列を受け取るように変えます。

```cpp
// Renderer.h に追加
void Render(const float clear_color[4], const DirectX::SimpleMath::Matrix& view_proj,
            const std::vector<LineVertex>& lines);
// std::unique_ptr<LineRenderer> line_renderer_;   ← コンストラクターの最後で作る
```

```cpp
// Renderer.cpp の Render の中、ClearRenderTargetView の直後
D3D12_VIEWPORT viewport = {0.0f, 0.0f, static_cast<float>(width_), static_cast<float>(height_), 0.0f, 1.0f};
D3D12_RECT scissor = {0, 0, static_cast<LONG>(width_), static_cast<LONG>(height_)};
list_->RSSetViewports(1, &viewport);
list_->RSSetScissorRects(1, &scissor);
line_renderer_->Draw(list_.Get(), frame_slot_, view_proj, lines);
```

`Engine::Tick` では、グリッドと軸を組み立てて、カメラの行列と一緒に渡します。

```cpp
void Engine::Tick(float delta_seconds) {
  auto& s = *impl_;
  ++s.frame_count;

  // 線の頂点：グリッドと座標軸
  std::vector<LineVertex> lines;
  const Vector4 grid_color(0.35f, 0.35f, 0.35f, 1.0f);
  for (int i = -10; i <= 10; ++i) {
    if (i == 0) continue;
    lines.push_back({Vector3(float(i), 0, -10), grid_color});     // Z 方向に伸びる線
    lines.push_back({Vector3(float(i), 0, 10), grid_color});
    lines.push_back({Vector3(-10, 0, float(i)), grid_color});     // X 方向に伸びる線
    lines.push_back({Vector3(10, 0, float(i)), grid_color});
  }
  lines.push_back({Vector3(0, 0, 0), Vector4(1, 0, 0, 1)});        // X 軸：赤
  lines.push_back({Vector3(3, 0, 0), Vector4(1, 0, 0, 1)});
  lines.push_back({Vector3(0, 0, 0), Vector4(0, 1, 0, 1)});        // Y 軸：緑
  lines.push_back({Vector3(0, 3, 0), Vector4(0, 1, 0, 1)});
  lines.push_back({Vector3(0, 0, 0), Vector4(0, 0, 1, 1)});        // Z 軸：青
  lines.push_back({Vector3(0, 0, 3), Vector4(0, 0, 1, 1)});

  const float aspect = float(s.desc.width) / float(std::max<std::uint32_t>(1, s.desc.height));
  const Matrix view_proj = s.camera.View() * s.camera.Projection(aspect);    // 行ベクトル：左から右へ

  const float clear[4] = {0.10f, 0.10f, 0.12f, 1.0f};
  try {
    s.renderer->Render(clear, view_proj, lines);
  } catch (const std::exception& e) {
    LogError("Render に失敗: {}", e.what());
  }
}
```

行ベクトルの約束では、ビュー、射影の順に左から右へ掛けるので、頂点は `v * view * projection` で変換されます。軸の色は、X が赤、Y が緑、Z が青です（RGB と XYZ が対応していると覚えると楽です）。背景は暗い色にして、色が変わる塗りつぶしは、ここで役目を終えます。

## C# で入力を受けて送る

Win32 のメッセージを受けるために、宣言を足します。

```csharp
// Win32.cs に追加
public const int WM_MOUSEMOVE = 0x0200;
public const int WM_LBUTTONDOWN = 0x0201, WM_LBUTTONUP = 0x0202;
public const int WM_RBUTTONDOWN = 0x0204, WM_RBUTTONUP = 0x0205;
public const int WM_MBUTTONDOWN = 0x0207, WM_MBUTTONUP = 0x0208;
public const int WM_MOUSEWHEEL = 0x020A;
public const int WM_KEYDOWN = 0x0100, WM_KEYUP = 0x0101;
public const int WM_KILLFOCUS = 0x0008;

[LibraryImport("user32.dll")]
public static partial nint SetCapture(nint hwnd);

[LibraryImport("user32.dll")]
[return: MarshalAs(UnmanagedType.Bool)]
public static partial bool ReleaseCapture();

[LibraryImport("user32.dll")]
[return: MarshalAs(UnmanagedType.Bool)]
public static partial bool ScreenToClient(nint hwnd, ref POINT point);

[LibraryImport("user32.dll")]
public static partial short GetKeyState(int virtualKey);

[StructLayout(LayoutKind.Sequential)]
public struct POINT { public int X, Y; }
```

`ViewportHost` で `WndProc` をオーバーライドすると、子ウィンドウに届いたメッセージを受け取れます。

```csharp
// 入力が来たことを知らせるイベント
public event EventHandler<ViewportInputEventArgs>? InputReceived;

protected override nint WndProc(nint hwnd, int msg, nint wParam, nint lParam, ref bool handled)
{
    switch (msg)
    {
        case Win32.WM_MOUSEMOVE:
            Raise(InputType.MouseMove, 0, lParam, 0);
            break;
        case Win32.WM_LBUTTONDOWN: OnButton(hwnd, true, 0, lParam); break;
        case Win32.WM_LBUTTONUP:   OnButton(hwnd, false, 0, lParam); break;
        case Win32.WM_RBUTTONDOWN: OnButton(hwnd, true, 1, lParam); break;
        case Win32.WM_RBUTTONUP:   OnButton(hwnd, false, 1, lParam); break;
        case Win32.WM_MBUTTONDOWN: OnButton(hwnd, true, 2, lParam); break;
        case Win32.WM_MBUTTONUP:   OnButton(hwnd, false, 2, lParam); break;
        case Win32.WM_MOUSEWHEEL:
        {
            // wParam の上位 16 ビットが回転量（符号つき）。120 で 1 目盛り。
            short wheel = (short)((long)wParam >> 16);
            Raise(InputType.Wheel, 0, 0, wheel / 120f);
            handled = true;
            break;
        }
        case Win32.WM_KILLFOCUS:
            Raise(InputType.FocusLost, 0, 0, 0);
            break;
    }
    return base.WndProc(hwnd, msg, wParam, lParam, ref handled);
}

private void OnButton(nint hwnd, bool down, int button, nint lParam)
{
    if (down)
    {
        Win32.SetFocus(hwnd);           // クリックされたら、キーボードの入力先にする
        Win32.SetCapture(hwnd);         // ボタンを押している間は、枠の外へ出ても、マウスを受け取る
    }
    else
    {
        Win32.ReleaseCapture();
    }
    Raise(down ? InputType.ButtonDown : InputType.ButtonUp, button, lParam, 0);
}

private void Raise(InputType type, int button, nint lParam, float delta)
{
    // lParam の下位 16 ビットが X、上位 16 ビットが Y（符号つき）
    short x = (short)((long)lParam & 0xFFFF);
    short y = (short)(((long)lParam >> 16) & 0xFFFF);
    InputReceived?.Invoke(this, new ViewportInputEventArgs(type, button, x, y, delta));
}
```

細かい点を拾っておきます。

- マウス座標は、`lParam` の下位 16 ビットが X、上位 16 ビットが Y です。`(short)` にキャストして符号つきにしているのは、ウィンドウの左や上の外までドラッグすると、座標が負になるからです。
- `SetCapture` は、ボタンを押している間、マウスがウィンドウの外に出てもメッセージを受け取り続ける指定です。ドラッグ操作には必須です。
- `SetFocus` は、キーボードの入力先にするために呼びます。
- `WM_MOUSEWHEEL` の `wParam` は、上位 16 ビットが回転量で、120 が 1 目盛りです。
- `WM_KILLFOCUS` はフォーカスを失ったときのメッセージです。押しっぱなしのボタンの状態をリセットするために、エンジンへ `FocusLost` を送ります。

イベントの引数と種類の定義をホストの近くに置きます。

```csharp
public enum InputType { MouseMove = 0, ButtonDown = 1, ButtonUp = 2, Wheel = 3, KeyDown = 4, KeyUp = 5, FocusLost = 6 }

public sealed class ViewportInputEventArgs : EventArgs
{
    public InputType Type { get; }
    public int Button { get; }
    public float X { get; }
    public float Y { get; }
    public float Delta { get; }

    public ViewportInputEventArgs(InputType type, int button, float x, float y, float delta)
    {
        Type = type; Button = button; X = x; Y = y; Delta = delta;
    }
}
```

`NativeMethods` に、構造体と関数を足します。

```csharp
[StructLayout(LayoutKind.Sequential)]
internal struct MeInputEvent
{
    public int Type;
    public int Button;
    public float X;
    public float Y;
    public float Delta;
    public int Key;
    public uint Modifiers;
}

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_engine_send_input(EngineHandle engine, in MeInputEvent inputEvent);
```

`IEngineService` に `SendInput(...)` を足して、`PInvokeEngineService` で実装します。

```csharp
// IEngineService
void SendInput(int type, int button, float x, float y, float delta, int key, uint modifiers);

// PInvokeEngineService
public void SendInput(int type, int button, float x, float y, float delta, int key, uint modifiers)
{
    var e = new MeInputEvent { Type = type, Button = button, X = x, Y = y, Delta = delta, Key = key, Modifiers = modifiers };
    NativeMethods.ThrowIfFailed(NativeMethods.me_engine_send_input(Handle, in e));
}
```

最後に、ビューとビューモデルをつなぎます。`ViewportView.xaml.cs` に 1 行足します。

```csharp
Host.InputReceived += (_, e) => ViewModel?.OnInput(e.Type, e.Button, e.X, e.Y, e.Delta);
```

`ViewportViewModel` には、命令の転送を足します。

```csharp
public void OnInput(Controls.InputType type, int button, float x, float y, float delta)
{
    // 描画スレッドで、エンジンへ送る（エンジンを触るのは描画スレッドだけ）
    _loop.Post(engine => engine.SendInput((int)type, button, x, y, delta, 0, 0));
}
```

マウスの動きは、1 秒に数百回届くことがありますが、`Post` は命令を積むだけなので軽く、描画スレッドが 1 フレームに複数の移動をまとめて処理するので、問題ありません。

## 動かして確かめる

- 起動すると、暗い背景に灰色のグリッドと、赤・緑・青の軸が見える。
- 右ボタンを押してドラッグすると、カメラが原点の周りを回る。上下にドラッグしても、真上・真下を越えない。
- 中ボタンのドラッグで平行移動、ホイールで近づく・遠ざかる。
- ボタンを押したまま枠の外に出ても、ドラッグが続く。ほかのパネルをクリックすると、押しっぱなしの状態が解除される。

??? failure "線が何も出ない"
    頂点数が 0 か、シェーダーのコンパイルに失敗しています（ログを確認します）。または `view_proj` が `Identity` のままで、すべての線がクリップされています。`XMMatrixLookAtLH` と `XMMatrixPerspectiveFovLH` の引数を見直します。

??? failure "絵が上下や左右に反転している"
    行列の転置の間違いです。`row_major` を付けていないと、列優先として読まれて転置になります。あるいは、右手系用の関数（`Matrix::CreateLookAt` など）を使っています。

??? failure "マウス ホイールが反応しない"
    `HwndHost` はフォーカスがないと、ホイールを受け取らないことがあります。クリックしたときに `SetFocus` を呼んでいるかを確認します。

??? failure "右ドラッグで、コンテキスト メニューが出てしまう"
    `WM_CONTEXTMENU` が親に伝わっています。WPF 側の `ContextMenu` をビューポートの親に設定しないようにします。

??? failure "カメラが勝手に動き続ける"
    `ButtonUp` が届いていません（ウィンドウの外でボタンを離した、など）。`SetCapture` を呼んでいるか、`FocusLost` で状態をリセットしているかを確かめます。

??? failure "`Pan` の速さが合わない"
    `Pan` の `scale` は、ビューポートの高さを 720 と仮定した近似です。正確には現在の高さを渡して計算します（第 42 章で改善します）。

## この章のまとめ

- 入力の意味づけはエンジンが持ち、C# は生の入力を送るだけにする。
- 線の描画は、ルート定数、動的な頂点バッファー、単純な HLSL でできる。
- カメラは、行ベクトルの規約で `view * projection`。
- マウスのドラッグには `SetCapture` が必須。

次の章から第 5 部です。シーンに物を置けるようにして、C# から作成、削除、変更できる API を作ります。

[第 39 章 シーンのデータと API](39-scene-api.md) へ進みます。
