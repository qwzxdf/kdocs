---
title: std::ssub_match
summary: "string 用の sub_match。"
order: 900
tags:
  - 入出力・文字列
---

# std::ssub_match

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`sub_match<std::string::const_iterator>` の別名です。`smatch` の `m[n]` の型です。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::ssub_match {#ssub_match}

```cpp
using ssub_match = sub_match<std::string::const_iterator>;
```

- 戻り値: `str()` で文字列
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  std::string s = "abc123";
  std::smatch m;
  std::regex_search(s, m, std::regex("(\\d+)"));
  std::ssub_match sm = m[1];
  std::println("{}", sm.str());
}
```

```text title="実行結果"
123
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `smatch` のグループを取り出す |

## よくあるミス

??? failure "文字列として保存せず参照を持ち続ける"
    元の文字列が消えると壊れます。`str()` でコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sub_match`](sub_match.md) | 元のテンプレート |
| [`csub_match`](csub_match.md) | C 文字列用 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] string 用の sub_match
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ssub_match](https://cpprefjp.github.io/reference/regex/ssub_match.html)
- [cppreference: std::ssub_match](https://en.cppreference.com/w/cpp/regex/ssub_match)
