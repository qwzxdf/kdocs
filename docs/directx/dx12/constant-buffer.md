---
title: Constant Buffer (D3D12)
tags:
  - DirectX
---

# Constant Buffer (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>定数バッファ</strong>はシェーダーに、パラメータ（行列、色、時間など）を渡すバッファです。D3D12 では <strong>UPLOAD ヒープの、バッファ</strong>に CPU が直接、書き GPU がそこから読みます。ただし、GPU が前のフレームを読んでいる間に、同じ領域を書き換えないよう <strong>フレームごとに、別の領域</strong>を使う必要があります。

!!! tip "ポイント"
    - 定数バッファは UPLOAD ヒープに、<strong>1 つの大きなバッファ</strong>を作り、<strong>永続的に `Map`</strong> したまま使う。
    - 1 つの CBV の、大きさは <strong>256 バイトの倍数</strong>。各物のデータの先頭も 256 バイトに、そろえる。
    - フレームごと物ごとに、別の領域に書く（GPU が読んでいる間に、書き換えない）。
    - シェーダーへの渡し方は、3 通り: <strong>ルート CBV</strong>（アドレスを直接）、<strong>ディスクリプタ テーブル内の CBV</strong>、<strong>ルート定数</strong>。
    - HLSL の `cbuffer` は、16 バイト（`float4`）の境界をまたげない。行列は `row_major`。

## HLSL 側

```hlsl
// register(b0): ルート シグネチャの、ルート CBV（b0）と、対応する。
cbuffer PerObject : register(b0) {
  row_major float4x4 world_view_projection;     // 行ベクトルの規約（v * M）
  float4 tint;
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  output.position = mul(float4(input.position, 1.0), world_view_projection);
  output.color = input.color * tint;
  return output;
}
```

行列の扱い（`row_major`）と 16 バイト境界の規則は、[Constant Buffer](../dx11/constant-buffer.md) と、同じです。

## C++ の構造体と 256 バイト境界

```cpp
struct PerObject {
  DirectX::XMFLOAT4X4 world_view_projection;     // 64 バイト
  DirectX::XMFLOAT4 tint;                        // 16 バイト → 合計 80 バイト
};

// D3D12 の CBV は、256 バイトの倍数。物ごとの領域を、256 バイトに、切り上げる。
constexpr UINT AlignUp(UINT size, UINT alignment) { return (size + alignment - 1) & ~(alignment - 1); }
constexpr UINT kPerObjectStride = AlignUp(sizeof(PerObject), 256);      // 80 → 256
```

D3D12 の CBV は <strong>256 バイトの、倍数</strong>の大きさ（`D3D12_CONSTANT_BUFFER_DATA_PLACEMENT_ALIGNMENT`）で <strong>256 バイト境界から、始まる</strong>必要があります。80 バイトの構造体でも 256 バイトぶんを、確保します。

## 永続 Map の定数バッファ

```cpp
constexpr UINT kMaxObjects = 1024;
constexpr UINT kBufferSize = kPerObjectStride * kMaxObjects * kFrameCount;   // 全フレーム・全物ぶん

// UPLOAD ヒープに、1 つ作って、そのまま、Map したままにする。
auto heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_UPLOAD);
auto desc = CD3DX12_RESOURCE_DESC::Buffer(kBufferSize);
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_GENERIC_READ, nullptr,
                                IID_PPV_ARGS(&constant_buffer));

uint8_t* mapped = nullptr;
CD3DX12_RANGE no_read(0, 0);
constant_buffer->Map(0, &no_read, reinterpret_cast<void**>(&mapped));   // Unmap しない（アプリの終わりまで）
```

アップロード ヒープのバッファは、<strong>`Map` したまま</strong>、使い続けてよいです。毎フレーム、`Map`/`Unmap` する必要はありません。

## 書き込み：フレームごと・物ごとに、別の領域

```cpp
// このフレームの、領域の先頭（フレーム イン フライトごとに、別）。
const UINT frame_base = frame_index * kPerObjectStride * kMaxObjects;

for (UINT i = 0; i < object_count; ++i) {
  PerObject data = MakePerObject(objects[i]);
  std::memcpy(mapped + frame_base + i * kPerObjectStride, &data, sizeof(data));   // 物 i の領域に、書く
}
```

GPU が前のフレームをまだ、読んでいる間にそのデータを上書きしないよう、<strong>フレーム イン フライトごとに、別の領域</strong>に書きます（[Frame Resources](frame-resources.md)）。物ごとにも別の領域です（描画の間に、同じ領域を書き換えると全描画が、最後の値を読みます）。

## 渡し方 1：ルート CBV（推奨）

物ごとの定数バッファは <strong>ルート CBV</strong>で、GPU アドレスを直接、渡すのが最も簡単です。ディスクリプタ ヒープに CBV を、作る必要がありません。

