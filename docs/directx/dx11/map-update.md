---
title: Map, Unmap and UpdateSubresource
tags:
  - DirectX
---

# Map, Unmap and UpdateSubresource

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

GPU のメモリ（バッファ、テクスチャ）に <strong>CPU から、データを書く</strong>方法は 2 つあります。`Map`/`Unmap`（メモリを直接、開いて書く）と `UpdateSubresource`（データを渡して、コピーしてもらう）です。どちらを使うかはリソースを作るときの <strong>`Usage`</strong>（用途）で決まります。これを間違えると遅くなったり `Map` が、失敗したり GPU が止まったり（ストール）します。

!!! tip "ポイント"
    - `Usage` は <strong>誰が読み書きするか</strong>の宣言: `IMMUTABLE`（変えない）、`DEFAULT`（GPU が使う）、`DYNAMIC`（CPU が毎フレーム、書く）、`STAGING`（CPU が読み書き GPU から、持ってくる）。
    - 毎フレーム、書くなら `DYNAMIC` + `Map(D3D11_MAP_WRITE_DISCARD)`。
    - たまにしか書かないまたは、テクスチャの一部なら `DEFAULT` + `UpdateSubresource`。
    - GPU の結果を CPU で読むなら `STAGING` に `CopyResource` して `Map(READ)`。
    - `WRITE_DISCARD` は前の内容を捨てる。一部だけを更新したいなら `WRITE_NO_OVERWRITE`。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## Usage（用途）の 4 種類

| `Usage` | GPU | CPU | 使いどころ |
| --- | --- | --- | --- |
| `IMMUTABLE` | 読む | なし（作成時の初期データだけ） | 変わらない、メッシュ、テクスチャ。最速 |
| `DEFAULT` | 読み書き | なし（`UpdateSubresource` は、可） | レンダー ターゲット、UAV、たまに更新する物 |
| `DYNAMIC` | 読む | 書く（`Map`） | 毎フレーム変わる定数バッファ、動的な頂点 |
| `STAGING` | なし（コピー元・先になれる） | 読み書き（`Map`） | GPU の結果の読み出し、アップロード用 |

`DYNAMIC` は `BindFlags` に制限があります（レンダー ターゲット、UAV、深度にできない）。

## DYNAMIC + Map

毎フレーム、変わるデータ（定数バッファ、動的な頂点バッファ）の標準の書き方です。

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
| `pResource` | `Map` するリソース |
| `Subresource` | サブリソース番号（バッファは 0。テクスチャはミップと配列で決まる） |
| `MapType` | 下の表 |
| `MapFlags` | `D3D11_MAP_FLAG_DO_NOT_WAIT`（GPU が使用中なら待たずに失敗） |
| `pMappedResource` | 出力: `pData`（ポインター）、`RowPitch`、`DepthPitch` |

### MapType の種類

| `MapType` | 内容 | 使える `Usage` |
| --- | --- | --- |
| `WRITE_DISCARD` | 古い内容を捨てて全部を書き直す。GPU を待たない | `DYNAMIC` |
| `WRITE_NO_OVERWRITE` | GPU がまだ使っていない、部分だけ追記する。待たない | `DYNAMIC`（頂点・インデックス バッファのみ） |
| `WRITE` | 書く（古い内容を保つ）。GPU の使用が終わるまで待つ | `STAGING` |
| `READ` | 読む | `STAGING` |
| `READ_WRITE` | 読み書き | `STAGING` |

### WRITE_DISCARD が、待たない理由

`WRITE_DISCARD` は「古い内容はもう要らない」と宣言してドライバーに <strong>新しい領域を割り当ててもらいます</strong>（バッファの、名前変更、renaming）。GPU は古い領域で前のフレームの描画を続け CPU は新しい領域に書きます。待ちが発生しません。

```cpp
// 1 フレームに、物ごとに、何度も、Map（DISCARD）して、描ける。毎回、別の領域が、渡る。
for (const Object& object : objects) {
  PerObject data = MakePerObject(object);
  UpdateConstants(data);                                    // Map(WRITE_DISCARD) → memcpy → Unmap
  context->DrawIndexed(object.index_count, 0, 0);
}
```

物ごとに `Map` する方法は 1 つのバッファでも動きます（ドライバーが、名前変更する）。ただし、数千回の `Map` は遅いので大量の物はまとめて 1 つの大きなバッファに書き、オフセットでつなぎます（[Constant Buffer](constant-buffer.md)）。

### WRITE_NO_OVERWRITE：リングバッファ

大きな動的な頂点バッファ（UI、パーティクル）に <strong>追記</strong>していくときは `NO_OVERWRITE` が、使えます。

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

