---
title: std::money_get
summary: "金額を、ロケールの通貨の書式から読み込むファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::money_get

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`"$12.34"` や `"¥1,234"` のような、通貨の書き方の文字列から、金額の数字だけを取り出す部品が `std::money_get` です。`std::get_money` という操作子の裏で動いています。通貨記号や桁区切りを取り除いて、数字の並びとして返します。

!!! tip "ポイント"
    - 結果は、数字だけの文字列（`digits`）か、`long double`
    - 記号や桁区切りは、`moneypunct` の規則に従って読み飛ばす
    - 読めなかったときは、`err` に `failbit` を立てる
    - 普段は `std::get_money` の操作子から使う

!!! info "このページを読む前に"
    [`std::moneypunct`](moneypunct.md) と [`std::money_put`](money_put.md) を先に読んでください。

## 関数の詳しい説明

### std::money_get {#money_get}

```cpp
template <class CharT, class InIt = std::istreambuf_iterator<CharT>>
class money_get {
 public:
  InIt get(InIt in, InIt end, bool intl, std::ios_base& str,
           std::ios_base::iostate& err, long double& units) const;
  InIt get(InIt in, InIt end, bool intl, std::ios_base& str,
           std::ios_base::iostate& err, std::basic_string<CharT>& digits) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `in`, `end` | `InIt` | 読み込み元の範囲 |
| `intl` | `bool` | 国際表記か |
| `str` | `std::ios_base&` | 書式の設定を持つストリーム |
| `err` | `std::ios_base::iostate&` | エラーの状態を受け取る |
| `digits` | `std::basic_string<CharT>&` | 結果の数字の文字列 |

`moneypunct` の書式に従って、金額を読みます。負の数なら、`digits` の先頭が `-` になります。数字の並びだけを返すので、通貨記号と桁区切りは含まれません。

`long double` で受け取る版は、小数の誤差があるので、金額の計算には向きません。数字の文字列で受け取って、整数に直すほうが確実です。

読めなかった場合は、`err` に `failbit` が立ち、`digits` は変わりません。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>
#include <string>

int main() {
  const auto& mg = std::use_facet<std::money_get<char>>(std::locale::classic());

  std::istringstream in("1234");
  std::istreambuf_iterator<char> b(in);
  std::istreambuf_iterator<char> e;
  std::ios_base::iostate err = std::ios_base::goodbit;
  std::string digits;

  mg.get(b, e, false, in, err, digits);
  std::println("digits: {}", digits);
  std::println("失敗: {}", (err & std::ios_base::failbit) != 0);
}
```

```text title="実行結果"
digits: 1234
失敗: false
```

## ゲームでの使いどころ

使う場面はほとんどありません。課金のレシートなどから価格を読むなら、サービスが返す数値のフィールドを直接使います。

## よくあるミス

??? failure "長い数を long double で受ける"
    精度が足りず、末尾の桁が丸められます。文字列で受け取って、整数に直します。

??? failure "err を初期化しない"
    `goodbit` に初期化してから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`money_put`](money_put.md) | 逆方向。金額を書き出す |
| [`moneypunct`](moneypunct.md) | 通貨の書式の規則 |
| [`std::get_money`](../get_money.md) | ストリームから読む操作子。普段はこちら |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `money_get` は、通貨の書式の文字列から金額を読む部品
    - [x] 数字の文字列で受け取ると、精度の問題が出ない
    - [x] 普段は操作子の `get_money`

## 関連ページ

- [cpprefjp: money_get](https://cpprefjp.github.io/reference/locale/money_get.html)
- [cppreference: std::money_get](https://en.cppreference.com/w/cpp/locale/money_get)
