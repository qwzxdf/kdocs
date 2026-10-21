---
title: std::pmr::null_memory_resource
summary: "確保しようとすると必ず失敗するメモリリソース。"
order: 6
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::null_memory_resource

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory_resource>`
</div>

`std::pmr::null_memory_resource()` は、**確保しようとすると必ず `std::bad_alloc` を投げる**メモリリソースです。`monotonic_buffer_resource` の親に指定して、「用意したバッファ以外からは絶対に確保させない」ようにするために使います。

!!! tip "ポイント"
    - 固定バッファだけを使い、ヒープに逃げさせない用途。
    - バッファが足りないと例外になるので、すぐ気づける。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### null_memory_resource {#null_memory_resource}

```cpp
memory_resource* null_memory_resource() noexcept;
```

- 戻り値: 確保しようとすると `std::bad_alloc` を投げるリソース
- 「**ヒープは絶対に使わせない**」ときの上流に指定します。固定のバッファが足りなくなると、ヒープに逃げずに例外が飛ぶので、バッファの大きさが足りないことにすぐ気づけます

```cpp
std::byte buffer[1024];
std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer),
                                         std::pmr::null_memory_resource());
```

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <new>
#include <print>
#include <vector>

int main() {
  std::pmr::vector<int> v(std::pmr::null_memory_resource());  // 確保を許さない
  try {
    v.push_back(1);
  } catch (const std::bad_alloc&) {
    std::println("確保できない");
  }
}
```

```text title="実行結果"
確保できない
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ヒープ確保禁止のコード（ゲームのフレーム処理） | `monotonic_buffer_resource pool(buf, size, std::pmr::null_memory_resource());` |

## よくあるミス

??? failure "バッファの大きさが足りない"
    例外が飛びます。大きさを余裕を持って決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new_delete_resource`](new_delete_resource.md) | 普通のヒープ |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 確保しようとすると例外
    - [x] ヒープに逃がさない用途
    - [x] 固定バッファと組み合わせる

## 関連ページ

- [cpprefjp: std::pmr::null_memory_resource](https://cpprefjp.github.io/reference/memory_resource/null_memory_resource.html)
- [cppreference: std::pmr::null_memory_resource](https://en.cppreference.com/w/cpp/memory/null_memory_resource)
