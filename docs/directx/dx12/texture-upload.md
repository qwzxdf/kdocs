---
title: Texture Upload
tags:
  - DirectX
---

# Texture Upload

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

テクスチャを、GPU に、送る流れは、頂点バッファと、同じで、<strong>UPLOAD ヒープの、中継バッファに、書き、GPU の、コピー命令で、DEFAULT ヒープの、テクスチャへ、送ります</strong>。ただし、テクスチャは、<strong>行の幅（ピッチ）に、アラインメントが、ある</strong>ので、中継バッファでの、並びが、画像と、違います。`UpdateSubresources` が、その面倒を、見てくれます。ミップマップも、D3D12 では、<strong>自動生成が、無い</strong>ので、自分で、作ります。

!!! tip "ポイント"
    - 流れ: DEFAULT の、テクスチャを、作る → UPLOAD の、中継バッファを、作る → `UpdateSubresources` で、コピーを、記録 → バリアで、`PIXEL_SHADER_RESOURCE` へ → SRV を、作る。
    - 中継バッファの、1 行の、幅は、<strong>256 バイト</strong>の倍数（`D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`）。
    - 中継バッファの、大きさは、`GetRequiredIntermediateSize` で、求める。
    - GPU が、コピーを、終えるまで、中継バッファは、解放できない（フェンス）。
    - ミップマップは、自動で、作られない。ビルド時に、DDS に、入れておく、または、計算シェーダーで、作る。

## 作る

```cpp
// ① DEFAULT ヒープの、テクスチャを、作る（初期状態は COPY_DEST）。
auto texture_desc = CD3DX12_RESOURCE_DESC::Tex2D(DXGI_FORMAT_R8G8B8A8_UNORM_SRGB, width, height, 1, 1);
auto default_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT);
device->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &texture_desc, D3D12_RESOURCE_STATE_COPY_DEST,
                                nullptr, IID_PPV_ARGS(&texture));

// ② 中継バッファの、大きさを、求めて、UPLOAD ヒープに、作る。
const UINT64 upload_size = GetRequiredIntermediateSize(texture.Get(), 0, 1);   // サブリソース 0 から 1 個ぶん
auto upload_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_UPLOAD);
auto upload_desc = CD3DX12_RESOURCE_DESC::Buffer(upload_size);
device->CreateCommittedResource(&upload_heap, D3D12_HEAP_FLAG_NONE, &upload_desc, D3D12_RESOURCE_STATE_GENERIC_READ,
                                nullptr, IID_PPV_ARGS(&upload_buffer));
```

`GetRequiredIntermediateSize` は、行の、アラインメントを、含んだ、中継バッファの、必要な、大きさを、返します（画像の、大きさ `width × height × 4` より、大きくなりうる）。

## コピーを、記録する

```cpp
// ③ 画素データを、記述して、UpdateSubresources で、コピー（中継バッファへの、書き込みと、コピー命令の、記録）。
D3D12_SUBRESOURCE_DATA data = {};
data.pData = pixels;                                          // 画素（RGBA、各 8 ビット）
data.RowPitch = width * 4;                                    // 1 行のバイト数（画像側。256 の倍数でなくてよい）
data.SlicePitch = data.RowPitch * height;                     // 1 枚の、バイト数

UpdateSubresources(command_list.Get(), texture.Get(), upload_buffer.Get(),
                   0,                                          // 中継バッファ内の、開始オフセット
                   0, 1,                                       // 最初のサブリソース、サブリソースの数
                   &data);

// ④ コピー後は、シェーダーから、読めるように、状態を、遷移する。
auto barrier = CD3DX12_RESOURCE_BARRIER::Transition(texture.Get(), D3D12_RESOURCE_STATE_COPY_DEST,
                                                    D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);
command_list->ResourceBarrier(1, &barrier);
```

`UpdateSubresources`（`d3dx12.h`）は、中継バッファに、<strong>行ごとに、256 バイト境界に、そろえて</strong>、画素を、コピーし、`CopyTextureRegion` の、命令を、コマンド リストに、記録します。<strong>実際の、GPU への、コピーは、`ExecuteCommandLists` の、後</strong>です。

```cpp
command_list->Close();
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
WaitForGpu();                                                 // コピーの完了を、待つ
upload_buffer.Reset();                                        // その後で、中継バッファを、解放
```

## SRV を作る

```cpp
// ⑤ シェーダーから、読むための、SRV を、ヒープに、作る。
D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(texture.Get(), &srv, srv_cpu_handle);
```

ディスクリプタの、作り方は、[Descriptor](descriptor.md) です。色のテクスチャは、`_SRGB`、法線マップなどは、リニアの `_UNORM` です。

## 行の、アラインメント

中継バッファでは、画像の、1 行が、<strong>256 バイトの倍数</strong>の幅に、そろえられて、並びます（`D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`）。`UpdateSubresources` は、これを、自動で、行いますが、自分で、コピーするとき（`CopyTextureRegion`）は、注意が、必要です。

