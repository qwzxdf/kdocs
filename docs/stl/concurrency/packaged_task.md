---
title: std::packaged_task
summary: "関数と future をセットにしたもの。自前のスレッドプールに便利。"
order: 93
tags:
  - 並行処理
---

# std::packaged_task

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::packaged_task` は、**関数と、その戻り値を受け取る `future` をセットにしたもの**です。呼び出すと関数を実行して、結果を `future` に入れます。自作のスレッドプールで、「キューに仕事を入れて、結果を `future` で受け取る」仕組みを作るのに使います。

!!! tip "ポイント"
    - `std::packaged_task<int()> task(関数);` → `task.get_future()` → `task()` で実行。
    - `task` はコピーできず、ムーブだけ。キューに入れるには `std::move`。
    - `std::async` は、これを自動でやってくれる。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::packaged_task {#packaged_task}

```cpp
template <class R, class... Args>
class packaged_task<R(Args...)>;
```

- 関数と、その結果を受け取る future をセットにしたもの。仕事をキューに入れて、別のスレッドで実行する仕組み（スレッドプール）を自作するときに使います

```cpp
#include <future>
#include <print>
#include <thread>
#include <utility>

int main() {
  std::promise<int> promise;
  std::shared_future<int> result = promise.get_future().share();
  std::jthread worker([&promise] { promise.set_value(42); });
  std::println("{} {}", result.get(), result.get());  // shared_future は何度でも get できる

  std::packaged_task<int(int)> task([](int x) { return x * 2; });
  std::future<int> f = task.get_future();
  std::jthread runner(std::move(task), 21);
  std::println("{}", f.get());
}
```

```text title="実行結果"
42 42
42
```

### operator() {#op_call}

```cpp
void operator()(Args... args);
```

- 計算量: 関数による

関数を呼んで、結果を `future` に設定します。例外が出たら、それが `future` に設定されます。

### get_future {#get_future}

```cpp
std::future<R> get_future();
```

- 計算量: 定数

結果を受け取る `future` を返します。**1 回だけ**呼べます。

### valid {#valid}

```cpp
bool valid() const noexcept;
```

- 計算量: 定数

関数を持っていれば `true`。

### make_ready_at_thread_exit {#make_ready_at_thread_exit}

```cpp
void make_ready_at_thread_exit(Args... args);
```

- 計算量: 関数による

関数を呼びますが、結果が見えるようになるのは、スレッドが完全に終わってからです。

### reset {#reset}

```cpp
void reset();
```

- 計算量: 定数

状態を捨てて、同じ関数で新しい状態を作ります。もう一度 `operator()` を呼べるようになります。

### swap {#swap}

```cpp
void swap(packaged_task& other) noexcept;
```

- 計算量: 定数

2 つの `packaged_task` を入れ替えます。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作のジョブシステムで、仕事と結果をセットにして投げる | `std::packaged_task<void()>` をキューに積む |

## よくあるミス

??? failure "task をコピーしようとする"
    コピーできません。`std::move` でキューに渡します。`std::function` に入れるときも注意が必要です（C++23 の `move_only_function` を使う）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::async`](async.md) | 自動でスレッドを選ぶ |
| [`std::promise`](promise.md) | 結果を自分で渡す |
| [`std::move_only_function`](../utilities/move_only_function.md) | ムーブだけの関数を持つ型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 関数と future をセットにする
    - [x] 呼ぶと実行されて future に結果が入る
    - [x] コピー不可

## 関連ページ

- [cpprefjp: std::packaged_task](https://cpprefjp.github.io/reference/future/packaged_task.html)
- [cppreference: std::packaged_task](https://en.cppreference.com/w/cpp/thread/packaged_task)