`NO_OVERWRITE` は「GPU がすでに使っている部分には、書かない」という約束です。約束を守れば待たずに追記でき約束を破ると（使用中の部分に書くと）、描画が壊れます。

## DEFAULT + UpdateSubresource

```cpp
// DEFAULT のバッファ・テクスチャの、一部、または、全部を、更新する。
context->UpdateSubresource(buffer.Get(), 0, nullptr, data, 0, 0);
```

| 引数 | 内容 |
| --- | --- |
| `pDstResource` | 更新先 |
| `DstSubresource` | サブリソース番号 |
| `pDstBox` | 更新する範囲（`nullptr` で、全部） |
| `pSrcData` | 元のデータ（CPU のメモリ） |
| `SrcRowPitch` | テクスチャの 1 行のバイト数 |
| `SrcDepthPitch` | 3D テクスチャの 1 層のバイト数 |

```cpp
// テクスチャの、一部の範囲（x: 10〜50, y: 20〜60）だけを、更新する。
D3D11_BOX box = {10, 20, 0, 50, 60, 1};                    // left, top, front, right, bottom, back
context->UpdateSubresource(texture.Get(), 0, &box, pixels, (50 - 10) * 4, 0);
```

`UpdateSubresource` はドライバーがデータを <strong>内部で、コピーして</strong>から GPU へ送るので、呼んだ後に CPU 側のメモリをすぐ解放しても安全です。ただし、毎フレームの定数バッファの更新には `Map` の方が速いことが多いです。

| | `Map`（`DYNAMIC`） | `UpdateSubresource`（`DEFAULT`） |
| --- | --- | --- |
| 向く | 毎フレーム、全部を書く | たまの更新、テクスチャの一部 |
| コピー | 直接、GPU のメモリへ | ドライバーが一度、コピー |
| 定数バッファ | 速い | やや遅いことがある |

## STAGING：GPU の結果を CPU で読む

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

スクリーンショット、GPU の計算結果の検証、ピッキング（ID バッファの読み出し）に使います。<strong>`Map(READ)` は GPU の完了を待つ</strong>ので、毎フレームの読み出しはフレームを止めます。数フレーム前の結果を読む（STAGING をリングで複数用意）と止まりません。

## RowPitch に注意

テクスチャの `Map` で得られる `RowPitch` は、<strong>幅 × 画素の大きさとは限りません</strong>（アラインメントのパディングが入る）。行ごとに `RowPitch` ずつ進めて読み書きします。

```cpp
// 書くとき: 1 行ずつ、コピーする。memcpy で、全体を、一気に、コピーしてはいけない。
uint8_t* dst = static_cast<uint8_t*>(mapped.pData);
for (UINT y = 0; y < height; ++y) {
  std::memcpy(dst + y * mapped.RowPitch, pixels + y * width * 4, width * 4);
}
```

## よくあるミス

??? failure "`Map` が、失敗する（`E_INVALIDARG`）"
    `Usage` と `MapType` の組み合わせが違う。`DEFAULT` や `IMMUTABLE` は `Map` できない。`DYNAMIC` に `READ` はできない。

??? failure "テクスチャの読み書きが斜めにずれる"
    `RowPitch` を無視して `width * 4` ずつ進めている。パディングがあるので `RowPitch` ずつ進める。

??? failure "`Map(READ)` で、フレームがガクッと止まる"
    GPU の完了を待っている。数フレーム遅れで読む（複数の STAGING をリングで）か非同期のクエリで完了を確認する。

??? failure "`WRITE_NO_OVERWRITE` で描画が、壊れる"
    GPU が使っている領域に書いている。リングバッファの使い方を間違えている。満杯になったら `DISCARD` で先頭に戻る。

??? failure "`DYNAMIC` のレンダー ターゲットを作ろうとして失敗する"
    `DYNAMIC` はレンダー ターゲット、UAV、深度にできない。それらは `DEFAULT`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `Usage`: `IMMUTABLE`（変えない）、`DEFAULT`（GPU）、`DYNAMIC`（毎フレーム CPU）、`STAGING`（CPU が読む）
    - [x] 毎フレーム書く → `DYNAMIC` + `Map(WRITE_DISCARD)`
    - [x] たまの更新 → `DEFAULT` + `UpdateSubresource`
    - [x] 追記 → `WRITE_NO_OVERWRITE`（リング）
    - [x] 読み出し → `STAGING` + `CopyResource` + `Map(READ)`（遅れて読む）
    - [x] テクスチャは `RowPitch` ずつ進める

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Constant Buffer](constant-buffer.md)
- [Vertex Buffer](vertex-buffer.md)
- [Texture2D](texture2d.md)
- [GPU Queries and Timing](query-timing.md)
- [Microsoft Learn: ID3D11DeviceContext::Map](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-map)
