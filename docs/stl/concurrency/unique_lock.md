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
