---
title: std::sub_match
summary: "一致したグループ 1 つぶんを表すクラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::sub_match

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`match_results` の `m[1]` のように、取り出したグループ 1 つぶんが `sub_match` です。`matched`（一致したか）、`str()`（文字列にする）、`length()`（長さ）などをもちます。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::sub_match {#sub_match}

```cpp
template <class BidirIt>
class sub_match : public pair<BidirIt, BidirIt>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `BidirIt` | 型 | 文字列のイテレータの型 |

- 戻り値: `first` / `second` が範囲、`str()` で文字列
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
  const auto& sm = m[1];
  std::println("{} {}", sm.matched, sm.length());
}
```

```text title="実行結果"
true 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | グループが一致したか調べて取り出す |

## よくあるミス

??? failure "`matched` を確かめない"
    省略されたグループ（`(a)?` など）は、`matched` が `false` で空になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ssub_match`](ssub_match.md) | string 用の別名 |
| [`match_results`](match_results.md) | グループの集まり |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一致したグループ 1 つぶんを表すクラス
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sub_match](https://cpprefjp.github.io/reference/regex/sub_match.html)
- [cppreference: std::sub_match](https://en.cppreference.com/w/cpp/regex/sub_match)
