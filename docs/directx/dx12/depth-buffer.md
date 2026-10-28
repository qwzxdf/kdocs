---
title: Depth Buffer (D3D12)
tags:
  - DirectX
---

# Depth Buffer (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

3D のシーンを描くときあとから描いた物が手前にある物を上書きしてしまっては困ります。そこで、各ピクセルで「今までに描いた中で、カメラに一番近い面までの距離」を覚えておき新しく描く面のほうが遠ければ、捨てます。この距離を覚えておくテクスチャが <strong>深度バッファ</strong>です。判定のことを深度テストと呼びます。

D3D12 では深度バッファを `ALLOW_DEPTH_STENCIL` のフラグを付けたリソースとして作ります。そして、専用の DSV ヒープに DSV（深度ステンシル ビュー）を作って、描画のときに束ねます。

!!! tip "ポイント"
    - 深度バッファは `ALLOW_DEPTH_STENCIL` を付けたテクスチャ。DSV は DSV 専用のヒープに作る。
    - 形式は `D32_FLOAT`（精度が高い）か `D24_UNORM_S8_UINT`（ステンシル付き）。
    - 深度を読む（SRV）なら `R32_TYPELESS` で作って、DSV と SRV で型を分ける。
    - 初期状態は `DEPTH_WRITE`。クリア値は作るときに最適化のヒントとして渡す。
    - PSO には `DSVFormat` と深度テストの設定（`DepthStencilState`）が必要。
    - 毎フレーム、`ClearDepthStencilView` でクリアする。

