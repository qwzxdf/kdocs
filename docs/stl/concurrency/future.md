---
title: std::future
summary: "別のスレッドの結果を、あとで受け取る。"
order: 94
tags:
  - 並行処理
---

# std::future

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

別のスレッドに投げた計算の結果をあとで受け取りたい。結果を入れる変数を共有して、終わったかのフラグも作って、と自分で書くと、データ競合の危険があります。`std::future` は、まだ出ていない結果をあとで受け取るための引換券です。`std::async` や `std::promise` から取り出せます。`get()` で結果を受け取り（終わるまで待つ）、`wait_for()` で終わったかを確かめます。

!!! tip "ポイント"
    - `get()` は**一度しか呼べない**（結果を受け取ると、`future` は空になる）。
    - ロード画面では `wait_for(0ms)` で「終わったか」を毎フレーム確かめる。
    - 複数の場所で受け取るなら [`shared_future`](shared_future.md)。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### get {#get}

```cpp
T get();
```

- 結果を受け取ります。まだ終わっていなければ終わるまで待ちます
- **1 回しか呼べません**（2 回目は未定義動作 / 例外）。呼んだあと `valid()` は false になります
- 関数の中で例外が投げられていたら、ここで投げ直されます

```cpp
#include <future>
#include <print>
#include <stdexcept>

int main() {
  auto f = std::async(std::launch::async, [] () -> int {
    throw std::runtime_error("ファイルが無い");
  });
  try {
    f.get();
  } catch (const std::exception& e) {
    std::println("受け取った例外: {}", e.what());
  }
}
```

```text title="実行結果"
受け取った例外: ファイルが無い
```

### wait_for {#wait_for}

```cpp
template <class Rep, class Period>
std::future_status wait_for(const std::chrono::duration<Rep, Period>& timeout) const;
```

- 最大 `timeout` だけ待って、状態を返します。`0s` を渡すと待たずに「今終わっているか」だけ調べられます

| 戻り値 | 意味 |
| --- | --- |
| `std::future_status::ready` | 終わっている（`get()` してすぐ受け取れる） |
| `std::future_status::timeout` | まだ終わっていない |
| `std::future_status::deferred` | `std::launch::deferred` で、まだ始まってもいない |

### valid {#valid}

```cpp
bool valid() const noexcept;
```

- まだ結果を受け取れる状態か。`get()` したあとや、何も入っていない future では `false`

### wait {#wait}

```cpp
void wait() const;
```

- 終わるまで待ちます（結果は受け取らない）

```cpp
#include <future>
#include <print>

int main() {
  std::future<int> f = std::async(std::launch::async, [] { return 7; });
  f.wait();
  bool before = f.valid();
  int value = f.get();
  std::println("valid {} / 値 {} / valid {}", before, value, f.valid());
}
```

```text title="実行結果"
valid true / 値 7 / valid false
```

### wait_until {#wait_until}

```cpp
template <class Clock, class Duration>
future_status wait_until(const std::chrono::time_point<Clock, Duration>& abs_time) const;
```

- 計算量: 最大で指定時刻まで

指定した時刻まで、結果が出るのを待ちます。結果が出たか、時間切れかを `future_status` で返します。

### share {#share}

```cpp
std::shared_future<T> share() noexcept;
```

- 計算量: 定数

`future` を `shared_future` に変換します。変換後の元の `future` は無効（`valid()` が偽）になります。結果を複数のスレッドで読みたいときに使います。

## ゲームでの使いどころ

ロード画面で、`wait_for(0ms)` を毎フレーム呼び、`ready` なら次の画面へ進みます。`get()` を直接呼ぶと、終わるまで画面が固まります。

`get()` は一度しか呼べません。結果を受け取ると、`future` は空になります。複数の場所で結果を使うなら、`shared_future` に変換します。

例外も運ばれます。別スレッドで例外が投げられると、`get()` を呼んだときに再び投げられます。受け取る側で `try` を用意します。

## よくあるミス

??? failure "get を 2 回呼ぶ"
    2 回目は例外です。`valid()` で確かめるか、`shared_future` にします。

??? failure "メインスレッドで get して固まる"
    まだ終わっていない `future` の `get()` は、終わるまで待ちます。画面が止まるので、`wait_for` で確かめてから呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::async`](async.md) | future の作り手 |
| [`std::shared_future`](shared_future.md) | 何度でも・何人でも |
| [`std::promise`](promise.md) | 書き込む側 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 結果の引換券
    - [x] `get()` は一度だけ
    - [x] `wait_for(0ms)` で終わったか確かめる

## 関連ページ

- [cpprefjp: std::future](https://cpprefjp.github.io/reference/future/future.html)
- [cppreference: std::future](https://en.cppreference.com/w/cpp/thread/future)
