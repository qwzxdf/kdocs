---
title: std::atomic_flag
summary: "一番単純なアトミックなフラグ（立っているか、いないか）。"
order: 62
tags:
  - 並行処理
---

# std::atomic_flag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <atomic>`
</div>

`std::atomic_flag` は、**必ずロックなしで動くことが保証された、最も単純なフラグ**です。「立てる（`test_and_set`）」「下ろす（`clear`）」の 2 つの操作だけを持ちます。スピンロック（ビジー待ちの鍵）の部品に使われます。普通のフラグには `std::atomic<bool>` のほうが使いやすいです。

!!! tip "ポイント"
    - `test_and_set()` が前の値を返し、同時に立てる。
    - C++20 で `test()` や `wait()` が追加され、`atomic<bool>` に近くなった。
    - 普通は `std::atomic<bool>` で足りる。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_flag {#atomic_flag}

```cpp
class atomic_flag {
 public:
  bool test_and_set() noexcept;
  void clear() noexcept;
  bool test() const noexcept;  // C++20
};
```

- 一番単純な bool の atomic。スピンロックを自作するときに使います

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> x;
  std::atomic_flag f;
  bool was_set = f.test_and_set();
  std::println("{} {} {}", x.is_lock_free(), was_set, f.test());
}
```

```text title="実行結果"
true false true
```

### test_and_set {#test_and_set}

```cpp
bool test_and_set(std::memory_order order = std::memory_order_seq_cst) noexcept;
```

- 計算量: 定数

旗を立てて、立てる前の状態を返します。スピンロックの基本部品です。

### clear {#clear}

```cpp
void clear(std::memory_order order = std::memory_order_seq_cst) noexcept;
```

- 計算量: 定数

旗を下ろします。

### test <span class="ver ver-20">C++20</span> {#test data-toc-label="test"}

```cpp
bool test(std::memory_order order = std::memory_order_seq_cst) const noexcept;
```

- 計算量: 定数

旗が立っているかを調べます（旗は変えません）。

### wait <span class="ver ver-20">C++20</span> {#wait data-toc-label="wait"}

```cpp
void wait(bool old, std::memory_order order = std::memory_order_seq_cst) const noexcept;
```

- 計算量: 待つ時間による

旗が `old` と等しい間、待ちます。

### notify_one <span class="ver ver-20">C++20</span> {#notify_one data-toc-label="notify_one"}

```cpp
void notify_one() noexcept;
```

- 計算量: 定数

`wait` で待っているスレッドを 1 つ起こします。

### notify_all <span class="ver ver-20">C++20</span> {#notify_all data-toc-label="notify_all"}

```cpp
void notify_all() noexcept;
```

- 計算量: 定数

`wait` で待っているスレッドを全部起こします。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スピンロックを自作する | `while (flag.test_and_set(std::memory_order_acquire)) {}` |

## よくあるミス

??? failure "スピンロックで長く待つ"
    CPU を使い続けます。待ちが長くなるなら、`mutex` や条件変数にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::atomic`](atomic.md) | `atomic<bool>` ならもっと自由 |
| [`std::mutex`](mutex.md) | 普通の鍵 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最も単純なアトミックなフラグ
    - [x] `test_and_set` / `clear`
    - [x] 普通は `atomic<bool>`

## 関連ページ

- [cpprefjp: std::atomic_flag](https://cpprefjp.github.io/reference/atomic/atomic_flag.html)
- [cppreference: std::atomic_flag](https://en.cppreference.com/w/cpp/atomic/atomic_flag)
