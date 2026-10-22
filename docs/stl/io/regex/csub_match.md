---
title: std::csub_match
summary: "C 文字列用の sub_match。"
order: 900
tags:
  - 入出力・文字列
---

# std::csub_match

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`sub_match<const char*>` の別名です。`cmatch` の `m[n]` の型です。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::csub_match {#csub_match}

```cpp
using csub_match = sub_match<const char*>;
```

- 戻り値: `str()` で文字列
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  const char* s = "abc123";
  std::cmatch m;
  std::regex_search(s, m, std::regex("(\\d+)"));
  std::csub_match sm = m[1];
  std::println("{}", sm.str());
}
```

```text title="実行結果"
123
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `cmatch` のグループを取り出す |

## よくあるミス

??? failure "元の文字列が先に消える"
    `csub_match` は元の文字列を指すだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sub_match`](sub_match.md) | 元のテンプレート |
| [`ssub_match`](ssub_match.md) | string 用 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 文字列用の sub_match
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::csub_match](https://cpprefjp.github.io/reference/regex/csub_match.html)
- [cppreference: std::csub_match](https://en.cppreference.com/w/cpp/regex/csub_match)