```cpp
// ルート シグネチャ: パラメータ 0 を、ルート CBV（b0）にする。
CD3DX12_ROOT_PARAMETER parameters[1];
parameters[0].InitAsConstantBufferView(0);                      // b0
```

```cpp
// 描画: 物ごとの、アドレスを、直接、渡す。
const D3D12_GPU_VIRTUAL_ADDRESS base = constant_buffer->GetGPUVirtualAddress() + frame_base;
for (UINT i = 0; i < object_count; ++i) {
  command_list->SetGraphicsRootConstantBufferView(0, base + i * kPerObjectStride);   // 物 i の定数
  command_list->DrawIndexedInstanced(objects[i].index_count, 1, 0, 0, 0);
}
```

ルート CBV はルート シグネチャの容量を、2 DWORD 使います（[Root Signature](root-signature.md)）。

## 渡し方 2：ディスクリプタ テーブルの CBV

CBV をディスクリプタ ヒープに並べて、テーブルで渡す方法です。1 つの描画で CBV を複数（フレーム共通、マテリアル、物）、使うときにまとめて渡せます。

```cpp
// CBV を、ヒープに、作る（256 バイトの倍数）。
D3D12_CONSTANT_BUFFER_VIEW_DESC cbv = {};
cbv.BufferLocation = constant_buffer->GetGPUVirtualAddress() + offset;
cbv.SizeInBytes = kPerObjectStride;                              // 256 の倍数
device->CreateConstantBufferView(&cbv, heap_cpu_handle);
```

ヒープが必要で作成の手間は増えますが、ルート シグネチャの容量は 1 DWORD で、済みます。

## 渡し方 3：ルート定数

少量の値（物の ID、数個の `float`）はルート定数が最速です（[Root Signature](root-signature.md)）。

```cpp
command_list->SetGraphicsRoot32BitConstants(1, 4, values, 0);   // バッファも、ディスクリプタも、不要
```

## 更新頻度で分ける

| バッファ | 更新の頻度 | 渡し方 |
| --- | --- | --- |
| フレーム共通（カメラ、時間、ライト） | フレームに 1 回 | ルート CBV（`b0`）。フレーム ごとに 1 つ |
| マテリアル | マテリアルごと | ディスクリプタ テーブルの CBV、またはルート CBV（`b1`） |
| 物ごと（ワールド行列） | 描画ごと | ルート CBV（`b2`）。物ごとに別の領域 |
| ごく少量の頻繁な値 | 描画ごと | ルート定数（`b3`） |

## 大きなバッファ 1 つ vs 多数の小さなバッファ

物ごとに別のバッファを作ると、リソースが増え管理が大変です。<strong>1 つの大きな UPLOAD バッファに全物の定数を並べ</strong>、オフセットで指すのが定石です。

| 方式 | リソース数 | 管理 |
| --- | --- | --- |
| 物ごとに別のバッファ | 物の数 × フレーム数 | 重い |
| 1 つの大きなバッファ + オフセット | フレーム数だけ（または 1 つ） | 軽い。この方式が標準 |

## 動的に足りなくなったとき

定数の領域が足りなくなったら、<strong>リング バッファ</strong>（1 フレームの領域を、使い切ったら先頭に戻る）を組むか、バッファを大きくします。1 フレームの物の数に上限を決めて `kMaxObjects` を十分に、取るのが簡単です。

## よくあるミス

??? failure "画面が、ちらつく前のフレームの値が混ざる"
    GPU が読んでいる、同じ領域を CPU が書き換えている。フレーム イン フライトごとに、別の領域に書く。

??? failure "全部の物が、同じ位置に描かれる"
    物ごとに別の領域に書かず、同じ領域を書き換えながら描いている（GPU は、記録された命令を後で実行するので、最後の値が全部の描画に使われる）。物ごとに別のオフセット。

??? failure "`CreateConstantBufferView` が、デバッグ レイヤーでエラー"
    `SizeInBytes` や `BufferLocation` が 256 の倍数・256 境界に、そろっていない。

??? failure "C++ で書いた値と、シェーダーの値がずれる"
    `cbuffer` の 16 バイト境界の規則を、無視している。パディングを入れる。`row_major` を付け忘れている。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 定数バッファ ＝ UPLOAD ヒープの、1 つの大きなバッファ。永続的に `Map`
    - [x] CBV の大きさ・開始位置は、256 バイトの倍数
    - [x] フレームごと・物ごとに、別の領域に書く
    - [x] 物ごとは、ルート CBV（アドレスを直接）が簡単。少量はルート定数
    - [x] `cbuffer` の 16 バイト境界と `row_major` は、同じ規則

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Root Signature](root-signature.md)
- [Frame Resources](frame-resources.md)
- [Upload Buffer](upload-buffer.md)
- [Constant Buffer](../dx11/constant-buffer.md)
- [Microsoft Learn: 定数バッファ ビュー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/using-constant-buffers-in-direct3d-12)
