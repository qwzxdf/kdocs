---
title: std::future_error
summary: "future / promise の使い方を間違えたときの例外。"
order: 900
tags:
  - 並行処理
---

# std::future_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::future` や `std::promise` の使い方を間違えると、`std::future_error` が投げられます。`std::logic_error` の派生クラスで、`code()` で、原因を `std::error_code` として取れます。原因は `std::future_errc` の値と比べて判定します。

!!! tip "ポイント"
    - `promise` / `future` の使い方の誤りを知らせる例外
    - `code()` で原因を取り、`future_errc` と比べる
    - `std::logic_error` の派生クラス
    - ワーカーの例外は、`future::get()` で再送出される（これは `future_error` ではない）

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::future_error {#future_error}

<span class="ver ver-11">C++11</span>

```cpp
class future_error : public std::logic_error {
 public:
  const std::error_code& code() const noexcept;
  const char* what() const noexcept override;
};
```

プログラムの誤りを示す例外です。`broken_promise` のように、実行中に起きうるものもあります。

ワーカー スレッドが投げた別の例外は、`future::get()` で、元の例外のまま再送出されます。`future_error` とは区別されます。

`what()` のメッセージは、実装ごとに違います。判定には使わず、`code()` で調べます。

## 実際に動かしてみる

```cpp
#include <future>
#include <print>
#include <stdexcept>

int main() {
  // 共有状態のない future を使う
  std::future<int> f;
  try {
    f.get();
  } catch (const std::future_error& e) {
    std::println("no_state: {}", e.code() == std::future_errc::no_state);
  }

  // 親クラスの logic_error でも捕まえられる
  try {
    std::promise<int> p;
    p.get_future();
    p.get_future();
  } catch (const std::logic_error&) {
    std::println("logic_error としても捕まえられる");
  }

  // ワーカーの例外は、元の型で再送出される
  auto g = std::async(std::launch::async, []() -> int { throw std::runtime_error("failed"); });
  try {
    g.get();
  } catch (const std::runtime_error&) {
    std::println("runtime_error がそのまま出た");
  }
}
```

```text title="実行結果"
no_state: true
logic_error としても捕まえられる
runtime_error がそのまま出た
```

## ゲームでの使いどころ

`promise` を使う自作の非同期処理で、誤用を検出して、ログに残します。

## よくあるミス

??? failure "ワーカーの例外も future_error だと思う"
    元の例外型で出ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future_errc`](future_errc.md) | エラー コード |
| [`promise`](promise.md) | 値を設定する側 |
| [`future`](future.md) | 受け取る側 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::future_error](https://cpprefjp.github.io/reference/future/future_error.html)
- [cppreference: std::future_error](https://en.cppreference.com/w/cpp/thread/future_error)
