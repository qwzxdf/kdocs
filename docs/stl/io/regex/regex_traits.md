---
title: std::regex_traits
summary: "文字の分類や変換の規則をまとめた、正規表現の部品。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

正規表現エンジンは、「数字か」「空白か」「大文字小文字を同一視するか」といった判断を `regex_traits` に任せています。ロケールによって規則を変えたいときに、差し替えられます。ふつうは意識しません。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_traits {#regex_traits}

```cpp
template <class CharT>
struct regex_traits {
  static std::size_t length(const CharT* p);
  CharT translate(CharT c) const;
  // ...
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |

- 戻り値: 文字の分類・変換の関数
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  std::println("{}", std::regex_traits<char>::length("abc"));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （正規表現の挙動を差し替えるとき） |

## よくあるミス

??? failure "ふつうは触らない"
    既定の `regex_traits` で足ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_regex`](basic_regex.md) | これを使う正規表現 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字の分類や変換の規則をまとめた、正規表現の部品
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::regex_traits](https://cpprefjp.github.io/reference/regex/regex_traits.html)
- [cppreference: std::regex_traits](https://en.cppreference.com/w/cpp/regex/regex_traits)
