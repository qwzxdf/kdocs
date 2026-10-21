---
title: std::atomic_ref
summary: "普通の変数を、一時的にアトミックに操作する。"
order: 63
tags:
  - 並行処理
---

# std::atomic_ref

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-20">C++20</span>
`#include <atomic>`
</div>

`std::atomic_ref` は、**すでにある普通の変数（`int` や配列の要素）を、その場でアトミックに操作できるようにする**参照です。大きな配列の一部の要素だけを、複数のスレッドから安全に足したいとき（ヒストグラムなど）に、`std::atomic<int>` の配列を作らずに済みます。

!!! tip "ポイント"
    - `std::atomic_ref<int> ref(counter);` と包むと、`fetch_add` などが使える。
    - `atomic_ref` を使っている間は、**その変数を他の方法で触ってはいけない**。
    - 変数は、`atomic_ref::required_alignment` のアラインメントを満たす必要がある。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_ref {#atomic_ref}

```cpp
template <class T>
struct atomic_ref {
  explicit atomic_ref(T& obj);
  T fetch_add(T arg, std::memory_order order = std::memory_order_seq_cst) const noexcept;
  // load / store / exchange / compare_exchange_* など、std::atomic と同じ操作
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | `T&` | 操作したい変数（整数、ポインター、トリビアルな型） |

- 戻り値: 各操作は `std::atomic` と同じ
- 計算量: O(1)

```cpp
#include <atomic>
#include <print>

int main() {
  int counter = 0;                  // ふつうの変数
  std::atomic_ref<int> ref(counter);

  ref.fetch_add(5);                 // アトミックに足す
  ++ref;
  std::println("{}", counter);
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 巨大な配列の要素を、複数のスレッドが加算する（ヒストグラム） | `std::atomic_ref<int>(bins[i]).fetch_add(1);` |

## よくあるミス

??? failure "同時に別の方法で触る"
    `atomic_ref` の最中に、普通の代入や読み取りを混ぜると競合します。アクセスは全部 `atomic_ref` 経由にします。

??? failure "アラインメントが足りない"
    `float` や `int` は通常問題ありませんが、パックされた構造体のメンバでは足りないことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::atomic`](atomic.md) | 最初からアトミックな型 |
| [`std::mutex`](mutex.md) | 複数の変数をまとめて守る |

## コンパイラ対応

C++20 の機能です。GCC 10 / Clang 19 / MSVC 19.28 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 普通の変数をその場でアトミックに操作する
    - [x] 最中は他の方法で触らない
    - [x] C++20

## 関連ページ

- [cpprefjp: std::atomic_ref](https://cpprefjp.github.io/reference/atomic/atomic_ref.html)
- [cppreference: std::atomic_ref](https://en.cppreference.com/w/cpp/atomic/atomic_ref)
