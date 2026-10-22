---
title: std::regex_error
summary: "正規表現のパターンが不正なときに投げられる例外。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex re("(")` のように、括弧が閉じていないパターンを作ろうとすると、`regex_error` が投げられます。`code()` で原因（`regex_constants::error_paren` など）を取れます。外から受け取ったパターンは `try` で囲みます。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_error {#regex_error}

```cpp
class regex_error : public runtime_error {
 public:
  regex_constants::error_type code() const;
};
```

- 戻り値: `code()` が原因
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  try {
    std::regex re("(");
  } catch (const std::regex_error& e) {
    std::println("{}", e.code() == std::regex_constants::error_paren);
  }
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ユーザーが入力したパターンを検査する |

## よくあるミス

??? failure "外から入ったパターンを `try` で囲まない"
    不正なパターンで例外が飛び、プログラムが落ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex`](../regex.md) | 正規表現 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正規表現のパターンが不正なときに投げられる例外
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::regex_error](https://cpprefjp.github.io/reference/regex/regex_error.html)
- [cppreference: std::regex_error](https://en.cppreference.com/w/cpp/regex/regex_error)
