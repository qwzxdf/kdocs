---
title: std::atomic_load_explicit
summary: "メモリ順序を指定して、アトミックに値を読む。"
order: 900
tags:
  - 並行処理
---

# std::atomic_load_explicit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`atomic` の値を読むときの標準のメモリ順序は、最も強い `seq_cst` で、他のスレッドの書き込みとの順序を、全体で保証します。強すぎて遅いときや、逆に、必要な保証だけを明示したいときに、順序を指定して読む関数が `atomic_load_explicit` です。

!!! tip "ポイント"
    - `atomic` の値を、メモリ順序を指定して読む
    - メンバー関数 `a.load(order)` と同じ
    - 読み込みに使える順序は `relaxed`、`consume`、`acquire`、`seq_cst`
    - `release` や `acq_rel` は読み込みには使えない

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_load_explicit {#atomic_load_explicit}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
T atomic_load_explicit(const std::atomic<T>* obj, std::memory_order order) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | `const std::atomic<T>*` | 読む対象 |
| `order` | `std::memory_order` | メモリ順序 |

`memory_order_acquire` は、「この読み込み以降の操作が、この読み込みの前に移動されない」保証と、「書き込む側が `release` した、それ以前の書き込みが見える」保証を与えます。フラグで完了を知らせる設計で、書く側が `release`、読む側が `acquire` の組を使います。

`memory_order_relaxed` は、値の原子性だけを保証し、他のデータとの順序は保証しません。カウンターの読み出しのように、順序が要らない場面で使います。

迷ったら、既定の `seq_cst` にします。誤りの余地が最も少ないからです。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  int data = 0;
  std::atomic<bool> ready{false};

  std::thread producer([&] {
    data = 42;                                              // 先にデータを書く
    std::atomic_store_explicit(&ready, true, std::memory_order_release);
  });

  // ready が立つまで待つ
  while (!std::atomic_load_explicit(&ready, std::memory_order_acquire)) {
  }
  std::println("{}", data);  // release / acquire の組で、42 が見える
  producer.join();
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

完了フラグでデータの準備を知らせる、軽い同期に使います。複雑になるなら、`mutex` や `condition_variable` にします。

## よくあるミス

??? failure "release と acquire を片方だけ使う"
    保証は組で成り立ちます。

??? failure "relaxed で他のデータの順序を期待する"
    保証されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_store_explicit`](atomic_store_explicit.md) | 順序を指定して書く |
| [`memory_order`](memory_order.md) | 順序の一覧 |
| [`atomic`](atomic.md) | 本体 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_load_explicit](https://cpprefjp.github.io/reference/atomic/atomic_load_explicit.html)
- [cppreference: std::atomic_load_explicit](https://en.cppreference.com/w/cpp/atomic/atomic_load_explicit)
