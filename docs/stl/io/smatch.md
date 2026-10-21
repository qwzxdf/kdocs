---
title: std::smatch
summary: "正規表現で見つかった部分と、グループを持つ結果。"
order: 89
tags:
  - 入出力・文字列
---

# std::smatch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::smatch` は、**正規表現の検索結果**です。全体の一致 `m[0]`、かっこで囲んだグループ `m[1]` `m[2]`、一致の前後の文字列、位置を持っています。`regex_search` や `regex_match` の第 2 引数に渡します。

!!! tip "ポイント"
    - `m[0]` が一致した全体、`m[1]` が 1 番目のグループ。
    - `m.str(1)` で文字列として取り出す。
    - `m.prefix()` / `m.suffix()` で、一致の前後。

!!! info "このページを読む前に"
    [`std::regex`](regex.md) を先に読んでください。

## 関数の詳しい説明

### std::smatch {#smatch}

```cpp
using smatch = std::match_results<std::string::const_iterator>;
```

- `m[0]` が一致した全体、`m[1]` 以降が `()` で囲んだグループ。`.str()` で文字列、`.position(i)` で位置
- **元の文字列が消えると使えない**（中で元の文字列を指している）

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  std::string text = "hp=45";
  std::smatch m;
  if (std::regex_match(text, m, std::regex(R"((\w+)=(\d+))"))) {
    std::println("{} {}", m.str(1), m.str(2));   // かっこ（グループ）ごとに取り出す
  }
}
```

```text title="実行結果"
hp 45
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「名前=値」から名前と値を取り出す | `R"((\w+)=(\d+))"` の `m[1]`、`m[2]` |

## よくあるミス

??? failure "元の文字列を先に破棄する"
    `smatch` は元の文字列を指す参照を持つので、元が消えると無効になります。一時的な文字列を渡さないでください。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::regex_search`](regex_search.md) | smatch を作る関数 |
| [`std::sregex_iterator`](sregex_iterator.md) | 全部の一致を回す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 検索結果。`m[0]` が全体、`m[1]` が最初のグループ
    - [x] `m.str(n)` で文字列
    - [x] 元の文字列が生きている間だけ有効

## 関連ページ

- [cpprefjp: std::smatch](https://cpprefjp.github.io/reference/regex/match_results.html)
- [cppreference: std::smatch](https://en.cppreference.com/w/cpp/regex/match_results)
