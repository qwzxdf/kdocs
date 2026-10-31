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

`recursive_mutex` は、同じスレッドが何度でもロックできるミューテックスです。`recursive_timed_mutex` は、さらに、時間を指定したロックの試み（`try_lock_for`）ができます。再帰ロックと時間指定の両方が要る、まれな場面のためのものです。

!!! tip "ポイント"
    - 同じスレッドが何度でもロックできる（ロックした数だけ `unlock` が要る）
    - `try_lock_for` / `try_lock_until` で、時間切れを指定できる
    - 他のスレッドは、持ち主が全部 `unlock` するまで取れない
    - 設計を見直して、再帰ロックを避けるのが望ましい

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::recursive_timed_mutex {#recursive_timed_mutex}

<span class="ver ver-11">C++11</span>

```cpp
class recursive_timed_mutex {
 public:
  void lock();
  bool try_lock();
  template <class Rep, class Period>
  bool try_lock_for(const std::chrono::duration<Rep, Period>& d);
  template <class Clock, class Duration>
  bool try_lock_until(const std::chrono::time_point<Clock, Duration>& t);
  void unlock();
};
```

内部にロック回数を数えるカウンターを持ち、同じスレッドが `lock` するたびに増やします。`unlock` で減らし、0 になったときに、ほかのスレッドが取れるようになります。

再帰ロックは、関数が互いを呼び合う構造で、どの関数でもロックが必要なときに便利ですが、ロックの範囲が曖昧になります。外側の関数でロックし、内側の関数はロックしない版を用意する設計のほうが、読みやすくなります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <mutex>
#include <print>
#include <thread>

int main() {
  using namespace std::chrono_literals;
  std::recursive_timed_mutex m;

  m.lock();
  m.lock();  // 同じスレッドは、何度でも取れる
  std::println("2 回ロックした");

  bool other = true;
  std::thread t([&] { other = m.try_lock_for(10ms); });
  t.join();
  std::println("別スレッドで取れた: {}", other);

  m.unlock();
  m.unlock();  // ロックした数だけ必要

  std::thread t2([&] {
    other = m.try_lock_for(10ms);
    if (other) m.unlock();
  });
  t2.join();
  std::println("全部解放後に取れた: {}", other);
}
```

```text title="実行結果"
2 回ロックした
別スレッドで取れた: false
全部解放後に取れた: true
```

## ゲームでの使いどころ

再帰ロックと時間指定が両方要る場面は、まれです。設計の見直しを先に考えます。

## よくあるミス

??? failure "unlock の回数が足りない"
    他のスレッドが取れないままになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`recursive_mutex`](recursive_mutex.md) | 時間指定のない版 |
| [`timed_mutex`](timed_mutex.md) | 再帰しない版 |
| [`mutex`](mutex.md) | 基本のミューテックス |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::recursive_timed_mutex](https://cpprefjp.github.io/reference/mutex/recursive_timed_mutex.html)
- [cppreference: std::recursive_timed_mutex](https://en.cppreference.com/w/cpp/thread/recursive_timed_mutex)
