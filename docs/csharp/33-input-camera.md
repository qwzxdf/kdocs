---
title: 第 33 章 入力とエディタ カメラ
tags:
  - C#連携
---

# 第 33 章 入力とエディタ カメラ

ここまでのビューポートは、<strong>色が変わるだけ</strong>でした。この章で、ビューポートに<strong>地面のグリッドと座標軸</strong>を描き、マウスで<strong>カメラを動かせる</strong>ようにします。3D エディタらしい画面に、ぐっと近づく章です。

この章には、3 つの作業があります。

1. エンジンに、<strong>線を描く仕組み</strong>（デバッグ描画）を足す。
2. エンジンに、<strong>エディタ用のカメラ</strong>を足す。
3. WPF の子ウィンドウで受けたマウスとキーを、<strong>エンジンに送る</strong>（C# → C++ の入力）。

## この章の考え方

### 誰が入力を処理するのか

マウスを動かしたとき、カメラを動かす計算は、<strong>どちらが行う</strong>べきでしょうか。

| 案 | 内容 | 問題 |
| --- | --- | --- |
| C# が計算 | C# でカメラの位置を計算し、行列をエンジンに渡す | Player（C++ のみ）にも同じカメラが要るので、二重に書く |
| <strong>エンジンが計算</strong> | C# は、<strong>生の入力（マウスの動き、ボタン）をそのまま送る</strong>だけ。カメラの計算は、エンジン内 | <strong>採用</strong>。エディタ以外でも、同じ入力処理が使える |

C# の役目は、<strong>WPF（Win32）の入力を、エンジンが分かる形に変換して送る</strong>ことだけです。入力の意味づけは、エンジンが持ちます。

### この教材の座標系

3D の約束を、先に確認します（このサイトの 3D の約束と同じです）。

| 項目 | 約束 |
| --- | --- |
| 座標系 | 右手系、Y が上 |
| 前方向 | −Z |
| 行列の掛け方 | 行ベクトル（`v * M`）。掛け順は左から右 |
| 三角形の表 | 反時計回り（CCW）が表 |
| 角度 | ラジアン |
| 数学ライブラリ | SimpleMath（DirectX Tool Kit） |

## この章のゴール

- ビューポートに、グリッドと XYZ 軸（X: 赤、Y: 緑、Z: 青）が描かれる。
- 右ドラッグで回転、中ドラッグで平行移動、ホイールで拡大縮小。
- C# のマウス入力が、描画スレッド経由でエンジンに届く。

## 手順 1：SimpleMath を使えるようにする

`Engine` の数学ライブラリに、DirectX Tool Kit の SimpleMath を使います。vcpkg で入れる方法を使います（[導入手順](../libs/index.md) と [Visual Studio の外部ライブラリ](../vs/index.md) も参照）。

1. `vcpkg install directxtk12:x64-windows`（SimpleMath は DirectXTK12 に含まれる）。
2. `vcpkg integrate install` で、Visual Studio に連携する。
3. `Engine` のコードから `#include <SimpleMath.h>` と書く。

!!! note "手短に済ませる場合"
    SimpleMath は `SimpleMath.h` / `SimpleMath.inl` / `SimpleMath.cpp` の 3 ファイルだけで動きます。DirectX Tool Kit のリポジトリから、これらを `Engine\third_party\simplemath\` に置く方法でも、使えます。

```cpp
#include <SimpleMath.h>
using DirectX::SimpleMath::Vector3;
using DirectX::SimpleMath::Matrix;
```

## 手順 2：線を描くシェーダー

線を描く最小のシェーダーです。頂点は「位置」と「色」だけ、変換は 1 つの行列（ビュー × 射影）だけです。

`Engine\src\Shaders.h`:

```cpp
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

