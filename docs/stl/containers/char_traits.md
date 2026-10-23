---
title: std::char_traits
summary: "文字型ごとの、比較・長さ・コピーといった基本の操作をまとめた部品。"
order: 29
tags:
  - コンテナ
---

# std::char_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <string>`
</div>

`std::char_traits<CharT>` は、**文字の型ごとの基本操作（比較、長さ、コピー、検索）をまとめた部品**です。`std::string` の内部で使われており、自作の文字列型で「大文字小文字を区別しない」などの比較を作りたいときに差し替えます。普段は直接使いません。

!!! tip "ポイント"
    - `std::char_traits<char>::length("abc")` のように、C 文字列の長さを調べるのに使えることがある（`std::strlen` の代わり）。
    - `basic_string<char, MyTraits>` のように差し替えると、比較の規則を変えた文字列型が作れる。
    - 普段は意識しない。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [イテレータ](../../basics/iterator.md)（イテレーターの基礎）

## 宣言

```cpp
template <class CharT>
struct char_traits;
```

## 関数の詳しい説明

### length {#length}

```cpp
static constexpr size_t length(const CharT* s);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const CharT*` | 終端が `\0` の文字列 |

- 戻り値: 文字数（終端を含まない）
- 計算量: O(n)

### compare {#compare}

```cpp
static constexpr int compare(const CharT* s1, const CharT* s2, size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s1`, `s2` | `const CharT*` | 比べる 2 つの文字列 |
| `n` | `size_t` | 比べる文字数 |

- 戻り値: `s1` が小さければ負、等しければ 0、大きければ正
- 計算量: O(n)

```cpp
#include <print>
#include <string>

int main() {
  using Traits = std::char_traits<char>;

  std::println("長さ {}", Traits::length("hello"));
  std::println("abc < abd ? {}", Traits::compare("abc", "abd", 3) < 0);
}
```

```text title="実行結果"
長さ 5
abc < abd ? true
```

### eq {#eq}

```cpp
static constexpr bool eq(CharT a, CharT b) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a`, `b` | `CharT` | 比べる 2 つの文字 |

- 戻り値: 等しければ `true`
- 計算量: O(1)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大文字小文字を区別しない文字列型を作る | `char_traits` を継承して `eq` / `lt` / `compare` を差し替える |

## よくあるミス

??? failure "char_traits を差し替えた文字列は、std::string と型が違う"
    `basic_string<char, MyTraits>` は `std::string` と別の型で、代入や比較が直接できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::basic_string`](basic_string.md) | `char_traits` を使う文字列クラス |
| `strlen` / `strcmp` | C 由来の同等の関数（[cstring](../memory/cstring.md)） |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字型ごとの基本操作の部品
    - [x] `std::string` の内部で使われる
    - [x] 普段は直接使わない

## 関連ページ

- [cpprefjp: std::char_traits](https://cpprefjp.github.io/reference/string/char_traits.html)
- [cppreference: std::char_traits](https://en.cppreference.com/w/cpp/string/char_traits)
