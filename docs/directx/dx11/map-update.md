---
title: Map, Unmap and UpdateSubresource
tags:
  - DirectX
---

# Map, Unmap and UpdateSubresource

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

GPU のメモリ（バッファ、テクスチャ）に、<strong>CPU から、データを、書く</strong>方法は、2 つあります。`Map`/`Unmap`（メモリを、直接、開いて、書く）と、`UpdateSubresource`（データを、渡して、コピーしてもらう）です。どちらを、使うかは、リソースを作るときの、<strong>`Usage`</strong>（用途）で、決まります。これを、間違えると、遅くなったり、`Map` が、失敗したり、GPU が、止まったり（ストール）します。

!!! tip "ポイント"
    - `Usage` は、<strong>誰が、読み書きするか</strong>の、宣言: `IMMUTABLE`（変えない）、`DEFAULT`（GPU が、使う）、`DYNAMIC`（CPU が、毎フレーム、書く）、`STAGING`（CPU が、読み書き、GPU から、持ってくる）。
    - 毎フレーム、書くなら、`DYNAMIC` + `Map(D3D11_MAP_WRITE_DISCARD)`。
    - たまにしか、書かない、または、テクスチャの一部なら、`DEFAULT` + `UpdateSubresource`。
    - GPU の結果を、CPU で、読むなら、`STAGING` に、`CopyResource` して、`Map(READ)`。
    - `WRITE_DISCARD` は、前の内容を、捨てる。一部だけを、更新したいなら、`WRITE_NO_OVERWRITE`。

## Usage（用途）の、4 種類

| `Usage` | GPU | CPU | 使いどころ |
| --- | --- | --- | --- |
| `IMMUTABLE` | 読む | なし（作成時の、初期データだけ） | 変わらない、メッシュ、テクスチャ。最速 |
| `DEFAULT` | 読み書き | なし（`UpdateSubresource` は、可） | レンダー ターゲット、UAV、たまに更新する物 |
| `DYNAMIC` | 読む | 書く（`Map`） | 毎フレーム変わる、定数バッファ、動的な頂点 |
| `STAGING` | なし（コピー元・先に、なれる） | 読み書き（`Map`） | GPU の結果の読み出し、アップロード用 |

`DYNAMIC` は、`BindFlags` に、制限があります（レンダー ターゲット、UAV、深度に、できない）。

## DYNAMIC + Map

毎フレーム、変わる、データ（定数バッファ、動的な頂点バッファ）の、標準の書き方です。

```cpp
D3D11_MAPPED_SUBRESOURCE mapped = {};
HRESULT hr = context->Map(buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);
if (SUCCEEDED(hr)) {
  std::memcpy(mapped.pData, data, size);                   // pData: GPU のメモリへの、書き込み用ポインター
  context->Unmap(buffer.Get(), 0);                         // 書き終わったら、必ず、Unmap
}
```

| 引数 | 内容 |
| --- | --- |
| `pResource` | `Map` する、リソース |
| `Subresource` | サブリソース番号（バッファは 0。テクスチャは、ミップと配列で、決まる） |
| `MapType` | 下の表 |
| `MapFlags` | `D3D11_MAP_FLAG_DO_NOT_WAIT`（GPU が、使用中なら、待たずに、失敗） |
| `pMappedResource` | 出力: `pData`（ポインター）、`RowPitch`、`DepthPitch` |

### MapType の、種類

| `MapType` | 内容 | 使える `Usage` |
| --- | --- | --- |
| `WRITE_DISCARD` | 古い内容を、捨てて、全部を、書き直す。GPU を、待たない | `DYNAMIC` |
| `WRITE_NO_OVERWRITE` | GPU が、まだ、使っていない、部分だけ、追記する。待たない | `DYNAMIC`（頂点・インデックス バッファのみ） |
| `WRITE` | 書く（古い内容を、保つ）。GPU の使用が、終わるまで、待つ | `STAGING` |
| `READ` | 読む | `STAGING` |
| `READ_WRITE` | 読み書き | `STAGING` |

### WRITE_DISCARD が、待たない理由

