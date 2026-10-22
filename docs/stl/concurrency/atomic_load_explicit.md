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

`a.load(order)` の自由関数版です。同期が必要な最小限の順序（`acquire` や `relaxed`）を指定して、速度を稼ぎます。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_load_explicit {#atomic_load_explicit}

```cpp
template <class T>
T atomic_load_explicit(const std::atomic<T>* obj, std::memory_order order) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | const atomic<T>* | 対象 |
| `order` | memory_order | メモリ順序 |

- 戻り値: 読んだ値
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a{5};
  std::println("{}", std::atomic_load_explicit(&a, std::memory_order_relaxed));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | フラグを軽く読む |

## よくあるミス

??? failure "順序を弱めすぎる"
    他のデータの可視性が必要なら `acquire` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_store_explicit`](atomic_store_explicit.md) | 書く |
| [`memory_order`](memory_order.md) | 順序 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メモリ順序を指定して、アトミックに値を読む
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_load_explicit](https://cpprefjp.github.io/reference/atomic/atomic_load_explicit.html)
- [cppreference: std::atomic_load_explicit](https://en.cppreference.com/w/cpp/atomic/atomic_load_explicit)