```cpp
// 例: 幅 100 ピクセル（400 バイト）の画像 → 中継バッファの、1 行は、512 バイト（256 の倍数に切り上げ）。
const UINT row_pitch = (width * 4 + 255) & ~255;

// GetCopyableFootprints で、正確な、レイアウトを、取得できる。
D3D12_PLACED_SUBRESOURCE_FOOTPRINT footprint;
UINT64 total_bytes;
device->GetCopyableFootprints(&texture_desc, 0, 1, 0, &footprint, nullptr, nullptr, &total_bytes);
// footprint.Footprint.RowPitch が、中継バッファでの、1 行のバイト数
```

`CopyTextureRegion` を、自分で、使うときは、`GetCopyableFootprints` で、レイアウトを、取り、その `RowPitch` で、画素を、並べます。

## ミップマップ

D3D12 には、ミップを、自動で、作る、関数が、<strong>ありません</strong>。ミップは、次のいずれかで、用意します。

| 方法 | 内容 |
| --- | --- |
| ビルド時に、DDS に、入れる | 画像ツール（`texconv`）で、ミップを、作り、DDS に、保存。実行時は、全ミップを、アップロード。最も、一般的 |
| 計算シェーダーで、作る | ミップ 0 から、順に、半分に、縮小する、計算シェーダーを、ミップごとに、ディスパッチ |
| CPU で、作る | 起動時に、縮小して、全ミップを、アップロード |

```cpp
// 全ミップを、アップロードする（サブリソース = ミップごと）。
std::vector<D3D12_SUBRESOURCE_DATA> subresources(mip_count);
for (UINT m = 0; m < mip_count; ++m) {
  subresources[m].pData = mip_pixels[m];
  subresources[m].RowPitch = (width >> m) * 4;
  subresources[m].SlicePitch = subresources[m].RowPitch * (height >> m);
}
UpdateSubresources(command_list.Get(), texture.Get(), upload_buffer.Get(), 0, 0, mip_count, subresources.data());
```

テクスチャの、作成時の、`MipLevels` を、ミップの数に、し、`GetRequiredIntermediateSize(texture, 0, mip_count)` で、中継バッファを、作ります。

## 画像ファイルの、読み込み

D3D12 自身は、PNG・JPG を、デコードしません。ライブラリを、使います。

| 方法 | 内容 |
| --- | --- |
| DirectXTK12 の `LoadWICTextureFromFile`、`LoadDDSTextureFromFile` | デコードして、`D3D12_SUBRESOURCE_DATA` を、返す。`ResourceUploadBatch` が、アップロードを、まとめる |
| DirectXTex | 画像の、読み込み、ミップ生成、圧縮 |
| `stb_image` | 軽量の、デコーダー。RGBA の、ピクセル列を、返す |

```cpp
// DirectXTK12: アップロードを、まとめて、非同期に、行う。
DirectX::ResourceUploadBatch upload(device.Get());
upload.Begin();
DirectX::CreateWICTextureFromFile(device.Get(), upload, L"albedo.png", &texture, true /* ミップ自動生成 */);
auto finished = upload.End(command_queue.Get());            // std::future。完了を、待てる
finished.wait();
```

製品では、ビルド時に、圧縮（BC7）つきの DDS に、変換して、実行時は、そのまま、アップロードします（[Texture Streaming](../../rendering/texture-streaming.md)）。

## 多数の、テクスチャを、まとめて

ロード時に、数百枚の、テクスチャを、アップロードするとき、1 枚ずつ、`WaitForGpu` すると、遅いです。<strong>1 つの、コマンド リストに、全部の、コピーを、記録し</strong>、<strong>1 回、投げて、1 回、待つ</strong>のが、効率的です。中継バッファは、全部の、コピーが、終わるまで、保ちます。

## よくあるミス

??? failure "テクスチャが、斜めに、ずれる、ノイズのように、見える"
    行のピッチを、`width * 4` のまま、中継バッファに、並べている（256 の倍数に、そろえていない）。`UpdateSubresources` を、使う。

??? failure "コピー後に、テクスチャが、真っ黒（または、化ける）"
    GPU が、コピーを、終える前に、中継バッファを、解放した。または、`COPY_DEST` → `PIXEL_SHADER_RESOURCE` の、バリアを、入れていない。

??? failure "遠くが、ちらつく（ミップが、無い）"
    D3D12 に、`GenerateMips` は、無い。ミップを、DDS で、用意するか、計算シェーダーで、作る。

??? failure "色が、くすむ（暗い）"
    色の画像を、`_UNORM`（リニア）で、読んでいる。`_SRGB` にする。

??? failure "ロードが、遅い"
    テクスチャごとに、`WaitForGpu` している。まとめて、1 回、待つ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DEFAULT のテクスチャ + UPLOAD の中継バッファ → `UpdateSubresources`
    - [x] 中継バッファの、1 行は、256 バイトの倍数。`GetRequiredIntermediateSize` で、大きさを、求める
    - [x] コピー後は、バリア（`COPY_DEST` → `PIXEL_SHADER_RESOURCE`）。完了まで、中継バッファを、解放しない
    - [x] ミップは、自動で、作られない。DDS か、計算シェーダー
    - [x] 色は `_SRGB`、データは、リニア
    - [x] 多数は、1 つのリストに、まとめて、1 回待つ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Upload Buffer](upload-buffer.md)
- [Descriptor](descriptor.md)
- [Resource Barrier](resource-barrier.md)
- [Texture Streaming](../../rendering/texture-streaming.md)
- [Microsoft Learn: UpdateSubresources](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/uploading-resources)
