---
title: std::regex_constants
summary: "正規表現のオプションとエラーコードをまとめた名前空間。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_constants

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex_constants` の中に `icase`（大文字小文字を区別しない）のような**構文オプション**、`match_continuous` のような**一致オプション**、`error_paren` のような**エラーコード**が入っています。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_constants {#regex_constants}

```cpp
namespace std::regex_constants {
  // syntax_option_type, match_flag_type, error_type の定数
}
```

- 戻り値: 各種の定数
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  std::regex re("ABC", std::regex_constants::icase);
  std::println("{}", std::regex_match("abc", re));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 大文字小文字を区別しない検索 |

## よくあるミス

??? failure "`using namespace` する"
    名前が衝突するので、必要な名前だけを `std::regex_constants::icase` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`syntax_option_type`](syntax_option_type.md) | 構文オプション |
| [`match_flag_type`](match_flag_type.md) | 一致オプション |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正規表現のオプションとエラーコードをまとめた名前空間
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::regex_constants](https://cpprefjp.github.io/reference/regex/regex_constants.html)
- [cppreference: std::regex_constants](https://en.cppreference.com/w/cpp/regex/regex_constants)
