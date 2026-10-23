---
title: Constant Buffer (D3D12)
tags:
  - DirectX
---

# Constant Buffer (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

行列、色、時間のようなシェーダーに渡したい値は、**定数バッファ**に入れて渡します。D3D12 では UPLOAD ヒープに置いたバッファへ CPU が直接書き込み、GPU がそこから読みます。

ただし、ひとつ注意があります。GPU は前のフレームの描画をまだ読んでいるかもしれません。そこへ CPU が新しい値を上書きすると、前のフレームの絵が壊れます。そのため、フレームごとに別の領域を使います。

!!! tip "ポイント"
    - 定数バッファは UPLOAD のヒープに大きなバッファを 1 つ作り、`Map` したまま使い続ける。
    - 1 つの CBV の大きさは、256 バイトの倍数。物ごとのデータの先頭も 256 バイトの境界にそろえる。
    - フレームごと物ごとに別の領域へ書く。GPU が読んでいる間は書き換えない。
    - シェーダーへの渡し方は 3 通り。ルート CBV（アドレスを直接）、ディスクリプタ テーブルの CBV、ルート定数。
    - HLSL の `cbuffer` は 16 バイト（`float4` 1 つ分）の境界をまたげない。行列は `row_major` にする。

!!! info "このページを読む前に"
    バッファを置く UPLOAD のヒープは [Heaps and Resources](heaps-resources.md)、フレームごとに領域を分ける考え方は [Frame Resources](frame-resources.md)、シェーダーへ渡す窓口は [Root Signature](root-signature.md) で説明しています。CBV のディスクリプタを作るメソッドは [ID3D12Device](api/id3d12device.md#createconstantbufferview) にあります。

## HLSL 側の宣言

まず、シェーダーでの受け取り方です。

```hlsl
// register(b0) は、ルート シグネチャのルート CBV（b0）に対応する。
cbuffer PerObject : register(b0) {
  row_major float4x4 world_view_projection;  // 行ベクトルの規約（v * M）
  float4 tint;
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  output.position = mul(float4(input.position, 1.0), world_view_projection);
  output.color = input.color * tint;
  return output;
}
```

`row_major` は行列の並べ方の指定です。このサイトは行ベクトル（`v * M`）なので、C++ の `XMFLOAT4X4` と同じ行が連続した並びにそろえます。付けないと HLSL は列が連続した並びとして読み行列が転置されます。

もう 1 つの決まりが**16 バイトの境界**です。`cbuffer` の中の変数は 16 バイト（`float4` 1 つ分）の区切りをまたげません。たとえば、`float3` の次に `float` を置くと同じ 16 バイトの中に収まります。ところが、`float3` の次に `float2` を置くと `float2` は 12 バイトの位置から 8 バイトぶんの場所が足りず、次の 16 バイトへ送られます。C++ の構造体とシェーダーの `cbuffer` で位置がずれたときは、この規則を疑います。行列・配列・構造体を含む詳しい規則は、[Constant Buffer Packing](../concepts/cbuffer-packing.md) にあります。

## C++ の構造体と 256 バイトの境界

```cpp
struct PerObject {
  DirectX::XMFLOAT4X4 world_view_projection;  // 64 バイト
  DirectX::XMFLOAT4 tint;                     // 16 バイト。合計 80 バイト
};

// D3D12 の CBV は 256 バイトの倍数。物ごとの領域を、256 バイトに切り上げる。
constexpr UINT AlignUp(UINT size, UINT alignment) { return (size + alignment - 1) & ~(alignment - 1); }
constexpr UINT kPerObjectStride = AlignUp(sizeof(PerObject), 256);  // 80 から 256 へ
```

D3D12 の CBV は大きさが 256 バイトの倍数（`D3D12_CONSTANT_BUFFER_DATA_PLACEMENT_ALIGNMENT`）で、先頭も 256 バイトの境界でなければなりません。構造体が 80 バイトしかなくても、256 バイトぶん確保します。

## 永続的に Map した定数バッファ

```cpp
constexpr UINT kMaxObjects = 1024;
constexpr UINT kBufferSize = kPerObjectStride * kMaxObjects * kFrameCount;  // 全フレーム、全物ぶん

// UPLOAD のヒープに 1 つ作って、そのまま Map したままにする。
D3D12_HEAP_PROPERTIES heap = MakeHeapProperties(D3D12_HEAP_TYPE_UPLOAD);
D3D12_RESOURCE_DESC desc = MakeBufferDesc(kBufferSize);
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_GENERIC_READ, nullptr,
                                IID_PPV_ARGS(&constant_buffer));

uint8_t* mapped = nullptr;
D3D12_RANGE no_read = {0, 0};
constant_buffer->Map(0, &no_read, reinterpret_cast<void**>(&mapped));  // Unmap しない（アプリの終わりまで）
```

UPLOAD のバッファは `Map` したまま使い続けて構いません。毎フレーム `Map` と `Unmap` を繰り返す必要はなく、`mapped` のポインターに書けば GPU がそのまま読みます。

## フレームごと物ごとに別の領域へ書く

```cpp
// このフレームの領域の先頭（同時に進めるフレームごとに別）。
const UINT frame_base = frame_index * kPerObjectStride * kMaxObjects;

for (UINT i = 0; i < object_count; ++i) {
  PerObject data = MakePerObject(objects[i]);
  std::memcpy(mapped + frame_base + i * kPerObjectStride, &data, sizeof(data));  // 物 i の領域に書く
}
```

GPU が前のフレームを読んでいる間に同じ領域を上書きしないようフレームごとに別の領域へ書きます（[Frame Resources](frame-resources.md)）。さらに、物ごとにも別の領域にします。1 つの領域を描画のたびに書き換えると、GPU は記録された命令をあとでまとめて実行するので、すべての描画が最後に書いた値を読んでしまうからです。

## 渡し方 1：ルート CBV

物ごとの定数バッファはルート CBV で GPU アドレスを直接渡すのが、一番簡単です。ディスクリプタ ヒープに CBV を作る必要がありません。ルート シグネチャでパラメーターの種類を `D3D12_ROOT_PARAMETER_TYPE_CBV` にします（[Root Signature](root-signature.md)）。

```cpp
// 描画。物ごとのアドレスを、直接渡す。
const D3D12_GPU_VIRTUAL_ADDRESS base = constant_buffer->GetGPUVirtualAddress() + frame_base;
for (UINT i = 0; i < object_count; ++i) {
  command_list->SetGraphicsRootConstantBufferView(0, base + i * kPerObjectStride);  // 物 i の定数
  command_list->DrawIndexedInstanced(objects[i].index_count, 1, 0, 0, 0);
}
```

ルート CBV はルート シグネチャの容量を 2 DWORD 使います。

## 渡し方 2：ディスクリプタ テーブルの CBV

CBV をディスクリプタ ヒープに並べて、テーブルで渡す方法もあります。1 回の描画でフレーム共通、マテリアル、物ごとのように複数の CBV を使うときまとめて渡せます。

```cpp
// CBV をヒープに作る（256 バイトの倍数）。
D3D12_CONSTANT_BUFFER_VIEW_DESC cbv = {};
cbv.BufferLocation = constant_buffer->GetGPUVirtualAddress() + offset;
cbv.SizeInBytes = kPerObjectStride;  // 256 の倍数
device->CreateConstantBufferView(&cbv, heap_cpu_handle);
```

ヒープが必要で作る手間は増えますが、ルート シグネチャの容量は 1 DWORD で済みます。

## 渡し方 3：ルート定数

物の ID や数個の `float` のような少量の値は、ルート定数が一番速いです。バッファもディスクリプタも要りません（[Root Signature](root-signature.md)）。

```cpp
command_list->SetGraphicsRoot32BitConstants(1, 4, values, 0);
```

## 更新の頻度で分ける

定数バッファは更新の頻度で分けておくと無駄な書き込みが減ります。カメラや時間、ライトのようなフレーム共通のものは、フレームに 1 回だけ書いて、ルート CBV（`b0`）で渡します。マテリアルごとのものはディスクリプタ テーブルの CBV か別のルート CBV（`b1`）で渡します。物ごとのワールド行列は描画ごとに変わるので、ルート CBV（`b2`）で物ごとに別の領域を指します。ごく少量で頻繁に変わる値はルート定数（`b3`）が向いています。

## 大きなバッファを 1 つ持つ

物ごとに別のバッファを作ると、リソースの数が増えて管理が大変になります。1 つの大きな UPLOAD のバッファに全物の定数を並べて、オフセットで指すのが定石です。物ごとに別のバッファを作ると、「物の数 × フレームの数」のリソースが必要です。大きなバッファ 1 つならフレームの数だけ（または 1 つだけ）で足ります。

1 フレームの領域が足りなくなったときは、使い切ったら先頭へ戻るリング バッファにするかバッファを大きくします。1 フレームの物の数に上限を決めて、`kMaxObjects` を十分に取るのが一番簡単です。

## よくあるミス

??? failure "画面がちらつく、前のフレームの値が混ざる"
    GPU が読んでいる同じ領域を CPU が書き換えています。同時に進めるフレームごとに別の領域へ書きます。

??? failure "全部の物が同じ位置に描かれる"
    物ごとに別の領域へ書かず同じ領域を書き換えながら描いています。GPU は記録された命令をあとで実行するので、最後の値がすべての描画に使われます。物ごとに別のオフセットにします。

??? failure "`CreateConstantBufferView` でデバッグ レイヤーがエラーを出す"
    `SizeInBytes` や `BufferLocation` が 256 の倍数と 256 の境界にそろっていません。

??? failure "C++ で書いた値とシェーダーの値がずれる"
    `cbuffer` の 16 バイトの境界の規則を無視しています。パディングを入れます。`row_major` の付け忘れもよくある原因です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 定数バッファは UPLOAD のヒープに置いた、1 つの大きなバッファ。永続的に `Map` する
    - [x] CBV の大きさと開始位置は、256 バイトの倍数
    - [x] フレームごと物ごとに別の領域へ書く
    - [x] 物ごとのデータは、ルート CBV（アドレスを直接）が簡単。少量はルート定数
    - [x] `cbuffer` は 16 バイトの境界をまたげない。行列は `row_major`

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12Device](api/id3d12device.md)
- [Root Signature](root-signature.md)
- [Frame Resources](frame-resources.md)
- [Upload Buffer](upload-buffer.md)
- [Constant Buffer Packing](../concepts/cbuffer-packing.md)
- [Microsoft Learn: 定数バッファ ビュー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/using-constant-buffers-in-direct3d-12)
