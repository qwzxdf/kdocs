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

`std::future` の `get()` は、1 回しか呼べず、結果を取り出すと空になります。複数のスレッドが、同じ結果を待ち、それぞれ読みたいなら、コピーできて、何度でも `get()` できる `std::shared_future` を使います。`future::share()` で作れます。

!!! tip "ポイント"
    - コピーできる。複数のスレッドが、それぞれ持てる
    - `get()` を何度でも呼べ、結果は const 参照で返る
    - `future::share()` で作る
    - 結果が出るまで、全員が待つ

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::shared_future {#shared_future}

<span class="ver ver-11">C++11</span>

```cpp
template <class T> class shared_future {
 public:
  shared_future(const shared_future&);
  const T& get() const;
  void wait() const;
  template <class Rep, class Period>
  std::future_status wait_for(const std::chrono::duration<Rep, Period>&) const;
};
```

`get()` は、`std::future` と違い `const T&` を返します。値を移動して取り出せないので、複数のスレッドが同じ値を読めます。

各スレッドは、自分のコピーを持ちます。1 つのオブジェクトを複数のスレッドから同時に触るのではなく、スレッドごとにコピーして使うのが、安全な使い方です。同じ `shared_future` オブジェクトを複数のスレッドが同時に触ると、データ競合です。

`std::promise` の `get_future().share()` で作るのが定番です。

## 実際に動かしてみる

```cpp
#include <future>
#include <print>
#include <thread>

int main() {
  std::promise<int> p;
  std::shared_future<int> sf = p.get_future().share();

  int r1 = 0;
  int r2 = 0;
  // それぞれのスレッドが、自分のコピーを持つ
  std::thread t1([sf, &r1] { r1 = sf.get(); });
  std::thread t2([sf, &r2] { r2 = sf.get(); });

  p.set_value(42);
  t1.join();
  t2.join();

  std::println("{} {}", r1, r2);
  std::println("何度でも読める: {} {}", sf.get(), sf.get());
}
```

```text title="実行結果"
42 42
何度でも読める: 42 42
```

## ゲームでの使いどころ

読み込み完了を、複数のシステム（描画、音、AI）が待つとき、1 つの結果を共有します。

## よくあるミス

??? failure "同じオブジェクトを複数のスレッドで触る"
    データ競合です。スレッドごとにコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future`](future.md) | 1 回しか読めない |
| [`promise`](promise.md) | 値を設定する |
| [`latch`](latch.md) | 回数の合図 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::shared_future](https://cpprefjp.github.io/reference/future/shared_future.html)
- [cppreference: std::shared_future](https://en.cppreference.com/w/cpp/thread/shared_future)
