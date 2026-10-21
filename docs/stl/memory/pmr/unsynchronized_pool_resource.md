---
title: std::pmr::unsynchronized_pool_resource
summary: "大きさごとの置き場を持ち、解放した分を再利用するメモリ領域（スレッド非対応）。"
order: 3
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::unsynchronized_pool_resource

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory_resource>`
</div>

`std::pmr::unsynchronized_pool_resource` は、**大きさごとの置き場（プール）を持ち、解放したメモリを再利用する**メモリリソースです。小さなオブジェクトを何度も作って捨てるときに速くなります。スレッドセーフではないので、1 つのスレッドだけで使います。

!!! tip "ポイント"
    - `monotonic_buffer_resource` と違い、個別の解放ができて再利用される。
    - 1 スレッド専用。複数スレッドなら `synchronized_pool_resource`。
    - 親のリソース（既定は `new_delete_resource`）から大きな塊を取る。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### unsynchronized_pool_resource {#unsynchronized_pool_resource}

```cpp
class unsynchronized_pool_resource : public memory_resource {
 public:
  unsynchronized_pool_resource();
  explicit unsynchronized_pool_resource(memory_resource* upstream);
  unsynchronized_pool_resource(const pool_options& opts, memory_resource* upstream);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `upstream` | `std::pmr::memory_resource*` | プールが足りないときに取りに行く先 |
| `opts` | `const pool_options&` | `max_blocks_per_chunk`（1 回に取るブロック数）、`largest_required_pool_block`（プールで扱う最大の大きさ）の設定 |

- **大きさごとのプール**（8、16、32…バイト）を持ち、解放されたブロックを**再利用**します。monotonic と違い、個別に `deallocate` したものが次の確保で使い回されます
- 要素を 1 つずつ確保して、どんどん追加・削除する `std::pmr::map`、`std::pmr::list`、`std::pmr::unordered_map` に向いています
- 大きすぎるものは上流に任せます。スレッドセーフではありません

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  std::pmr::unsynchronized_pool_resource pool;
  std::pmr::vector<int> v(&pool);
  v.assign({1, 2, 3});
  std::println("{}", v.size());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 寿命がバラバラな小さなオブジェクトを何度も作る | `std::pmr::unsynchronized_pool_resource pool;` |

## よくあるミス

??? failure "複数スレッドで共有する"
    スレッドセーフではありません。`synchronized_pool_resource` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`synchronized_pool_resource`](synchronized_pool_resource.md) | スレッドセーフ版 |
| [`monotonic_buffer_resource`](monotonic_buffer_resource.md) | 積むだけ |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 解放した分を再利用するプール
    - [x] 1 スレッド専用
    - [x] 個別に解放できる

## 関連ページ

- [cpprefjp: std::pmr::unsynchronized_pool_resource](https://cpprefjp.github.io/reference/memory_resource/unsynchronized_pool_resource.html)
- [cppreference: std::pmr::unsynchronized_pool_resource](https://en.cppreference.com/w/cpp/memory/unsynchronized_pool_resource)