!!! info "このページを読む前に"
    DSV のヒープは [Descriptor Heap](descriptor-heap.md)、テクスチャを作る `MakeTexture2DDesc` は [Helper Functions](util.md)、深度テストの設定を持つ PSO は [PSO](pso.md)、状態の切り替えは [Resource Barrier](resource-barrier.md) で説明しています。クリアの命令は [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md#cleardepthstencilview) にあります。

## 作る

まず、深度バッファのリソースを作ります。クリア値を最適化のヒントとして渡します。

```cpp
// 1. 深度バッファのリソース（DEFAULT のヒープ）。
D3D12_CLEAR_VALUE clear = {};
clear.Format = DXGI_FORMAT_D32_FLOAT;
clear.DepthStencil.Depth = 1.0f;  // 最も遠い（リバース Z なら 0.0f）
clear.DepthStencil.Stencil = 0;

D3D12_HEAP_PROPERTIES heap = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
D3D12_RESOURCE_DESC desc = MakeTexture2DDesc(DXGI_FORMAT_D32_FLOAT, width, height, 1, 1,
                                             D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL);  // 深度として使うフラグ
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_DEPTH_WRITE, &clear,
                                IID_PPV_ARGS(&depth_buffer));
```

次に、DSV 用のヒープと DSV を作ります。

```cpp
// 2. DSV 用のディスクリプタ ヒープと DSV。
D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
heap_desc.NumDescriptors = 1;
heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_DSV;
heap_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;  // DSV はシェーダー可視にできない
device->CreateDescriptorHeap(&heap_desc, IID_PPV_ARGS(&dsv_heap));

D3D12_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;
dsv.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_buffer.Get(), &dsv, dsv_heap->GetCPUDescriptorHandleForHeapStart());
```

深度バッファの大きさはレンダー ターゲットと同じにします。違うと描画のときにエラーになります。

## 形式を選ぶ

`D32_FLOAT` は 32 ビットの浮動小数点で、ステンシルはありません。精度が必要なときやリバース Z に向きます。`D24_UNORM_S8_UINT` は 24 ビットの深度と 8 ビットのステンシルです。マスクや輪郭のようにステンシルが要るときに使います。`D32_FLOAT_S8X24_UINT` は 32 ビット浮動小数点の深度とステンシルの両方です。`D16_UNORM` は 16 ビットで軽くシャドウ マップに使います。

## 描画で使う

PSO に深度の形式と深度テストの設定を書きます。

```cpp
pso_desc.DSVFormat = DXGI_FORMAT_D32_FLOAT;
pso_desc.DepthStencilState = MakeDefaultDepthStencilDesc();  // 深度テストあり、書き込みあり、LESS
```

描画ではレンダー ターゲットと DSV を束ねて、クリアします。

```cpp
D3D12_CPU_DESCRIPTOR_HANDLE rtv = OffsetHandle(rtv_heap->GetCPUDescriptorHandleForHeapStart(), frame_index, rtv_size);
D3D12_CPU_DESCRIPTOR_HANDLE dsv_handle = dsv_heap->GetCPUDescriptorHandleForHeapStart();
command_list->OMSetRenderTargets(1, &rtv, FALSE, &dsv_handle);  // 第 4 引数は DSV のハンドルへのポインター

command_list->ClearDepthStencilView(dsv_handle, D3D12_CLEAR_FLAG_DEPTH | D3D12_CLEAR_FLAG_STENCIL,
                                    1.0f, 0, 0, nullptr);  // 深度 1.0、ステンシル 0
```

`ClearDepthStencilView` の引数は DSV のハンドル、クリアする対象（`CLEAR_FLAG_DEPTH` と `CLEAR_FLAG_STENCIL`）、深度とステンシルの値、範囲です。範囲を `0` と `nullptr` にすると、全体を塗ります。値は作るときの最適化クリア値とそろえます。

毎フレーム、必ずクリアします。クリアしないと前のフレームの深度が残って、新しい描画がはじかれます。

## 深度をシェーダーで読む

AO、SSR、ソフト パーティクル、フォグのように深度をシェーダーから読みたいときは、リソースを TYPELESS で作り DSV と SRV で型を分けます。

```cpp
D3D12_RESOURCE_DESC desc = MakeTexture2DDesc(DXGI_FORMAT_R32_TYPELESS, width, height, 1, 1,
                                             D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL);
D3D12_CLEAR_VALUE clear = {};
clear.Format = DXGI_FORMAT_D32_FLOAT;
clear.DepthStencil.Depth = 1.0f;
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_DEPTH_WRITE, &clear,
                                IID_PPV_ARGS(&depth_buffer));

D3D12_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;  // 書くとき。深度として
dsv.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_buffer.Get(), &dsv, dsv_handle);

D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R32_FLOAT;  // 読むとき。普通の float として
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(depth_buffer.Get(), &srv, srv_cpu_handle);
```

深度を描いたあと読む前にバリアで `DEPTH_WRITE` から `PIXEL_SHADER_RESOURCE`（または `NON_PIXEL_SHADER_RESOURCE`）へ切り替えます（[Resource Barrier](resource-barrier.md)）。読み終えたら次のフレームの描画の前に `DEPTH_WRITE` へ戻します。

## 読み取り専用の深度

深度テストをしながら同じ深度を SRV として読みたいとき（ソフト パーティクルや半透明）は、読み取り専用の DSV を作って、状態を `DEPTH_READ`（と `PIXEL_SHADER_RESOURCE`）にします。

```cpp
dsv.Flags = D3D12_DSV_FLAG_READ_ONLY_DEPTH;  // 深度の書き込みを禁止（テストだけ）
device->CreateDepthStencilView(depth_buffer.Get(), &dsv, readonly_dsv_handle);
// 状態は D3D12_RESOURCE_STATE_DEPTH_READ | D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE
```

## 深度ステンシルの設定

深度テストの設定は PSO の `DepthStencilState` で行います（[PSO](pso.md)）。

```cpp
D3D12_DEPTH_STENCIL_DESC ds = MakeDefaultDepthStencilDesc();
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D12_DEPTH_WRITE_MASK_ALL;  // 半透明は ZERO
ds.DepthFunc = D3D12_COMPARISON_FUNC_LESS;       // リバース Z は GREATER
```

使い分けは次のとおりです。不透明な物は `DepthEnable = TRUE`、`DepthWriteMask = ALL`、`DepthFunc = LESS` でテストして書き込みます。半透明はテストはしても書き込みはしないので `DepthWriteMask = ZERO`、`DepthFunc = LESS_EQUAL` にします。ポストプロセスは深度を使わないので、`DepthEnable = FALSE` です。事前に深度だけを描いた（深度プリパス）あとの本描画は `DepthWriteMask = ZERO`、`DepthFunc = EQUAL` で同じ深度の面だけを通します。リバース Z では `DepthFunc = GREATER` にします。

## 画面の大きさが変わったとき

画面の大きさが変わったら深度バッファも作り直します。GPU が使い終わるのをフェンスで待ってから、古いものを解放して新しいものを作り DSV も書き直します（[Swap Chain](swap-chain.md)）。

## よくあるミス

??? failure "物が前後逆に見える"
    PSO の `DepthStencilState` で深度テストが無効になっています。`OMSetRenderTargets` に DSV を渡していないか PSO の `DSVFormat` が `UNKNOWN` の場合もあります。

??? failure "深度の SRV を作れない"
    `D32_FLOAT` で作っています。`R32_TYPELESS` で作って DSV と SRV で型を分けます。

??? failure "デバッグ レイヤーがクリア値の警告を出す"
    `ClearDepthStencilView` の値が作るときの最適化クリア値と違います。そろえます。

??? failure "深度を読むと真っ黒になるまたは乱れる"
    バリアで `DEPTH_WRITE` から読み取り用の状態へ切り替えていません。

??? failure "画面が真っ黒になる（深度テストで全部はじかれる）"
    深度をクリアしていないかクリア値が `0` です（`LESS` では、すべてはじかれます）。`1.0` でクリアします（リバース Z は 0.0）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度バッファは `ALLOW_DEPTH_STENCIL` を付けたリソース。DSV は DSV ヒープに作る
    - [x] 形式は `D32_FLOAT`（読むなら `R32_TYPELESS`）。初期状態は `DEPTH_WRITE`
    - [x] PSO に `DSVFormat` と深度の設定。描画で `OMSetRenderTargets` に DSV を渡す
    - [x] 毎フレーム `ClearDepthStencilView`（作るときのクリア値と同じ値で）
    - [x] 読む前にバリアで状態を切り替える

## 関連ページ

- [DirectX 12 Guide](index.md)
- [PSO](pso.md)
- [Helper Functions](util.md)
- [Resource Barrier](resource-barrier.md)
- [Descriptor Heap](descriptor-heap.md)
- [Microsoft Learn: 深度バッファ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/depth-buffers)
