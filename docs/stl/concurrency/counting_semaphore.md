---
title: std::counting_semaphore
summary: "同時に入れる数を制限する入場券。"
order: 96
tags:
  - 並行処理
---

# std::counting_semaphore

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-20">C++20</span>
`#include <semaphore>`
</div>

`std::counting_semaphore` は、**「同時に N 人まで」と、入れる数を制限する**道具です。入場券が N 枚あり、`acquire()` で 1 枚取り（無ければ待つ）、`release()` で返します。「同時に読み込むファイルを 3 つまでにする」「ワーカーに仕事の数を知らせる」といった使い方があります。

!!! tip "ポイント"
    - `std::counting_semaphore<8> sem(3);` は、最大 8 枚、今は 3 枚。
    - `acquire()` で 1 枚減らし、`release()` で 1 枚増やす。
    - 最大が 1 でよいなら [`binary_semaphore`](binary_semaphore.md)。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::counting_semaphore {#counting_semaphore}

```cpp
template <std::ptrdiff_t LeastMaxValue = /* 実装による */>
class counting_semaphore {
 public:
  explicit counting_semaphore(std::ptrdiff_t desired);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `LeastMaxValue` | テンプレート引数 | 入場券の最大数 |
| `desired` | `std::ptrdiff_t` | 最初に使える入場券の数 |

### acquire {#acquire}

```cpp
void acquire();
```

- 入場券を 1 枚取ります。残りが 0 なら、誰かが返すまで待ちます

### release {#release}

```cpp
void release(std::ptrdiff_t update = 1);
```

- 入場券を返します

### try_acquire {#try_acquire}

```cpp
bool try_acquire() noexcept;
```

- 入場券を取れたら `true`、残りが無ければ待たずに `false`

```cpp
#include <atomic>
#include <print>
#include <semaphore>
#include <thread>
#include <vector>

int main() {
  std::counting_semaphore<2> slots(2);  // 同時に読み込めるのは 2 つまで
  std::atomic<int> running = 0;
  std::atomic<int> max_running = 0;

  {
    std::vector<std::jthread> jobs;
    for (int i = 0; i < 6; ++i) {
      jobs.emplace_back([&] {
        slots.acquire();
        int now = ++running;
        int prev = max_running.load();
        while (now > prev && !max_running.compare_exchange_weak(prev, now)) {
        }
        --running;
        slots.release();
      });
    }
  }
  std::println("同時に動いたのは最大 2 以下？ {}", max_running.load() <= 2);
  std::println("空き無しで try_acquire: {}", [] {
    std::counting_semaphore<1> s(0);
    return s.try_acquire();
  }());
}
```

```text title="実行結果"
同時に動いたのは最大 2 以下？ true
空き無しで try_acquire: false
```

### try_acquire_for {#try_acquire_for}

```cpp
template <class Rep, class Period>
bool try_acquire_for(const std::chrono::duration<Rep, Period>& rel_time);
```

- 計算量: 最大で指定時間

指定した時間まで待って、取得を試みます。取れたら `true`。

### try_acquire_until {#try_acquire_until}

```cpp
template <class Clock, class Duration>
bool try_acquire_until(const std::chrono::time_point<Clock, Duration>& abs_time);
```

- 計算量: 最大で指定時刻まで

指定した時刻まで待って、取得を試みます。取れたら `true`。

### max {#max}

```cpp
static constexpr ptrdiff_t max() noexcept;
```

- 計算量: 定数

カウンタの最大値。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同時に読み込むテクスチャを 3 つまでに制限する | `sem.acquire(); ...; sem.release();` |
| ワーカーに「仕事が N 個ある」と知らせる | `sem.release(n)` |

## よくあるミス

??? failure "release を忘れる"
    例外で `acquire` と `release` の間を抜けると、券が戻りません。RAII のラッパーを作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::binary_semaphore`](binary_semaphore.md) | 最大 1 枚 |
| [`std::mutex`](mutex.md) | 同時に 1 人だけ |

## コンパイラ対応

C++20 の機能です。GCC 11 / Clang 16 / MSVC 19.28 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同時に N 人まで入れる
    - [x] `acquire` で取り、`release` で返す
    - [x] 最大が 1 なら binary_semaphore

## 関連ページ

- [cpprefjp: std::counting_semaphore](https://cpprefjp.github.io/reference/semaphore/counting_semaphore.html)
- [cppreference: std::counting_semaphore](https://en.cppreference.com/w/cpp/thread/counting_semaphore)
