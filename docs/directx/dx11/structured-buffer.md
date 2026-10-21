---
title: Structured and Raw Buffers
tags:
  - DirectX
---

# Structured and Raw Buffers

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

頂点バッファ、インデックス バッファ、定数バッファは <strong>決まった用途</strong>のバッファです。シェーダーが <strong>自由な構造体の配列</strong>を読み書きしたいとき（インスタンス データ、パーティクル、ライトの一覧、カリングの結果）に使うのが <strong>構造化バッファ</strong>（Structured Buffer）と、<strong>生のバッファ</strong>（Raw / ByteAddress Buffer）です。計算シェーダーの入出力の中心です。

!!! tip "ポイント"
    - <strong>構造化バッファ</strong> ＝ 構造体の配列。HLSL では `StructuredBuffer<T>`（読む）、`RWStructuredBuffer<T>`（読み書き）。
    - <strong>生のバッファ</strong> ＝ バイトの列。`ByteAddressBuffer`、`RWByteAddressBuffer`。4 バイト単位で自由に読み書き。
    - 作成は `CreateBuffer` に `MiscFlags` で種類を指定する。`StructureByteStride` に構造体の大きさ。
    - 読む用に SRV、書く用に UAV を作る（[Shader Resource View (SRV)](shader-resource-view.md)、[Unordered Access View (UAV)](uav.md)）。
    - 定数バッファと違い 16 バイト境界の制約は緩い（構造体は、そのまま並ぶ）。サイズの上限も大きい。

## 構造化バッファ

```cpp
struct Particle {
  DirectX::XMFLOAT3 position;     // 12 バイト
  float life;                     // 4 バイト
  DirectX::XMFLOAT3 velocity;     // 12 バイト
  float size;                     // 4 バイト → 合計 32 バイト
};

D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(Particle) * max_particles;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;   // 読む（SRV）と、書く（UAV）
desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;                      // 構造化バッファ
desc.StructureByteStride = sizeof(Particle);                                 // 1 要素の大きさ
device->CreateBuffer(&desc, nullptr, &particle_buffer);
```

```cpp
// SRV: 構造化バッファは、Format を UNKNOWN、NumElements で、要素数を指定する。
D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_UNKNOWN;
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_BUFFER;
srv_desc.Buffer.FirstElement = 0;
srv_desc.Buffer.NumElements = max_particles;
device->CreateShaderResourceView(particle_buffer.Get(), &srv_desc, &particle_srv);

// UAV: 同様に。
D3D11_UNORDERED_ACCESS_VIEW_DESC uav_desc = {};
uav_desc.Format = DXGI_FORMAT_UNKNOWN;
uav_desc.ViewDimension = D3D11_UAV_DIMENSION_BUFFER;
uav_desc.Buffer.FirstElement = 0;
uav_desc.Buffer.NumElements = max_particles;
device->CreateUnorderedAccessView(particle_buffer.Get(), &uav_desc, &particle_uav);
```

```hlsl
struct Particle {
  float3 position;
  float life;
  float3 velocity;
  float size;
};

StructuredBuffer<Particle> g_particles_in : register(t0);       // 読む（SRV）
RWStructuredBuffer<Particle> g_particles_out : register(u0);    // 書く（UAV）

[numthreads(64, 1, 1)]
void UpdateCS(uint3 id : SV_DispatchThreadID) {
  Particle p = g_particles_in[id.x];
  p.position += p.velocity * g_delta_time;
  p.life -= g_delta_time;
  g_particles_out[id.x] = p;
}
```

HLSL の構造体と C++ の構造体を <strong>同じ並び・同じ大きさ</strong>にそろえます。定数バッファと違い 16 バイト境界の規則は、ありませんが `float3` の次に `float` を置くときれいに 16 バイトに収まる並びに、しておくと GPU のアクセスが、効率的です。

## 生のバッファ（ByteAddressBuffer）

構造体の型を持たず <strong>バイト アドレス</strong>で、読み書きします。1 つのバッファにいろいろな型のデータを詰めるときに使います。

```cpp
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = byte_size;                                          // 4 の倍数
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;
desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_ALLOW_RAW_VIEWS;         // 生のビューを、許可
device->CreateBuffer(&desc, nullptr, &raw_buffer);

D3D11_UNORDERED_ACCESS_VIEW_DESC uav_desc = {};
uav_desc.Format = DXGI_FORMAT_R32_TYPELESS;                          // 生のビューは、R32_TYPELESS
uav_desc.ViewDimension = D3D11_UAV_DIMENSION_BUFFER;
uav_desc.Buffer.NumElements = byte_size / 4;                         // 4 バイト単位の、数
uav_desc.Buffer.Flags = D3D11_BUFFER_UAV_FLAG_RAW;                   // RAW
device->CreateUnorderedAccessView(raw_buffer.Get(), &uav_desc, &raw_uav);
```

