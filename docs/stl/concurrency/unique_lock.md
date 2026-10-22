---
title: std::unique_lock
summary: "途中で開け閉めできる鍵。条件変数と一緒に使う。"
order: 80
tags:
  - 並行処理
---

# std::unique_lock

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::unique_lock` は、`lock_guard` より**柔軟な鍵**です。ロックを後からかけたり、途中で開けたり、別の場所に渡したりできます。[`condition_variable`](condition_variable.md) は、待っている間に鍵を開ける必要があるので、必ず `unique_lock` を使います。

!!! tip "ポイント"
    - **条件変数と使うなら `unique_lock`**。それ以外は `lock_guard` で足りる。
    - `std::unique_lock lock(m, std::defer_lock);` で、ロックせずに作れる。
    - 手動の `lock()` / `unlock()` ができるぶん、`lock_guard` よりわずかに重い。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::unique_lock {#unique_lock}

```cpp
template <class Mutex>
class unique_lock;
```

- lock_guard と同じですが、途中で `unlock()` / `lock()` したり、ムーブしたりできます。[`std::condition_variable`](condition_variable.md) で待つときに必要です

### try_lock {#try_lock}

```cpp
bool try_lock();
```

- 計算量: 定数

待たずに、ミューテックスのロックを試みます。取れたら `true`。

### try_lock_for {#try_lock_for}

```cpp
template <class Rep, class Period>
bool try_lock_for(const std::chrono::duration<Rep, Period>& rel_time);
```

- 計算量: 最大で指定時間

指定した時間まで待って、ロックを試みます。

### try_lock_until {#try_lock_until}

```cpp
template <class Clock, class Duration>
bool try_lock_until(const std::chrono::time_point<Clock, Duration>& abs_time);
```

- 計算量: 最大で指定時刻まで

指定した時刻まで待って、ロックを試みます。

### unlock {#unlock}

```cpp
void unlock();
```

- 計算量: 定数

ロックを解除します。スコープの途中で、早めに解除したいときに使います。

### swap {#swap}

```cpp
void swap(unique_lock& other) noexcept;
```

- 計算量: 定数

2 つの `unique_lock` を入れ替えます。

### release {#release}

```cpp
mutex_type* release() noexcept;
```

- 計算量: 定数

ミューテックスとの関連を切り離し、そのポインタを返します。解除はしないので、以降は自分で `unlock` します。

### mutex {#mutex}

```cpp
mutex_type* mutex() const noexcept;
```

- 計算量: 定数

管理しているミューテックスへのポインタ。

### owns_lock {#owns_lock}

```cpp
bool owns_lock() const noexcept;
```

- 計算量: 定数

ロックを持っていれば `true`。`defer_lock` や `try_to_lock` で作ったときに確かめます。

### explicit operator bool {#op_bool}

```cpp
explicit operator bool() const noexcept;
```

- 計算量: 定数

`owns_lock()` と同じです。

### lock {#lock}

```cpp
void lock();
```

- 計算量: 待つ時間による

管理しているミューテックスをロックします。すでにロックを持っているときに呼ぶと、`std::system_error` です。`defer_lock` で作ったときに、あとからロックするのに使います。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::mutex m;
  std::unique_lock lock(m, std::defer_lock);  // まだロックしない
  std::println("{}", lock.owns_lock());
  lock.lock();
  std::println("{}", lock.owns_lock());
  lock.unlock();
}
```

```text title="実行結果"
false
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ワーカースレッドが、仕事が来るまで待つ | `std::unique_lock lock(m); cv.wait(lock, ...);` |

## よくあるミス

??? failure "lock_guard で足りるのに使う"
    条件変数も、途中の開け閉めも要らないなら、`lock_guard` のほうが軽くて意図が伝わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::lock_guard`](lock_guard.md) | 開け閉めしない |
| [`std::condition_variable`](condition_variable.md) | `unique_lock` が必要 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 開け閉めできる鍵
    - [x] 条件変数と使う
    - [x] 普段は lock_guard

## 関連ページ

- [cpprefjp: std::unique_lock](https://cpprefjp.github.io/reference/mutex/unique_lock.html)
- [cppreference: std::unique_lock](https://en.cppreference.com/w/cpp/thread/unique_lock)
