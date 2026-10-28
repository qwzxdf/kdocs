---
title: std::shared_future
summary: "複数の場所から、同じ結果を受け取れる future。"
order: 92
tags:
  - 並行処理
---

# std::shared_future

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::shared_future` は、**同じ結果を複数のスレッド・場所から受け取れる `future`** です。普通の `std::future` は `get()` を一度しか呼べませんが、`shared_future` は何度でも、何人でも `get()` できます。「ロードが終わったら、全員が結果を使う」という場面に向きます。

!!! tip "ポイント"
    - `std::future` から `.share()` で作る。
    - `get()` は const 参照を返す。何度呼んでもよい。
    - コピーできる。各スレッドにコピーを渡す。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::shared_future {#shared_future}

```cpp
template <class T>
class shared_future;
```

- コピーでき、複数の場所から `get()` できる future。`future.share()` で作ります

### get {#get}

```cpp
const T& get() const;
```

- 計算量: 結果が出るまで待つ

結果への参照を返します。結果が出るまで待ち、**何回呼んでも**同じ結果を返します（`future::get` は 1 回だけ）。

### valid {#valid}

```cpp
bool valid() const noexcept;
```

- 計算量: 定数

結果を受け取れる状態なら `true`。

### wait {#wait}

```cpp
void wait() const;
```

- 計算量: 結果が出るまで待つ

結果が出るまで待ちます。

### wait_for {#wait_for}

```cpp
template <class Rep, class Period>
future_status wait_for(const std::chrono::duration<Rep, Period>& rel_time) const;
```

- 計算量: 最大で指定時間

指定した時間まで、結果が出るのを待ちます。

### wait_until {#wait_until}

```cpp
template <class Clock, class Duration>
future_status wait_until(const std::chrono::time_point<Clock, Duration>& abs_time) const;
```

- 計算量: 最大で指定時刻まで

指定した時刻まで、結果が出るのを待ちます。

## 実際に動かしてみる

```cpp
#include <future>
#include <print>

int main() {
  std::shared_future<int> sf = std::async(std::launch::async, [] { return 5; }).share();
  std::println("{} {}", sf.get(), sf.get());   // 何度でも受け取れる
}
```

```text title="実行結果"
5 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 つのロード結果を描画・物理・AI の全スレッドで使う | `std::shared_future<Assets> assets = loader.share();` |

## よくあるミス

??? failure "結果を書き換えようとする"
    `get()` が返すのは const 参照です。書き換えるなら、自分でコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::future`](future.md) | 1 回しか受け取れない |
| [`std::promise`](promise.md) | 結果を渡す側 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ結果を何人でも受け取れる
    - [x] `future.share()` で作る
    - [x] コピーできる

## 関連ページ

- [cpprefjp: std::shared_future](https://cpprefjp.github.io/reference/future/shared_future.html)
- [cppreference: std::shared_future](https://en.cppreference.com/w/cpp/thread/shared_future)