```hlsl
RWByteAddressBuffer g_raw : register(u0);

uint value = g_raw.Load(byte_offset);                       // 4 バイトを、読む
g_raw.Store(byte_offset, value);                            // 4 バイトを、書く
g_raw.InterlockedAdd(byte_offset, 1);                       // アトミックに、足す
uint4 four = g_raw.Load4(byte_offset);                      // 16 バイトを、まとめて
```

ヒストグラム（[Auto Exposure](../../graphics/postprocess/tonemapping/auto-exposure.md)）、描画の引数バッファ（間接描画）、バインドレスなデータの詰め合わせに使います。

## カウンターと追加・消費（Append / Consume）

UAV に <strong>カウンター</strong>を付けると、「要素の追加」と「取り出し」をアトミックにできます。パーティクルの生成・消滅やカリング後のリストの作成に向いています。

```cpp
uav_desc.Buffer.Flags = D3D11_BUFFER_UAV_FLAG_APPEND;                // 追加・消費バッファ（カウンターつき）
device->CreateUnorderedAccessView(buffer.Get(), &uav_desc, &append_uav);
```

```hlsl
AppendStructuredBuffer<Particle> g_alive_list : register(u0);       // 追加
ConsumeStructuredBuffer<uint> g_free_list : register(u1);           // 取り出し

g_alive_list.Append(particle);                                      // カウンターを +1 して、末尾に書く
uint index = g_free_list.Consume();                                 // カウンターを -1 して、末尾から取る
```

```cpp
// UAV を束ねるとき、最後の引数で、カウンターの、初期値を、指定する（-1 で、そのまま、維持。0 で、空に）。
UINT initial_counts[] = {0};
context->CSSetUnorderedAccessViews(0, 1, append_uav.GetAddressOf(), initial_counts);

// カウンターの値を、別のバッファ（間接描画の引数など）へ、コピーする。
context->CopyStructureCount(args_buffer.Get(), sizeof(UINT), append_uav.Get());
```

`CopyStructureCount` はカウンターを GPU 上で、別のバッファにコピーして CPU に読み戻さずに間接描画の引数に使えます（[Instanced Drawing](instancing-draw.md)）。

## 構造化バッファと定数バッファの違い

| | 定数バッファ | 構造化バッファ |
| --- | --- | --- |
| 用途 | 少量のパラメータ | 大量の構造体の配列 |
| 大きさの上限 | 64 KB | 数百 MB 以上 |
| 16 バイト境界の制約 | きびしい | ゆるい |
| 読み書き | 読み取り専用 | SRV で読む UAV で書く |
| 速さ | 全スレッドが同じ値を読むなら速い | スレッドごとに別の要素を読むなら速い |

全ピクセルが同じ値（カメラ行列）を読むなら定数バッファが速く頂点・インスタンスごとに、別の要素を読むなら構造化バッファが、向きます。

## よくあるミス

??? failure "`CreateBuffer` が、失敗する（構造化バッファ）"
    `StructureByteStride` が 0、または `ByteWidth` がストライドの倍数でない。構造化バッファに `BIND_CONSTANT_BUFFER`、`BIND_VERTEX_BUFFER` を同時に指定している。

??? failure "C++ で書いた、データとシェーダーで読んだ値が、ずれる"
    HLSL の構造体と C++ の構造体の並びが違う。`float3` の後のパディングの扱いが違う。`static_assert(sizeof(T) == ...)` で確かめる。

??? failure "`CreateShaderResourceView` が、失敗する（構造化バッファ）"
    `Format` が `UNKNOWN` でない。`NumElements` がバッファの要素数を超えている。

??? failure "Append バッファに追加したのに要素数が増えない"
    UAV の束縛時の初期カウント（`pUAVInitialCounts`）が毎回、0 でリセットされている。維持したいときは `-1`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 構造化バッファ ＝ 構造体の配列。`MiscFlags = BUFFER_STRUCTURED`、`StructureByteStride`
    - [x] 生のバッファ ＝ バイトの列。`ALLOW_RAW_VIEWS`、`ByteAddressBuffer`
    - [x] 読む SRV（`Format = UNKNOWN`）、書く UAV
    - [x] HLSL と C++ の構造体をそろえる
    - [x] Append / Consume + `CopyStructureCount` で、GPU 上のリストと間接描画

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Compute Shader](compute-shader.md)
- [Unordered Access View (UAV)](uav.md)
- [Instanced Drawing](instancing-draw.md)
- [Microsoft Learn: Structured Buffer](https://learn.microsoft.com/ja-jp/windows/win32/direct3d11/direct3d-11-advanced-stages-cs-resources)
