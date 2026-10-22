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

`promise` から `get_future()` を 2 回呼ぶ、`promise` を使わずに壊す、などの使い方のミスがあると、`future_error` が投げられます。`code()` で原因を `future_errc` として取り出せます。

!!! tip "ポイント"
    - `std::logic_error` から派生。
    - `code()` で原因（`future_errc`）を取る。
    - プログラムのミスを表す例外。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::future_error {#future_error}

```cpp
class future_error : public logic_error {
 public:
  const error_code& code() const noexcept;
};
```

- 戻り値: `code()` が原因の `error_code`
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <future>
#include <print>

int main() {
  std::promise<int> p;
  p.get_future();
  try {
    p.get_future();
  } catch (const std::future_error& e) {
    std::println("{}", e.code() == std::future_errc::future_already_retrieved);
  }
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `promise` の二重取得を検出 | `catch (const std::future_error& e) { e.code() == std::future_errc::future_already_retrieved }` |

## よくあるミス

??? failure "通常のエラーとして扱う"
    プログラムのミスを表す例外です。入力のエラーとして扱うものではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future_errc`](future_errc.md) | 原因の列挙型 |
| [`promise`](promise.md) | 値を渡す側 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] future / promise のミスを表す例外
    - [x] code() で原因を取る
    - [x] future_errc

## 関連ページ

- [cpprefjp: std::future_error](https://cpprefjp.github.io/reference/future/future_error.html)
- [cppreference: std::future_error](https://en.cppreference.com/w/cpp/thread/future_error)
