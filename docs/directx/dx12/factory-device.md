---
title: Device and Factory
tags:
  - DirectX
---

# Device and Factory

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 の、出発点は、<strong>DXGI ファクトリー</strong>で、GPU（アダプター）を、選び、そのアダプターから、<strong>デバイス</strong>（`ID3D12Device`）を、作ることです。デバイスは、GPU に、「物を作らせる」窓口で、リソース、ヒープ、PSO、ルート シグネチャ、コマンド キューなどは、すべて、デバイスが、作ります。<strong>命令を、出す、窓口は、デバイスには、ありません</strong>（命令は、コマンド リストに、記録します）。

!!! tip "ポイント"
    - デバイス ＝ 作る窓口。命令を、出すのは、デバイスでは、なく、[Command List](command-list.md) に、記録する。
    - <strong>デバッグ レイヤーは、デバイスを、作る前に</strong>、有効にする（`EnableDebugLayer`）。
    - アダプターは、DXGI で、選ぶ。高性能な GPU を、優先する。
    - 機能レベルは、11.0 以上。個々の、機能（DXR、メッシュ シェーダー）は、`CheckFeatureSupport` で、確認する。
    - 新しい機能は、`ID3D12Device5`、`Device10` のような、番号つきの、インターフェースに、ある。

## デバッグ レイヤー

```cpp
#include <d3d12.h>
#include <dxgi1_6.h>
#include <wrl/client.h>

#include <d3dx12.h>

using Microsoft::WRL::ComPtr;

UINT factory_flags = 0;
#if defined(_DEBUG)
{
  ComPtr<ID3D12Debug> debug;
  if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
    debug->EnableDebugLayer();                 // デバイスを作る「前」に呼ぶ。後だと、デバイスが、無効になる
    factory_flags |= DXGI_CREATE_FACTORY_DEBUG;
  }
}
#endif
```

デバッグ レイヤーは、<strong>デバイスを、作る前</strong>に、有効にします。作った後で、有効にすると、既存の、デバイスが、削除されます。詳しくは、[Debug Layer](debug-layer.md) です。

## ファクトリーと、アダプター

```cpp
ComPtr<IDXGIFactory6> factory;
CreateDXGIFactory2(factory_flags, IID_PPV_ARGS(&factory));

// 高性能な GPU から順に、D3D12 に対応する、最初のアダプターを選ぶ。
ComPtr<IDXGIAdapter1> adapter;
for (UINT i = 0;
     factory->EnumAdapterByGpuPreference(i, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE, IID_PPV_ARGS(&adapter)) !=
     DXGI_ERROR_NOT_FOUND;
     ++i) {
  DXGI_ADAPTER_DESC1 desc;
  adapter->GetDesc1(&desc);
  if (desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE) continue;               // WARP（ソフトウェア）は、飛ばす
  // nullptr を渡すと、「作れるか」だけを、確認する（デバイスは、作らない）。
  if (SUCCEEDED(D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_11_0, __uuidof(ID3D12Device), nullptr))) break;
}
```

アダプターの、列挙は、[DXGI Factory and Adapter](../dx11/dxgi.md) と、同じです（DXGI は、DirectX の、各バージョンに、共通）。

## デバイスを作る

```cpp
ComPtr<ID3D12Device> device;
HRESULT hr = D3D12CreateDevice(adapter.Get(),                // 使う GPU
                               D3D_FEATURE_LEVEL_11_0,       // 最低限の、機能レベル
                               IID_PPV_ARGS(&device));
if (FAILED(hr)) {
  // 失敗: GPU が、D3D12 に対応していない。WARP（ソフトウェア）で、再試行する
}
```

| 引数 | 内容 |
| --- | --- |
| `pAdapter` | 使う GPU。`nullptr` で、既定 |
| `MinimumFeatureLevel` | 必要な、最低の、機能レベル。D3D12 は、11.0 から |
| `riid`・`ppDevice` | 取り出す、インターフェース。`IID_PPV_ARGS` で、渡す |

D3D12 の、機能レベルの、最低が、11.0 なのは、古い世代の、GPU でも、D3D12 の、API が、使える（機能は、限られる）、ためです。

## 機能の、確認

DXR、メッシュ シェーダー、ビンドレスなどは、<strong>GPU ごとに、対応が違う</strong>ので、使う前に、確認します。

