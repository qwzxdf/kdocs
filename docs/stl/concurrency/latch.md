---
title: std::latch
summary: "カウンタが 0 になるまで待つ、1 回きりの待ち合わせ。"
order: 95
tags:
  - 並行処理
---

# std::latch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-20">C++20</span>
`#include <latch>`
</div>

`std::latch` は、**カウンタが 0 になるまで、スレッドを待たせる**道具です。「N 個の仕事がすべて終わるまで待つ」ときに使います。カウンタを 0 にしたら、もう元に戻せません（1 回きり）。繰り返し使うなら [`barrier`](barrier.md)。

!!! tip "ポイント"
    - `std::latch l(3);` で、3 回の `count_down()` を待つ。
    - 仕事が終わるたびに `count_down()`。待つ側は `wait()`。
    - 1 回きり。使い回せない。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::latch {#latch}

```cpp
class latch {
 public:
  explicit latch(std::ptrdiff_t expected);
};
```

- 最初に数を決め、0 になるまで待てるカウンタ。0 になったら終わり（再利用できない）

### count_down {#count_down}

```cpp
void count_down(std::ptrdiff_t n = 1);
```

- カウンタを `n` 減らします。仕事が 1 つ終わるたびに呼びます

### wait {#latch-wait}

```cpp
void wait() const;
```

- カウンタが 0 になるまで待ちます

### arrive_and_wait {#latch-arrive_and_wait}

```cpp
void arrive_and_wait(std::ptrdiff_t n = 1);
```

- `count_down(n)` してから `wait()` します

```cpp
#include <atomic>
#include <latch>
#include <print>
#include <thread>
#include <vector>

int main() {
  constexpr int kAssets = 4;
  std::latch loaded(kAssets);
  std::atomic<int> count = 0;

  std::vector<std::jthread> loaders;
  for (int i = 0; i < kAssets; ++i) {
    loaders.emplace_back([&] {
      ++count;              // 1 つ読み込んだ
      loaded.count_down();  // 終わったことを知らせる
    });
  }
  loaded.wait();  // 4 つ全部終わるまで待つ
  std::println("全部読み込んだ: {}", count.load());
}
```

```text title="実行結果"
全部読み込んだ: 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ロードを 4 つのスレッドで分担し、全部終わったらゲーム開始 | `std::latch done(4);` |
| 全員の準備ができるまで、開始の号砲を待つ | `start.wait()` |

## よくあるミス

??? failure "count_down が足りず永遠に待つ"
    例外が起きたスレッドが `count_down` を呼ばないと、待つ側が永遠に待ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::barrier`](barrier.md) | 繰り返し使える |
| [`std::counting_semaphore`](counting_semaphore.md) | 同時に入れる数を制限する |

## コンパイラ対応

C++20 の機能です。GCC 11 / Clang 16 / MSVC 19.28 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カウンタが 0 になるまで待つ
    - [x] 1 回きり
    - [x] 繰り返すなら barrier

## 関連ページ

- [cpprefjp: std::latch](https://cpprefjp.github.io/reference/latch/latch.html)
- [cppreference: std::latch](https://en.cppreference.com/w/cpp/thread/latch)
