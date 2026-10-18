---
title: Texture Upload
tags:
  - DirectX
---

# Texture Upload

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

テクスチャを GPU に送る流れは頂点バッファと同じで <strong>UPLOAD ヒープの、中継バッファに書き GPU のコピー命令で DEFAULT ヒープのテクスチャへ送ります</strong>。ただし、テクスチャは <strong>行の幅（ピッチ）にアラインメントがある</strong>ので中継バッファでの並びが画像と、違います。`UpdateSubresources` がその面倒を見てくれます。ミップマップも D3D12 では <strong>自動生成が無い</strong>ので自分で、作ります。

!!! tip "ポイント"
    - 流れ: DEFAULT のテクスチャを作る → UPLOAD の、中継バッファを作る → `UpdateSubresources` で、コピーを記録 → バリアで `PIXEL_SHADER_RESOURCE` へ → SRV を作る。
    - 中継バッファの 1 行の幅は、<strong>256 バイト</strong>の倍数（`D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`）。
    - 中継バッファの大きさは `GetRequiredIntermediateSize` で、求める。
    - GPU がコピーを終えるまで中継バッファは解放できない（フェンス）。
    - ミップマップは自動で、作られない。ビルド時に DDS に入れておくまたは、計算シェーダーで作る。

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

`GetRequiredIntermediateSize` は行のアラインメントを含んだ、中継バッファの必要な大きさを返します（画像の大きさ `width × height × 4` より大きくなりうる）。

## コピーを記録する

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

`UpdateSubresources`（`d3dx12.h`）は中継バッファに <strong>行ごとに 256 バイト境界にそろえて</strong>、画素をコピーし `CopyTextureRegion` の命令をコマンド リストに記録します。<strong>実際の GPU へのコピーは `ExecuteCommandLists` の後</strong>です。

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

ディスクリプタの作り方は[Descriptor](descriptor.md) です。色のテクスチャは `_SRGB`、法線マップなどはリニアの `_UNORM` です。

## 行のアラインメント

中継バッファでは画像の 1 行が、<strong>256 バイトの倍数</strong>の幅にそろえられて並びます（`D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`）。`UpdateSubresources` はこれを自動で行いますが自分で、コピーするとき（`CopyTextureRegion`）は注意が、必要です。

```cpp
// 例: 幅 100 ピクセル（400 バイト）の画像 → 中継バッファの、1 行は、512 バイト（256 の倍数に切り上げ）。
const UINT row_pitch = (width * 4 + 255) & ~255;

// GetCopyableFootprints で、正確な、レイアウトを、取得できる。
D3D12_PLACED_SUBRESOURCE_FOOTPRINT footprint;
UINT64 total_bytes;
device->GetCopyableFootprints(&texture_desc, 0, 1, 0, &footprint, nullptr, nullptr, &total_bytes);
// footprint.Footprint.RowPitch が、中継バッファでの、1 行のバイト数
```

`CopyTextureRegion` を自分で使うときは `GetCopyableFootprints` で、レイアウトを取りその `RowPitch` で画素を並べます。

## ミップマップ

D3D12 にはミップを自動で作る関数が、<strong>ありません</strong>。ミップは次のいずれかで用意します。

| 方法 | 内容 |
| --- | --- |
| ビルド時に DDS に入れる | 画像ツール（`texconv`）で、ミップを作り DDS に保存。実行時は全ミップをアップロード。最も一般的 |
| 計算シェーダーで作る | ミップ 0 から順に半分に縮小する計算シェーダーをミップごとに、ディスパッチ |
| CPU で作る | 起動時に縮小して全ミップをアップロード |

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

テクスチャの作成時の `MipLevels` をミップの数にし `GetRequiredIntermediateSize(texture, 0, mip_count)` で、中継バッファを作ります。

## 画像ファイルの読み込み

D3D12 自身は PNG・JPG をデコードしません。ライブラリを使います。

| 方法 | 内容 |
| --- | --- |
| DirectXTK12 の `LoadWICTextureFromFile`、`LoadDDSTextureFromFile` | デコードして `D3D12_SUBRESOURCE_DATA` を返す。`ResourceUploadBatch` がアップロードをまとめる |
| DirectXTex | 画像の読み込みミップ生成、圧縮 |
| `stb_image` | 軽量のデコーダー。RGBA のピクセル列を返す |

```cpp
// DirectXTK12: アップロードを、まとめて、非同期に、行う。
DirectX::ResourceUploadBatch upload(device.Get());
upload.Begin();
DirectX::CreateWICTextureFromFile(device.Get(), upload, L"albedo.png", &texture, true /* ミップ自動生成 */);
auto finished = upload.End(command_queue.Get());            // std::future。完了を、待てる
finished.wait();
```

製品ではビルド時に圧縮（BC7）つきの DDS に変換して実行時はそのままアップロードします（[Texture Streaming](../../rendering/texture-streaming.md)）。

## 多数のテクスチャをまとめて

ロード時に数百枚のテクスチャをアップロードするとき 1 枚ずつ `WaitForGpu` すると遅いです。<strong>1 つのコマンド リストに全部のコピーを記録し</strong>、<strong>1 回、投げて 1 回、待つ</strong>のが効率的です。中継バッファは全部のコピーが、終わるまで保ちます。

## よくあるミス

??? failure "テクスチャが斜めにずれる、ノイズのように見える"
    行のピッチを `width * 4` のまま中継バッファに並べている（256 の倍数に、そろえていない）。`UpdateSubresources` を使う。

??? failure "コピー後にテクスチャが真っ黒（または化ける）"
    GPU がコピーを終える前に中継バッファを解放した。または、`COPY_DEST` → `PIXEL_SHADER_RESOURCE` のバリアを入れていない。

??? failure "遠くが、ちらつく（ミップが無い）"
    D3D12 に `GenerateMips` は無い。ミップを DDS で用意するか計算シェーダーで作る。

??? failure "色が、くすむ（暗い）"
    色の画像を `_UNORM`（リニア）で、読んでいる。`_SRGB` にする。

??? failure "ロードが遅い"
    テクスチャごとに `WaitForGpu` している。まとめて 1 回、待つ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DEFAULT のテクスチャ + UPLOAD の中継バッファ → `UpdateSubresources`
    - [x] 中継バッファの 1 行は 256 バイトの倍数。`GetRequiredIntermediateSize` で大きさを求める
    - [x] コピー後はバリア（`COPY_DEST` → `PIXEL_SHADER_RESOURCE`）。完了まで中継バッファを解放しない
    - [x] ミップは自動で、作られない。DDS か計算シェーダー
    - [x] 色は `_SRGB`、データはリニア
    - [x] 多数は 1 つのリストにまとめて 1 回待つ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Upload Buffer](upload-buffer.md)
- [Descriptor](descriptor.md)
- [Resource Barrier](resource-barrier.md)
- [Texture Streaming](../../rendering/texture-streaming.md)
- [Microsoft Learn: UpdateSubresources](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/uploading-resources)
