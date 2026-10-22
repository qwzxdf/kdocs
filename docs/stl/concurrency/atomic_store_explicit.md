---
title: std::atomic_store_explicit
summary: "メモリ順序を指定して、アトミックに値を書く。"
order: 900
tags:
  - 並行処理
---

# std::atomic_store_explicit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`a.store(x, order)` の自由関数版です。`release` で書くと、それより前の書き込みが、読む側から見えるようになります。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_store_explicit {#atomic_store_explicit}

```cpp
template <class T>
void atomic_store_explicit(std::atomic<T>* obj, T desired, std::memory_order order) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | atomic<T>* | 対象 |
| `desired` | T | 書く値 |
| `order` | memory_order | メモリ順序 |

- 戻り値: なし
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a{0};
  std::atomic_store_explicit(&a, 5, std::memory_order_release);
  std::println("{}", a.load());
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 完了フラグを立てる |

## よくあるミス

??? failure "`acquire` を指定する"
    書き込みに `acquire` は使えません（`release` / `seq_cst` / `relaxed`）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_load_explicit`](atomic_load_explicit.md) | 読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メモリ順序を指定して、アトミックに値を書く
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_store_explicit](https://cpprefjp.github.io/reference/atomic/atomic_store_explicit.html)
- [cppreference: std::atomic_store_explicit](https://en.cppreference.com/w/cpp/atomic/atomic_store_explicit)