`WRITE_DISCARD` は、「古い内容は、もう、要らない」と、宣言して、ドライバーに、<strong>新しい領域を、割り当ててもらいます</strong>（バッファの、名前変更、renaming）。GPU は、古い領域で、前のフレームの、描画を、続け、CPU は、新しい領域に、書きます。待ちが、発生しません。

```cpp
// 1 フレームに、物ごとに、何度も、Map（DISCARD）して、描ける。毎回、別の領域が、渡る。
for (const Object& object : objects) {
  PerObject data = MakePerObject(object);
  UpdateConstants(data);                                    // Map(WRITE_DISCARD) → memcpy → Unmap
  context->DrawIndexed(object.index_count, 0, 0);
}
```

物ごとに、`Map` する、方法は、1 つの、バッファでも、動きます（ドライバーが、名前変更する）。ただし、数千回の、`Map` は、遅いので、大量の物は、まとめて、1 つの、大きなバッファに、書き、オフセットで、つなぎます（[Constant Buffer](constant-buffer.md)）。

### WRITE_NO_OVERWRITE：リングバッファ

大きな、動的な、頂点バッファ（UI、パーティクル）に、<strong>追記</strong>していくときは、`NO_OVERWRITE` が、使えます。

```cpp
// 1 つの大きな頂点バッファを、リングのように、使う。先頭から、追記し、末尾まで来たら、DISCARD で、先頭へ戻る。
D3D11_MAP map_type = D3D11_MAP_WRITE_NO_OVERWRITE;
if (write_offset_ + size > buffer_size_) {
  map_type = D3D11_MAP_WRITE_DISCARD;                       // 満杯: 全部を、捨てて、最初から
  write_offset_ = 0;
}
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(buffer.Get(), 0, map_type, 0, &mapped);
std::memcpy(static_cast<char*>(mapped.pData) + write_offset_, data, size);
context->Unmap(buffer.Get(), 0);
const UINT start_vertex = write_offset_ / sizeof(Vertex);
write_offset_ += size;
```

`NO_OVERWRITE` は、「GPU が、すでに、使っている部分には、書かない」という、約束です。約束を、守れば、待たずに、追記でき、約束を、破ると（使用中の、部分に、書くと）、描画が、壊れます。

## DEFAULT + UpdateSubresource

```cpp
// DEFAULT のバッファ・テクスチャの、一部、または、全部を、更新する。
context->UpdateSubresource(buffer.Get(), 0, nullptr, data, 0, 0);
```

| 引数 | 内容 |
| --- | --- |
| `pDstResource` | 更新先 |
| `DstSubresource` | サブリソース番号 |
| `pDstBox` | 更新する、範囲（`nullptr` で、全部） |
| `pSrcData` | 元のデータ（CPU のメモリ） |
| `SrcRowPitch` | テクスチャの、1 行の、バイト数 |
| `SrcDepthPitch` | 3D テクスチャの、1 層の、バイト数 |

```cpp
// テクスチャの、一部の範囲（x: 10〜50, y: 20〜60）だけを、更新する。
D3D11_BOX box = {10, 20, 0, 50, 60, 1};                    // left, top, front, right, bottom, back
context->UpdateSubresource(texture.Get(), 0, &box, pixels, (50 - 10) * 4, 0);
```

`UpdateSubresource` は、ドライバーが、データを、<strong>内部で、コピーして</strong>から、GPU へ、送るので、呼んだ後に、CPU 側の、メモリを、すぐ、解放しても、安全です。ただし、毎フレームの、定数バッファの、更新には、`Map` の方が、速いことが、多いです。

| | `Map`（`DYNAMIC`） | `UpdateSubresource`（`DEFAULT`） |
| --- | --- | --- |
| 向く | 毎フレーム、全部を、書く | たまの更新、テクスチャの一部 |
| コピー | 直接、GPU のメモリへ | ドライバーが、一度、コピー |
| 定数バッファ | 速い | やや、遅いことが、ある |

## STAGING：GPU の結果を、CPU で、読む

