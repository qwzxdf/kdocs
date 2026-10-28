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

`put_money` が内部で使っているのが `money_put` です。通貨記号、桁区切り、小数点以下の桁数を `moneypunct` の規則に従って出力します。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::money_put {#money_put}

```cpp
template <class CharT, class OutIt = ostreambuf_iterator<CharT>>
class money_put {
 public:
  OutIt put(OutIt out, bool intl, std::ios_base& str, CharT fill, long double units) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き出し先 |
| `intl` | bool | 国際表記にするか |
| `units` | 数値 | 金額（最小単位） |

- 戻り値: 書き終えた後の出力イテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  std::ostringstream os;
  os.imbue(std::locale::classic());
  std::use_facet<std::money_put<char>>(std::locale::classic()).put(std::ostreambuf_iterator<char>(os), false, os, ' ', 12345L);
  std::println("{}", os.str());
}
```

```text title="実行結果"
12345
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 通貨を国ごとの書式で表示する |

## よくあるミス

??? failure "直接使う"
    ふつうは `std::put_money` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`put_money`](../put_money.md) | ストリームに書く |
| [`moneypunct`](moneypunct.md) | 書式の記号 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 金額をロケールの通貨の書式で書き出すファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::money_put](https://cpprefjp.github.io/reference/locale/money_put.html)
- [cppreference: std::money_put](https://en.cppreference.com/w/cpp/locale/money_put)
