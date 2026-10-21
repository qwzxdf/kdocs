---
title: std::barrier
summary: "全員がそろうのを待つ。何度でも繰り返し使える。"
order: 98
tags:
  - 並行処理
---

# std::barrier

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-20">C++20</span>
`#include <barrier>`
</div>

`std::barrier` は、**参加者全員が「ここまで来た」とそろうまで、全員を待たせる**道具です。[`latch`](latch.md) と違い、**そろったら自動でカウンタが戻り、何度でも使えます**。「全スレッドが今のフレームの更新を終えてから、次の段階に進む」という同期に向きます。

!!! tip "ポイント"
    - `std::barrier sync(スレッド数);` で作り、各スレッドが `arrive_and_wait()`。
    - 全員がそろうと、一斉に再開してカウンタが戻る。
    - 完了時に実行する関数（completion function）も渡せる。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 物理 → AI → 描画の段階を、全スレッドで揃えて進める | 各段階の終わりで `barrier.arrive_and_wait()` |

## よくあるミス

??? failure "参加者の数を間違える"
    数が合わないと、全員がそろわず永遠に待ちます。途中で抜けるスレッドは `arrive_and_drop()` で抜けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::latch`](latch.md) | 1 回きり |
| [`std::counting_semaphore`](counting_semaphore.md) | 入れる数を制限 |

## コンパイラ対応

C++20 の機能です。GCC 11 / Clang 16 / MSVC 19.28 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全員がそろうまで待つ
    - [x] 繰り返し使える
    - [x] 抜けるなら `arrive_and_drop`

## 関連ページ

- [cpprefjp: std::barrier](https://cpprefjp.github.io/reference/barrier/barrier.html)
- [cppreference: std::barrier](https://en.cppreference.com/w/cpp/thread/barrier)
