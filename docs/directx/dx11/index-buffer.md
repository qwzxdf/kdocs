---
title: Index Buffer
tags:
  - DirectX
---

# Index Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>インデックス バッファ</strong>は、「どの頂点を、どの順で、三角形に、つなぐか」を、<strong>頂点の番号</strong>で、並べた、バッファです。四角形（三角形 2 枚）は、頂点が 4 つで、足りるのに、頂点バッファだけで、描くと、6 頂点が、要ります。インデックスを、使うと、<strong>共有できる頂点を、1 つにまとめて</strong>、データを、減らせます。

!!! tip "ポイント"
    - 頂点バッファ（頂点の、データ）と、インデックス バッファ（頂点の、番号）の、2 つで、メッシュを、表す。
    - 番号は、`uint16_t`（65535 頂点まで）か、`uint32_t`。フォーマットを、`IASetIndexBuffer` に、渡す。
    - 描画は `DrawIndexed`。`Draw` ではない。
    - 三角形の、頂点の並びが、反時計回り（CCW）が、表。
    - 同じ頂点を、共有すると、GPU の、頂点キャッシュが、効き、頂点シェーダーの、呼び出しが、減る。

## なぜ、インデックスを、使うのか

四角形を、描くとき、比べます。

```text
頂点バッファだけ（6 頂点）:    A B C   A C D          ← A と C が、2 回ずつ
頂点 + インデックス（4 頂点 + 6 個の番号）: 頂点 A B C D、インデックス 0 1 2  0 2 3
```

頂点が、位置・法線・uv・接線で、数十バイトあると、共有により、データが、大きく、減ります。普通のメッシュ（なめらかな、モデル）は、1 つの頂点が、平均で、6 枚の三角形に、共有されるので、頂点の数が、約 1/6 になります。

## 作る

```cpp
// 四角形: 頂点 4 つ、インデックス 6 個（三角形 2 枚。どちらも反時計回り）。
const Vertex vertices[] = {
    {{-0.5f, 0.5f, 0.0f}, {1, 0, 0, 1}},     // 0: 左上
    {{-0.5f, -0.5f, 0.0f}, {0, 1, 0, 1}},    // 1: 左下
    {{0.5f, -0.5f, 0.0f}, {0, 0, 1, 1}},     // 2: 右下
    {{0.5f, 0.5f, 0.0f}, {1, 1, 0, 1}},      // 3: 右上
};
const uint16_t indices[] = {0, 1, 2,         // 左上 → 左下 → 右下（反時計回り）
                            0, 2, 3};        // 左上 → 右下 → 右上（反時計回り）
```

どちらの三角形も、反時計回りになるように、番号を、並べます。

```cpp
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(indices);
desc.Usage = D3D11_USAGE_IMMUTABLE;
desc.BindFlags = D3D11_BIND_INDEX_BUFFER;                  // インデックス バッファとして使う

D3D11_SUBRESOURCE_DATA init = {};
init.pSysMem = indices;

Microsoft::WRL::ComPtr<ID3D11Buffer> index_buffer;
device->CreateBuffer(&desc, &init, &index_buffer);
```

頂点バッファと、作り方は、同じで、`BindFlags` だけが、違います（[Vertex Buffer](vertex-buffer.md)）。

## パイプラインにつなぐ

```cpp
context->IASetIndexBuffer(index_buffer.Get(), DXGI_FORMAT_R16_UINT, 0);   // フォーマット: 番号の型。オフセット: 0
```

| 引数 | 内容 |
| --- | --- |
| `pIndexBuffer` | インデックス バッファ |
| `Format` | `DXGI_FORMAT_R16_UINT`（16 ビット）、`DXGI_FORMAT_R32_UINT`（32 ビット） |
| `Offset` | バッファの、使い始める、位置（バイト） |

| 型 | 頂点の、最大数 | 大きさ |
| --- | --- | --- |
| `uint16_t`（`R16_UINT`） | 65,536 | 小さい |
| `uint32_t`（`R32_UINT`） | 約 43 億 | 2 倍 |

頂点が、65,536 を超えない、メッシュは、16 ビットで、データを、半分に、できます。大きな、メッシュ（地形）は、32 ビットにします。

## 描く

```cpp
context->DrawIndexed(6,      // インデックスの数
                     0,      // インデックス バッファの、何番目から、読み始めるか
                     0);     // 各インデックスに、足す値（頂点バッファの、基準位置）
```

| 引数 | 内容 |
| --- | --- |
| `IndexCount` | 使う、インデックスの数 |
| `StartIndexLocation` | インデックス バッファの、開始位置（個数） |
| `BaseVertexLocation` | 頂点バッファから、頂点を引くとき、各インデックスに、足す値 |

<strong>`BaseVertexLocation`</strong> は、1 つの、大きな、頂点バッファに、複数の、メッシュを、詰めたときに、役立ちます。

```cpp
// メッシュ A: 頂点 0〜99、メッシュ B: 頂点 100〜199。どちらも、インデックスは、0 始まりで、持てる。
context->DrawIndexed(a_index_count, a_index_start, 0);       // A: 頂点の基準 0
context->DrawIndexed(b_index_count, b_index_start, 100);     // B: 各インデックスに 100 を足して、頂点を引く
```

## プリミティブ リスタート

`TRIANGLESTRIP`（ストリップ）で、複数の、ストリップを、1 回で、描きたいときは、インデックスの、最大値（`0xFFFF`、`0xFFFFFFFF`）を、「切れ目」として、使えます。

```cpp
const uint16_t strip[] = {0, 1, 2, 3, 0xFFFF, 4, 5, 6, 7};   // 2 つの、ストリップを、1 回で
```

普通の、三角形リスト（`TRIANGLELIST`）では、使いません。

## よくあるミス

??? failure "メッシュが、化ける、または、一部が、欠ける"
    `IASetIndexBuffer` の、フォーマットが、インデックスの、型と、合っていない（`uint16_t` の、データに `R32_UINT` を指定した、など）。

??? failure "`Draw` を、呼んで、何も、描かれない"
    インデックスを、使うメッシュは、`DrawIndexed`。`Draw` は、インデックス バッファを、無視して、頂点バッファを、順に、読む。

??? failure "片方の三角形だけ、見えない"
    その三角形の、並びが、時計回り（CW）で、裏面として、捨てられている。2 枚とも、反時計回りに、そろえる。

??? failure "65,536 を超える頂点で、メッシュが、壊れる"
    16 ビットのインデックスで、表せない。`uint32_t` と `R32_UINT` に、する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] インデックス ＝ 頂点の番号。頂点を、共有して、データを、減らす
    - [x] `D3D11_BIND_INDEX_BUFFER`、`IASetIndexBuffer`（フォーマットは、番号の型）
    - [x] 描画は `DrawIndexed`
    - [x] 並びは、反時計回りが表
    - [x] 1 つの、大きなバッファに、詰めるときは、`BaseVertexLocation`

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Vertex Buffer](vertex-buffer.md)
- [Drawing a Triangle](triangle.md)
- [Rasterizer State](rasterizer-state.md)
- [Microsoft Learn: ID3D11DeviceContext::DrawIndexed](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-drawindexed)