```cpp
// DXR（レイトレーシング）の対応。
D3D12_FEATURE_DATA_D3D12_OPTIONS5 options5 = {};
device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS5, &options5, sizeof(options5));
bool dxr = options5.RaytracingTier >= D3D12_RAYTRACING_TIER_1_0;

// シェーダー モデルの、最大の対応。
D3D12_FEATURE_DATA_SHADER_MODEL shader_model = {D3D_SHADER_MODEL_6_6};
device->CheckFeatureSupport(D3D12_FEATURE_SHADER_MODEL, &shader_model, sizeof(shader_model));
// shader_model.HighestShaderModel に、対応する、最大の SM が入る。

// リソース バインディングの、段階（ビンドレスに、影響）。
D3D12_FEATURE_DATA_D3D12_OPTIONS options = {};
device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS, &options, sizeof(options));
// options.ResourceBindingTier（1・2・3）
```

| 機能 | 確認する、構造体 | 内容 |
| --- | --- | --- |
| DXR | `OPTIONS5.RaytracingTier` | `1_0`、`1_1`（`RayQuery`） |
| メッシュ シェーダー | `OPTIONS7.MeshShaderTier` | メッシュ・増幅シェーダー |
| シェーダー モデル | `D3D12_FEATURE_SHADER_MODEL` | 最大の SM（6.0〜6.8） |
| リソース バインディング | `OPTIONS.ResourceBindingTier` | 3 で、ほぼ、無制限（ビンドレス） |
| 拡張バリア | `OPTIONS12.EnhancedBarriersSupported` | 新しい、バリア API |

## 新しい、インターフェース

D3D12 は、機能を、足すたびに、`ID3D12Device1`、`…Device5`、`…Device10` のように、番号つきの、インターフェースを、増やします。`QueryInterface`（`ComPtr::As`）で、取り出します。

```cpp
ComPtr<ID3D12Device5> device5;
if (SUCCEEDED(device.As(&device5))) {
  // DXR の、ステート オブジェクト（CreateStateObject）、加速構造（GetRaytracingAccelerationStructurePrebuildInfo）が、使える
}
```

| インターフェース | 追加された、主な機能 |
| --- | --- |
| `ID3D12Device1` | パイプライン ライブラリ、残り容量の確認 |
| `ID3D12Device2` | パイプライン ステート ストリーム（`CreatePipelineState`） |
| `ID3D12Device5` | DXR（ステート オブジェクト、加速構造） |
| `ID3D12Device8` | `GetResourceAllocationInfo2` など |
| `ID3D12Device10` | 拡張バリア、`CreateCommittedResource3` |

コマンド リストにも、同じ、番号つきの、系列（`ID3D12GraphicsCommandList4`、`…6`、`…7`）が、あります。

## 名前を付ける

```cpp
device->SetName(L"Main Device");
resource->SetName(L"GBuffer Albedo");                        // PIX、デバッグ レイヤーに、名前が、出る
```

`SetName` で、リソースなどに、名前を、付けられます。全オブジェクトに、名前を、付けると、デバッグが、はるかに、楽になります。

## 後始末

D3D12 は、終了前に、<strong>GPU が、すべての、仕事を、終えるのを、待つ</strong>必要があります。GPU が、まだ、使っている、リソースを、解放すると、クラッシュします。

```cpp
WaitForGpu();                                                // フェンスで、GPU の完了を、待つ（fence.md）
// この後で、ComPtr を、解放する（リソース → デバイスの順）
```

## よくあるミス

??? failure "デバッグ レイヤーを、有効にしたのに、メッセージが、出ない"
    `EnableDebugLayer` を、デバイスを、作った後に、呼んでいる。デバイスを、作る前に、呼ぶ。

??? failure "`D3D12CreateDevice` が、失敗する"
    GPU が、D3D12 に、対応していない。または、「グラフィックス ツール」が、入っていない状態で、デバッグ レイヤーを、要求した。WARP アダプターで、再試行する。

??? failure "ノート PC で、内蔵 GPU が、選ばれて、遅い"
    アダプターを、`nullptr`（既定）に、任せている。`EnumAdapterByGpuPreference(HIGH_PERFORMANCE)` で、選ぶ。

??? failure "終了時に、クラッシュする（GPU が、リソースを、使用中）"
    GPU の完了を、待たずに、リソースを、解放した。終了前に、フェンスで、待つ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] デバイス ＝ 作る窓口。D3D12 に、即時コンテキストは、無い
    - [x] デバッグ レイヤーは、デバイスを、作る「前」に、有効にする
    - [x] ファクトリー → アダプター（高性能 GPU）→ `D3D12CreateDevice`
    - [x] 機能は、`CheckFeatureSupport` で、確認してから、使う
    - [x] 新しい機能は、番号つきの、インターフェース（`Device5` など）
    - [x] 終了前に、GPU の完了を、待つ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command Queue](command-queue.md)
- [Debug Layer](debug-layer.md)
- [DXGI Factory and Adapter](../dx11/dxgi.md)
- [Microsoft Learn: D3D12CreateDevice](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-d3d12createdevice)
