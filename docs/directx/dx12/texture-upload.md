---
title: Texture Upload
tags:
  - DirectX
---

# Texture Upload

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

テクスチャを GPU に送る流れは頂点バッファと同じです。UPLOAD のヒープに置いた中継バッファへ画素を書き GPU のコピー命令で、DEFAULT のヒープのテクスチャへ送ります。

ただし、テクスチャには頂点バッファにない決まりがあります。中継バッファの中では画像の 1 行ごとの幅（ピッチ）を決まった倍数にそろえなければなりません。画像のデータをそのまま並べると、1 行ごとにずれて斜めにゆがんだ絵になります。このページではその並べ方を `GetCopyableFootprints` で計算して、自分でコピーします。D3D12 にはミップマップを自動で作る関数もないので、その用意の仕方も説明します。

!!! tip "ポイント"
    - 流れは DEFAULT のテクスチャを作り UPLOAD の中継バッファを作り、行ごとにコピーして `CopyTextureRegion` を記録し、バリアで読める状態にして SRV を作る。
    - 中継バッファの 1 行の幅は、256 バイトの倍数（`D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`）。
    - 中継バッファの大きさと各行の位置は、`GetCopyableFootprints` が教えてくれる。
    - GPU がコピーを終えるまで、中継バッファは解放できない（フェンスで待つ）。
    - ミップマップは自動では作られない。ビルド時に DDS へ入れておくか計算シェーダーで作る。