| 部分 | 説明 |
| --- | --- |
| `R"( … )"` | C++ の<strong>生文字列リテラル</strong>。エスケープなしで、複数行の文字列を書ける。HLSL をソースに埋め込むのに便利 |
| `row_major float4x4` | HLSL は、既定で<strong>列優先</strong>（`column_major`）で行列を読む。DirectXMath（SimpleMath）の行列は<strong>行優先</strong>なので、`row_major` と明示して、そのまま渡せるようにする |
| `mul(float4(position, 1.0), g_view_proj)` | <strong>行ベクトル × 行列</strong>。座標系の約束（`v * M`）と一致する |
| `SV_POSITION` | 頂点シェーダーの出力で、クリップ空間の位置を表す |
| `SV_TARGET` | ピクセル シェーダーの出力先（レンダー ターゲット 0） |
| `register(b0)` | 定数バッファーのスロット 0。ルート定数として受け取る |

## 手順 3：LineRenderer（線を描くクラス）

`Engine\src\LineRenderer.h`:

```cpp
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

`Engine\src\LineRenderer.cpp`:

### ルート シグネチャとパイプライン

```cpp
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
  pso.RasterizerState.FrontCounterClockwise = TRUE;               // CCW が表
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

| 部分 | 説明 |
| --- | --- |
| `InitAsConstants(16, 0, 0, …)` | ルート定数。<strong>16 個の 32 ビット値</strong>を、シェーダー レジスタ `b0`、スペース 0 に直接渡す。4×4 行列がちょうど入る。定数バッファーを作らずに済む |
| `D3D12SerializeRootSignature` | ルート シグネチャを、GPU が読める形（バイト列）に変換 |
| `D3DCompile` | HLSL を、実行時にコンパイルする。`"vs_5_0"` はシェーダー モデル 5.0 の頂点シェーダー。失敗時のメッセージは `compile_error` に入る |
| `D3D12_INPUT_ELEMENT_DESC` | 頂点のレイアウト。`POSITION` は 12 バイト（float3）、`COLOR` はその後ろの 12 バイト目から 16 バイト（float4） |
| `FrontCounterClockwise = TRUE` | この教材の約束（CCW が表）を明示する |
| `PrimitiveTopologyType = LINE` | 線を描くパイプライン |
| `RTVFormats[0]` | 描画先のフォーマット。第 3 章のレンダー ターゲット ビューと<strong>同じ</strong>にする |

DirectX 12 のパイプラインの各項目は、[DX12 Guide の PSO](../directx/dx12/pso.md) と [Root Signature](../directx/dx12/root-signature.md) で説明しています。

### 頂点バッファー（アップロード ヒープ）

```cpp
  // ④ フレームごとの頂点バッファー（CPU から書ける領域を、常時マップしておく）
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

| 部分 | 説明 |
| --- | --- |
| `D3D12_HEAP_TYPE_UPLOAD` | CPU が書き、GPU が読むための領域 |
| `GENERIC_READ` | アップロード ヒープのリソースの初期状態（変更できない） |
| `Map` | CPU から書けるアドレスを得る。アップロード ヒープは<strong>マップしたまま使い続けてよい</strong> |
| フレームごとに 3 つ | GPU が前のフレームを読んでいる最中に、CPU が同じバッファーを書き換えないため（第 3 章のスロット） |

### 描く

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

| 部分 | 説明 |
| --- | --- |
| `memcpy(mapped_[slot], …)` | 頂点を、マップ済みのバッファーにコピー。GPU が読むのは、このフレームのコマンドが実行されるとき |
| `SetGraphicsRoot32BitConstants(0, 16, &view_proj, 0)` | 行列の 16 個の `float` を、ルート パラメーター 0 に書く。`Matrix`（SimpleMath）は、メモリ上で 16 個の `float` が並んだ<strong>行優先</strong>の並び |
| `LINELIST` | 頂点 2 つで 1 本の線 |
| `DrawInstanced(count, 1, 0, 0)` | 頂点数 `count`、インスタンス 1 つ |

## 手順 4：カメラ

エディタの定番、<strong>オービット カメラ</strong>（注視点の周りを回る）を作ります。

`Engine\src\EditorCamera.h`:

```cpp
#pragma once

#include <SimpleMath.h>

