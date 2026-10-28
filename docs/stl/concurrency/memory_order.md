---
title: std::memory_order
summary: "アトミック操作の、メモリの見え方の順序を決める指定。"
order: 64
tags:
  - 並行処理
---

# std::memory_order

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <atomic>`
</div>

`std::memory_order` は、**アトミック操作がほかのメモリ操作に対して「どの順番で見えるか」を指定する**値です。分からなければ指定しない（既定の `seq_cst` が最も安全）のが基本です。「フラグを立てる前に書いたデータをフラグを見た側がきちんと読める」ようにするには、`release` と `acquire` を組で使います。

!!! tip "ポイント"
    - **迷ったら指定しない。** 既定の `memory_order_seq_cst` が一番安全。
    - `release`（書く側）と `acquire`（読む側）が一組。
    - 単純なカウンタには `relaxed` で足りる（順序の保証が要らないとき）。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 値の一覧

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `memory_order_seq_cst`（省略時） | <span class="rank rank-sometimes">たまに</span> | 一番厳しい。すべてのスレッドから見て操作の順番がそろう |
| `memory_order_relaxed` | <span class="rank rank-rare">知ってるだけ</span> | その変数の値が壊れないことだけ保証。順番は保証しない（単純なカウンタ向け） |
| `memory_order_acquire` | <span class="rank rank-rare">知ってるだけ</span> | 読み込み用。これより後の読み書きが前に来ない |
| `memory_order_release` | <span class="rank rank-rare">知ってるだけ</span> | 書き込み用。これより前の読み書きが後に来ない（acquire と組で使う） |
| `memory_order_acq_rel` | <span class="rank rank-rare">知ってるだけ</span> | acquire と release の両方（読んで書く操作用） |
| `memory_order_consume` | <span class="rank rank-rare">知ってるだけ</span> | 使わない（C++26 で非推奨） |

## 関数の詳しい説明

### release と acquire の組 {#release_acquire}

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  std::atomic<bool> ready{false};
  int data = 0;

  std::thread writer([&] {
    data = 42;                                            // ① データを書く
    ready.store(true, std::memory_order_release);         // ② 「できた」と知らせる（①より前に動かない）
  });

  while (!ready.load(std::memory_order_acquire)) {        // ③ 知らせを待つ
  }
  std::println("{}", data);                               // ④ ①の書き込みが必ず見える

  writer.join();
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フラグで「データができた」と知らせる | `ready.store(true, release)` と `ready.load(acquire)` |
| 統計用のカウンタ | `counter.fetch_add(1, std::memory_order_relaxed)` |

## よくあるミス

??? failure "relaxed を安易に使う"
    relaxed は順序を保証しません。フラグとデータの組には使えません。

??? failure "acquire だけ、release だけを使う"
    両方がそろって初めて、「書いたものが見える」保証になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::atomic`](atomic.md) | メモリオーダーを指定できる |
| [`std::mutex`](mutex.md) | ロックの中は順序が自動で保証される |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 迷ったら指定しない（seq_cst）
    - [x] release と acquire が一組
    - [x] relaxed は順序なし

## 関連ページ

- [cpprefjp: std::memory_order](https://cpprefjp.github.io/reference/atomic/memory_order.html)
- [cppreference: std::memory_order](https://en.cppreference.com/w/cpp/atomic/memory_order)