!!! info "このページを読む前に"
    アップロードの基本の流れは [Upload Buffer](upload-buffer.md)、テクスチャを作る `MakeTexture2DDesc` は [Helper Functions](util.md)、コピーする命令は [ID3D12GraphicsCommandList::CopyTextureRegion](api/id3d12graphicscommandlist.md#copytextureregion)、配置を計算するメソッドは [ID3D12Device::GetCopyableFootprints](api/id3d12device.md#getcopyablefootprints) にあります。

## テクスチャと中継バッファを作る

まず、DEFAULT のテクスチャを作ります。初期状態はこれからコピーを受けるので、`COPY_DEST` です。

```cpp
// 1. DEFAULT のテクスチャを作る（初期状態は COPY_DEST）。
D3D12_RESOURCE_DESC texture_desc = MakeTexture2DDesc(DXGI_FORMAT_R8G8B8A8_UNORM_SRGB, width, height);
D3D12_HEAP_PROPERTIES default_heap = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
device->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &texture_desc,
                                D3D12_RESOURCE_STATE_COPY_DEST, nullptr, IID_PPV_ARGS(&texture));
```

次に、中継バッファの大きさを求めます。ここで `GetCopyableFootprints` を使います。画像の大きさ（`width × height × 4`）より大きくなることがあるのは、行の幅が 256 の倍数にそろえられるからです。

```cpp
// 2. 中継バッファの配置と大きさを計算する。
D3D12_PLACED_SUBRESOURCE_FOOTPRINT footprint = {};
UINT num_rows = 0;
UINT64 row_size_in_bytes = 0;
UINT64 total_bytes = 0;
device->GetCopyableFootprints(&texture_desc, 0, 1, 0, &footprint, &num_rows, &row_size_in_bytes, &total_bytes);

D3D12_HEAP_PROPERTIES upload_heap = MakeHeapProperties(D3D12_HEAP_TYPE_UPLOAD);
D3D12_RESOURCE_DESC upload_desc = MakeBufferDesc(total_bytes);
device->CreateCommittedResource(&upload_heap, D3D12_HEAP_FLAG_NONE, &upload_desc,
                                D3D12_RESOURCE_STATE_GENERIC_READ, nullptr, IID_PPV_ARGS(&upload_buffer));
```

引数の意味は次のとおりです。第 2、第 3 引数は計算するサブリソースの範囲（最初の番号と個数）です。第 4 引数は中継バッファの中の開始位置です。出力は各サブリソースの配置（`footprint`）、行数（`num_rows`）、画像側の 1 行のバイト数（`row_size_in_bytes`）、全体の大きさ（`total_bytes`）の 4 つです。

## 行ごとにコピーしてコピーの命令を記録する

中継バッファの 1 行の幅は `footprint.Footprint.RowPitch` です。この幅で 1 行ずつ並べるために画像の行を 1 つずつコピーします。

```cpp
// 3. 画素を中継バッファへ 1 行ずつコピーする。
uint8_t* mapped = nullptr;
D3D12_RANGE no_read = {0, 0};
upload_buffer->Map(0, &no_read, reinterpret_cast<void**>(&mapped));
const UINT src_row_pitch = width * 4;  // 画像側の 1 行のバイト数（256 の倍数でなくてよい）
for (UINT row = 0; row < num_rows; ++row) {
  std::memcpy(mapped + footprint.Offset + row * footprint.Footprint.RowPitch,  // 中継バッファの行
              pixels + row * src_row_pitch,                                      // 画像の行
              row_size_in_bytes);
}
upload_buffer->Unmap(0, nullptr);
```

画像側の行のバイト数（`src_row_pitch`）と中継バッファの行の幅（`RowPitch`）は、別の値です。`RowPitch` のほうが大きいので行の末尾に使わない余白が入ります。`row_size_in_bytes` ぶんだけをコピーします。

次に、コピーの命令を記録します。

```cpp
// 4. 中継バッファからテクスチャへコピーを記録する。
D3D12_TEXTURE_COPY_LOCATION dst = {};
dst.pResource = texture.Get();
dst.Type = D3D12_TEXTURE_COPY_TYPE_SUBRESOURCE_INDEX;
dst.SubresourceIndex = 0;

D3D12_TEXTURE_COPY_LOCATION src = {};
src.pResource = upload_buffer.Get();
src.Type = D3D12_TEXTURE_COPY_TYPE_PLACED_FOOTPRINT;
src.PlacedFootprint = footprint;

command_list->CopyTextureRegion(&dst, 0, 0, 0, &src, nullptr);

// 5. コピーのあと、シェーダーから読めるように状態を切り替える。
D3D12_RESOURCE_BARRIER barrier = MakeTransitionBarrier(
    texture.Get(), D3D12_RESOURCE_STATE_COPY_DEST, D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);
command_list->ResourceBarrier(1, &barrier);
```

`CopyTextureRegion` はコピー先とコピー元を `D3D12_TEXTURE_COPY_LOCATION` で指します。コピー先は「テクスチャのサブリソース番号」（`SUBRESOURCE_INDEX`）、コピー元は「バッファの中の配置」（`PLACED_FOOTPRINT`）です。コピーの実行そのものは `ExecuteCommandLists` のあとに GPU が行うので、実行後にフェンスで待ってから、中継バッファを解放します。

```cpp
command_list->Close();
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
WaitForGpu();  // コピーの完了を待つ
upload_buffer.Reset();  // そのあとで、中継バッファを解放する
```

## SRV を作る

最後に、シェーダーから読むための SRV をヒープに作ります。

```cpp
D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(texture.Get(), &srv, srv_cpu_handle);
```

色の画像は `_SRGB`、法線マップのようなデータはリニアの `_UNORM` にします（[Descriptor](descriptor.md)）。

## ミップマップ

D3D12 にはミップを自動で作る関数がありません。ミップは次のどれかで用意します。

一番一般的なのはビルド時に DDS ファイルへ入れておく方法です。画像ツール（`texconv` など）でミップを作って保存し、実行時は全ミップをアップロードします。次に、計算シェーダーで作る方法があります。ミップ 0 から順に半分へ縮小する計算シェーダーをミップごとに実行します。起動時に CPU で縮小して、全ミップをアップロードする方法もあります。

ミップがあるテクスチャではミップの数だけサブリソースがあります。`GetCopyableFootprints` にサブリソースの数を渡して、まとめて計算します。

```cpp
// 全ミップをアップロードする（サブリソースはミップごと）。
std::vector<D3D12_PLACED_SUBRESOURCE_FOOTPRINT> footprints(mip_count);
std::vector<UINT> rows(mip_count);
std::vector<UINT64> row_sizes(mip_count);
UINT64 total_bytes = 0;
device->GetCopyableFootprints(&texture_desc, 0, mip_count, 0, footprints.data(), rows.data(), row_sizes.data(),
                              &total_bytes);
// total_bytes で中継バッファを作り、ミップごとに行をコピーして、CopyTextureRegion を mip_count 回記録する。
for (UINT m = 0; m < mip_count; ++m) {
  const UINT src_row_pitch = (width >> m) * 4;
  for (UINT row = 0; row < rows[m]; ++row) {
    std::memcpy(mapped + footprints[m].Offset + row * footprints[m].Footprint.RowPitch,
                mip_pixels[m] + row * src_row_pitch, row_sizes[m]);
  }
  // dst.SubresourceIndex = m、src.PlacedFootprint = footprints[m] で CopyTextureRegion
}
```

テクスチャを作るときの `MipLevels` にミップの数を渡します。ミップごとの幅と高さは `width >> m` と `height >> m` です（最低 1）。

## 画像ファイルを読み込む

D3D12 自身は PNG や JPG を読み込めません。ライブラリを使います。

DirectXTK12 の `LoadWICTextureFromFile` と `LoadDDSTextureFromFile` は、画像をデコードして `D3D12_SUBRESOURCE_DATA` を返します。`ResourceUploadBatch` がアップロードをまとめて行います。DirectXTex は読み込みミップの生成、圧縮までできます。`stb_image` は軽いデコーダーで RGBA のピクセル列を返します。

```cpp
// DirectXTK12。アップロードをまとめて、非同期に行う。
DirectX::ResourceUploadBatch upload(device.Get());
upload.Begin();
DirectX::CreateWICTextureFromFile(device.Get(), upload, L"albedo.png", &texture, true /* ミップを自動生成 */);
auto finished = upload.End(command_queue.Get());  // std::future。完了を待てる
finished.wait();
```

製品ではビルド時に圧縮形式（BC7）の DDS へ変換しておき実行時はそのままアップロードします（[Texture Streaming](../../rendering/texture-streaming.md)）。

## たくさんのテクスチャをまとめて送る

ロード時に数百枚のテクスチャを送るとき 1 枚ずつ `WaitForGpu` すると、とても遅くなります。1 つのコマンド リストに全部のコピーを記録して、1 回だけ渡し 1 回だけ待つのが効率的です。中継バッファはすべてのコピーが終わるまで、持ち続けます。

## よくあるミス

??? failure "テクスチャが斜めにずれる、ノイズのように見える"
    中継バッファへ行のピッチを `width * 4` のまま並べています。`footprint.Footprint.RowPitch` の幅で 1 行ずつコピーします。

??? failure "コピーしたあとテクスチャが真っ黒になる（または化ける）"
    GPU がコピーを終える前に中継バッファを解放しました。または、`COPY_DEST` から `PIXEL_SHADER_RESOURCE` へのバリアを入れていません。

??? failure "遠くがちらつく（ミップがない）"
    D3D12 には `GenerateMips` がありません。ミップを DDS で用意するか計算シェーダーで作ります。

??? failure "色がくすむ（暗い）"
    色の画像を `_UNORM`（リニア）で読んでいます。`_SRGB` にします。

??? failure "ロードが遅い"
    テクスチャごとに `WaitForGpu` しています。まとめて 1 回だけ待ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DEFAULT のテクスチャと UPLOAD の中継バッファを使い、`CopyTextureRegion` で送る
    - [x] 中継バッファの 1 行は 256 バイトの倍数。配置は `GetCopyableFootprints` で計算する
    - [x] コピーのあとはバリア（`COPY_DEST` から `PIXEL_SHADER_RESOURCE`）。完了まで中継バッファを解放しない
    - [x] ミップは自動では作られない。DDS か計算シェーダーで用意する
    - [x] 色は `_SRGB`、データはリニア
    - [x] たくさんのときは、1 つのリストにまとめて 1 回だけ待つ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Upload Buffer](upload-buffer.md)
- [Helper Functions](util.md)
- [ID3D12Device](api/id3d12device.md)
- [Descriptor](descriptor.md)
- [Resource Barrier](resource-barrier.md)
- [Texture Streaming](../../rendering/texture-streaming.md)
- [Microsoft Learn: アップロードとリードバック](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/uploading-resources)
