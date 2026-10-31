---
title: std::pmr::pool_options
summary: "プールのメモリリソースの、ブロックの大きさと数の設定。"
order: 900
tags:
  - メモリ
---

# std::pmr::pool_options

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory_resource>`
</div>

プール リソース（`synchronized_pool_resource` と `unsynchronized_pool_resource`）の振る舞いを調整する設定が `std::pmr::pool_options` です。1 つの塊（チャンク）に何個のブロックを取るか、どの大きさまでをプールで扱うかを指定します。0 を指定した項目は、実装の既定値が使われます。

!!! tip "ポイント"
    - `max_blocks_per_chunk`: 上流から 1 回に取るブロックの数の上限
    - `largest_required_pool_block`: プールで扱う最大のブロックの大きさ
    - 0 は「実装の既定値を使う」の意味
    - 実際の値は、実装が丸めたり、調整したりする

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::pool_options {#pool_options}

<span class="ver ver-17">C++17</span>

```cpp
struct pool_options {
  std::size_t max_blocks_per_chunk = 0;
  std::size_t largest_required_pool_block = 0;
};
```

| メンバー | 意味 |
| --- | --- |
| `max_blocks_per_chunk` | チャンク 1 つに入れるブロックの最大数 |
| `largest_required_pool_block` | プールで扱う最大のブロックの大きさ。これより大きい要求は、上流から直接取る |

プールは、大きさごとのブロックの列（プール）を持ち、足りなくなると、上流から新しいチャンクを取ります。`max_blocks_per_chunk` を大きくすると、上流への要求が減りますが、使わないブロックが増えます。

`largest_required_pool_block` は、小さなオブジェクトだけを速く扱いたいときに、小さく指定します。大きな要求がプールに入ると、メモリを無駄に使うからです。

指定した値は、プールを作った後で `options()` から読めますが、実装が丸めた値が返ります。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>

int main() {
  // 既定の設定: どちらも 0 (実装の既定値を使う)
  std::pmr::pool_options opts;
  std::println("{} {}", opts.max_blocks_per_chunk, opts.largest_required_pool_block);

  // 小さなオブジェクト向けに調整する
  opts.max_blocks_per_chunk = 64;
  opts.largest_required_pool_block = 256;
  std::pmr::unsynchronized_pool_resource pool(opts);

  // 指定した値は、実装に調整された上で保持される
  const std::pmr::pool_options actual = pool.options();
  std::println("調整後の最大ブロック: {}", actual.largest_required_pool_block > 0);
}
```

```text title="実行結果"
0 0
調整後の最大ブロック: true
```

## ゲームでの使いどころ

ゲーム内の小さなオブジェクト（弾、エフェクト）専用のプールを作るとき、最大ブロックを小さくして、無駄を減らします。

## よくあるミス

??? failure "設定した値が、そのままになると思う"
    実装が丸めます。`options()` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unsynchronized_pool_resource`](unsynchronized_pool_resource.md) | スレッド セーフでないプール |
| [`synchronized_pool_resource`](synchronized_pool_resource.md) | スレッド セーフなプール |
| [`monotonic_buffer_resource`](monotonic_buffer_resource.md) | 解放しないリソース |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::pool_options](https://cpprefjp.github.io/reference/memory_resource/pool_options.html)
- [cppreference: std::pmr::pool_options](https://en.cppreference.com/w/cpp/memory/pool_options)
