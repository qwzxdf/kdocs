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

`std::smatch`（`std::string` を検索した結果）の `m[1]` のように取り出す、グループ 1 つぶんの型が `std::ssub_match` です。`sub_match<std::string::const_iterator>` の別名で、機能は [`sub_match`](sub_match.md) のページに書いています。名前を書くのは、`auto` で受けずに、型を明示したいときくらいです。

!!! tip "ポイント"
    - `sub_match<std::string::const_iterator>` の別名
    - `m[n]` の型。`matched`、`length()`、`str()` を持つ
    - `auto` で受けられるので、型名を書くことは少ない
    - `std::wstring` 用は `std::wssub_match`

!!! info "このページを読む前に"
    [`std::sub_match`](sub_match.md) を先に読んでください。

## 関数の詳しい説明

### std::ssub_match {#ssub_match}

```cpp
using ssub_match = sub_match<std::string::const_iterator>;
```

`std::string` を検索対象にしたとき、`std::smatch` が持つ要素の型です。`const_iterator` なのは、検索対象が `const` の文字列として扱われるためです。

`std::smatch` と `std::ssub_match` は、対で使います。`const char*` を検索対象にしたなら `std::cmatch` と `std::csub_match`、`std::wstring` なら `std::wsmatch` と `std::wssub_match`、`const wchar_t*` なら `std::wcmatch` と `std::wcsub_match` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  const std::string s = "abc123";
  std::smatch m;
  std::regex_search(s, m, std::regex("(\\d+)"));

  std::ssub_match sm = m[1];  // 型を明示して受ける
  std::println("{}", sm.str());
  std::println("先頭から {} 文字目", sm.first - s.begin());
}
```

```text title="実行結果"
123
先頭から 3 文字目
```

`first` は元の文字列のイテレータなので、`s.begin()` との差で、位置が求まります。

## ゲームでの使いどころ

`for (const std::ssub_match& sm : m)` のように、結果を全部回すとき以外は、`auto` で足ります。

## よくあるミス

??? failure "std::string の一時オブジェクトを検索して、ssub_match が無効になる"
    `std::regex_search(get_string(), m, re)` は、一時オブジェクトを渡すことになり、コンパイルできません（削除されています）。名前のある変数に入れてから検索します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sub_match`](sub_match.md) | 元のテンプレート |
| [`csub_match`](csub_match.md) | `const char*` 用 |
| [`std::smatch`](../smatch.md) | `ssub_match` の集まり |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ssub_match` は、`std::string` の検索結果の、グループ 1 つぶんの型
    - [x] 型名は `auto` で受けられる
    - [x] 検索対象は名前のある変数にする

## 関連ページ

- [cpprefjp: ssub_match](https://cpprefjp.github.io/reference/regex/ssub_match.html)
- [cppreference: std::ssub_match](https://en.cppreference.com/w/cpp/regex/sub_match)
