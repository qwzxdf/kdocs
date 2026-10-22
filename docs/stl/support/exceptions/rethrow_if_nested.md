---
title: std::rethrow_if_nested
summary: "包まれた例外があれば、それを取り出して投げ直す。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::rethrow_if_nested

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

`throw_with_nested` で包まれた例外には、元の例外が入っています。`rethrow_if_nested(e)` は、`e` が包まれた例外をもっていれば、それを投げ直し、もっていなければ何もしません。再帰で原因の鎖をたどるときに使います。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::rethrow_if_nested {#rethrow_if_nested}

```cpp
template <class E>
void rethrow_if_nested(const E& e);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | 例外 | 調べる例外 |

- 戻り値: なし（包まれた例外があれば投げ直す）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  try {
    try {
      throw std::runtime_error("inner");
    } catch (...) {
      std::throw_with_nested(std::logic_error("outer"));
    }
  } catch (const std::exception& e) {
    std::println("{}", e.what());
    try {
      std::rethrow_if_nested(e);
    } catch (const std::exception& inner) {
      std::println("{}", inner.what());
    }
  }
}
```

```text title="実行結果"
outer
inner
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 例外の原因の鎖をログに全部出す |

## よくあるミス

??? failure "包まれていない例外を気にして `try` を省く"
    包まれていなければ何も起きません。`catch` の中で使うので、`try` で囲む必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`throw_with_nested`](throw_with_nested.md) | 包んで投げる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 包まれた例外があれば、それを取り出して投げ直す
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::rethrow_if_nested](https://cpprefjp.github.io/reference/exception/rethrow_if_nested.html)
- [cppreference: std::rethrow_if_nested](https://en.cppreference.com/w/cpp/error/rethrow_if_nested)
