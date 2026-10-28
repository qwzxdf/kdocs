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

プール方式のメモリリソースは、同じ大きさのブロックをまとめて用意します。「1 回にいくつ取るか」「どの大きさまでプールにするか」を `pool_options` で指定します。

!!! tip "ポイント"
    - `max_blocks_per_chunk` と `largest_required_pool_block` の 2 つのメンバ。
    - 0 を指定すると実装の既定値になる。
    - `unsynchronized_pool_resource` と `synchronized_pool_resource` に渡す。

!!! info "このページを読む前に"
    [`memory_resource`](memory_resource.md) を先に読んでください。

## 関数の詳しい説明

### std::pmr::pool_options {#pool_options}

```cpp
struct pool_options {
  size_t max_blocks_per_chunk = 0;
  size_t largest_required_pool_block = 0;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `max_blocks_per_chunk` | size_t | 1 回の確保で用意するブロックの最大数 |
| `largest_required_pool_block` | size_t | プールで扱う最大のブロックサイズ（バイト） |

- 戻り値: なし（設定値）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>

int main() {
  std::pmr::pool_options opts;
  opts.max_blocks_per_chunk = 64;
  opts.largest_required_pool_block = 256;
  std::pmr::unsynchronized_pool_resource pool(opts);
  std::println("{}", pool.options().max_blocks_per_chunk);
}
```

```text title="実行結果"
64
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 小さなオブジェクトを大量に作るプールの調整 | `opts.largest_required_pool_block = 256;` |

## よくあるミス

??? failure "大きすぎる値を入れる"
    `largest_required_pool_block` を大きくすると、プールを用意するメモリが増えます。実測してから決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unsynchronized_pool_resource`](unsynchronized_pool_resource.md) | スレッド非対応のプール |
| [`synchronized_pool_resource`](synchronized_pool_resource.md) | スレッド対応のプール |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プールの設定をまとめた構造体
    - [x] 0 は既定値
    - [x] プールの resource に渡す

## 関連ページ

- [cpprefjp: std::pmr::pool_options](https://cpprefjp.github.io/reference/memory_resource/pool_options.html)
- [cppreference: std::pmr::pool_options](https://en.cppreference.com/w/cpp/memory/pool_options)
