---
title: std::current_exception
summary: "いま処理中の例外を、exception_ptr として取り出す。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::current_exception

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

例外をそのまま別のスレッドに渡したい、あとで投げ直したい、というときに、`catch` の中で `current_exception()` を呼んで `exception_ptr` に保存します。`catch` の外で呼ぶと、空の `exception_ptr` が返ります。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::current_exception {#current_exception}

```cpp
std::exception_ptr current_exception() noexcept;
```

- 戻り値: 処理中の例外の `exception_ptr`（なければ空）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::runtime_error("boom");
  } catch (...) {
    std::exception_ptr p = std::current_exception();
    std::println("{}", p != nullptr);
  }
  std::println("{}", std::current_exception() != nullptr);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 別スレッドの例外をメインスレッドに渡す |

## よくあるミス

??? failure "`catch` の外で呼ぶ"
    処理中の例外がないと、空のポインタが返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception_ptr`](exception_ptr.md) | 例外を持ち歩く型 |
| [`rethrow_exception`](rethrow_exception.md) | 投げ直す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] いま処理中の例外を、exception_ptr として取り出す
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::current_exception](https://cpprefjp.github.io/reference/exception/current_exception.html)
- [cppreference: std::current_exception](https://en.cppreference.com/w/cpp/error/current_exception)
