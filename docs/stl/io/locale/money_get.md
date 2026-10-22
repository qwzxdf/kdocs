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

`get_money` が内部で使っているのが `money_get` です。ロケールの通貨の書式を解釈して、金額の数値に直します。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::money_get {#money_get}

```cpp
template <class CharT, class InIt = istreambuf_iterator<CharT>>
class money_get {
 public:
  InIt get(InIt in, InIt end, bool intl, std::ios_base& str, std::ios_base::iostate& err, std::basic_string<CharT>& digits) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `in, end` | 入力イテレータ | 読み込み元の範囲 |
| `intl` | bool | 国際表記か |
| `err` | iostate& | エラーの状態を受け取る |
| `digits` | string | 結果の数字の文字列 |

- 戻り値: 読み終えた位置の入力イテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream in("1234");
  std::istreambuf_iterator<char> b(in);
  std::istreambuf_iterator<char> e;
  std::ios_base::iostate err = std::ios_base::goodbit;
  std::string digits;
  std::use_facet<std::money_get<char>>(std::locale::classic()).get(b, e, false, in, err, digits);
  std::println("{}", digits);
}
```

```text title="実行結果"
1234
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 通貨の入力を解釈する |

## よくあるミス

??? failure "直接使う"
    ふつうは `std::get_money` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_money`](../get_money.md) | ストリームから読む |
| [`money_put`](money_put.md) | 書き出し側 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 金額を、ロケールの通貨の書式から読み込むファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::money_get](https://cpprefjp.github.io/reference/locale/money_get.html)
- [cppreference: std::money_get](https://en.cppreference.com/w/cpp/locale/money_get)
