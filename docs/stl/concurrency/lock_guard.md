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

mutex の `lock()` と `unlock()` を自分で呼ぶと、途中で `return` したり、例外が飛んだりしたときに、`unlock()` を呼び忘れます。鍵が開かないまま、他のスレッドが永遠に待ちます。`std::lock_guard` は、作った瞬間に mutex の鍵をかけ、スコープを抜けるときに自動で鍵を開ける小さなクラスです。どの経路で抜けても、必ず開きます。

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

共有データを触る前に、`std::lock_guard lock(mutex_);` と 1 行書きます。ログの出力、タスクキューへの追加、共有カウンターの更新など、短い区間を守るのが定番です。

鍵をかけている間は、他のスレッドが待たされます。必要な部分だけを `{ }` で区切り、重い処理は鍵の外に出します。

途中で開け閉めしたいなら `unique_lock`、複数の mutex を同時にかけるなら `scoped_lock` を使います。C++17 以降は、`scoped_lock` を mutex 1 つにも使えます。

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
