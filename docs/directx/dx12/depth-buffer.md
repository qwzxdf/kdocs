---
title: Depth Buffer (D3D12)
tags:
  - DirectX
---

# Depth Buffer (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>深度バッファ</strong>は、各ピクセルで、カメラから、最も近い、面までの、距離を、覚えておく、テクスチャです。後から、描いた物が、手前の物を、上書きしないよう、深度で、判定します（深度テスト）。D3D12 では、深度を、<strong>DEPTH_STENCIL の、フラグつきの、リソース</strong>として、作り、<strong>DSV</strong>（深度ステンシル ビュー）を、専用の、ヒープに、作って、描画で、束ねます。

!!! tip "ポイント"
    - 深度バッファ ＝ `ALLOW_DEPTH_STENCIL` つきの、テクスチャ。DSV は、<strong>DSV 用ヒープ</strong>に、作る。
    - フォーマットは `D32_FLOAT`（精度が高い）か `D24_UNORM_S8_UINT`（ステンシルつき）。
    - 読む（SRV）なら、<strong>`R32_TYPELESS`</strong> で作り、DSV と SRV で、型を、分ける。
    - 初期状態は `DEPTH_WRITE`。クリア値は、作成時に、最適化の、ヒントとして、渡す。
    - PSO の `DSVFormat` と、深度テストの、設定（`DepthStencilState`）が、必要。
    - 毎フレーム、<strong>`ClearDepthStencilView`</strong> で、クリアする。

## 作る

```cpp
// ① 深度バッファのリソース（DEFAULT ヒープ）。クリア値を、最適化のヒントとして、渡す。
D3D12_CLEAR_VALUE clear = {};
clear.Format = DXGI_FORMAT_D32_FLOAT;
clear.DepthStencil.Depth = 1.0f;                               // 最も遠い（reverse-Z なら 0.0f）
clear.DepthStencil.Stencil = 0;

auto heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT);
auto desc = CD3DX12_RESOURCE_DESC::Tex2D(DXGI_FORMAT_D32_FLOAT, width, height, 1, 1, 1, 0,
                                         D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL);   // 深度として使う、フラグ
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_DEPTH_WRITE, &clear,
                                IID_PPV_ARGS(&depth_buffer));
```

```cpp
// ② DSV 用の、ディスクリプタ ヒープと、DSV。
D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
heap_desc.NumDescriptors = 1;
heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_DSV;
heap_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;             // DSV は、シェーダー可視にできない
device->CreateDescriptorHeap(&heap_desc, IID_PPV_ARGS(&dsv_heap));

D3D12_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;
dsv.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_buffer.Get(), &dsv, dsv_heap->GetCPUDescriptorHandleForHeapStart());
```

深度バッファの、大きさは、<strong>レンダー ターゲットと、同じ</strong>にします。

## フォーマット

| フォーマット | 内容 | 使いどころ |
| --- | --- | --- |
| `D32_FLOAT` | 32 ビット浮動小数点。ステンシルなし | 精度が必要、reverse-Z |
| `D24_UNORM_S8_UINT` | 24 ビット + 8 ビットのステンシル | ステンシルが要る（マスク、輪郭） |
| `D32_FLOAT_S8X24_UINT` | 32 ビット浮動小数点 + ステンシル | 精度とステンシルの、両方 |
| `D16_UNORM` | 16 ビット | シャドウ マップ（軽量） |

## 描画で、使う

```cpp
// PSO: 深度の、フォーマットと、深度テストの、設定。
pso_desc.DSVFormat = DXGI_FORMAT_D32_FLOAT;
pso_desc.DepthStencilState = CD3DX12_DEPTH_STENCIL_DESC(D3D12_DEFAULT);        // 深度テスト有り・書き込み有り・LESS
```

```cpp
// 描画: レンダー ターゲットと、DSV を、束ねて、クリアする。
CD3DX12_CPU_DESCRIPTOR_HANDLE rtv(rtv_heap->GetCPUDescriptorHandleForHeapStart(), frame_index, rtv_size);
CD3DX12_CPU_DESCRIPTOR_HANDLE dsv_handle(dsv_heap->GetCPUDescriptorHandleForHeapStart());
command_list->OMSetRenderTargets(1, &rtv, FALSE, &dsv_handle);                 // 第 4 引数: DSV のハンドル

command_list->ClearDepthStencilView(dsv_handle, D3D12_CLEAR_FLAG_DEPTH | D3D12_CLEAR_FLAG_STENCIL,
                                    1.0f, 0, 0, nullptr);                      // 深度 1.0、ステンシル 0
```

| 引数（`ClearDepthStencilView`） | 内容 |
| --- | --- |
| `DepthStencilView` | DSV の CPU ハンドル |
| `ClearFlags` | `CLEAR_FLAG_DEPTH`、`CLEAR_FLAG_STENCIL` |
| `Depth`・`Stencil` | クリア値（作成時の、最適化値と、同じに） |
| `NumRects`・`pRects` | 範囲を、限定（`0`、`nullptr` で、全体） |

毎フレーム、必ず、クリアします。クリアしないと、前のフレームの、深度が、残り、新しい描画が、はじかれます。