namespace mini {

// 注視点の周りを回るカメラ。右手系、Y が上、前は -Z。
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

`Engine\src\EditorCamera.cpp`:

```cpp
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
  // 球面座標。yaw = 0, pitch = 0 のとき、注視点の +Z 側に居て、-Z 方向を見る。
  const float cp = std::cos(pitch_);
  return target_ + Vector3(cp * std::sin(yaw_), std::sin(pitch_), cp * std::cos(yaw_)) * distance_;
}

EditorCamera::Matrix EditorCamera::View() const {
  return Matrix::CreateLookAt(Position(), target_, Vector3::Up);
}

EditorCamera::Matrix EditorCamera::Projection(float aspect) const {
  return Matrix::CreatePerspectiveFieldOfView(fov_, aspect, kNear, kFar);
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
  const float scale = distance_ * std::tan(fov_ * 0.5f) * 2.0f / 720.0f;   // 1 ピクセルが、注視点付近で何メートルか（高さ 720 を仮定）
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

| 部分 | 説明 |
| --- | --- |
| 球面座標 | `yaw`（横）、`pitch`（縦）、`distance`（距離）から、カメラの位置を求める。注視点を中心に、球の上を動く |
| `Matrix::CreateLookAt(eye, target, up)` | SimpleMath の<strong>右手系</strong>のビュー行列。前は −Z になる |
| `Matrix::CreatePerspectiveFieldOfView(fov, aspect, near, far)` | 右手系の透視投影。`fov` は<strong>縦</strong>の視野角（ラジアン） |
| `view._11, _21, _31` | ビュー行列の<strong>第 1 列</strong>が、カメラの右方向（ワールド空間）。行ベクトルの規約では、行列の列が基底の向きを表す |
| `Pan` の `scale` | 注視点の距離にある 1 ピクセルの大きさ。距離が遠いほど、同じマウスの動きで、大きく動く |
| `std::pow(0.9f, notches)` | ホイール 1 目盛りで、距離が 0.9 倍になる。ズームイン（`notches` > 0）で近づく |
| `std::clamp` | 距離を範囲内に収める |

## 手順 5：入力イベントを C の API に足す

### C の構造体と関数

`EngineApi.h` に追加します。

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

実装は、これまでと同じ形です（`Guard`、引数の検査）。

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

### エンジン側の入力処理

`Engine.h` の公開ヘッダーに、入力の型と関数を足します。

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

`Engine.cpp` の `Impl` に、カメラと入力の状態を持たせます。

```cpp
struct Engine::Impl {
  // …
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

## 手順 6：Tick で描く

`Renderer::Render` が、線の頂点とカメラの行列を受け取るように変更します。バック バッファーを塗る前後に、`OMSetRenderTargets` の後で、ビューポートとシザー矩形を設定し、線を描きます。

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

`Engine::Tick` で、グリッドと軸を組み立てます。

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

| 部分 | 説明 |
| --- | --- |
| `view * projection` | 行ベクトルの約束で、<strong>ビュー → 射影</strong>の順に掛ける。頂点は `v * view * projection` で変換される |
| 色 | 軸は X: 赤、Y: 緑、Z: 青（RGB = XYZ の覚え方） |
| `clear` を暗い色に | 色が変わる塗りつぶしは、ここで役目を終える |

## 手順 7：C# で入力を受けて送る

### Win32 のメッセージ

`ViewportHost` の `WndProc` をオーバーライドすると、子ウィンドウに届いたメッセージを受け取れます。

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

### ViewportHost で受ける

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `WndProc(…)` のオーバーライド | `HwndHost` が、子ウィンドウに届いたメッセージを渡してくる。`handled = true` にすると、それ以上、処理を進めない |
| `lParam` の下位／上位 16 ビット | マウス座標の詰め方。`(short)` のキャストで、<strong>符号つき</strong>にする（ウィンドウの左・上の外にドラッグすると負になる） |
| `SetCapture` / `ReleaseCapture` | ボタンを押している間、マウスが<strong>ウィンドウの外</strong>に出ても、メッセージを受け取り続ける。ドラッグ操作に必須 |
| `SetFocus` | キーボードの入力先にする。これをしないと、キー入力が届かない |
| `WM_MOUSEWHEEL` の `wParam` | 上位 16 ビットが回転量。`WHEEL_DELTA = 120` が 1 目盛り |
| `WM_KILLFOCUS` | フォーカスを失ったときのメッセージ。押しっぱなしのボタンの状態を、リセットさせる |
| `(long)wParam >> 16` | `nint` を `long` に広げてからシフトする。`>>` は符号つきシフト |

`ViewportInputEventArgs` と `InputType` を、ホストの近くに定義します。

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

### P/Invoke と窓口

`NativeMethods` に構造体と関数を足します。

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

`IEngineService` に `SendInput(...)` を足し、`PInvokeEngineService` で実装します。

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

### ビュー、ビューモデルをつなぐ

`ViewportView.xaml.cs` に、1 行足します。

```csharp
Host.InputReceived += (_, e) => ViewModel?.OnInput(e.Type, e.Button, e.X, e.Y, e.Delta);
```

`ViewportViewModel` に、命令の転送を足します。

```csharp
public void OnInput(Controls.InputType type, int button, float x, float y, float delta)
{
    // 描画スレッドで、エンジンへ送る（エンジンを触るのは描画スレッドだけ）
    _loop.Post(engine => engine.SendInput((int)type, button, x, y, delta, 0, 0));
}
```

マウスの動きは、1 秒に数百回届くことがあります。`Post` は、命令を積むだけなので軽いですが、<strong>描画スレッドが 1 フレームに複数の移動を一度に処理する</strong>ため、問題ありません。

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 起動 | 暗い背景に、灰色のグリッド、赤・緑・青の軸が見える |
| 右ボタンを押してドラッグ | カメラが、原点の周りを回る。上下にドラッグして、真上・真下を越えない |
| 中ボタンを押してドラッグ | 画面が平行移動する |
| ホイール | 近づく、遠ざかる |
| ボタンを押したまま枠の外に出る | ドラッグが続く（`SetCapture`） |
| ほかのパネルをクリック | 押しっぱなしの状態が解除される |

## よくあるミス

??? failure "線が何も出ない"
    頂点数が 0、またはシェーダーのコンパイルに失敗している（ログを確認）。`view_proj` が `Identity` のままで、すべての線がクリップされている。`CreateLookAt` と `CreatePerspectiveFieldOfView` の引数を確認する。

??? failure "絵が上下反転している／左右反転している"
    行列の転置の間違い。`row_major` を付けていない（列優先で読まれて、転置になる）。または、左手系用の関数（`CreateLookAtLH`）を使った。

??? failure "マウス ホイールで反応しない"
    `HwndHost` はフォーカスがないと、ホイールを受け取らないことがある。`WM_MOUSEWHEEL` は、フォーカスのあるウィンドウに送られる。クリックしたときに `SetFocus` を呼んでいるか確認する。

??? failure "右ドラッグで、メニューが出てしまう"
    `WM_CONTEXTMENU` が親に伝わって、コンテキスト メニューが開いている。WPF 側の `ContextMenu` を設定しない。

??? failure "カメラが勝手に動き続ける"
    `ButtonUp` が届いていない（ウィンドウの外でボタンを離した）。`SetCapture` を呼んでいるか、`FocusLost` で状態をリセットしているか確認する。

??? failure "`Pan` の速さが合わない"
    `Pan` の `scale` は、ビューポートの高さ 720 を仮定した近似。正確には、現在の高さを渡して計算する（改善は第 37 章で扱う）。

## この章のまとめ

- 入力の<strong>意味づけ</strong>はエンジンが持ち、C# は<strong>生の入力を送る</strong>だけ。
- 線の描画は、ルート定数 + 動的な頂点バッファー + 単純な HLSL。
- カメラは、行ベクトルの規約で `view * projection`。
- マウスのドラッグには `SetCapture` が必須。

## 次の章へ

次の章から第 5 部です。次の章（[第 34 章 シーンの API を作る](34-scene-api.md)）では、シーンに物（オブジェクト）を置けるようにして、C# から作成、削除、変更できる API を作ります。
