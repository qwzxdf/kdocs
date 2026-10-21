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

`std::pmr::new_delete_resource()` は、**普通の `new` / `delete`（ヒープ）を使うメモリリソース**を返す関数です。pmr コンテナに何も指定しなかったときの既定の取り先です。ほかのリソースが「足りなくなったら親から取る」ときの親にもなります。

!!! tip "ポイント"
    - 返るのはポインター。解放不要（プログラム全体で 1 つ）。
    - スレッドセーフ。
    - 明示したいときに使う。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### new_delete_resource {#new_delete_resource}

```cpp
memory_resource* new_delete_resource() noexcept;
```

- 戻り値: 普通の `operator new` / `operator delete` を使うリソースへのポインタ（グローバルに 1 つ）
- デフォルトで使われるリソースです。`monotonic_buffer_resource` や pool の**上流**に指定するのが主な使い方です

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>

int main() {
  std::pmr::memory_resource* r = std::pmr::new_delete_resource();
  void* p = r->allocate(16);
  r->deallocate(p, 16);
  std::println("{}", r == std::pmr::get_default_resource());  // 既定のリソース
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 既定の取り先を明示する | `std::pmr::vector<int> v(std::pmr::new_delete_resource());` |

## よくあるミス

??? failure "delete しようとする"
    返ってくるのは共有のオブジェクトです。解放不要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`null_memory_resource`](null_memory_resource.md) | 確保させない |
| [`monotonic_buffer_resource`](monotonic_buffer_resource.md) | 積むだけ |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 普通のヒープを使う
    - [x] 既定の取り先
    - [x] スレッドセーフ

## 関連ページ

- [cpprefjp: std::pmr::new_delete_resource](https://cpprefjp.github.io/reference/memory_resource/new_delete_resource.html)
- [cppreference: std::pmr::new_delete_resource](https://en.cppreference.com/w/cpp/memory/new_delete_resource)