## 深度を、読む（SRV）

AO・SSR・ソフト パーティクル・フォグで、深度を、シェーダーから、読むには、<strong>TYPELESS で作り、DSV と SRV で、型を、分けます</strong>。

```cpp
auto desc = CD3DX12_RESOURCE_DESC::Tex2D(DXGI_FORMAT_R32_TYPELESS, width, height, 1, 1, 1, 0,
                                         D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL);
D3D12_CLEAR_VALUE clear = {DXGI_FORMAT_D32_FLOAT};
clear.DepthStencil.Depth = 1.0f;
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_DEPTH_WRITE, &clear,
                                IID_PPV_ARGS(&depth_buffer));

D3D12_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;                           // 書く: 深度として
dsv.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_buffer.Get(), &dsv, dsv_handle);

D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R32_FLOAT;                           // 読む: 普通の float として
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(depth_buffer.Get(), &srv, srv_cpu_handle);
```

深度を、描いた後、読む前に、<strong>バリア</strong>で、`DEPTH_WRITE` から、`PIXEL_SHADER_RESOURCE`（または `NON_PIXEL_SHADER_RESOURCE`）に、切り替えます（[Resource Barrier](resource-barrier.md)）。読み終えたら、次のフレームの、描画の前に、`DEPTH_WRITE` に、戻します。

## 読み取り専用の、深度

深度テストを、しつつ、同じ深度を、SRV として、読みたい（ソフト パーティクル、半透明）ときは、<strong>読み取り専用の DSV</strong> を、作り、状態を、`DEPTH_READ`（と `PIXEL_SHADER_RESOURCE`）にします。

```cpp
dsv.Flags = D3D12_DSV_FLAG_READ_ONLY_DEPTH;                    // 深度の、書き込みを、禁止（テストだけ）
device->CreateDepthStencilView(depth_buffer.Get(), &dsv, readonly_dsv_handle);
// 状態: D3D12_RESOURCE_STATE_DEPTH_READ | D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE
```

## 深度ステンシル ステート

深度テストの、設定は、PSO の `DepthStencilState` で、行います（[PSO](pso.md)）。

```cpp
D3D12_DEPTH_STENCIL_DESC ds = CD3DX12_DEPTH_STENCIL_DESC(D3D12_DEFAULT);
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D12_DEPTH_WRITE_MASK_ALL;                // 半透明は、ZERO
ds.DepthFunc = D3D12_COMPARISON_FUNC_LESS;                     // reverse-Z は、GREATER
```

| 用途 | `DepthEnable` | `DepthWriteMask` | `DepthFunc` |
| --- | --- | --- | --- |
| 不透明 | TRUE | ALL | LESS |
| 半透明 | TRUE | ZERO | LESS_EQUAL |
| ポスト プロセス | FALSE | — | — |
| 事前深度の後の、本描画 | TRUE | ZERO | EQUAL |
| reverse-Z | TRUE | ALL | GREATER |

## リサイズ時

画面の、大きさが、変わったら、深度バッファも、作り直します。GPU が、使い終わるのを、フェンスで、待ってから、古いものを、解放し、新しいものを、作り、DSV も、書き直します（[Swap Chain](swap-chain.md)）。

## よくあるミス

??? failure "物が、前後、逆に見える"
    PSO の、`DepthStencilState` で、深度テストが、無効。`OMSetRenderTargets` に、DSV を、渡していない。PSO の `DSVFormat` が、`UNKNOWN`。

??? failure "深度の SRV を、作れない"
    `D32_FLOAT` で、作っている。`R32_TYPELESS` で作り、DSV と SRV で、型を、分ける。

??? failure "デバッグ レイヤーが、クリア値の、警告を、出す"
    `ClearDepthStencilView` の、値が、作成時の、最適化クリア値と、違う。そろえる。

??? failure "深度を、読むと、真っ黒、または、乱れる"
    バリアで、`DEPTH_WRITE` から、読み取り用の、状態に、遷移していない。

??? failure "画面が、真っ黒（深度テストで、全部、はじかれる）"
    深度を、クリアしていない、または、クリア値が、`0`（`LESS` で、全部、はじく）。`1.0` で、クリア（reverse-Z は 0.0）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度バッファ ＝ `ALLOW_DEPTH_STENCIL` つきのリソース。DSV は、DSV ヒープに
    - [x] `D32_FLOAT`（読むなら `R32_TYPELESS`）。初期状態は `DEPTH_WRITE`
    - [x] PSO に、`DSVFormat` と、深度ステート。描画で、`OMSetRenderTargets` に DSV
    - [x] 毎フレーム `ClearDepthStencilView`（作成時の、クリア値と、同じ値で）
    - [x] 読む前に、バリアで、状態を、切り替える

## 関連ページ

- [DirectX 12 Guide](index.md)
- [PSO](pso.md)
- [Resource Barrier](resource-barrier.md)
- [Descriptor Heap](descriptor-heap.md)
- [Depth Buffer and DSV](../dx11/depth-stencil.md)
- [Microsoft Learn: 深度バッファ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/depth-buffers)
