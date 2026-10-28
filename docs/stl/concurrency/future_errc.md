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

`future_error` がなぜ投げられたかを `future_errc` の値で区別できます。`broken_promise`（約束が果たされなかった）、`future_already_retrieved`（`get_future` の二重呼び出し）、`promise_already_satisfied`（値を二重に設定）、`no_state`（状態がない）の 4 つです。

!!! tip "ポイント"
    - `broken_promise`: `promise` が値を設定する前に破棄された。
    - `future_already_retrieved`: `get_future()` を 2 回呼んだ。
    - `promise_already_satisfied`: 値を 2 回設定した。 `no_state`: 状態を持たない `future` を使った。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::future_errc {#future_errc}

```cpp
enum class future_errc {
  broken_promise = /* 実装定義 */,
  future_already_retrieved,
  promise_already_satisfied,
  no_state
};
```

- 戻り値: なし（列挙型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <future>
#include <print>

int main() {
  std::future<int> f;  // 状態を持たない
  try {
    f.get();
  } catch (const std::future_error& e) {
    std::println("{}", e.code() == std::future_errc::no_state);
  }
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| エラーの原因ごとに処理を分ける | `switch (e.code().value()) { ... }` ではなく `e.code() == std::future_errc::...` で比べる |

## よくあるミス

??? failure "`value()` を直接比べる"
    数値は実装依存です。`future_errc` との比較（`==`）を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future_error`](future_error.md) | 例外クラス |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] future_error の原因
    - [x] 4 つの値
    - [x] == で比べる

## 関連ページ

- [cpprefjp: std::future_errc](https://cpprefjp.github.io/reference/future/future_errc.html)
- [cppreference: std::future_errc](https://en.cppreference.com/w/cpp/thread/future_errc)
