---
title: std::recursive_timed_mutex
summary: "同じスレッドで何度でもロックでき、時間切れも指定できるミューテックス。"
order: 900
tags:
  - 並行処理
---

# std::recursive_timed_mutex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`recursive_mutex`（同じスレッドが何度でもロックできる）と、`timed_mutex`（ロックの待ち時間を指定できる）を両方使えるようにしたものです。再帰的に呼ばれる関数の中でロックが必要で、かつ時間切れも指定したいという、まれな場面で使います。

!!! tip "ポイント"
    - 同じスレッドが何度でも `lock()` できる（解除も同じ回数）。
    - `try_lock_for`・`try_lock_until` で待ち時間を指定できる。
    - ふつうは設計を見直して、必要としない形にする。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::recursive_timed_mutex {#recursive_timed_mutex}

```cpp
class recursive_timed_mutex {
 public:
  void lock();
  bool try_lock();
  template <class Rep, class Period> bool try_lock_for(const std::chrono::duration<Rep, Period>& d);
  template <class Clock, class Duration> bool try_lock_until(const std::chrono::time_point<Clock, Duration>& t);
  void unlock();
};
```

- 戻り値: `try_lock_for` / `try_lock_until` はロックできたら `true`
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <chrono>
#include <mutex>
#include <print>

int main() {
  using namespace std::chrono_literals;
  std::recursive_timed_mutex m;
  m.lock();
  m.lock();  // 同じスレッドなので、もう一度ロックできる
  m.unlock();
  m.unlock();
  std::println("{}", m.try_lock_for(10ms));
  m.unlock();
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 再帰呼び出しの中で時間つきでロックする | `if (m.try_lock_for(10ms)) { ... m.unlock(); }` |

## よくあるミス

??? failure "ロックと同じ回数だけ解除しない"
    `lock()` を 2 回したら、`unlock()` も 2 回必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`recursive_mutex`](recursive_mutex.md) | 時間指定なし |
| [`timed_mutex`](timed_mutex.md) | 再帰なし |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 再帰ロック + 時間切れのミューテックス
    - [x] ロックした回数だけ解除する
    - [x] ふつうは別の設計にする

## 関連ページ

- [cpprefjp: std::recursive_timed_mutex](https://cpprefjp.github.io/reference/mutex/recursive_timed_mutex.html)
- [cppreference: std::recursive_timed_mutex](https://en.cppreference.com/w/cpp/thread/recursive_timed_mutex)
