---
title: std::weak_ordering
summary: "「等しいが、区別はできる」場合を含む比較結果（大文字小文字を無視した比較など）。"
order: 3
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::weak_ordering

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`std::weak_ordering` は、**「等しい（`equivalent`）と判定されても、中身は同じとは限らない」比較結果**です。たとえば、大文字小文字を無視した比較では、"Abc" と "aBC" は等しいですが、別の文字列です。値は `less`、`equivalent`、`greater` の 3 つです。

!!! tip "ポイント"
    - `equal` ではなく `equivalent` という名前。
    - `strong_ordering` から暗黙に変換できる。
    - 大文字小文字を無視した比較、近似的な比較に使う。

## 関数の詳しい説明

### std::weak_ordering {#weak_ordering}

```cpp
struct weak_ordering {
  static const weak_ordering less, equivalent, greater;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `weak_ordering` | 比較結果 |

- 戻り値: `less` / `equivalent` / `greater`
- 計算量: O(1)

```cpp
#include <cctype>
#include <compare>
#include <print>
#include <string>

struct CaseInsensitive {
  std::string text;

  static std::string Lower(std::string s) {
    for (char& c : s) {
      c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    }
    return s;
  }
  std::weak_ordering operator<=>(const CaseInsensitive& o) const {
    return Lower(text) <=> Lower(o.text);  // strong_ordering から変換される
  }
  bool operator==(const CaseInsensitive& o) const { return (*this <=> o) == 0; }
};

int main() {
  std::println("{}", CaseInsensitive{"Abc"} == CaseInsensitive{"aBC"});
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大文字小文字を区別しないキー | `CaseInsensitive` を `map` のキーにする |

## よくあるミス

??? failure "operator== を忘れる"
    `<=>` を自分で書いたときは、`==` は自動で生えません。別に書きます（`= default` のときだけ自動）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strong_ordering`](strong_ordering.md) | 等しいなら区別できない |
| [`partial_ordering`](partial_ordering.md) | 比べられない場合がある |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 等しくても区別できるかも
    - [x] `equivalent` という名前
    - [x] 大文字小文字無視の比較に

## 関連ページ

- [cpprefjp: std::weak_ordering](https://cpprefjp.github.io/reference/compare/weak_ordering.html)
- [cppreference: std::weak_ordering](https://en.cppreference.com/w/cpp/utility/compare/weak_ordering)
