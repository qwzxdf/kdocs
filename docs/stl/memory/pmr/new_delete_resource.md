---
title: std::pmr::new_delete_resource
summary: "普通の new / delete を使うメモリリソース（既定）。"
order: 5
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::new_delete_resource

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory_resource>`
</div>

`std::pmr::new_delete_resource()` は、グローバルの `operator new` / `operator delete` から確保する、標準のリソースを返します。何も指定しない `pmr` コンテナの取り先（既定のリソース）がこれです。普通のコンテナと同じ動作になります。

!!! tip "ポイント"
    - 戻り値は `memory_resource*`。プログラムに 1 つだけのオブジェクト
    - アライメントつきの `operator new` を使い、要求どおりのアライメントを守る
    - `pmr` のコンテナの既定の取り先
    - 他のリソースの「上流」としてよく使う

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::new_delete_resource {#new_delete_resource}

<span class="ver ver-17">C++17</span>

```cpp
std::pmr::memory_resource* new_delete_resource() noexcept;
```

いつ呼んでも、同じオブジェクトへのポインターを返します。`set_default_resource` を呼ばない限り、`get_default_resource()` はこれを返します。

スレッド セーフです。複数のスレッドから同時に確保しても、`operator new` に委ねられます。

グローバルの `operator new` を置き換えているときは、そのメモリ管理を通ります。確保の統計を取りたいなら、`operator new` の置き換えか、自作の `memory_resource` で包みます。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>

int main() {
  std::pmr::memory_resource* r = std::pmr::new_delete_resource();

  // 直接確保して、返す
  void* p = r->allocate(64, 16);
  std::println("確保できた: {}", p != nullptr);
  r->deallocate(p, 64, 16);

  // 何度呼んでも同じオブジェクト
  std::println("同じ: {}", r == std::pmr::new_delete_resource());

  // 既定のリソースは、これ
  std::println("既定のリソース: {}", std::pmr::get_default_resource() == r);
}
```

```text title="実行結果"
確保できた: true
同じ: true
既定のリソース: true
```

## ゲームでの使いどころ

`monotonic_buffer_resource` などの上流に指定します。何も渡さない `pmr` コンテナは、これを使います。

## よくあるミス

??? failure "deallocate に違う大きさを渡す"
    `allocate` と同じ大きさとアライメントで返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`default_resource`](default_resource.md) | 既定のリソースの取得・設定 |
| [`null_memory_resource`](null_memory_resource.md) | 常に失敗するリソース |
| [`memory_resource`](memory_resource.md) | 基底クラス |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::new_delete_resource](https://cpprefjp.github.io/reference/memory_resource/new_delete_resource.html)
- [cppreference: std::pmr::new_delete_resource](https://en.cppreference.com/w/cpp/memory/new_delete_resource)
