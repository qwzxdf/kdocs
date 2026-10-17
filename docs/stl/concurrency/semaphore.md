---
title: セマフォ・ラッチ・バリア
tags:
  - 並行処理
---

# セマフォ・ラッチ・バリア

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <semaphore>` / `#include <latch>` / `#include <barrier>`
</div>

C++20 で、スレッドどうしの待ち合わせに使う 3 つの道具が入りました。**セマフォ**は「同時に入れる人数を制限する入場券」、**ラッチ**は「決まった数の仕事が全部終わるまで待つ」ための使い捨てのカウンタ、**バリア**は「全員がそろったら次の段階へ進む」を何度も繰り返すための集合場所です。mutex と条件変数で自作していたものが、簡単に書けるようになりました。

!!! tip "ポイント"
    - 「同時に動くのは最大 N 個まで」→ `std::counting_semaphore<N>`。
    - 「N 個の仕事が全部終わるまで待つ」（1 回きり）→ `std::latch`。
    - 「毎フレーム、全員がそろってから次へ」（繰り返し）→ `std::barrier`。
    - 学生のゲームで必要になることは少ない。ジョブシステムを自作するときに。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 型一覧

| 型 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::latch`](#latch) | <span class="rank rank-rare">知ってるだけ</span> | カウンタが 0 になるまで待つ（1 回きり） |
| [`std::counting_semaphore`](#counting_semaphore) | <span class="rank rank-rare">知ってるだけ</span> | 同時に入れる数を制限する |
| [`std::binary_semaphore`](#binary_semaphore) | <span class="rank rank-rare">知ってるだけ</span> | 最大 1 のセマフォ（合図に使う） |
| [`std::barrier`](#barrier) | <span class="rank rank-rare">知ってるだけ</span> | 全員がそろうのを繰り返し待つ |

## 関数一覧

| 関数 | 対象 | 何をする |
| --- | --- | --- |
| [`count_down`](#count_down) | latch | カウンタを減らす |
| [`wait`](#latch-wait) | latch | 0 になるまで待つ |
| [`arrive_and_wait`](#latch-arrive_and_wait) | latch | 減らして、0 になるまで待つ |
| [`acquire`](#acquire) | semaphore | 入場券を 1 枚取る（無ければ待つ） |
| [`release`](#release) | semaphore | 入場券を返す |
| [`try_acquire`](#try_acquire) | semaphore | 取れなければすぐ諦める |
| [`arrive_and_wait`](#barrier-arrive_and_wait) | barrier | 到着して、全員がそろうまで待つ |
| [`arrive_and_drop`](#arrive_and_drop) | barrier | 到着して、以後の参加をやめる |

## 型と関数の詳しい説明

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

### std::binary_semaphore {#binary_semaphore}

```cpp
using binary_semaphore = std::counting_semaphore<1>;
```

- 入場券が最大 1 枚のセマフォ。「準備できた」の合図をスレッド間で送るのに使えます（mutex と違い、取ったスレッドと別のスレッドが返してもいい）

```cpp
#include <print>
#include <semaphore>
#include <thread>

int main() {
  std::binary_semaphore ready(0);  // 最初は 0（まだ準備できていない）
  std::jthread worker([&] {
    ready.acquire();  // 合図が来るまで待つ
    std::println("合図を受け取った");
  });
  ready.release();  // 合図を送る
}
```

```text title="実行結果"
合図を受け取った
```

### std::barrier {#barrier}

```cpp
template <class CompletionFunction = /* 何もしない */>
class barrier {
 public:
  explicit barrier(std::ptrdiff_t expected, CompletionFunction f = {});
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `expected` | `std::ptrdiff_t` | 参加するスレッドの数 |
| `f` | 関数 | 全員がそろったときに 1 回呼ばれる関数（フェーズの切り替え処理） |

- 全員が到着するたびに `f` が呼ばれ、また次の段階で使えます（latch と違って繰り返し使える）

### arrive_and_wait {#barrier-arrive_and_wait}

```cpp
void arrive_and_wait();
```

- 到着して、全員がそろうまで待ちます

### arrive_and_drop {#arrive_and_drop}

```cpp
void arrive_and_drop();
```

- 到着して、次の段階からは参加しないことにします（参加人数が 1 減る）

```cpp
#include <atomic>
#include <barrier>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::atomic<int> phases = 0;
  std::barrier sync(3, [&]() noexcept { ++phases; });  // 3 人そろうたびに呼ばれる

  {
    std::vector<std::jthread> workers;
    for (int t = 0; t < 3; ++t) {
      workers.emplace_back([&] {
        for (int frame = 0; frame < 4; ++frame) {
          // このフレームの自分の担当分を処理する
          sync.arrive_and_wait();  // 全員が終わるまで次のフレームへ進まない
        }
      });
    }
  }
  std::println("そろった回数: {}", phases.load());
}
```

```text title="実行結果"
そろった回数: 4
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 道具 |
| --- | --- |
| アセットを並列に読み込み、全部終わったらゲーム開始 | latch |
| 同時に開くファイル・同時の通信の数を制限 | counting_semaphore |
| 物理・AI・アニメーションを並列に計算し、毎フレーム全員の完了を待つ | barrier |

## よくあるミス

??? failure "latch を使い回そうとする"
    latch は 0 になったら終わりです。繰り返すなら barrier を使います。

??? failure "barrier の参加人数と実際のスレッド数が違う"
    参加人数が多すぎると永遠にそろわず、止まってしまいます。

## 理解度チェック

!!! question "Q1. 「毎フレーム、4 つのワーカーが担当分を計算し終わるまで描画を待つ」に向いているのは？"
    <div class="spoiler" markdown>

    **答え:** `std::barrier`。毎フレーム繰り返し待ち合わせるので、1 回きりの latch より向いています。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 人数制限はセマフォ、1 回きりの完了待ちはラッチ、繰り返しの待ち合わせはバリア

## 関連ページ

- [並行処理の基本](../../basics/concurrency.md)
- [cppreference: std::counting_semaphore](https://en.cppreference.com/w/cpp/thread/counting_semaphore)
- [cppreference: std::barrier](https://en.cppreference.com/w/cpp/thread/barrier)
