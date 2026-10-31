---
title: std::pmr::monotonic_buffer_resource
summary: "積むだけで、個別には解放しないメモリ領域。フレーム用に一括解放する。"
order: 1
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::monotonic_buffer_resource

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <memory_resource>`
</div>

1 フレームの間だけ使う一時的なデータは、フレームの終わりにまとめて捨てられます。個別に解放する必要はありません。`std::pmr::monotonic_buffer_resource` は、渡されたバッファの先頭から順に切り出して渡す、最も単純で速いリソースです。解放は何もせず、`release()` か破棄で一度に全部を返します。

!!! tip "ポイント"
    - 確保は、バッファの現在位置を進めるだけで、非常に速い
    - 個別の解放は何もしない。メモリは減らない
    - バッファが尽きたら、上流のリソース（既定は `new_delete_resource`）から追加で取る
    - `release()` で、確保した全部を一度に返す

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::monotonic_buffer_resource {#monotonic_buffer_resource}

<span class="ver ver-17">C++17</span>

```cpp
monotonic_buffer_resource(void* buffer, std::size_t size,
                          std::pmr::memory_resource* upstream = std::pmr::get_default_resource());
explicit monotonic_buffer_resource(std::pmr::memory_resource* upstream);
void release();
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer`, `size` | 領域 | 最初に使う領域。省略すると、上流から取る |
| `upstream` | `memory_resource*` | 領域が尽きたときの取り先 |

確保のたびに、アライメントを合わせて位置を進めます。足りなくなると、上流から次の塊（前の 1.5 倍程度）を取ります。個別の `deallocate` は何もしません。

そのため、`std::pmr::vector` で `push_back` を繰り返すと、領域を増やすたびに古い領域が残って、メモリを余計に使います。大きさが分かっているなら `reserve` で一度に確保します。

`release()` を呼ぶか、リソースを破棄すると、上流から取った塊を全部返します。デストラクターは、確保したオブジェクトのデストラクターを呼ばないので、オブジェクトは別途壊します。

上流を `null_memory_resource()` にすると、バッファを使い切った瞬間に `std::bad_alloc` が飛ぶので、「バッファに収まる設計か」を検証できます。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  std::byte buffer[1024];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer),
                                           std::pmr::null_memory_resource());

  std::pmr::vector<int> v(&pool);
  v.reserve(16);  // 一度に確保して、無駄を出さない
  for (int i = 0; i < 16; ++i) v.push_back(i);

  const auto* p = reinterpret_cast<const std::byte*>(v.data());
  std::println("要素はバッファの中: {}", p >= buffer && p < buffer + sizeof(buffer));

  // バッファに収まらない要求は、上流が null なので例外
  try {
    std::pmr::vector<int> big(&pool);
    big.resize(100000);
  } catch (const std::bad_alloc&) {
    std::println("バッファを使い切ると bad_alloc");
  }
}
```

```text title="実行結果"
要素はバッファの中: true
バッファを使い切ると bad_alloc
```

## ゲームでの使いどころ

1 フレームだけ使う一時データ（描画コマンド、衝突の結果、デバッグ文字列）を、フレームの始めに `release()` して、使い回します。

## よくあるミス

??? failure "push_back で膨らませる"
    古い領域が残ります。`reserve` で一度に取ります。

??? failure "オブジェクトのデストラクターが呼ばれると思う"
    呼ばれません。コンテナを先に破棄します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unsynchronized_pool_resource`](unsynchronized_pool_resource.md) | 個別に解放できるプール |
| [`null_memory_resource`](null_memory_resource.md) | 上流に置いて溢れを検出する |
| [`memory_resource`](memory_resource.md) | 基底クラス |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::monotonic_buffer_resource](https://cpprefjp.github.io/reference/memory_resource/monotonic_buffer_resource.html)
- [cppreference: std::pmr::monotonic_buffer_resource](https://en.cppreference.com/w/cpp/memory/monotonic_buffer_resource)
