---
title: std::call_once
summary: "何回呼ばれても、初期化を 1 回だけ実行する。"
order: 84
tags:
  - 並行処理
---

# std::call_once

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

複数のスレッドが、同じ初期化処理を同時に呼ぶことがあります。`std::call_once(flag, f, args...)` は、同じ `flag` に対して、`f` が 1 回だけ実行されることを保証します。他のスレッドは、実行中の `f` の完了を待ってから、先へ進みます。

!!! tip "ポイント"
    - `flag` ごとに、`f` が 1 回だけ実行される
    - 他のスレッドは、`f` が終わるまで待つ
    - `f` が例外を投げたら、実行済みにならず、次の呼び出しが再実行する
    - 実行後の呼び出しは軽い

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::call_once {#call_once}

<span class="ver ver-11">C++11</span>

```cpp
template <class Callable, class... Args>
void call_once(std::once_flag& flag, Callable&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `flag` | `std::once_flag&` | 実行済みを覚える印 |
| `f` | 呼び出し可能なもの | 1 回だけ実行する関数 |
| `args` | 任意 | `f` に渡す引数 |

`f` の実行が終わると、その中の書き込みは、すべてのスレッドから見えるようになります（同期が保証されます）。

`f` の中で、同じ `flag` に `call_once` を再帰的に呼ぶと、デッドロックします。

`static` 変数のローカル初期化のほうが簡潔で、同じ保証があります。`call_once` は、クラスのメンバーなど、`static` にできない場面で使います。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>
#include <string>
#include <thread>

class Config {
 public:
  const std::string& Get() {
    std::call_once(flag_, [this] { value_ = "loaded"; ++loads_; });
    return value_;
  }
  int loads() const { return loads_; }

 private:
  std::once_flag flag_;
  std::string value_;
  int loads_ = 0;
};

int main() {
  Config c;
  std::thread t1([&] { c.Get(); });
  std::thread t2([&] { c.Get(); });
  t1.join();
  t2.join();

  std::println("{} 読み込み回数 {}", c.Get(), c.loads());
}
```

```text title="実行結果"
loaded 読み込み回数 1
```

## ゲームでの使いどころ

設定ファイルの遅延読み込みなど、最初に使われたときに 1 回だけ行う処理に使います。

## よくあるミス

??? failure "f の中で例外が出るのを考えない"
    実行済みにならず、次の呼び出しで再実行されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`once_flag`](once_flag.md) | 実行済みの印 |
| [`mutex`](mutex.md) | 毎回ロックする |
| `static` 変数 | 関数内の簡単な遅延初期化 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::call_once](https://cpprefjp.github.io/reference/mutex/call_once.html)
- [cppreference: std::call_once](https://en.cppreference.com/w/cpp/thread/call_once)
