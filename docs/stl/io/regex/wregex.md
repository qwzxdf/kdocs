---
title: std::wregex
summary: "`wchar_t` 用の正規表現。"
order: 900
tags:
  - 入出力・文字列
---

# std::wregex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::wregex` は、`basic_regex<wchar_t>` の別名です。`wchar_t` の文字列（`wstring`）を検索するときに使います。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::wregex {#wregex}

```cpp
using wregex = basic_regex<wchar_t>;
```

- 戻り値: 正規表現のオブジェクト
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  std::wregex re(L"a+");
  std::wstring s = L"aaa";
  std::println("{}", std::regex_match(s, re));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | Windows の `wstring` に対して検索する |

## よくあるミス

??? failure "`regex` と `wstring` を混ぜる"
    文字の型を合わせます。`wstring` には `wregex` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex`](../regex.md) | char 版 |
| [`wsmatch`](wsmatch.md) | 結果の型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wchar_t` 用の正規表現
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wregex](https://cpprefjp.github.io/reference/regex/wregex.html)
- [cppreference: std::wregex](https://en.cppreference.com/w/cpp/regex/wregex)
