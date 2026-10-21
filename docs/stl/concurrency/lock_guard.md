---
title: std::lock_guard
summary: "スコープの間だけ鍵をかけ、抜けるときに自動で開ける。"
order: 78
tags:
  - 並行処理
---

# std::lock_guard

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::lock_guard` は、**作った瞬間に mutex の鍵をかけて、スコープを抜けるときに自動で鍵を開ける**ための小さなクラスです。`lock()` / `unlock()` を直接呼ぶと、例外や `return` で開け忘れますが、`lock_guard` なら必ず開きます（RAII）。mutex を使うときの基本の形です。

!!! tip "ポイント"
    - 共有データを触る前に `std::lock_guard lock(mutex);` と 1 行書く。
    - 鍵をかけている間は短く。スコープを `{ }` で区切って、必要な部分だけにする。
    - 途中で開け閉めしたいなら [`unique_lock`](unique_lock.md)、複数の鍵を同時なら [`scoped_lock`](scoped_lock.md)。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::lock_guard {#lock_guard}

```cpp
template <class Mutex>
class lock_guard {
 public:
  explicit lock_guard(Mutex& m);  // ここで lock
  ~lock_guard();                  // ここで unlock
};
```

- 作ったときに鍵をかけ、スコープを抜けるときに自動で開けます。途中で return や例外があっても必ず開きます

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>
#include <thread>

int main() {
  int counter = 0;
  std::mutex m;
  auto work = [&] {
    for (int i = 0; i < 1000; ++i) {
      std::lock_guard lock(m);  // スコープの間だけ鍵をかける
      ++counter;
    }
  };
  std::thread a(work);
  std::thread b(work);
  a.join();
  b.join();
  std::println("{}", counter);
}
```

```text title="実行結果"
2000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 共有ログに書き込む | `std::lock_guard lock(log_mutex_);` |
| ゲームの状態をスレッド間で共有する | 読み書きの前に `lock_guard` |

## よくあるミス

??? failure "ロックを変数にせず、一時オブジェクトにする"
    `std::lock_guard<std::mutex>(m);` は名前がないので、その行でロックが開きます。必ず `lock` のように名前を付けます。

??? failure "ロックしたまま重い処理をする"
    ファイル読み込みなどをロックの中で行うと、ほかのスレッドが待たされます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::scoped_lock`](scoped_lock.md) | 複数の鍵をまとめてかける |
| [`std::unique_lock`](unique_lock.md) | 開け閉めできる |
| [`std::mutex`](mutex.md) | 鍵そのもの |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 鍵をかけて、抜けるときに自動で開ける
    - [x] RAII で開け忘れない
    - [x] `lock` と名前を付ける

## 関連ページ

- [cpprefjp: std::lock_guard](https://cpprefjp.github.io/reference/mutex/lock_guard.html)
- [cppreference: std::lock_guard](https://en.cppreference.com/w/cpp/thread/lock_guard)
