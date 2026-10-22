---
title: std::moneypunct
summary: "通貨の書式（記号・桁区切り・小数点以下の桁数）を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::moneypunct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

通貨の書式は、国によって大きく違います。その規則を持っているのが `moneypunct` ファセットです。`frac_digits()`（小数点以下の桁数）・`curr_symbol()`（通貨記号）などを返します。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::moneypunct {#moneypunct}

```cpp
template <class CharT, bool International = false>
class moneypunct {
 public:
  int frac_digits() const;
  std::basic_string<CharT> curr_symbol() const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |
| `International` | bool | 国際表記か |

- 戻り値: 通貨の書式の情報
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  const auto& mp = std::use_facet<std::moneypunct<char>>(std::locale::classic());
  std::println("{}", mp.frac_digits());
}
```

```text title="実行結果"
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 通貨の小数点以下の桁数を調べる |

## よくあるミス

??? failure "日本円だと思う"
    クラシックロケールは通貨の設定が空です。`ja_JP` などのロケールを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`money_put`](money_put.md) | 書き出し |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 通貨の書式（記号・桁区切り・小数点以下の桁数）を担当するファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::moneypunct](https://cpprefjp.github.io/reference/locale/moneypunct.html)
- [cppreference: std::moneypunct](https://en.cppreference.com/w/cpp/locale/moneypunct)
