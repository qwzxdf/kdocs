---
title: std::future_errc
summary: "future_error の原因を表す列挙型。"
order: 900
tags:
  - 並行処理
---

# std::future_errc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::promise` と `std::future` の使い方を間違えたとき、`std::future_error` が投げられます。何を間違えたかを表すエラー コードの列挙型が `std::future_errc` で、4 種類あります。

!!! tip "ポイント"
    - `broken_promise`: 値を入れずに `promise` が破棄された
    - `future_already_retrieved`: `get_future` を 2 回呼んだ
    - `promise_already_satisfied`: `set_value` を 2 回呼んだ
    - `no_state`: 共有状態を持たない `future` / `promise` を使った

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::future_errc {#future_errc}

<span class="ver ver-11">C++11</span>

```cpp
enum class future_errc {
  broken_promise = 1,
  future_already_retrieved,
  promise_already_satisfied,
  no_state
};
```

`future_error::code()` が返す `std::error_code` と、`future_errc` を比べて、原因を判定します。

```cpp
catch (const std::future_error& e) {
  if (e.code() == std::future_errc::promise_already_satisfied) { /* ... */ }
}
```

`broken_promise` は、値を入れずに `promise` が破棄されたとき、待っていた `future` の `get()` が投げます。ワーカー スレッドが、値を設定する前に例外などで終わった場合に起きます。

`std::error_code` との比較は、`std::make_error_code(future_errc)` を通して行われます。`is_error_code_enum` が特殊化されているため、`==` で直接比べられます。

## 実際に動かしてみる

```cpp
#include <future>
#include <print>

int main() {
  std::promise<int> p;
  p.set_value(1);

  try {
    p.set_value(2);  // 2 回目
  } catch (const std::future_error& e) {
    std::println("2 回設定: {}", e.code() == std::future_errc::promise_already_satisfied);
  }

  std::future<int> f = p.get_future();
  try {
    p.get_future();  // 2 回目
  } catch (const std::future_error& e) {
    std::println("2 回取得: {}", e.code() == std::future_errc::future_already_retrieved);
  }

  // 値を入れずに promise が破棄される
  std::future<int> g;
  {
    std::promise<int> q;
    g = q.get_future();
  }
  try {
    g.get();
  } catch (const std::future_error& e) {
    std::println("約束が破られた: {}", e.code() == std::future_errc::broken_promise);
  }
}
```

```text title="実行結果"
2 回設定: true
2 回取得: true
約束が破られた: true
```

## ゲームでの使いどころ

非同期処理のエラー処理で、原因ごとの対処（ログ、再試行）を分けるときに使います。

## よくあるミス

??? failure "set_value を二重に呼ぶ"
    `promise_already_satisfied` で例外になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future_error`](future_error.md) | この列挙型を持つ例外 |
| [`promise`](promise.md) | 値を設定する側 |
| [`future`](future.md) | 受け取る側 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::future_errc](https://cpprefjp.github.io/reference/future/future_errc.html)
- [cppreference: std::future_errc](https://en.cppreference.com/w/cpp/thread/future_errc)