```cpp
// ① CPU が読める、STAGING テクスチャを、作る。GPU からは、直接、使えない。
D3D11_TEXTURE2D_DESC desc;
source_texture->GetDesc(&desc);
desc.Usage = D3D11_USAGE_STAGING;
desc.BindFlags = 0;                                        // どこにも、束ねない
desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
desc.MiscFlags = 0;
Microsoft::WRL::ComPtr<ID3D11Texture2D> staging;
device->CreateTexture2D(&desc, nullptr, &staging);

// ② GPU 上で、コピー。
context->CopyResource(staging.Get(), source_texture.Get());

// ③ CPU で、読む。GPU のコピーが、終わるまで、Map が待つ（ストール）。
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(staging.Get(), 0, D3D11_MAP_READ, 0, &mapped);
const uint8_t* row = static_cast<const uint8_t*>(mapped.pData);
for (UINT y = 0; y < desc.Height; ++y) {
  // 1 行ごとに RowPitch バイト進む（幅 × 画素の大きさ とは限らない）
  ProcessRow(row + y * mapped.RowPitch, desc.Width);
}
context->Unmap(staging.Get(), 0);
```

スクリーンショット、GPU の計算結果の、検証、ピッキング（ID バッファの読み出し）に、使います。<strong>`Map(READ)` は、GPU の、完了を、待つ</strong>ので、毎フレームの、読み出しは、フレームを、止めます。数フレーム前の、結果を、読む（STAGING を、リングで、複数用意）と、止まりません。

## RowPitch に、注意

テクスチャの、`Map` で、得られる、`RowPitch` は、<strong>幅 × 画素の大きさ、とは、限りません</strong>（アラインメントの、パディングが、入る）。行ごとに、`RowPitch` ずつ、進めて、読み書きします。

```cpp
// 書くとき: 1 行ずつ、コピーする。memcpy で、全体を、一気に、コピーしてはいけない。
uint8_t* dst = static_cast<uint8_t*>(mapped.pData);
for (UINT y = 0; y < height; ++y) {
  std::memcpy(dst + y * mapped.RowPitch, pixels + y * width * 4, width * 4);
}
```

## よくあるミス

??? failure "`Map` が、失敗する（`E_INVALIDARG`）"
    `Usage` と、`MapType` の、組み合わせが、違う。`DEFAULT` や `IMMUTABLE` は、`Map` できない。`DYNAMIC` に `READ` は、できない。

??? failure "テクスチャの、読み書きが、斜めに、ずれる"
    `RowPitch` を、無視して、`width * 4` ずつ、進めている。パディングが、あるので、`RowPitch` ずつ、進める。

??? failure "`Map(READ)` で、フレームが、ガクッと、止まる"
    GPU の、完了を、待っている。数フレーム遅れで、読む（複数の、STAGING を、リングで）か、非同期のクエリで、完了を、確認する。

??? failure "`WRITE_NO_OVERWRITE` で、描画が、壊れる"
    GPU が、使っている、領域に、書いている。リングバッファの、使い方を、間違えている。満杯になったら、`DISCARD` で、先頭に、戻る。

??? failure "`DYNAMIC` のレンダー ターゲットを、作ろうとして、失敗する"
    `DYNAMIC` は、レンダー ターゲット、UAV、深度に、できない。それらは、`DEFAULT`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `Usage`: `IMMUTABLE`（変えない）、`DEFAULT`（GPU）、`DYNAMIC`（毎フレーム CPU）、`STAGING`（CPU が読む）
    - [x] 毎フレーム書く → `DYNAMIC` + `Map(WRITE_DISCARD)`
    - [x] たまの更新 → `DEFAULT` + `UpdateSubresource`
    - [x] 追記 → `WRITE_NO_OVERWRITE`（リング）
    - [x] 読み出し → `STAGING` + `CopyResource` + `Map(READ)`（遅れて読む）
    - [x] テクスチャは、`RowPitch` ずつ、進める

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Constant Buffer](constant-buffer.md)
- [Vertex Buffer](vertex-buffer.md)
- [Texture2D](texture2d.md)
- [GPU Queries and Timing](query-timing.md)
- [Microsoft Learn: ID3D11DeviceContext::Map](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-map)
