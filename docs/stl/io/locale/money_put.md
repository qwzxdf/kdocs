---
title: std::money_put
summary: "金額を、ロケールの通貨の書式で書き出すファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::money_put

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

金額を、そのロケールの通貨の書き方で出力する部品が `std::money_put` です。`std::put_money` という操作子は、この部品を呼んでいます。記号や桁区切り、小数点以下の桁数は、`moneypunct` の規則に従います。

金額は、`long double` か文字列で渡します。いずれも、通貨の最小単位（円なら 1 円、ドルなら 1 セント）の個数を表します。

!!! tip "ポイント"
    - 金額は最小単位の整数。ドルで 12.34 は `1234`
    - `intl` が `true` だと国際表記（通貨コード）、`false` だと通貨記号
    - 書式は `moneypunct` が決める。記号を付けるかは `showbase` の設定による
    - `std::put_money(金額)` の操作子から使うのが普通

!!! info "このページを読む前に"
    [`std::moneypunct`](moneypunct.md) と、[`std::put_money`](../put_money.md) を先に読んでください。

## 関数の詳しい説明

### std::money_put {#money_put}

```cpp
template <class CharT, class OutIt = std::ostreambuf_iterator<CharT>>
class money_put {
 public:
  OutIt put(OutIt out, bool intl, std::ios_base& str, CharT fill, long double units) const;
  OutIt put(OutIt out, bool intl, std::ios_base& str, CharT fill,
            const std::basic_string<CharT>& digits) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | `OutIt` | 書き出し先の出力イテレータ |
| `intl` | `bool` | 国際表記にするか |
| `str` | `std::ios_base&` | 書式の設定（幅、`showbase` など）を持つストリーム |
| `fill` | `CharT` | 幅を埋める文字 |
| `units` | `long double` | 金額（最小単位の個数） |

2 つのオーバーロードのうち、`long double` を受け取るほうは、精度が限られます。大きな金額や、正確さが必要なときは、数字の文字列を受け取るほうを使います。負の金額は、文字列の先頭に `-` を付けます。

出力される形は、`moneypunct` の `pos_format` と `neg_format` で決まります。記号は、`str` に `showbase` が設定されているときだけ付きます。

ロケールにより、整数の `12345` が、`12,345` や `123.45`（`frac_digits` が 2 の場合）と出力されます。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  std::ostringstream os;
  const auto& mp = std::use_facet<std::money_put<char>>(std::locale::classic());

  // classic は小数点以下 0 桁なので、整数がそのまま出る
  mp.put(std::ostreambuf_iterator<char>(os), false, os, ' ', 12345L);
  std::println("{}", os.str());
}
```

```text title="実行結果"
12345
```

`"C"` ロケールは、記号も桁区切りもなく、小数点以下も 0 桁です。ほかのロケールでは、見た目が変わります。

## ゲームでの使いどころ

現実の通貨を表示する課金画面などで使えます。ストアから通貨記号つきの価格を取れる場合は、その文字列をそのまま出すほうが確実です。

## よくあるミス

??? failure "金額を小数で渡す"
    `12.34` を渡しても、12 セントや 12 円として扱われます。最小単位の整数（`1234`）にして渡します。

??? failure "記号が出ない"
    `showbase` を設定していないと、記号は付きません。`os << std::showbase` を先に設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`money_get`](money_get.md) | 逆方向。文字列から金額を読む |
| [`moneypunct`](moneypunct.md) | 通貨の書式の規則 |
| [`std::put_money`](../put_money.md) | ストリームに流す操作子。普段はこちら |
| [`num_put`](num_put.md) | 通貨ではない数値を書き出す |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `money_put` は、金額を通貨の書式で書き出す部品
    - [x] 金額は最小単位の整数で渡す
    - [x] 普段は操作子の `put_money` から使う

## 関連ページ

- [cpprefjp: money_put](https://cpprefjp.github.io/reference/locale/money_put.html)
- [cppreference: std::money_put](https://en.cppreference.com/w/cpp/locale/money_put)
