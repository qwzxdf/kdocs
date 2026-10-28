---
title: std::promise
summary: "結果を、別のスレッドへ渡すための「約束」。書き込む側を自分で持つ。"
order: 91
tags:
  - 並行処理
---

# std::promise

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::promise` は、<strong>別のスレッドに結果（または例外）を渡すための「書き込み口」</strong>です。`promise` から取り出した [`future`](future.md) を相手に渡し、自分は好きなタイミングで `set_value()` を呼びます。`std::async` が関数の戻り値を自動で渡すのに対し、こちらは**自分で結果を渡す時点を決められます**。

!!! tip "ポイント"
    - `std::promise<int> p; std::future<int> f = p.get_future();` の 2 つがセット。
    - 結果を書くのは `set_value()`、例外なら `set_exception()`。
    - 書かずに `promise` を破棄すると、`future` 側に例外が飛ぶ。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::promise {#promise}

```cpp
template <class T>
class promise {
 public:
  std::future<T> get_future();
  void set_value(T value);
  void set_exception(std::exception_ptr p);
};
```

- 「結果を書く側」を自分で持ちます。async で表せない形（スレッドの途中で結果を渡す、など）で使います

### get_future {#get_future}

```cpp
std::future<T> get_future();
```

- 計算量: 定数

この `promise` と結びついた `future` を返します。**1 回だけ**呼べます。2 回呼ぶと `future_error` です。

### set_value {#set_value}

```cpp
void set_value(const T& value);
void set_value(T&& value);
```

- 計算量: 定数

結果の値を設定します。待っている `future::get()` が、これで戻ります。2 回設定すると `future_error` です。

### set_exception {#set_exception}

```cpp
void set_exception(std::exception_ptr p);
```

- 計算量: 定数

値の代わりに、例外を設定します。`future::get()` がこの例外を投げ直します。

### set_value_at_thread_exit {#set_value_at_thread_exit}

```cpp
void set_value_at_thread_exit(const T& value);
```

- 計算量: 定数

値を設定しますが、結果が見えるようになるのは、スレッドが完全に終わってからです（`thread_local` の後始末のあと）。

### set_exception_at_thread_exit {#set_exception_at_thread_exit}

```cpp
void set_exception_at_thread_exit(std::exception_ptr p);
```

- 計算量: 定数

例外を設定しますが、結果が見えるようになるのは、スレッドが完全に終わってからです。

### swap {#swap}

```cpp
void swap(promise& other) noexcept;
```

- 計算量: 定数

2 つの `promise` を入れ替えます。

## 実際に動かしてみる

```cpp
#include <future>
#include <print>
#include <thread>

int main() {
  std::promise<int> p;
  std::future<int> f = p.get_future();
  std::thread t([&p] { p.set_value(7); });   // 別のスレッドが結果を書き込む
  std::println("{}", f.get());
  t.join();
}
```

```text title="実行結果"
7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ロード完了を別のスレッドへ通知する | `promise.set_value(handle)` |
| コールバック形式のAPIを future にする | コールバックの中で `set_value` |

## よくあるミス

??? failure "set_value を 2 回呼ぶ"
    2 回目は例外（`future_error`）になります。結果は一度だけです。

??? failure "get_future を 2 回呼ぶ"
    同じく例外です。`future` は 1 つだけ取り出せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::future`](future.md) | 受け取る側 |
| [`std::async`](async.md) | 関数の戻り値を自動で渡す |
| [`std::packaged_task`](packaged_task.md) | 関数と future をセットにした |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 結果を渡す書き込み口
    - [x] `get_future()` で受け取る側を作る
    - [x] `set_value()` は一度だけ

## 関連ページ

- [cpprefjp: std::promise](https://cpprefjp.github.io/reference/future/promise.html)
- [cppreference: std::promise](https://en.cppreference.com/w/cpp/thread/promise)
