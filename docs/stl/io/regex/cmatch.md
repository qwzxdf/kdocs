---
title: std::cmatch
summary: "C 文字列用の match_results。"
order: 900
tags:
  - 入出力・文字列
---

# std::cmatch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`match_results<const char*>` の別名です。`std::string` ではなく、C の文字列（`const char*`）を検索した結果を入れます。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::cmatch {#cmatch}

```cpp
using cmatch = match_results<const char*>;
```

- 戻り値: `m[n]` で n 番目のグループ（`csub_match`）
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  const char* s = "x=5";
  std::cmatch m;
  std::regex_search(s, m, std::regex("(\\w)=(\\d)"));
  std::println("{}", m[2].str());
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | C の文字列から値を取り出す |

## よくあるミス

??? failure "一時オブジェクトを検索する"
    `std::string` の一時オブジェクトを渡すと、結果が壊れます（`smatch` も同じ）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`smatch`](../smatch.md) | string 用 |
| [`match_results`](match_results.md) | 元のテンプレート |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 文字列用の match_results
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::cmatch](https://cpprefjp.github.io/reference/regex/cmatch.html)
- [cppreference: std::cmatch](https://en.cppreference.com/w/cpp/regex/cmatch)
