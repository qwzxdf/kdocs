---
title: std::match_results
summary: "一致の結果（全体とグループ）を保持するクラスの、元になるテンプレート。"
order: 900
tags:
  - 入出力・文字列
---

# std::match_results

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`regex_search` や `regex_match` は、一致した部分を `match_results` に入れて返します。`m[0]` が一致した全体、`m[1]` 以降が括弧で囲んだグループです。`std::smatch` は、これの `string` 用の別名です。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::match_results {#match_results}

```cpp
template <class BidirIt, class Alloc = allocator<sub_match<BidirIt>>>
class match_results;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `BidirIt` | 型 | 文字列のイテレータの型 |

- 戻り値: `m[n]` で n 番目のグループ（`sub_match`）
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  std::string s = "10-20";
  std::match_results<std::string::const_iterator> m;
  std::regex_search(s, m, std::regex("(\\d+)-(\\d+)"));
  std::println("{} {}", m[1].str(), m[2].str());
}
```

```text title="実行結果"
10 20
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テキストから数値を取り出す |

## よくあるミス

??? failure "`m[0]` を最初のグループと思う"
    `m[0]` は一致した全体です。括弧のグループは `m[1]` からです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`smatch`](../smatch.md) | string 用の別名 |
| [`sub_match`](sub_match.md) | 各グループの型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一致の結果（全体とグループ）を保持するクラスの、元になるテンプレート
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::match_results](https://cpprefjp.github.io/reference/regex/match_results.html)
- [cppreference: std::match_results](https://en.cppreference.com/w/cpp/regex/match_results)
