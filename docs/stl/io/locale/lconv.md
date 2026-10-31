---
title: std::lconv
summary: "数値と通貨の書式情報をまとめた構造体。"
order: 900
tags:
  - 入出力・文字列
---

# std::lconv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <clocale>`
</div>

`localeconv` が返す構造体が `lconv` です。数値の小数点、桁区切り、桁のまとめ方と、通貨の記号、符号の位置、小数点以下の桁数などが入っています。項目が多く、名前も似ているので、よく使うものから見ていきます。

!!! tip "ポイント"
    - 数値の項目は `decimal_point`、`thousands_sep`、`grouping`
    - 通貨の項目は `currency_symbol`、`mon_decimal_point`、`frac_digits` など。国際表記の `int_` つきもある
    - `"C"` ロケールでは、数値型の項目は `CHAR_MAX`（未設定を表す）、文字列は空
    - `grouping` は文字列に見えるが、中身は桁数の数値の並び

!!! info "このページを読む前に"
    [`std::localeconv`](localeconv.md) を先に読んでください。

## 関数の詳しい説明

### std::lconv {#lconv}

```cpp
struct lconv {
  char* decimal_point;       // 小数点
  char* thousands_sep;       // 桁区切り
  char* grouping;            // 桁のまとめ方
  char* currency_symbol;     // 通貨記号
  char* mon_decimal_point;   // 通貨の小数点
  char* mon_thousands_sep;   // 通貨の桁区切り
  char* mon_grouping;        // 通貨の桁のまとめ方
  char* positive_sign;       // 正の符号
  char* negative_sign;       // 負の符号
  char frac_digits;          // 小数点以下の桁数
  // ...（int_ で始まる国際表記の項目など）
};
```

### 数値の項目 {#numeric}

`decimal_point` は、小数点の文字です。`"C"` ロケールでは `"."` で、ドイツ語などでは `","` です。`thousands_sep` は、桁区切りの文字で、日本の `1,234` の `","` です。`"C"` ロケールでは空の文字列で、桁区切りなしを意味します。

`grouping` は、桁をいくつずつまとめるかを表す、数値の並びです。文字列の型ですが、中身は文字ではなく数値で、`"\3"` なら「下から 3 桁ごと」です。`"\3\2"` は、最初の 3 桁のあとは 2 桁ずつ（インドの数え方）。`CHAR_MAX` は、それ以降はまとめない、の意味です。

### 通貨の項目 {#money}

`currency_symbol` は、通貨記号で、日本なら `"円"` や `"¥"` です。`frac_digits` は、小数点以下の桁数で、日本円は 0、ドルは 2 です。`positive_sign` と `negative_sign` は、符号の文字です。符号や記号を、数の前に置くか後ろに置くかは、`p_cs_precedes`、`n_cs_precedes` などの項目が決めます。

`int_curr_symbol` や `int_frac_digits` のように、`int_` で始まる項目は、国際的な表記（`JPY` のような 3 文字の通貨コード）のためのものです。

### 未設定の値 {#unset}

`char` 型の数値の項目で `CHAR_MAX` があれば、そのロケールでは値が決まっていません。`"C"` ロケールの通貨の項目は、ほぼ全部これです。`frac_digits` を、そのまま小数の桁数として使うと、127 桁などと解釈されます。使う前に、`CHAR_MAX` でないことを確かめます。

## 実際に動かしてみる

```cpp
#include <climits>
#include <clocale>
#include <print>

int main() {
  const std::lconv* lc = std::localeconv();

  std::println("小数点: {}", lc->decimal_point);
  std::println("桁区切りは空: {}", lc->thousands_sep[0] == '\0');
  std::println("通貨の小数桁は未設定: {}", lc->frac_digits == CHAR_MAX);
}
```

```text title="実行結果"
小数点: .
桁区切りは空: true
通貨の小数桁は未設定: true
```

## ゲームでの使いどころ

使う場面はあまりありません。ユーザーのロケールに合わせて金額を表示する機能を、自作するときの材料です。

## よくあるミス

??? failure "文字列として保存せず、ポインタを保持する"
    ポインタは、次の `setlocale` で無効になります。必要ならコピーします。

??? failure "CHAR_MAX を桁数として使う"
    `"C"` ロケールの `frac_digits` は `CHAR_MAX`（127）です。未設定の値なので、検査してから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`localeconv`](localeconv.md) | この構造体を返す関数 |
| [`std::numpunct`](numpunct.md) | C++ のロケールの数値の書式 |
| [`std::moneypunct`](moneypunct.md) | C++ のロケールの通貨の書式 |

## コンパイラ対応

C 由来の構造体です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `lconv` は、数値と通貨の書式を持つ構造体
    - [x] `"C"` ロケールでは、数値の項目は未設定（`CHAR_MAX`）
    - [x] `grouping` は文字列に見えて、数値の並び

## 関連ページ

- [cpprefjp: lconv](https://cpprefjp.github.io/reference/clocale/lconv.html)
- [cppreference: std::lconv](https://en.cppreference.com/w/cpp/locale/lconv)
