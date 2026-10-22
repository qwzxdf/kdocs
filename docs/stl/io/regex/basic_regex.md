---
title: std::basic_regex
summary: "正規表現を保持するクラスの、元になるテンプレート（`regex` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_regex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex` は、`basic_regex<char>` の別名です。文字の型を選べるように、元になるクラステンプレートがあります。正規表現のコンパイル（文字列を内部の形に直す処理）は重いので、何度も使うなら、1 回作って使い回します。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_regex {#basic_regex}

```cpp
template <class CharT, class Traits = regex_traits<CharT>>
class basic_regex;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |
| `Traits` | 型 | 省略可。文字の分類などの規則 |

- 戻り値: 正規表現のオブジェクト
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  std::basic_regex<char> re("a+");
  std::println("{}", std::regex_match("aaa", re));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 同じ正規表現を何度も使うときに保持する |

## よくあるミス

??? failure "ループの中で毎回作る"
    正規表現の構築は重い処理です。ループの外で 1 回作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex`](../regex.md) | char 版の別名 |
| [`wregex`](wregex.md) | wchar_t 版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正規表現を保持するクラスの、元になるテンプレート（`regex` の元）
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::basic_regex](https://cpprefjp.github.io/reference/regex/basic_regex.html)
- [cppreference: std::basic_regex](https://en.cppreference.com/w/cpp/regex/basic_regex)
